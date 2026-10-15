---
title: Protocol Binar UART
tags:
  - hardware
  - uart
  - protocol
  - serial
aliases:
  - Protocol UART
  - Cadru Binar
---

# 🔌 Protocol Binar de Comunicație UART

Pentru a transmite fluxul masiv de date CSI la 250 Hz fără blocaje de lățime de bandă sau overhead de text (JSON/ASCII), firmware-ul ESP32 transmite pachete binare compacte de dimensiune fixă: **138 octeți**.

* **Viteză serială (Baud rate):** `921600` baud.
* **Header Magic:** `0xA55A` (transmis Little-Endian: `0x5A`, `0xA5`).

Modulul de parsare și flux este implementat în [`src/csi/packets.py`](file:///home/vlads4r4/dev/Licenta/src/csi/packets.py) și achiziția sincronă în [`src/csi/record.py`](file:///home/vlads4r4/dev/Licenta/src/csi/record.py).

---

## 📦 Structura Cadrului Binar (138 Octeți)

| Câmp | Dimensiune | Format C | Semnificație |
| :--- | :---: | :---: | :--- |
| **Magic Header** | 2 B | `uint16_t` | `0xA55A` (sincronizare început cadru) |
| **Node ID** | 1 B | `uint8_t` | Identificatorul nodului sursă (`1`, `2` sau `3`) |
| **RSSI** | 1 B | `int8_t` | Nivelul puterii semnalului recepționat (dBm) |
| **Timestamp** | 4 B | `uint32_t` | Timp hardware intern ESP32 ($\mu s$) |
| **Sequence No.** | 2 B | `uint16_t` | Număr de secvență pentru detecție pierdere pachete |
| **CSI Payload** | 128 B | `int8_t[128]` | 64 subpurtătoare $\times$ 2 valori ($I$ și $Q$) |

---

## 🧮 Decodarea și Clasa `PacketStream` ([`src/csi/packets.py`](file:///home/vlads4r4/dev/Licenta/src/csi/packets.py))

În canalul de 20 MHz HT20, radioul furnizează 64 de perechi $(I, Q)$, din care sunt active cele **52 de subpurtătoare** utile (indicii $[-26..-1, 1..26]$ conform `SUBCARRIER_INDICES`):

```python
# Extragere din clasa PacketStream
def parse_bytes(self, chunk: bytes):
    self.buffer.extend(chunk)
    while len(self.buffer) >= PACKET_BYTES:
        if self.buffer[0] == 0x5A and self.buffer[1] == 0xA5:
            packet_data = bytes(self.buffer[:PACKET_BYTES])
            del self.buffer[:PACKET_BYTES]
            # struct.unpack: < = little-endian, H=uint16, B=uint8, b=int8, I=uint32, H=uint16
            magic, node_id, rssi, ts_us, seq = struct.unpack("<HBbIH", packet_data[:10])
            
            # 64 subpurtatoare x 2 (I si Q) int8
            iq = np.frombuffer(packet_data[10:138], dtype=np.int8)
            complex_csi = iq[0::2] + 1j * iq[1::2]
            
            # Decupare 52 subpurtatoare active
            csi_52 = np.concatenate([complex_csi[6:32], complex_csi[33:59]])
            ...
```

---

## 🛡️ Sincronizare și Recuperare din Pierderi de Cadre

Dacă apare un octet corupt pe magistrală:
1. `PacketStream` elimină octetul eronat și caută din nou secvența `0x5A, 0xA5`.
2. Pachetele sunt asamblate asincron de `SerialNodeReader` ([`src/csi/record.py`](file:///home/vlads4r4/dev/Licenta/src/csi/record.py)) sau preluate direct în GUI prin `FrameSource` ([`src/csi/gui/frame_source.py`](file:///home/vlads4r4/dev/Licenta/src/csi/gui/frame_source.py)).
