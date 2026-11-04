# [P5] See Through Walls with WiFi! (Wi-Vi)

- **Autori:** Fadel Adib, Dina Katabi
- **Publicație:** *ACM SIGCOMM 2013*, pp. 75–86, Aug. 2013
- **DOI:** [10.1145/2486001.2486039](https://doi.org/10.1145/2486001.2486039)
- **Fișier PDF Local:** [`docs/Materials/CSI_Sensing/sources-2026-10-21/Adib_2013_See_Through_Walls_with_WiFi.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/sources-2026-10-21/Adib_2013_See_Through_Walls_with_WiFi.pdf)
- **Cod BibTeX:** `@inproceedings{adib2013seethroughwalls, ...}` în `references_csi.bib`

---

## 1. Contribuție & Inovație Tehnică

Articolul de referință al grupului MIT CSAIL demonstrează capacitatea semnalelor Wi-Fi comerciale de a detecta mișcarea umană prin obstacole solide (pereți de cărămidă, beton, lemn):

1. **Problema Reflexiilor Statice (Flash Effect):**
   - Reflexia undei directe de pe perete este cu $10^4 - 10^5$ ori mai puternică ($40 - 50\text{ dB}$) decât reflexia minusculă venită de la corpul uman din spatele peretelui.
   - Receptorul se saturează dacă nu se aplică anularea semnalului static.

2. **Soluția de Anulare a Componentei Statice:**
   - Wi-Vi utilizează două antene de transmisie în antifază ($180^\circ$ defazaj) pentru a anula direct pe receptor semnalul static provenit de la perete.
   - În proiectul nostru, eliminarea reflexiilor parazite statice este realizată analitic în banda de bază prin **filtrare trece-bandă Butterworth IIR (0.2–8.0 Hz)** și scăderea mediei dinamice a liniei de bază (baseline subtraction), fără a necesita hardware RF complex cu anulare analogică.
