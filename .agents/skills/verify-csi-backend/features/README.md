# Backend Pipeline Features

Detailed technical specifications and verification contracts for the CSI processing pipeline:

- [serial_ingest.md](serial_ingest.md): Binary UART deserializer, packet format, baud rate contracts.
- [dsp_pipeline.md](dsp_pipeline.md): Noise reduction, subcarrier sanitization, PCA extraction, STFT Doppler.
- [fsm_engine.md](fsm_engine.md): Analytical state machine, activity gates, impact thresholds, dormancy verification.
