from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from csi.fall_detector import STATE_LABELS, FallState
from csi.gui.frames import Frame
from csi.gui.theme import (
    CARD_STYLE,
    CARD_TITLE_STYLE,
    COLORS,
    SECTION_TITLE_STYLE,
    STATE_COLORS,
    card_value_style,
    fall_state_badge_style,
)
from csi.room import LINKS

MAX_HEIGHT_M = 1.8
INITIAL_HEIGHT_M = 1.75
HEIGHT_EASING = 0.2
SEATED_HEIGHT_M = 1.0
FLOOR_HEIGHT_M = 0.5
ACTIVE_LINK_ACTIVITY = 0.1
FLASH_INTERVAL_MS = 250
NO_VALUE = "--"
HEIGHT_TICKS = (
    (1.8, "1.8m (Picioare)"),
    (1.2, "1.2m"),
    (0.8, "0.8m (Așezat)"),
    (0.4, "0.4m (Sol)"),
    (0.0, "0.0m"),
)


class HeightGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(85, 200)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.height_m = INITIAL_HEIGHT_M

    def set_height_m(self, target_m: float):
        target_m = max(0.0, min(MAX_HEIGHT_M, target_m))
        self.height_m += (target_m - self.height_m) * HEIGHT_EASING
        self.update()

    def fill_color(self):
        if self.height_m < FLOOR_HEIGHT_M:
            return QColor(COLORS["red_strong"])
        if self.height_m < SEATED_HEIGHT_M:
            return QColor(COLORS["amber"])
        return QColor(COLORS["green"])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar_x, bar_w, top_y = 12.0, 26.0, 20.0
        bottom_y = self.height() - 25.0
        bar_h = bottom_y - top_y

        painter.setBrush(QBrush(QColor(COLORS["top_bar"])))
        painter.setPen(QPen(QColor(COLORS["border_strong"]), 1.5))
        painter.drawRoundedRect(QRectF(bar_x, top_y, bar_w, bar_h), 6.0, 6.0)

        fill_h = self.height_m / MAX_HEIGHT_M * bar_h
        fill_color = self.fill_color()
        painter.setBrush(QBrush(fill_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(bar_x + 2, bottom_y - fill_h, bar_w - 4, fill_h), 4.0, 4.0)

        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QColor(COLORS["muted"]))
        for value_m, text in HEIGHT_TICKS:
            tick_y = bottom_y - value_m / MAX_HEIGHT_M * bar_h
            painter.drawLine(QPointF(bar_x + bar_w, tick_y), QPointF(bar_x + bar_w + 4, tick_y))
            painter.drawText(int(bar_x + bar_w + 8), int(tick_y + 3), text)

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(fill_color)
        painter.drawText(int(bar_x - 4), int(self.height() - 6), f"{self.height_m:.2f} m")


class Card(QFrame):
    def __init__(self, title, value, value_color):
        super().__init__()
        self.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(CARD_TITLE_STYLE)
        self.value = QLabel(value)
        self.value.setStyleSheet(card_value_style(value_color))

        layout.addWidget(title_label)
        layout.addWidget(self.value)

    def set_value(self, text):
        self.value.setText(text)


class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = FallState.CALM
        self.flash_on = False

        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_timer.start(FLASH_INTERVAL_MS)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(14)

        self.height_gauge = HeightGauge(self)
        layout.addWidget(self.height_gauge)

        column = QVBoxLayout()
        column.setSpacing(10)

        section_title = QLabel("STARE FSM & TELEMETRIE CSI")
        section_title.setStyleSheet(SECTION_TITLE_STYLE)
        column.addWidget(section_title)

        self.state_badge = QLabel()
        self.state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_badge.setFixedHeight(44)
        self._apply_state_style()
        column.addWidget(self.state_badge)

        self.latency_card = Card("Latență Procesare", NO_VALUE, COLORS["accent"])
        self.rssi_card = Card("Putere RSSI", NO_VALUE, COLORS["mint"])
        self.links_card = Card("Link-uri Active", f"{len(LINKS)} / {len(LINKS)} Mesh", COLORS["violet"])
        self.motion_card = Card("Energie PC1", NO_VALUE, COLORS["yellow"])

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(self.latency_card, 0, 0)
        grid.addWidget(self.rssi_card, 0, 1)
        grid.addWidget(self.links_card, 1, 0)
        grid.addWidget(self.motion_card, 1, 1)
        column.addLayout(grid)
        column.addStretch(1)

        layout.addLayout(column, stretch=1)

    def _apply_state_style(self):
        colors = STATE_COLORS[self.state]
        background = COLORS["red_darker"] if self.state == FallState.ALARM and self.flash_on else colors.background
        self.state_badge.setText(STATE_LABELS[self.state])
        self.state_badge.setStyleSheet(fall_state_badge_style(background, colors))

    def _toggle_flash(self):
        if self.state == FallState.ALARM:
            self.flash_on = not self.flash_on
            self._apply_state_style()

    def clear_alarm(self):
        self.state = FallState.CALM
        self._apply_state_style()

    def show_frame(self, frame: Frame):
        self.height_gauge.set_height_m(frame.height_m)

        if frame.state != self.state:
            self.state = frame.state
            self.flash_on = False
            self._apply_state_style()

        self.rssi_card.set_value(f"{frame.rssi_dbm:.1f} dBm")
        self.motion_card.set_value(f"{frame.motion:.2f}")
        active_links = len(LINKS) if frame.activity > ACTIVE_LINK_ACTIVITY else 0
        self.links_card.set_value(f"{active_links} / {len(LINKS)} Mesh")
        latency = NO_VALUE if frame.latency_s is None else f"{frame.latency_s:.2f} s"
        self.latency_card.set_value(latency)
