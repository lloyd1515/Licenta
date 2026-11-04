# Scene plan (licenta-remake)

Audience: total newcomer. Style: YouTube code explainer. EVERY code scene follows this pattern:

- Code card on the LEFT (x 60, about 1100 px wide, font 36-40). Exactly the lines listed below, verbatim, real indentation.
- Glow ONE line at a time, cued on the phrase that talks about it (`glow: [{line, from, until}]`), moving down the card as the narration moves.
- RIGHT side (x ~1200-1860): a plain-words callout for the glowing line (K.lines / K.text, 44 px+, max ~10 words, e.g. "`iq` = the 128 reading bytes, as numbers"), each replaced by the next with `until`. Write variable names with `K.mono`.
- Under or beside the callouts: a small LIVE picture that changes as the line runs (K.custom, drawn from t, or kit charts): see "picture" per scene. This is the "watch it happen" part; it must change on screen, not sit still.
- Nothing on screen holds more than ~5 s without something changing. Never open on an empty stage: the code card appears on the scene's first sentence.
- No zooms (no `inside`). Scenes run back-to-back with almost no gap, so draw from the first sentence.
- Numbers on screen only those spoken in the scene (listed below). No other values.

Module split: **builder A = c2** (c2-parse, c2-feed, c2-sheet, c2-drop). **builder B = d2 + c3** (d2-band, d2-pca, d2-slope, d2-fsm, d2-still, c3-show, c3-try).
Modules intro, a1, a2, a3, outro are placeholders (HyperFrames is laid over them). Do not touch them.

---

## c2-parse: open the envelope
Code `src/csi/packets.py:42-47`:
```python
def _parse(raw):
    _, node_id, rssi_dbm, timestamp_us, seq = struct.unpack(HEADER_FORMAT, raw[:HEADER_BYTES])
    iq = np.frombuffer(raw[HEADER_BYTES:PACKET_BYTES], dtype=np.int8)
    csi = iq[0::2] + 1j * iq[1::2]
    active = np.concatenate([csi[part] for part in ACTIVE_SUBCARRIERS])
    return Packet(node_id, rssi_dbm, timestamp_us, seq, active)
```
(font 32-34 if needed; line 1 is long.)
Glow: line 1 on "reads the address"; line 2 on "128 reading bytes"; line 3 on "paired up"; line 4 on "52 useful stations".
Callouts: `node_id` = which board · `rssi_dbm` = how strong · `timestamp_us` = when · `seq` = a counter; then `iq` = 128 small whole numbers; then `csi` = pairs: first + second × j; then `active` = keep 52 stations.
Picture: a row of 138 small tiles (10 address tiles in violet/muted, 128 reading tiles), the 10 lighting on line 1, the 128 on line 2; on line 3 the 128 tiles merge pairwise into 64; on line 4, 12 of the 64 fade, 52 remain (the count "52" appears on "52 useful stations").

## c2-feed: the conveyor belt
Code `src/csi/packets.py:54-69` (`PacketStream.feed`), cut to ≤ 11 lines if needed with a `# ...` comment line marking cuts; must include `start = self._buffer.find(_WIRE_MAGIC)`, `del self._buffer[:start]`, `if len(self._buffer) < PACKET_BYTES:` + `return packets`, `packets.append(_parse(bytes(self._buffer[:PACKET_BYTES])))`, `del self._buffer[:PACKET_BYTES]`.
Glow: find on "looks for the stamp"; `del self._buffer[:start]` on "gets deleted"; the `<` check on "waits for more"; append+del on "opens that envelope".
Picture: a horizontal belt of byte tiles sliding left; junk tiles grey, a stamp tile pair `5A A5` highlighted; on "deleted" the junk tiles fall off; on "waits" a progress bar fills toward 138; on "opens that envelope" a 138-tile block lifts off the belt.
Spoken numbers: 138. Stamp shown as `A55A`.

## c2-sheet: the spreadsheet
Code `src/csi/packets.py:77`:
```python
    amplitude = np.array([np.abs(row) for row in csi_rows], dtype=np.float32)
```
Glow it on "keeps only the arrow lengths".
Picture: a grid (heatmap) filling row by row from the top; labels "669 rows" on "669 rows", "52 columns" on "52 numbers"; on "every row is one moment" one row highlights; on "every column is one station" one column highlights. Counter "about 33 rows / second" on "33 rows a second", "20 s" on "20 seconds".

