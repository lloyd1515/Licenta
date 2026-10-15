---
title: Dicționar Fizică și Propagare Unde
tags:
  - licenta
  - fizica
  - propagare
  - fresnel
  - doppler
  - reflexie
aliases:
  - Dictionar Fizica
  - Fizica si Unde
  - Ghid Propagare Unde
---

# 🌊 Dicționar Fizică și Propagare Unde: Cum se Comportă Undele Radio în Cameră

> [!tip] Despre acest ghid
> Nu trebuie să fii fizician ca să înțelegi cum funcționează radarul Wi-Fi! Aici vei descoperi fenomenele fizice fascinante (reflexia, zonele Fresnel, efectul Doppler și gravitația) explicate prin exemple simple din natură: valuri pe un lac, baloane de rugby și sirene de ambulanță.

---

## 🪞 1. Cum Călătoresc Undele prin Cameră: Cei Trei Călători

Când transmițătorul Wi-Fi emite un semnal, acesta nu este o linie dreaptă subțire ca un laser. Unda radio se propagă ca un val tridimensional care umple întreaga cameră, întâlnind obstacole și comportându-se în 3 moduri distincte:

```
        1. REFLEXIE (Oglinda)
        [Unda] --------\
                        \====> [Perete/Corp] ----> Ricoșează mai departe
        
        2. DIFRACȚIE (Ocolirea obstacolului)
        [Unda] --------+
                       | [Colț Ușă]
                       +------------> Se curbează după colț
        
        3. ATENUARE (Filtrarea prin perdea)
        [Unda] --------> [Perete Cărămidă] ------> Iese mult mai slabă
```

### 1. Reflexia (Oglinda radio)
* Exact cum lumina se reflectă într-o oglindă de baie, unda Wi-Fi ricoșează din suprafețele netede: pereți de beton, gresie, faianță și, cel mai important, **din corpul uman**.
* Unghiul sub care unda lovește corpul este egal cu unghiul sub care sare mai departe spre antenele de recepție.

### 2. Difracția (Ocolirea colțurilor)
* Dacă un prieten vorbește cu tine din camera alăturată printr-o ușă deschisă, îl auzi perfect chiar dacă nu îl vezi direct. De ce? Unda de sunet „ocolește colțul” tocului de ușă.
* Undele Wi-Fi fac exact același lucru! Când o undă atinge marginea unei piese de mobilier sau muchia peretelui, ea se îndoaie și umple spațiul din spatele obstacolului. De aceea poți avea semnal Wi-Fi chiar dacă ești ascuns după un dulap.

### 3. Atenuarea (Pierderea de putere)
* Când unda trece printr-un material solid (aer, perdele, uși de lemn, corp omenesc), o parte din energia ei este absorbită și transformată într-o cantitate microscopică de căldură.
* Semnalul care iese de pe cealaltă parte a obstacolului are o amplitudine mai mică (este mai „obosit”).

---

## 👤 2. Corpul Uman ca Dielectric: De ce suntem un „Stâlp Reflectorizant de Apă Sărată”

De ce detectează Wi-Fi-ul atât de ușor omul, dar ignoră o pernă sau o cutie de carton?

> [!info] Ce conține corpul nostru?
> Corpul uman adult este format din peste **70% apă**, îmbogățită cu săruri minerale dizolvate (sodiu, potasiu, clorură - electroliți).

În fizică, un material care interacționează puternic cu câmpurile electromagnetice se numește **dielectric cu pierderi**:
* **Constanta dielectrică relativă a apei la $2.4\text{ GHz}$** este foarte mare ($\epsilon_r \approx 50 - 60$), în timp ce aerul are doar $\epsilon_r \approx 1$.
* Din perspectiva unei unde radio Wi-Fi, când un om stă în picioare în mijlocul camerei, el nu arată ca un sac de oase, ci ca un **cilindru uriaș de apă sărată, înalt de 1.7 metri, cu proprietăți puternic reflectante**!

Aproximativ jumătate din unda Wi-Fi care te lovește ricoșează ca o minge dintr-un zid (reflexie), iar cealaltă jumătate este atenuată în interiorul țesutului. Fiecare pas, fiecare mișcare a mâinii sau fiecare cădere modifică radical traseul ecourilor din încăpere.

