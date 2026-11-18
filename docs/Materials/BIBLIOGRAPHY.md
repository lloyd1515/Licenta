# Catalog Bibliografic Complet & Lucrări de Referință

Acest catalog centralizează totalitatea literaturii academice, articolelor științifice și resurselor bibliografice utilizate în proiectul de licență, acoperind pilonul principal de **Detecție Pasivă Wi-Fi CSI & Modelare Fresnel**, inclusiv lucrările descărcate automat prin motorul `AutoResearcher`.

---

## 1. Lucrări Seminale Wi-Fi CSI Sensing & Modele Fresnel [P1]–[P8]

Toate fișierele de citare BibTeX sunt disponibile în [`CSI_Sensing/references_csi.bib`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/references_csi.bib) și [`references_master.bib`](file:///home/vlads4r4/dev/Licenta/docs/Materials/references_master.bib).

### [P1] Fresnel Zone Based Indoor Localization and Activity Sensing
- **Autori:** Daqing Zhang, Hao Wang, Dan Wang
- **Publicație:** *IEEE/ACM Transactions on Networking (ToN)*, Vol. 25, Nr. 5, pp. 2843–2857, Oct. 2017
- **DOI:** [10.1109/TNET.2017.2721442](https://doi.org/10.1109/TNET.2017.2721442)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P1_Zhang_2017_Fresnel_Zone.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P1_Zhang_2017_Fresnel_Zone.md)
- **Concepte cheie:** Geometria zonelor Fresnel la 2.4 GHz ($\lambda = 12.31\text{ cm}$), raza primei zone $r_1 \approx 30.38\text{ cm}$, pas spațial de modulație $\lambda/2 = 6.15\text{ cm}$.

### [P2] Wi-Fi Sensing on the Edge: Who and Where are You?
- **Autori:** Steven M. Hernandez, Eyuphan Bulut
- **Publicație:** *IEEE Internet of Things Journal (IoT-J)*, Vol. 9, Nr. 10, pp. 7000–7014, Mai 2021
- **DOI:** [10.1109/JIOT.2021.3116035](https://doi.org/10.1109/JIOT.2021.3116035) | arXiv: [2109.11718](https://arxiv.org/abs/2109.11718)
- **PDF Local:** lipsă. Articol apropiat al acelorași autori (IEEE COMST 2022): [`CSI_Sensing/sources-2026-10-21/Hernandez_2022_WiFi_Sensing_on_the_Edge.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Hernandez_2022_WiFi_Sensing_on_the_Edge.pdf)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P2_Hernandez_2021_ESP32_CSI_Tool.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P2_Hernandez_2021_ESP32_CSI_Tool.md)
- **Concepte cheie:** Extragere pachete CSI pe ESP32, 52 subpurtătoare active OFDM HT20, cerință cadență $f_s \ge 100\text{ Hz}$ (motivul trecerii de la UART la UDP).

### [P3] RT-Fall: Real-Time Fall Detection using Wi-Fi Radio Frequency Signals
- **Autori:** Hao Wang, Daqing Zhang, Yasha Wang, Junyi Ma, Yuxiang Wang, Shengjie Li
- **Publicație:** *ACM MobiCom 2014*, pp. 511–526 (extins în *IEEE TMC*, 2017)
- **DOI:** [10.1145/2639108.2639143](https://doi.org/10.1145/2639108.2639143)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P3_Wang_2014_RT_Fall.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P3_Wang_2014_RT_Fall.md)
- **Concepte cheie:** Cinematica căderii ($v > 2.5\text{ m/s}$, Doppler $>35\text{ Hz}$), durată impact $<450\text{ ms}$, fereastră de imobilitate $\ge 2.5\text{ s}$, automat FSM de detecție.

### [P4] Multi-Link Indoor Localization Based on Wi-Fi CSI
- **Autori:** Jian Liu, Yingying Chen, Yan Wang, Xiaonan Chen, Jie Cheng
- **Publicație:** *IEEE Transactions on Vehicular Technology (TVT)*, Vol. 68, Nr. 11, pp. 11200–11211, Nov. 2019
- **DOI:** [10.1109/TVT.2019.2941199](https://doi.org/10.1109/TVT.2019.2941199)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P4_Liu_2019_MultiLink_Fresnel.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P4_Liu_2019_MultiLink_Fresnel.md)
- **Concepte cheie:** Necesitatea geometrică a 3 noduri necoliniare pentru rang Jacobian complet 2 pe coordonate $(x, y)$, rezolvare NLLS Levenberg-Marquardt.

### [P5] See Through Walls with WiFi! (Wi-Vi)
- **Autori:** Fadel Adib, Dina Katabi
- **Publicație:** *ACM SIGCOMM 2013*, pp. 75–86, Aug. 2013
- **DOI:** [10.1145/2486001.2486039](https://doi.org/10.1145/2486001.2486039)
- **PDF Local:** [`CSI_Sensing/sources-2026-10-21/Adib_2013_See_Through_Walls_with_WiFi.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Adib_2013_See_Through_Walls_with_WiFi.pdf)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P5_Adib_2013_See_Through_Walls.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P5_Adib_2013_See_Through_Walls.md)
- **Concepte cheie:** Anularea reflexiei statice puternice de pe pereți (Flash Effect) prin diferențiere și filtrare trece-bandă.

### [P6] Exploiting CSI Phase for Vital Signs Monitoring with Commodity WiFi Devices (PhaseBeat)
- **Autori:** Xuyu Wang, Chao Yang, Shiwen Mao
- **Publicație:** *IEEE Transactions on Mobile Computing (TMC)*, Vol. 16, Nr. 10, pp. 2803–2816, Oct. 2017
- **DOI:** [10.1109/TMC.2017.2706338](https://doi.org/10.1109/TMC.2017.2706338) | arXiv: [1709.02897](https://arxiv.org/abs/1709.02897)
- **PDF Local:** lipsă. Versiunea extinsă PhaseBeat a acelorași autori (2020): [`CSI_Sensing/sources-2026-10-21/Wang_Mao_2020_PhaseBeat_Vital_Signs.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Wang_Mao_2020_PhaseBeat_Vital_Signs.pdf)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P6_Wang_2017_PhaseBeat_Vital_Signs.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P6_Wang_2017_PhaseBeat_Vital_Signs.md)
- **Concepte cheie:** Igienizarea fazei CSI, eliminare erori CFO/SFO, detecție micro-mișcări toracice post-cădere.

### [P7] Time-Reversal Machine: A Wireless IoT Revolution
- **Autori:** K. J. Ray Liu, Beibei Wang
- **Publicație:** *IEEE Signal Processing Letters (SPL)*, Vol. 24, Nr. 12, pp. 1808–1812, Dec. 2017
- **DOI:** [10.1109/LSP.2017.2758838](https://doi.org/10.1109/LSP.2017.2758838) | arXiv: [1709.06201](https://arxiv.org/abs/1709.06201)
- **PDF Local:** lipsă. Articole înrudite despre time reversal (grupul K. J. Ray Liu): [`CSI_Sensing/sources-2026-10-21/Chen_Liu_2016_WiFi_TRIPS_Time_Reversal.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Chen_Liu_2016_WiFi_TRIPS_Time_Reversal.pdf), [`CSI_Sensing/sources-2026-10-21/Chen_Liu_2018_TR_BREATH_Time_Reversal.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Chen_Liu_2018_TR_BREATH_Time_Reversal.pdf)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P7_Liu_2017_Time_Reversal_Machine.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P7_Liu_2017_Time_Reversal_Machine.md)
- **Concepte cheie:** Teoria rezonanței temporale multipath, spațiul de interior tratat ca lentilă electromagnetică de precizie.

### [P8] Non-Cooperative Wi-Fi Localization (Wi-Peep)
- **Autori:** Ali Abedi, Deepak Vasisht
- **Publicație:** *ACM MobiCom 2022*, pp. 707–720, Oct. 2022
- **DOI:** [10.1145/3495243.3560530](https://doi.org/10.1145/3495243.3560530) | arXiv: [2209.05607](https://arxiv.org/abs/2209.05607)
- **PDF Local:** lipsă. Articol înrudit al aceluiași prim autor: [`CSI_Sensing/sources-2026-10-21/Abedi_2023_WiFi_Physical_Layer_Stays_Awake.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Abedi_2023_WiFi_Physical_Layer_Stays_Awake.pdf)
- **Dossier de analiză:** [`CSI_Sensing/Dossiers/P8_Abedi_2022_WiPeep_NonCooperative.md`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/Dossiers/P8_Abedi_2022_WiPeep_NonCooperative.md)
- **Concepte cheie:** Localizare pasivă non-cooperativă bazată pe timpi de răspuns la nivel hardware MAC 802.11.

---

## 2. Lucrări Extinse Descărcate prin `AutoResearcher` (9 Articole PDF)

Aceste lucrări au fost identificate și descărcate automat prin motorul de cercetare `AutoResearcher` din `/home/vlads4r4/dev/side-projects/AutoResearcher/core/pdf_resolver.py`, utilizând cascada de rezolvare (ArXiv Direct + Unpaywall API + OpenAlex Repository Scan + Verificare Magic-Byte `b"%PDF-"`).

PDF-urile sunt salvate în [`CSI_Sensing/PDFs/`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/PDFs/). Două articole au fost mutate în `sources-2026-10-21/` și sunt marcate în listă:

1. **Strohmayer_2024_ESP32_Through_Wall_CSI_Sensing.pdf** (10.7 MB, mutat în [`CSI_Sensing/sources-2026-10-21/`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/)) – Detecție pasivă prin pereți folosind plăci ESP32 și caracteristicile CSI de subpurtătoare.
2. **CiUAV_ESP32_CSI_3D_Localization.pdf** (6.4 MB) – Algoritmi de localizare 3D bazată pe CSI extras pe microcontroller ESP32.
3. **DeepCRF_CSI_RF_Fingerprinting.pdf** (1.1 MB, arXiv:2403.15739 / IEEE INFOCOM 2024) – Amprentare RF la nivel fizic prin micro-semnale CSI.
4. **Benchmarking_OpenWiFiSync_ESP32.pdf** (2.6 MB) – Benchmark de sincronizare între multiple plăci ESP32 pentru măsurători radio distribuite.
5. **OpenWiFiSync_Implementation_WiFi.pdf** (720 KB) – Implementare de sincronizare a nodurilor Wi-Fi fără cabluri fizice de ceas.
6. **Fine_Time_Measurement_IoT_ESP32.pdf** (2.8 MB) – Protocolul 802.11mc FTM (Fine Time Measurement) pe ESP32 pentru distanțe ToF.
7. **Hybrid_WiFi_BLE_Fingerprinting_ESP32.pdf** (21.1 MB) – Tehnici hibride de localizare prin fuziunea semnalelor Wi-Fi CSI și BLE pe ESP32.
8. **Abedi_2023_WiFi_Physical_Layer_Stays_Awake.pdf** (2.8 MB, arXiv:2301.00269, mutat în [`CSI_Sensing/sources-2026-10-21/`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/)) – Vulnerabilități ale stratului fizic Wi-Fi ce răspunde la pachete nesolicitate.
9. **Even_Black_Cats_Cannot_Stay_Hidden.pdf** (1.3 MB) – Detecție radio pasivă a țintelor non-cooperative în medii multipath complexe.
