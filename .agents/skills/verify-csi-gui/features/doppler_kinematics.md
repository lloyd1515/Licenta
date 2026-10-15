# Feature: Doppler Kinematics & Velocity Profile

## 1. Kinematic Velocity Mapping
Physical relationship between human body velocity $v$ and Doppler frequency $f_D$:
$$f_D = \frac{2v}{\lambda} \cos \theta$$
At $f_c = 2.437\text{ GHz}$, $\lambda \approx 12.3\text{ cm}$.

| Action | Velocity ($v$) | Expected Doppler ($f_D$) |
|---|---|---|
| Stationary / Breathing | $0.0 - 0.1\text{ m/s}$ | $< 2.0\text{ Hz}$ |
| Normal Walking | $0.8 - 1.2\text{ m/s}$ | $13 - 19\text{ Hz}$ |
| Rapid Human Fall | $2.5 - 4.5\text{ m/s}$ | $> 35.0\text{ Hz}$ |

## 2. Visualization Contract
- Live time-history line plot showing peak estimated Doppler frequency over a rolling 100-frame window.
- Red dashed threshold line permanently rendered at $35.0\text{ Hz}$.
- Visual alert state triggers when curve crosses above the $35.0\text{ Hz}$ boundary.