---

## 🌊 3. Interferența Constructivă și Distructivă: Jocul Valurilor

Ce se întâmplă atunci când la antena receptorului sosesc în același moment două unde: unda directă (care a venit drept prin aer) și un ecou (care a ricoșat mai întâi din corpul tău)?

### Analogia pietricelelor aruncate în lac
Dacă arunci două pietricele în apă la mică distanță una de alta, ambele creează cercuri de valuri concentrice. Unde cercurile se întâlnesc:

```
   Val 1:     /\__/\__/\       Val 1:     /\__/\__/\
   Val 2:     /\__/\__/\       Val 2:     \/__\/__\/ (în contratimp)
   ---------------------       ---------------------
   REZULTAT:  /¯¯\__/¯¯\       REZULTAT:  ---------- (linie dreaptă!)
   (Constructivă: Dublu!)      (Distructivă: Zero semnal!)
```

1. **Interferență Constructivă (Undele se ajută):**
   * Creasta valului 1 se suprapune perfect peste creasta valului 2.
   * Cele două energii se adună: la antenă, semnalul Wi-Fi devine brusc **de două ori mai puternic**!
2. **Interferență Distructivă / Fading (Undele se anulează):**
   * Creasta valului 1 se întâlnește exact cu o adâncitură (vale) a valului 2.
   * Ele se anulează reciproc: semnalul Wi-Fi la antenă **scade aproape la zero**, deși transmițătorul emite la putere maximă!

Când un om face un singur pas de 10 centimetri, lungimea drumului parcurs de ecou se schimbă. Antena trece continuu de la interferență constructivă la distructivă. Aceste oscilații ritmice reprezintă exact „bătăile inimii” semnalului CSI pe care le monitorizăm!

---

## 🏉 4. Zonele Fresnel: Balonul de Rugby și Coardele de Chitară din Aer

Unul dintre cele mai importante concepte din lucrare este **Zona Fresnel** (numită după fizicianul francez Augustin-Jean Fresnel).

### Ce este Zona Fresnel?
Între antena de emisie ($TX$) și antena de recepție ($RX$), energia undelor nu circulă doar pe o linie milimetrică. Ea ocupă un volum spațial 3D în formă de **balon de rugby invizibil** întins între cele două aparate.

```
                  . - ~ ~ ~ - .
              . '               ' .
           .                         .
[ Nod TX ] =========================== [ Nod RX ]  (Axa directă LoS)
           .                         .
              . ,               , .
                  ' - ~ ~ ~ - '
            <- Balon de rugby Fresnel ->
```

Raza maximă a acestui balon de rugby la mijlocul distanței se calculează prin formula:

$$r_1 = \frac{1}{2} \sqrt{\lambda \cdot d}$$

Unde:
* $\lambda = 0.123\text{ m}$ (lungimea de undă la Canalul 6).
* $d = 4\text{ m}$ (distanța între antene).
* $r_1 \approx \frac{1}{2} \sqrt{0.123 \times 4} = \frac{1}{2} \sqrt{0.492} \approx 0.35\text{ metri} = 35\text{ centimetri}$.

> [!tip] Analogia corzilor de chitară
> Imaginează-ți spațiul dintre cele două antene ca fiind plin de o serie de coarde invizibile de chitară concentrice (Zonele Fresnel 1, 2, 3...).
> * Când camera este goală, corzile stau în liniște deplină.
> * Când pășești în cameră și corpul tău taie marginea unui balon Fresnel, este ca și cum **ai ciupi o coardă de chitară**.
> * La fiecare $\frac{\lambda}{2} \approx 6\text{ centimetri}$ parcurși de corpul tău, semnalul CSI face o oscilație completă (urcă pe un vârf și coboară într-o vale).

Prin urmărirea acestor elipse pe cele 3 noduri, sistemul poate calcula cu acuratețe milimetrică traiectoria omului prin cameră. Vezi [[Localizare 2D Elipse Fresnel]].

---

## 🚑 5. Efectul Doppler: Sirena de Ambulanță a Căderii

### Ce este Efectul Doppler?
Cu toții am trăit această experiență pe stradă:
* Când o **ambulanță vine spre tine cu viteză**, sunetul sirenei este **ascuțit, pițigăiat** (frecvență înaltă), pentru că mașina comprimă undele sonore în fața ei.
* În secunda în care trece de tine și **se îndepărtează**, sunetul devine brusc **grav și gros** (frecvență joasă), deoarece undele se dilată în spatele ei.

