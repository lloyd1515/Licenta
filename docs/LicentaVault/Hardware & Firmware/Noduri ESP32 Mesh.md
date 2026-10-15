---
title: Noduri ESP32 Mesh
tags:
  - hardware
  - esp32
  - mesh
  - rf
aliases:
  - ESP32
  - Noduri
---

# 📡 Rețeaua Triunghiulară de Noduri ESP32

Sistemul utilizează **3 noduri fizice ESP32** configurate să opereze pe banda Wi-Fi de **2.4 GHz** (Canal 6, $f_c = 2.437\text{ GHz}$). Constantele fizice sunt centralizate în modulul [`src/csi/room.py`](file:///home/vlads4r4/dev/Licenta/src/csi/room.py).

---

## 📐 Topologia Spațială a Camerei (5m × 5m)

Nodurile sunt amplasate la periferia încăperii pentru a acoperi zona centrală prin 3 legături radio intersectate (bază de triangulație radio):

```
       Y (Nord)
       ^
  +2.5 ┼─────────────────────────────────┐
       │                                 │
  +1.2 ┼───[Nod 1]─────────────[Nod 2]───┤
       │   (-2.0, 1.2)         (2.0, 1.2)│
   0.0 ┼                 X               │
       │               (0, 0)            │
       │                                 │
  -2.0 ┼────────────[Nod 3]──────────────┤
       │            (0.0, -2.0)          │
  -2.5 ┼─────────────────────────────────┘
       └───────┼─────────┼─────────┼─────> X (Est)
             -2.5       0.0      +2.5
```

### Legăturile Radio Active (`LINKS = ((1, 2), (2, 3), (3, 1))`)
1. **Link 1-2:** Distanță directă $d_{12} = 4.0\text{ m}$ (axa superioară orizontală).
2. **Link 2-3:** Distanță directă $d_{23} = \sqrt{(0 - 2)^2 + (-2 - 1.2)^2} \approx 3.77\text{ m}$.
3. **Link 3-1:** Distanță directă $d_{31} = \sqrt{(-2 - 0)^2 + (1.2 - (-2))^2} \approx 3.77\text{ m}$.

---

## ⚙️ Parametrii Tehnici Radio

* **Standard:** IEEE 802.11n HT20 (Single Spatial Stream SISO).
* **Frecvență purtătoare ($f_c$):** $2.437\times 10^9\text{ Hz}$ (`CENTER_FREQ_HZ`).
* **Lungime de undă ($\lambda$):** $\lambda = \frac{c}{f_c} \approx 0.123\text{ m}$ ($12.3\text{ cm}$, `WAVELENGTH_M`).
* **Număr subpurtătoare active OFDM:** 52 subpurtătoare cu indici $[-26..-1, 1..26]$ (`SUBCARRIER_INDICES`, spațiate la $312.5\text{ kHz}$).
* **Frecvență de eșantionare ($f_s$):** $\approx 250\text{ Hz}$ pe nodurile fizice.

---

## 💻 Firmware ESP32 ([`src/firmware/esp32_csi_node/`](file:///home/vlads4r4/dev/Licenta/src/firmware/esp32_csi_node))

* Scris în **C**, bazat pe **ESP-IDF v5.x** și **FreeRTOS**.
* Folosește callback-ul nativ `esp_wifi_set_csi_rx_cb()` pentru interceptarea cadrelor brute în mod promiscuu.
* Împachetează datele și le transmite pe portul serial prin UART de mare viteză (921600 baud) conform specificației din [[Protocol Binar UART]].
