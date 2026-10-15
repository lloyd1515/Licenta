---
name: verify-csi-gui
description: Automated visual verification and UI integration suite for the PyQt6 Wi-Fi CSI sensing desktop application.
---

# verify-csi-gui

Automated visual proof and UI integration verification suite for the desktop interface, validating offscreen rendering, widget layouts, real-time telemetry updates, and emergency alert state transitions.

## Quick Start

```bash
# Execute offscreen Qt verification & capture visual proof artifacts
.venv/bin/python .agents/skills/verify-csi-gui/scripts/verify_gui_screens.py
```

## Features Verified

1. **Room Map & 2D Kinematic Tracking** (`features/room_map_tracking.md`):
   - 2D room floorplan (-2.5m to +2.5m), node anchor positions (ESP1, ESP2, ESP3).
   - Dynamic Fresnel ellipsoidal zones with live activity coloring (cyan/yellow/red).
   - Target avatar positioning, velocity vector arrow, posture state indicator.

2. **Spectral Waterfall Matrix** (`features/spectral_waterfall.md`):
   - 52 OFDM subcarriers rolling waterfall heatmap (rolling depth 120 frames).
   - Plasma colormap mapping CSI amplitudes (0 to 120 ADC units).

3. **Doppler Kinematics & Velocity Profile** (`features/doppler_kinematics.md`):
   - Micro-Doppler frequency line chart (0 to 60 Hz).
   - Red dashed threshold line at 35.0 Hz per RT-Fall (P3).
   - Peak frequency tracking during walking (< 20 Hz) vs fall impact (> 35 Hz).

4. **Telemetry & System Health** (`features/telemetry_fsm.md`):
   - Active serial ports, baud rate (921600), stream FPS (30-50 Hz).
   - Real-time RSSI, PC1 amplitude, CoM height bar (1.75m down to 0.15m).
   - Current FSM classification badge (CALM / MERS / IMPACT / DORMANCY / ALARMĂ).

5. **Emergency Alert Banner** (`features/alert_banner.md`):
   - High-contrast blinking crimson warning banner (`#DC2626`).
   - Latency annotation, fall confirmation text, dismiss button callback.
