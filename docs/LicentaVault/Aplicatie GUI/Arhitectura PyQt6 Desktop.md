---
title: Arhitectura PyQt6 Desktop
tags:
  - gui
  - pyqt6
  - desktop
  - threading
aliases:
  - GUI
  - PyQt6
---

# 🖥️ Aplicația Desktop PyQt6: Arhitectură și Monitorizare

Interfața grafică desktop este construită în **PyQt6** și **PyQtGraph** pentru a asigura randare fluidă la 30–60 FPS a cascadelor spectrale CSI și a hărții 2D a încăperii.

Pachetul este localizat în [`src/csi/gui/`](file:///home/vlads4r4/dev/Licenta/src/csi/gui) și se lansează prin comanda:
```bash
python -m csi.gui
```

---

## 🧵 Arhitectura Multithreaded Decuplată

Pentru a preveni blocarea interfeței grafice (UI freeze) cauzată de calculul intens al filtrelor DSP (Hampel, PCA, STFT) și al detecției de cădere, execuția este decuplată prin `QThread`:

```
[ Thread Secundar: FrameSource (QThread în frame_source.py) ]
   ├── Ingestie pachete UART reale sau Replay din .NPZ
   ├── Rulare LiveTracker (csi/gui/frames.py) pe fereastră de 10 secunde
   ├── Rulare detect_fall (csi/fall_detector.py)
   └── Emite semnal Qt: frame_ready.emit(frame)
                     │
                     ▼ (Signal/Slot asincron)
[ Thread Principal: MainWindow (csi/gui/main_window.py) ]
   ├── Recepție obiect Frame (instantaneu telemetric)
   ├── Actualizare PyQtGraph (RoomMap, SubcarrierWaterfall, DopplerPlot)
   ├── Actualizare StatusPanel (etichete stări, CoM, FPS)
   └── Declanșare Banner Critic Animat la Cădere
```

---

## 🕹️ Moduri de Operare ale Aplicației

1. **Mod Replay Offline (`python -m csi.gui --replay`):**
   * Încarcă automat fișierul real de cădere `test_C_cadere_reala.npz` (sau cel specificat) și îl redă în buclă la viteza eșantioanelor reale.
2. **Mod Live UART (`python -m csi.gui --live --port /dev/ttyUSB0`):**
   * Se conectează la porturile seriale ale nodurilor ESP32 și procesează fluxul în timp real la 921600 baud.
   * Dacă nodurile hardware nu sunt conectate la porturile menționate, comută automat pe fallback la modul Replay.

---

## 📸 Suita de Verificare Vizuală Automată (`csi/gui/screenshots.py`)

Aplicația include o suită de testare offscreen ([`src/csi/gui/screenshots.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/screenshots.py)) care capturează **24 de screenshot-uri de control** în [`src/csi/gui/screenshots/`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/screenshots) pe parcursul celor 4 faze ale căderii:

```bash
python -m csi.gui.screenshots
```

### Faza 2: Mers Normal
![[phase_2_walking_window.png|750]]

### Faza 3: Impact Cădere (Alertă Critică)
![[phase_3_impact_window.png|750]]
