---
title: Dicționar Matematică și DSP
tags:
  - dsp
  - matematica
  - ghid
  - analogii
  - incepatori
aliases:
  - Dictionar DSP
  - Dictionar Matematica
  - Ghid DSP
---

# 📚 Dicționar Matematică și DSP (Digital Signal Processing)

> [!tip] Pentru cine este acest ghid?
> Acest document este scris pentru **oricine pornește de la zero**. Fără formule aruncate la întâmplare, fără jargon academic neprietenos. Folosim analogii din viața de zi cu zi (ceasuri, bucătari, site de făină, umbre și partituri muzicale) pentru a înțelege exact ce se întâmplă în spatele ecranului atunci când undele Wi-Fi detectează o cădere.

---

## 🍳 1. Ce este DSP? Bucătăria Digitală a Semnalelor

Dacă auzi termenul pompos **DSP** (*Digital Signal Processing* sau *Procesarea Digitală a Semnalului*), gândește-te la o **bucătărie profesională de restaurant**.

* **Ingredientele brute:** Din aer, antenele Wi-Fi adună mii de numere pe secundă. Aceste numere sunt precum legumele abia scoase din pământ: pline de noroi, rădăcini uscate și pietricele.
* **Bucătăria DSP:** Este spațiul de lucru în care curățăm, spălăm, tocăm și filtrăm aceste date brute.
* **Preparatul final:** DSP-ul aruncă la gunoi noroiul (interferențele și zgomotul electric) și păstrează doar esența curată — de exemplu: *"Un om a pășit spre stânga"* sau *"Cineva s-a prăbușit brusc la podea"*.

Fără DSP, datele venite de la cipul Wi-Fi ar fi doar un haos indescifrabil de cifre. Cu DSP, ele devin o vedere clară, cu raze X, asupra camerei.

Codul din proiect care se ocupă de această bucătărie se află în:
[`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py).

---

## ⏰ 2. Numere Complexe ($I$ și $Q$, Real și Imaginar)

La școală, numerele complexe ($z = a + b \cdot j$) păreau o abstracțiune inventată pentru a chinui elevii. În radiocomunicații și Wi-Fi, ele au o reprezentare fizică extrem de intuitivă: **un ceas cu o singură limbă**.

Imaginează-ți cadranul unui ceas mecanic:
* **Lungimea limbii ceasului = Amplitudinea (Puterea Semnalului):**
  Cât de lungă este limba indică cât de puternică a ajuns unda la antenă. Dacă semnalul a traversat un perete gros, limba se scurtează (putere mică). Dacă unda a călătorit prin aer curat direct la antenă, limba este lungă (putere mare).
* **Direcția unde arată limba pe cadran = Faza (Unghiul Undei):**
  Arată limba spre ora 12? Sau spre ora 3? Sau spre ora 6? Aceasta este **Faza** $\theta$. Ea ne spune în ce punct al oscilației sale se afla unda în milisecunda exactă în care a atins antena.
* **Componentele $I$ și $Q$ (Umbrele limbii de ceas):**
  Cipul electronic nu măsoară direct lungimea și unghiul. El măsoară două proiecții:
  * **$I$ (In-Phase / Partea Reală):** Umbra lăsată de limbă pe axa orizontală (stânga - dreapta).
  * **$Q$ (Quadrature / Partea Imaginară):** Umbra lăsată de limbă pe axa verticală (sus - jos).

$$
z = I + j \cdot Q
$$

$$
\text{Amplitudine} = \sqrt{I^2 + Q^2}, \qquad \text{Fază} = \arctan\left(\frac{Q}{I}\right)
$$

```
           +Q (Imaginar)
                 ▲
                 │     / Limba ceasului (Semnalul CSI)
                 │    /  Lungime = Amplitudine
                 │   /
                 │  / ) Unghi = Faza (θ)
                 │ /
  ───────────────┼────────────────► +I (Real)
                 │  Umbra orizontală = I
                 │  Umbra verticală  = Q
