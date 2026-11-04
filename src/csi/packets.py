import socket
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np

UDP_PORT = 5005
UDP_RECEIVE_BYTES = 2048
MAGIC = 0xA55A
HEADER_FORMAT = "<HBbIH"
HEADER_BYTES = 10
CSI_IQ_BYTES = 128
PACKET_BYTES = HEADER_BYTES + CSI_IQ_BYTES
ACTIVE_SUBCARRIERS = (slice(6, 32), slice(33, 59))
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


def encode_packet(packet):
    iq = np.zeros(CSI_IQ_BYTES // 2, dtype=np.complex128)
    sizes = [part.stop - part.start for part in ACTIVE_SUBCARRIERS]
    for part, values in zip(ACTIVE_SUBCARRIERS, np.split(np.asarray(packet.csi), np.cumsum(sizes)[:-1])):
        iq[part] = values
    interleaved = np.empty(CSI_IQ_BYTES, dtype=np.int8)
    interleaved[0::2] = np.clip(np.round(iq.real), -128, 127)
    interleaved[1::2] = np.clip(np.round(iq.imag), -128, 127)
    header = struct.pack(HEADER_FORMAT, MAGIC, packet.node_id, packet.rssi_dbm, packet.timestamp_us, packet.seq)
    return header + interleaved.tobytes()


def parse_datagram(data):
    return [
        _parse(data[start:start + PACKET_BYTES])
        for start in range(0, len(data) - PACKET_BYTES + 1, PACKET_BYTES)
        if data[start:start + 2] == _WIRE_MAGIC
    ]


def open_udp_socket(port, timeout_s=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    sock.settimeout(timeout_s)
    return sock


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
