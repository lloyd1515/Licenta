---
title: Dicționar Hardware și Rețea
tags:
  - licenta
  - hardware
  - retea
  - esp32
  - ofdm
  - uart
aliases:
  - Dictionar Hardware
  - Hardware si Retea
  - Ghid Hardware
---

# 🔌 Dicționar Hardware și Rețea: De la Cipuri Ieftine la Pachete de Mare Viteză

> [!info] Despre acest dicționar
> Aici găsești explicația intuitivă a tuturor pieselor fizice și a protocoalelor de comunicare din proiect. Fără jargon academic steril – fiecare concept tehnic este tradus printr-o analogie din lumea reală.

---

## 🧠 1. ESP32: „Creierul” de 20 de Lei

### Ce este?
Un **ESP32** este un microcontroler – adică un computer miniatural construit pe o singură plăcuță electronică de dimensiunea unei cutii de chibrituri. Este proiectat de compania *Espressif Systems*.

```
       +-------------------------------+
       |  [ Antenă PCB Wi-Fi / BLE ]   |
       |  +-------------------------+  |
       |  |   Xtensa Dual-Core      |  |
       |  |   Procesor 240 MHz      |  |
       |  +-------------------------+  |
       |  [ Micro-USB / UART Port ]    |
       +-------------------------------+
```

### De ce este uimitor pentru acest proiect?
* **Cost infim:** Costă între 15 și 25 de lei (cât o cafea și un corn). Sistemele comerciale radar de laborator costă mii de euro. Noi obținem aceleași rezultate cu hardware accesibil oricui.
* **Are radio Wi-Fi integrat:** Include hardware complet pentru emisia și recepția undelor pe $2.4\text{ GHz}$.
* **Permite acces la CSI:** Espressif a lăsat în mod oficial o „ușiță deschisă” în codul lor (API-ul ESP-IDF), care permite extragerea valorilor brute de la nivelul fizic al undelor (stratul PHY).

În camera noastră de test ($5 \times 5\text{ metri}$) folosim o echipă de **3 plăcuțe ESP32**:
1. **Nodul 1 (TX - Transmițător):** Joacă rolul de „far călăuzitor” – emite neobosit impulsuri radio.
2. **Nodurile 2 și 3 (RX1, RX2 - Receptoare):** Joacă rolul de „antene de ascultare” – prind undele și raportează instant ecourile către PC.

Pentru detalii complete de firmware în cod C, vezi [[Noduri ESP32 Mesh]].

---

## 📡 2. Canalul 6 Wi-Fi ($2.437\text{ GHz}$) și Lungimea de Undă $\lambda = 12.3\text{ cm}$

### Ce înseamnă frecvența de $2.437\text{ GHz}$?
Înseamnă că unda electromagnetică trimisă de antenă urcă și coboară de **$2.437.000.000$ de ori într-o singură secundă**.

### De unde vine lungimea de undă de $12.3\text{ cm}$?
Undele radio călătoresc prin aer cu viteza luminii ($c \approx 300.000\text{ km/s}$ sau $3 \times 10^8\text{ m/s}$). Între viteză, frecvență ($f$) și lungimea unei singure oscilații ($\lambda$, litera grecească *lambda*) există formula de fizică de gimnaziu:

$$\lambda = \frac{c}{f} = \frac{3 \times 10^8\text{ m/s}}{2.437 \times 10^9\text{ s}^{-1}} \approx 0.123\text{ metri} = 12.3\text{ centimetri}$$

