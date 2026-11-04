# FIRMWARE ESP32: NOD REȚEA MESH CSI

Acest firmware transformă un modul ESP32 într-un nod senzor radio pasiv:
1. Emite cadre broadcast 802.11 la o rată de $250\text{ Hz}$ folosind `esp_wifi_80211_tx`.
2. Extrage datele CSI (64 subpurtătoare, din care 52 active HT20) din fiecare pachet recepționat de la celelalte noduri.
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
- `CSI_UDP_PORT`: portul UDP (implicit `5005`).

Pe PC: `python -m csi.gui --live --port 5005` sau `python -m csi.record --port 5005`. Firewall-ul trebuie să permită UDP pe acest port.

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
| `csi_iq` | 128 bytes | 64 subpurtătoare x 2 (valori I și Q, `int8_t`) |
