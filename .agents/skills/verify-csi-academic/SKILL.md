---
name: verify-csi-academic
description: "Audits Wi-Fi CSI sensing, Fresnel models, Doppler signatures, and fall FSM against canonical academic papers [P1]-[P4] (Zhang 2017, Hernandez 2021, Wang 2014, Liu 2019)."
---

# verify-csi-academic

Rigorous academic verification skill that benchmarks the repository's CSI DSP pipeline against the 4 seminal peer-reviewed papers cited in the graduation thesis.

## 1. Grounding Papers

- **[P1] Zhang et al. (IEEE/ACM ToN 2017)**: *Fresnel Zone Based Theory for Device-Free Human Activity Identification*.
- **[P2] Hernandez & Bulut (IEEE IoTJ 2021)**: *Wi-Fi Sensing on the Edge: Who and Where are You?* (ESP32-CSI-Tool).
- **[P3] Wang et al. (ACM MobiCom 2014)**: *RT-Fall: Device-Free Fall Detection by Retrieving Spatial and Temporal Information*.
- **[P4] Liu et al. (IEEE TVT 2019)**: *Multi-Link Fresnel Zone Model for Indoor Human Localization*.

## 2. Launch

To run the full academic compliance verification suite:
```bash
.venv/bin/python .agents/skills/verify-csi-academic/scripts/verify_academic_compliance.py
```

## 3. Doctor

Before driving verification, check mathematical and environment prerequisites:
1. Python environment contains `numpy`, `scipy`.
2. Reference datasets exist in `dsp_lab/test_*.npz`.
3. Check status:
```bash
.venv/bin/python -c "import numpy, scipy; from dsp_lab.filters import butterworth_bandpass; print('Academic Doctor: OK')"
```

## 4. Drive

Run targeted verification per paper:
- **P1 Audit:** Fresnel wavelength $\lambda = 12.31\text{ cm}$, $r_1 \approx 30.4\text{ cm}$ @ 3m, spatial fringe $\lambda/2 \approx 6.15\text{ cm}$.
- **P2 Audit:** Subcarrier count (52 active OFDM HT20), non-zero active mask, packet rate check ($f_s \ge 100\text{ Hz}$).
- **P3 Audit:** Fall kinematics: peak Doppler $>35\text{ Hz}$, duration $<400\text{ ms}$, post-fall dormancy $\ge 2.0\text{ s}$ with $\text{var} < \sigma_{\text{calm}}^2$.
- **P4 Audit:** 3-link non-linear least squares solvability (Levenberg-Marquardt), full column rank $J$ matrix, RMSE error $<0.40\text{ m}$.

## 5. Evidence

All audit executions generate structured JSON proof:
- Output file: `.agents/skills/verify-csi-academic/evidence/academic_compliance_report.json`
- Proof metrics:
  - Exact calculated numerical values vs. theoretical thresholds.
  - Per-paper pass/fail status and warning flags.

## 6. Cleanup

Audit scripts operate deterministically and read-only on datasets. No running daemon processes are left behind. Evidence files are preserved in `evidence/`.