> [!tip] De ce contează că $\lambda$ are dimensiunea unei palme umane?
> În fizica propagării undelor există o regulă de aur: **o undă observă bine doar obiectele care au mărimi comparabile cu lungimea ei de undă!**
> * Dacă foloseam unde radio lungi (precum radioul clasic FM cu $\lambda = 3\text{ metri}$), unda ar fi trecut peste corpul omului fără să-l bage în seamă (omul este prea mic față de undă).
> * Dacă foloseam unde milimetrice ($\lambda = 3\text{ milimetri}$), unda s-ar fi oprit în prima foaie de hârtie, perdea sau tricou subțire.
> * La **$12.3\text{ cm}$**, unda Wi-Fi este la „dimensiunea de aur”: ignoră hainele subțiri, trece prin uși din lemn, dar **se lovește direct de toracele, capul și brațele omului**, oferind ecoul perfect pentru detecție!

---

## 🛣️ 3. OFDM și cele 52 de Subpurtătoare: Autostrada cu 52 de Benzi

Wi-Fi-ul modern nu trimite toate datele pe o singură frecvență groasă. El folosește o tehnologie numită **OFDM** (*Orthogonal Frequency Division Multiplexing*).

### Analogia autostrăzii
* **Canalul Wi-Fi clasic vechi:** O șosea cu o singură bandă. Dacă un tir mare vrea să treacă, blochează tot drumul.
* **OFDM (Wi-Fi 802.11n):** O **autostradă modernă cu 52 de benzi paralele**. Fiecare bandă transportă mașinuța ei cu date. Benzile sunt separate fin, la distanțe de doar $312.5\text{ kHz}$.

```
Canal 6 Wi-Fi Total (20 MHz lățime)
|-----------------------------------------------------------------------|
  Banda 1   Banda 2   Banda 3  ...  Banda 26  ...  Banda 51   Banda 52
   [Sub 1]   [Sub 2]   [Sub 3]       [Sub 26]       [Sub 51]   [Sub 52]
     ||        ||        ||             ||             ||         ||
```

### De ce este OFDM secretul magic al senzorului nostru?
Când un om se mișcă într-o cameră, ecourile ricoșează din pereți și se întâlnesc în mod diferit pe fiecare bandă:
* Pe **banda 10**, ecoul de pe perete și ecoul de pe om se pot nimeri în contratimp și semnalul scade la zero.
* Pe **banda 25**, aceleași ecouri se ajută reciproc și semnalul se dublează!

Astfel, la fiecare mișcare a corpului, primim o **„amprentă spectrală” unică pe 52 de frecvențe**. Dacă am fi avut o singură bandă, am fi fost orbi la aceste detalii fine.

Pentru modul în care reducem matematic aceste 52 de benzi la un singur semnal curat, vezi [[Analiza PCA si Selectie Subpurtatoare]].

---

## 🚰 4. UART și Baud Rate ($921600\text{ baud}$): Furtunul de Mare Presiune

### Ce este UART?
**UART** (*Universal Asynchronous Receiver-Transmitter*) este conexiunea pe fir care leagă plăcuța ESP32 de calculator prin cablul USB. Este linia de transport pe care ESP32 „varsă” datele citite din aer direct în programul Python de pe PC.

### Ce înseamnă Baud Rate?
Rata de transfer (Baud Rate) reprezintă numărul de biți (de $0$ și $1$) trimiși pe fir în fiecare secundă.

| Baud Rate comun | Viteză | Echivalent în viața reală | Ce s-ar întâmpla în proiectul nostru? |
| :--- | :--- | :--- | :--- |
| **9600 baud** | Foarte lent | O picătură de apă la fiecare secundă | Sistemul ar îngheța instant; datele se pierd |
| **115200 baud** | Standard hobby | Robinetul chiuvetei deschis normal | Buffer overflow (inundație de memorie) |
| **921600 baud** | Ultrarapid | **Furtun de pompieri cu apă sub presiune** | **Pachetele curg fără nicio întârziere (latență < 1 ms)** |

Am configurat cipurile noastre la **$921600\text{ baud}$**. Datorită acestei viteze mari, putem transmite fără gâtuire peste **100 de rapoarte CSI complete pe secundă** de la fiecare nod receptor!

---

## ✉️ 5. Cadrul Binar de 138 Octeți și Magic Header-ul `0xA55A`