## c2-drop: drop broken stations
Code `src/csi/dsp.py:51-56`:
```python
def drop_bad_subcarriers(amplitude):
    variance = np.var(amplitude, axis=0)
    valid = (variance >= MIN_SUBCARRIER_VARIANCE) & (variance <= MAX_SUBCARRIER_VARIANCE)
    if not np.any(valid):
        return amplitude
    return amplitude[:, valid]
```
Glow: line 1 (`variance = ...`) on "measures how much each column wobbles"; line 2 (`valid = ...`) on "marks the columns"; last line on "removes them".
Term: `K.term("variance")` = "how much a line wobbles", on "called the variance".
Picture: 52 vertical bars (one per column, heights illustrative, NOT real values; label "illustrative"), appearing on line 1; two horizontal limit lines on line 2, the bars outside turn red (exactly 11 red); on "removes them" the 11 red bars drop away and the rest close up; counters "11 go" / "41 stay" on their words.

## d2-band: the equalizer, in code
Code `src/csi/dsp.py:59-63`:
```python
def bandpass(amplitude, rate_hz, low_hz=BAND_LOW_HZ, high_hz=BAND_HIGH_HZ):
    nyquist_hz = 0.5 * rate_hz
    high_hz = min(high_hz, rate_hz / NYQUIST_MARGIN)
    b, a = signal.butter(BAND_ORDER, [low_hz / nyquist_hz, high_hz / nyquist_hz], btype="band")
    return signal.filtfilt(b, a, amplitude, axis=0)
```
(font ~32.) Glow `signal.butter` line on "butter designs that equalizer"; filtfilt line on "filtfilt runs the filter".
Callouts: "keep 0.2 to 12 wobbles per second" on "between 0.2 and 12"; `K.term("hertz")` = "times per second" on "has a name: hertz"; "forwards, then backwards" on filtfilt.
Picture: a noisy line morphing into a smooth line on "butter designs"; on "forwards and then backwards" an arrow sweeps right then left across it.

## d2-pca: 41 lines become 1
Code `src/csi/dsp.py:66-70`:
```python
def motion_signal(amplitude):
    centered = amplitude - np.mean(amplitude, axis=0)
    covariance = np.cov(centered, rowvar=False)
    _, eigenvectors = np.linalg.eigh(covariance)
    return np.dot(centered, eigenvectors[:, -1])
```
Glow: `centered` line on "centres every column on zero"; `covariance` + `eigh` lines on "find the direction" (one then the other, or both via two glows in sequence); return line on "projects onto it".
Callouts: "move each line to sit around zero" · "which way do they lean together?" · "one number per moment"; `K.term("PCA")` on "called P C A".
Picture: 41 thin overlapping wiggly lines (illustrative) appear on "41 lines"; on "centres" they slide to a common zero; on "projects onto it" they collapse into one bold line labelled "motion line".

## d2-slope: find the jerk
Code `src/csi/fall_detector.py:53-58`:
```python
def _normalized(motion):
    return motion / (np.max(np.abs(motion)) + NORMALIZE_EPSILON)


def _slopes(normalized, rate_hz):
    return np.abs(np.gradient(normalized, 1.0 / rate_hz))
```
Glow `_normalized` return line on "rescaled so its biggest swing equals 1"; `_slopes` return line on "gradient measures how steep".
Picture (watch it happen): a motion line drawn left to right with a cursor; a steepness meter (vertical bar or gauge) beside it follows the cursor; a red threshold line "17.5" on "steeper than 17.5"; at the impact the meter jumps over it and shows "17.63" on "hits 17.63"; "only 3 moments this steep" on "only 3 moments". Constant chip `⚙️ IMPACT_SLOPE = 17.5` (muted) on "steeper than 17.5". The motion line may be illustrative but must show busy → jerk → flat.

## d2-fsm: the stages, in code
Code: from `src/csi/fall_detector.py` loop (lesson.md "Layer 8"), these lines, verbatim with real indentation, cuts marked `# ...`:
```python
    for i in range(1, count):
        if state in (FallState.CALM, FallState.MOVING):
            if active_links[i] >= min_links and has_impact_slope[i]:
                state = FallState.IMPACT
                impact_index = i
        # ...
        elif state == FallState.IMPACT:
            state = FallState.CHECKING_STILL
        elif state == FallState.CHECKING_STILL:
            if i - impact_index >= still_samples:
```
Glow: `for` line on "a loop over every moment"; IMPACT lines on "steep enough"; CHECKING_STILL line on "switches to checking still"; last line on "counts readings".
Picture: five stage boxes in a row (CALM, MOVING, IMPACT, CHECKING_STILL, ALARM) with arrows only along real transitions; the current one lit, following the narration (IMPACT lit on "becomes impact", CHECKING_STILL on "checking still"). ALARM box stays unlit in this scene.

