---
title: Simulator Sintetic CSI
tags:
  - date
  - simulare
  - dsp
  - model-fizic
aliases:
  - Simulator
  - Synthetic Gen
---

# 💻 Simulatorul Sintetic CSI Fizic

Pentru a dezvolta și valida algoritmii fără a depinde în fiecare moment de hardware-ul radio, a fost dezvoltat un simulator bazat pe fizica propagării undelor în [`src/csi/simulator.py`](file:///home/vlads4r4/dev/Licenta/src/csi/simulator.py).

---

## 🏃 Modelul Traiectoriei Umane ([`make_trajectory`](file:///home/vlads4r4/dev/Licenta/src/csi/simulator.py#L62))

Scenariul prestabilit durează $20\text{ secunde}$ (`SIMULATION_DURATION_S`) la o frecvență de eșantionare $f_s = 250\text{ Hz}$ (`SIMULATION_RATE_HZ`):
1. **$0 - 3\text{ s}$ (Staționar, `STILL_END_S`):** Persoana stă nemișcată la coordonata $(1.8, 1.8)\text{ m}$ (`START_XY_M`, înălțime $z = 1.7\text{ m}$).
2. **$3 - 10\text{ s}$ (Mers activ, `WALK_END_S`):** Deplasare diagonală către $(0.1, 0.0)\text{ m}$ (`FALL_XY_M`) cu viteză de $0.95\text{ m/s}$ (`WALK_SPEED_M_S`) și balans vertical fiziologic al pasului:
   $$z(t) = 1.7 + 0.04 \sin(2\pi \times 2.0 \times t)$$
3. **$10 - 10.35\text{ s}$ (Cădere violentă, `FALL_END_S`):** Prăbușire accelerată în $350\text{ ms}$:
   $$z(t) = 1.7 - 1.5 \tau^2, \quad v(t) = 2.8 \tau \text{ m/s}$$
4. **$10.35 - 20\text{ s}$ (Imobilitate la sol):** Corpul rămâne inert la podea ($z = 0.2\text{ m}$, `LYING_HEIGHT_M`, $v = 0$).

---

## 📡 Modelul Canalului Radio ([`simulate_csi`](file:///home/vlads4r4/dev/Licenta/src/csi/simulator.py#L136))

Funcția `simulate_csi(trajectory, snr_db=22.0, add_spikes=True, seed=0)` oferă control determinist complet prin parametrul `seed` (generat prin `np.random.default_rng(seed)`):

$$
H(t, k) = H_{\text{static}}(k) + H_{\text{dinamic}}(t, k) + n_{\text{AWGN}}(t, k)
$$

### 1. Componenta Statică (LOS + Pereți):
$$
H_{\text{static}}(k) = \frac{1}{d_{\text{direct}}^{1.8}} \exp\left( -j \frac{2\pi d_{\text{direct}}}{\lambda_k} \right)
$$
Exponentul pierderii de cale: `STATIC_PATH_LOSS_EXPONENT = 1.8`.

### 2. Componenta Dinamică (Reflexie Corp Uman):
* Secțiunea transversală radar (RCS): modelată în funcție de distanța la elipsa Fresnel (`extra_path_m`) și starea corpului (`BODY_REFLECTION = 0.35`, iar la cădere `FALLEN_REFLECTION = 0.85`).
* Fază Doppler injectată la viteze mari ($v > 1.5\text{ m/s}$, `DOPPLER_MIN_SPEED_M_S`):
  $$H_{\text{dinamic}} \propto \text{RCS} \cdot \exp\left( -j \frac{2\pi d_{\text{refl}}}{\lambda_k} \right) \exp\left( j 2\pi f_D t \right)$$

### 3. Zgomot și Spike-uri LNA:
* Zgomot termic Gaussian AWGN calculat din `snr_db` (implicit $22.0\text{ dB}$).
* Spike-uri LNA: $0.8\%$ din eșantioane (`SPIKE_FRACTION = 0.008`) sunt amplificate aleator cu factori între $1.8$ și $3.2$ (`SPIKE_GAIN_RANGE`).

---

## 📈 Rularea Simulării și Generarea Figurilor

Pentru generarea figurilor sintetice (1–4) ale tezei în [`src/csi/plots/`](file:///home/vlads4r4/dev/Licenta/src/csi/plots):
```bash
python -m csi.figures synthetic
```
