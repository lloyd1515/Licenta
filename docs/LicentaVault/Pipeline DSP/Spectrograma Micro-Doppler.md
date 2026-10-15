---
title: Spectrograma Micro-Doppler
tags:
  - dsp
  - doppler
  - stft
  - frecventa
aliases:
  - Doppler
  - STFT
---

# ⚡ Analiza Micro-Doppler prin STFT

O cădere umană implică o accelerare verticală rapidă a masei corporale către podea sub acțiunea gravitației ($g \approx 9.81\text{ m/s}^2$). Această cinematică generează o deplasare Doppler caracteristică pe unda reflectată.

Implementat în [`spectrogram`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L73) din [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py).

---

## 📐 Fizica Deplasării Doppler Wi-Fi

Pentru o lungime de undă $\lambda = 0.123\text{ m}$ (Canal 6 la $2.437\text{ GHz}$, `WAVELENGTH_M` din `room.py`), deplasarea Doppler instantanee este:

$$
f_D(t) = \frac{2 v(t)}{\lambda} \cos \theta
$$

* **Mers obișnuit ($v \approx 0.8 - 1.2\text{ m/s}$):**
  $$f_D \approx 10\text{ Hz} - 20\text{ Hz}$$
* **Cădere accelerată ($v > 2.5\text{ m/s}$):**
  $$f_D = \frac{2 \times 2.8}{0.123} \approx 45.5\text{ Hz}$$
* **Prăbușire la sol (imobilitate):**
  $$f_D \approx 0\text{ Hz}$$

Pragul de referință utilizat pentru marcarea căderii este `DOPPLER_REFERENCE_HZ = 35.0` Hz.

> [!important] De ce semnalul pentru Doppler NU trece prin Butterworth 12 Hz
> Filtrul Butterworth taie componentele peste 12 Hz pentru anvelopa de poziție. Dacă am aplica STFT pe semnalul filtrat Butterworth, vârful critic de cădere (>35 Hz) ar fi complet anihilat! De aceea, STFT se calculează direct pe semnalul curățat cu Hampel (bandă largă), fie pe o subpurtătoare aleasă (ex: index 10), fie pe media amplitudinii.

---

## 🎛️ Parametrii STFT (Short-Time Fourier Transform)

```python
def spectrogram(signal_1d, rate_hz, window, overlap):
    centered = signal_1d - np.mean(signal_1d)
    freqs_hz, times_s, stft = signal.stft(
        centered, fs=rate_hz, window="hann", nperseg=window, noverlap=overlap, return_onesided=True
    )
    power_db = 10 * np.log10(np.abs(stft) ** 2 + 1e-6)
    return Spectrogram(times_s, freqs_hz, power_db)
```

* **Fereastră:** Hann (`nperseg = 64`, `noverlap = 56` pentru figuri de înaltă rezoluție).
* **Putere calculată (dB):** $P(t, f) = 10 \log_{10} (|Z_{xx}(t, f)|^2 + 10^{-6})$.

---

## 📊 Semnătura Doppler a Căderii

![[2_doppler_spectrogram.png|800]]

*Se observă clar tranziția triplă: (1) Mers normal sub 20 Hz, (2) Explozie scurtă la cădere depășind pragul critic de 35 Hz, (3) Liniște radio la sol (0 Hz).*
