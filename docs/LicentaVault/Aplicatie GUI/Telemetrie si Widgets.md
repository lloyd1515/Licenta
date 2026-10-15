---
title: Telemetrie si Widgets
tags:
  - gui
  - widgets
  - pyqtgraph
  - telemetrie
aliases:
  - Widgets
  - Telemetrie
---

# 🎛️ Panoul de Telemetrie și Componentele GUI

Componentele vizuale ale aplicației desktop sunt modularizate în folderul [`src/csi/gui/`](file:///home/vlads4r4/dev/Licenta/src/csi/gui) și stilizate prin tema Dark Industrial definită în [`theme.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/theme.py).

---

## 1. Harta Încăperii ([`RoomMap`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/room_map.py))

* Afișează spațiul 2D al camerei $[-2.5\text{ m} .. +2.5\text{ m}]$ conform constantelor din `room.py`.
* **Nodurile ESP32:** N1, N2, N3 desenate cu marcatori luminoși și coordonate exacte.
* **Elipsele Fresnel:** Zonele de sensibilitate desenate dinamic între perechile de noduri.
* **Avatarul utilizatorului:** 
  * Culoare cyan / verde când persoana merge (`FallState.MOVING`).
  * Culoare roșie intermitentă și postură orizontală pe podea când FSM confirmă căderea la sol (`FallState.ALARM`).

![[phase_1_calm_room_map.png|450]]

---

## 2. Cascada Spectrală CSI ([`SubcarrierWaterfall`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/charts.py))

* Cascadă termică dinamică pe toate cele **52 de subpurtătoare active OFDM** (indici $[-26..26]$).
* Păstrează un istoric glisant de 100 de cadre (`WATERFALL_FRAMES = 100`), folosind colormap-ul `plasma`.
* Permite operatorului să observe vizual cum fiecare subpurtătoare își modifică atenuarea în timp real când corpul uman trece prin lobii radio.

![[phase_2_walking_waterfall.png|450]]

---

## 3. Spectrograma Doppler ([`DopplerPlot`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/charts.py))

* Vizualizează deplasarea Doppler instantanee în domeniul $0 - 65\text{ Hz}$.
* **Linie critică roșie punctată la 35 Hz (`DOPPLER_REFERENCE_HZ`):** pragul de cădere accelerată.
* Permite diferențierea imediată între gesturi lente de mers ($<20\text{ Hz}$) și șocul căderii gravitaționale ($>35\text{ Hz}$).

![[phase_3_impact_doppler.png|450]]

---

## 4. Panoul de Stare și Telemetrie ([`StatusPanel`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/status_panel.py))

* **Indicator Înălțime CoM:** Arată înălțimea estimată a centrului de masă ($1.7\text{ m} \to 0.2\text{ m}$).
* **Badge Stare FSM:** Pastilă colorată conform `STATE_LABELS`:
  * `CALM` (Cyan / Gri)
  * `MERS` (Verde)
  * `IMPACT` (Galben / Portocaliu)
  * `VERIFICARE` (Galben intens)
  * `ALARMĂ` (Roșu aprins)
* **Metrici Rețea:** Frecvența cadrelor (FPS), rata de eșantioane și latența deciziei.

![[phase_3_impact_telemetry.png|450]]
