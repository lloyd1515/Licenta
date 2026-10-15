# Feature: Binary Serial Packet Ingestion

## 1. Physical Framing
ESP32 nodes stream CSI frames over UART at 921600 baud.
Packet size is strictly 138 bytes:

| Offset (Bytes) | Type | Field | Description |
|---|---|---|---|
| 0..1 | uint16 | magic | 0xA55A (0x5AA5 in little-endian) |
| 2 | uint8 | node_id | Sender node ID (1, 2, or 3) |
| 3 | int8 | rssi | Receiver RSSI (dBm) |
| 4..7 | uint32 | timestamp | Microsecond hardware timer (`esp_timer_get_time`) |
| 8..9 | uint16 | seq | Incremental packet sequence index |
| 10..137 | int8[128] | csi_payload | 64 raw (I, Q) complex subcarrier pairs |

## 2. Subcarrier Decoupling
802.11n HT20 utilizes 52 active OFDM subcarriers: indices [-26..-1, 1..26].
DC pilot (index 0) and out-of-band guard subcarriers (0..5 and 59..63) are stripped:
```python
csi_52 = np.concatenate([complex_csi[6:32], complex_csi[33:59]])
```
