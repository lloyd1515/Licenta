# Wi-Fi CSI Sensing & Fall Detection: Master Video Production Specification
**Synthesized Arena Deliverable: Candidate 1 (Base) + Candidate 2 (Audio & NLE) + Candidate 3 (Motion Graphics)**  
**Version:** 1.0.0-PROD  
**Target Output:** 4:30 Master Explainer Video (1920x1080 @ 30.000 FPS, ITU-R BT.709, -14.0 LUFS)  
**Tools:** FilmCraft MCP (NLE Timeline Assembly), EffectCraft MCP (Motion Graphics), diagram-tour & Remotion (Visual Sources)

---

## 1. Executive Summary & Master Narrative Arc

This specification governs the production of the official technical explainer video for the Wi-Fi CSI passive sensing and fall detection system developed at UTCN. The video solves the critical audience retention problems of academic software walkthroughs by deploying a battle-tested four-pillar framework:
1. **The Veritasium Cold Open:** Hook viewers within 15 seconds with the privacy paradox (elderly domestic falls occur in private spaces where cameras are forbidden and wearables are abandoned) and the immediate technical punchline ($3\times\ \$5$ ESP32 microcontrollers detecting the fall in under 400 milliseconds).
2. **The 3Blue1Brown Physical Intuition:** Demystify electromagnetic waves as a "52-string radio harp" disturbed by human dielectric water mass ($\varepsilon_r \approx 50$), with free-fall gravitational acceleration creating an unmistakable 48.5 Hz Doppler spike versus 15–22 Hz walking.
3. **The Fireship Kinetic Cadence:** Enforce the 5-second dynamic pacing rule with shot durations $\le 4.8$ seconds, constantly cutting between the Graphviz architecture map, live PyQt6 telemetry screenshots, and 3D Fresnel wave physics.
4. **The Computerphile Empirical Rigor:** Ground every claim in repository source code (`src/firmware/`, `src/dsp_lab/`, `src/gui/`), physical dataset benchmarks (`test_A`, `test_B`, `test_C_cadere_reala.npz`), and automated headless QTest evidence (24/24 screenshots).

---

## 2. Broadcast & Audio Engineering Compliance (Grafted from Candidate 2)

* **Integrated Loudness ($I_{norm}$):** $-14.0\,\text{LUFS} \pm 0.5\,\text{LU}$ (conforming to YouTube Loudness Normalization).
* **True Peak Ceiling ($TP_{max}$):** $-1.0\,\text{dBTP}$ across all stems to eliminate inter-sample clipping during lossy AAC/Opus transcoding.
* **Momentary & Short-Term Ceilings:** $M_{max} = -11.0\,\text{LUFS}$ (400 ms window), $S_{max} = -13.0\,\text{LUFS}$ (3.0 s sliding window).
* **Loudness Range (LRA):** Target $8.0\,\text{LU} \pm 2.0\,\text{LU}$ for optimal mobile intelligibility.
* **High-Precision Timebase:** Professional 64-bit integer tick clock:
  $$\text{Ticks per Second} = 254{,}016{,}000{,}000$$
  $$\text{Master Duration (270.0s @ 30.000 fps)} = 68{,}584{,}320{,}000{,}000\,\text{ticks} \quad (8{,}100\,\text{frames})$$
* **Dynamic Sidechain Auto-Ducking Envelope:**
  * Track A1 (Speech): Gated at $-16.0\,\text{LUFS}$.
  * Track A2 (Ambient Bed): Resting at $-22.0\,\text{LUFS}$; dynamically attenuated to $-28.0\,\text{LUFS}$ ($-6.0\,\text{dB}$ gain offset) during speech.
  * Time Constants: Attack $40\,\text{ms}$, Hold $250\,\text{ms}$, Release $650\,\text{ms}$.
  * EQ Deconfliction: Voiceover HPF at 80 Hz, notch at 310 Hz, presence boost at 4.2 kHz; Music bed carved at 2.2 kHz with $12\,\text{dB/oct}$ roll-off above 12 kHz.
* **SMPTE ST 2046-1 Safe Areas:**
  * Action Safe (93%): $1786 \times 1004\,\text{px}$.
  * Title Safe (90%): $1728 \times 972\,\text{px}$.
  * Mobile UI Buffer: All lower thirds and critical telemetry constrained above $y = 939\,\text{px}$ (141px bottom clearance) to clear YouTube player seekbars and scrub thumbnails.

---

