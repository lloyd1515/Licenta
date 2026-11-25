import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRectF

from csi.domain import subcarriers

HISTORY_ROWS = 300
MIN_COLOR_LEVEL = 1.0
MICROSECONDS = 1_000_000


# Coloana unui nod: spectru, cascada
class NodeColumn:
    # Construieste cele doua grafice
    def __init__(self, layout, col, node_id):
        self.node_id = node_id
        self.history = np.zeros((HISTORY_ROWS, subcarriers.COUNT), dtype=np.float32)
        self.spectrum = layout.addPlot(row=1, col=col, title=f"nod {node_id}")
        self.spectrum.setLabels(bottom="index subpurtatoare in buffer", left="amplitudine")
        self.spectrum.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.spectrum.plot(pen="y", symbol="o", symbolSize=4)
        waterfall = layout.addPlot(row=2, col=col, title=f"Cascada: ultimele {HISTORY_ROWS} pachete (cel mai nou sus)")
        waterfall.setLabels(bottom="index subpurtatoare in buffer", left="pachet")
        waterfall.setXLink(self.spectrum)
        self.image = pg.ImageItem(self.history.T, colorMap=pg.colormap.get("viridis"))
        self.image.setRect(QRectF(-0.5, 0, subcarriers.COUNT, HISTORY_ROWS))
        waterfall.addItem(self.image)

    # Deseneaza cadrele noi ale nodului
    def show(self, node, frames):
        self.history = np.vstack([self.history] + [frame.amplitude for frame in frames])[-HISTORY_ROWS:]
        newest = frames[-1]
        self.curve.setData(np.arange(subcarriers.COUNT), newest.amplitude)
        self.image.setImage(self.history.T, levels=(0, max(MIN_COLOR_LEVEL, float(self.history.max()))))
        self.spectrum.setTitle(
            f"nod {self.node_id} | RSSI {newest.rssi_dbm} dBm | seq {newest.seq} | "
            f"pierdute {node.frames_lost} | t {node.elapsed_us / MICROSECONDS:.1f} s"
        )
