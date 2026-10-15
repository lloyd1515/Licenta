---
title: Dataset-uri Hardware Reale
tags:
  - date
  - experimente
  - hardware
  - npz
aliases:
  - Date Reale
  - Dataset
---

# 💾 Dataset-uri Experimentale Hardware Reale ($n=3$)

Pentru validarea pe echipament fizic, au fost efectuate înregistrări experimentale folosind cele 3 noduri ESP32 conectate prin cabluri UART.

Datele brute sunt salvate în fișiere comprimate NumPy `.npz` în folderul [`src/csi/data/`](file:///home/vlads4r4/dev/Licenta/src/csi/data):
1. [`test_A_camera_goala.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_A_camera_goala.npz) (124 KB) — **Test A: Liniște RF în cameră complet goală** (durată ~20 s).
2. [`test_B_mers_normal.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_B_mers_normal.npz) (60 KB) — **Test B: Subiect mergând continuu în încăpere** fără căderi.
3. [`test_C_cadere_reala.npz`](file:///home/vlads4r4/dev/Licenta/src/csi/data/test_C_cadere_reala.npz) (73 KB) — **Test C: Cădere umană reală pe saltea**, urmată de imobilitate prelungită la sol.

Scriptul unificat de generare a figurilor din teză este [`src/csi/figures.py`](file:///home/vlads4r4/dev/Licenta/src/csi/figures.py) (`python -m csi.figures real`).

---

## 🔬 Comparație Triplă: Cameră Goală vs Mers vs Cădere

![[5_real_hardware_abc_comparison.png|850]]

### Observații Experimentale:
* **Test A (Cameră goală):** Amplitudinea CSI pe cele 52 subpurtătoare este stabilă orizontal. Semnalul PC1 are variație minimă ($\sigma < 11.0$).
* **Test B (Mers normal):** Apar ondulații cvasi-periodice datorate trecerii prin lobii Fresnel, dar fără pante abrupte de colaps.
* **Test C (Cădere reală):** Se distinge clar căderea bruscă a puterii pe toate subpurtătoarele, urmată de o linie plată de imobilitate (victima la sol).

---

## ⚡ Spectrograma Doppler pe Căderea Reală

![[6_real_fall_doppler_spectrogram.png|850]]

În Testul C, momentul prăbușirii generează o explozie spectrală depășind pragul critic de **35 Hz** pe o durată scurtă ($< 400\text{ ms}$), urmată de stabilizare la 0 Hz în timpul imobilității.

---

## ⏱️ Validare Telemetrie FSM pe Hardware Real

![[7_real_fall_fsm_validation.png|850]]

* Latența totală de detecție și confirmare a alertei calculată de detector pe datele reale din Testul C este de **$\approx 3.0$ secunde** (impact la 4.35 s, alarmă confirmată la 7.36 s, din care 2.5 s reprezintă fereastra obligatorie de monitorizare a imobilității).
* Automatul FSM rămâne în starea `CALM` pentru Testul A și în starea `MOVING` (MERS) pentru Testul B $\implies$ **0 alarme false pe datele reale existente**.
