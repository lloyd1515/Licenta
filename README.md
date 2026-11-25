# Licenta: Wi-Fi CSI Sensing on ESP32

Bachelor thesis project (UTCN, 2026). The project measures Wi-Fi Channel State Information (CSI) with ESP32 boards. It shows the measurements on a PC.

## What CSI is

CSI is the response of the Wi-Fi channel on each subcarrier. It is a complex number (I, Q) for each subcarrier. People and walls change the radio signal on its path. This change is visible in CSI.

## Current status (November 2026)

| Area | Status |
| :--- | :--- |
| ESP32 firmware (5 modules in `main/`) | Works. Two nodes tested with a phone hotspot on channel 1. |
| PC viewer (`src/csi/`, started with `src/csi_ui.py`) | Works. One column for each node. It shows the amplitude on 64 subcarriers, the lost packets and the node time. |
| Board tools (flash and serial log) | Done. |
| Study of the closed Wi-Fi libraries | Done. Notes cover `libnet80211.a`, `libpp.a` and `libphy.a`. |
| Reply to the advisor notes of 5 Nov | Written. Latest version in `docs/StatusLicenta/16Nov2026/`. |
| Thesis (LaTeX, UTCN template) | In progress. Only the physics chapter has text that is checked against sources. |
| Detection, localization and fall detection | Not in the current code. The code was reduced to firmware and viewer. |

### Measured result

At unicast, the PC lost 0% of the packets from two nodes. At broadcast, the access point re-sent each packet at 11b rates. The PC lost up to 24% of the packets.

## How it works

1. Each node sends a probe request frame every 10 ms (100 Hz) at 6 Mbps.
2. Each node receives the frames of the other nodes in promiscuous mode.
3. The Wi-Fi driver gives the LLTF CSI of each frame to the `on_csi` callback.
4. The node sends 138 bytes in a UDP datagram to the PC on port `5005`.
5. The PC viewer (`src/csi/`) shows the amplitude of each subcarrier in time.

The packet format is in [src/firmware/esp32_csi_node/README.md](src/firmware/esp32_csi_node/README.md).

## Repository layout

| Path | Content |
| :--- | :--- |
| `src/firmware/esp32_csi_node/` | ESP-IDF v5.1.7 firmware and board tools |
| `src/csi/` | PC viewer package (PyQt6 and pyqtgraph), divided by DDD layers |
| `src/csi_ui.py` | Start script for the PC viewer |
| `tests/` | Unit tests for `src/csi/` (pytest) |
| `thesis/` | LaTeX source of the thesis |
| `docs/StatusLicenta/` | Status reports for the advisor |
| `docs/Materials/` | Sources and bibliography |
| `docs/learning/` | Study notes and code maps |
| `docs/idei/` | Ideas for future work |

## Run

1. Install ESP-IDF v5.1.7 and run `. $HOME/esp/esp-idf/export.sh`.
2. Go to `src/firmware/esp32_csi_node/`.
3. Run `idf.py menuconfig`. Set the Wi-Fi name, the password, the PC address and the port.
4. Set `Node ID` in the same menu. Each board must have a different ID. As an alternative, use `NODE_ID=4 WIFI_SSID=... WIFI_PASS=... bash tools/flash.sh`.
5. Run `idf.py -p /dev/ttyUSB0 flash monitor`.
6. On the PC, run `.venv/bin/python src/csi_ui.py --port 5005` from the repository root.

CAUTION: Allow UDP on port `5005` in the PC firewall. Without this rule, the viewer shows no data.

## Code structure (Domain Driven Design)

The code has four bounded contexts. Each context has one job.

| Context | PC side (`src/csi/`) | Firmware side (`main/`) |
| :--- | :--- | :--- |
| Capture | — | `node_wifi.c`, `csi_capture.c`, `probe_sender.c` |
| Packet contract (138 bytes) | `contract/packet_v1.py` | `csi_packet.h` |
| Domain model | `domain/`: `CsiFrame`, `NodeId`, `Node`, events, subcarrier layout | — |
| Use cases | `application/`: `IngestFrames`, `Throughput` | — |
| Adapters | `infrastructure/`: UDP socket, node repository | `udp_transport.c` |
| Display | `ui/`: `CsiView`, `NodeColumn` | — |

The domain layer does not use the network or Qt. `CsiFrame` keeps the complex I/Q values, so the phase is available. `CsiFrame.data_subcarriers()` gives the 52 LLTF subcarriers in the order k = -26..26, without k = 0.

## Tests

1. Go to the repository root.
2. Run `.venv/bin/python -m pytest --cov=csi`.

## Next steps

- Test with and without a person between two nodes.
- Describe the data in the thesis (amplitude in time, for each subcarrier).
- Write the chapter about CSI extraction on the ESP32.
