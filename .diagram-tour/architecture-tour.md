---
diagram-tour: 1
diagram: ./architecture.dot
stops:
  1: FULL
  2: cluster_hardware
  3: cluster_ingestion
  4: cluster_dsp
  5: cluster_decision
  6: cluster_gui
  7: cluster_simulation
  8: FULL
---

# Wi-Fi CSI Cartography and Fall Detection Architecture Tour

## Stop 1 — Orientation

Every year, millions of seniors experience domestic falls in spaces where optical cameras are strictly forbidden and emergency buttons sit forgotten. Standard Wi-Fi radio waves in the walls can detect a severe fall in four hundred milliseconds using three five-dollar microcontrollers. Six clusters organize the architecture. Hardware and Firmware collects raw radio frames on physical microcontrollers. Ingestion and Telemetry Engine streams binary packets into host memory. DSP Pipeline filters raw noise and extracts Doppler frequencies. Decision and Spatial Reasoning detects falls and tracks two-dimensional position. Desktop User Interface renders real-time telemetry at sixty frames per second. Simulation and Validation provides physics modeling and automated test suites. We trace the signal from antenna to screen.

## Stop 2 — Hardware and Firmware

The Hardware and Firmware cluster captures channel state perturbations at the physical boundary. esp32_csi_node runs on three ESP32 microcontrollers forming an invisible fifty-two string radio harp across eight hundred two point eleven n channel six. The human body is seventy percent saltwater, acting as a massive dielectric mirror that perturbs the multipath wavefront. The promiscuous callback wifi_csi_rx_cb extracts complex channel state information across fifty-two active orthogonal subcarriers. The firmware packs these values with sequence counters and timestamps into UART stream. This delivers continuous one hundred thirty-eight byte binary frames with magic header zero x A five five A over UART at nine hundred twenty-one thousand six hundred baud.

## Stop 3 — Ingestion and Telemetry Engine

The Ingestion and Telemetry Engine receives raw bytes from external serial hardware. capture_serial.py runs dedicated worker threads to synchronize frame boundaries, unpack real and imaginary channel pairs, and archive offline datasets. CSIDataEngine runs as a background thread in the desktop environment. It provides live streaming from serial ports and seamless fallback to recorded numpy experiments. The engine dispatches processed frames to graphical subscribers with high temporal precision.

## Stop 4 — DSP Pipeline

The DSP Pipeline transforms noisy channel state matrices into clean kinematic signals. filters.py strips antenna switching spikes using an adaptive Hampel filter and removes direct-current drift with a Butterworth bandpass filter. PCA First Component projects the fifty-two subcarriers onto their dominant variance vector, isolating human motion while suppressing ambient noise. STFT Micro-Doppler computes time-frequency spectrograms, capturing the rapid velocity shifts characteristic of falling bodies.

## Stop 5 — Decision and Spatial Reasoning

The Decision and Spatial Reasoning cluster converts continuous wave features into discrete states and spatial coordinates. fall_detector.py implements a five-state analytical automaton covering calm, moving, pre-fall, impact, and prolonged lying states. Horizontal walking produces Doppler shifts of fifteen to twenty-two hertz. Gravitational free fall accelerates the torso to four meters per second, causing STFT Micro-Doppler to spike past thirty-five hertz to peak at forty-eight point five hertz. localization.py applies the Fresnel ellipsoid model and Levenberg-Marquardt optimization to multi-link attenuation curves, calculating two-dimensional coordinates with centimeter-level precision.

## Stop 6 — Desktop User Interface

The Desktop User Interface presents real-time telemetry for clinical and experimental monitoring. main_window.py hosts the dark industrial application layout and manages system state transitions. widgets.py coordinates the visualization suite. RoomMap displays room geometry and avatar coordinates. Waterfall plots subcarrier heatmaps across time. Doppler tracks frequency spectra against impact thresholds. Telemetry displays numerical center-of-mass and critical alerts.

## Stop 7 — Simulation and Validation

The Simulation and Validation cluster grounds the engineering implementation in theoretical physics and automated regression tests. simulation-remotion models electromagnetic wave propagation and Fresnel diffraction zones using React, Three.js, and Remotion. verify_gui_evidence.py executes offscreen automated test scenarios across calm, walking, impact, and alert states, producing twenty-four deterministic screenshots to guarantee graphical stability.

## Stop 8 — Closing Summary

The complete architecture operates as a coherent real-time sensing pipeline. Signals flow from Hardware and Firmware through Ingestion and Telemetry Engine into DSP Pipeline. Decision and Spatial Reasoning evaluates safety conditions, Desktop User Interface displays actionable telemetry to users, and Simulation and Validation verifies theoretical fidelity. The system demonstrates robust passive ambient monitoring using commodity Wi-Fi hardware. Clone the open source repository and download the full thirty-nine page thesis document to inspect every verification benchmark.
