# [P1] Fresnel Zone Based Indoor Localization and Activity Sensing

- **Autori:** Daqing Zhang, Hao Wang, Dan Wang
- **Publicație:** *IEEE/ACM Transactions on Networking (ToN)*, Vol. 25, Nr. 5, pp. 2843–2857, Oct. 2017
- **DOI:** [10.1109/TNET.2017.2721442](https://doi.org/10.1109/TNET.2017.2721442)
- **Cod BibTeX:** `@article{zhang2017fresnel, ...}` în `references_csi.bib`

---

## 1. Fundamente Fizice & Teoretice

Articolul introduce modelul analitic fundamental al **zonelor Fresnel** pentru detecția și localizarea pasivă fără senzori purtați (*device-free radio sensing*).

### 1.1. Lungimea de Undă și Frecvența Canalului Wi-Fi
Pentru canalul 6 Wi-Fi la frecvența centrală $f_c = 2.437\text{ GHz}$:
$$\lambda = \frac{c}{f_c} \approx 0.1231\text{ m} = 12.31\text{ cm}$$

### 1.2. Ecuația Elipselor Fresnel Confocale
Pentru o legătură între emițătorul $T$ și receptorul $R$ la distanța $D$:
$$|d(T, P) + d(P, R) - D| = n \frac{\lambda}{2}, \quad n \in \{1, 2, 3, \dots\}$$
- Frontiera zonei Fresnel de ordinul $n$ este definită de o diferență de fază de $n \cdot \pi$ ($n \lambda / 2$).
- **Pasul de modulație spațială (Spatial fringe):** $\Delta d = \lambda / 2 \approx 6.15\text{ cm}$. La fiecare deplasare a corpului uman cu $6.15\text{ cm}$ transversal pe elipsă, semnalul parcurge o alternanță completă interferență constructivă $\leftrightarrow$ distructivă (o oscilație sinusoidală completă a anvelopei CSI).

### 1.3. Raza Primei Zone Fresnel ($n=1$)
La mijlocul distanței ($d_1 = d_2 = D/2$):
$$r_1 = \frac{1}{2} \sqrt{\lambda D}$$
- La $D = 3\text{ m}$: $r_1 = \frac{1}{2}\sqrt{0.1231 \times 3} \approx 30.38\text{ cm}$.

---

## 2. Rolul în Proiectul Nostru de Licență

1. **Modelarea hărții camerei:** Implementată în [`src/dsp_lab/synthetic_gen.py`](file:///home/vlads4r4/dev/Licenta/src/dsp_lab/synthetic_gen.py) și afișată în interfața PyQt6 [`src/gui/widgets.py`](file:///home/vlads4r4/dev/Licenta/src/gui/widgets.py).
2. **Audit automat:** Verificat la nivel de milimetru în testul academic `verify_academic_compliance.py` (`audit_p1_fresnel_theory`), din skill-ul `verify-csi-academic`, eliminat pe 2026-11-04.
