# Plan: Triangulare device-uri BT/BLE din capturi pe 4 colțuri de sală (RALPLAN-DR, short mode)

Status: **PENDING APPROVAL** (consens Planner → Architect → Critic finalizat, APPROVED)
Sursă: `.omc/specs/deep-interview-ble-triangulation.md`

## RALPLAN-DR Summary

### Principles (3-5)
1. **Nu pretinde precizie care nu există** — datele sunt non-simultane, geometria e aproximativă, identitatea BLE e ambiguă prin design (RPA). Output-ul trebuie să comunice incertitudinea (nivel de încredere), nu coordonate false-precise.
   - **(reformulat după review Fable):** non-simultaneitatea (ferestre la 15-35 min distanță) NU e doar un factor de "încredere redusă" — pentru un device care s-a mișcat între ferestre, poziția (x,y) rezultată e fizic **greșită**, nu doar imprecisă. Aceasta e o **limită de scop structurală**: triangularea are sens metodologic doar pentru device-uri presupuse staționare (beacon-uri, periferice fixe), nu pentru telefoane purtate de persoane care se deplasează. Spec-ul/output-ul trebuie să declare explicit această presupunere de staționaritate, nu să o ascundă în spatele unui scor de încredere numeric.
2. **Reutilizare, nu duplicare** — `estimate_distance()` din `ble_utils.py` rămâne sursa unică de adevăr pentru conversia RSSI→distanță; nu se reimplementează.
3. **Separare extractor / model / UI** — parsarea pcap (sursă nouă de date), modelul de poziționare (matematică pură) și interfața de configurare sunt module distincte, testabile independent (many-small-files, coding-style.md).
4. **Simplitate întâi** — centroid ponderat ca MVP; least-squares e non-goal explicit (evită supra-inginerie pe date deja zgomotoase).
5. **Filtrare temporală strictă** — corelarea colț↔fișier pcap se face prin suprapunerea timestamp-ului pachetului cu fereastra orară din `Logs.md`, nu prin numele fișierului (rotația ciclează pe canal, nu pe colț — confirmat din `scan_log.txt`).

### Decision Drivers (top 3)
1. **Corectitudine față de limitările fizice ale datelor** (non-simultaneitate, RPA, geometrie aproximativă) — orice abordare care ascunde aceste limitări e respinsă.
2. **Reutilizare a codului existent** (`ble_utils.py`) pentru a nu duplica logica RSSI→distanță deja testată.
3. **Livrabil util pentru teză** — output dual (tabel + hartă) cerut explicit de user, trebuie să fie prezentabil ca rezultat de cercetare, cu caveat-uri metodologice clare (așa cum fac și cele 2 paper-e din vault).

### Viable Options (extractor de date din pcap)

**Opțiunea A: Parser pcap manual (struct, ca în explorarea inițială)**
- Pro: fără dependențe noi, control total pe linktype 256 (`BLUETOOTH_LE_LL_WITH_PHDR`) și 255; deja am prototip funcțional (folosit la inspecția inițială a fișierelor).
- Contra: trebuie implementat manual decodarea payload-ului LE LL (adresă, RSSI, canal) — risc de bug-uri subtile în parsing.

**Opțiunea B: `scapy` cu dissector Bluetooth LE**
- Pro: bibliotecă matură, dissector BLE LL testat, reduce riscul de parsing greșit.
- Contra: dependență nouă (`scapy` nu e instalat — confirmat, `ModuleNotFoundError` la verificare anterioară); linktype 255 (rx_*.pcap, posibil BT clasic) ar putea să nu fie suportat corect de scapy pentru BR/EDR.

**Decizie revizuită (după review Architect):** Opțiunea C (sinteză) — **`scapy` pentru DLT 256** (dissector BLE LL testat, decodare corectă PDU/AdvA — critică pentru identitatea device-ului, pe care un parser manual ar putea-o corupe silențios), plus un **reader manual subțire doar pentru byte-ul RSSI din PHDR și pentru DLT 255** (pe care scapy nu-l disecă oricum). `scapy` e pură Python, fără dependențe de sistem — se adaugă ca dependență de dev, pinned.

