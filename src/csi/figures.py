import sys
from pathlib import Path
from typing import NamedTuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from csi.dsp import (
    BAND_HIGH_HZ,
    BAND_LOW_HZ,
    Spectrogram,
    analyze_recording,
    bandpass,
    motion_signal,
    remove_outliers,
    spectrogram,
)
from csi.fall_detector import IMPACT_SLOPE, SLOPE_ACTIVE, STATE_LABELS, Detection, detect_fall, normalized_slopes
from csi.localization import track_with_noisy_ranges
from csi.packets import EMPTY_ROOM, REAL_FALL, WALKING, load_recording
from csi.room import DOPPLER_REFERENCE_HZ, LINKS, NODE_POSITIONS_M, link_name
from csi.simulator import FALL_XY_M, Trajectory, make_trajectory, simulate_csi

FIGURES_DIR = Path(__file__).parent / "plots"
SYNTHETIC_DPI = 200
REAL_DPI = 300
BACKGROUND = "#0d1117"
CYAN = "#00f0ff"
GREEN = "#00ff88"
AMBER = "#ffb700"
RED = "#ff2a55"
LINK_COLORS = (CYAN, GREEN, AMBER)
STATE_TICKS = [f"{state.value}: {label}" for state, label in STATE_LABELS.items()]
SPECTROGRAM_WINDOW = 64
SPECTROGRAM_OVERLAP = 56
SPECTROGRAM_SUBCARRIER = 10
SPECTROGRAM_RANGE_DB = (-25, 15)
SPECTROGRAM_MAX_HZ = 70.0
REAL_SPECTROGRAM_MAX_HZ = 20.0
TRACK_STEP = 10
LEGEND_ALPHA = 0.8


def apply_style():
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "font.sans-serif": "DejaVu Sans",
            "font.size": 10,
            "figure.facecolor": BACKGROUND,
            "axes.edgecolor": "#334455",
            "axes.linewidth": 1.2,
            "grid.color": "#223344",
            "grid.linestyle": "--",
            "grid.alpha": 0.5,
        }
    )


def save(fig, name, dpi):
    FIGURES_DIR.mkdir(exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[+] Salvat: {path}")


def style_axis(ax, title, ylabel, title_color="white", legend_loc="upper right", legend_alpha=LEGEND_ALPHA, **title_style):
    ax.set_title(title, color=title_color, **{"fontsize": 11, **title_style})
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc=legend_loc, framealpha=legend_alpha)


def plot_state_steps(ax, times_s, states, color):
    ax.step(times_s, states, where="post", color=color, linewidth=2.0)
    ax.set_yticks(range(len(STATE_TICKS)))
    ax.set_yticklabels(STATE_TICKS)


class SyntheticScenario(NamedTuple):
    trajectory: Trajectory
    raw: np.ndarray
    cleaned: np.ndarray
    motion: dict
    spec: Spectrogram
    detection: Detection
    rate_hz: float


def synthetic_scenario():
    trajectory = make_trajectory()
    simulated = simulate_csi(trajectory, snr_db=22.0, add_spikes=True)
    rate_hz = simulated.rate_hz
    raw = {name: np.abs(csi) for name, csi in simulated.csi_by_link.items()}
    cleaned = {name: remove_outliers(amplitude) for name, amplitude in raw.items()}
    motion = {name: motion_signal(bandpass(amplitude, rate_hz)) for name, amplitude in cleaned.items()}
    first_link = link_name(LINKS[0])
    spec = spectrogram(cleaned[first_link][:, SPECTROGRAM_SUBCARRIER], rate_hz, SPECTROGRAM_WINDOW, SPECTROGRAM_OVERLAP)
    detection = detect_fall(trajectory.times_s, motion, rate_hz)
    return SyntheticScenario(trajectory, raw[first_link], cleaned[first_link], motion, spec, detection, rate_hz)


def plot_raw_vs_filtered(trajectory, raw, cleaned, motion, impact_time_s):
    times_s = trajectory.times_s
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(times_s, raw[:, ::5], alpha=0.4, linewidth=0.8)
    style_axis(axes[0], "1. Amplitudine CSI Brută pe Subpurtătoare (Include Spike-uri LNA & Zgomot)", "Amplitudine (L1-2)", CYAN)
    axes[1].plot(times_s, cleaned[:, ::5], alpha=0.5, linewidth=0.8)
    style_axis(axes[1], "2. Amplitudine după Filtru Hampel (Outlier-uri LNA Eliminate)", "Amplitudine Hampel", GREEN)
    for (name, signal), color in zip(motion.items(), LINK_COLORS):
        axes[2].plot(times_s, signal, label=name, color=color, linewidth=1.5)
    axes[2].axvline(impact_time_s, color=RED, linestyle="--", linewidth=1.8, label=f"Impact Cădere (t={impact_time_s:.0f}s)")
    axes[2].set_xlabel("Timp (secunde)")
    style_axis(axes[2], "3. Semnal PC1 Filtrat pe Cele 3 Legături (Colaps Simultana la Cădere)", "Magnitudine PC1", AMBER)
    fig.tight_layout()
    save(fig, "1_raw_vs_filtered_csi.png", SYNTHETIC_DPI)


