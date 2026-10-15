# [P6] PhaseBeat: Exploiting CSI Phase for Vital Signs Monitoring with Commodity WiFi Devices

- **Autori:** Xuyu Wang, Chao Yang, Shiwen Mao
- **Publicație:** *IEEE Transactions on Mobile Computing (TMC)*, Vol. 16, Nr. 10, pp. 2803–2816, Oct. 2017
- **DOI:** [10.1109/TMC.2017.2706338](https://doi.org/10.1109/TMC.2017.2706338)
- **Preprint arXiv:** [arXiv:1709.02897](https://arxiv.org/abs/1709.02897)
- **Fișier PDF Local:** [`docs/Materials/CSI_Sensing/PDFs/P6_Wang_2017_PhaseBeat_VitalSigns.pdf`](file:///home/vlads4r4/dev/Licenta/docs/Materials/CSI_Sensing/PDFs/P6_Wang_2017_PhaseBeat_VitalSigns.pdf)
- **Cod BibTeX:** `@article{wang2017phasebeat, ...}` în `references_csi.bib`

---

## 1. Contribuție & Inovație Tehnică

1. **Sensibilitatea Fazei CSI:**
   - Deplasările milimetrice ale cutiei toracice provocate de respirație ($5 - 12\text{ mm}$) și puls ($0.2 - 0.5\text{ mm}$) produc variații infime de amplitudine, dar produc deplasări clare de fază:
     $$\Delta \theta = \frac{2\pi}{\lambda} \cdot 2 \Delta d$$
   - La $\lambda = 12.31\text{ cm}$, o deplasare toracică de $5\text{ mm}$ induce un defazaj de $\approx 0.51\text{ rad} \approx 29.3^\circ$.

2. **Igienizarea Fazei (Phase Sanitization):**
   - Erorile de sincronizare a ceasului hardware (Carrier Frequency Offset - CFO, Sampling Frequency Offset - SFO) cauzează o derivă liniară a fazei brute.
   - Articolul propune eliminarea derivei prin transformare liniară:
     $$\hat{\theta}_k = \theta_k - a k - b$$
     unde $a$ și $b$ sunt panta și originea deduse prin regresie pe cele 52 de subpurtătoare active.

3. **Relevanță pentru Starea de Cădere:**
   - În starea post-impact (starea 3 - Imobilitate a FSM-ului), monitorizarea variațiilor fine de fază poate confirma dacă persoana căzută respiră sau este în stop respirator.
