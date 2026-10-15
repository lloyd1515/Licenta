# Feature: ESP32 CSI Subcarrier Processing & Sanitization

## Reference
[P2] Steven M. Hernandez, Eyuphan Bulut. *Wi-Fi Sensing on the Edge: Who and Where are You?*, IEEE Internet of Things Journal, Vol. 8, No. 12, pp. 9508-9519, 2021.

## Sub-features
- 52 active OFDM subcarriers in 20 MHz HT20 band ($[-26 \dots -1, 1 \dots 26]$).
- Extraction of raw $I/Q$ signed 8-bit bytes from ESP-IDF binary structure (`0xA55A` magic).
- Rejection of pilot DC subcarrier (index 0) and edge nulls.
- Sampling rate requirement: $f_s \ge 100\text{ Hz}$ to avoid Nyquist aliasing on human movement.

## How to get to it (user POV)
- In [`gui/app.py`](file:///home/vlads4r4/dev/Licenta/gui/app.py), observe the top-right panel (`WaterfallWidget`): displays the 52 subcarrier amplitudes in real-time plasma colormap.

## Driving it with harness
```bash
.venv/bin/python .agents/skills/verify-csi-academic/scripts/verify_academic_compliance.py
```
Checks:
- Exact 52-column matrix structure.
- Active non-zero subcarrier variance.
- Warning flag if measured hardware sampling rate $f_s < 100\text{ Hz}$.

## Gotchas
- When raw packets contain internal zero-padded subcarriers, those dead subcarriers must be masked out before computing global variance, otherwise noise metrics become artificially depressed.
