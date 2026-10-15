import collections

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from csi.gui.frames import Frame
from csi.gui.theme import COLORS, DOPPLER_LABEL_CRITICAL, DOPPLER_LABEL_NORMAL
from csi.room import DOPPLER_REFERENCE_HZ, SUBCARRIER_COUNT, WAVELENGTH_M

pg.setConfigOptions(antialias=True)
pg.setConfigOption("background", COLORS["background"])
pg.setConfigOption("foreground", COLORS["plot_foreground"])

WATERFALL_FRAMES = 100
WATERFALL_LEVELS = (0.0, 35.0)
DOPPLER_HISTORY_POINTS = 120
DOPPLER_MOVING_HZ = 10.0
DOPPLER_Y_MAX_HZ = 65


class SubcarrierWaterfall(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer = np.zeros((WATERFALL_FRAMES, SUBCARRIER_COUNT), dtype=np.float32)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Cascadă Amplitudine CSI (52 Subpurtătoare)", color=COLORS["plot_foreground"], size="10pt")
        self.plot_widget.setLabel("bottom", "Index Subpurtătoare OFDM", units="[-26 .. 26]")
        self.plot_widget.setLabel("left", "Istoric Timp", units="Cadre")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)

        self.image_item = pg.ImageItem()
        self.image_item.setColorMap(pg.colormap.get("plasma"))
        self.image_item.setRect(QRectF(-26, 0, SUBCARRIER_COUNT, WATERFALL_FRAMES))
        self.plot_widget.addItem(self.image_item)
        self.plot_widget.setXRange(-26, 26, padding=0.01)
        self.plot_widget.setYRange(0, WATERFALL_FRAMES, padding=0.01)

        layout.addWidget(self.plot_widget)

    def show_frame(self, frame: Frame):
        row = np.asarray(frame.amplitude, dtype=np.float32)[np.newaxis, :]
        self.buffer = np.concatenate([self.buffer[1:], row])
        self.image_item.setImage(self.buffer.T, autoLevels=False, levels=WATERFALL_LEVELS)


class DopplerPlot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = collections.deque([0.0] * DOPPLER_HISTORY_POINTS, maxlen=DOPPLER_HISTORY_POINTS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.speed_label = QLabel("Doppler: 0.0 Hz | Viteză Corp: 0.00 m/s [CALM]")
        self.speed_label.setStyleSheet(DOPPLER_LABEL_NORMAL)
        layout.addWidget(self.speed_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Spectru Doppler Live (0 - 60 Hz)", color=COLORS["plot_foreground"], size="10pt")
        self.plot_widget.setLabel("bottom", "Cadre")
        self.plot_widget.setLabel("left", "Frecvență Doppler", units="Hz")
        self.plot_widget.setYRange(0, DOPPLER_Y_MAX_HZ, padding=0.02)
        self.plot_widget.setXRange(0, DOPPLER_HISTORY_POINTS, padding=0.01)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.25)

        self.reference_line = pg.InfiniteLine(
            pos=DOPPLER_REFERENCE_HZ,
            angle=0,
            pen=pg.mkPen(color=COLORS["red"], width=2.2, style=Qt.PenStyle.DashLine),
            label=f"Prag Cădere ({DOPPLER_REFERENCE_HZ:.0f} Hz)",
            labelOpts={"position": 0.85, "color": COLORS["red"], "fill": (35, 10, 10, 210)},
        )
        self.plot_widget.addItem(self.reference_line)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color=COLORS["cyan"], width=2.5))
        layout.addWidget(self.plot_widget)

    def show_frame(self, frame: Frame):
        doppler_hz = frame.doppler_hz
        speed_m_s = doppler_hz * WAVELENGTH_M / 2
        self.history.append(doppler_hz)
        self.curve.setData(list(self.history))

        if doppler_hz >= DOPPLER_REFERENCE_HZ:
            self.curve.setPen(pg.mkPen(color=COLORS["red"], width=3.0))
            self.speed_label.setText(f"⚠ IMPACT! Doppler: {doppler_hz:.1f} Hz | Viteză: {speed_m_s:.2f} m/s [CRITIC]")
            self.speed_label.setStyleSheet(DOPPLER_LABEL_CRITICAL)
        else:
            self.curve.setPen(pg.mkPen(color=COLORS["cyan"], width=2.5))
            description = "MERS" if doppler_hz > DOPPLER_MOVING_HZ else "CALM"
            self.speed_label.setText(f"Doppler: {doppler_hz:.1f} Hz | Viteză: {speed_m_s:.2f} m/s [{description}]")
            self.speed_label.setStyleSheet(DOPPLER_LABEL_NORMAL)
