# [P4] Multi-Link Indoor Localization Based on Wi-Fi CSI

- **Autori:** Jian Liu, Yingying Chen, Yan Wang, Xiaonan Chen, Jie Cheng
- **Publicație:** *IEEE Transactions on Vehicular Technology (TVT)*, Vol. 68, Nr. 11, pp. 11200–11211, Nov. 2019
- **DOI:** [10.1109/TVT.2019.2941199](https://doi.org/10.1109/TVT.2019.2941199)
- **Cod BibTeX:** `@article{liu2019multilink, ...}` în `references_csi.bib`

---

## 1. Localizare 2D pe Legături Multiple (Multi-Link)

Articolul demonstrează matematic de ce o singură legătură Wi-Fi este insuficientă pentru localizarea carteziană 2D $(x, y)$ și formulează sistemul pe legături multiple:

1. **Rangul Matricii Jacobiene:**
   - O singură pereche emițător-receptor $T_1-R_1$ generează o singură ecuație eliptică. Matricea Jacobiană $J = \left[\frac{\partial d_1}{\partial x}, \frac{\partial d_1}{\partial y}\right]$ are **rangul 1**. Sistemul este subdeterminat $\implies$ infinitate de soluții de-a lungul elipsei.
   - Folosirea a **3 noduri necoliniare** (ce formează un triunghi) produce 3 legături independente: $L_{1 \to 2}$, $L_{2 \to 3}$, $L_{3 \to 1}$.
   - Matricea Jacobiană asociată:
     $$J = \begin{bmatrix}
     \frac{\partial d_{12}}{\partial x} & \frac{\partial d_{12}}{\partial y} \\
     \frac{\partial d_{23}}{\partial x} & \frac{\partial d_{23}}{\partial y} \\
     \frac{\partial d_{31}}{\partial x} & \frac{\partial d_{31}}{\partial y}
     \end{bmatrix}$$
     are **rangul complet 2**, permițând convergența unică a algoritmilor de optimizare (Levenberg-Marquardt sau Gauss-Newton).

2. **Formularea Celor Mai Mici Pătrate Nelineare (NLLS):**
   $$\hat{P}(x, y) = \arg\min_{(x,y)} \sum_{i=1}^{3} w_i \left( \Delta \hat{d}_i^{\text{măsurat}} - \Delta d_i(x, y) \right)^2$$
   - Eroare medie obținută: sub $0.40\text{ m}$ în condiții de interior standard.

---

## 2. Limita de Sincronizare Identificată în Proiect

- În sistemul nostru ([`src/dsp_lab/localization.py`](file:///home/vlads4r4/dev/Licenta/src/dsp_lab/localization.py)), rezolvarea numerică stabilă cere ca măsurătorile $\Delta \hat{d}_i$ de pe toate cele 3 legături să fie disponibile simultan.
- Dacă citirea de pe porturile seriale are întârzieri sau pachete lipsă pe una dintre legături, rangul Jacobian scade instant la 1, iar cursorul de poziție $(X, Y)$ își pierde stabilitatea sau suferă salturi bruște (jitter).
- Aceasta este a doua limitare majoră documentată în secțiunea 7 din `Status_Licenta_CSI.html`.
