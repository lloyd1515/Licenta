# Feature: DSP Signal Conditioning Pipeline

## 1. Subcarrier Sanitization (Hernandez & Bulut, 2021)
Raw ESP32 CSI frames contain dead zero-subcarriers (indices 21 to 30) and pilot noise artifacts (indices 1 to 6) exhibiting $\sigma^2 > 1000$.
`sanitize_subcarriers` applies a variance filter ($0.05 \le \sigma^2 \le 350$) to isolate valid dynamic multipath channels.

## 2. Bandpass Filtering
Static multipath reflections from walls and fixed furniture appear at DC ($f \approx 0$).
A 4th-order Butterworth IIR bandpass filter (0.2 Hz to 12.0 Hz) attenuates static DC and high-frequency RF thermal noise while preserving human gait oscillations (0.5 to 3.0 Hz).

## 3. Principal Component Analysis (PCA)
Calculates the covariance matrix across valid subcarriers and projects onto the first eigenvector $\mathbf{v}_1$:
$$\text{PC1}(t) = (\mathbf{S}(t) - \boldsymbol{\mu}) \cdot \mathbf{v}_1$$
This extracts the dominant human kinematic trajectory while cancelling uncorrelated noise.

## 4. STFT Doppler Spectrogram
STFT with Hann window computes the micro-Doppler time-frequency signature:
$$P(t, f) = 10 \log_{10} (|X(t, f)|^2 + 10^{-6})$$
High-frequency Doppler energy ($> 35\text{ Hz}$) indicates accelerated gravitational collapse.
