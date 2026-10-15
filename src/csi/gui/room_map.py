import math

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QSizePolicy, QWidget

from csi.fall_detector import FallState
from csi.gui.frames import Frame
from csi.gui.theme import COLORS
from csi.room import LINKS, NODE_POSITIONS_M, ROOM_HALF_SIZE_M, ROOM_SIZE_M, WAVELENGTH_M

MARGIN_PX = 35.0
MIN_SIDE_PX = 100.0
IDLE_ACTIVITY = 0.1
PULSE_STEP = 0.12
ANIMATION_INTERVAL_MS = 40
FALL_STATES = (FallState.IMPACT, FallState.CHECKING_STILL, FallState.ALARM)
MIN_ARROW_SPEED_M_S = 0.05
ARROW_PX_PER_M_S = 26.0
ARROW_MIN_PX = 18.0
ARROW_MAX_PX = 50.0
ARROW_HEAD_PX = 8.0


def with_alpha(color_name, alpha):
    color = QColor(COLORS[color_name])
    color.setAlpha(alpha)
    return color


class RoomMap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(380, 380)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.x_m = 0.0
        self.y_m = 0.0
        self.vx_m_s = 0.0
        self.vy_m_s = 0.0
        self.state = FallState.CALM
        self.activity = IDLE_ACTIVITY

        self.pulse_phase = 0.0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._tick)
        self.animation_timer.start(ANIMATION_INTERVAL_MS)

    def _tick(self):
        self.pulse_phase = (self.pulse_phase + PULSE_STEP) % (2.0 * math.pi)
        self.update()

    def show_frame(self, frame: Frame):
        self.x_m = frame.x_m
        self.y_m = frame.y_m
        self.vx_m_s = frame.vx_m_s
        self.vy_m_s = frame.vy_m_s
        self.state = frame.state
        self.activity = frame.activity
        self.update()

    def room_square(self):
        side = max(MIN_SIDE_PX, min(self.width(), self.height()) - 2.0 * MARGIN_PX)
        left = (self.width() - side) / 2.0
        top = (self.height() - side) / 2.0
        return left, top, side, side / ROOM_SIZE_M

    def to_pixels(self, x_m, y_m):
        left, top, _, scale = self.room_square()
        return QPointF(
            left + (x_m + ROOM_HALF_SIZE_M) * scale,
            top + (ROOM_HALF_SIZE_M - y_m) * scale,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self._draw_background(painter)
        self._draw_grid(painter)
        for link in LINKS:
            self._draw_link(painter, link)
        for node_id, position in NODE_POSITIONS_M.items():
            self._draw_node(painter, node_id, position)
        if self.state in FALL_STATES:
            self._draw_fallen_person(painter)
        else:
            self._draw_walking_person(painter)
        self._draw_title(painter)

    def _draw_background(self, painter):
        left, top, side, _ = self.room_square()
        painter.fillRect(self.rect(), QColor(COLORS["map_background"]))
        painter.setBrush(QBrush(QColor(COLORS["background"])))
        painter.setPen(QPen(QColor(COLORS["border"]), 2.0))
        painter.drawRect(QRectF(left, top, side, side))

    def _draw_grid(self, painter):
        left, _, _, _ = self.room_square()
        grid_pen = QPen(QColor(COLORS["grid"]), 1.0, Qt.PenStyle.DashLine)
        axis_pen = QPen(QColor(COLORS["border_strong"]), 1.5, Qt.PenStyle.SolidLine)
        painter.setFont(QFont("Monospace", 8))

        half = ROOM_HALF_SIZE_M
        for meters in range(-int(half), int(half) + 1):
            top_point = self.to_pixels(meters, half)
            bottom_point = self.to_pixels(meters, -half)
            left_point = self.to_pixels(-half, meters)
            right_point = self.to_pixels(half, meters)

            painter.setPen(axis_pen if meters == 0 else grid_pen)
            painter.drawLine(top_point, bottom_point)
            painter.drawLine(left_point, right_point)

            painter.setPen(QColor(COLORS["dim"]))
            painter.drawText(int(bottom_point.x() - 12), int(bottom_point.y() + 15), f"{meters:+d}m")
            painter.drawText(int(left - 30), int(left_point.y() + 4), f"{meters:+d}m")

    def _draw_link(self, painter, link):
        _, _, _, scale = self.room_square()
        tx_x, tx_y = NODE_POSITIONS_M[link[0]]
        rx_x, rx_y = NODE_POSITIONS_M[link[1]]
        distance_m = math.hypot(rx_x - tx_x, rx_y - tx_y)

        tx_px = self.to_pixels(tx_x, tx_y)
        rx_px = self.to_pixels(rx_x, rx_y)
        center_px = self.to_pixels((tx_x + rx_x) / 2.0, (tx_y + rx_y) / 2.0)
        angle_deg = math.degrees(math.atan2(rx_px.y() - tx_px.y(), rx_px.x() - tx_px.x()))

        pulse = 0.5 + 0.5 * math.sin(self.pulse_phase + float(link[0]))
        alpha = max(20, min(230, int(35 + 180 * self.activity * pulse)))

        a1_px = (distance_m + WAVELENGTH_M / 2.0) / 2.0 * scale
        b1_px = 0.5 * math.sqrt(WAVELENGTH_M * distance_m + (WAVELENGTH_M ** 2) / 4.0) * scale
        a2_px = (distance_m + WAVELENGTH_M) / 2.0 * scale
        b2_px = 0.5 * math.sqrt(2.0 * WAVELENGTH_M * distance_m) * scale

        painter.save()
        painter.translate(center_px)
        painter.rotate(angle_deg)

        half_line_px = distance_m * scale / 2.0
        painter.setPen(QPen(with_alpha("cyan", int(40 + 80 * self.activity)), 1.2, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(-half_line_px, 0), QPointF(half_line_px, 0))

        painter.setBrush(QBrush(with_alpha("cyan", int(alpha * 0.18))))
        painter.setPen(QPen(with_alpha("cyan", alpha), 1.8))
        painter.drawEllipse(QRectF(-a1_px, -b1_px, 2.0 * a1_px, 2.0 * b1_px))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(with_alpha("accent", int(alpha * 0.4)), 1.0, Qt.PenStyle.DotLine))
        painter.drawEllipse(QRectF(-a2_px, -b2_px, 2.0 * a2_px, 2.0 * b2_px))

        painter.restore()

    def _draw_node(self, painter, node_id, position):
        center = self.to_pixels(*position)

        ring_px = 14.0 + 3.0 * math.sin(self.pulse_phase + node_id)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(with_alpha("accent", 120), 1.5))
        painter.drawEllipse(center, ring_px, ring_px)

        painter.setBrush(QBrush(QColor(COLORS["node"])))
        painter.setPen(QPen(QColor(COLORS["node_edge"]), 2.0))
        painter.drawEllipse(center, 8.0, 8.0)

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(COLORS["text_bright"]))
        painter.drawText(int(center.x() + 12), int(center.y() + 4), f"ESP32 #{node_id}")

    def _draw_walking_person(self, painter):
        center = self.to_pixels(self.x_m, self.y_m)

        glow = QRadialGradient(center, 30.0, center)
        glow.setColorAt(0.0, with_alpha("walker", 160))
        glow.setColorAt(0.5, with_alpha("walker", 60))
        glow.setColorAt(1.0, with_alpha("walker", 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 28.0, 28.0)

        painter.setBrush(QBrush(QColor(COLORS["walker"])))
        painter.setPen(QPen(QColor(COLORS["white"]), 2.0))
        painter.drawEllipse(center, 9.0, 9.0)

        self._draw_velocity_arrow(painter, center)

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(COLORS["walker_text"]))
        painter.drawText(int(center.x() - 35), int(center.y() + 24), f"OM ({self.x_m:+.2f}, {self.y_m:+.2f})")

    def _draw_velocity_arrow(self, painter, center):
        speed_m_s = math.hypot(self.vx_m_s, self.vy_m_s)
        if speed_m_s <= MIN_ARROW_SPEED_M_S:
            return
        direction_x = self.vx_m_s / speed_m_s
        direction_y = -self.vy_m_s / speed_m_s
        length_px = min(ARROW_MAX_PX, max(ARROW_MIN_PX, speed_m_s * ARROW_PX_PER_M_S))
        tip = QPointF(center.x() + direction_x * length_px, center.y() + direction_y * length_px)

        painter.setPen(QPen(QColor(COLORS["walker_light"]), 2.5, Qt.PenStyle.SolidLine))
        painter.drawLine(center, tip)

        angle = math.atan2(direction_y, direction_x)
        for side in (-0.5, 0.5):
            head = QPointF(
                tip.x() - ARROW_HEAD_PX * math.cos(angle + side),
                tip.y() - ARROW_HEAD_PX * math.sin(angle + side),
            )
            painter.drawLine(tip, head)

    def _draw_fallen_person(self, painter):
        center = self.to_pixels(self.x_m, self.y_m)

        for wave in range(2):
            radius_px = (int(self.pulse_phase * 18 + wave * 20) % 46) + 12
            alpha = max(0, int(220 - radius_px * 4.2))
            painter.setPen(QPen(with_alpha("red", alpha), 2.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, float(radius_px), float(radius_px))

        body_w, body_h = 60.0, 20.0
        body = QRectF(center.x() - body_w / 2.0, center.y() - body_h / 2.0, body_w, body_h)
        flash_on = int(self.pulse_phase * 4) % 2 == 0
        painter.setBrush(QBrush(QColor(COLORS["red_strong"] if flash_on else COLORS["red_darker"])))
        painter.setPen(QPen(QColor(COLORS["red_light"]), 2.2))
        painter.drawRoundedRect(body, 6.0, 6.0)

        painter.setBrush(QBrush(QColor(COLORS["white"])))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center.x() - 19.0, center.y()), 4.5, 4.5)

        banner_w, banner_h = 230.0, 24.0
        banner = QRectF(center.x() - banner_w / 2.0, center.y() - 38.0, banner_w, banner_h)
        painter.setBrush(QBrush(with_alpha("red_dark", 230)))
        painter.setPen(QPen(QColor(COLORS["red"]), 1.8))
        painter.drawRoundedRect(banner, 4.0, 4.0)

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(COLORS["warning_text"]))
        painter.drawText(banner, Qt.AlignmentFlag.AlignCenter, "⚠ CĂDERE DETECTATĂ / PERSOANĂ LA SOL")

    def _draw_title(self, painter):
        left, top, _, _ = self.room_square()
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor(COLORS["muted"]))
        painter.drawText(int(left + 8), int(top + 18), "HARTĂ CAMERĂ 2D - ZONE FRESNEL & POZIȚIE")