## d2-still: is the person getting up?
Code `src/csi/fall_detector.py:65-68`:
```python
def _is_still(normalized, impact_index, i, settle_samples):
    window_start = impact_index + settle_samples
    variances = [np.var(signal[window_start:i]) for signal in normalized]
    return np.mean(variances) < STILL_MAX_VARIANCE
```
Glow `variances` line on "measures how much the line wobbled"; return line on "far below the limit".
Picture (watch it happen): a tick counter filling 0 → 83 ticks on "counts 83 readings" (label "about 2.5 s"); then a wobble gauge reading "0.06" against a limit line "0.2" (chip `⚙️ STILL_MAX_VARIANCE = 0.20`) on "the wobble is 0.06"; then the ALARM box (reuse d2-fsm's stage row if possible, else a single red ✕ ALARM box) lights red on "Alarm, at about seven seconds"; "about 3 s" on "took about 3 seconds" with a timeline: jerk → alarm.

## c3-show: when the bell rings
Code `src/csi/gui/main_window.py:248-259`:
```python
    def show_frame(self, frame: Frame):
        self.frame_count += 1

        self.room_map.show_frame(frame)
        self.doppler_plot.show_frame(frame)
        self.waterfall.show_frame(frame)
        self.status_panel.show_frame(frame)

        if not frame.alarm:
            self.alarm_dismissed = False
        elif not self.alarm_dismissed:
            self.show_alarm(frame.latency_s)
```
Glow: `def` line on "show frame runs"; room_map on "room map"; doppler_plot then waterfall on "two charts" (sequential glows); status_panel on "status panel"; `show_alarm` line on "shows the red banner".
Picture: a dashboard mock with 4 tiles (Room map, Chart, Chart, Status) each pulsing as its line glows; a red banner "ALARM" sliding in on "red banner"; a `careful` note "figure = drawing of the stage, not measured" on "does not measure".

## c3-try: try it yourself
Code card 1 (bash, title "Run from the repository root"):
```bash
cd src && ../.venv/bin/python -m csi.gui --replay
```
on "run the app in replay mode"; callout "plays this fall on a loop, no hardware".
Code card 2 `src/csi/fall_detector.py:28`:
```python
STILL_WINDOW_S = 2.5
```
on "change the still window", then a cross-fade to the same card showing `STILL_WINDOW_S = 1.0` on "to 1.0 seconds" (in-place change: `slide: 0`). Two question chips on their words: "alarm sooner?" and "rings when someone sits?".

---

## Chapter 4-6 addition (2026-10-21). Module split: **builder C = d5** (d5-norm only). Do not touch other modules.

## d5-norm: why a soft bed looks like a hard floor
Code `src/csi/fall_detector.py:53-58` (same lines as d2-slope, shown again):
```python
def _normalized(motion):
    return motion / (np.max(np.abs(motion)) + NORMALIZE_EPSILON)


def _slopes(normalized, rate_hz):
    return np.abs(np.gradient(normalized, 1.0 / rate_hz))
```
Glow: `_normalized` return line on "Look at the first line" until "Then gradient"; `_slopes` return line on "Then gradient measures".
Callouts: on "divided by its own biggest swing" → "`np.max(np.abs(motion))` = the biggest swing → every line peaks at 1"; on "A thump on a mattress" → "mattress or tiles: same size after this line"; on "Then gradient" → "`np.gradient` = only how fast the line changes"; on "We checked this" → "test signals were made up (synthetic), not recorded".
Picture (right side): two raw motion lines stacked, labelled "flop on a mattress" (small swing, muted) and "fall on tiles" (big swing, red). On "divided by its own biggest swing" both rescale to the same height (animate the y-scale), with a dashed "1" line. On "only how fast" a steepness meter appears under both and both meters jump over a red "17.5" line together. On "The slow lie-down stayed calm" a result card: "slow lie-down: steepness 1.84 → no alarm" (green); on "The flop rang the alarm": "flop: steepness 20.78 → ALARM after 2.5 s" (red). Small mono footnote under the cards: "synthetic test, 3 links, 250 Hz".
Spoken numbers: none (exact values on screen only).
