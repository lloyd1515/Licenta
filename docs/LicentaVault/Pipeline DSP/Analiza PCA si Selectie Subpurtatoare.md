---
title: Analiza PCA si Selectie Subpurtatoare
tags:
  - dsp
  - pca
  - subpurtatoare
  - ofdm
aliases:
  - PCA
  - Selectie Subpurtatoare
---

# 🧠 Reducerea Dimensionalității: PCA pe 52 Subpurtătoare

Într-un mediu de interior cu reflexii multiple, undele Wi-Fi suferă de **fading selectiv în frecvență** (frequency-selective multipath fading). Cele 52 de subpurtătoare active nu reacționează identic la traversarea corpului uman:
* Unele subpurtătoare interferează constructiv (amplitudinea crește).
* Alte subpurtătoare interferează distructiv (amplitudinea se atenuează).

> [!danger] De ce simpla medie aritmetică e greșită
> O medie simplă peste cele 52 de canale ar provoca anularea distructivă reciprocă a variațiilor de fază și amplitudine, degradând dramatic raportul semnal-zgomot (SNR).

Implementarea completă se află în [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py).

---

## 1. Salubrizarea Subpurtătoarelor ([`drop_bad_subcarriers`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L51))

Conform studiului academic **Hernandez & Bulut (2021)**:
* Subpurtătoarele aproape inactive ($\text{Var} < 0.05$, `MIN_SUBCARRIER_VARIANCE`) conțin doar zgomot rezidual.
* Subpurtătoarele de la marginea benzii cu varianță extremă ($\text{Var} > 350.0$, `MAX_SUBCARRIER_VARIANCE`) sunt afectate de filtrele hardware analogice de bandă.
* Funcția maschează și elimină canalele degenerate înainte de extragerea vectorilor proprii:

```python
def drop_bad_subcarriers(amplitude):
    variance = np.var(amplitude, axis=0)
    valid = (variance >= MIN_SUBCARRIER_VARIANCE) & (variance <= MAX_SUBCARRIER_VARIANCE)
    if not np.any(valid):
        return amplitude
    return amplitude[:, valid]
```

---

## 2. Formularea Matematică PCA ([`motion_signal`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L66))

1. **Centrarea Datelor:**
   Fie matricea de amplitudini filtrate $X \in \mathbb{R}^{N \times K}$ (unde $N$ este numărul de eșantioane și $K \le 52$):
   $$
   \tilde{X} = X - \mu_X
   $$
2. **Matricea de Covarianță:**
   $$
   \Sigma = \frac{1}{N-1} \tilde{X}^T \tilde{X} \in \mathbb{R}^{K \times K}
   $$
3. **Descompunerea în Valori și Vectori Proprii:**
   $$
   \Sigma v_i = \lambda_i v_i, \quad \lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_K
   $$
   Vectorul $v_1$ (corespunzător celei mai mari valori proprii $\lambda_1$) indică direcția de variație maximă corelată cu deplasarea corpului uman.
4. **Proiecția Semnalului (PC1):**
   $$
   s_{\text{PC1}} = \tilde{X} v_1 \in \mathbb{R}^N
   $$

```python
def motion_signal(amplitude):
    centered = amplitude - np.mean(amplitude, axis=0)
    covariance = np.cov(centered, rowvar=False)
    _, eigenvectors = np.linalg.eigh(covariance)
    return np.dot(centered, eigenvectors[:, -1])
```

Semnalul scalar $s_{\text{PC1}}(t)$ are SNR maxim și este transmis direct către detectorul FSM ([[Detector Cadere FSM]]) și modulul de localizare ([[Localizare 2D Elipse Fresnel]]).
