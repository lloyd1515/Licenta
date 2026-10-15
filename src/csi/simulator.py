from dataclasses import dataclass

import numpy as np

from csi.room import (
    CENTER_FREQ_HZ,
    LINKS,
    NODE_POSITIONS_M,
    SPEED_OF_LIGHT_M_S,
    SUBCARRIER_INDICES,
    SUBCARRIER_SPACING_HZ,
    WAVELENGTH_M,
    extra_path_m,
    link_name,
)

SIMULATION_RATE_HZ = 250.0
SIMULATION_DURATION_S = 20.0
STILL_END_S = 3.0
WALK_END_S = 10.0
FALL_END_S = 10.35
STANDING_HEIGHT_M = 1.7
LYING_HEIGHT_M = 0.2
WALK_SPEED_M_S = 0.95
START_XY_M = (1.8, 1.8)
FALL_XY_M = (0.1, 0.0)
SPIKE_FRACTION = 0.008
SPIKE_GAIN_RANGE = (1.8, 3.2)
GAIT_BOB_M = 0.04
GAIT_BOB_HZ = 2.0
FALL_DROP_M = STANDING_HEIGHT_M - LYING_HEIGHT_M
FALL_PEAK_SPEED_M_S = 2.8
DOPPLER_MIN_SPEED_M_S = 1.5
STATIC_PATH_LOSS_EXPONENT = 1.8
BODY_REFLECTION = 0.35
FALLEN_REFLECTION = 0.85
FRESNEL_SCALE = 1.5

SUBCARRIER_WAVELENGTHS_M = SPEED_OF_LIGHT_M_S / (
    CENTER_FREQ_HZ + np.array(SUBCARRIER_INDICES) * SUBCARRIER_SPACING_HZ
)


@dataclass(frozen=True)
class Trajectory:
    times_s: np.ndarray
    x_m: np.ndarray
    y_m: np.ndarray
    height_m: np.ndarray
    speed_m_s: np.ndarray
    fallen: np.ndarray
    fall_start_index: int


@dataclass(frozen=True)
class SimulatedCsi:
    trajectory: Trajectory
    rate_hz: float
    csi_by_link: dict


def make_trajectory(duration_s=SIMULATION_DURATION_S, rate_hz=SIMULATION_RATE_HZ):
    count = int(duration_s * rate_hz)
    times_s = np.linspace(0, duration_s, count)
    x_m = np.zeros(count)
    y_m = np.zeros(count)
    height_m = np.ones(count) * STANDING_HEIGHT_M
    speed_m_s = np.zeros(count)
    fallen = np.zeros(count, dtype=bool)

    walk_start = int(STILL_END_S * rate_hz)
    fall_start = int(WALK_END_S * rate_hz)
    fall_end = int(FALL_END_S * rate_hz)

    x_m[:walk_start] = START_XY_M[0]
    y_m[:walk_start] = START_XY_M[1]

    walk_progress = np.linspace(0, 1, fall_start - walk_start)
    x_m[walk_start:fall_start] = START_XY_M[0] - (START_XY_M[0] - FALL_XY_M[0]) * walk_progress
    y_m[walk_start:fall_start] = START_XY_M[1] - (START_XY_M[1] - FALL_XY_M[1]) * walk_progress
    height_m[walk_start:fall_start] = STANDING_HEIGHT_M + GAIT_BOB_M * np.sin(
        2 * np.pi * GAIT_BOB_HZ * times_s[walk_start:fall_start]
    )
    speed_m_s[walk_start:fall_start] = WALK_SPEED_M_S

    fall_progress = np.linspace(0, 1, fall_end - fall_start)
    x_m[fall_start:fall_end] = FALL_XY_M[0]
    y_m[fall_start:fall_end] = FALL_XY_M[1]
    height_m[fall_start:fall_end] = STANDING_HEIGHT_M - FALL_DROP_M * fall_progress**2
    speed_m_s[fall_start:fall_end] = FALL_PEAK_SPEED_M_S * fall_progress
    fallen[fall_start:] = True

    x_m[fall_end:] = FALL_XY_M[0]
    y_m[fall_end:] = FALL_XY_M[1]
    height_m[fall_end:] = LYING_HEIGHT_M

    return Trajectory(times_s, x_m, y_m, height_m, speed_m_s, fallen, fall_start)


def _link_csi(trajectory, link, snr_db, add_spikes, rng):
    tx = np.array(NODE_POSITIONS_M[link[0]])
    rx = np.array(NODE_POSITIONS_M[link[1]])
    direct_m = np.linalg.norm(rx - tx)
    count = len(trajectory.times_s)

    static = direct_m ** -STATIC_PATH_LOSS_EXPONENT * np.exp(-1j * 2 * np.pi * direct_m / SUBCARRIER_WAVELENGTHS_M)

    points = np.stack([trajectory.x_m, trajectory.y_m], axis=1)
    extra_m = extra_path_m(points, link)
    reflected_m = extra_m + direct_m
    fresnel_radius_m = 0.5 * np.sqrt(WAVELENGTH_M * direct_m)
    reflection = np.where(
        trajectory.fallen,
        FALLEN_REFLECTION,
        BODY_REFLECTION * np.exp(-extra_m / (fresnel_radius_m * FRESNEL_SCALE)),
    )
    phase = -2 * np.pi * reflected_m[:, None] / SUBCARRIER_WAVELENGTHS_M
    dynamic = reflection[:, None] * np.exp(1j * phase)

    doppler_phase = 2 * np.pi * (2 * trajectory.speed_m_s / WAVELENGTH_M) * trajectory.times_s
    fast = trajectory.speed_m_s > DOPPLER_MIN_SPEED_M_S
    dynamic[fast] *= np.exp(1j * doppler_phase[fast])[:, None]

    csi = static + dynamic

    noise_power = np.mean(np.abs(csi) ** 2) / (10 ** (snr_db / 10.0))
    noise = rng.standard_normal(csi.shape) + 1j * rng.standard_normal(csi.shape)
    csi = csi + noise * np.sqrt(noise_power / 2)

    if add_spikes:
        spike_rows = rng.choice(count, size=int(count * SPIKE_FRACTION), replace=False)
        csi[spike_rows] *= rng.uniform(*SPIKE_GAIN_RANGE, size=(len(spike_rows), 1))
    return csi


def simulate_csi(trajectory, snr_db=22.0, add_spikes=True, seed=0):
    rng = np.random.default_rng(seed)
    csi_by_link = {
        link_name(link): _link_csi(trajectory, link, snr_db, add_spikes, rng) for link in LINKS
    }
    rate_hz = float(round(1.0 / (trajectory.times_s[1] - trajectory.times_s[0])))
    return SimulatedCsi(trajectory, rate_hz, csi_by_link)
