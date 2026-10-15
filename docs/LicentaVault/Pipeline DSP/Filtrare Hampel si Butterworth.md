---
title: Filtrare Hampel si Butterworth
tags:
  - dsp
  - filtrare
  - hampel
  - butterworth
aliases:
  - Hampel
  - Butterworth
  - Filtrare
---

# 🧹 Condiționarea Semnalului: Filtrele Hampel și Butterworth

Semnalul brut CSI obținut de la cipurile ESP32 suferă de două surse majore de degradare:
1. **Spike-uri LNA (Low-Noise Amplifier):** Comutarea treptelor automate de amplificare ale radioului generează salturi artificiale uriașe pe eșantioane individuale.
2. **Componenta continuă (DC drift):** Reflexiile statice puternice din pereți și mobilier generează un offset constant masiv care maschează perturbația fină produsă de corpul uman.

Implementarea se găsește în [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py).

---

## 1. Filtrul Hampel Adaptiv ([`remove_outliers`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L38))

Filtrul Hampel detectează și înlocuiește valorile aberante (outliers) dintr-o fereastră glisantă folosind **Abaterea Mediană Absolută** (**MAD - Median Absolute Deviation**), o măsură statistică robustă implementată vectorizat prin `numpy.lib.stride_tricks.sliding_window_view`:

$$
\text{MAD} = 1.4826 \times \text{median}(|x_i - \text{median}(x)|)
$$

### Criteriu de Înlocuire:
Dacă $|x_i - \text{median}(x)| > 3.0 \times \text{MAD}$, valoarea $x_i$ este considerată spike LNA și este înlocuită cu mediana locală.

```python
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
```

---

## 2. Filtrul Butterworth Trece-Bandă IIR ([`bandpass`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L59))

* **Tip:** IIR Butterworth de ordinul 4 (`BAND_ORDER = 4`).
* **Bandă utilă:** `BAND_LOW_HZ = 0.2` – `BAND_HIGH_HZ = 12.0` Hz (banda specifică deplasărilor umane).
* **Filtrare Zero-Phase:** Se aplică `scipy.signal.filtfilt` (înainte și înapoi pe axa temporală), garantând **întârziere de fază zero** (zero-phase distortion), esențială pentru sincronizarea corectă a momentului impactului.

### De ce 0.2 Hz - 12.0 Hz?
* **Sub 0.2 Hz:** Se taie componenta continuă (LOS static și pereții imobili).
* **Peste 12 Hz:** Se elimină zgomotul termic AWGN de înaltă frecvență din anvelopa de amplitudine.

---

## 📈 Comparație Vizuală (Brut vs Filtrate)

![[1_raw_vs_filtered_csi.png|800]]

*Graficul superior arată semnalul brut cu spike-uri LNA; graficul median arată semnalul netezit prin filtrul Hampel; graficul inferior prezintă semnalele PC1 filtrate pe cele 3 legături.*
