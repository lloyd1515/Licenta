import argparse
import signal
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from csi.gui.main_window import MainWindow
from csi.packets import BAUD_RATE, DEFAULT_PORTS, REAL_FALL

DEFAULT_REPLAY = "DEFAULT"
DEFAULT_FPS = 50.0
SIGNAL_POLL_MS = 200


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sistem Inteligent de Monitorizare Ambientală Wi-Fi CSI — Desktop App (PyQt6)"
    )
    parser.add_argument(
        "--replay",
        nargs="?",
        const=DEFAULT_REPLAY,
        default=None,
        help=f"Rulează în mod Replay. Opțional specifică calea către fișierul .npz (implicit: {REAL_FALL.name})",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Pornește automat achiziția Live USB la lansare",
    )
    parser.add_argument(
        "--port",
        type=str,
        default=DEFAULT_PORTS[0],
        help=f"Port serial principal pentru nodul ESP32 (implicit: {DEFAULT_PORTS[0]})",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=BAUD_RATE,
        help=f"Baudrate port serial ESP32 (implicit: {BAUD_RATE})",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=DEFAULT_FPS,
        help=f"Frecvență țintă redare cadre (implicit: {DEFAULT_FPS} FPS)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("Wi-Fi CSI Sensing & Fall Detection")
    app.setOrganizationName("UTCN")

    signal_timer = QTimer()
    signal_timer.setInterval(SIGNAL_POLL_MS)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start()

    replay = args.replay is not None
    recording_path = Path(args.replay) if replay and args.replay != DEFAULT_REPLAY else REAL_FALL
    ports = (args.port, *(port for port in DEFAULT_PORTS if port != args.port))

    window = MainWindow(ports, args.baud, args.fps, recording_path)
    if replay:
        window.start_replay()
    elif args.live:
        window.start_live()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
