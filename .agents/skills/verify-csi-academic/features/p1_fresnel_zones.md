# Feature: Fresnel Zone Theory & Spatial Fringe Modulation

## Reference
[P1] Daqing Zhang, Hao Wang, Dan Wu. *Fresnel Zone Based Theory for Device-Free Human Activity Identification*, IEEE/ACM Transactions on Networking (ToN), Vol. 25, No. 6, pp. 3643-3656, Dec. 2017.

## Sub-features
- Central frequency $f_c = 2.437\text{ GHz}$ $\rightarrow$ wavelength $\lambda = 12.31\text{ cm}$.
- Zone radius $r_n = \sqrt{n \lambda D / 4}$ at midpoint ($r_1 \approx 30.4\text{ cm}$ for $D = 3\text{ m}$).
- Half-wavelength modulation: walking across boundary produces sinusoidal envelope with period $\Delta d = \lambda/2 \approx 6.15\text{ cm}$.

## How to get to it (user POV)
- In [`gui/app.py`](file:///home/vlads4r4/dev/Licenta/gui/app.py), observe the 2D room map: the concentric dashed ellipses connecting ESP32 nodes represent the first two Fresnel zones.
- When an object/person enters the Fresnel zone, line thickness and glow pulse dynamically.

## Driving it with harness
Run the verification auditor:
```bash
.venv/bin/python .agents/skills/verify-csi-academic/scripts/verify_academic_compliance.py
```
Assert that `P1_fresnel` passes wavelength and radius tolerances.

## Gotchas
- Fresnel theory assumes line-of-sight (LOS) dominant component. In heavy multipath clutter, Rician K-factor drops, attenuating fringe contrast.
