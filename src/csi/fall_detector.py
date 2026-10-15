from dataclasses import dataclass
from enum import IntEnum

import numpy as np


class FallState(IntEnum):
    CALM = 0
    MOVING = 1
    IMPACT = 2
    CHECKING_STILL = 3
    ALARM = 4


STATE_LABELS = {
    FallState.CALM: "CALM",
    FallState.MOVING: "MERS",
    FallState.IMPACT: "IMPACT",
    FallState.CHECKING_STILL: "VERIFICARE",
    FallState.ALARM: "ALARMĂ",
}

SLOPE_ACTIVE = 0.05
IMPACT_SLOPE = 17.5
MIN_LINKS_AT_IMPACT = 2
CALM_RETURN_S = 0.6
IMPACT_SETTLE_S = 0.5
STILL_WINDOW_S = 2.5
STILL_MAX_VARIANCE = 0.20
EMPTY_ROOM_STD_SIMULATED = 0.20
EMPTY_ROOM_STD_HARDWARE = 11.0
SIMULATED_MIN_RATE_HZ = 100.0
NORMALIZE_EPSILON = 1e-6


@dataclass(frozen=True)
class Detection:
    states: np.ndarray
    impact_time_s: float | None
    alarm_time_s: float | None

    @property
    def alarm(self):
        return self.alarm_time_s is not None

    @property
    def latency_s(self):
        if self.impact_time_s is None or self.alarm_time_s is None:
            return None
        return self.alarm_time_s - self.impact_time_s


def _normalized(motion):
    return motion / (np.max(np.abs(motion)) + NORMALIZE_EPSILON)


def _slopes(normalized, rate_hz):
    return np.abs(np.gradient(normalized, 1.0 / rate_hz))


def normalized_slopes(motion_by_link, rate_hz):
    return {name: _slopes(_normalized(motion), rate_hz) for name, motion in motion_by_link.items()}


def _is_still(normalized, impact_index, i, settle_samples):
    window_start = impact_index + settle_samples
    variances = [np.var(signal[window_start:i]) for signal in normalized]
    return np.mean(variances) < STILL_MAX_VARIANCE


def detect_fall(times_s, motion_by_link, rate_hz):
    count = len(times_s)
    states = np.zeros(count, dtype=int)

    empty_room_std = EMPTY_ROOM_STD_SIMULATED if rate_hz >= SIMULATED_MIN_RATE_HZ else EMPTY_ROOM_STD_HARDWARE
    mean_std = float(np.mean([np.std(motion) for motion in motion_by_link.values()]))
    if mean_std < empty_room_std:
        return Detection(states, None, None)

    normalized = [_normalized(motion) for motion in motion_by_link.values()]
    slopes = np.array([_slopes(signal, rate_hz) for signal in normalized])
    active_links = (slopes > SLOPE_ACTIVE).sum(axis=0)
    has_impact_slope = (slopes > IMPACT_SLOPE).any(axis=0)
    min_links = min(MIN_LINKS_AT_IMPACT, len(normalized))

    calm_samples = int(CALM_RETURN_S * rate_hz)
    still_samples = int(STILL_WINDOW_S * rate_hz)
    settle_samples = int(IMPACT_SETTLE_S * rate_hz)

    state = FallState.CALM
    impact_index = None
    alarm_index = None
    calm_counter = 0

    for i in range(1, count):
        if state in (FallState.CALM, FallState.MOVING):
            if active_links[i] >= min_links and has_impact_slope[i]:
                state = FallState.IMPACT
                impact_index = i
            elif active_links[i] >= 1:
                state = FallState.MOVING
                calm_counter = 0
            else:
                calm_counter += 1
                if calm_counter > calm_samples:
                    state = FallState.CALM
        elif state == FallState.IMPACT:
            state = FallState.CHECKING_STILL
        elif state == FallState.CHECKING_STILL:
            if i - impact_index >= still_samples:
                if _is_still(normalized, impact_index, i, settle_samples):
                    state = FallState.ALARM
                    alarm_index = i
                else:
                    state = FallState.MOVING
        states[i] = state

    impact_time_s = float(times_s[impact_index]) if impact_index is not None else None
    alarm_time_s = float(times_s[alarm_index]) if alarm_index is not None else None
    return Detection(states, impact_time_s, alarm_time_s)
