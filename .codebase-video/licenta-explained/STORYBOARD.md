# Licenta remake: storyboard v1 (for review before build)

Audience: total newcomer. Never heard of Wi-Fi sensing, signal processing, Qt.
Goal: understand *why* it works (real-life pictures), then *how* (real code, line by line).

## Rules for the whole video

| Rule | Value |
|---|---|
| Length | ~9 min (≈1400 words) |
| Voice | one Kokoro voice for both engines (`af_heart`), speed 1.05 → ~155 wpm |
| Silence | no gap > 0.8 s; total < 5%. No `[think]` pauses, no `[rest]` |
| New terms | max 1 per ~20 s. Picture first → plain sentence → *then* the real name |
| Numbers | ≤ 2 spoken per scene, rounded ("about 3 seconds"). Exact values only on screen |
| Screen | visual changes every 5–8 s |
| Words | "packet" = radio message, "screen update" = GUI Frame. Never bare "frame" |
| Cut | Hampel aside, UART/PyQt6/QThread names in intro, replay step arithmetic, "links", 3 recaps → 1 |

Engine split: **HF** = HyperFrames (analogies, hook, motion-heavy hero scenes). **CV** = codebase-video (code walkthroughs: real code, one line lit at a time + variable callouts). Rendered separately at 1920×1080, stitched with ffmpeg, one shared voice track per scene.

---

## Act 0. Cold open (0:00–0:20) · HF

- **Visual**: dark room, three small boards glowing on walls. Stick figure walks, wobbles, falls. Red banner slams in: `FALL DETECTED`. Freeze.
- **Say**: "Someone just fell in this room. No camera saw it. Nobody wore a sensor. The Wi-Fi did. In nine minutes you'll know exactly how, down to the line of code that rang this alarm."

## Act 1. Intuition, no code (0:20–2:30)

### 1.1 Why care (0:20–0:40) · HF
- **Visual**: older person alone at home; phone out of reach; clock ticking.
- **Say**: "Older people who fall alone often can't call for help. Cameras feel like spying, and wristbands get left on the nightstand. So: can a room notice a fall by itself?"

### 1.2 Ripples in a pond = Wi-Fi sensing (0:40–1:15) · HF
- **Analogy**: drop a stone in a pond; ripples bounce off a reed; someone on the far bank sees the ripple pattern change without seeing the reed.
- **Visual**: pond ripples morph into radio waves between two boards; person steps in, waves bend and wobble; receiver needle shakes.
- **Say**: "Radio waves bounce around a room like ripples in a pond. A body in the way changes how they arrive. We don't look at the person. We watch the ripples wobble."
- **New term (end)**: CSI = "the radio's report of how each wave arrived."

### 1.3 52 radio stations = subcarriers (1:15–1:45) · HF
- **Analogy**: Wi-Fi is not one wave but 52 at once, like 52 radio stations / 52 piano keys.
- **Visual**: one wave splits into a row of 52 thin bars (an equalizer). Person moves → bars jump differently.
- **Say**: "Wi-Fi sends 52 narrow waves at once, like 52 radio stations. For every message, the board reports how loud each station arrived. 52 volume numbers, about 33 times a second."
- **New term**: subcarrier (on screen, after the sentence).

### 1.4 What a fall looks like (1:45–2:30) · HF
- **Visual**: three short line charts side by side: *empty room* (flat), *walking* (busy wiggle), *fall* (busy → one huge jerk → flat). Highlight jerk in red, flat part in blue.
- **Say**: "Turn all that into one wiggly line, and three rooms look like this. Empty: calm. Walking: busy. A fall: busy, then one sharp jerk, then flat, because the person is lying still. The whole program hunts for this shape: a jerk, then stillness."
- **Payoff promise**: "Now let's follow one real fall through the code."

## Act 2. One real fall, through the code (2:30–7:30) · CV unless noted

Format for every code scene: code panel left (5–8 real lines), one line lit at a time, floating callout per variable ("`iq` = raw bytes as numbers"), small live chart right that changes as the line runs.

### 2.1 The packet (2:30–3:20)
- **Analogy**: a letter in an envelope: header = address on the envelope (who sent it, when); payload = the 52 volume readings.
- **Visual** (HF intro 5 s): envelope opens, 138 bytes spill as tiles: 10 address tiles + 128 reading tiles.
- **Code**: `src/csi/packets.py:42-47` `_parse`, lines lit in turn:
  - `struct.unpack(...)` → callout "read the envelope: node, signal strength, time, number"
  - `iq = np.frombuffer(...)` → "the 128 bytes, as small signed numbers"
  - `csi = iq[0::2] + 1j * iq[1::2]` → "pair them up: every reading is 2 numbers"
  - `active = ...` → "keep the 52 useful stations, drop the edges"
- **Why 2 numbers? (HF 10 s)**: graph paper, arrow 30 right, 40 down. Triangle 30-40-50. "Each reading is an arrow. We only care how long it is: 50. That length is the loudness."

### 2.2 Finding letters in a stream (3:20–3:50)
- **Analogy**: a conveyor belt of letters with no gaps; every letter starts with the same stamp `A55A`. Find the stamp, cut 138 bytes, repeat.
- **Visual**: byte tiles scroll on a belt; scanner light finds `5A A5`; scissors cut.
- **Code**: `packets.py:54-69` `PacketStream.feed`, lit: `find(_WIRE_MAGIC)` → `del self._buffer[:start]` (throw junk away) → `if len < PACKET_BYTES: return` (wait for the rest) → `_parse(...)`.