Pentru ca datele să zboare cu viteză maximă de la ESP32 la PC, **nu folosim texte sau fișiere JSON**. 

> [!example] De ce textul este „leneș” și binarul este „eficient”?
> Dacă ai vrea să transmiți textul:  
> `{"nod": 1, "subpurtatoare": 45, "amplitudine": 12.8}`  
> Acest text ocupă peste **50 de caractere (50 de octeți)** doar pentru un număr!  
> În format binar pur, aceleași informații ocupă doar **2 sau 3 octeți**.

Noi împachetăm datele într-un **cadru binar ultra-compact de fix 138 de octeți**:

```
+--------------------------------------------------------------------------+
| Magic Header | Node ID | Timestamp | RSSI  |  52 Valori CSI (I & Q)      |
|    0xA55A    | (1 B)   |   (4 B)   | (1 B) |      (104 octeți)           |
|   (2 octeți) |         |           |       | (52 reale + 52 imaginare)   |
+--------------------------------------------------------------------------+
Total fix: 138 octeți per pachet
```

### De ce este nevoie de „Magic Header” `0xA55A`?
Cablul USB transmite un flux continuu, nesfârșit, de cifre binare: `01101001010110...`. Calculatorul nu știe automat unde se termină un pachet și unde începe următorul.

**`0xA55A` este parola secretă (sigiliul de ceară):**
* În notație hexazecimală, `0xA55A` corespunde celor doi octeți `165` și `90`.
* În biți, arată simetric și special: `10100101 01011010`.
* Când algoritmul din Python citește fluxul de date, scanează continuu până dă peste această secvență magică `0xA55A`. În acel moment spune: *„Aha! Aici începe o scrisoare nouă de 138 de octeți!”*, decupează cadrul și citește valorile corect.

Pentru specificația binară la nivel de bit, vezi [[Protocol Binar UART]].

---

## 📐 6. Topologia Triunghiulară (Mesh 3 Noduri într-o Cameră $5\times 5\text{ m}$)

De ce nu am folosit doar două noduri (un emițător și un receptor)?

```
        Nod 2 (RX1)
         [Colț Sus]
           /      \
          /        \
    Legătura 1    Legătura 2
        /            \
       /              \
Nod 1 (TX) --------- Nod 3 (RX2)
[Colț Stânga]  Legătura 3   [Colț Dreapta]
```

### Problema cu două noduri:
Dacă ai doar o linie dreaptă între două noduri ($TX \to RX$), semnalul îți spune doar că omul a intersectat acea linie undeva. Dar nu știi dacă este la stânga, la dreapta, mai sus sau mai jos. Ești limitat la o singură dimensiune (o linie).

### Soluția: Triangulația cu 3 noduri
Am plasat cele 3 noduri în formă de triunghi în camera de test ($5\text{m} \times 5\text{m}$):
* Obținem simultan **3 căi de comunicație distincte**:
  1. Drumul de la $TX$ la $RX1$.
  2. Drumul de la $TX$ la $RX2$.
  3. Drumul direct sau indirect între receptoare.
* Fiecare pereche trasează în spațiu un set de curbe invizibile (elipse Fresnel). 
* Acolo unde **ecourile din toate cele 3 legături se intersectează**, se află cu precizie centimetrice poziția omului $(X, Y)$ pe ecranul aplicației!

Pentru formula matematică a calculării poziției, vezi [[Localizare 2D Elipse Fresnel]].

---

## 🔗 Continuă explorarea

* Înapoi la ghidul de bază: [[00 - Ghid pentru Incepatori (De la Zero)]]
* Dicționarul de fizică a undelor: [[02 - Dictionar Fizica si Propagare Unde]]
* Dicționarul de matematică și DSP: [[03 - Dictionar Matematica si DSP]]
* Arhitectura software completă: [[01 - Arhitectura Sistem]]
