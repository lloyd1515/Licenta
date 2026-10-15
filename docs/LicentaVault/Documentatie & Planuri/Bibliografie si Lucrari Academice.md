---
title: Bibliografie si Lucrari Academice
tags:
  - documentatie
  - bibliografie
  - papers
  - academic
aliases:
  - Bibliografie
  - Lucrari Academice
---

# 📚 Sinteză Academică și Lucrări de Referință

Lucrarea de licență se bazează pe literatura de specialitate canonică în domeniul detecției pasive prin semnale Wi-Fi CSI (Device-Free Wireless Sensing).

Toate fișierele PDF și fișierele BibTeX sunt centralizate în folderul [`docs/Materials/`](file:///home/vlads4r4/dev/Licenta/docs/Materials).

---

## 🏛️ Cele 4 Lucrări Fundamentale ([P1] - [P4])

### [P1] Zhang et al. (MobiCom 2017)
> **Titlu:** *Fresnel Zone Based Indoor Localization and Motion Sensing*  
> **Contribuție aplicată:** Fundamentează modelul teoretic al elipselor Fresnel pentru unde radio de 2.4 GHz. Arată cum deplasarea pe axa ortogonală față de linia directă generează trecerea prin zone constructive și distructive, permițând localizarea prin rezolvarea lungimilor suplimentare de drum $\Delta d$.

### [P2] Hernandez & Bulut (IEEE Internet of Things 2021)
> **Titlu:** *Lightweight and Standalone IoT Based Device-Free Fall Detection System using Wi-Fi CSI on Edge*  
> **Contribuție aplicată:** Demonstrează fezabilitatea capturii CSI pe cipuri low-cost ESP32. Definește criteriul de salubrizare a subpurtătoarelor (eliminarea canalelor inactive $\text{Var} < 0.05$ și a celor de margine zgomotoase $\text{Var} > 350.0$), implementat în [`drop_bad_subcarriers`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L51).

### [P3] Wang et al. (IEEE INFOCOM 2014)
> **Titlu:** *RT-Fall: Device-Free Fall Detection Using Channel State Information*  
> **Contribuție aplicată:** Stabilește principiul automatului de stări FSM pentru căderi: combinarea vitezei de colaps a anvelopei ($|dA/dt|$) cu verificarea imobilității la sol timp de 2–3 secunde pentru a evita alarmele false provocate de așezarea pe scaun.

### [P4] Liu et al. (ACM UbiComp 2019)
> **Titlu:** *Fall Detection using Wi-Fi Channel State Information with Multi-Link Fusion*  
> **Contribuție aplicată:** Impune cerința de fuziune spațială multi-link: un impact de cădere corporală este un eveniment global în încăpere, afectând cel puțin 2 legături radio simultan, spre deosebire de un gest al mâinii care perturbă o singură legătură.

---

## 📑 Alte Lucrări Importante din Arhivă
* **Adib & Katabi (MobiCom 2013):** *See Through Walls with Wi-Fi!*
* **Wang et al. (TMC 2017):** *PhaseBeat: Exploiting CSI Phase for Vital Signs Monitoring.*
* **Liu et al. (IEEE TSP 2017):** *Time-Reversal Machine for Indoor Tracking.*
* **Abedi et al. (IEEE S&P 2022):** *WiPeep: Exploiting Wi-Fi Response Dynamics.*
