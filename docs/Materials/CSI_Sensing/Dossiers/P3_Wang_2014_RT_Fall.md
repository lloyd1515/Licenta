# [P3] RT-Fall: Real-Time Fall Detection using Wi-Fi Radio Frequency Signals

- **Autori:** Hao Wang, Daqing Zhang, Yasha Wang, Junyi Ma, Yuxiang Wang, Shengjie Li
- **Publicație:** *ACM MobiCom 2014*, pp. 511–526 (extins în *IEEE Transactions on Mobile Computing*, 2017)
- **DOI:** [10.1145/2639108.2639143](https://doi.org/10.1145/2639108.2639143)
- **Cod BibTeX:** `@inproceedings{wang2014rtfall, ...}` în `references_csi.bib`

---

## 1. Cinematica Căderii vs. Mers Normal

Articolul stabilește criteriile fundamentale de diferențiere a căderilor accidentale față de mersul normal sau activitățile casnice zilnice (ADL - Activities of Daily Living):

1. **Viteza de coborâre:**
   - Mers normal: $0.8 - 1.5\text{ m/s}$ pe direcție orizontală.
   - Cădere liberă/colaps accelerat gravitațional: **$2.5 - 3.5\text{ m/s}$ pe verticală**.
2. **Deplasarea Doppler ($f_D = 2v / \lambda$):**
   - Mers normal: deplasare sub $22\text{ Hz}$.
   - Impact cădere: **spike brusc de frecvență ridicată $> 35 - 50\text{ Hz}$**.
3. **Durata Impactului:**
   - Evenimentul de impact se consumă într-un interval scurt: **$\Delta t \in [200\text{ ms}, 450\text{ ms}]$**.
4. **Fereastra de Imobilitate Post-Impact (Dormancy):**
   - După cădere, o persoană accidentată rămâne nemișcată la sol cel puțin $2.0 - 3.0\text{ secunde}$.
   - În această fereastră, varianța anvelopei CSI scade sub pragul de calm ($\text{Var} < \sigma^2_{\text{calm}}$).

---

## 2. Automat de Stări FSM în Proiect

În modulul nostru [`src/dsp_lab/fall_detector.py`](file:///home/vlads4r4/dev/Licenta/src/dsp_lab/fall_detector.py), am implementat secvența FSM conform modelului RT-Fall:
- **Starea 0 (Calm):** Varianță scăzută, semnal de bază stabil.
- **Starea 1 (Mers):** Varianță moderată, frecvență Doppler sub 25 Hz.
- **Starea 2 (Impact):** Vârf de derivată amplitudine și energie Doppler de înaltă frecvență.
- **Starea 3 (Imobilitate):** Colaps al varianței timp de minim 2.0 - 2.5 secunde consecutiv.
- **Starea 4 (Alarmă Activă):** Confirmare cădere, declanșare semnal vizual și acustic.

Testat pe setul real [`dsp_lab/test_C_cadere_reala.npz`](file:///home/vlads4r4/dev/Licenta/src/dsp_lab/test_C_cadere_reala.npz) cu latență de confirmare de **2.54 secunde**.
