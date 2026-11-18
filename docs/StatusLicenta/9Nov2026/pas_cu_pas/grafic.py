"""Fereastra live pentru main/main.c: citeste jurnalul placii pe portul serial si il deseneaza.
Rulare: ~/dev/Licenta/.venv/bin/python grafic.py [/dev/ttyUSB0]
La pornire, fereastra reseteaza placa, ca sa vezi tot drumul, de la app_main()."""
import collections
import re
import sys
import time

import pyqtgraph as pg
import serial
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BAUD = 115200                     # aceeasi viteza ca in ruleaza.sh
HISTORY_S = 60                    # cate secunde arata graficele in timp
SUBCARRIERS = [k for k in range(-26, 27) if k not in (0, 1)]   # aceleasi 51 ca in on_csi
WATCH = ["-20", "-7", "+7", "+20"]                           # aceleasi ca in linia A_medie din main.c
COLORS = ["#e15759", "#f28e2b", "#59a14f", "#4e79a7"]
ANSI = re.compile(r"\x1b\[[0-9;]*m")                          # culorile din jurnal
RATE = re.compile(r"(\d+) CSI/s\s+rssi=\s*(-?\d+)")         # linia 1 pe secunda din on_csi
AMPS = re.compile(r"A_medie=\s*([\d.]+)\s+A\[-20\]=\s*([\d.]+) A\[-7\]=\s*([\d.]+)"
                  r" A\[\+7\]=\s*([\d.]+) A\[\+20\]=\s*([\d.]+)")   # linia 2


def open_board(port):
    """Deschide portul si reseteaza placa (RTS = pinul EN, DTR = pinul IO0)."""
    ser = serial.Serial()
    ser.port, ser.baudrate, ser.timeout = port, BAUD, 0
    ser.dtr, ser.rts = False, True    # EN jos: placa sta in reset
    ser.open()
    time.sleep(0.1)
    ser.rts = False                   # EN sus: placa porneste normal
    return ser


class Window(QWidget):
    def __init__(self, ser):
        super().__init__()
        self.ser, self.buf, self.t0 = ser, "", time.time()
        self.rssi_hist = collections.deque(maxlen=HISTORY_S)   # (t, rssi)
        self.amp_hist = collections.deque(maxlen=HISTORY_S)    # (t, A_medie, A[-20], A[-7], A[+7], A[+20])
        self.setWindowTitle("CSI live")
        self.status = QLabel("Astept placa ...")
        self.status.setFont(QFont("monospace", 14, QFont.Weight.Bold))

        plots = pg.GraphicsLayoutWidget()
        p_rssi = plots.addPlot(title="RSSI (dBm) - puterea cadrului, calibrata")
        p_amp = plots.addPlot(title="Amplitudinea CSI - medii pe secunda")
        plots.nextRow()
        p_spec = plots.addPlot(title="Spectrul: amplitudinea pe fiecare sub-frecventa k (ultima secunda)", colspan=2)
        for p in (p_rssi, p_amp):
            p.setLabel("bottom", "timp (s)")
            p.showGrid(x=True, y=True, alpha=0.3)
        p_spec.setLabel("bottom", "sub-frecventa k")
        p_amp.addLegend(offset=(5, 5))
        self.c_rssi = p_rssi.plot(pen=pg.mkPen("w", width=2), symbol="o", symbolSize=4)
        self.c_avg = p_amp.plot(pen=pg.mkPen("w", width=3), name="A_medie")
        self.c_watch = [p_amp.plot(pen=pg.mkPen(c, width=2), name=f"A[{w}]") for w, c in zip(WATCH, COLORS)]
        self.bars = pg.BarGraphItem(x=SUBCARRIERS, height=[0] * len(SUBCARRIERS), width=0.8, brush="#76b7b2")
        p_spec.addItem(self.bars)
        for w, c in zip(WATCH, COLORS):   # marcam cele 4 sub-frecvente urmarite
            p_spec.addItem(pg.InfiniteLine(int(w), pen=pg.mkPen(c, style=pg.QtCore.Qt.PenStyle.DashLine)))

        self.log = QPlainTextEdit(readOnly=True, maximumBlockCount=300)
        self.log.setFont(QFont("monospace", 9))
        self.log.setMaximumHeight(170)

        box = QVBoxLayout(self)
        box.addWidget(self.status)
        box.addWidget(plots, stretch=1)
        box.addWidget(QLabel("Jurnalul placii (fara liniile SPEC):"))
        box.addWidget(self.log)

        self.timer = QTimer(timeout=self.read_serial)
        self.timer.start(100)                 # citim portul de 10 ori pe secunda

    def read_serial(self):
        self.buf += self.ser.read(self.ser.in_waiting or 1).decode(errors="replace")
        *lines, self.buf = self.buf.split("\n")
        for line in lines:
            self.handle(ANSI.sub("", line).strip())

    def handle(self, line):
        if line.startswith("SPEC "):          # linia noua din on_csi: 51 de amplitudini
            values = [float(v) for v in line.split()[1:]]
            if len(values) == len(SUBCARRIERS):
                self.bars.setOpts(height=values)
            return
        if line and "�" not in line:     # fara zgomotul de la reset (alta viteza)
            self.log.appendPlainText(line)
        now = time.time() - self.t0
        if m := RATE.search(line):
            n, rssi = int(m[1]), int(m[2])
            self.rssi_hist.append((now, rssi))
            self.c_rssi.setData(*zip(*self.rssi_hist))
            self.status.setText(f"{n} CSI/s   RSSI {rssi} dBm")
        elif m := AMPS.search(line):
            self.amp_hist.append((now, *(float(v) for v in m.groups())))
            t, avg, *watch = zip(*self.amp_hist)
            self.c_avg.setData(t, avg)
            for curve, values in zip(self.c_watch, watch):
                curve.setData(t, values)
        elif "Conectat" in line:
            self.status.setText(line.split("CSI: ")[-1])

    def closeEvent(self, event):
        self.ser.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window(open_board(PORT))
    win.resize(1200, 850)
    win.show()
    sys.exit(app.exec())