```

> [!info] De ce ne pasă de Fază?
> Când un om se mișcă doar 3 centimetri în cameră, unda Wi-Fi parcurge o distanță puțin diferită, iar limba ceasului se rotește complet! Faza este mult mai sensibilă la mișcări fine (cum ar fi respirația sau tremurul) decât simpla putere a semnalului.

---

## 📺 3. Zgomotul AWGN: Puricii de pe Televizorul Vechi

**AWGN** vine de la *Additive White Gaussian Noise* (Zgomot Alb Gaussian Aditiv). 

* **Analogia:** Îți amintești televizoarele vechi cu tub catodic când scoteai mufa de antenă? Ecranul se umplea de "purici" albi și negri care fâșâiau haotic. Sau gândește-te la sunetul ploii torențiale pe un acoperiș de tablă.
* **De unde vine în Wi-Fi?** În orice cip electronic din lume, electronii se agită natural din cauza temperaturii ambiante. Această agitație creează un fâșâit continuu pe fundal.
* **De ce este "Aditiv"?** Pentru că se adună peste semnalul nostru util:
  $$
  \text{Semnal Primit} = \text{Semnal Om} + \text{Zgomot AWGN}
  $$
* **Cum îl combatem?** Folosind filtre statistice și medieri (despre care vorbim mai jos).

---

## ⚡ 4. Spike-urile LNA: Salturile False ale Amplificatorului

În interiorul fiecărui receptor Wi-Fi ESP32 există un bloc numit **LNA** (*Low-Noise Amplifier* sau Amplificator cu Zgomot Redus).

* **Analogia:** Conduci o mașină manuală și apeși brutal ambreiajul, iar mașina smucește violent dintr-o treaptă în alta. Sau gândești-te la un megafon cu reglaj automat de volum care, la cea mai mică șoaptă, sare brusc pe treapta maximă pentru o miime de secundă și îți sparge timpanele.
* **Ce se întâmplă fizic:** Receptorul vrea să țină semnalul la un nivel constant. Dacă semnalul slăbește o fracțiune de secundă, LNA schimbă automat treapta de amplificare.
* **Efectul pe date:** Această comutare bruscă generează un **spike** (un salt enorm și complet fals) pe un singur eșantion. Semnalul era la valoarea 40, sare pentru o milisecundă la 400, apoi revine la 40!
* **Capcana mortală:** Dacă un algoritm naiv vede acel 400, va crede că s-a prăbușit tavanul camerei! De aceea, avem nevoie de un "arbitru" vigilent care să șteargă aceste salturi false înainte de orice alt calcul. Acest arbitru este **Filtrul Hampel**.

---

## ⚖️ 5. Filtrul Hampel și MAD: Arbitrul cu Bun Simț

Cum distingem un salt fals (un spike LNA de 1 milisecundă) de o cădere reală a unui om (care durează sute de milisecunde)?

* **Analogia:** Ședința asociației de locatari cu 7 vecini.
  7 vecini discută despre temperatura apei calde. 6 dintre ei spun: *"La mine are 42, 43, 41, 42, 44, 43 de grade"*. Al șaptelea vecin zbiară din senin: *"La mine are 10.000 de grade!"*.
  * Ce ar face o **medie aritmetică obișnuită**? Ar aduna toate valorile și ar spune: *"Temperatura medie a blocului este de 1.465 de grade!"* — o absurditate totală! Un singur nebun a distrus tot calculul.
  * Ce face **Filtrul Hampel**? Este arbitrul cu bun simț. El ordonează valorile crescător și alege valoarea din mijloc: **Mediana** (care este 42.5 grade).

### Cum funcționează MAD (*Median Absolute Deviation*):
Mediana nu se lasă păcălită de extreme. Pentru a măsura cât de răspândite sunt valorile normale, filtrul calculează **Abaterea Mediană Absolută (MAD)**:

$$
\text{MAD} = 1.4826 \times \text{median}(|x_i - \text{median}(x)|)
$$

Arbitrul compară fiecare punct cu cei 3 vecini din stânga și cei 3 din dreapta (o fereastră de 7 puncte). Dacă punctul curent sare la mai mult de $3 \times \text{MAD}$ distanță de mediană, arbitrul îl declară "fals / nebun" și îl înlocuiește pe loc cu valoarea mediană a vecinilor săi.

Spike-ul LNA dispare fără urmă, iar semnalul rămâne neted și curat!

> [!tip] Implementarea în Proiect
> Găsești funcția la linia 38 din [`src/csi/dsp.py`](file:///home/vlads4r4/dev/Licenta/src/csi/dsp.py#L38):
> ```python
> def remove_outliers(amplitude, window=7, sigmas=3.0):
>     # Înlocuiește valorile aberante cu mediana locală folosind sliding_window_view
> ```
> Mai multe detalii tehnice în [[Filtrare Hampel si Butterworth]].

---

## 🌾 6. Filtrul Butterworth Trece-Bandă (0.2 – 12.0 Hz)

După ce am curățat spike-urile, semnalul conține încă lucruri care nu ne interesează. Avem nevoie de o **sită de cernut**.

* **Analogia Sitei de Făină:**
  Când cerni făină pentru prăjituri, vrei doar făina fină. Sita oprește cocoloașele mari și pietricelele, dar lasă să curgă doar pulberea aerată.

În semnalul Wi-Fi din cameră există trei lumi diferite:
1. **Lumea Imobilă ($0\text{ Hz}$ - Componenta Continuă):** Pereții din beton, dulapul, biroul, canapeaua. Ele reflectă 90% din undele Wi-Fi! Semnalul lor este uriaș, dar este complet inert (frecvență zero). Filtrul nostru taie tot ce este sub $0.2\text{ Hz}$ pentru a ignora complet mobilierul.
2. **Lumea Electronică Rapidă ($> 12\text{ Hz}$):** Vibrația compresorului de la frigider, paraziții de rețea electrică la 50 Hz, zgomotul termic. Filtrul nostru taie tot ce depășește $12\text{ Hz}$.
3. **Lumea Corpului Uman ($0.2\text{ Hz} - 12.0\text{ Hz}$):** Aceasta este banda de aur! Toracele omului când respiră se mișcă la $\approx 0.3\text{ Hz}$. Picioarele când merg oscilează la $1 - 3\text{ Hz}$. Un corp în cădere accelerează spre podea și produce componente până la $8 - 12\text{ Hz}$.

### De ce "Filtrare cu Fază Zero" (`filtfilt`)?
* **Analogia Trenului care nu Întârzie:**
  Dacă treci un semnal printr-un filtru obișnuit, operațiile matematice introduc o mică întârziere în timp (un decalaj de fază). Imaginați-vă că omul cade la secunda `10.0`, dar filtrul scoate semnalul la secunda `10.3`!
* **Soluția elegantă (`scipy.signal.filtfilt`):**
  Rulăm filtrul Butterworth de două ori: o dată **înainte** (de la trecut spre viitor) și o dată **înapoi** (de la viitor spre trecut). Decalajul introdus la prima trecere este anulat matematic la a doua trecere!
  Rezultatul: **decalaj de timp strict ZERO**. Momentul impactului este raportat cu precizie de milisecundă.

---

## 👥 7. PCA: Teatrul de Umbre pe Perete

**PCA** înseamnă *Principal Component Analysis* (Analiza Componentelor Principale). Sună înfricoșător, dar este un simplu joc de lumini și umbre.

* **Problema celor 52 de dimensiuni:**
  Cipul nostru Wi-Fi nu trimite un singur semnal. Conform standardului OFDM (802.11n), el folosește **52 de subpurtătoare** paralele (52 de canale mici de frecvență).
  Cum poate creierul sau un algoritm să urmărească 52 de grafice simultan pentru a vedea dacă a căzut cineva? Este mult prea complicat.
* **Analogia Teatrului de Umbre:**
  Imaginează-ți că ai în mână o sculptură complicată din sârmă cu 52 de laturi încurcate în spațiu 3D.
  Iei o lanternă puternică și proiectezi umbra sculpturii pe un perete alb 2D.
  * Dacă ții lanterna la întâmplare, umbra e un ghemotoc confuz.
  * Dar dacă rotești lanterna până găsești **unghiul perfect**, umbra proiectată pe perete dezvăluie clar conturul persoanei și toată mișcarea ei!
* **Ce este PC1 (Prima Componentă Principală)?**
  PCA este algoritmul matematic care găsește automat acel "unghi perfect al lanternei". El fuzionează cele 52 de subpurtătoare într-un **singur semnal esențial (PC1)**, care păstrează peste 80% din toată energia mișcării umane și aruncă zgomotul redundant.

> [!info] Consultă notița dedicată:
> Pentru formula matricei de covarianță și vectorii proprii, vezi [[Analiza PCA si Selectie Subpurtatoare]].

---

## 🎹 8. Transformata Fourier și STFT: Partitura Muzicală a Căderii

* **Analogia Acordului de Pian:**
  Dacă un pianist apasă cu 5 degete simultan pe clapele unui pian, urechea ta aude un singur sunet bogat (un acord). Dacă ești un ascultător obișnuit, nu poți spune exact ce note individuale au fost cântate.
* **Ce face Transformata Fourier (FFT)?**
  Transformata Fourier este "urechea absolută" a matematicii. Ea ascultă acordul combinat și îți spune instantaneu: *"Aici ai nota Do de 261 Hz, nota Mi de 329 Hz și nota Sol de 392 Hz"*. Descompune orice semnal haotic într-o sumă de frecvențe pure (sinusoide).

### De ce avem nevoie de STFT (*Short-Time Fourier Transform*)?
FFT clasică are o problemă majoră: îți spune **ce note** s-au cântat, dar nu știe **când** s-au cântat! Într-un cântec de 3 minute, e o diferență uriașă dacă nota Do s-a auzit la început sau la sfârșit.

Aici intervine **STFT**:
1. Împărțim timpul în ferestre mici (de exemplu, feliuțe de câte 0.5 secunde).
2. Aplicăm Transformata Fourier pe fiecare feliuță în parte.
3. Rezultatul este o **Spectrogramă (o partitură muzicală colorată)**:
   * Axa orizontală = Timpul (secunde).
   * Axa verticală = Frecvența Doppler (Hz - viteza mișcării corpului).
   * Culoarea = Cât de puternică este mișcarea (galben/roșu = puternic, albastru = liniște).

```
Frecvență Doppler (Hz)
     ▲
  50 ┤                ████  <── CĂDERE: explozie de frecvențe înalte (>35 Hz)!
  35 ┤               ██████
  20 ┤    █████     ████████
   5 ┤   ███████   ██████████   <── MERS NORMAL: frecvențe joase (5-15 Hz)
   0 ┼───┴─────────┴─────────┴──► Timp (s)
       [Mers agale] [Impact la sol]