**Descoperire critică (Architect, verificată pe date reale):** corelarea colț↔fișier NU poate fi presupusă din denumirea/volumul fișierelor. Verificând epocile pachetelor față de ferestrele din `Logs.md` (08:50-09:25 local, fișierele au timestamp local în nume, pcap-urile intern UTC+3=local):
- Majoritatea fișierelor BLE mari (DLT256: `..._074723`, `..._081341`) cad **în afara** ferestrelor (înainte de 8:50); `..._083208` se termină la 08:51:32, deci atinge doar ~1.5 min din fereastra stânga-sus (8:50-9:10) — nu e complet în afară, dar contribuie marginal.
- **Corectat după verificare Critic (pe epoci reale de pachet, nu pe nume fișier):** pentru **dreapta-jos (9:00-9:20)** există totuși suprapunere DLT256 utilă — `btle_ch37_20260617_085225.pcap` (până la 09:03:40) și `btle_ch39_20260617_084213.pcap` (până la 09:01:15). **Doar dreapta-sus (9:05-9:25) e efectiv rx-only** (DLT 255) — acesta e colțul cu adevărat expus riscului, nu ambele colțuri din dreapta cum sugera formularea inițială.
- **Implicație:** DLT 255 nu e caz marginal pentru dreapta-sus — poate fi singura sursă RSSI pentru acel colț. Dacă RSSI nu e extractibil din DLT 255, dreapta-sus rămâne fără date de triangulare, ceea ce trebuie raportat explicit (Principiul 1: nu ascunde limitarea), nu descoperit la final.
- **Notă suplimentară pentru Step 0 (Critic):** unele fișiere `rx_*.pcap` au timestamp-uri non-monotone între pachete (ex. `rx_20260617_085406.pcap`, `rx_20260617_091503.pcap`, `rx_20260617_092032.pcap`) — posibil rezultat al concatenării/resetării ceasului. Auditul de acoperire (Step 0) trebuie să filtreze per-pachet pe timestamp individual, nu pe intervalul [prim pachet, ultim pachet] al fișierului, altfel numărătoarea de acoperire poate fi greșită.
- **Acțiune adăugată: Step 0 — audit de acoperire temporală** (vezi Implementation Steps), care rulează ÎNAINTE de a finaliza design-ul extractorului, exact pentru a decide dacă DLT 255 conține RSSI utilizabil.

## Goal (moștenit din spec)
Extinderea `ble_utils.py`/`export_analysis.py` cu un modul de estimare a poziției (x,y) a device-urilor BT/BLE detectate în sesiunea de captură din 2026-06-17, corelând cele 4 ferestre orare de colț din `Logs.md` cu pachetele din pcap-urile relevante, afișând rezultatul tabelar + hartă vizuală 2D.

## Acceptance Criteria (testabile)
- [ ] `extract_windowed_packets(pcap_dir, corner_schedule)` returnează un DataFrame cu coloane `[timestamp, corner_label, mac_or_lap, rssi, channel, bt_type]`, filtrând strict pe suprapunerea timestamp-fereastră (nu pe nume fișier).
- [ ] Pentru `rx_*.pcap` fără RSSI extractibil, funcția marchează explicit rândurile ca `rssi=NaN` + `bt_type='classic_no_rssi'` (sau echivalent), nu le exclude silențios și nu inventează valori.
- [ ] `estimate_position(corner_distances: dict, corner_coords: dict) -> (x, y, confidence)` reutilizează `BLEAnalyzerUtils.estimate_distance()` (apelată de caller pentru a converti RSSI→distanță înainte de a intra în această funcție, care rămâne pură) și calculează centroid ponderat (x,y); testat cu cel puțin 3 cazuri: device echidistant de toate colțurile (poziție = centru), device foarte aproape de un colț (poziție trasă spre acel colț), și caz cu date lipsă la 1-2 colțuri (funcția nu crapă, produce încredere redusă). **(Corectat după review Fable — bug real de plan):** semnătura anterioară din acest punct (`corner_rssi_map, room_params`) era inconsistentă cu Step 2 (`corner_distances, corner_coords`) — două semnături diferite pentru aceeași funcție ar fi blocat scrierea testului RED. Semnătura finală e cea din Step 2.
- [ ] Modul de identitate device: funcție `match_devices(mode='cross_window'|'per_window', df)` — modul `per_window` nu unește niciun rând între ferestre; modul `cross_window` grupează după (nume advertising, UUID servicii) cu caveat documentat că nu e identitate criptografic garantată (RPA).
- [ ] Interfața de configurare (popup) expune minim: lungime/lățime sală (implicit: valori standard sală examen), și selectorul de mod identitate — testabilă prin apelarea funcției de bază fără UI (UI e un wrapper subțire peste o funcție pură testabilă).
- [ ] Output: funcție care produce simultan un `DataFrame` exportabil (CSV) și un plot matplotlib 2D cu poziția colțurilor + pozițiile estimate ale device-urilor, adnotate cu nivelul de încredere.
- [ ] Test acoperă cazul „toate cele 4 colțuri lipsesc RSSI pentru un device" — funcția nu trebuie să producă o poziție falsă (returnează None/NaN + flag).
- [ ] `pytest --cov` respectă pragul din `.coverage-thresholds.json` pentru fișierele noi.
- [ ] **(adăugat după review Architect)** Auditul de acoperire temporală (Step 0) rulează și raportează, per colț, câte pachete cu RSSI utilizabil există în fereastra respectivă; dacă un colț are 0 pachete RSSI-utilizabile, output-ul final marchează harta ca parțială pentru acel colț (nu produce o poziție falsă bazată pe absența datelor).
- [ ] **(adăugat după review Fable)** Auditul de observabilitate (Step 0) raportează explicit numărul de identități distincte observate la ≥3 colțuri, per mod (`per_window`/`cross_window`), înainte de a scrie codul modelului de poziționare. `estimate_position()` nu se apelează pentru device-uri sub acest prag.
- [ ] **(adăugat după review Fable)** Raportul final afișează fracția "identități cu matching reușit / identități totale observate" pentru modul `cross_window`, ca metrică vizibilă, nu doar rezultatele pozitive.