def annotate_box(ax, x, y, text, color, face, **kwargs):
    ax.text(x, y, text, color=color, fontsize=10, bbox=dict(boxstyle="round", facecolor=face, alpha=0.8), **kwargs)


def plot_synthetic_spectrogram(spec, impact_time_s):
    fig, ax = plt.subplots(figsize=(11, 5))
    mesh = ax.pcolormesh(
        spec.times_s, spec.freqs_hz, spec.power_db, shading="gouraud", cmap="plasma",
        vmin=SPECTROGRAM_RANGE_DB[0], vmax=SPECTROGRAM_RANGE_DB[1],
    )
    colorbar = fig.colorbar(mesh, ax=ax, label="Putere Doppler (dB)")
    colorbar.ax.yaxis.label.set_color("white")
    colorbar.ax.tick_params(colors="white")
    ax.axvline(impact_time_s, color=GREEN, linestyle="--", linewidth=1.8, label="Impact Cădere")
    ax.axhline(DOPPLER_REFERENCE_HZ, color=RED, linestyle=":", linewidth=1.5, label=f"Prag Critic Cădere ({DOPPLER_REFERENCE_HZ:.0f} Hz)")
    annotate_box(ax, 5.5, 20.0, "Mers Normal\n(10 - 22 Hz)", "white", "#1e222d")
    annotate_box(ax, 10.2, 50.0, "VÂRF DOPPLER CĂDERE\n(> 45 Hz, < 400 ms)", "#ff5555", "#2d1e22", weight="bold")
    annotate_box(ax, 14.0, 8.0, "Imobilitate la Sol\n(~0 Hz)", CYAN, "#1e222d")
    ax.set_ylim(0, SPECTROGRAM_MAX_HZ)
    ax.set_xlabel("Timp (secunde)")
    style_axis(ax, "Spectrogramă Micro-Doppler STFT: Mers Normal vs Impact Cădere vs Imobilitate", "Deplasare Doppler (Hz)", CYAN, fontsize=12)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    save(fig, "2_doppler_spectrogram.png", SYNTHETIC_DPI)


def plot_trajectory(trajectory):
    track = track_with_noisy_ranges(trajectory, step=TRACK_STEP)
    fig, ax = plt.subplots(figsize=(8, 8))
    for node_id, (x, y) in NODE_POSITIONS_M.items():
        ax.scatter(x, y, s=180, color=CYAN, edgecolors="white", linewidth=1.5, zorder=5)
        ax.text(x, y + 0.25, f"ESP32 Nod {node_id}", color=CYAN, fontsize=10, weight="bold", ha="center")
    for tx, rx in LINKS:
        (x1, y1), (x2, y2) = NODE_POSITIONS_M[tx], NODE_POSITIONS_M[rx]
        ax.plot([x1, x2], [y1, y2], color="#334466", linestyle="-", linewidth=2.0, alpha=0.6)
    ax.plot(trajectory.x_m, trajectory.y_m, color="#ffffff", linestyle="--", linewidth=1.8, label="Traiectorie Reală (Ground Truth)")
    ax.scatter(track.x_m, track.y_m, color="#ffaa00", s=25, alpha=0.7, label=f"Estimare Fresnel (RMSE = {track.rmse_m:.2f} m)")
    ax.scatter(*FALL_XY_M, s=250, color="#ff0033", marker="X", edgecolors="white", linewidth=2, zorder=6, label=f"Locație Cădere Sol ({FALL_XY_M[0]}, {FALL_XY_M[1]})")
    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-3.0, 3.0)
    ax.set_aspect("equal")
    ax.set_xlabel("Coordonata X (metri)")
    style_axis(ax, f"Cartografiere Radio Pasivă 2D (Triunghi 3x ESP32)\nEroare Medie: {track.rmse_m * 100:.1f} cm", "Coordonata Y (metri)", GREEN, "lower left", fontsize=12)
    fig.tight_layout()
    save(fig, "3_trajectory_cartography.png", SYNTHETIC_DPI)


