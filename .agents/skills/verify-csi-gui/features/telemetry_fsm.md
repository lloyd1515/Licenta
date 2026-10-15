# Feature: Telemetry & System Health

## 1. Metric Indicators
- Stream FPS: rolling frames per second delivered by the backend thread (target: 50 FPS).
- Port status: active UART devices (`/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyUSB2`) or Replay Mode indicator.
- RSSI: Decibel signal strength of the active link (typically -40 dBm to -85 dBm).
- PC1 Amplitude: Current output of the first principal component filter.

## 2. Center-of-Mass (CoM) Posture Height
- Vertical gauge showing reconstructed human height ($z \in [0.0, 2.0]\text{ m}$).
- Standing: $1.70 - 1.80\text{ m}$.
- Fall: Rapid collapse down to $0.15 - 0.20\text{ m}$.

## 3. FSM State Badge
Displays deterministic analytical state:
- `0: CALM` (Blue)
- `1: MERS` (Green)
- `2: IMPACT` (Orange)
- `3: DORMANCY` (Amber)
- `4: ALARMĂ` (Crimson)
