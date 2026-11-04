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
