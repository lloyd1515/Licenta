import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from csi.gui.charts import DopplerPlot, SubcarrierWaterfall
from csi.gui.frame_source import FrameSource
from csi.gui.frames import Frame
from csi.gui.room_map import RoomMap
from csi.gui.status_panel import StatusPanel
from csi.gui.theme import BADGE_LIVE, BADGE_OFF, BADGE_REPLAY, STYLESHEET
from csi.packets import REAL_FALL, UDP_PORT

WINDOW_TITLE = "Sistem Inteligent de Monitorizare Ambientală Wi-Fi CSI — Licență UTCN"
MIN_UDP_PORT = 1024
MAX_UDP_PORT = 65535
FPS_REFRESH_MS = 1000
NO_LATENCY = "--"
CONNECTION_BADGES = {
    "live": ("● LIVE UDP (:{port})", BADGE_LIVE),
    "replay": ("● REPLAY (TEST C)", BADGE_REPLAY),
    None: ("● DECONECTAT", BADGE_OFF),
}


def alarm_text(latency_s):
    latency = NO_LATENCY if latency_s is None else f"{latency_s:.2f}"
    return f"⚠️ ALERTĂ DE CĂDERE DETECTATĂ! PERSOANĂ LA SOL — LATENȚĂ: {latency} s — CONFIRMARE IMOBILITATE ACTIVĂ"