## Non-Goals (moștenite din spec)
- Least-squares/Levenberg-Marquardt (extensie viitoare posibilă, nu în acest scop).
- Rezolvare criptografică a RPA (necesită IRK, indisponibil pasiv).
- Colectare de date noi — se lucrează exclusiv cu pcap-urile din 2026-06-17.

## Implementation Steps

0. **Audit de acoperire temporală ȘI de observabilitate (OBLIGATORIU, înaintea oricărui cod de extracție)**
   - Pentru fiecare fereastră de colț din `Logs.md`, numără pachete DLT256-cu-RSSI vs pachete DLT255-doar, din toate pcap-urile disponibile.
   - Determină dacă payload-ul DLT 255 (`rx_*.pcap`) conține un câmp RSSI utilizabil (inspecție manuală a structurii — byte-uri după header LL).
   - Rezultatul acestui audit e un **finding de nivel spec**, nu un detaliu de implementare: dacă un colț nu are date RSSI, se documentează explicit ca "hartă parțială" în output, nu se ascunde.
   - **(adăugat după review Fable — gate critic, blochează scrierea codului de model dacă eșuează):** numără câte identități distincte (per fiecare mod, `per_window` și `cross_window`) sunt observate la **≥3 din cele 4 colțuri**. Triangularea reală (poziție (x,y) semnificativă, nu doar coordonata unui singur colț) e posibilă DOAR pentru acest subset. Dacă numărul e aproape de zero, acesta e un rezultat de raportat onest în teză ("populația de device-uri triangulabile e X din Y total observate"), nu un motiv de a ascunde limitarea sau de a proceda ca și cum triangularea ar funcționa pentru toate device-urile.

1. **Extractor pcap → DataFrame** (`ble_utils.py` sau modul nou `pcap_extractor.py`, respectând limita de 800 linii/fișier din coding-style.md)
   - `scapy` (dissector BLE LL) pentru linktype 256 — decodare corectă PDU type + AdvA (adresă device), câmp RSSI din PHDR.
   - Reader manual subțire pentru linktype 255 (`rx_*.pcap`), condiționat de rezultatul Step 0 — dacă RSSI nu e extractibil, funcția întoarce explicit `rssi=NaN, bt_type='classic_no_rssi'`, documentat, nu exclus silențios.
   - Funcție de corelare cu `Logs.md`: schedule citit dintr-un fișier de config (nu hardcodat în cod, per principiul imutabilității/configurabilității din coding-style.md), corelarea se face **exclusiv prin suprapunere timestamp pachet ↔ fereastră oră**, niciodată prin numele fișierului (confirmat: rotația ciclează pe canal/mod, nu pe colț fizic).

