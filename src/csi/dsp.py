from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy import signal

from csi.fall_detector import Detection, detect_fall
from csi.packets import Recording

MAD_TO_SIGMA = 1.4826
MAD_EPSILON = 1e-6
MIN_SUBCARRIER_VARIANCE = 0.05
MAX_SUBCARRIER_VARIANCE = 350.0
BAND_LOW_HZ = 0.2
BAND_HIGH_HZ = 12.0
BAND_ORDER = 4
NYQUIST_MARGIN = 2.1
MAX_WINDOW = 32
MIN_WINDOW = 16
WINDOW_DIVISOR = 8


class Spectrogram(NamedTuple):
    times_s: np.ndarray
    freqs_hz: np.ndarray
    power_db: np.ndarray


@dataclass(frozen=True)
class Analysis:
    recording: Recording
    motion: np.ndarray
    spectrogram: Spectrogram
    detection: Detection


def remove_outliers(amplitude, window=7, sigmas=3.0):
    half = window // 2
    cleaned = amplitude.copy()
    if len(amplitude) < 2 * half + 1:
        return cleaned
    windows = sliding_window_view(amplitude, 2 * half + 1, axis=0)
    median = np.median(windows, axis=-1)
    mad = MAD_TO_SIGMA * np.median(np.abs(windows - median[..., None]), axis=-1) + MAD_EPSILON
    centre = amplitude[half:len(amplitude) - half]
    cleaned[half:len(amplitude) - half] = np.where(np.abs(centre - median) > sigmas * mad, median, centre)
    return cleaned


def drop_bad_subcarriers(amplitude):
    variance = np.var(amplitude, axis=0)
    valid = (variance >= MIN_SUBCARRIER_VARIANCE) & (variance <= MAX_SUBCARRIER_VARIANCE)
    if not np.any(valid):
        return amplitude
    return amplitude[:, valid]


def bandpass(amplitude, rate_hz, low_hz=BAND_LOW_HZ, high_hz=BAND_HIGH_HZ):
    nyquist_hz = 0.5 * rate_hz
    high_hz = min(high_hz, rate_hz / NYQUIST_MARGIN)
    b, a = signal.butter(BAND_ORDER, [low_hz / nyquist_hz, high_hz / nyquist_hz], btype="band")
    return signal.filtfilt(b, a, amplitude, axis=0)


def motion_signal(amplitude):
    centered = amplitude - np.mean(amplitude, axis=0)
    covariance = np.cov(centered, rowvar=False)
    _, eigenvectors = np.linalg.eigh(covariance)
    return np.dot(centered, eigenvectors[:, -1])


def spectrogram(signal_1d, rate_hz, window, overlap):
    centered = signal_1d - np.mean(signal_1d)
    freqs_hz, times_s, stft = signal.stft(
        centered, fs=rate_hz, window="hann", nperseg=window, noverlap=overlap, return_onesided=True
    )
    power_db = 10 * np.log10(np.abs(stft) ** 2 + 1e-6)
    return Spectrogram(times_s, freqs_hz, power_db)


def peak_frequencies_hz(spec):
    return spec.freqs_hz[np.argmax(spec.power_db, axis=0)]


def analyze_recording(recording):
    cleaned = drop_bad_subcarriers(recording.amplitude)
    motion = motion_signal(bandpass(cleaned, recording.rate_hz))
    window = min(MAX_WINDOW, max(MIN_WINDOW, len(motion) // WINDOW_DIVISOR))
    spec = spectrogram(np.mean(recording.amplitude, axis=1), recording.rate_hz, window, window // 2)
    detection = detect_fall(recording.times_s, {"node": motion}, recording.rate_hz)
    return Analysis(recording, motion, spec, detection)
