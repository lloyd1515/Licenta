"""UI simplu pentru CSI brut: amplitudinea pe cele 64 de subpurtatoare, primita prin UDP de la nodurile ESP32.
O coloana pentru fiecare nod. Rulare: .venv/bin/python src/csi_ui.py [--port 5005] [--node 3]"""
import argparse
import collections
import signal
import socket
import struct
import sys
import time
from typing import NamedTuple

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRectF, QTimer
from PyQt6.QtWidgets import QApplication

HEADER = struct.Struct("<HBbIH")  # magic, node_id, rssi_dbm, timestamp_us, seq
MAGIC = 0xA55A
SUBCARRIERS = 64
PACKET_BYTES = HEADER.size + 2 * SUBCARRIERS
HISTORY_ROWS = 300
REFRESH_MS = 50
RATE_WINDOW_S = 1.0


class Packet(NamedTuple):
    node_id: int
    rssi_dbm: int
    seq: int
    amplitude: np.ndarray


def parse_packet(data):
    """Intoarce un Packet, sau None daca datagrama nu are formatul nodului."""
    if len(data) != PACKET_BYTES:
        return None
    magic, node_id, rssi_dbm, _, seq = HEADER.unpack_from(data)
    if magic != MAGIC:
        return None
    iq = np.frombuffer(data, dtype=np.int8, offset=HEADER.size).astype(np.float32)
    return Packet(node_id, rssi_dbm, seq, np.hypot(iq[0::2], iq[1::2]))


class NodeColumn:
    """Coloana unui nod: spectrul ultimului pachet (sus) si cascada (jos)."""

    def __init__(self, layout, col, node_id):
        self.node_id = node_id
        self.history = np.zeros((HISTORY_ROWS, SUBCARRIERS), dtype=np.float32)
        self.spectrum = layout.addPlot(row=1, col=col, title=f"nod {node_id}")
        self.spectrum.setLabels(bottom="index subpurtatoare in buffer", left="amplitudine")
        self.spectrum.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.spectrum.plot(pen="y", symbol="o", symbolSize=4)
        waterfall = layout.addPlot(row=2, col=col, title=f"Cascada: ultimele {HISTORY_ROWS} pachete (cel mai nou sus)")
        waterfall.setLabels(bottom="index subpurtatoare in buffer", left="pachet")
        waterfall.setXLink(self.spectrum)
        self.image = pg.ImageItem(self.history.T, colorMap=pg.colormap.get("viridis"))
        self.image.setRect(QRectF(-0.5, 0, SUBCARRIERS, HISTORY_ROWS))
        waterfall.addItem(self.image)

    def show(self, packets):
        self.history = np.vstack([self.history] + [packet.amplitude for packet in packets])[-HISTORY_ROWS:]
        newest = packets[-1]
        self.curve.setData(np.arange(SUBCARRIERS), newest.amplitude)
        self.image.setImage(self.history.T, levels=(0, max(1.0, float(self.history.max()))))
        self.spectrum.setTitle(f"nod {self.node_id} | RSSI {newest.rssi_dbm} dBm | seq {newest.seq}")


class CsiView(pg.GraphicsLayoutWidget):
    def __init__(self, sock, port, node=None):
        super().__init__(title=f"CSI brut - UDP {port}")
        self.sock, self.port, self.node = sock, port, node
        self.columns = {}  # node_id -> NodeColumn, in ordinea primului pachet
        self.arrivals = collections.deque()
        self.total = 0
        self.info = self.addLabel("astept pachete...", row=0, col=0, colspan=3)
        self.timer = QTimer(interval=REFRESH_MS, timeout=self.refresh)
        self.timer.start()

    def receive(self):
        packets = []
        while True:
            try:
                packet = parse_packet(self.sock.recv(2048))
            except BlockingIOError:
                return packets
            if packet and (self.node is None or packet.node_id == self.node):
                packets.append(packet)

    def refresh(self):
        packets = self.receive()
        now = time.monotonic()
        self.total += len(packets)
        self.arrivals.extend([now] * len(packets))
        while self.arrivals and now - self.arrivals[0] > RATE_WINDOW_S:
            self.arrivals.popleft()
        for node_id in sorted({packet.node_id for packet in packets}):
            if node_id not in self.columns:
                self.columns[node_id] = NodeColumn(self, len(self.columns), node_id)
            self.columns[node_id].show([packet for packet in packets if packet.node_id == node_id])
        self.info.setText(f"UDP {self.port} | {self.total} pachete | {len(self.arrivals)} pachete/s")


def main():
    parser = argparse.ArgumentParser(description="UI simplu pentru CSI brut primit prin UDP.")
    parser.add_argument("--port", type=int, default=5005, help="portul UDP (implicit 5005)")
    parser.add_argument("--node", type=int, help="arata doar pachetele acestui nod")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("portul trebuie sa fie intre 1 si 65535")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", args.port))
    except OSError as error:
        sys.exit(f"Nu pot asculta pe UDP {args.port}: {error}")
    sock.setblocking(False)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    view = CsiView(sock, args.port, args.node)
    view.resize(1400, 700)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
