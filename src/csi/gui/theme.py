from string import Template
from typing import NamedTuple

from csi.fall_detector import FallState

COLORS = {
    "background": "#0b0f19",
    "map_background": "#080d1a",
    "surface": "#111827",
    "surface_raised": "#1f2937",
    "top_bar": "#0f172a",
    "border": "#1e293b",
    "border_strong": "#334155",
    "divider": "#374151",
    "grid": "#151e32",
    "text": "#e2e8f0",
    "text_bright": "#f8fafc",
    "muted": "#94a3b8",
    "dim": "#64748b",
    "plot_foreground": "#9ca3af",
    "accent": "#38bdf8",
    "cyan": "#06b6d4",
    "cyan_dark": "#0891b2",
    "green": "#10b981",
    "green_dark": "#059669",
    "walker": "#22c55e",
    "walker_light": "#4ade80",
    "walker_text": "#86efac",
    "red": "#ef4444",
    "red_strong": "#dc2626",
    "red_dark": "#991b1b",
    "red_darker": "#7f1d1d",
    "red_background": "#450a0a",
    "red_light": "#fca5a5",
    "node": "#0284c7",
    "node_edge": "#e0f2fe",
    "warning_text": "#fef08a",
    "amber": "#f59e0b",
    "violet": "#a78bfa",
    "mint": "#34d399",
    "yellow": "#fbbf24",
    "white": "#ffffff",
}


class StateColors(NamedTuple):
    background: str
    foreground: str
    border: str


STATE_COLORS = {
    FallState.CALM: StateColors("#334155", "#f1f5f9", "#64748b"),
    FallState.MOVING: StateColors("#1d4ed8", "#ffffff", "#3b82f6"),
    FallState.IMPACT: StateColors("#ea580c", "#ffffff", "#f97316"),
    FallState.CHECKING_STILL: StateColors("#ca8a04", "#ffffff", "#eab308"),
    FallState.ALARM: StateColors("#dc2626", "#ffffff", "#ef4444"),
}

STYLESHEET = Template(
    """
QMainWindow {
    background-color: $background;
}

QWidget {
    color: $text;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

QFrame#PanelFrame {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 8px;
}

QFrame#PanelHeader {
    background-color: $surface_raised;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom: 1px solid $divider;
    padding: 6px 12px;
}

QLabel#PanelTitle {
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.8px;
    color: $accent;
    text-transform: uppercase;
}

QFrame#TopBar {
    background-color: $top_bar;
    border-bottom: 1px solid $border;
    padding: 8px 16px;
}

QLabel#AppTitle {
    font-size: 16px;
    font-weight: 800;
    color: $text_bright;
    letter-spacing: 0.5px;
}

QLabel#AppSubtitle {
    font-size: 11px;
    font-weight: 500;
    color: $cyan;
}

QLabel#Badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QLabel#MetricBadge {
    background-color: $surface;
    color: $accent;
    border: 1px solid $border;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
}

QSpinBox {
    background-color: $border;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 5px 12px;
    color: $text_bright;
    font-weight: 600;
    min-width: 140px;
}

QPushButton#ToggleLive, QPushButton#ToggleReplay {
    background-color: $border;
    border: 1px solid $border_strong;
    border-radius: 6px;
    color: $muted;
    font-weight: 700;
    padding: 6px 14px;
}

QPushButton#ToggleLive:checked {
    background-color: rgba(16, 185, 129, 0.2);
    border: 1px solid $green;
    color: $green;
}

QPushButton#ToggleReplay:checked {
    background-color: rgba(6, 182, 212, 0.2);
    border: 1px solid $cyan;
    color: $cyan;
}

QFrame#AlertBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 $red_dark, stop:0.5 $red_strong, stop:1 $red_dark);
    border: 2px solid $red;
    border-radius: 8px;
    margin: 4px 8px 8px 8px;
    padding: 8px 16px;
}

QLabel#AlertText {
    color: $white;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.6px;
}

QPushButton#AlertResetButton {
    background-color: $red_darker;
    color: $white;
    border: 2px solid $red_light;
    border-radius: 6px;
    font-weight: 800;
    padding: 6px 18px;
    text-transform: uppercase;
    font-size: 12px;
}

QPushButton#AlertResetButton:hover {
    background-color: $red_dark;
    border-color: $white;
}

QSplitter::handle {
    background-color: $border;
    width: 3px;
    height: 3px;
}

QStatusBar {
    background-color: $background;
    border-top: 1px solid $border;
    color: $dim;
    font-size: 11px;
}
"""
).substitute(COLORS)


def connection_badge_style(background, color, border):
    return (
        f"background-color: {background}; color: {color}; border: 1px solid {border}; "
        "padding: 5px 12px; border-radius: 6px; font-weight: 700;"
    )


def doppler_label_style(color, background, border):
    return (
        f"QLabel {{ color: {color}; font-family: 'Segoe UI', Monospace; font-size: 12px; "
        f"font-weight: bold; background-color: {background}; border: 1px solid {border}; "
        "border-radius: 5px; padding: 4px 8px; }"
    )


def fall_state_badge_style(background, colors):
    return (
        f"QLabel {{ background-color: {background}; color: {colors.foreground}; "
        f"border: 2px solid {colors.border}; border-radius: 8px; font-size: 13px; "
        "font-weight: bold; padding: 6px; }"
    )


def card_value_style(color):
    return f"color: {color}; font-size: 13px; font-weight: bold; font-family: Monospace;"


BADGE_OFF = connection_badge_style(COLORS["border"], COLORS["muted"], COLORS["border_strong"])
BADGE_REPLAY = connection_badge_style("rgba(6, 182, 212, 0.2)", COLORS["cyan"], COLORS["cyan_dark"])
BADGE_LIVE = connection_badge_style("rgba(16, 185, 129, 0.2)", COLORS["green"], COLORS["green_dark"])

DOPPLER_LABEL_NORMAL = doppler_label_style(COLORS["accent"], COLORS["background"], COLORS["border"])
DOPPLER_LABEL_CRITICAL = doppler_label_style(COLORS["red_light"], COLORS["red_background"], COLORS["red_strong"])

CARD_STYLE = (
    f"QFrame {{ background-color: {COLORS['background']}; border: 1px solid {COLORS['border']}; "
    "border-radius: 6px; padding: 6px; }"
)
CARD_TITLE_STYLE = f"color: {COLORS['dim']}; font-size: 9px; font-weight: bold;"
SECTION_TITLE_STYLE = f"color: {COLORS['muted']}; font-weight: bold; font-size: 11px;"
