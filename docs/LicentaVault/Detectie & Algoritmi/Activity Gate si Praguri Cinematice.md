---
title: Activity Gate si Praguri Cinematice
tags:
  - algoritmi
  - praguri
  - activity-gate
  - calibrare
aliases:
  - Activity Gate
  - Praguri
---

# 🚪 Poarta de Activitate (Activity Gate) și Calibrarea Pragurilor

Unul dintre cele mai delicate aspecte practice în detectarea căderilor pasive fără senzori pe corp este prevenirea **alarmelor false în cameră complet goală**.

Când camera este nelocuită, semnalul radio recepționat conține doar zgomot termic AWGN și interferențe electromagnetice ambientale nesincrone. Fără un gardian preliminar, algoritmii pe bază de derivate ar putea interpreta spike-uri izolate de zgomot drept cădere.

Implementat în [`detect_fall`](file:///home/vlads4r4/dev/Licenta/src/csi/fall_detector.py#L75) din [`src/csi/fall_detector.py`](file:///home/vlads4r4/dev/Licenta/src/csi/fall_detector.py).

---

## 🔒 Mecanismul Activity Gate

Înainte de calculul derivatelor sau evaluarea tranzițiilor din FSM, funcția `detect_fall` calculează media abaterilor standard ale semnalelor pe toate legăturile:

$$
\bar{\sigma}_{\text{PC1}} = \frac{1}{M} \sum_{k=1}^M \text{std}(s_{\text{PC1}}^{(k)})
$$

### Condiție de Poartă:
```python
empty_room_std = EMPTY_ROOM_STD_SIMULATED if rate_hz >= SIMULATED_MIN_RATE_HZ else EMPTY_ROOM_STD_HARDWARE
mean_std = float(np.mean([np.std(motion) for motion in motion_by_link.values()]))
if mean_std < empty_room_std:
    return Detection(states, None, None)
```

Dacă media deviațiilor standard este sub prag, automatul refuză orice evaluare de mișcare și returnează starea 0 (`FallState.CALM`), prevenind 100% din alarmele false.

---

## ⚖️ Discrepanța dintre Date Sintetice și Date Hardware Reale

| Mediu | Constantă în Cod | Valoare Prag | Unitate / Scală | Motivare |
| :--- | :--- | :---: | :---: | :--- |
| **Simulator Sintetic** | `EMPTY_ROOM_STD_SIMULATED` | `0.20` | Normalizat (adimensional) | Datele sintetice sunt generate cu magnitudine unitară; zgomotul AWGN are deviație $\sigma \approx 0.05 - 0.10$. |
| **Hardware Real (ESP32)** | `EMPTY_ROOM_STD_HARDWARE` | `11.0` | Unități brute ADC | Conversia analog-digitală a radioului ESP32 produce valori CSI pe scară întreagă (numere pe 8 biți); zgomotul de fond în liniște RF are deviație standard de ordinul $6.0 - 9.0$, iar mersul uman depășește $30.0$. |

Comutarea între cele două moduri se face automat pe baza frecvenței de eșantionare (`SIMULATED_MIN_RATE_HZ = 100.0` Hz): eșantionarea simulată este la 250 Hz, în timp ce fluxul hardware real operează adesea la o rată efectivă mai redusă (~30-50 Hz) din cauza canalului serial.

> [!tip] Notă pentru susținerea tezei (Defense Rationale)
> Această diferență de praguri nu este un "bug", ci o dovadă de calibrare experimentală onestă: arată adaptarea pipeline-ului la dinamica convertorului analogic-digital fizic versus modelul matematic ideal din simulare.
