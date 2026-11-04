# Lungimea de undă

## Ce este

Lungimea de undă este distanța dintre două vârfuri succesive ale undei radio. Pentru Wi-Fi pe 2.437 GHz, această distanță este aproximativ 12.3 cm.

## Unde o folosește proiectul

- [simulator.py:120](src/csi/simulator.py#L120) transformă viteza persoanei în frecvență Doppler.
- [charts.py:87](src/csi/gui/charts.py#L87) face calculul invers: din frecvența Doppler obține viteza.
- [simulator.py:111](src/csi/simulator.py#L111) și [room_map.py:134-137](src/csi/gui/room_map.py#L134-L137) calculează zonele Fresnel dintre noduri.

## Exemplu

Doppler 35 Hz × 0.123 m / 2 ≈ 2.15 m/s. Persoana se mișcă aproximativ cu această viteză.


# Efectul Doppler

## Ce este

Efectul Doppler este o schimbare de frecvență. Schimbarea apare când sursa sau obiectul care reflectă unda se mișcă.

Gândește-te la o ambulanță. Când vine spre tine, sirena are un sunet mai înalt. Când pleacă, sunetul devine mai jos.

## În proiect

Unda Wi-Fi se reflectă pe o persoană. Când persoana se mișcă, unda reflectată are o frecvență puțin diferită. Această diferență este frecvența Doppler, `doppler_hz`.

O persoană care stă pe loc dă 0 Hz. O persoană care se mișcă repede dă o valoare mare.

## Calculul

```
viteza = doppler_hz × lungime_de_undă / 2
       = 35 Hz × 0.123 m / 2
       ≈ 2.15 m/s
```

- **35 Hz**: semnalul reflectat se schimbă de 35 de ori pe secundă.
- **× 0.123 m**: la fiecare schimbare, drumul undei se schimbă cu o lungime de undă.
- **/ 2**: când persoana se mișcă 1 cm, drumul undei se schimbă cu aproximativ 2 cm. Unda merge la persoană și apoi înapoi. Astfel, drumul se schimbă de două ori.

Acest calcul este în [charts.py:87](src/csi/gui/charts.py#L87). Factorul 2 este o aproximare. Valoarea exactă depinde de poziția persoanei față de noduri.


# De ce 2.437 GHz

## Motivul

Valoarea 2.437 GHz este frecvența canalului 6 din banda Wi-Fi de 2.4 GHz. Placa ESP32 funcționează numai în banda de 2.4 GHz. Canalul 6 este în mijlocul benzii, iar multe routere îl folosesc implicit.

## Ce trebuie să știi

Codul nu impune canalul 6. Placa se conectează la router ([main.c:151-157](src/firmware/esp32_csi_node/main/main.c#L151-L157)), iar routerul alege canalul. Așa că valoarea din `room.py` este o presupunere. Ea trebuie să fie egală cu canalul real al routerului.

## Ce se întâmplă cu altă frecvență

Pe canalul 1 (2.412 GHz), lungimea de undă devine 12.4 cm, nu 12.3 cm. Diferența este mică. Dar faza semnalului depinde de lungimea de undă, deci o valoare greșită dă calcule puțin greșite.

# Subpurtătoarea

O subpurtătoare este una din cele 52 de frecvențe mici din canalul Wi-Fi. Fiecare transmite o parte din date.

# Cele 52 de frecvențe

Wi-Fi împarte canalul de 20 MHz în 52 de unde separate, la 312.5 kHz distanță. CSI măsoară fiecare undă.

# Unde sau frecvențe

Fiecare subpurtătoare este o undă radio, iar fiecare undă are frecvența ei proprie.

Frecvența este numărul care identifică unda. Exemplu: subpurtătoarea +1 este unda cu frecvența de 2.437 GHz + 312.5 kHz.

# Indicii de la −26 la +26

## Semnul indicelui
Indicele arată poziția undei față de centrul canalului, adică 2.437 GHz. Un indice negativ înseamnă o undă sub centru. Un indice pozitiv înseamnă o undă peste centru.

## De ce lipsește indicele 0
Indicele 0 este exact frecvența centrală. Receptorul are acolo un zgomot propriu, care vine din circuitul lui intern. Standardul Wi-Fi nu trimite date pe această frecvență.

## De ce limita este 26
Canalul are 64 de poziții, de la −32 la +31. Standardul lasă goale pozițiile de la margini. Astfel, canalul nu deranjează canalele Wi-Fi vecine.

Rămân 52 de unde utile: 26 sub centru și 26 peste centru.

## Detectorul de cadere vs Doppler 

## Rolurile
- Detectorul decide alarma. El folosește pantele semnalului de mișcare și starea de nemișcare de după impact.
- Doppler arată viteza corpului pe grafic. Nu influențează alarma.

## Legătura
Ambele pornesc din aceleași date CSI. Ele sunt însă două calcule separate, cu două scopuri diferite.

## Praguri ale detectorului de cădere
Întrebare: ce praguri are detectorul de cădere?

Fișier: `src/csi/fall_detector.py`, liniile 23-29.
- `SLOPE_ACTIVE = 0.05`: pragul pentru mișcare.
- `IMPACT_SLOPE = 17.5`: pragul pentru impact.
- `MIN_LINKS_AT_IMPACT = 2`: numărul minim de legături la impact.
- `STILL_MAX_VARIANCE = 0.20`: varianța maximă pentru starea de nemișcare.
- `STILL_WINDOW_S = 2.5`: fereastra de verificare a nemișcării, în secunde.

## Pante vs Doppler
Întrebare: care este diferența dintre pantele semnalului de mișcare și Doppler?

- Semnalul de mișcare vine din amplitudinea CSI după filtrul trece-bandă. Panta este viteza de schimbare a acestui semnal în timp. Detectorul folosește panta.
- Doppler este o frecvență în Hz. Formula este `viteză = Doppler × lungime de undă / 2`. Graficul arată Doppler.

Linia roșie "Prag Cădere (35 Hz)" este doar o referință vizuală. Eticheta poate induce în eroare.

## Funcția extra_path_m
Întrebări: ce înseamnă "adună segmentele" și "scade drumul albastru"? Ce face `np.linalg.norm`? Ce este un vector?

- Vector: o listă de numere. `[3, 4]` are lungimea 5.
- `np.linalg.norm` calculează lungimea unui vector. Pentru `point - tx`, rezultatul este distanța dintre punct și emițător.
- Funcția adună TX→persoană și persoană→RX. Apoi scade drumul direct TX→RX.
- Rezultatul este drumul în plus, în metri.
- Exemplu: direct 6 m, ocol 4 m + 4 m = 8 m. Drumul în plus este 2 m.

## Ce face simulatorul cu drumul în plus
Întrebare: ce este zona Fresnel? Verifică în cod.

Codul nu folosește o zonă Fresnel cu limita λ/2. Codul folosește `simulator.py:111-116`:
- `L = 1.5 · 0.5 · √(λ · d)`. Pentru `d = 4 m`, `L = 0.53 m`.
- `amplitudine = 0.35 · e^(−în plus / L)`.
- Amplitudinea scade exponențial când drumul în plus crește.
- Persoană căzută: amplitudine fixă `FALLEN_REFLECTION = 0.85`.

| Drum în plus | Amplitudine reflexie |
|---|---|
| 0 m | 0.35 |
| 0.53 m | 0.13 |
| 1.05 m | 0.05 |

`0.35` este `BODY_REFLECTION`. Nu are legătură cu `DOPPLER_REFERENCE_HZ = 35.0`.

## Variabilele din desenul "Drum în plus"
| Variabilă | Ce este |
|---|---|
| TX, RX | placa care emite, placa care primește |
| `d` | distanța directă TX → RX: `√(4² + 0²) = 4 m` |
| persoana | punctul `(x, y)` tras prin cameră |
| `a`, `b` | TX → persoană, persoană → RX |
| în plus | `a + b − d` |
| `L` | scara de scădere: `1.5 · 0.5 · √(λ · d)` |
| amplitudine | `0.35 · e^(−în plus / L)` |
| `csi` | `static + dynamic` (`simulator.py:124`) |

Idei importante:
- `d` nu se schimbă când muți persoana. Nodurile sunt fixe.
- Pe linia directă, `a + b = d`, deci "în plus" este 0 și amplitudinea este maximă: `0.35`.
- "În plus" măsoară depărtarea de linia directă. Nu măsoară apropierea de un nod.
- Persoana este în afara elipsei albastre când `în plus > L`.
- Amplitudine mică (`0.05`) înseamnă că simulatorul vede greu mișcarea persoanei.


# Sesiunea din 4 noiembrie 2026: main.c pe placă

Întrebările vin din două conversații. Conversația originală acoperă punctul 3, placa reală și comenzile. Conversația ramificată acoperă punctul 4.

## Atributul packed (punctul 3)
Întrebare: ce face `__attribute__((packed))`? Ce octeți interzice?

- Compilatorul adaugă uneori octeți de umplutură, pentru alinierea câmpurilor.
- În `csi_packet_t`, câmpurile sunt deja aliniate. Umplutura apare doar la sfârșit: 2 octeți.
- Cu `packed`, mărimea este 138. Fără `packed`, mărimea este 140. PC-ul așteaptă exact 138.
- `_Static_assert` verifică mărimea la compilare.
- Quiz: unde apar cei 2 octeți fără `packed`? Răspuns: la sfârșit, după `csi_iq`.

## Ce este `__attribute__`
- `__attribute__` este o extensie GCC. Ea adaugă o instrucțiune specială la o definiție.
- Parantezele duble sunt sintaxa GCC. `packed` este numele atributului.

## Little-endian
- `magic = 0xA55A` apare în memorie ca `5A A5`. Octetul mic vine primul.
- `timestamp_us = 0x01020304` apare ca `04 03 02 01`.
- Demo: în `docs/learning/exercitii`, rulați `sh run_packed_demo.sh`.

## Pot rula main.c direct pe PC?
- Nu. `main.c` are nevoie de ESP-IDF și de procesorul ESP32 (Xtensa).
- Harness-ul din `docs/learning/ilustrat/debug-harness` compilează `main.c` nemodificat, cu biblioteci false.
- Radioul, rețeaua și FreeRTOS sunt simulate. GDB poate opri codul pe fiecare linie.

## Depanare live pe placă
Întrebare: dacă conectez placa, pot vedea live ce se întâmplă?

- Placa este un ESP32 clasic, cu punte USB CP210x. Ea nu are JTAG prin USB.
- Fără JTAG, nu puteți pune puncte de oprire pe placă.
- Variante: `ESP_LOGI` în cod, harness pe PC, adaptor ESP-Prog (JTAG extern), GDBStub (netestat).
- CAUTION: Nu opriți placa mult timp într-un punct de oprire. Oprirea blochează radioul și conexiunea cu AP.

## ESP-IDF
- ESP-IDF este kitul oficial Espressif pentru ESP32.
- El conține FreeRTOS, driverul Wi-Fi, lwIP, biblioteca de log, NVS, compilatorul și `idf.py`.
- `gcc` de pe PC nu compilează pentru ESP32. ESP-IDF aduce compilatorul potrivit.
- Locuri: `~/esp/esp-idf` (kitul v5.1.7), `~/.espressif` (unelte), `~/esp/csi-node` (fișiere compilate).

## idf.py
- Unde este? În `~/esp/esp-idf/tools/idf.py`, nu în `src`. `export.sh` îl pune în `PATH`.
- Ce face? Configurează, compilează, scrie firmware-ul pe placă și arată monitorul serial.
- `idf.py` nu face singur munca. El pornește `cmake`, `ninja` și `esptool`.
- De ce Python? `esptool` și uneltele ESP-IDF sunt scrise în Python. Python rulează pe Linux, Windows și macOS.

## Rețeaua Wi-Fi a plăcii
- ESP32 funcționează doar pe 2,4 GHz. O rețea doar pe 5 GHz nu este vizibilă pentru placă.
- PC-ul și placa trebuie să fie în aceeași rețea. Broadcast-ul `255.255.255.255` nu trece între rețele.
- Parola stă în `~/esp/csi-node/wifi.defaults`, în afara repository-ului.

## Cele trei comenzi
Pregătire: `PY=~/.espressif/python_env/idf5.1_py3.14_env/bin/python`

| Comandă | Ce face |
|---|---|
| `python3 asculta.py 5` (în `docs/learning/exercitii`) | Ascultă UDP pe portul 5005. Decodează antetul și primii 8 octeți CSI. |
| `$PY src/firmware/esp32_csi_node/tools/start_log.py 15` | Jurnalul plăcii, curat și colorat, 15 secunde. |
| `$PY src/firmware/esp32_csi_node/tools/start_log_raw.py 15` | Tot jurnalul, exact cum vine. |
| `WIFI_SSID=<rețea> WIFI_PASS=<parolă> bash src/firmware/esp32_csi_node/tools/flash.sh` | Compilează și scrie pe placă. Rezultat scurt, cu bare de progres. |
| `WIFI_SSID=<rețea> WIFI_PASS=<parolă> bash src/firmware/esp32_csi_node/tools/flash_raw.sh` | La fel, dar cu tot jurnalul `idf.py`. |

Bucla de depanare: editați `main.c`, rulați `flash.sh`, apoi citiți jurnalul sau pachetele.

CAUTION: Nu scrieți un `ESP_LOGI` la fiecare pachet. Folosiți `if (packet.seq % 20 == 0)`. Altfel jurnalul încetinește `on_csi`.

## seq
- `seq` este numărul de ordine al pachetului. `on_csi` îl crește cu 1 la fiecare pachet.
- Golurile arată pachete pierdute, în coadă sau în rețea.
- `seq` are 16 biți. După 65 535, valoarea revine la 0.

## Șablonul `<HBbIH`
| Literă | Tip C | Octeți | Câmp |
|---|---|---|---|
| `<` | — | 0 | Little-endian, fără umplutură |
| `H` | `uint16_t` | 2 | `magic` |
| `B` | `uint8_t` | 1 | `node_id` |
| `b` | `int8_t` | 1 | `rssi_dbm` |
| `I` | `uint32_t` | 4 | `timestamp_us` |
| `H` | `uint16_t` | 2 | `seq` |

Literă mare: fără semn. Literă mică: cu semn. Total: 10 octeți de antet.

## Vectorul csi_iq
- 64 de perechi (Q, I), câte una pentru fiecare subpurtătoare. Fiecare număr este un `int8_t`.
- Exemplu: `0xFC` = 252. Octeții de la 128 la 255 sunt negativi: 252 − 256 = −4.
- Amplitudinea este `sqrt(I² + Q²)`. Faza este `atan2(Q, I)`.
- `asculta.py` afișează doar primii 8 octeți, adică 4 subpurtătoare. Restul sunt în `data[18:138]`.
- `packets.py` păstrează 52 de subpurtătoare utile: `slice(6, 32)` și `slice(33, 59)`.

## Unde este decodarea?
- `main.c` nu decodează. `main.c` codează: `on_csi` scrie câmpurile, `sendto` trimite 138 de octeți.
- PC-ul decodează: `asculta.py:20` și `src/csi/packets.py`, cu `<HBbIH`.
- CAUTION: Dacă schimbați `csi_packet_t`, schimbați și șablonul Python.

## copy_len
- `copy_len` este cel mult 128. `csi_iq` are loc doar pentru 128 de octeți.
- Fără limită, `memcpy` scrie peste alte date.

## Quiz: 5 din 5
1. `sizeof(csi_packet_t)` cu `packed`: 138.
2. Primul octet în memorie pentru `0xA55A`: `5A`.
3. `0xF0` ca `int8_t`: −16 (240 − 256).
4. Decodarea cu `<HBbIH`: în `asculta.py`, pe PC.
5. Un gol în `seq`: unul sau mai multe pachete pierdute.

## Jurnalul plăcii
- Linia `I (4952) CSI_NODE: ...` are nivelul (`I`, `W`, `E`), milisecundele de la pornire, `TAG` și mesajul.
- Primele linii ROM apar stricate, cu litere lipsă. Acest lucru este normal la pornire.
- Prima conectare eșuează adesea. A doua reușește, apoi placa primește IP.
- `log.py` afișează jurnalul serial, nu pachetele CSI. Pachetele merg prin UDP.

## 115200
- 115200 este viteza consolei seriale, în biți pe secundă (baud).
- Un octet folosește 10 biți: start, 8 biți de date, stop. Rezultă 11 520 octeți pe secundă.
- 11 520 B/s = 11,5 KB/s = 0,0115 MB/s = 0,1152 Mb/s.
- `MB` (B mare) înseamnă megaoctet. `Mb` (b mic) înseamnă megabit. 1 octet = 8 biți.
- Corecție: vechiul firmware trimitea CSI pe UART la 921 600 baud, nu la 115 200. Aceasta înseamnă aproximativ 667 de pachete pe secundă. Afirmația „83 de pachete pe secundă, deci UDP” este greșită.

## flash_raw.sh, pe scurt
- `set -e` oprește scriptul la prima eroare.
- `: "${WIFI_SSID:?...}"` oprește scriptul dacă variabila lipsește.
- `PORT="${PORT:-/dev/ttyUSB0}"` dă o valoare implicită.
- `. export.sh` pune `idf.py` și compilatorul în `PATH`.
- `-B` și `-DSDKCONFIG` țin fișierele generate în afara repository-ului.
- `-DSDKCONFIG_DEFAULTS` citește setările proiectului, apoi rețeaua și parola.
- `build flash` compilează, apoi scrie pe placă.

## Octeții ficși ai cadrului probe (punctul 4)
Întrebare: ce rol au `PROBE_FRAME_CONTROL`, `BROADCAST_MAC` și `SOURCE_MAC`?

Analogia: placa strigă des „E cineva aici?”. Celelalte plăci aud strigătul. Pereții și oamenii schimbă puțin sunetul pe drum. Această schimbare este CSI.

Radioul nu trimite strigătul fără plic. Codul scrie plicul octet cu octet:

| Octeții | Valoarea | Rolul |
|---|---|---|
| 0 | `0x40` | Eticheta „probe request”: o întrebare despre rețelele din jur. |
| 1 | `0x00` | Opt steaguri nebifate: fără criptare, fără repetare, fără fragmente. |
| 2-3 | `0x00 0x00` | Durata 0: canalul nu rămâne rezervat. Nimeni nu confirmă primirea. |
| 4-9 | `FF:FF:FF:FF:FF:FF` | Destinația „pentru toată lumea”, ca un anunț la difuzor. |
| 10-15 | `24:0A:C4:00:00:03` | Semnătura „sunt nodul 3”. Ultimul octet este `NODE_ID`. |
| 16-21 | `FF:FF:FF:FF:FF:FF` | BSSID „orice rețea”. |
| 22-63 | zero | Plic fără conținut. |

Lucrul important: CSI nu depinde de textul de pe plic. CSI vine din preambul, semnalul cunoscut de la începutul cadrului.

Analogia pentru preambul: tehnicianul de sunet spune mereu „unu, doi, trei”. El știe cuvintele, deci aude exact ce schimbă sala.

Quiz:
1. De ce Address 1 este `FF:FF:FF:FF:FF:FF`? Răspuns: toate plăcile aud cadrul și nicio placă nu trimite ACK.
2. Se schimbă CSI dacă schimbați zerourile din corp? Răspuns: nu. CSI vine din preambul, nu din plic.

## Unde am rămas
Următorul pas este punctul 5: variabilele comune `csi_queue`, `wifi_events` și `next_seq`.