def plot_synthetic_telemetry(trajectory, motion, detection, rate_hz):
    times_s = trajectory.times_s
    impact_time_s = times_s[trajectory.fall_start_index]
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    for (name, slope), color in zip(normalized_slopes(motion, rate_hz).items(), LINK_COLORS):
        axes[0].plot(times_s, slope, label=f"|dA/dt| {name}", color=color, linewidth=1.2)
    axes[0].axhline(SLOPE_ACTIVE, color=AMBER, linestyle="--", linewidth=1.5, label=f"Prag Legătură Activă ({SLOPE_ACTIVE})")
    axes[0].axhline(IMPACT_SLOPE, color=RED, linestyle="--", linewidth=1.5, label=f"Prag Derivată Impact ({IMPACT_SLOPE})")
    axes[0].axvline(impact_time_s, color="#ff0033", linestyle=":", linewidth=1.5)
    style_axis(axes[0], "Viteza de Scădere a Anvelopei pe Fiecare Legătură (|dA/dt|)", "Derivată Instantanee", CYAN)
    plot_state_steps(axes[1], times_s, detection.states, "#ff0033")
    if detection.alarm:
        axes[1].axvline(detection.alarm_time_s, color=GREEN, linestyle="-", linewidth=2.0, label=f"Alarmă Confirmată (t = {detection.alarm_time_s:.2f} s)")
    axes[1].set_xlabel("Timp (secunde)")
    style_axis(axes[1], "Evoluția Stărilor Automatului FSM de Decizie", "Stare FSM", GREEN, "lower right")
    fig.tight_layout()
    save(fig, "4_fsm_decision_telemetry.png", SYNTHETIC_DPI)


def make_synthetic_figures():
    scenario = synthetic_scenario()
    trajectory = scenario.trajectory
    impact_time_s = trajectory.times_s[trajectory.fall_start_index]
    plot_raw_vs_filtered(trajectory, scenario.raw, scenario.cleaned, scenario.motion, impact_time_s)
    plot_synthetic_spectrogram(scenario.spec, impact_time_s)
    plot_trajectory(trajectory)
    plot_synthetic_telemetry(trajectory, scenario.motion, scenario.detection, scenario.rate_hz)


def plot_abc_comparison(analyses):
    fig, axes = plt.subplots(3, 3, figsize=(16, 11), constrained_layout=True)
    titles = (
        ("Test A: Cameră Goală (Liniște RF)", "#38BDF8"),
        ("Test B: Mers Normal în Încăpere", "#34D399"),
        ("Test C: Cădere Reală + Imobilitate", "#F87171"),
    )
    for column, (analysis, (title, color)) in enumerate(zip(analyses, titles)):
        recording = analysis.recording
        times_s = recording.times_s
        image = axes[0, column].imshow(
            recording.amplitude.T, aspect="auto", origin="lower", extent=[times_s[0], times_s[-1], 0, 52], cmap="plasma"
        )
        axes[0, column].set_title(title, fontsize=12, fontweight="bold", color=color, pad=8)
        axes[0, column].set_ylabel("Index Subpurtătoare [0..51]")
        if column == 0:
            fig.colorbar(image, ax=axes[0, column], orientation="vertical", label="Amplitudine CSI")
        axes[1, column].plot(times_s, analysis.motion, color=color, linewidth=1.5, label="Componenta Principală (PC1)")
        axes[1, column].set_ylabel("Amplitudine PC1 [u.a.]")
        axes[1, column].grid(True)
        axes[1, column].legend(loc="upper right", framealpha=0.4)
        variance = np.var(recording.amplitude, axis=0)
        mean_variance = np.mean(variance)
        axes[2, column].bar(range(len(variance)), variance, color=color, alpha=0.7, edgecolor="none")
        axes[2, column].axhline(mean_variance, color="#FBBF24", linestyle="--", linewidth=1.2, label=f"Medie $\\sigma^2 = {mean_variance:.1f}$")
        axes[2, column].set_xlabel("Timp [secunde] / Index Subpurtătoare")
        axes[2, column].set_ylabel("Varianță CSI $\\sigma^2$")
        axes[2, column].set_ylim(0, max(np.max(variance) * 1.2, 50.0))
        axes[2, column].grid(True)
        axes[2, column].legend(loc="upper right", framealpha=0.4)
    save(fig, "5_real_hardware_abc_comparison.png", REAL_DPI)