## 3. Dark Industrial Motion Design System (Grafted from Candidate 3)

### 3.1 Color Token Architecture (EffectCraft Normalized RGBA Vectors)
* `color.bg.void`: `[0.043, 0.059, 0.098, 1.0]` (`#0B0F19`) — Base canvas obsidian void.
* `color.surface.panel`: `[0.067, 0.094, 0.153, 1.0]` (`#111827`) — Carbon slate panel backing.
* `color.surface.elevated`: `[0.118, 0.161, 0.231, 1.0]` (`#1E293B`) — Elevated active node fill & guide grid.
* `color.border.subtle`: `[0.200, 0.255, 0.333, 1.0]` (`#334155`) — 1px hairline panel borders.
* `color.accent.cyan`: `[0.220, 0.741, 0.973, 1.0]` (`#38BDF8`) — 2.4 GHz RF carrier, telemetry baseline.
* `color.alarm.red`: `[0.937, 0.267, 0.267, 1.0]` (`#EF4444`) — Fall impact, Doppler > 35 Hz peak.
* `color.pass.green`: `[0.063, 0.725, 0.506, 1.0]` (`#10B981`) — Calm baseline, test assertion pass.
* `color.dsp.violet`: `[0.545, 0.361, 0.965, 1.0]` (`#8B5CF6`) — Hampel MAD, Butterworth, PCA.
* `color.ingest.indigo`: `[0.388, 0.400, 0.945, 1.0]` (`#6366F1`) — UART binary framing, 921,600 baud.

### 3.2 Typography & OpenType Hierarchy
* **Display Titles:** Inter Display 700 (Bold), 56px, tracking -0.02em, fill `#F8FAFC`.
* **Technical Subheads & Symbols:** JetBrains Mono 500/700, 20–22px, tracking +0.06em, fill `#38BDF8`.
* **Telemetry Counters:** JetBrains Mono 700 with tabular figures (`tnum`, `zero`) preventing horizontal digit jitter.

### 3.3 Motion Curves & Visual FX Stack
* **Apple Snappy Easing:** `cubic-bezier(0.16, 1.0, 0.3, 1.0)` (0.45s duration) on all UI transitions and camera zooms.
* **Breathing Reticles:** 4 corner L-brackets on active Graphviz clusters with breathing glow ($I(t) = I_0 + A\sin(\pi t)$) and automated 25% opacity / 4px blur dimming of inactive clusters.
* **Damped Impact Shockwave:** $S(t) = S_{\max} e^{-4.5t} \cos(18\pi t)$ triggered on screen at the 2:35 fall event.
* **3D Fresnel Particle World:** `ec.sim.ccparticleworld` vortex configuration visualizing RF scattering.

---

## 4. Multi-Track Timeline & B-Roll EDL (270.0s Master)

### 4.1 Track Hierarchy
* **Track V3 (Titles & Motion Overlays):** EffectCraft lower-third badges, focal reticles, impact alert ribbons, and CTA cards.
* **Track V2 (B-Roll Compositing):** 24 PyQt6 GUI screenshots (`src/gui/screenshots/`), 7 DSP analytical plots (`src/dsp_lab/plots/`), and 3D Remotion WebGL simulations (scaled to 80% with cyan borders or full-screen).
* **Track V1 (Base Architecture Anchor):** Continuous Graphviz diagram tour render providing persistent spatial orientation.
* **Track A1 (Dialogue Master):** Studio English narration speech, gated at -16.0 LUFS.
* **Track A2 (Ambient Music Bed):** Cyberpunk electronic drone, resting at -22.0 LUFS, ducked to -28.0 LUFS.

### 4.2 Scene-by-Scene Timeline & Cue Sheet

