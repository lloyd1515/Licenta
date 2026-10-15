# Deep Interview Spec: Triangulare device-uri BT/BLE din capturi pe 4 colțuri de sală

## Metadata
- Interview ID: ble-triangulation-20260617
- Rounds: 7
- Final Ambiguity Score: ~19%
- Type: brownfield
- Generated: 2026-07-15
- Threshold: 0.2
- Threshold Source: default
- Initial Context Summarized: no
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.85 | 35% | 0.2975 |
| Constraint Clarity | 0.75 | 25% | 0.1875 |
| Success Criteria | 0.85 | 25% | 0.2125 |
| Context Clarity | 0.75 | 15% | 0.1125 |
| **Total Clarity** | | | **0.81** |
| **Ambiguity** | | | **0.19** |

## Topology
| Component | Status | Description | Coverage / Deferral Note |
|-----------|--------|-------------|---------------------------|
| Extragere & matching date | active | Parsare pcap-uri BT clasic + BLE, filtrare strictă pe fereastra orară a fiecărui colț (ignoră restul înregistrărilor) | Confirmat de user explicit — filtrare pe oră e obligatorie |
| Geometria sălii | active | Sală standard de examen, dimensiuni configurabile prin popup (nu hardcodate) | User nu are măsurători exacte — folosim valori implicite tipice + input configurabil |
| Model matematic de poziționare | active | Reutilizează `estimate_distance()` existent (Log-Distance Path Loss) per colț, combină cele 4 distanțe via centroid ponderat pentru (x,y) | Recomandare AI acceptată de user: centroid ponderat ca MVP; least-squares/Levenberg-Marquardt = extensie viitoare, nu cerință curentă |
| Identitate device peste ferestre | active | Popup oferă 2 moduri selectabile: (a) matching cross-fereastră pe nume/UUID/tipar advertising, (b) analiză per-fereastră independentă (fără unificare identitate) | Confirmat: ambele moduri trebuie implementate ca opțiuni, nu doar unul |
| Interfață de configurare (popup) | active | Formular pentru parametrii sălii + selectarea modului de matching identitate | Tehnologia lăsată la latitudinea implementării — alegere: cea mai simplă potrivire cu stack-ul Python existent (probabil ipywidgets/tkinter, decis la faza de plan) |
| Output/vizualizare | active | Tabel (device, poziție estimată, încredere) + hartă vizuală 2D a sălii cu pozițiile marcate | Confirmat explicit: ambele formate, nu doar unul |

## Goal
Construirea unui instrument (script/notebook Python, extinzând `ble_utils.py`/`export_analysis.py`) care, pornind de la capturile pcap existente (BT clasic + BLE, canalele 37/38/39, din 2026-06-17) și programul de rotație pe 4 colțuri din `LicentaVault/My Notes/Logs.md`, estimează poziția aproximativă (x,y) a device-urilor detectate în sală, afișând rezultatul atât tabelar cât și vizual pe o hartă 2D a sălii.

## Constraints
- Se folosesc **doar** înregistrările din fereastra orară asociată fiecărui colț (ex: pentru colțul stânga-sus, doar pachetele între 8:50–9:10); restul se ignoră.
- Datele acoperă atât **BT clasic (BR/EDR)** cât și **BLE** — extragerea trebuie să gestioneze ambele formate de captură.
- Nu există coordonate fizice exacte ale sălii — se folosește o estimare/parametru configurabil (sală standard de examen), nu măsurători certificate.
- Ferestrele de captură **nu sunt simultane** (sunt secvențiale, cu suprapuneri de 5 minute) — algoritmul trebuie să trateze această limitare explicit, nu să pretindă simultaneitate perfectă.
- Reutilizează modelul existent `estimate_distance(rssi, tx_power=-59, n=3.0)` din `ble_utils.py` ca bază pentru distanța 1D per colț.

## Non-Goals
- Nu se implementează least-squares/Levenberg-Marquardt în această iterație (posibilă extensie viitoare).
- Nu se pretinde precizie de coordonate GPS/topografice — rezultatul e o estimare calitativă/aproximativă, nu o măsurătoare certificată.
- Nu se colectează date noi de captură — se lucrează exclusiv cu pcap-urile deja existente din 2026-06-17.

## Acceptance Criteria
- [ ] Scriptul filtrează pachetele din fiecare fișier pcap strict pe fereastra orară a colțului corespunzător.
- [ ] Scriptul procesează atât capturile BT clasic cât și cele BLE.
- [ ] Popup-ul de configurare permite introducerea/ajustarea dimensiunilor sălii.
- [ ] Popup-ul de configurare permite alegerea între modul "matching cross-fereastră" și modul "per-fereastră independent".
- [ ] Pentru fiecare device identificat (per criteriul de identitate ales), se calculează o poziție estimată (x,y) via centroid ponderat pe baza distanțelor derivate din `estimate_distance()` la cele 4 colțuri.
- [ ] Rezultatul e disponibil atât ca tabel (device, poziție estimată, nivel de încredere) cât și ca hartă vizuală 2D a sălii cu pozițiile marcate.
- [ ] Codul reutilizează `estimate_distance()` din `ble_utils.py` fără duplicare a logicii de conversie RSSI→distanță.

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| Cele 4 colțuri sunt puncte fixe simultane (ca în BluePIL) | Contrazis de `Logs.md`: e o rotație secvențială a unui singur Ubertooth | Confirmat de user: sunt ferestre orare secvențiale, nu simultane — se filtrează strict pe oră |
| Identitatea device-ului rămâne stabilă între ferestre (35 min total) | BLE randomizează MAC-ul la ~15 min — un device poate avea 2-3 adrese diferite pe parcursul capturii | User a ales să ofere ambele strategii ca opțiuni configurabile: matching cross-fereastră vs analiză per-fereastră |
| Există coordonate fizice exacte ale sălii | Nu există măsurători — doar etichete relative de colț | Parametru configurabil prin popup, cu valori implicite pentru sală standard de examen |
| Least-squares (Levenberg-Marquardt) e necesar pentru precizie | Date deja zgomotoase (non-simultane, geometrie aproximativă) — precizia suplimentară nu se justifică | Centroid ponderat ales ca MVP; least-squares rămâne non-goal pentru această iterație |

