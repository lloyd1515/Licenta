---
name: verify-csi-backend
description: Automated verification suite for the Wi-Fi CSI sensing backend pipeline, UART packet ingestion, DSP filtering, and FSM fall detection.
---

# verify-csi-backend

Automated verification suite validating the CSI data acquisition and DSP processing pipeline against physical hardware constraints and academic baselines.

## Quick Start

```bash
# Run end-to-end backend verification
.venv/bin/python .agents/skills/verify-csi-backend/scripts/verify_backend_pipeline.py
```

## Features Verified

1. **Serial Packet Ingestion** (`features/serial_ingest.md`):
   - 138-byte binary packets at 921600 baud.
   - Header magic `0xA55A`, node ID, signed RSSI, microsecond timestamp, sequence counter.
   - 64 raw I/Q subcarrier pairs parsed into 52 active OFDM subcarriers.

2. **DSP Filtering Pipeline** (`features/dsp_pipeline.md`):
   - Hampel filter outlier rejection (LNA gain steps).
   - Hernandez & Bulut (2021) subcarrier sanitization (pruning dead zero-carriers 21-30 and guard pilot noise).
   - 4th-order Butterworth bandpass (0.2 - 12.0 Hz) removing DC static multipath.
   - First Principal Component (PC1) extraction via covariance eigen-decomposition.
   - Short-Time Fourier Transform (STFT) Doppler power spectrogram.

3. **Deterministic FSM Engine** (`features/fsm_engine.md`):
   - 5-State FSM: State 0 (CALM), State 1 (WALKING), State 2 (IMPACT), State 3 (DORMANCY), State 4 (ALARM).
   - Validated on real experimental hardware datasets:
     - `test_A_camera_goala.npz`: 0 false alarms.
     - `test_B_mers_normal.npz`: Walking detected, 0 false fall alarms.
     - `test_C_cadere_reala.npz`: Impact detected, dormancy verified, fall confirmed.
