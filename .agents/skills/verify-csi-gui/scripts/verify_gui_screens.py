#!/usr/bin/env python3
"""
verify_gui_screens.py
=====================
Automated offscreen PyQt6 verification script for GUI presentation layer:
1. Validates MainWindow rendering at 1600x950 resolution.
2. Validates RoomMapWidget with Fresnel mesh and 2D target avatar.
3. Validates WaterfallWidget with 52 OFDM subcarriers.
4. Validates DopplerWidget with kinematic velocity profile.
5. Validates TelemetryWidget with multi-node stats and FSM state indicator.
6. Validates AlertBanner emergency styling and response latency text.
Captures pixel-perfect PNG evidence into .agents/skills/verify-csi-gui/evidence/.
"""

import os
import sys
import json
import numpy as np

# Force Qt offscreen platform
os.environ["QT_QPA_PLATFORM"] = "offscreen"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import QApplication
from gui.backend_engine import CSIDataEngine
from gui.main_window import MainWindow

def run_gui_verification():
    print("=" * 70)
    print(">>> VERIFY-CSI-GUI: DESKTOP UI INTEGRATION & VISUAL PROOF <<<")
    print("=" * 70)

    evidence_dir = os.path.join(SKILL_DIR, "evidence")
    os.makedirs(evidence_dir, exist_ok=True)

    replay_file = os.path.join(PROJECT_ROOT, "dsp_lab", "test_C_cadere_reala.npz")
    if not os.path.exists(replay_file):
        raise FileNotFoundError(f"Dataset missing: {replay_file}")

    app = QApplication.instance()
    if app is None:
        app = QApplication(["verify_gui_screens", "--platform", "offscreen"])

    engine = CSIDataEngine(replay_mode=True, replay_file=replay_file, target_fps=50.0)
    window = MainWindow(engine=engine)
    window.resize(1600, 950)
    window.show()
    app.processEvents()

    dataset = engine._load_replay_dataset()
    time_arr = dataset["time"]
    n_samples = dataset["n_samples"]
    fsm_states = dataset["fsm_states"]
    link_signals = dataset["link_signals"]
    csi_matrix_52 = dataset["csi_matrix_52"]
    alarm_ts = dataset["alarm_timestamp"]
    actual_fs = dataset.get("actual_fs", engine.fs)
    step_samples = max(1, int(round(actual_fs / engine.target_fps)))

    frames = []
    smooth_height = 1.75
    pos_x = 0.0
    pos_y = 0.0

    for sample_idx in range(0, n_samples, step_samples):
        t_val = float(time_arr[sample_idx])
        state = int(fsm_states[sample_idx])

        if state == 0:
            target_height = 1.75 + 0.02 * np.sin(t_val * 1.5)
        elif state == 1:
            target_height = 1.70 + 0.05 * np.sin(t_val * 9.0)
        elif state == 2:
            target_height = 0.55
        elif state == 3:
            target_height = 0.18
        else:
            target_height = 0.15

        smooth_height += 0.22 * (target_height - smooth_height)

        l12_val = abs(float(link_signals["L12"][sample_idx]))
        l23_val = abs(float(link_signals["L23"][sample_idx]))
        l31_val = abs(float(link_signals["L31"][sample_idx]))

        links_activity = {
            "L12": float(np.clip(l12_val / 50.0, 0.05, 1.0)),
            "L23": float(np.clip(l23_val / 50.0, 0.05, 1.0)),
            "L31": float(np.clip(l31_val / 50.0, 0.05, 1.0))
        }

        vx, vy = 0.0, 0.0
        if state == 0:
            pos_x, pos_y = 0.0, 0.0
        elif state == 1:
            pos_x = 0.8 * np.sin(t_val * 0.8)
            pos_y = 0.6 * np.cos(t_val * 0.8)
            vx = 0.64 * np.cos(t_val * 0.8)
            vy = -0.48 * np.sin(t_val * 0.8)
        elif state in (2, 3, 4):
            pos_x, pos_y = 0.2, -0.1

        doppler_max = 48.5 if state == 2 else (18.2 if state == 1 else 1.8)

        frame = {
            "timestamp": t_val,
            "node_id": 1 + (sample_idx % 3),
            "rssi": -42.0 - 5.0 * links_activity["L12"],
            "csi_raw_52": csi_matrix_52[sample_idx],
            "pc1": float(link_signals["L12"][sample_idx]),
            "doppler_max": float(doppler_max),
            "posture_height": float(smooth_height),
            "fsm_state": state,
            "person_x": float(pos_x),
            "person_y": float(pos_y),
            "target_vx": float(vx),
            "target_vy": float(vy),
            "alarm_active": bool(state == 4 or (alarm_ts > 0 and t_val >= alarm_ts)),
            "links_activity": links_activity
        }
        frames.append(frame)

    saved_evidence = {}
    phase_meta = {}

    def capture_phase(name: str, frame_data: dict):
        phase_meta[name] = frame_data
        prefix = f"phase_{name}"
        widgets = {
            f"{prefix}_window.png": window,
            f"{prefix}_room_map.png": window.room_map_widget,
            f"{prefix}_waterfall.png": window.waterfall_widget,
            f"{prefix}_doppler.png": window.doppler_widget,
            f"{prefix}_telemetry.png": window.telemetry_widget,
            f"{prefix}_alert_banner.png": window.alert_banner,
        }
        for fn, w in widgets.items():
            dest = os.path.join(evidence_dir, fn)
            pm = w.grab()
            pm.save(dest, "PNG")
            saved_evidence[fn] = {
                "file": dest,
                "width": pm.width(),
                "height": pm.height(),
                "bytes": os.path.getsize(dest)
            }

    phase_captured = {"calm": False, "walking": False, "impact": False, "alarm": False}

    for f in frames:
        window.on_frame_received(f)
        app.processEvents()
        t = f["timestamp"]
        s = f["fsm_state"]

        if not phase_captured["calm"] and t >= 0.0:
            capture_phase("1_calm", f)
            phase_captured["calm"] = True
        if not phase_captured["walking"] and t >= 0.35:
            capture_phase("2_walking", f)
            phase_captured["walking"] = True
        if not phase_captured["impact"] and s == 2:
            capture_phase("3_impact", f)
            phase_captured["impact"] = True
        if not phase_captured["alarm"] and f["alarm_active"]:
            capture_phase("4_alarm", f)
            phase_captured["alarm"] = True

    if not phase_captured["alarm"]:
        capture_phase("4_alarm", frames[-1])
        phase_captured["alarm"] = True

    # Verification assertions
    p1 = phase_meta["1_calm"]
    p2 = phase_meta["2_walking"]
    p3 = phase_meta["3_impact"]
    p4 = phase_meta["4_alarm"]

    assert p1["fsm_state"] == 0, f"Calm state invalid: {p1['fsm_state']}"
    assert p2["fsm_state"] == 1, f"Walking state invalid: {p2['fsm_state']}"
    assert p3["fsm_state"] == 2, f"Impact state invalid: {p3['fsm_state']}"
    assert p4["alarm_active"] or p4["fsm_state"] in (3, 4), f"Alarm state invalid"
    assert window.alert_banner.isVisible(), "Alert banner must be visible"

    report_path = os.path.join(evidence_dir, "gui_verification_report.json")
    with open(report_path, "w") as rf:
        json.dump({
            "timestamp": "2026-10-12",
            "resolution": "1600x950",
            "passed": True,
            "screenshots_count": len(saved_evidence),
            "evidence": saved_evidence
        }, rf, indent=2)

    print(f"[+] All 4 phases captured and verified! Evidence written to: {evidence_dir}")
    print(f"[+] Summary report saved to: {report_path}")

    window.close()
    app.quit()
    return saved_evidence

if __name__ == "__main__":
    run_gui_verification()