class MainWindow(QMainWindow):
    def __init__(self, udp_port=UDP_PORT, fps=50.0, recording_path=REAL_FALL):
        super().__init__()
        self.udp_port = udp_port
        self.fps = fps
        self.recording_path = recording_path
        self.source = None
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.alarm_dismissed = False

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1600, 950)
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(STYLESHEET)

        self._build_top_bar()
        columns = self._build_panels()
        self._build_alarm_banner()
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistem gata. Selectați modul Live UDP sau Replay Salvare.")
        self._build_layout(*columns)

        self.fps_timer = QTimer(self)
        self.fps_timer.setInterval(FPS_REFRESH_MS)
        self.fps_timer.timeout.connect(self._update_fps_label)
        self.fps_timer.start()

    def _build_top_bar(self):
        self.top_bar = QFrame(self)
        self.top_bar.setObjectName("TopBar")
        layout = QHBoxLayout(self.top_bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(14)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Sistem Inteligent de Monitorizare Ambientală Wi-Fi CSI", self.top_bar)
        title.setObjectName("AppTitle")
        subtitle = QLabel("Licență Calculatoare UTCN • Modul Multi-Link Fresnel & Detecție Căderi", self.top_bar)
        subtitle.setObjectName("AppSubtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        layout.addLayout(titles)
        layout.addStretch(1)

        self.status_badge = QLabel("● DECONECTAT", self.top_bar)
        self.status_badge.setObjectName("Badge")
        self.status_badge.setStyleSheet(BADGE_OFF)
        layout.addWidget(self.status_badge)

        self.fps_label = QLabel("FPS: --", self.top_bar)
        self.fps_label.setObjectName("MetricBadge")
        layout.addWidget(self.fps_label)

        self.port_box = QSpinBox(self.top_bar)
        self.port_box.setRange(MIN_UDP_PORT, MAX_UDP_PORT)
        self.port_box.setPrefix("UDP :")
        self.port_box.setValue(self.udp_port)
        layout.addWidget(self.port_box)

        self.live_button = QPushButton("Live UDP", self.top_bar)
        self.live_button.setObjectName("ToggleLive")
        self.live_button.setCheckable(True)
        self.live_button.clicked.connect(self._on_live_clicked)
        layout.addWidget(self.live_button)

        self.replay_button = QPushButton("Replay Salvare (Test C)", self.top_bar)
        self.replay_button.setObjectName("ToggleReplay")
        self.replay_button.setCheckable(True)
        self.replay_button.clicked.connect(self._on_replay_clicked)
        layout.addWidget(self.replay_button)

    def _titled_panel(self, title, widget):
        frame = QFrame(self)
        frame.setObjectName("PanelFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame(frame)
        header.setObjectName("PanelHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        title_label = QLabel(title, header)
        title_label.setObjectName("PanelTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)
        layout.addWidget(widget, 1)
        return frame

    def _build_panels(self):
        self.room_map = RoomMap(self)
        self.doppler_plot = DopplerPlot(self)
        self.waterfall = SubcarrierWaterfall(self)
        self.status_panel = StatusPanel(self)

        room_map_box = self._titled_panel("HARTĂ DE PROPAGARE RF & POZIȚIONARE 2D (ZONE FRESNEL)", self.room_map)
        doppler_box = self._titled_panel("SEMNĂTURĂ DOPPLER & DINAMICĂ VITEZĂ IMPACT", self.doppler_plot)
        waterfall_box = self._titled_panel("PROFIL SPECTRAL CSI (52 SUBPURTĂTOARE HT20)", self.waterfall)
        status_box = self._titled_panel("TELEMETRIE SISTEM & FSM MONITORIZARE CĂDERE", self.status_panel)
        return (
            self._stacked_splitter(self, room_map_box, doppler_box),
            self._stacked_splitter(self, waterfall_box, status_box),
        )

    def _build_alarm_banner(self):
        self.alarm_banner = QFrame(self)
        self.alarm_banner.setObjectName("AlertBanner")
        layout = QHBoxLayout(self.alarm_banner)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        self.alarm_label = QLabel(alarm_text(None), self.alarm_banner)
        self.alarm_label.setObjectName("AlertText")
        layout.addWidget(self.alarm_label, 1)

        self.dismiss_button = QPushButton("Resetează Alarmă", self.alarm_banner)
        self.dismiss_button.setObjectName("AlertResetButton")
        self.dismiss_button.clicked.connect(self.dismiss_alarm)
        layout.addWidget(self.dismiss_button)

        self.alarm_banner.hide()

    def _stacked_splitter(self, parent, top, bottom):
        container = QWidget(parent)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        splitter = QSplitter(Qt.Orientation.Vertical, container)
        splitter.addWidget(top)
        splitter.addWidget(bottom)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        layout.addWidget(splitter)
        return container

    def _build_layout(self, left_column, right_column):
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.addWidget(self.top_bar)

        main_splitter = QSplitter(Qt.Orientation.Horizontal, central)
        main_splitter.addWidget(left_column)
        main_splitter.addWidget(right_column)
        main_splitter.setStretchFactor(0, 5)
        main_splitter.setStretchFactor(1, 5)

        layout.addWidget(main_splitter, 1)
        layout.addWidget(self.alarm_banner)

    def _start_source(self, live):
        self.stop_source()
        self.source = FrameSource(
            live=live,
            udp_port=self.udp_port,
            fps=self.fps,
            recording_path=self.recording_path,
        )
        self.source.frame_ready.connect(self.show_frame)
        self.source.status_changed.connect(self.status_bar.showMessage)
        self.source.start()

    def start_live(self):
        self.udp_port = self.port_box.value()
        self.replay_button.setChecked(False)
        self.live_button.setChecked(True)
        self._start_source(True)
        self.set_connection_status("live")
        self.status_bar.showMessage(f"Ascultare noduri hardware pe portul UDP {self.udp_port}...")

    def start_replay(self):
        self.live_button.setChecked(False)
        self.replay_button.setChecked(True)
        self._start_source(False)
        self.set_connection_status("replay")
        self.status_bar.showMessage("Se rulează replay din salvarea Test C (Scenariu Cădere + Mers)...")

    def stop_source(self):
        if self.source is None:
            return
        self.source.stop()
        self.source = None

    def _on_live_clicked(self, checked):
        if checked:
            self.start_live()
            return
        self.stop_source()
        self.set_connection_status(None)
        self.status_bar.showMessage("Captura live a fost oprită.")

    def _on_replay_clicked(self, checked):
        if checked:
            self.start_replay()
            return
        self.stop_source()
        self.set_connection_status(None)
        self.status_bar.showMessage("Replay-ul a fost oprit.")

    def show_frame(self, frame: Frame):
        self.frame_count += 1

        self.room_map.show_frame(frame)
        self.doppler_plot.show_frame(frame)
        self.waterfall.show_frame(frame)
        self.status_panel.show_frame(frame)

        if not frame.alarm:
            self.alarm_dismissed = False
        elif not self.alarm_dismissed:
            self.show_alarm(frame.latency_s)

    def show_alarm(self, latency_s):
        self.alarm_label.setText(alarm_text(latency_s))
        self.alarm_banner.show()
        latency = NO_LATENCY if latency_s is None else f"{latency_s:.2f}"
        self.status_bar.showMessage(f"ALARMĂ CRITICĂ: Cădere confirmată cu latență de {latency} s!")

    def dismiss_alarm(self):
        self.alarm_dismissed = True
        self.alarm_banner.hide()
        self.status_panel.clear_alarm()
        if self.source is not None:
            self.source.reset_alarm()
        self.status_bar.showMessage("Alarma de cădere a fost resetată manual de utilizator.")

    def set_connection_status(self, mode):
        text, style = CONNECTION_BADGES[mode]
        self.status_badge.setText(text.format(port=self.port_box.value()))
        self.status_badge.setStyleSheet(style)

    def _update_fps_label(self):
        now = time.time()
        elapsed = now - self.last_fps_time
        if elapsed >= 1.0:
            self.fps_label.setText(f"FPS: {self.frame_count / elapsed:.1f}")
            self.frame_count = 0
            self.last_fps_time = now

    def closeEvent(self, event):
        self.stop_source()
        event.accept()
