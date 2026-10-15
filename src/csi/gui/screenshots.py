import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from csi.dsp import analyze_recording
from csi.fall_detector import FallState
from csi.gui.frames import frames_from_analysis
from csi.gui.main_window import MainWindow
from csi.packets import REAL_FALL, load_recording

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
WINDOW_SIZE = (1600, 950)
FEED_FPS = 50.0
MIN_PNG_BYTES = 1000
PHASES = (
    ("1_calm", FallState.CALM),
    ("2_walking", FallState.MOVING),
    ("3_impact", FallState.IMPACT),
    ("4_dormancy_alarm", FallState.ALARM),
)


def first_index(states, wanted):
    matches = [index for index, state in enumerate(states) if state == wanted]
    if not matches:
        raise RuntimeError(f"Recording never reaches {wanted.name}")
    return matches[0]


def main():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    app = QApplication.instance() or QApplication([])

    analysis = analyze_recording(load_recording(REAL_FALL))
    frames = frames_from_analysis(analysis)
    step = max(1, round(analysis.recording.rate_hz / FEED_FPS))
    capture_at = {first_index(analysis.detection.states, state): name for name, state in PHASES}

    window = MainWindow()
    window.resize(*WINDOW_SIZE)
    window.show()
    app.processEvents()

    phase_frames = {}
    for index, frame in enumerate(frames):
        if index not in capture_at and index % step:
            continue
        window.show_frame(frame)
        app.processEvents()
        if index not in capture_at:
            continue
        name = capture_at[index]
        phase_frames[name] = frame
        targets = {
            "window": window,
            "room_map": window.room_map,
            "waterfall": window.waterfall,
            "doppler": window.doppler_plot,
            "telemetry": window.status_panel,
            "alert_banner": window.alarm_banner,
        }
        for suffix, widget in targets.items():
            path = SCREENSHOTS_DIR / f"phase_{name}_{suffix}.png"
            if not widget.grab().save(str(path), "PNG"):
                raise RuntimeError(f"Failed to save screenshot: {path}")
            assert path.stat().st_size > MIN_PNG_BYTES, f"Screenshot too small: {path}"
        print(f"{name}: t={frame.time_s:.2f}s state={frame.state.name} height={frame.height_m:.2f}m")
        if len(phase_frames) == len(PHASES):
            break

    for name, state in PHASES:
        assert phase_frames[name].state == state, f"{name}: expected {state.name}, got {phase_frames[name].state.name}"
    assert window.alarm_banner.isVisible(), "Alarm banner is not visible in the alarm phase"
    assert phase_frames["1_calm"].height_m >= 1.65
    assert phase_frames["4_dormancy_alarm"].height_m <= 0.25
    print(f"Saved {len(list(SCREENSHOTS_DIR.glob('phase_*.png')))} screenshots in {SCREENSHOTS_DIR}")

    window.close()


if __name__ == "__main__":
    main()
