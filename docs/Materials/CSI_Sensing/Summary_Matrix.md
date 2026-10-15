# Matrice Sinteză Academică CSI Sensing [P1]–[P8]

| Id | Titlu Articol | Venue & An | Autori Cheie | Tehnologie RF | Eșantionare ($f_s$) | Contribuție Fundamentală | Limite / Constrângeri |
|---|---|---|---|---|---|---|---|
| **[P1]** | *Fresnel Zone Based Indoor Localization* | IEEE/ACM ToN 2017 | D. Zhang, H. Wang | Wi-Fi 2.4 GHz | $\ge 50\text{ Hz}$ | Modelul analitic al zonelor Fresnel ($\lambda=12.31\text{ cm}$, $r_1=30.4\text{ cm}$, pas spațial $\lambda/2=6.15\text{ cm}$) | 1 singură legătură = zonă oarbă pe axa minoră |
| **[P2]** | *Wi-Fi Sensing on the Edge* | IEEE IoTJ 2021 | S. M. Hernandez, E. Bulut | ESP32 HT20 | $\ge 100\text{ Hz}$ standard | Pachet CSI binar 138B, 52 subpurtătoare active pe ESP32 | UART limitează cadența la 33–50 Hz $\implies$ cere UDP |
| **[P3]** | *RT-Fall: Real-Time Fall Detection* | ACM MobiCom 2014 | H. Wang, D. Zhang | Wi-Fi CSI | $\ge 100\text{ Hz}$ | Cinematica căderii ($v > 2.5\text{ m/s}$, Doppler $>35\text{ Hz}$, imobilitate $>2\text{ s}$) | Aliere spectrală dacă $f_s < 70\text{ Hz}$ |
| **[P4]** | *Multi-Link Indoor Localization* | IEEE TVT 2019 | J. Liu, Y. Chen | Multi-Link Wi-Fi | $\ge 50\text{ Hz}$ | Rang Jacobian 2 necesită 3 noduri necoliniare | Necesită sincronizare temporală simultană pe cele 3 legături |
| **[P5]** | *See Through Walls with WiFi! (Wi-Vi)* | ACM SIGCOMM 2013 | F. Adib, D. Katabi | Wi-Fi MIMO | $\ge 100\text{ Hz}$ | Eliminare reflexii masive pereți (Flash Effect) | Necesită antene inverse sau filtrare Butterworth IIR |
| **[P6]** | *Exploiting CSI Phase for Vital Signs* | IEEE TMC 2017 | X. Wang, S. Mao | Wi-Fi Phase | $\ge 40\text{ Hz}$ | Igienizare fază CSI pentru micro-mișcări toracice | Derivă de ceas hardware (CFO / SFO) |
| **[P7]** | *Time-Reversal Machine* | IEEE SPL 2017 | K. J. R. Liu, B. Wang | Wi-Fi Multipath | $\ge 50\text{ Hz}$ | Rezonanță multipath temporală ca lentilă fizică | Schimbarea mobilierului alterează amprenta statică |
| **[P8]** | *Non-Cooperative Wi-Fi Localization* | ACM MobiCom 2022 | A. Abedi, D. Vasisht | Wi-Fi ToF 802.11 | Răspuns nanosecunde | Audit ToF pe timpii de răspuns hardware 802.11 | Necesită măsurători ToF de ultra-înaltă precizie |
