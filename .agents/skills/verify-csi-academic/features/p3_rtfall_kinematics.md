# Feature: RT-Fall Kinematic Detection & Post-Fall Dormancy

## Reference
[P3] Hao Wang, Daqing Zhang, Junyi Ma, Yasha Wang, Yuxiang Wang. *RT-Fall: Device-Free Fall Detection by Retrieving Spatial and Temporal Information from Wi-Fi Signals*, ACM MobiCom, pp. 315-326, 2014.

## Sub-features
- **Kinematic Fall Signature:** Accelerated vertical body descent within $300 - 400\text{ ms}$.
- **Doppler Threshold:** High-frequency Doppler burst exceeding $35\text{ Hz}$ ($35 - 60\text{ Hz}$), whereas normal human walking produces $10 - 22\text{ Hz}$.
- **Post-Fall Dormancy:** Mandatory confirmation of immobility ($\ge 2.0\text{ s}$) following impact, where signal variance drops below the resting noise floor.
- **Deterministic FSM:** 5 states: `0: CALM`, `1: WALKING`, `2: IMPACT`, `3: DORMANCY`, `4: ALARM`.

## How to get to it (user POV)
- In [`gui/app.py`](file:///home/vlads4r4/dev/Licenta/gui/app.py), observe bottom-left Doppler panel (red dashed line at 35 Hz) and bottom-right Telemetry panel (FSM state pill and vertical posture gauge).
- When a fall occurs, the Doppler curve spikes over the 35 Hz threshold, height gauge collapses to 0.15m, and after 2 seconds of immobility, the emergency alert banner pops up.

## Driving it with harness
```bash
.venv/bin/python .agents/skills/verify-csi-academic/scripts/verify_academic_compliance.py
```
Checks:
- Maximum Doppler during impact exceeds $35\text{ Hz}$.
- Alarm trigger requires verified dormancy period ($1.8\text{ s} - 3.5\text{ s}$ latency).

## Gotchas
- Rapid sitting down can cause a brief Doppler increase, but will not produce simultaneous multi-link power collapse or the high-frequency burst $>35\text{ Hz}$ characteristic of free fall.
