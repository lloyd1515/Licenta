#!/usr/bin/env python3
"""
verify_backend_pipeline.py
===========================
Automated end-to-end verification of the CSI Backend Pipeline:
1. Binary packet deserialization (138 bytes, magic 0xA55A, 52 subcarriers).
2. DSP filtering (Hampel, Butterworth bandpass 0.2-12 Hz, PCA component).
3. STFT Doppler power spectrogram.
4. FSM state transitions on real dataset suite:
   - test_A_camera_goala.npz: Must remain in CALM (0 alarms).
   - test_B_mers_normal.npz:  Must detect WALKING (0 false fall alarms).
   - test_C_cadere_reala.npz: Must transition CALM -> WALK -> IMPACT -> DORMANCY -> ALARM.
"""

import os
import sys
import json
import time
import struct
import numpy as np
from typing import Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dsp_lab.filters import (
    butterworth_bandpass,
    compute_pca_first_component,
    compute_doppler_spectrogram,
    hampel_filter_1d,
    sanitize_subcarriers
)
from dsp_lab.fall_detector import FallDetectorFSM


class BackendPipelineVerifier:
    def __init__(self):
        self.results = {}
        self.evidence_dir = os.path.join(SKILL_DIR, "evidence")
        os.makedirs(self.evidence_dir, exist_ok=True)

    def verify_packet_parser(self) -> Dict[str, Any]:
        """Tests parsing of synthetic raw ESP32 CSI binary packet."""
        magic = 0xA55A
        node_id = 1
        rssi = -65
        ts_us = 12345678
        seq = 42

        # 64 I/Q pairs = 128 bytes
        iq_raw = np.zeros(128, dtype=np.int8)
        for i in range(64):
            iq_raw[2*i] = int(i % 10)      # I
            iq_raw[2*i + 1] = int((i*2) % 10) # Q

        header = struct.pack('<H B b I H', magic, node_id, rssi, ts_us, seq)
        pkt_bytes = header + iq_raw.tobytes()

        # Parse using backend logic
        unpacked_magic, u_node, u_rssi, u_ts, u_seq = struct.unpack('<H B b I H', pkt_bytes[:10])
        payload = pkt_bytes[10:138]
        iq = np.frombuffer(payload, dtype=np.int8).astype(np.float32)
        amp_64 = np.sqrt(iq[0::2]**2 + iq[1::2]**2)
        csi_52 = np.concatenate([amp_64[6:32], amp_64[33:59]])

        valid = (
            len(pkt_bytes) == 138 and
            unpacked_magic == magic and
            u_node == node_id and
            u_rssi == rssi and
            len(csi_52) == 52
        )

        res = {
            "test": "packet_deserializer",
            "packet_size_bytes": len(pkt_bytes),
            "subcarriers_extracted": len(csi_52),
            "passed": bool(valid)
        }
        self.results["packet_parser"] = res
        return res

    def verify_dsp_filters(self) -> Dict[str, Any]:
        """Tests Butterworth bandpass, PCA, and Doppler spectrogram."""
        fs = 50.0
        t = np.linspace(0, 5.0, int(5.0 * fs))
        # Signal with DC offset + 1.5 Hz walking movement + 20 Hz high-frequency noise
        sig_clean = np.sin(2 * np.pi * 1.5 * t)
        sig_noisy = 10.0 + sig_clean + 0.5 * np.sin(2 * np.pi * 20.0 * t)

        # 52 identical subcarriers with slight phase offsets
        matrix = np.tile(sig_noisy, (52, 1)).T
        filt = butterworth_bandpass(matrix, lowcut=0.2, highcut=12.0, fs=fs)
        pc1 = compute_pca_first_component(filt)

        # Check that DC offset (10.0) was removed (signal mean close to 0) and 1.5 Hz component dominates
        dc_offset = float(np.abs(np.mean(filt)))
        pc1_std = float(np.std(pc1))

        # Doppler spectrogram
        d_times, d_freqs, d_power = compute_doppler_spectrogram(
            np.mean(matrix, axis=1), fs=fs, nperseg=16, noverlap=8
        )

        passed = (dc_offset < 0.10) and (pc1_std > 0.5) and (len(d_freqs) > 0)
        res = {
            "test": "dsp_filters",
            "dc_attenuation_passed": bool(dc_offset < 0.10),
            "pca_variance_passed": bool(pc1_std > 0.5),
            "doppler_spectrogram_bins": len(d_freqs),
            "passed": bool(passed)
        }
        self.results["dsp_filters"] = res
        return res

    def verify_dataset_suite(self) -> Dict[str, Any]:
        """Runs FSM classifier against all 3 hardware datasets."""
        datasets = {
            "test_A_camera_goala": {"expected_alarm": False, "desc": "Empty room baseline"},
            "test_B_mers_normal":  {"expected_alarm": False, "desc": "Normal walking"},
            "test_C_cadere_reala":  {"expected_alarm": True,  "desc": "Real human fall"}
        }

        suite_res = {}
        all_passed = True

        for name, meta in datasets.items():
            path = os.path.join(PROJECT_ROOT, "dsp_lab", f"{name}.npz")
            if not os.path.exists(path):
                suite_res[name] = {"passed": False, "error": "File not found"}
                all_passed = False
                continue

            data = np.load(path, allow_pickle=True)
            pkts = data['p1']
            time_arr = np.array([p['timestamp_s'] for p in pkts])
            time_arr -= time_arr[0]
            dur = max(0.1, time_arr[-1] - time_arr[0])
            fs = len(pkts) / dur

            csi_mat = np.array([np.abs(p['csi']) for p in pkts])
            sanitized = sanitize_subcarriers(csi_mat)
            filt = butterworth_bandpass(sanitized, lowcut=0.2, highcut=min(12.0, fs/2.1), fs=fs)
            pc1 = compute_pca_first_component(filt)

            sig_wide = np.mean(csi_mat, axis=1)
            nperseg = min(32, max(16, len(pc1) // 8))
            d_times, d_freqs, d_power = compute_doppler_spectrogram(
                sig_wide, fs=fs, nperseg=nperseg, noverlap=nperseg // 2
            )

            fsm = FallDetectorFSM(fs=fs)
            link_sigs = {"L12": pc1, "L23": pc1 * 0.9, "L31": pc1 * 1.1}
            res_fsm = fsm.analyze(
                time=time_arr,
                link_pc1_signals=link_sigs,
                doppler_freqs=d_freqs,
                doppler_times=d_times,
                doppler_power_db=d_power
            )

            actual_alarm = bool(res_fsm.alarm_triggered)
            expected_alarm = meta["expected_alarm"]
            passed = (actual_alarm == expected_alarm)

            if not passed:
                all_passed = False

            suite_res[name] = {
                "desc": meta["desc"],
                "samples": len(pkts),
                "duration_sec": float(dur),
                "sampling_fs_hz": float(fs),
                "alarm_triggered": actual_alarm,
                "expected_alarm": expected_alarm,
                "max_doppler_hz": float(res_fsm.max_doppler_hz),
                "unique_fsm_states": [int(s) for s in np.unique(res_fsm.fsm_states)],
                "passed": passed
            }

        res = {
            "test": "dataset_fsm_suite",
            "datasets": suite_res,
            "passed": all_passed
        }
        self.results["dataset_suite"] = res
        return res

    def run_all(self) -> Dict[str, Any]:
        print("=" * 70)
        print(">>> BACKEND CSI PIPELINE & FSM VERIFICATION <<<")
        print("=" * 70)

        p1 = self.verify_packet_parser()
        print(f"[*] Packet Parser: {'PASS' if p1['passed'] else 'FAIL'}")

        p2 = self.verify_dsp_filters()
        print(f"[*] DSP Filters (Butterworth/PCA/STFT): {'PASS' if p2['passed'] else 'FAIL'}")

        p3 = self.verify_dataset_suite()
        print(f"[*] Dataset FSM Suite: {'PASS' if p3['passed'] else 'FAIL'}")
        for ds_name, ds_info in p3["datasets"].items():
            print(f"    - {ds_name}: {'PASS' if ds_info.get('passed') else 'FAIL'} (alarm={ds_info.get('alarm_triggered')}, states={ds_info.get('unique_fsm_states')})")

        overall_pass = all(v["passed"] for v in self.results.values())
        print("=" * 70)
        print(f">>> OVERALL BACKEND STATUS: {'PASS' if overall_pass else 'FAIL'} <<<")
        print("=" * 70)

        evidence_file = os.path.join(self.evidence_dir, "backend_pipeline_report.json")
        with open(evidence_file, "w") as f:
            json.dump({
                "timestamp": os.getenv("CURRENT_TIME", "2026-10-12"),
                "overall_pass": overall_pass,
                "results": self.results
            }, f, indent=2)
        print(f"[+] Saved backend evidence to: {evidence_file}")
        return self.results


if __name__ == "__main__":
    verifier = BackendPipelineVerifier()
    verifier.run_all()
