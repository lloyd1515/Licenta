---
title: Ghidul Folderelor si Fisierelor din Proiect
tags:
  - ghid
  - structura
  - fisiere
  - repo
  - csi
aliases:
  - Harta Fisierelor
  - Structura Proiect
---

# 🗺️ Harta Completă a Folderelor și Fișierelor din Proiect

Dacă deschizi proiectul pentru prima dată, s-ar putea să te simți copleșit de numărul de fișiere `.py`, `.c`, `.npz` sau `.md`. Nu te speria! Fiecare fișier are un rol clar, asemenea pieselor dintr-un ceas mecanic elvețian.

Codul Python este organizat curat într-un **singur pachet unificat**: [`src/csi/`](file:///home/vlads4r4/dev/Licenta/src/csi).

---

## 🏛️ Privire de Ansamblu: Cele 4 Mari Ținuturi ale Proiectului

Proiectul nostru este împărțit în 4 mari secțiuni logice:

```
Licenta/
├── src/
│   ├── csi/                      ──► [Pachetul Principal Python] Laborator DSP, FSM, Localizare, GUI
│   │   ├── data/                 ──► [Casetele Video] Fișierele .npz cu înregistrări hardware reale
│   │   ├── plots/                ──► [Galeria de Artă] Cele 7 figuri generate pentru lucrarea de licență
│   │   └── gui/                  ──► [Aplicația Desktop] Interfața grafică PyQt6 (RoomMap, Waterfall, etc.)
│   ├── firmware/                 ──► [Cipurile Fizice] Codul în limbajul C ars pe cele 3 plăcuțe ESP32
│   └── simulation-remotion/      ──► [Animație Video 3D] Vizualizarea 3D a zonelor Fresnel în React/Three.js
├── docs/                         ──► [Documentația] Ghidurile tale din Obsidian (LicentaVault) și cărțile științifice
```

---

## 🔬 1. Pachetul Python Principal: `src/csi/`

Aici locuiește toată inteligența proiectului. Poți rula orice modul direct din terminal din rădăcina `src/` folosind `python -m csi.<nume_modul>`.

### 📐 [`src/csi/room.py`](file:///home/vlads4r4/dev/Licenta/src/csi/room.py)
* **Ce este:** Harta camerei și constantele fizice universale.
* **Ce conține:**
  * Viteza luminii ($c = 3\times 10^8\text{ m/s}$), frecvența purtătoare a canalului 6 ($2.437\text{ GHz}$) și lungimea de undă $\lambda = 12.3\text{ cm}$.
  * Pozițiile celor 3 noduri ESP32 în camera de $5\text{m} \times 5\text{m}$: Nod 1 `(-2.0, 1.2)`, Nod 2 `(2.0, 1.2)`, Nod 3 `(0.0, -2.0)`.
  * Funcția `extra_path_m(point_xy, link)` care calculează drumul suplimentar parcurs de undă reflectată de corp față de drumul direct.

### 📦 [`src/csi/packets.py`](file:///home/vlads4r4/dev/Licenta/src/csi/packets.py)
* **Ce este:** Vameșul și translatorul de pachete binare.
* **Ce conține:**
  * Clasa `PacketStream` care caută sigiliul magic `0xA55A`, citește cei 138 de octeți și transformă numerele brute $I$ și $Q$ în matrice complexe pe 52 de subpurtătoare OFDM.
  * Clasa `Recording` și funcțiile `load_recording` / `save_recording` pentru încărcarea și salvarea fișierelor `.npz`.

### 📡 [`src/csi/record.py`](file:///home/vlads4r4/dev/Licenta/src/csi/record.py)
* **Ce este:** Pescarul de date seriale live.
* **Ce conține:** Deschide porturile USB (`/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.) la viteza de 921600 baud și ascultă sincron transmisiile celor 3 cipuri ESP32, salvând rezultatul într-un fișier `.npz`.

### 🧰 [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py)
* **Ce este:** Bucătăria matematică / curățătoria de semnale (DSP = *Digital Signal Processing*).
* **Ce conține:**
  * `remove_outliers(amplitude)`: Filtrul Hampel cu MAD care elimină spike-urile LNA prin fereastră glisantă.
  * `drop_bad_subcarriers(amplitude)`: Elimină subpurtătoarele moarte sau ultra-zgomotoase conform criteriului Hernandez & Bulut.
  * `bandpass(amplitude, rate_hz)`: Filtrul Butterworth (0.2 – 12 Hz) cu fază zero (`filtfilt`) care scoate pereții ficși.
  * `motion_signal(amplitude)`: Algoritmul PCA care comasează cele 52 de subpurtătoare în semnalul principal PC1.
  * `spectrogram(signal_1d, ...)`: STFT-ul micro-Doppler care extrage viteza de cădere în Hz.
  * `analyze_recording(recording)`: Funcția agregatoare care trece o înregistrare completă prin tot lanțul DSP.

### 🛡️ [`src/csi/fall_detector.py`](file:///home/vlads4r4/dev/Licenta/src/csi/fall_detector.py)
* **Ce este:** Creierul decizional / detectorul de cădere FSM (*Finite State Machine*).
* **Ce conține:**
  * `FallState`: Cele 5 stări fundamentale ale automatului (`CALM`, `MOVING`, `IMPACT`, `CHECKING_STILL`, `ALARM`).
  * `detect_fall(times_s, motion_by_link, rate_hz)`: Verifică poarta de activitate (camera goală), colapsul simultan al pantei pe $\ge 2$ legături ($|dA/dt| > 17.5$) și măsoară liniștea de la sol timp de 2.5 secunde.
  * Returnează un obiect `Detection` cu timpii exacți de impact și alarmă și latența de decizie.

### 📍 [`src/csi/localization.py`](file:///home/vlads4r4/dev/Licenta/src/csi/localization.py)
* **Ce este:** GPS-ul de interior bazat pe elipse Fresnel.
* **Ce conține:**
  * `locate(extra_paths_m)`: Rezolvitorul neliniar Levenberg-Marquardt care găsește punctul $(x, y)$ unde se intersectează cele 3 elipse.
  * `track_with_noisy_ranges(...)`: Netezirea exponențială a pașilor și calculul erorii medii pătratice (RMSE = 0.043 m).

### 🧪 [`src/csi/simulator.py`](file:///home/vlads4r4/dev/Licenta/src/csi/simulator.py)
* **Ce este:** Laboratorul virtual / "Matrix-ul" care simulează mișcarea fizică și propagarea undelor.
* **Ce conține:**
  * `make_trajectory()`: Generează un om virtual care stă pe loc (0–3s), merge pe diagonală (3–10s), cade accelerat sub 400 ms (10–10.35s) și zace la podea (10.35–20s).
  * `simulate_csi(trajectory, ..., seed=0)`: Calculează reflexia electromagnetică pe corpul uman, atenuarea undelor, deplasarea Doppler, zgomotul termic și spike-urile LNA, având suport complet pentru un `seed` reproductibil.

### 📊 [`src/csi/figures.py`](file:///home/vlads4r4/dev/Licenta/src/csi/figures.py)
* **Ce este:** Pictorul oficial al lucrării de licență.
* **Ce face:** Generează cele 7 figuri științifice de înaltă rezoluție în `src/csi/plots/`:
  * `python -m csi.figures synthetic` $\to$ Figurile 1–4 (semnal brut vs filtrat, spectrogramă Doppler, traiectorie 2D, telemetrie FSM).
  * `python -m csi.figures real` $\to$ Figurile 5–7 (comparație triplă ABC pe hardware real, Doppler cădere reală, validare latență 3.0 s pe Test C).

---

## 💾 2. Dataset-urile Reale: `src/csi/data/`

Aici sunt stocate înregistrările experimentale reale captate cu cele 3 noduri ESP32 conectate prin cablu:
* [`test_A_camera_goala.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_A_camera_goala.npz): Camera a fost complet goală. Dovedește că Activity Gate ține sistemul în liniște și produce 0 alarme false.
* [`test_B_mers_normal.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_B_mers_normal.npz): O persoană se plimbă continuu printre noduri. Dovedește că FSM rămâne în starea `MOVING` (MERS) fără să confunde pașii cu o cădere.
* [`test_C_cadere_reala.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_C_cadere_reala.npz): Cădere umană reală pe saltea: conține șocul violent, explozia Doppler de peste 35 Hz și confirmarea alertei roșii cu o latență de $\approx 3.0$ secunde!

---

## 🖥️ 3. Aplicația Grafică Desktop: `src/csi/gui/`

Aceasta este vitrina comercială a proiectului. Tot ce a calculat laboratorul matematic este afișat aici în timp real la 30–60 FPS.

```bash
python -m csi.gui
```

* **[`src/csi/gui/__main__.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/__main__.py):** Cheia de pornire a aplicației. Primește argumente din consolă (`--replay`, `--live`, `--port`).
* **[`src/csi/gui/frame_source.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/frame_source.py):** "Bucătarul din spate". Rulează într-un `QThread` separat și asamblează pachetele venite pe USB sau din fișierul `.npz`.
* **[`src/csi/gui/frames.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/frames.py):** Conține `LiveTracker` care menține o fereastră glisantă de 10 secunde și rulează detectorul de cădere, plus clasa `Frame` (pachetul de telemetrie transmis ferestrei).
* **[`src/csi/gui/main_window.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/main_window.py):** "Caroseria" aplicației. Conține bara de unelte, bara de stare și **Bannerul Roșu Animat de Alertă Critică** care se aprinde intermitent când omul este căzut la pământ.
* **Componentele Vizuale (Widgets):**
  * [`room_map.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/room_map.py) (`RoomMap`): Desenează camera 2D, triunghiul celor 3 noduri, elipsele Fresnel și avatarul uman (în picioare sau prăbușit la sol).
  * [`charts.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/charts.py) (`SubcarrierWaterfall` & `DopplerPlot`): Cascada termică colorată pe cele 52 de subpurtătoare și spectrul de viteze Doppler cu linia critică roșie la 35 Hz.
  * [`status_panel.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/status_panel.py) (`StatusPanel`): Afișează badge-ul colorat al stării FSM (`CALM`, `MERS`, `IMPACT`, `VERIFICARE`, `ALARMĂ`), înălțimea centrului de masă (CoM) și FPS-ul.
  * [`theme.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/theme.py): Paleta cromatică Dark Industrial.
* **[`src/csi/gui/screenshots.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/screenshots.py):** Robotul de verificare automată; rulează aplicația "offscreen" (fără ecran fizic) și salvează 24 de capturi de ecran în `screenshots/` pentru a dovedi buna funcționare.

---

## ⚡ 4. Firmware ESP32: `src/firmware/esp32_csi_node/`

* **[`main/main.c`](file:///home/vlads4r4/dev/Licenta/src/firmware/esp32_csi_node/main/main.c):** Codul scris în limbajul **C**, compilat cu ESP-IDF v5.x.
* **Ce face:** Trece placa Wi-Fi în mod promiscuu pe canalul 6, interceptează pachetele radio, extrage cele 52 de subpurtătoare OFDM și le transmite pe portul serial prin UART la 921600 baud folosind pachetele binare de 138 de octeți.

---

## 🧭 Tabel Rapid: "Dacă vreau să fac X, unde mă uit?"

| Ce Vreau să Fac | Unde Găsesc Fișierul | Ce Funcție / Clasă Caut |
| :--- | :--- | :--- |
| **Vreau să pornesc aplicația desktop** | `src/csi/gui/__main__.py` | Rulează `python -m csi.gui` |
| **Vreau să regenerez cele 7 grafice din teză**| `src/csi/figures.py` | Rulează `python -m csi.figures synthetic` sau `real` |
| **Vreau să schimb pragurile de impact/cădere**| [`src/csi/fall_detector.py`](file:///home/vlads4r4/dev/Licenta/src/csi/fall_detector.py) | Modifică `IMPACT_SLOPE`, `STILL_WINDOW_S` |
| **Vreau să schimb frecvențele filtrelor** | [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py) | Modifică `BAND_LOW_HZ` (0.2), `BAND_HIGH_HZ` (12.0) |
| **Vreau să schimb pozițiile nodurilor în cameră**| [`src/csi/room.py`](file:///home/vlads4r4/dev/Licenta/src/csi/room.py) | Modifică dicționarul `NODE_POSITIONS_M` |
| **Vreau să văd cum se decodează octeții UART**| [`src/csi/packets.py`](file:///home/vlads4r4/dev/Licenta/src/csi/packets.py) | Uită-te în metoda `parse_bytes` a `PacketStream` |
| **Vreau să capturez date noi de la ESP32 fizic**| [`src/csi/record.py`](file:///home/vlads4r4/dev/Licenta/src/csi/record.py) | Rulează `python -m csi.record --p1 /dev/ttyUSB0 ...` |
| **Vreau să văd testul automat cu 24 de poze** | [`src/csi/gui/screenshots.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/screenshots.py)| Rulează `python -m csi.gui.screenshots` |

---

*Navighează mai departe:*
* [[00 - Start Aici]] — Înapoi la cuprinsul principal al vault-ului.
* [[01 - Arhitectura Sistem]] — Schema bloc a întregului sistem.
* [[04 - Dictionar Algoritmi si Software]] — Explicația algoritmilor și conceptelor software.
