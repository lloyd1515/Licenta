---
title: Start Aici - Hub Licenta CSI
tags:
  - licenta
  - hub
  - moc
  - utcn
aliases:
  - Home
  - Start
  - Index
---

# 📡 Licență UTCN: Cartografiere Radio Pasivă și Detecție a Căderilor (Wi-Fi CSI)

> **Universitatea Tehnică din Cluj-Napoca (UTCN)**  
> **Facultatea de Automatică și Calculatoare**  
> **Student:** Vlad Sărăndan  
> **Subiect:** Sistem device-free bazat pe Wi-Fi Channel State Information (CSI) pe 52 subpurtătoare OFDM cu 3 noduri ESP32.  
> **Pachet Python unificat:** `src/csi/`

---

## 🗺️ Harta Notițelor (Map of Content)

### 0. 💡 Ghid Explicativ & Legendă (De la Zero)
* [[00 - Ghid pentru Incepatori (De la Zero)]] — Ce face licența pe înțelesul tuturor, sonarul Wi-Fi, RSSI vs CSI.
* [[01 - Dictionar Hardware si Retea]] — Dicționar ESP32, autostrada OFDM 52 subpurtătoare, baud 921600, cadru 138B `0xA55A`.
* [[02 - Dictionar Fizica si Propagare Unde]] — Reflexie corp uman, elipsoizi Fresnel (balon rugby), Doppler (>35 Hz) și cădere sub 400 ms.
* [[03 - Dictionar Matematica si DSP]] — Bucătăria DSP, numere complexe ca ace de ceasornic, site de filtrare, PCA și STFT.
* [[04 - Dictionar Algoritmi si Software]] — FSM semafor/tonomat, cele 5 stări de cădere, portar Activity Gate, bucătar și ospătar PyQt6.
* [[05 - Ghidul Folderelor si Fisierelor]] — Harta completă a fișierelor și modulelor din pachetul `csi` (`dsp.py`, `fall_detector.py`, `gui`, `data`, etc.).

### 1. Arhitectură Generală
* [[01 - Arhitectura Sistem]] — Schema bloc, flux de date complet de la hardware la GUI în noul modul `csi`.

### 2. Hardware & Achiziție
* [[Noduri ESP32 Mesh]] — Firmware ESP-IDF v5.x, mod promiscuu Canal 6 (2.437 GHz), topologie triunghiulară în `room.py`.
* [[Protocol Binar UART]] — Format cadru binar 138 octeți, Magic `0xA55A`, 921600 baud, decodare prin `packets.py` și `record.py`.

### 3. Pipeline DSP (Semnal & Filtrare)
* [[Filtrare Hampel si Butterworth]] — Eliminare spike-uri LNA (`remove_outliers`) și izolare mișcare umană 0.2–12 Hz (`bandpass`).
* [[Analiza PCA si Selectie Subpurtatoare]] — Eliminare subpurtătoare defecte (`drop_bad_subcarriers`) și fuziune PCA (`motion_signal`).
* [[Spectrograma Micro-Doppler]] — Transformata STFT (`spectrogram`), semnătură Doppler cădere (>35 Hz) vs mers.

### 4. Algoritmi & Detecție
* [[Detector Cadere FSM]] — Automat cu 5 stări (`FallState`: CALM, MERS, IMPACT, VERIFICARE, ALARMĂ) în `fall_detector.py`.
* [[Localizare 2D Elipse Fresnel]] — Model geometric Fresnel, Levenberg-Marquardt (`locate`) și tracking traiectorie în `localization.py`.
* [[Activity Gate si Praguri Cinematice]] — Eliminare alarme false în cameră goală (0.20 sintetic vs 11.0 hardware).

### 5. Date & Experimente
* [[Dataset-uri Hardware Reale]] — Înregistrările experimentale din `src/csi/data/` (`test_A`, `test_B`, `test_C`).
* [[Simulator Sintetic CSI]] — Generator fizic bazat pe elipsoizi Fresnel în `simulator.py` (cu suport seed reproductibil).

### 6. Interfață Desktop
* [[Arhitectura PyQt6 Desktop]] — Aplicație modulară `python -m csi.gui` (`FrameSource`, `LiveTracker`, stil Dark Industrial).
* [[Telemetrie si Widgets]] — `RoomMap`, `SubcarrierWaterfall`, `DopplerPlot`, `StatusPanel`.

### 7. Documentație, Planuri & Apărare
* [[Bibliografie si Lucrari Academice]] — Referințele [P1]–[P4] (Zhang, Hernandez, Wang, Liu) și sinteza teoretică.
* [[Plan Integrare Eval Harness (Pattern 4)]] — Plan de testare automată, Monte-Carlo sweep și CI gate.
* [[Analiza Critica si Whiteboard Defense]] — Ghid de întrebări și răspunsuri pentru susținerea tehnică pe tablă.

---

## 📊 Status Proiect & Dovezi

| Modul | Fișier Sursă | Status | Dovezi / Grafice |
| :--- | :--- | :---: | :--- |
| **Firmware ESP32** | `src/firmware/esp32_csi_node/` | **Gata** | Pachete 138B stabile pe 3 noduri |
| **Pipeline DSP** | [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py) | **Gata** | ![[1_raw_vs_filtered_csi.png\|200]] ![[2_doppler_spectrogram.png\|200]] |
| **Detector FSM** | [`src/csi/fall_detector.py`](file:///home/vlads4r4/dev/Licenta/src/csi/fall_detector.py) | **Gata** | Latență decizie $\approx 3.0\text{ s}$ ![[4_fsm_decision_telemetry.png\|200]] |
| **Localizare 2D** | [`src/csi/localization.py`](file:///home/vlads4r4/dev/Licenta/src/csi/localization.py) | **Gata** | Reconstrucție RMSE = 0.043 m ![[3_trajectory_cartography.png\|200]] |
| **Date Reale** | [`src/csi/data/`](file:///home/vlads4r4/dev/Licenta/src/csi/data) | **Gata** | ![[5_real_hardware_abc_comparison.png\|200]] ![[6_real_fall_doppler_spectrogram.png\|200]] |
| **Aplicație GUI** | [`src/csi/gui/`](file:///home/vlads4r4/dev/Licenta/src/csi/gui) | **Gata** | 24/24 screenshot-uri offscreen ![[phase_3_impact_window.png\|200]] |
| **Figuri Teză** | [`src/csi/figures.py`](file:///home/vlads4r4/dev/Licenta/src/csi/figures.py) | **Gata** | Toate cele 7 figuri în `src/csi/plots/` |
