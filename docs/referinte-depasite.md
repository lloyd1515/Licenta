# Referințe depășite după conversia DDD

Codul s-a schimbat pe 25 nov. 2026. `main.c` are acum 29 de linii, iar funcțiile lui sunt în alte fișiere din `main/`. `csi_ui.py` pornește doar pachetul `src/csi/`. `parse_packet` este acum `decode` din `src/csi/contract/packet_v1.py`. `NODE_ID` este acum opțiunea Kconfig `CSI_NODE_ID`.

Documentele de mai jos descriu codul vechi. Deocamdată rămân neschimbate. Nu folosi numerele de linie din ele pentru codul nou.

## docs/StatusLicenta/16Nov2026/

- `Status_Licenta_16_Nov.html` (3): parse_packet / Packet x2, main.c 119 linii x1
  - linii: 91, 253, 270
- `raspunsuri_note_5nov_detaliat.html` (8): simbol firmware in main.c x7, main.c 119 linii x1, linie main.c x1
  - linii: 328, 387, 405, 409, 549, 594, 595, 596

## docs/StatusLicenta/9Nov2026/

- `csi_de_la_zero.html` (2): simbol firmware in main.c x1, parse_packet / Packet x1
  - linii: 299, 406
- `notite_curs_main.md` (23): linie main.c x22, simbol firmware in main.c x2
  - linii: 225, 234, 294, 436, 466, 514, 576, 639, 690, 829, 929, 998, 1037, 1064, 1178, 1272, 1482, 1584, 1708, 2058, 2133, 2433, 2434
- `raspunsuri_tehnice_5nov.html` (9): linie main.c x5, parse_packet / Packet x2, simbol firmware in main.c x2, main.c 119 linii x1
  - linii: 109, 185, 200, 257, 288, 295, 296, 297, 298

## docs/StatusLicenta/9Nov2026/pas_cu_pas/output/

- `08_main_reparat_12nov.txt` (1): parse_packet / Packet x1
  - linii: 228

## docs/StatusLicenta/9Nov2026/unelte/

- `gen_curs.py` (3): simbol firmware in main.c x2, linie main.c x2
  - linii: 125, 831, 832
- `gen_diag_main.py` (3): NODE_ID in main.c x2, simbol firmware in main.c x1
  - linii: 3, 19, 87

## docs/idei/senzor-tactic-wifi-csi/

- `README.md` (1): linie main.c x1
  - linii: 93
- `surse.md` (1): linie main.c x1
  - linii: 625

## docs/idei/senzor-tactic-wifi-csi/fezabilitate/

- `RAPORT.md` (1): linie main.c x1, simbol firmware in main.c x1
  - linii: 133

## docs/idei/senzor-tactic-wifi-csi/fezabilitate/rezultate/

- `capabilitati.json` (3): linie main.c x3
  - linii: 154, 161, 168

## docs/learning/

- `harta-main-c-csi-ui.html` (13): parse_packet / Packet x10, main.c 119 linii x1, simbol UI in csi_ui.py x1, NODE_ID in main.c x1
  - linii: 210, 254, 499, 632, 670, 741, 754, 758, 790, 818, 847, 934, 1035
- `notite.md` (2): linie main.c x1, simbol firmware in main.c x1
  - linii: 55, 253
