---
title: Analiza Critica si Whiteboard Defense
tags:
  - defense
  - whiteboard
  - intrebari
  - licenta
aliases:
  - Whiteboard Defense
  - Intrebari Comisie
---

# 🎓 Ghid de Apărare Tehnică: Whiteboard Defense

Acest document sintetizează întrebările dificile, deciziile critice de arhitectură și capcanele pe care profesorii din comisia de licență sau recrutorii tehnici le pot ridica la tablă.

---

## 🥊 Întrebări Cheie și Argumentația de Apărare

### 1. De ce filtrezi cu Hampel înainte de filtrul Butterworth?
> **Răspuns la tablă:**
> Filtrul Butterworth este un filtru IIR (*Infinite Impulse Response*) cu feedback autoregresiv. Dacă un spike hardware masiv (produs de comutarea LNA din radioul ESP32) intră într-un filtru IIR, răspunsul său la impuls va genera o oscilație tranzitorie falsă (*ringing*) pe durata a 1–2 secunde în semnalul filtrat, declanșând alarme false pe derivată. Filtrul Hampel elimină punctual valorile aberante (prin mediana locală și MAD) înainte ca semnalul să atingă filtrele cu memorie.

---

### 2. De ce folosești PCA în loc să faci media celor 52 de subpurtătoare?
> **Răspuns la tablă:**
> Într-o cameră cu multipath intens, apare fenomenul de **fading selectiv în frecvență**. Două subpurtătoare la distanță de câțiva megahertzi pot avea faze opuse la trecerea corpului (una suferă interferență constructivă, cealaltă distructivă). O medie aritmetică simplă ar duce la anularea reciprocă a semnalelor, distrugând perturbația utilă. PCA identifică primul vector propriu al matricei de covarianță, aliniind optim contribuțiile tuturor subpurtătoarelor pe direcția de variație maximă.

---

### 3. Cum distinge sistemul o cădere reală de așezarea energică pe un scaun?
> **Răspuns la tablă:**
> Prin două mecanisme fizice distincte:
> 1. **Cinematică de impact:** Așezarea pe un scaun este un proces controlat muscular (viteza verticală este rar peste $1.0\text{ m/s}$, iar Doppler rămâne sub $20\text{ Hz}$). Căderea liberă gravitațională este accelerată ($v > 2.5\text{ m/s}$), producând un Doppler de peste $35\text{ Hz}$ și un colaps abrupt de pantă $|dA/dt| > 17.5$ simultan pe $\ge 2$ legături.
> 2. **Fereastra de imobilitate (`VERIFY_DORMANCY`):** Chiar dacă o așezare pe fotoliu atinge accidental pragul de derivată, FSM așteaptă 2.5 secunde. O persoană așezată pe scaun respiră, își mișcă mâinile sau își ajustează poziția ($\text{Var} > 0.20 \implies$ tranziție înapoi în `WALKING`). Doar victima inertă la sol menține varianța minimă ($\text{Var} < 0.20$), confirmând starea de urgență.

---

### 4. Sistemul tău are "98% acuratețe în lumea reală"?
> **Răspuns onest la tablă:**
> **Nu.** Numerele de detecție din simulare reprezintă *self-consistency* (detectorul și simulatorul au fost proiectate pe baza aceluiași model fizic de propagare). Pe date hardware reale avem la dispoziție un set restrâns ($n=3$ înregistrări: cameră goală, mers, cădere). Este un *proof-of-concept funcțional cu zero alarme false pe testele existente*, dar validarea clinică statistică necesită sute de voluntari și zeci de tipologii de încăperi, aspect lăsat ca direcție de dezvoltare viitoare.

---

## 🚫 Ce să NU pretinzi niciodată în prezentare

* **NU spune că este "AI" sau "Agentic Fall Detection":** Pipeline-ul este matematic și determinist (DSP + FSM). Nu există modele LLM sau rețele neurale în codul de detecție.
* **NU prezenta erorile din simulator (RMSE 0.043 m) drept precizie garantată în orice clădire:** Spațiile reale au mobilier metalic, pereți de beton armat și atenuări complexe care măresc eroarea.
* **NU ascunde discrepanța de praguri (0.20 vs 11.0):** Prezint-o ca o trăsătură de adaptare a detectorului între date normalizate și reprezentarea ADC întreagă a cipului ESP32.