```
   Ambulanță în viteză --->  ))))) [Urechea Ta] (Unde comprimate = Frecvență Mare)
```

Undele radio pățesc exact același lucru! Când un corp se mișcă spre o antenă cu viteza $v$, ecoul ricoșat suferă o **deplasare Doppler de frecvență** ($f_D$):

$$f_D = \frac{v}{\lambda} \cdot \cos(\theta)$$

### Mers normal vs. Cădere bruscă

| Mișcare | Viteză Corp ($v$) | Frecvență Doppler ($f_D$) | Aspect pe Spectrogramă |
| :--- | :--- | :--- | :--- |
| **Om nemișcat (pe scaun)** | $0\text{ m/s}$ | $0\text{ Hz}$ | Linie perfect plată, liniște totală |
| **Mers normal la pas** | $0.5 - 1.2\text{ m/s}$ | **$10 - 20\text{ Hz}$** | Unduiri line, ritmice, la frecvențe joase |
| **Cădere violentă pe podea** | **$> 2.5\text{ m/s}$** | **$> 35\text{ Hz}$ (Vârf uriaș!)** | **„Munte” exploziv pe ecran în câteva milisecunde** |

Când un bătrân merge prin cameră, viteza corpului este moderată ($10-20\text{ Hz}$). Când se împiedică și cade, gravitația îl accelerează spre podea la peste $2.5\text{ m/s}$, producând un **semnal Doppler exploziv de peste $35\text{ Hz}$**. Acest vârf uriaș este semnătura inconfundabilă a căderii!

Pentru detalii despre cum calculăm această spectrogramă prin STFT, vezi [[Spectrograma Micro-Doppler]].

---

## ⏱️ 6. Gravitația și Accelerația Căderii: Colapsul sub 400 de Milisecunde

De ce este imposibil să confunzi o cădere reală cu o așezare pe canapea? Datorită legilor nemiloase ale gravitației terestre.

Când un om stă în picioare, centrul său de greutate se află la aproximativ $h = 1\text{ metru}$ deasupra podelei. Dacă își pierde echilibrul sau leșină, el intră în cădere liberă sub influența accelerației gravitaționale ($g = 9.81\text{ m/s}^2$).

Timpul fizic necesar pentru a atinge podeaua este:

$$t_{\text{cădere}} = \sqrt{\frac{2h}{g}} = \sqrt{\frac{2 \times 1.0\text{ m}}{9.81\text{ m/s}^2}} \approx \sqrt{0.204} \approx 0.45\text{ secunde} = 450\text{ milisecunde!}$$

> [!important] De ce nu există alarme false la așezarea pe scaun?
> * **Când te așezi pe canapea:** Creierul tău folosește mușchii picioarelor pentru a frâna controlat coborârea. Mișcarea durează între $1.5$ și $2.5\text{ secunde}$, viteza rareori depășește $0.8\text{ m/s}$, iar la final corpul se mișcă în continuare (respiri, te aranjezi pe pernă).
> * **Când cazi pe podea:** Este un **colaps necontrolat sub 400–500 ms**, viteza atinge $2.5 - 3.5\text{ m/s}$, impactul produce o decelerare violentă, urmată de o **nemișcare suspectă și prelungită** la nivelul solului (doleanță / pierdere de cunoștință).

Algoritmul nostru logic urmărește această cronologie strictă în 5 pași. Dacă evenimentul a fost prea lent, sistemul știe că a fost doar o așezare pe scaun și ignoră alarma.

Pentru mecanismul decizional complet, vezi [[Detector Cadere FSM]].

---

## 🔗 Continuă explorarea

* Ghidul introductiv simplu: [[00 - Ghid pentru Incepatori (De la Zero)]]
* Componentele electronice și pachetele de date: [[01 - Dictionar Hardware si Retea]]
* Matematică și procesare de semnal: [[03 - Dictionar Matematica si DSP]]
* Schema arhitecturală completă a sistemului: [[01 - Arhitectura Sistem]]
* Indexul general al lucrării: [[00 - Start Aici]]
