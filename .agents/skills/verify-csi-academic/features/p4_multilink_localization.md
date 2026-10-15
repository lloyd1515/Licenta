# Feature: Multi-Link 2D Localization by Ellipse Intersection

## Reference
[P4] Chunshan Liu, Daqing Zhang, Jie Xiong, Jingrong Wang. *Multi-Link Fresnel Zone Model for Indoor Human Localization*, IEEE Transactions on Vehicular Technology, Vol. 68, No. 11, 2019.

## Sub-features
- Non-linear path excess equations:
  $$\Delta d_i = \|P - T_i\| + \|P - R_i\| - \|R_i - T_i\|, \quad i \in \{1, 2, 3\}$$
- **Rank Condition:**
  - $N=1$ link: Rank of Jacobian is 1 $\rightarrow$ locus of solutions is an entire confocal ellipse (infinite ambiguous solutions).
  - $N=2$ links: Up to 4 ambiguous intersection points.
  - $N=3$ non-collinear links: Jacobian has full column rank 2 in $\mathbb{R}^2$. Yields unique Cartesian coordinates $(x, y)$.
- Numerical solver: Levenberg-Marquardt (scipy `least_squares` with TRF bounds inside room dimensions).

## How to get to it (user POV)
- In [`gui/app.py`](file:///home/vlads4r4/dev/Licenta/gui/app.py), observe the top-left 2D room map (`RoomMapWidget`). The green target shows the reconstructed $(x, y)$ coordinate in meters.

## Driving it with harness
```bash
.venv/bin/python .agents/skills/verify-csi-academic/scripts/verify_academic_compliance.py
```
Checks:
- Full column rank of the 3-link Jacobian matrix ($rank(J) = 2$).
- Reconstruction error on known target positions ($RMSE < 0.40\text{ m}$).

## Gotchas
- If fewer than 3 spatial links are active (e.g. only 2 ESP32 nodes powered), exact 2D Cartesian intersection cannot be mathematically solved. The platform must clearly indicate single-link ambiguity rather than hallucinating $(x, y)$ points.