| Scene | Timecode | Duration | Primary Visual (V1/V2) | V3 Motion GFX & Telemetry | Audio Cues (A1/A2) |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **0. Cold Hook** | 0:00–0:18 | 18s | Glitched CCTV $\to$ Remotion 3D Fall $\to$ Doppler 48.5 Hz spike | EffectCraft Title Sting: `WI-FI CSI PASSIVE SENSING` | Alarm siren, sub-bass hit, tension drone |
| **1. The Radio Harp** | 0:18–0:52 | 34s | Remotion 3D triangle $\to$ 52 glowing OFDM strings $\to$ Human dielectric body | Reticle on 52 carriers; Dielectric mirror badge ($\varepsilon_r \approx 50$) | Resonant string pluck, driving synth beat |
| **2. Hardware Ingestion** | 0:52–1:35 | 43s | Macro ESP32 $\to$ C firmware `main.c` $\to$ UART hex stream (0xA55A) | Lower third: `138B Binary Frame @ 921600 Baud` | Data ticker clicks, mechanical whir |
| **3. The DSP Gauntlet** | 1:35–2:25 | 50s | Hampel MAD comparison $\to$ Butterworth filter $\to$ PCA PC1 $\to$ STFT | DSP Violet badges: Hampel MAD, Butterworth [0.2-10 Hz] | Rising tempo pulse, filter frequency sweep |
| **4. The Fall Event** | 2:25–3:15 | 50s | Split-screen: Remotion 3D Fall + PyQt6 Doppler 48.5 Hz spike | Critical Alarm Red flash; Damped shockwave ring | Heavy impact thud, cardiac monitor tone |
| **5. 2D Cartography** | 3:15–3:55 | 40s | PyQt6 RoomMap $\to$ Fresnel ellipsoids $\to$ Levenberg-Marquardt solver | Metric chip: `RMSE = 0.043 m (4.3 cm)` | Geometric tone, harmonic synth pad |
| **6. Real Hardware Proof** | 3:55–4:20 | 25s | Test A/B/C dataset plots $\to$ 24/24 QTest headless screenshots | Pass Green badge: `100% PASS • 2.54s Latency` | Terminal completion chime, solid beat |
| **7. Outro & Next Steps** | 4:20–4:35 | 15s | GitHub repo clone $\to$ LaTeX thesis PDF (`main.pdf`) $\to$ YouTube cards | Subscribe CTA; End-screen video cards | Melodic outro resolve, fade to black |

---

## 5. FilmCraft & EffectCraft MCP Integration Blueprints

### 5.1 FilmCraft Sequence Initialization Payload
```json
{
  "ServerName": "filmcraft",
  "ToolName": "command_batch",
  "Arguments": {
    "commands": [
      {
        "id": "file.newProject",
        "params": { "name": "WiFi_CSI_Master_Project", "baseDir": "/home/vlads4r4/dev/Licenta" }
      },
      {
        "id": "file.newSequence",
        "params": {
          "name": "WiFi_CSI_Master_1080p30",
          "width": 1920,
          "height": 1080,
          "frameRate": 30.0,
          "videoTracks": 3,
          "audioTracks": 2,
          "audioSampleRate": 48000
        }
      }
    ]
  }
}
```

### 5.2 EffectCraft Lower-Third Generator Script
```javascript
function createLowerThird(comp, titleText, metaText, inTimeSec, isAlarm) {
  var accentColor = isAlarm ? [0.937, 0.267, 0.267, 1.0] : [0.220, 0.741, 0.973, 1.0];
  var panel = comp.layers.addSolid([0.067, 0.094, 0.153], "LT_Panel", 480, 72, 1.0);
  panel.property("Position").setValue([96 + 240, 940, 0]);
  panel.inPoint = inTimeSec;
  panel.outPoint = inTimeSec + 5.5;
  
  var titleLayer = comp.layers.addText(titleText);
  titleLayer.property("Position").setValue([96 + 24, 930, 0]);
  titleLayer.inPoint = inTimeSec + 0.1;
  titleLayer.outPoint = inTimeSec + 5.5;
  
  var metaLayer = comp.layers.addText(metaText);
  metaLayer.property("Position").setValue([96 + 24, 955, 0]);
  metaLayer.inPoint = inTimeSec + 0.2;
  metaLayer.outPoint = inTimeSec + 5.5;
}
```

---

## 6. Formal Rejections & Non-Goals

1. **Rejected 100-Second Duration:** A 100s duration compresses the thesis to 12.5s per cluster, destroying technical depth. Master length fixed at 4:30.
2. **Rejected Romanian Primary Audio:** Primary release is in English to maximize global algorithmic reach, citations, and repository stars. Romanian subtitles provided as secondary track.
3. **Rejected Static Visuals:** Any continuous shot exceeding 5.0 seconds without B-roll, camera movement, or telemetry update is barred.
4. **Rejected 60 fps Master:** Master is locked at 30.000 fps ($8{,}467{,}200{,}000\,\text{ticks/frame}$) to match physical 30–50 Hz CSI rate and deterministic Remotion rendering without pull-down judder.
5. **Rejected Pure After Effects Assembly:** EffectCraft generates isolated motion graphics passes; FilmCraft acts as the master multi-track NLE.