## Technical Context
- `ble_utils.py:68-77` — `estimate_distance(rssi, tx_power=-59, n=3.0)`, model Log-Distance Path Loss existent, de reutilizat ca-atare.
- `export_analysis.py:66` — folosește deja `estimate_distance()` pentru grafice, poate servi ca punct de plecare pentru integrare.
- `verify_cdf.py` — analiză CDF RSSI existentă, cutoff -85dBm (context, nu de reutilizat direct).
- Date sursă: `ubertooth-standalone/data/captures/` — `btle_ch{37,38,39}_YYYYMMDD_HHMMSS.pcap` (linktype 256, BLE cu PHDR/RSSI) + `rx_YYYYMMDD_HHMMSS.pcap` (linktype 255, fără PHDR — necesită investigare suplimentară pentru extragere RSSI/format BT clasic la faza de plan).
- `LicentaVault/My Notes/Logs.md` — sursa programului de rotație pe cele 4 colțuri (orele exacte).
- `LicentaVault/My Notes/Scan Session - 2026-06-17.md` — raport RSSI per MAC/LAP deja existent, posibil reutilizabil ca sursă de date procesate.
- Paper de referință: `LicentaVault/AI research/Papers/BluePIL a Bluetooth-based PassIve Localization Method.md` — model teoretic de trilaterare cu 4 noduri (folosit ca inspirație, nu ca implementare directă, dat fiind non-goal-ul least-squares).

## Ontology (Key Entities)
| Entity | Type | Fields | Relationships |
|--------|------|--------|----------------|
| Device (BT/BLE) | core domain | MAC/LAP address, tip (clasic/BLE), nume advertising, UUID-uri servicii | Detectat de la 1-4 Colțuri de captură; poate avea identitate ambiguă între ferestre (BLE random MAC) |
| Colț captură | core domain | etichetă (stg-sus/stg-jos/dr-jos/dr-sus), fereastră orară, poziție (x,y) configurabilă | Parte din Sală; sursă pentru un fișier pcap |
| Fereastră temporală | supporting | oră start, oră stop (20 min, suprapunere 5 min) | Asociată unui Colț captură; filtrează pachetele relevante |
| Sală | core domain | dimensiuni (lungime x lățime), formă | Conține cele 4 Colțuri captură; parametri configurabili prin popup |
| Poziție estimată | core domain | (x,y), nivel de încredere | Rezultatul calculului per Device, derivat din distanțele la cele 4 Colțuri |

## Ontology Convergence
| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|--------------|-----|---------|--------|------------------|
| 1 | 4 | 4 | - | - | N/A |
| 3 | 5 | 1 (Interfață configurare, nu e entitate ci componentă) | 0 | 4 | 100% |
| 5 | 5 | 0 | 0 | 5 | 100% |
| 7 | 5 | 0 | 0 | 5 | 100% |

## Interview Transcript
<details>
<summary>Full Q&A (7 rounds + Round 0 topologie)</summary>

### Round 0 (Topologie)
**Q:** Confirmare topologie 5 componente (extragere/matching, geometrie sală, model matematic, identitate device, output)
**A:** Confirmat, cu 2 amendamente: pozițiile colțurilor nu sunt coordonate fixe cunoscute; există date atât BT clasic cât și BLE.

### Round 1
**Q:** Ai coordonatele fizice ale celor 4 colțuri / dimensiunile sălii în metri?
**A:** Pot estima aproximativ.
**Ambiguitate:** 66%

### Round 2
**Q:** Dă-mi estimarea aproximativă a sălii (dimensiuni, formă, referință colțuri).
**A:** E o sală standard de examen, dar vreau ca parametrii să fie configurabili dintr-un popup box.
**Ambiguitate:** ~55% (componentă nouă adăugată: Interfață de configurare)

### Round 3
**Q:** Unde/cum rulează acest popup de configurare — ce platformă/tehnologie?
**A:** Nu contează tehnologia, decide tu.
**Ambiguitate:** ~48%

### Round 4 (notat ca Round 3 completă/tranziție)
(scorare intermediară după decizia de tehnologie delegată)

### Round 5
**Q:** Cum tratezi rotația adreselor MAC BLE între ferestre — ce înseamnă "același device" între colțuri?
**A:** Vreau ca popup-ul să ofere ambele opțiuni: matching cross-fereastră și analiză per-fereastră independentă.
**Ambiguitate:** ~38%

### Round 6
**Q:** Care e forma minimă viabilă a output-ului final — hartă, tabel, sau ambele?
**A:** Ambele — tabel + hartă vizuală.
**Ambiguitate:** ~31%

### Round 7
**Q:** Ce algoritm matematic pentru combinarea celor 4 distanțe într-o poziție (x,y) — least-squares sau centroid ponderat?
**A:** Nu știu, recomandă tu.
**Recomandare AI (acceptată):** centroid ponderat ca MVP, least-squares ca non-goal/extensie viitoare.
**Ambiguitate:** ~19% — sub pragul de 20%.

</details>