def plot_real_spectrogram(analysis):
    recording = analysis.recording
    detection = analysis.detection
    spec = analysis.spectrogram
    mean_amplitude = np.mean(recording.amplitude, axis=1)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, constrained_layout=True)
    ax1.plot(recording.times_s, mean_amplitude, color="#60A5FA", linewidth=1.4, label="Amplitudine Medie Canal CSI")
    ax1.axvline(detection.impact_time_s, color="#EF4444", linestyle="--", linewidth=1.8, label=f"Impact Fizic ($t = {detection.impact_time_s:.2f}\\text{{ s}}$)")
    ax1.axvspan(detection.impact_time_s, detection.alarm_time_s, color="#F59E0B", alpha=0.15, label=f"Fereastră Imobilitate (${detection.latency_s:.2f}\\text{{ s}}$)")
    ax1.axvline(detection.alarm_time_s, color="#10B981", linestyle="-", linewidth=2.0, label=f"Alarmă Confirmată ($t = {detection.alarm_time_s:.2f}\\text{{ s}}$)")
    style_axis(ax1, "Scenariu Experimental Real: Impact Cădere și Imobilitate Post-Colaps (Test C)", "Amplitudine [u.a.]", legend_alpha=0.6, fontsize=13, fontweight="bold", pad=10)
    image = ax2.pcolormesh(spec.times_s, spec.freqs_hz, spec.power_db, shading="gouraud", cmap="magma")
    ax2.axhline(BAND_HIGH_HZ, color="#F87171", linestyle=":", linewidth=1.5, label=f"Limită Filtru Trece-Bandă ({BAND_LOW_HZ}-{BAND_HIGH_HZ:.0f} Hz)")
    ax2.set_xlabel("Timp [secunde]")
    ax2.set_ylim(0, min(REAL_SPECTROGRAM_MAX_HZ, recording.rate_hz / 2.0))
    style_axis(ax2, "", "Frecvență Doppler [Hz]", legend_alpha=0.6)
    fig.colorbar(image, ax=ax2, orientation="horizontal", pad=0.08, label="Densitate Spectrală de Putere [dB]")
    save(fig, "6_real_fall_doppler_spectrogram.png", REAL_DPI)


def plot_real_validation(analysis):
    times_s = analysis.recording.times_s
    detection = analysis.detection
    slope = normalized_slopes({"node": analysis.motion}, analysis.recording.rate_hz)["node"]
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9), sharex=True, constrained_layout=True)
    ax1.plot(times_s, analysis.motion, label="Nod ESP32", color=LINK_COLORS[0], linewidth=1.4)
    style_axis(ax1, "Validare FSM pe Hardware Real: Pante de Colaps și Latență de Decizie", "Semnal PC1 [u.a.]", legend_alpha=0.5, fontsize=13, fontweight="bold", pad=10)
    ax2.plot(times_s, slope, label="|dA/dt| Nod", color=LINK_COLORS[0], linewidth=1.2, alpha=0.85)
    ax2.axhline(SLOPE_ACTIVE, color="#EF4444", linestyle="--", linewidth=1.5, label=f"Prag Legătură Activă ({SLOPE_ACTIVE})")
    ax2.axhline(IMPACT_SLOPE, color="#FBBF24", linestyle="--", linewidth=1.5, label=f"Prag Derivată Impact ({IMPACT_SLOPE})")
    ax2.set_ylim(0, max(np.max(slope) * 1.2, SLOPE_ACTIVE * 2))
    style_axis(ax2, "", "Viteză de Variație |dA/dt|", legend_alpha=0.5)
    plot_state_steps(ax3, times_s, detection.states, "#F43F5E")
    ax3.set_ylim(-0.5, len(STATE_TICKS) - 0.5)
    ax3.set_xlabel("Timp [secunde]")
    if detection.alarm:
        ax3.axvspan(detection.impact_time_s, detection.alarm_time_s, color="#EF4444", alpha=0.2, label=f"Latență Decizie: {detection.latency_s:.2f} s")
        ax3.annotate(
            f"ALARMĂ CONFIRMATĂ!\nLatență = {detection.latency_s:.2f} s",
            xy=(detection.alarm_time_s, 4),
            xytext=(detection.alarm_time_s + 1.0, 3.2),
            arrowprops=dict(facecolor="#10B981", edgecolor="none", shrink=0.08),
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#10B981", linewidth=1.5),
            color="#10B981",
            fontweight="bold",
        )
    style_axis(ax3, "", "Stare FSM", legend_alpha=0.5)
    save(fig, "7_real_fall_fsm_validation.png", REAL_DPI)


def make_real_figures():
    analyses = [analyze_recording(load_recording(path)) for path in (EMPTY_ROOM, WALKING, REAL_FALL)]
    plot_abc_comparison(analyses)
    plot_real_spectrogram(analyses[2])
    plot_real_validation(analyses[2])


def main(argv):
    which = argv[0] if argv else "all"
    if which not in ("all", "synthetic", "real"):
        raise SystemExit("usage: python -m csi.figures [synthetic|real]")
    apply_style()
    if which in ("all", "synthetic"):
        make_synthetic_figures()
    if which in ("all", "real"):
        make_real_figures()


if __name__ == "__main__":
    main(sys.argv[1:])
