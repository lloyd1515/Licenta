# FIRMWARE ESP32: NOD REȚEA MESH CSI

Acest firmware transformă un modul ESP32 într-un nod senzor radio pasiv:
1. Emite cadre broadcast 802.11 la o rată de $250\text{ Hz}$ folosind `esp_wifi_80211_tx`.
2. Extrage datele CSI (64 subpurtătoare, din care 52 active HT20) din fiecare pachet recepționat de la celelalte noduri.
3. Transmite pachetele binare prin UART la $921600\text{ baud}$ către PC.

---

## 1. Configurare ID Nod

Înainte de flash, se ajustează `#define NODE_ID` în `main/main.c`:
- Nodul 1: `NODE_ID 1`
- Nodul 2: `NODE_ID 2`
- Nodul 3: `NODE_ID 3`

---

## 2. Compilare și Flash (ESP-IDF)

```bash
# Setează mediul ESP-IDF
. $HOME/esp/esp-idf/export.sh

# Setare țintă ESP32
idf.py set-target esp32

# Compilare și scriere pe portul serial (ex: /dev/ttyUSB0)
idf.py -p /dev/ttyUSB0 flash monitor
```

---

## 3. Format Pachet Binar UART (138 bytes / pachet)

| Câmp | Dimensiune | Descriere |
| :--- | :--- | :--- |
| `magic` | 2 bytes | Valoare fixă `0xA55A` pentru aliniere cadru |
| `node_id` | 1 byte | ID-ul nodului receptor (`1`, `2` sau `3`) |
| `rssi_dbm` | 1 byte | Puterea semnalului recepționat (dBm) |
| `timestamp_us` | 4 bytes | Timestamp intern microsecunde (`esp_timer_get_time`) |
| `seq` | 2 bytes | Contor secvențial pachete |
| `csi_iq` | 128 bytes | 64 subpurtătoare x 2 (valori I și Q, `int8_t`) |
