from typing import NamedTuple

import numpy as np
from scipy.optimize import least_squares

from csi.room import LINKS, ROOM_HALF_SIZE_M, extra_path_m
from csi.simulator import START_XY_M, STILL_END_S, WALK_END_S

RANGE_NOISE_STD_M = 0.07
MIN_NOISY_EXTRA_PATH_M = 0.01
SMOOTHING = 0.4


class Track(NamedTuple):
    times_s: np.ndarray
    x_m: np.ndarray
    y_m: np.ndarray
    rmse_m: float


def locate(extra_paths_m, start_xy=(0.0, 0.0)):
    def residuals(point):
        return np.array([extra_path_m(point, link) - extra_paths_m[i] for i, link in enumerate(LINKS)])

    bound = ROOM_HALF_SIZE_M
    result = least_squares(residuals, start_xy, bounds=([-bound, -bound], [bound, bound]), method="trf")
    return result.x[0], result.x[1]


def track_with_noisy_ranges(trajectory, step=10, seed=0):
    rng = np.random.default_rng(seed)
    indices = np.arange(0, len(trajectory.times_s), step)
    estimate = np.array(START_XY_M)
    x_m = []
    y_m = []
    for i in indices:
        true_point = (trajectory.x_m[i], trajectory.y_m[i])
        measured = [
            max(MIN_NOISY_EXTRA_PATH_M, extra_path_m(true_point, link) + rng.normal(0, RANGE_NOISE_STD_M))
            for link in LINKS
        ]
        solution = np.array(locate(np.array(measured), start_xy=estimate))
        estimate = (1 - SMOOTHING) * estimate + SMOOTHING * solution
        x_m.append(estimate[0])
        y_m.append(estimate[1])
    x_m = np.array(x_m)
    y_m = np.array(y_m)

    times_s = trajectory.times_s[indices]
    walking = (times_s >= STILL_END_S) & (times_s <= WALK_END_S)
    errors = np.hypot(x_m[walking] - trajectory.x_m[indices][walking], y_m[walking] - trajectory.y_m[indices][walking])
    rmse_m = float(np.sqrt(np.mean(errors**2)))
    return Track(times_s, x_m, y_m, rmse_m)