```

Când un om merge agale prin cameră, spectrograma arată doar note joase ($5 - 15\text{ Hz}$). Când omul se prăbușește, corpul accelerează vertiginos spre podea, generând un efect Doppler masiv ce depășește **$35\text{ Hz}$** — semnătura inconfundabilă a impactului!

> [!tip] Aprofundare
> Vezi analiza detaliată a spectrogramei în [[Spectrograma Micro-Doppler]].

---

## 🧭 Tabel Recapitulativ: Concepte pe Scurt

| Concept | Analogia din Viața Reală | Rolul în Licență |
| :--- | :--- | :--- |
| **DSP** | Bucătăria de restaurant care curăță ingredientele | Transformă pachetele brute de octeți în detecție de cădere |
| **Numere Complexe ($I, Q$)** | Ceasul cu o limbă (Lungime = Putere, Unghi = Fază) | Captează atât atenuarea cât și întârzierea undei Wi-Fi |
| **Zgomot AWGN** | Puricii și fâșâitul unui televizor deconectat | Zgomotul termic de fond al electronicii receptorului |
| **Spike LNA** | Smucitura violentă la schimbarea vitezei cu ambreiajul | Salt fals de un eșantion generat de amplificatorul intern |
| **Filtrul Hampel & MAD** | Arbitrul cu bun simț la ședința de bloc | Șterge spike-urile LNA și le înlocuiește cu mediana locală |
| **Filtrul Butterworth** | Sita fină de făină a bunicii | Oprește pereții imobili (0 Hz) și zgomotul înalt (>12 Hz) |
| **Filtrare Fază Zero** | Trenul punctual fără întârzieri temporale | Asigură că timestamp-ul impactului nu este decalat în timp |
| **PCA (PC1)** | Găsirea unghiului perfect al lanternei pentru umbră | Comprimă 52 de subpurtătoare într-un singur semnal cu SNR maxim |
| **STFT (Doppler)** | Partitura muzicală care arată notele în timp | Măsoară viteza corpului și trădează prăbușirea (>35 Hz) |

---

*Navighează mai departe:*
* [[04 - Dictionar Algoritmi si Software]] — Cum ia sistemul decizii logice pe baza acestor semnale.
* [[05 - Ghidul Folderelor si Fisierelor]] — Harta completă a fișierelor din calculator.
* [[00 - Start Aici]] — Pagina principală a proiectului.
