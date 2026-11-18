# Licență – status

9 Nov 2026 · Sursa task-urilor: secțiunea „Notes” din `../5Nov2026/Status_5Nov_2026_final.md` (discuția cu îndrumătorul).

Mod de lucru: un task pe sesiune. Pentru fiecare task: întrebare → test pe placă → răspuns scurt cu sursă.

Cod de test: `pas_cu_pas/main/main.c`, un main nou, mic. Îl construim pas cu pas. Rulare: `bash pas_cu_pas/ruleaza.sh`.

- [ ] Pasul 1: Wi-Fi + mod promiscuu pe canalul 1 + CSI → afișează `len` și `rssi` (task 1)
  Output-uri explicate: `pas_cu_pas/output/`.
- [ ] Pasul 2: conectare la hotspot + `ESP_ERROR_CHECK` + MAC-ul sursei → 1 CSI în 30 s (task 1, 2)
  Output: `output/05_pas2_conectare.md`. Codul pasului 1: `istoric/pas1_main.c`.
- [ ] Studiu: ce se întâmplă în spatele funcțiilor (header-e, cod deschis, biblioteci închise) → `notite_curs_main.md` (task 1, 2, 4)
- [ ] Pasul 3: ping la gateway (50/s) → 50 CSI/s + amplitudinea pe sub-frecvențe, o linie pe secundă
  Jurnal: `output/06_pas3_corp_intre.log`. Codul pasului 2: `istoric/pas2_main.c`.
  De făcut: același test fără persoană în cale, apoi comparația.
- [x] 11 Nov: `main.c` rescris de la zero, în 7 etape, cu nume simple (versiunea veche: `istoric/pas3_spec_main.c`). Fereastra live: `pas_cu_pas/grafic.py`.
  **Notițe de curs (un singur fișier): `notite_curs_main.md`**, în ordinea execuției, până la regiștri. Regenerare: `bash unelte/genereaza_curs.sh`. Jurnal: `output/07_main_nou.log`.

---

## Task-uri

### Partea practică (biblioteca `esp_wifi`)

- [ ] **1. Calea CSI: de la controllerul Wi-Fi la `on_csi`** (!)
  Ce funcție pornește CSI, cine apelează `on_csi` și ce conține `wifi_csi_info_t`.
  Test: afișează pe serial `info->len`, `first_word_invalid` și `rx_ctrl.sig_mode` pentru 10 pachete.

- [ ] **2. Ce fac funcțiile de configurare** („regiștrii de control” = parametrii din API)
  `esp_wifi_set_mode`, `set_ps`, `set_promiscuous`, `set_promiscuous_filter`, `set_csi_config`, `set_csi_rx_cb`, `set_csi`.
  Test: scoate pe rând câte o funcție din `main.c` și notează ce se schimbă.

- [ ] **3. Cum se schimbă parametrii de recepție**
  Câmpurile din `wifi_csi_config_t` (`lltf_en`, `htltf_en`, `stbc_htltf2_en`, `ltf_merge_en`) și canalul.
  Test: schimbă câte un câmp și compară `info->len` și numărul de pachete pe secundă.
  Atenție: `main.c` copiază doar primii 128 de octeți (`CSI_BYTES`). Restul bufferului se pierde.

### Partea de documentare

- [ ] **4. Ce face biblioteca, pentru studiul bibliografic**
  Rezumă task-urile 1–3 cu surse oficiale (ghidul ESP-IDF, `esp_wifi_types.h`).
  Marchează clar ce nu se poate ști (driverul are cod închis).

- [ ] **5. Planul capitolului 1**
  1.1 Fizica CSI (gata, în `5Nov2026`). 1.2 Extragerea CSI pe ESP32 (din task-ul 4).

- [ ] **6. Descrierea datelor**
  Descrie ce arată datele (amplitudine în timp, pe sub-frecvențe), fără o ipoteză de dovedit.
  Începe după task-ul 3.

---

## Răspunsuri

(Aici scriem câte un răspuns scurt, cu sursă, după fiecare task.)

### Task 1 (în lucru)

- `esp_wifi_set_csi_rx_cb` înregistrează `on_csi`. `esp_wifi_set_csi(true)` pornește apelurile. Driverul apelează `on_csi` din task-ul Wi-Fi, pentru fiecare cadru primit [ESP-IDF v5.1.7, `wifi.rst`, „Wi-Fi Channel State Information”].
- Test pe placă (9 Nov): 10 pachete. 9 au `sig_mode=0` (non-HT) și `len=128`. 1 are `sig_mode=1` (HT) și `len=384`.
- Tabelul din `wifi.rst`: non-HT = doar LLTF (128 B). HT cu 384 B = trei blocuri LTF (STBC, 20 MHz) sau HT 40 MHz. Încă nu știm care caz este.
- `first_word_invalid=1` la toate pachetele.
- CSI vine și înainte de conectarea la AP. Motivul: modul promiscuu.
- `main.c` păstrează doar primii 128 B. La pachetele HT, se pierd blocurile HT-LTF.
