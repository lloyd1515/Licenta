import math
from collections import deque
from dataclasses import dataclass, replace
from typing import NamedTuple

import numpy as np

from csi.dsp import Analysis, analyze_recording, peak_frequencies_hz
from csi.fall_detector import FallState
from csi.packets import Packet, recording_from_packets

MIN_ACTIVITY = 0.05
MAX_ACTIVITY = 1.0
MOTION_EPSILON = 1e-9
MIN_LIVE_SAMPLES = 64
MICROSECONDS_PER_SECOND = 1e6
LIVE_WINDOW_S = 10.0
STANDING_HEIGHT_M = 1.75
WALKING_HEIGHT_M = 1.70
IMPACT_HEIGHT_M = 0.55
CHECKING_HEIGHT_M = 0.18
ALARM_HEIGHT_M = 0.15
BREATHING_HEIGHT_M = 0.02
BREATHING_RAD_S = 1.5
STEP_HEIGHT_M = 0.05
STEP_RAD_S = 9.0
WALK_RADIUS_X_M = 0.8
WALK_RADIUS_Y_M = 0.6
WALK_RAD_S = 0.8
FALLEN_XY_M = (0.2, -0.1)


@dataclass(frozen=True)
class Frame:
    time_s: float
    amplitude: np.ndarray
    rssi_dbm: float
    motion: float
    doppler_hz: float
    state: FallState
    alarm: bool
    latency_s: float | None
    x_m: float
    y_m: float
    vx_m_s: float
    vy_m_s: float
    height_m: float
    activity: float


class Pose(NamedTuple):
    x_m: float
    y_m: float
    vx_m_s: float
    vy_m_s: float
    height_m: float


def illustrative_pose(state, time_s):
    if state == FallState.CALM:
        height_m = STANDING_HEIGHT_M + BREATHING_HEIGHT_M * math.sin(time_s * BREATHING_RAD_S)
        return Pose(0.0, 0.0, 0.0, 0.0, height_m)
    if state == FallState.MOVING:
        phase = time_s * WALK_RAD_S
        return Pose(
            WALK_RADIUS_X_M * math.sin(phase),
            WALK_RADIUS_Y_M * math.cos(phase),
            WALK_RADIUS_X_M * WALK_RAD_S * math.cos(phase),
            -WALK_RADIUS_Y_M * WALK_RAD_S * math.sin(phase),
            WALKING_HEIGHT_M + STEP_HEIGHT_M * math.sin(time_s * STEP_RAD_S),
        )
    height_m = {
        FallState.IMPACT: IMPACT_HEIGHT_M,
        FallState.CHECKING_STILL: CHECKING_HEIGHT_M,
        FallState.ALARM: ALARM_HEIGHT_M,
    }[state]
    return Pose(*FALLEN_XY_M, 0.0, 0.0, height_m)


def _frames(analysis, indices):
    recording = analysis.recording
    detection = analysis.detection
    peaks_hz = peak_frequencies_hz(analysis.spectrogram)
    columns = np.abs(np.subtract.outer(recording.times_s[indices], analysis.spectrogram.times_s)).argmin(axis=1)
    strongest = max(float(np.max(np.abs(analysis.motion))), MOTION_EPSILON)
    frames = []
    for index, column in zip(indices, columns):
        time_s = float(recording.times_s[index])
        state = FallState(int(detection.states[index]))
        pose = illustrative_pose(state, time_s)
        motion = float(analysis.motion[index])
        frames.append(
            Frame(
                time_s=time_s,
                amplitude=recording.amplitude[index],
                rssi_dbm=float(recording.rssi_dbm[index]),
                motion=motion,
                doppler_hz=float(peaks_hz[column]),
                state=state,
                alarm=state == FallState.ALARM,
                latency_s=detection.latency_s if state == FallState.ALARM else None,
                x_m=pose.x_m,
                y_m=pose.y_m,
                vx_m_s=pose.vx_m_s,
                vy_m_s=pose.vy_m_s,
                height_m=pose.height_m,
                activity=float(np.clip(abs(motion) / strongest, MIN_ACTIVITY, MAX_ACTIVITY)),
            )
        )
    return frames


def frames_from_analysis(analysis: Analysis):
    return _frames(analysis, list(range(len(analysis.motion))))


class LiveTracker:
    def __init__(self):
        self._packets = {}
        self._origin_us = None
        self._latched = False
        self._latency_s = None

    def add(self, packet: Packet):
        if self._origin_us is None:
            self._origin_us = packet.timestamp_us
        window = self._packets.setdefault(packet.node_id, deque())
        window.append(packet)
        oldest_us = packet.timestamp_us - LIVE_WINDOW_S * MICROSECONDS_PER_SECOND
        while window[0].timestamp_us < oldest_us:
            window.popleft()

    def frame(self):
        if not self._packets:
            return None
        window = max(self._packets.values(), key=len)
        if len(window) < MIN_LIVE_SAMPLES:
            return None
        analysis = analyze_recording(recording_from_packets(list(window)))
        frame = _frames(analysis, [len(analysis.motion) - 1])[0]
        elapsed_s = (window[-1].timestamp_us - self._origin_us) / MICROSECONDS_PER_SECOND
        frame = replace(frame, time_s=elapsed_s)
        if frame.alarm:
            self._latched = True
            self._latency_s = frame.latency_s
        if self._latched:
            frame = replace(frame, alarm=True, latency_s=self._latency_s)
        return frame

    def reset_alarm(self):
        self._packets = {}
        self._latched = False
        self._latency_s = None
