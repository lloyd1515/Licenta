import time

import pyqtgraph as pg
from PyQt6.QtCore import QTimer

from csi.application.throughput import Throughput
from csi.domain.events import NodeDiscovered
from csi.ui.node_column import NodeColumn

REFRESH_MS = 50
RATE_WINDOW_S = 1.0
INFO_COLSPAN = 3


# Fereastra principala cu noduri
class CsiView(pg.GraphicsLayoutWidget):
    # Construieste fereastra si timerul
    def __init__(self, source, ingest):
        super().__init__(title=f"CSI brut - UDP {source.port}")
        self.source, self.ingest = source, ingest
        self.columns = {}
        self.throughput = Throughput(RATE_WINDOW_S)
        self.info = self.addLabel("astept pachete...", row=0, col=0, colspan=INFO_COLSPAN)
        self.timer = QTimer(interval=REFRESH_MS, timeout=self.refresh)
        self.timer.start()

    # Tick: citeste, actualizeaza, deseneaza
    def refresh(self):
        result = self.ingest(self.source.drain())
        self.throughput = self.throughput.add(time.monotonic(), len(result.frames))
        for event in result.events:
            if isinstance(event, NodeDiscovered):
                self.columns = {**self.columns, event.node_id: NodeColumn(self, len(self.columns), event.node_id)}
        for node in sorted(result.nodes, key=lambda n: n.node_id):
            frames = [frame for frame in result.frames if frame.node_id == node.node_id]
            self.columns[node.node_id].show(node, frames)
        self.info.setText(
            f"UDP {self.source.port} | {self.throughput.total} pachete | "
            f"{self.throughput.per_second:.0f} pachete/s"
        )