2. **Model de poziționare** (extensie în `ble_utils.py`, lângă `estimate_distance`)
   - `estimate_position(corner_distances: dict[str, float], corner_coords: dict[str, tuple]) -> tuple[float, float, float]` (x, y, confidence) — funcție pură, fără efecte laterale, imutabilă (nu modifică dict-urile primite).
   - **Formulă de ponderare explicită (cerută de review Fable — nu era definită anterior):** `weight_i = 1 / distance_i` (inverse-distance weighting standard), poziția = `sum(weight_i * corner_coords_i) / sum(weight_i)`. Trebuie documentat explicit în docstring, nu lăsat implicit.
   - **Guard obligatoriu (găsit de test-engineer Fable la deep-dive testare):** `distance_i = 0` produce `ZeroDivisionError`/`inf` cu formula brută (caz real: device fix lângă un colț, sau RSSI foarte puternic). Se aplică `max(distance_i, ε)` (ex. `ε=0.1m`) înainte de calculul ponderii.
   - **Limitare structurală de disclosat, nu de ascuns (Fable):** centroid ponderat NU poate produce niciodată o poziție în afara hull-ului convex al celor 4 colțuri (matematic garantat) — practic netezește rezultatele spre centrul sălii, nu localizează precis. Docstring + output trebuie să menționeze explicit acest bias sistematic, mai ales pentru device-uri aproape de pereți/colțuri reale.
   - **Precondiție obligatorie (Fable, punct critic #2):** `estimate_position` se aplică DOAR device-urilor identificate ca observate la ≥3 colțuri (rezultat din Step 0). Pentru restul, funcția nu trebuie apelată deloc — un device văzut la 1-2 colțuri nu produce o poziție triangulată, ci rămâne marcat explicit `confidence='insufficient_corners'` (per limitarea deja documentată la modul `per_window`).
   - Confidence = funcție de numărul de colțuri cu date valide (4/4 = încredere maximă, 3/4 = încredere medie; <3/4 = triangulare imposibilă structural, nu doar "încredere redusă" — vezi precondiția de mai sus).

3. **Rezolvare identitate device**
   - `match_devices(df, mode)` — pur, întoarce un nou DataFrame cu coloană `device_group_id` adăugată (nu mutează df-ul original).
   - Mod `per_window`: `device_group_id = f"{corner_label}_{mac_or_lap}"` (fără unire cross-fereastră). **Limitare documentată explicit (Architect):** în acest mod, un device văzut la un singur colț nu poate fi triangulat — poziția rezultată e pur și simplu coordonata acelui colț, nu o estimare (x,y) reală. Trebuie semnalat clar în output (ex: `confidence='single_corner_only'`), nu prezentat ca poziție triangulată.
   - Mod `cross_window`: grupare euristică pe (nume advertising normalizat, set UUID servicii) — documentat clar în docstring ca best-effort, nu identitate garantată (RPA nu poate fi rezolvat pasiv fără IRK). Funcționează doar pentru device-uri care emit nume/UUID stabile; device-urile complet anonime (doar RPA, fără alte câmpuri) rămân netriangulabile în acest mod și trebuie raportate ca atare.
   - **Încadrare onestă obligatorie (Fable, punct #4 — nu era spus clar anterior):** majoritatea telefoanelor moderne (iOS/Android) NU emit nume în advertising nedirecționat și adesea nu au UUID-uri de serviciu stabile. `cross_window` va reuși practic doar pe beacon-uri/wearables/periferice, nu pe telefoane — adică exact populația care umple o sală de examen. Raportul final trebuie să afișeze explicit fracția "identități matched / identități totale observate" ca metrică, nu doar rezultatele pozitive, altfel se creează impresia falsă de acoperire completă.

4. **Interfață de configurare (popup)**
   - Wrapper subțire (tehnologie la alegerea implementatorului — recomandare: `ipywidgets` dacă lucrul se face în notebook, coerent cu `export_analysis.py`) peste o funcție pură `build_room_config(length, width, corner_mode) -> RoomConfig` — logica de business separată de UI, testabilă fără a instanția widget-uri.

5. **Output tabel + hartă**
   - `render_position_table(results_df) -> pd.DataFrame` (export CSV-ready).
   - `render_position_map(results_df, room_config) -> matplotlib.Figure` — plot 2D cu colțuri + poziții + adnotări încredere.

6. **Teste (TDD, conform CLAUDE.md — obligatoriu înainte de implementare)**
   - Teste unitare pentru fiecare funcție pură de mai sus, cu date sintetice (nu depind de pcap-urile reale pentru determinism).
   - Cel puțin 1 test de integrare care rulează pipeline-ul complet pe un subset mic dintr-un pcap real care **se suprapune efectiv cu o fereastră de colț** — `btle_ch37_20260617_085225.pcap` (local 08:52, suprapune fereastra stânga-jos 8:55-9:15 și stânga-sus 8:50-9:10). **Corecție față de draftul inițial:** `btle_ch37_20260617_075606.pcap` (07:56) cade complet în afara tuturor ferestrelor — un pipeline filtrat temporal ar produce 0 pachete pe acest fișier, deci testul de integrare nu ar exercita nimic util.

## Risks and Mitigations

| Risc | Impact | Mitigare |
|---|---|---|
| `parse_kv_logs()` existent NU e compatibil cu pcap-urile (așteaptă `.txt` KV) — confuzie posibilă despre "reutilizare" | Mediu | Documentat explicit în plan: se reutilizează DOAR `estimate_distance()`; se scrie extractor nou pentru pcap |
| RPA face matching cross-fereastră nesigur | Mediu | Documentat ca limitare metodologică în output; mod `per_window` disponibil ca alternativă fără această presupunere |
| `rx_*.pcap` (linktype 255) pot să nu conțină RSSI utilizabil | Mediu | Investigare explicită în Step 1; degradare gracioasă (flag, nu excludere silențioasă sau crash) |
| Corelarea colț↔fișier eronată dacă orele din `Logs.md` nu se potrivesc exact cu timestamp-urile reale din pcap | Ridicat | Test de validare explicit: verifică că fiecare fereastră orară are cel puțin un pachet înainte de a continua; loghează ferestre goale |
| Geometrie sală aproximativă → poziții (x,y) cu eroare mare | Acceptat ca limitare cunoscută (documentată în spec ca non-goal de precizie GPS) | Comunicat explicit în output (nivel de încredere), nu ascuns |

## Verification & Testing Strategy (deep-dive, model Fable — `oh-my-claudecode:test-engineer`)

Strategie pe 3 axe cerute explicit de user înainte de execuție: funcționalitate, corectitudinea logicii, acuratețea datelor. Înlocuiește draftul inițial de 4 puncte generice.

### Axa 0 — Precondiții de mediu (blocante, înaintea oricărui test)
- `pytest`, `pytest-cov`, `scapy` **nu sunt instalate** (confirmat `ModuleNotFoundError`) — se adaugă pinned în `requirements-dev.txt` la rădăcină.
- Poarta de coverage e **100%** conform `.coverage-thresholds.json` (fără override pentru rădăcină — override-ul de 80% e doar pentru `ubertooth-windows-host`). Cod greu de acoperit (parsing binar scapy, randare matplotlib) trebuie izolat în adaptoare subțiri, ca logica pură să rămână 100% testabilă; excepțiile primesc `# pragma: no cover` cu justificare explicită, nu abuziv.
- Nu există `tests/` la rădăcină — se creează `tests/conftest.py` cu bootstrap `sys.path` (pattern deja folosit în `academic-research-skills/`).

### Axa 1 — Funcționalitate (cap-la-coadă, degradare gracioasă)
Fișiere: `tests/test_pipeline_e2e.py`, `tests/test_pcap_extractor.py`.
- **Fixture pcap real:** felie de ~50 pachete tăiată determinist din `btle_ch37_20260617_085225.pcap` (se suprapune efectiv cu ferestrele stânga-jos/stânga-sus) → `tests/fixtures/tiny_btle_sample.pcap`.
- `test_extract_windowed_packets_returns_expected_columns` — DataFrame `[timestamp, corner_label, mac_or_lap, rssi, channel, bt_type]`, ≥1 rând.
- `test_full_pipeline_produces_positions_and_figure` — extract → observability gate → estimate_position → render, fără excepție.
- **Degradare pe input invalid** (cerința explicită a userului "erori controlate"): director gol → DataFrame gol (nu crash); director inexistent → `FileNotFoundError` cu mesaj clar; DLT255 fără RSSI → `rssi=NaN, bt_type='classic_no_rssi'` (nu exclus silențios); pcap corupt/trunchiat → înregistrat în lista de erori (pattern `BLEAnalyzerUtils._errors`), pipeline continuă; fereastră fără niciun pachet → hartă marcată explicit "parțială" pentru acel colț.
- **Randare headless:** `matplotlib.use('Agg')` forțat în `conftest.py` înaintea oricărui import `pyplot`.

### Axa 2 — Corectitudinea logicii (TDD unitar, funcții pure, date sintetice)

**Fixture canonic** (`tests/conftest.py`): cameră `room_8x6` (L=8m, W=6m), colțuri `{stanga_jos:(0,0), dreapta_jos:(8,0), stanga_sus:(0,6), dreapta_sus:(8,6)}`, centroid=(4.0,3.0). Helper `rssi_from_distance(d) = -59 - 30*log10(d)` (inversul lui `estimate_distance`), pentru a fabrica RSSI sintetic din distanțe cunoscute.

**`test_estimate_position.py`** (funcția-cheie):
| Caz | Assert |
|---|---|
| Echidistant (toate distanțele=5.0) | poziție = centroid exact (±1e-9), confidence=4/4 |
| Aproape de un colț (`{sj:0.5, dj:9, ss:7, ds:11}`) | poziție trasă spre acel colț, mai aproape de (0,0) decât de centroid |
| 3 din 4 colțuri | poziție validă în interiorul triunghiului celor 3, confidence=3/4 (medie) |
| 2 din 4 colțuri | **NU** triangulează — `confidence='insufficient_corners'`, x,y=None (precondiția Fable din Step 2) |
| Toate lipsă | `(None, None, flag)` — nicio poziție falsă |
| Nu mută input-urile | dict-uri de intrare neschimbate după apel (imutabilitate) |
| **Invariant hull convex** (parametrizat, ~20 seturi de distanțe aleatoare pozitive) | poziția rezultată e mereu `0≤x≤8` și `0≤y≤6` — formalizează bias-ul deja documentat ca proprietate testată, nu doar menționată |
| Pull monoton | pe măsură ce distanța la un colț scade, poziția se apropie monoton de acel colț |
| **Distanță zero** | fără `ZeroDivisionError`/`inf` — poziția = colțul respectiv (testează guard-ul `max(d, ε)` adăugat mai sus) |

**`test_match_devices.py`:** `per_window` nu unește niciodată cross-fereastră (imutabil); `cross_window` unește pe (nume normalizat, UUID-uri) — normalizare testată explicit (`"Tile"` == `"tile "`); device-uri complet anonime (doar RPA) rămân neunite; metrica "fracție matching reușit" testată cu un caz concret (5 identități, 2 matchable → 0.4).

**`test_coverage_audit.py` / `test_observability_audit.py`** (Step 0): folosind schedule-ul real din `Logs.md` ca fixture — testează explicit că filtrarea e **per-pachet, nu pe interval** (caz: pachete la 08:40, 09:00, 08:45 pentru fereastra 08:50-09:10 → count=1, nu 3 — validează exact nota Critic despre `rx_*.pcap` non-monotone); testează contractul de graniță a ferestrei (inclusiv/exclusiv, definit explicit ca `[start, end)`); testează gate-ul de observabilitate (device la 3 colțuri → triangulabil, la 2 → exclus).

**`test_room_config.py`:** `build_room_config` respinge dimensiuni ≤0 și mod de identitate necunoscut cu `ValueError` (validare input, coding-style.md).

**`test_render_output.py`:** tabel cu coloanele așteptate (incl. `confidence`); figura e `matplotlib.figure.Figure`, nr. puncte = 4 colțuri + N device-uri.

### Axa 3 — Acuratețea datelor (fără ground-truth fizic direct — cea mai grea axă)

Insight cheie (Fable): **coordonatele celor 4 colțuri sunt deja ground-truth cunoscut exact** — nu trebuie așteptat un device de referință extern pentru validare cantitativă.

1. **Monte Carlo pe model invers** (`tests/test_ground_truth_validation.py`): alege un punct sintetic cunoscut, calculează distanțele reale la cele 4 colțuri, inversează în RSSI + zgomot gaussian (σ≈4dB, tipic shadowing), rulează `estimate_position`, măsoară eroarea pe 1000 de trageri. Dă o **limită inferioară teoretică** a erorii (cel mai bun caz posibil) — număr citabil direct în teză.
2. **Leave-One-Corner-Out pe coordonatele colțurilor** (nu pe device-uri reale): ascunde un colț, tratează-l ca emițător virtual cu distanțe cunoscute exact la ceilalți 3 (distanțe inter-colț geometrice), prezice poziția lui din cei 3 rămași, compară cu coordonata reală a colțului. **Rezultat așteptat, nu eșec:** un colț e mereu în afara triunghiului celorlalte 3 → centroidul ponderat nu-l poate atinge structural; eroarea LOCO cuantifică exact cât "trage" harta spre centru la margini — de raportat direct ca bias caracterizat, nu ascuns.
3. **LOCO pe device-uri reale (distinct de #2 — doar stabilitate, NU acuratețe):** pentru un device văzut la toate 4 colțuri, calculează poziția cu toate 4 + cele 4 variante leave-one-out; raza de dispersie a celor 5 estimări = metrică de încredere (`<1m`=high, `<3m`=medium, altfel low) — fără să compari cu vreun adevăr, deci nu trebuie prezentată ca "acuratețe".
4. **Verificări ordinale pe date reale** (mai puternice decât simpla monotonie discutată inițial): colțul cu RSSI maxim pentru un device trebuie să fie cel mai apropiat de poziția estimată a acelui device (`argmin(dist(pred, corners)) == argmax(rssi_per_corner)`) — rulat agregat pe toate device-urile reale, raportează procentul care trece.
5. **Comparație cu literatura (BluePIL 1.0-1.4m) — context, NU test**: nu se face `assert` împotriva acestei marje (regim experimental diferit: simultan/calibrat vs. non-simultan/aproximat); se raportează narativ, alături de #1-2, că setup-ul curent e structural mai puțin precis (consistent cu Principiul 1).
6. **Ancoră reală opțională (cost mic, valoare mare):** dacă userul confirmă că a avut un telefon propriu (MAC/nume cunoscut) la o poziție știută în timpul uneia din ferestre — sau poate măsura acum cu ruleta poziția vreunui device static din sală — asta oferă o singură ancoră metrică absolută, care schimbă calitativ validarea din "plauzibil" în "calibrat pe cel puțin un punct real". Rămâne opțional/condiționat, nu blocant.

### Ordine TDD (RED → GREEN → REFACTOR, per CLAUDE.md)
Step 0 audits → `estimate_position` → `match_devices` → `build_room_config` → extractor pcap → render → e2e → ground-truth (Axa 3). Fiecare test scris și văzut picând înainte de implementare. Verificare finală: `pytest --cov --cov-fail-under=100` verde.

### Structură fișiere `tests/`
```
tests/
  conftest.py                     # sys.path + matplotlib Agg + fixture-uri (room_8x6, corner_schedule, rssi_from_distance)
  fixtures/
    tiny_btle_sample.pcap         # ~50 pachete, in-window, din btle_ch37_20260617_085225.pcap
    corner_schedule.json          # cele 4 ferestre din Logs.md
  test_estimate_position.py
  test_match_devices.py
  test_coverage_audit.py
  test_observability_audit.py
  test_room_config.py
  test_render_output.py
  test_pcap_extractor.py
  test_pipeline_e2e.py
  test_ground_truth_validation.py
```

## ADR (Architecture Decision Record)

**Decision:** Extractorul pcap folosește `scapy` pentru fișierele DLT 256 (BLE cu PHDR) și un reader manual subțire pentru byte-ul RSSI din PHDR + pentru DLT 255 (`rx_*.pcap`). Modelul de poziționare e centroid ponderat peste `estimate_distance()` existent (nu least-squares). Corelarea colț↔pachet se face exclusiv prin suprapunere timestamp-fereastră (Logs.md), niciodată prin nume de fișier.

**Drivers:** (1) corectitudinea identității device-ului (AdvA) contează mai mult decât zero-dependențe; (2) precizia matematică suplimentară a least-squares e irosită pe date deja zgomotoase/non-simultane; (3) numele fișierelor s-au dovedit înșelătoare față de conținutul lor temporal real (verificat empiric de Architect + Critic).

**Alternatives considered:**
- Parser manual pentru tot (respins: risc de corupere silențioasă a AdvA pe calea DLT256, care e critică pentru identitate).
- Least-squares/Levenberg-Marquardt de la început (respins: non-goal explicit din spec — precizie falsă pe date zgomotoase).
- Corelare colț↔fișier pe baza numelui fișierului (respins: infirmat empiric — `..._085225` conține pachete la 08:58-09:03, nu 08:52).

**Why chosen:** Sinteza (scapy + manual subțire) izolează riscul de parsing greșit exact unde contează (AdvA pe DLT256), fără a adăuga dependențe grele (scapy e pur Python). Centroid ponderat respectă Principiul 1 (nu pretinde precizie inexistentă) și Principiul 4 (simplitate).

**Consequences:** Se adaugă `scapy` ca dependență de dev (pinned). Step 0 (audit acoperire temporală) devine obligatoriu înainte de orice cod de extracție — crește costul inițial, dar previne un design bazat pe presupuneri false despre acoperirea datelor (confirmat necesar de ambele revizii).

**Follow-ups:**
- La pin-uirea `scapy`, verifică explicit că versiunea suportă disecția `BLUETOOTH_LE_LL_WITH_PHDR` (linktype 256) cu extragere RSSI (Critic, open question).
- Clarifică la Step 0 dacă payload-ul DLT 255 e BR/EDR clasic sau alt format — determină dacă dreapta-sus poate fi triangulat deloc.
- Posibilă extensie viitoare (non-goal curent): least-squares/Levenberg-Marquardt dacă acoperirea RSSI se dovedește suficient de densă și non-goal-ul e revizuit explicit de user.

## Consensus Changelog

- **Planner (pass 1):** Draft inițial cu extractor manual struct-based, centroid ponderat, 6 componente din spec.
- **Architect:** A infirmat presupunerea "corner ↔ nume fișier"; a identificat că DLT255 e load-bearing pentru colțurile din dreapta, nu caz marginal; a respins fixture-ul de test de integrare (în afara ferestrelor); a recomandat scapy pentru DLT256 + manual subțire pentru DLT255/RSSI byte.
- **Planner (pass 2, aplicat de orchestrator):** Adoptă recomandarea Architect (Opțiunea C); adaugă Step 0 (audit acoperire temporală) ca gate obligatoriu; corectează fixture-ul de test la `btle_ch37_20260617_085225.pcap`; documentează explicit limitările modurilor `per_window`/`cross_window`.
- **Critic:** APPROVED, cu corecție de acuratețe — doar **dreapta-sus** (nu ambele colțuri din dreapta) e efectiv rx-only; `083208` atinge marginal fereastra stg-sus; a semnalat timestamp-uri non-monotone în unele `rx_*.pcap` ca ipoteză de validat în Step 0.
- **Planner (pass 3, aplicat de orchestrator):** Corectat textul "Descoperire critică" conform verificării Critic; adăugată nota despre filtrare per-pachet (nu pe interval) pentru fișierele cu timestamp-uri non-monotone.
- **Critic (model Fable, review suplimentar la cererea userului):** REVISE — a identificat o gaură metodologică pe care consensul Opus a ratat-o complet: Step 0 audita acoperirea RSSI, dar nu audita *observabilitatea* (câte identități sunt văzute la ≥3 colțuri, precondiție reală pentru triangulare). A mai semnalat: non-simultaneitatea schimbă natura erorii din "imprecisă" în "greșită" pentru device-uri mobile; formula de ponderare a centroid-ului nu era definită explicit și are un bias structural spre hull-ul convex; `cross_window` va rata practic majoritatea telefoanelor moderne (fără nume/UUID stabile în advertising).
- **Planner (pass 4, aplicat de orchestrator):** Adăugat gate de observabilitate în Step 0 (blochează `estimate_position()` pentru device-uri sub 3 colțuri); reformulat non-simultaneitatea ca limită de scop structurală (presupunere de staționaritate), nu doar caveat de încredere; definită explicit formula de ponderare + disclosat bias-ul de hull convex; adăugată cerința de raportare a fracției de matching reușit pentru `cross_window`.
- **Test Engineer (model Fable, deep-dive testare la cererea userului):** A găsit un bug real de plan — semnătura `estimate_position()` era definită diferit în Acceptance Criteria vs. Step 2, ceea ce ar fi blocat scrierea testului RED. A propus strategie completă pe 3 axe (funcționalitate/logică/acuratețe date), cu insight cheie pentru problema ground-truth: coordonatele celor 4 colțuri sunt deja adevăr cunoscut exact, permițând leave-one-corner-out fără niciun device real de referință. A mai găsit: guard lipsă pentru distanță=0 (div-by-zero), precondiții de mediu neinstalate (`pytest`, `scapy`), și riscul poartei de coverage 100% pe cod greu de testat (parsing binar, randare).
- **Planner (pass 5, aplicat de orchestrator):** Corectată semnătura `estimate_position()` peste tot în plan; adăugat guard `max(distance, ε)`; secțiunea "Verification Steps" (4 puncte generice) înlocuită integral cu strategia detaliată pe 3 axe (Axa 0-3), inclusiv structură de fișiere `tests/` și fixture-uri canonice.

## Sources / Grounding
- [A Bluetooth Low Energy Indoor Positioning System with Channel Diversity, Weighted Trilateration and Kalman Filtering](https://www.mdpi.com/1424-8220/17/12/2927) — validează centroid/trilaterare ponderată ca abordare competitivă pentru ancore puține/zgomotoase.
- [Accuracy Analysis of the Indoor Location System Based on Bluetooth Low-Energy RSSI Measurements](https://www.mdpi.com/1996-1073/15/23/8832)
- [Design and Implementation of an RSSI-Based Bluetooth Low Energy Indoor Localization System](https://arxiv.org/pdf/2310.14704) — confirmă formula log-distance path loss folosită deja în `ble_utils.py`.
- [Breaking BLE MAC Address Randomization with Allowlist-Based Side Channels](https://dl.acm.org/doi/10.1145/3744559) — confirmă că RPA se rotește ~15 min și necesită IRK pentru rezolvare, imposibil pasiv fără cheie.
- [Demystifying Bluetooth LE (BLE) Addresses - Argenox](https://argenox.com/library/bluetooth-low-energy/demystifying-ble-addresses)
- Vault: `BluePIL a Bluetooth-based PassIve Localization Method.md` — model Log-Distance + LM, limitări (shadowing, coeficient n variabil, degradare termică Ubertooth).
- Vault: `Analysis of a Bluetooth Traffic Dataset Obtained during University Examination Sessions.md` — precedent direct de trilaterare RSSI în sală de examen cu Ubertooth, cutoff -73dBm, KDE heatmaps.
- Vault: `Scan Session - 2026-06-17.md` — confirmă structura reală a datelor (canale, tipuri PDU, top device-uri, LAP-uri BT clasic).
