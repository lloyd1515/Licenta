# FIRMWARE ESP32: NOD REȚEA MESH CSI

Acest firmware transformă un modul ESP32 într-un nod senzor radio pasiv:
1. Emite cadre broadcast 802.11 (probe request, 6 Mbps OFDM) la fiecare tick FreeRTOS (10 ms, adică $100\text{ Hz}$) folosind `esp_wifi_80211_tx`.
2. Extrage datele CSI din LLTF (64 subpurtătoare, din care 52 active) din fiecare probe request OFDM recepționat de la celelalte noduri. Celelalte cadre sunt ignorate: CSI din pachetele UDP ale altui nod ar crea o buclă (UDP → CSI → UDP).
3. Transmite pachetele binare prin Wi-Fi, ca datagrame UDP (un pachet / datagramă), către PC pe portul `5005`.

---

## 1. Configurare ID Nod

Înainte de flash, se ajustează `#define NODE_ID` în `main/main.c`:
- Nodul 1: `NODE_ID 1`
- Nodul 2: `NODE_ID 2`
- Nodul 3: `NODE_ID 3`

---

## 2. Configurare Rețea (UDP)

Nodul se conectează ca stație la un AP și trimite datele prin UDP. Toate nodurile folosesc același AP, deci același canal Wi-Fi.
Se setează în `idf.py menuconfig` → `CSI Node UDP`:
- `CSI_WIFI_SSID` / `CSI_WIFI_PASSWORD`: rețeaua Wi-Fi.
- `CSI_UDP_HOST`: IP-ul PC-ului receptor (implicit broadcast `255.255.255.255`; IP-ul unicast al PC-ului dă latență mai mică).
  Test din 12 nov. 2026, cu două noduri: la broadcast, AP-ul retransmite fiecare pachet la rate 11b, iar PC-ul a pierdut până la 24% din pachete. La unicast, PC-ul a pierdut 0%. La unicast, un singur program de pe PC primește pachetele, deci `csi_ui.py` merge într-o singură fereastră. Fereastra are o coloană pentru fiecare nod.
- `CSI_UDP_PORT`: portul UDP (implicit `5005`).

Pe PC: `.venv/bin/python src/csi_ui.py --port 5005` (din rădăcina repo-ului). Firewall-ul trebuie să permită UDP pe acest port.

---

## 3. Compilare și Flash (ESP-IDF)

```bash
# Setează mediul ESP-IDF
. $HOME/esp/esp-idf/export.sh

# Setare țintă ESP32
idf.py set-target esp32

# Setare SSID, parolă, IP și port UDP
idf.py menuconfig

# Compilare și scriere pe portul serial de programare (ex: /dev/ttyUSB0)
idf.py -p /dev/ttyUSB0 flash monitor
```

---

## 4. Format Pachet Binar UDP (138 bytes / datagramă)

| Câmp | Dimensiune | Descriere |
| :--- | :--- | :--- |
| `magic` | 2 bytes | Valoare fixă `0xA55A` pentru aliniere cadru |
| `node_id` | 1 byte | ID-ul nodului receptor (`1`, `2` sau `3`) |
| `rssi_dbm` | 1 byte | Puterea semnalului recepționat (dBm) |
| `timestamp_us` | 4 bytes | Timestamp intern microsecunde (`esp_timer_get_time`) |
| `seq` | 2 bytes | Contor secvențial pachete |
| `csi_iq` | 128 bytes | 64 subpurtătoare LLTF x 2 (`int8_t`): întâi Q (imaginar), apoi I (real); ordinea k = 0…31, apoi −32…−1. Dacă `first_word_invalid` este adevărat, primii 4 octeți (k = 0 și k = 1) sunt 0. |