### 2.3 The spreadsheet (3:50–4:10)
- **Visual**: each packet becomes one row; rows stack into a 669 × 52 grid (heatmap). Clock: "20 seconds of recording".
- **Code**: `packets.py:77` `np.abs(row)` → "keep the arrow lengths only."
- **Say** (1 number): "About 33 rows per second, 20 seconds: a spreadsheet of 669 rows."

### 2.4 Clean step 1: drop broken stations (4:10–4:40)
- **Analogy**: a choir; some singers are silent, some scream. Remove both.
- **Code**: `dsp.py:51-56`, lit: `variance = np.var(...)` → bar chart of 52 "how much it wobbles" bars; `valid = ...` → bars too low/too high turn red; `amplitude[:, valid]` → red columns slide out of the grid, 52 → 41.
- **New term**: variance = "how much a line wobbles."

### 2.5 Clean step 2: keep human speed (4:40–5:10)
- **Analogy**: an equalizer. Turn down the slow drift (room warming up) and the fast hiss (electronics). Keep the middle: how fast bodies move.
- **Visual** (HF): EQ sliders; noisy line before → smooth line after.
- **Code**: `dsp.py:59-63` `bandpass`, lit: `signal.butter(...)` → "design the filter: keep 0.2 to 12 wobbles per second"; `filtfilt` → "run it forward and backward so nothing shifts in time."
- **New term**: hertz = "times per second" (spoken once).

### 2.6 Clean step 3: 41 lines → 1 (5:10–5:45)
- **Analogy**: 41 people watching the same match; they all lean the same way when a goal happens. Listen to the crowd's lean, not each person.
- **Visual**: 41 thin lines collapse into one bold line.
- **Code**: `dsp.py:66-70` `motion_signal`, lit: `centered = ...` → "center each line on zero"; `eigh(covariance)` → "find the direction they all lean together"; `np.dot(centered, eigenvectors[:, -1])` → "project onto it: one number per moment."
- **New term**: PCA, name on screen only.

### 2.7 Find the jerk (5:45–6:25)
- **Analogy**: steepness of a hill / a speedometer for the line.
- **Code**: `fall_detector.py:53-58`, lit: `_normalized` → "rescale so the loudest moment is 1; big room and small room use the same rule"; `np.gradient(...)` + `np.abs` → "how steep is the line right now."
- **Visual**: the motion line; a slope meter rides along it; red threshold line at 17.5. At sample 153 the meter crosses: 17.63. "Close call: only 3 moments in the whole recording go that steep."

### 2.8 The smoke-alarm logic (6:25–7:30)
- **Analogy**: a careful smoke alarm with stages: *quiet* → *something's moving* → *big jerk!* → *wait and watch* → *ALARM*. It doesn't scream at the jerk; it waits to see if you get up.
- **Visual** (HF): five stage lights in a row, one lit at a time, driven by the real test C timeline.
- **Code**: `fall_detector.py` loop, 3 branches lit in turn (`IMPACT` when steep, `CHECKING_STILL` next, `ALARM` if still), then `_is_still` (`65-68`): `np.var(signal[window_start:i])` → "how much did the line wobble since the jerk?"; `< STILL_MAX_VARIANCE` → "barely: 0.06, under the 0.2 limit. They're not getting up."
- **Ticker**: 83 tick marks fill in after the jerk ("count 83 readings, about 2.5 seconds… here 3, because packets arrived a bit slow"). Ends: ALARM at 7.4 s.

## Act 3. On the screen (7:30–8:30)

### 3.1 Kitchen and dining room = threads (7:30–8:05) · HF + CV
- **Analogy**: the kitchen (`FrameSource`) cooks in the back so the dining room (the window) never freezes. Each finished plate goes through a hatch with a bell (`frame_ready`).
- **Code**: `main_window.py:248-259` `show_frame`, four widget lines lit one by one as each widget pulses on a dashboard mock: room map, motion chart, waterfall, status panel. Then the `show_alarm` line → banner.
- **Honest note (on screen, 3 s)**: "the stick figure is an illustration of the state, not a measured position."

### 3.2 Try it yourself (8:05–8:30) · CV
- **On screen**: `cd src && python -m csi.gui --replay` → "plays the real fall on a loop, no hardware needed."
- **Challenge**: "Open `src/csi/fall_detector.py`, change `STILL_WINDOW_S` from 2.5 to 1.0. Does the alarm come sooner? Does it now fire when someone just sits down?"

## Act 4. One-screen recap (8:30–8:50) · HF

- **Visual**: the full pipeline drawn as the analogies, left to right: pond ripples → 52 stations → envelope → spreadsheet → choir/EQ/crowd → hill meter → smoke alarm → dining room. Each labelled with its file name underneath.
- **Say**: "Ripples, stations, letters, a spreadsheet, three cleanups, one steep moment, a careful alarm. That's the whole repo."

---

## Open questions for you

1. Length ~9 min OK, or shorter (~6 min, drop 2.2 and 3.1)?
2. Voice: female `af_heart` (current CV) or male `am_michael` (current HF)?
3. Language: English, or Romanian narration?
