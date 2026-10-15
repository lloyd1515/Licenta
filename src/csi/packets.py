import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np

BAUD_RATE = 921600
MAGIC = 0xA55A
HEADER_FORMAT = "<HBbIH"
HEADER_BYTES = 10
CSI_IQ_BYTES = 128
PACKET_BYTES = HEADER_BYTES + CSI_IQ_BYTES
ACTIVE_SUBCARRIERS = (slice(6, 32), slice(33, 59))
DEFAULT_PORTS = ("/dev/ttyUSB1", "/dev/ttyUSB0", "/dev/ttyUSB2")
FALLBACK_RATE_HZ = 30.0
DATA_DIR = Path(__file__).parent / "data"
EMPTY_ROOM = DATA_DIR / "test_A_camera_goala.npz"
WALKING = DATA_DIR / "test_B_mers_normal.npz"
REAL_FALL = DATA_DIR / "test_C_cadere_reala.npz"

_WIRE_MAGIC = struct.pack("<H", MAGIC)
_PORT_KEYS = ("p1", "p2", "p3")


@dataclass(frozen=True)
class Packet:
    node_id: int
    rssi_dbm: int
    timestamp_us: int
    seq: int
    csi: np.ndarray


@dataclass(frozen=True)
class Recording:
    times_s: np.ndarray
    rate_hz: float
    amplitude: np.ndarray
    rssi_dbm: np.ndarray


def _parse(raw):
    _, node_id, rssi_dbm, timestamp_us, seq = struct.unpack(HEADER_FORMAT, raw[:HEADER_BYTES])
    iq = np.frombuffer(raw[HEADER_BYTES:PACKET_BYTES], dtype=np.int8)
    csi = iq[0::2] + 1j * iq[1::2]
    active = np.concatenate([csi[part] for part in ACTIVE_SUBCARRIERS])
    return Packet(node_id, rssi_dbm, timestamp_us, seq, active)


class PacketStream:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, data):
        self._buffer.extend(data)
        packets = []
        while True:
            start = self._buffer.find(_WIRE_MAGIC)
            if start == -1:
                if self._buffer[-1:] == _WIRE_MAGIC[:1]:
                    del self._buffer[:-1]
                else:
                    self._buffer.clear()
                return packets
            del self._buffer[:start]
            if len(self._buffer) < PACKET_BYTES:
                return packets
            packets.append(_parse(bytes(self._buffer[:PACKET_BYTES])))
            del self._buffer[:PACKET_BYTES]


def _recording(times_s, csi_rows, rssi_dbm):
    times_s = np.asarray(times_s, dtype=np.float64)
    times_s = times_s - times_s[0]
    duration_s = times_s[-1] - times_s[0]
    rate_hz = float(len(times_s) / duration_s) if duration_s > 0 else FALLBACK_RATE_HZ
    amplitude = np.array([np.abs(row) for row in csi_rows], dtype=np.float32)
    return Recording(times_s, rate_hz, amplitude, np.asarray(rssi_dbm, dtype=np.float64))


def recording_from_packets(packets):
    return _recording(
        [packet.timestamp_us * 1e-6 for packet in packets],
        [packet.csi for packet in packets],
        [packet.rssi_dbm for packet in packets],
    )


def load_recording(path):
    data = np.load(path, allow_pickle=True)
    rows = max((data[key] for key in _PORT_KEYS if key in data.files), key=len)
    return _recording(
        [row["timestamp_s"] for row in rows],
        [row["csi"] for row in rows],
        [row["rssi"] for row in rows],
    )


def save_recording(path, packets_by_port):
    saved = {
        f"p{index + 1}": [
            {
                "timestamp_s": packet.timestamp_us * 1e-6,
                "node_id": packet.node_id,
                "rssi": packet.rssi_dbm,
                "seq": packet.seq,
                "csi": packet.csi,
            }
            for packet in packets
        ]
        for index, packets in enumerate(packets_by_port)
    }
    np.savez_compressed(path, **saved)
