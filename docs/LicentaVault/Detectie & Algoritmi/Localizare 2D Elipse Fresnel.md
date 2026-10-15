---
title: Localizare 2D Elipse Fresnel
tags:
  - algoritmi
  - localizare
  - fresnel
  - 2d
aliases:
  - Localizare
  - Fresnel 2D
---

# 🎯 Cartografiere Radio 2D prin Intersecția Elipselor Fresnel

Sistemul estimează poziția în plan orizontal $(x, y)$ a persoanei fără senzori corporali, bazat pe modelul zonelor Fresnel (**Zhang et al., 2017**).

Implementarea completă se află în [`src/csi/localization.py`](file:///home/vlads4r4/dev/Licenta/src/csi/localization.py) și geometria camerei în [`src/csi/room.py`](file:///home/vlads4r4/dev/Licenta/src/csi/room.py).

---

## 🌐 Modelul Geometric Fresnel (`extra_path_m`)

Pentru fiecare legătură radio formată dintr-un emițător $TX$ și un receptor $RX$:
* Distanța directă în linie de vedere (LOS) este:
  $$d_{\text{direct}} = \| \mathbf{p}_{RX} - \mathbf{p}_{TX} \|$$
* Când o persoană se află la poziția $\mathbf{p} = (x, y)$, unda suferă o reflexie pe corpul dielectric uman, parcurgând un drum indirect:
  $$d_{\text{indirect}}(\mathbf{p}) = \| \mathbf{p} - \mathbf{p}_{TX} \| + \| \mathbf{p} - \mathbf{p}_{RX} \|$$
* **Lungimea suplimentară de drum ($\Delta d$):**
  $$\Delta d = d_{\text{indirect}}(\mathbf{p}) - d_{\text{direct}}$$

Implementat concis în [`src/csi/room.py`](file:///home/vlads4r4/dev/Licenta/src/csi/room.py#L20):

```python
def extra_path_m(point_xy, link):
    tx = np.array(NODE_POSITIONS_M[link[0]])
    rx = np.array(NODE_POSITIONS_M[link[1]])
    point = np.asarray(point_xy, dtype=float)
    reflected = np.linalg.norm(point - tx, axis=-1) + np.linalg.norm(point - rx, axis=-1)
    return reflected - np.linalg.norm(rx - tx)
```

Locul geometric al punctelor cu o lungime de drum constantă $\Delta d$ formează o **elipsă** având focarele în nodurile $TX$ și $RX$.

---

## 📐 Rezolvarea prin Optimizare Neliniară (`locate`)

Avem 3 legături radio simultane, generând un sistem de 3 ecuații de reziduuri rezolvat cu algoritmul **Levenberg-Marquardt** (`scipy.optimize.least_squares` cu limite pe spațiul camerei $5\text{m} \times 5\text{m}$):

```python
def locate(extra_paths_m, start_xy=(0.0, 0.0)):
    def residuals(point):
        return np.array([extra_path_m(point, link) - extra_paths_m[i] for i, link in enumerate(LINKS)])

    bound = ROOM_HALF_SIZE_M
    result = least_squares(residuals, start_xy, bounds=([-bound, -bound], [bound, bound]), method="trf")
    return result.x[0], result.x[1]
```

---

## 🏃 Filtrarea Traiectoriei și Rezultate (`track_with_noisy_ranges`)

Pentru a evalua acuratețea, traiectoria simulată este perturbată cu zgomot gaussian realist de distanță ($\sigma = 7\text{ cm}$, `RANGE_NOISE_STD_M = 0.07`), iar estimările sunt netezite exponențial (`SMOOTHING = 0.4`):

$$
\mathbf{p}_k^{\text{filt}} = (1 - \alpha) \mathbf{p}_{k-1}^{\text{filt}} + \alpha \mathbf{p}_k^{\text{sol}}
$$

### Precizie Măsurată în Simulare:
* **Eroare Medie Pătratică (RMSE):** **0.043 metri** ($4.3\text{ cm}$) pe porțiunea de mers activ ($3\text{s} - 10\text{s}$).

![[3_trajectory_cartography.png|800]]

*Harta 2D a încăperii: triunghiul celor 3 noduri ESP32, elipsele Fresnel intersectate și traiectoria ground truth comparată cu traiectoria estimată.*
