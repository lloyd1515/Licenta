# Licenta: Wi-Fi CSI fall detection, end to end

## What this is and why it exists

Licenta is a bachelor thesis system (UTCN) that detects a human fall in a room without any wearable or camera. It listens to how a human body disturbs Wi-Fi radio signals between three ESP32 boards (README.md:1-14). A Python package named `csi` turns the raw radio measurements into one "motion" signal, runs a small state machine over it, and shows the result in a PyQt6 desktop app (README.md:44-70).

Who calls what: a person runs `python -m csi.gui` (live or replay), `python -m csi.record` (capture to a file), or `python -m csi.figures` (thesis plots) from `src/` (README.md:134-166).

Words a newcomer must know:

- **CSI (Channel State Information)**: for every received Wi-Fi frame the radio reports, per OFDM subcarrier, a complex number describing how the channel changed that subcarrier. The code uses 52 active subcarriers (src/csi/room.py:7-8).
- **Subcarrier**: one narrow frequency slot of the OFDM signal, spaced 312.5 kHz apart (src/csi/room.py:6).
- **Link**: an ordered pair of nodes. There are three: `LINKS = ((1, 2), (2, 3), (3, 1))` (src/csi/room.py:12).
- **Frame**: in firmware, one 138-byte UART packet (src/firmware/esp32_csi_node/main/main.c:47). In the GUI, `Frame` is a different thing: one screen update (src/csi/gui/frames.py:33-48). Do not confuse them.
- **Motion signal**: the single 1-D number series per recording that the fall detector reads (src/csi/dsp.py:66-70).

## The ideas it builds on

**Device-free sensing.** A body in a room changes the path of reflected radio waves, so the amplitude of CSI fluctuates when someone moves. Nobody has to carry anything. Here the amplitude of each subcarrier is the only thing used; phase is discarded (`np.abs(row)`, src/csi/packets.py:77).

**Fresnel zone / extra path.** The ellipse of points whose detour (tx to point to rx, minus the direct tx to rx distance) is constant. `extra_path_m` computes that detour for a point and a link (src/csi/room.py:20-25). The simulator and the localizer use it; the real-data fall detector does not.

**Band-pass filtering.** Keep only frequencies in a band. Body motion lives roughly between 0.2 and 12 Hz, so a 4th-order Butterworth band-pass keeps that (src/csi/dsp.py:15-17, 59-63).

**Outlier removal (Hampel filter).** Replace a sample by the local median when it is more than N robust standard deviations away; robust sigma = 1.4826 x MAD (median absolute deviation) (src/csi/dsp.py:11, 38-48).

**PCA (principal component analysis).** Find the direction in which many correlated channels vary most, and project onto it. The code takes the eigenvector of the covariance matrix with the largest eigenvalue (src/csi/dsp.py:66-70). That turns the surviving subcarriers (41 of 52 on test C) into one series.

**Finite state machine (FSM).** A program that is always in exactly one named state and moves between states on conditions. Here: `CALM, MOVING, IMPACT, CHECKING_STILL, ALARM` (src/csi/fall_detector.py:7-12).

**Stream framing with a magic number.** Serial bytes have no packet boundaries. Every packet starts with a known 2-byte marker (`0xA55A`); the receiver searches for it to re-synchronise (src/csi/packets.py:8, 21, 50-69).

**Producer thread and signal/slot (Qt).** A `QThread` produces data; it emits a Qt signal; the GUI thread's slot draws it. `FrameSource` emits `frame_ready`, `MainWindow.show_frame` receives it (src/csi/gui/frame_source.py:22-24; src/csi/gui/main_window.py:206).

## The map

Pipeline, left to right (src/csi/packets.py, dsp.py, fall_detector.py, gui/*):

```
ESP32 firmware --UART 921600--> PacketStream --> Recording --> analyze_recording --> Detection
 (main.c)                        (packets.py)                    (dsp.py)          (fall_detector.py)
                                       |                              |
                      record.py -> .npz file -> load_recording        v
                                                         frames.py (Frame per update)
                                                                      |
                                              FrameSource (QThread) --frame_ready--> MainWindow --> widgets
```

Directory layout that matters:

- `src/firmware/esp32_csi_node/main/main.c`: the whole firmware (167 lines).
- `src/csi/`: the Python package. `room.py` (geometry constants), `packets.py` (wire format, `Recording`, `.npz` I/O), `record.py` (capture CLI), `dsp.py` (filters, PCA, spectrogram, `analyze_recording`), `fall_detector.py` (FSM), `simulator.py` (synthetic CSI), `localization.py` (2-D position solver), `figures.py` (thesis plots).
- `src/csi/gui/`: `__main__.py` (CLI), `main_window.py`, `frame_source.py`, `frames.py`, widgets `room_map.py`, `charts.py`, `status_panel.py`, `theme.py`, `screenshots.py`.
- `src/csi/data/`: three real recordings `test_A_camera_goala.npz` (empty room), `test_B_mers_normal.npz` (walking), `test_C_cadere_reala.npz` (real fall) (src/csi/packets.py:16-19).

Ignore: `src/simulation-remotion` (a separate React/Remotion animation project, README.md:94-95), `src/firmware/esp32_csi_node/build`, `src-backup-pre-simplify-2026-10-14.tar.gz`, `docs/` (Obsidian notes, partly stale), `.omc/`, `.claude/`, `.agents/`.

Parts:

- Firmware: external device (ESP32 C program) (src/firmware/esp32_csi_node/main/main.c:154-167)
- packets: internal module, wire parser and `Recording` (src/csi/packets.py:50-69)
- dsp: internal module, filters and PCA (src/csi/dsp.py:86-92)
- fall_detector: internal module, 5-state FSM (src/csi/fall_detector.py:71-120)
- FrameSource: internal module, QThread producer (src/csi/gui/frame_source.py:22-121)
- MainWindow: entry point, GUI window (src/csi/gui/main_window.py:41-60)
- data: data store, `.npz` recordings (src/csi/packets.py:16-19)

Connections:

- Firmware -> packets: streams 138-byte frames over UART (src/firmware/esp32_csi_node/main/main.c:82; src/csi/packets.py:68)
- packets -> dsp: hands over a `Recording` (src/csi/dsp.py:86-87)
- dsp -> fall_detector: calls `detect_fall` with the motion signal (src/csi/dsp.py:91)
- data -> packets: `load_recording` reads `.npz` (src/csi/packets.py:89-96)
- FrameSource -> dsp: runs `analyze_recording` on replay file or live window (src/csi/gui/frame_source.py:102; src/csi/gui/frames.py:139)
- FrameSource -> MainWindow: emits `frame_ready` signal (src/csi/gui/frame_source.py:89, 112; src/csi/gui/main_window.py:206)
- MainWindow -> FrameSource: starts, stops, resets alarm (src/csi/gui/main_window.py:199-214, 272)

## The core mechanism

**One sentence:** a stream of per-subcarrier amplitudes is collapsed into one band-passed "motion" series (drop bad subcarriers, Butterworth band-pass, PCA), and the fall is declared when that series shows a sudden steep slope followed by a stillness window of `int(2.5 * rate)` samples (83 samples on test C).

Follow one real example: the recording `test_C_cadere_reala.npz`, loaded by `load_recording`. It has 669 packets, 52 columns, rate 33.51 Hz, 20 s long (values from running the code on this checkout).

### Layer 1: bytes on the wire

The firmware's callback fills a packed struct and queues it:

`src/firmware/esp32_csi_node/main/main.c:38-47`
```c
typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t  node_id;
    int8_t   rssi_dbm;
    uint32_t timestamp_us;
    uint16_t seq;
    int8_t   csi_iq[CSI_BYTES];
} csi_packet_t;

_Static_assert(sizeof(csi_packet_t) == 138, "wire packet must be 138 bytes");
```

The Python side declares the same layout as `"<HBbIH"` (10 bytes header) plus 128 IQ bytes (src/csi/packets.py:9-12). `_parse` turns the int8 pairs into complex numbers and keeps two slices of 26 subcarriers:

`src/csi/packets.py:42-47`
```python
def _parse(raw):
    _, node_id, rssi_dbm, timestamp_us, seq = struct.unpack(HEADER_FORMAT, raw[:HEADER_BYTES])
    iq = np.frombuffer(raw[HEADER_BYTES:PACKET_BYTES], dtype=np.int8)
    csi = iq[0::2] + 1j * iq[1::2]
    active = np.concatenate([csi[part] for part in ACTIVE_SUBCARRIERS])
    return Packet(node_id, rssi_dbm, timestamp_us, seq, active)
```

Worked bytes (I built a packet and fed it to the parser): header `5aa503cc404b4c000700` = magic `5a a5` (little-endian 0xA55A), node 3, rssi `0xcc` = -52, timestamp `404b4c00` = 5 000 000 us, seq 7. IQ payload bytes 12 and 13 (packet bytes 22 and 23) set to 30 and -40 land in complex index 6, which is the first kept subcarrier (`slice(6, 32)`), giving `30-40j`, amplitude 50.0 (src/csi/packets.py:13).

### Layer 2: resynchronising the byte stream

`PacketStream.feed` searches for the magic bytes, drops garbage before it, waits for 138 bytes, parses, and loops:

`src/csi/packets.py:54-69`
```python
    def feed(self, data):
        self._buffer.extend(data)
        packets = []
        while True:
            start = self._buffer.find(_WIRE_MAGIC)
            if start == -1:
                if self._buffer[-1:] == _WIRE_MAGIC[:1]:
                    del self._buffer[:-1]
                else:
                    self._buffer.clear()
                return packets
            del self._buffer[:start]
            if len(self._buffer) < PACKET_BYTES:
                return packets
            packets.append(_parse(bytes(self._buffer[:PACKET_BYTES])))
            del self._buffer[:PACKET_BYTES]
```

Tested: two junk bytes plus half a packet gives no packet; feeding the rest yields exactly one. If the buffer ends with a lone `0x5A` it is kept in case the next chunk starts with `0xA5`.

> Note: the parser trusts the magic only; a payload byte pair equal to `5A A5` is harmless once the stream is aligned, because after a good packet the buffer is cut by exactly 138 bytes; but when re-synchronising mid-packet a `5A A5` inside a payload is taken as a header and produces one bogus packet (checked by running `PacketStream.feed`), and a corrupted packet would not be detected (no checksum in the format, src/csi/packets.py:9-12) (inferred).

### Layer 3: packets to a Recording (amplitude matrix)

`src/csi/packets.py:72-78`
```python
def _recording(times_s, csi_rows, rssi_dbm):
    times_s = np.asarray(times_s, dtype=np.float64)
    times_s = times_s - times_s[0]
    duration_s = times_s[-1] - times_s[0]
    rate_hz = float(len(times_s) / duration_s) if duration_s > 0 else FALLBACK_RATE_HZ
    amplitude = np.array([np.abs(row) for row in csi_rows], dtype=np.float32)
    return Recording(times_s, rate_hz, amplitude, np.asarray(rssi_dbm, dtype=np.float64))
```

The sampling rate is not configured; it is measured as packets divided by duration. For test C: 669 / 19.96 s = 33.51 Hz.

### Layer 4: drop bad subcarriers

`src/csi/dsp.py:51-56`
```python
def drop_bad_subcarriers(amplitude):
    variance = np.var(amplitude, axis=0)
    valid = (variance >= MIN_SUBCARRIER_VARIANCE) & (variance <= MAX_SUBCARRIER_VARIANCE)
    if not np.any(valid):
        return amplitude
    return amplitude[:, valid]
```

A column is kept only if its variance over the recording is between 0.05 and 350 (src/csi/dsp.py:13-14). On test C columns 2 and 21-30 (11 columns) fail, so the matrix goes from (669, 52) to (669, 41). At the impact sample, row values `[6, 10.63, 4.47, 9.22]` become `[6, 10.63, 9.22, 16.55]` because column 2 vanished.

> Note: the Hampel filter `remove_outliers` (src/csi/dsp.py:38-48) exists but `analyze_recording` never calls it; the README still describes a Hampel-first pipeline (README.md:24, 50, 69) (read from src/csi/dsp.py:86-92).

### Layer 5: band-pass

`src/csi/dsp.py:59-63`
```python
def bandpass(amplitude, rate_hz, low_hz=BAND_LOW_HZ, high_hz=BAND_HIGH_HZ):
    nyquist_hz = 0.5 * rate_hz
    high_hz = min(high_hz, rate_hz / NYQUIST_MARGIN)
    b, a = signal.butter(BAND_ORDER, [low_hz / nyquist_hz, high_hz / nyquist_hz], btype="band")
    return signal.filtfilt(b, a, amplitude, axis=0)
```

At 33.51 Hz the cap `rate_hz / 2.1` = 15.96 Hz is above 12, so the band stays 0.2 to 12 Hz. `filtfilt` runs the filter forward and backward (zero phase), along time (axis 0). Note it is non-causal: it uses the whole window, including the future. That is fine for replay and for the live 10 s window, which is re-filtered each update (src/csi/gui/frames.py:139).

### Layer 6: PCA to one number per time step

`src/csi/dsp.py:66-70`
```python
def motion_signal(amplitude):
    centered = amplitude - np.mean(amplitude, axis=0)
    covariance = np.cov(centered, rowvar=False)
    _, eigenvectors = np.linalg.eigh(covariance)
    return np.dot(centered, eigenvectors[:, -1])
```

`eigh` returns eigenvalues in ascending order, so `[:, -1]` is the dominant direction. Output: 669 numbers. Around the impact, `motion[151:156]` is about `[-38.5, -48.1, 2.8, 22.2, -14.8]`; the global peak magnitude is 66.77 at sample 258; the std is 15.30.

> Note: eigenvector sign is arbitrary, so the series may be mirrored between runs; the detector uses absolute slopes, so this does not matter (src/csi/fall_detector.py:58).

### Layer 7: normalise and take the slope

`src/csi/fall_detector.py:53-62`
```python
def _normalized(motion):
    return motion / (np.max(np.abs(motion)) + NORMALIZE_EPSILON)


def _slopes(normalized, rate_hz):
    return np.abs(np.gradient(normalized, 1.0 / rate_hz))


def normalized_slopes(motion_by_link, rate_hz):
    return {name: _slopes(_normalized(motion), rate_hz) for name, motion in motion_by_link.items()}
```

Dividing by the peak maps the series into [-1, 1]; the slope is then in "full-scale units per second". At the impact sample the slope is 17.63, just above `IMPACT_SLOPE = 17.5` (src/csi/fall_detector.py:24). Only 3 samples in the whole recording exceed 17.5; the maximum is 18.90.

> Note: an "active" link at a sample means normalised slope above `SLOPE_ACTIVE = 0.05` (src/csi/fall_detector.py:23, 82). That is so low that on test C 658 of 669 samples count as active, which is why the state is almost always MOVING and CALM appears once.

> Note: because the series is normalised by its own maximum, the thresholds depend on the window content. In live mode a different 10 s window changes the scale (inferred from src/csi/fall_detector.py:53-54 and src/csi/gui/frames.py:17).

### Layer 8: the state machine (the bottom layer)

`src/csi/fall_detector.py:71-120` (trimmed)
```python
def detect_fall(times_s, motion_by_link, rate_hz):
    count = len(times_s)
    states = np.zeros(count, dtype=int)

    empty_room_std = EMPTY_ROOM_STD_SIMULATED if rate_hz >= SIMULATED_MIN_RATE_HZ else EMPTY_ROOM_STD_HARDWARE
    mean_std = float(np.mean([np.std(motion) for motion in motion_by_link.values()]))
    if mean_std < empty_room_std:
        return Detection(states, None, None)

    normalized = [_normalized(motion) for motion in motion_by_link.values()]
    slopes = np.array([_slopes(signal, rate_hz) for signal in normalized])
    active_links = (slopes > SLOPE_ACTIVE).sum(axis=0)
    has_impact_slope = (slopes > IMPACT_SLOPE).any(axis=0)
    min_links = min(MIN_LINKS_AT_IMPACT, len(normalized))
    # …
    for i in range(1, count):
        if state in (FallState.CALM, FallState.MOVING):
            if active_links[i] >= min_links and has_impact_slope[i]:
                state = FallState.IMPACT
                impact_index = i
            elif active_links[i] >= 1:
                state = FallState.MOVING
                calm_counter = 0
            else:
                calm_counter += 1
                if calm_counter > calm_samples:
                    state = FallState.CALM
        elif state == FallState.IMPACT:
            state = FallState.CHECKING_STILL
        elif state == FallState.CHECKING_STILL:
            if i - impact_index >= still_samples:
                if _is_still(normalized, impact_index, i, settle_samples):
                    state = FallState.ALARM
                    alarm_index = i
                else:
                    state = FallState.MOVING
        states[i] = state
```

The "still" check:

`src/csi/fall_detector.py:65-68`
```python
def _is_still(normalized, impact_index, i, settle_samples):
    window_start = impact_index + settle_samples
    variances = [np.var(signal[window_start:i]) for signal in normalized]
    return np.mean(variances) < STILL_MAX_VARIANCE
```

For test C at 33.51 Hz: `calm_samples = int(0.6*33.51) = 20`, `still_samples = int(2.5*33.51) = 83`, `settle_samples = int(0.5*33.51) = 16` (constants src/csi/fall_detector.py:26-28). The impact fires at sample 153 (t = 4.3455 s). The state goes IMPACT at 153, CHECKING_STILL at 154. At sample 236 (153 + 83) the detector computes the variance of the normalised series from sample 169 to 236; it is 0.060, below `STILL_MAX_VARIANCE = 0.20`, so state ALARM at t = 7.3613 s. Latency = 7.3613 - 4.3455 = 3.016 s, which is the `latency_s` property (src/csi/fall_detector.py:46-50). The state counts over the whole recording are CALM 1, MOVING 152, IMPACT 1, CHECKING_STILL 82, ALARM 433.

> Note: the "latency" is the confirmation window, not computation time. It is counted in samples (`still_samples = int(STILL_WINDOW_S * rate_hz)`, src/csi/fall_detector.py:28, 87, 110), so its length in seconds follows the packet timestamps. On test C the 83 samples from 153 to 236 span 3.016 s (about 27.5 Hz locally, below the 33.51 Hz average), which is why the latency is 3.0 s and not 2.5 s. Once the state reaches ALARM no branch leaves it (src/csi/fall_detector.py:95-116), so the alarm stays for the rest of the recording.

> Note: `dsp.analyze_recording` passes a single link `{"node": motion}` (src/csi/dsp.py:91), so `min_links = min(2, 1) = 1` (src/csi/fall_detector.py:84). The "at least two links collapse" rule in the README (README.md:70) is only exercised with the multi-link simulator path in `figures.py`, not by the real-data/GUI path (inferred; I did not trace figures.py fully).

Table of the example (test C, values from running the code):

| Moment | Sample | Value | Result |
| --- | --- | --- | --- |
| One packet | n/a | IQ bytes (30, -40) | amplitude 50.0 |
| Matrix | n/a | (669, 52), 33.51 Hz | after drop: (669, 41) |
| Motion signal near impact | 153 | about 2.8 (global peak 66.77) | slope 17.63 > 17.5 |
| Detector | 153 / 154 | state | IMPACT, then CHECKING_STILL |
| Still check | 236 | variance 0.060 < 0.20 | ALARM at 7.3613 s |
| Output | n/a | impact 4.3455 s, alarm 7.3613 s | latency 3.016 s |

For comparison, empty room test A: std of motion 9.60 < 11.0 so the detector exits early with all zeros (src/csi/fall_detector.py:75-78). Walking test B: std 16.65, 552 MOVING samples, no impact, no alarm.

## Flow 1: live capture to alarm banner

Entry: `python -m csi.gui --live --port /dev/ttyUSB0` (README.md:146-148).

1. `main()` parses args, builds the ports tuple with the chosen port first, creates `MainWindow`, and calls `window.start_live()` (src/csi/gui/__main__.py:67-76).
2. `_start_source` creates a `FrameSource`, connects its signals, and starts the thread (src/csi/gui/main_window.py:197-208).
3. `FrameSource.run` opens ports; with none it falls back to replay:

`src/csi/gui/frame_source.py:35-42`
```python
    def run(self):
        if self._live:
            connections = self._open_ports()
            if connections:
                self._run_live(connections)
                return
            self.status_changed.emit("Hardware ports unavailable. Falling back to Replay Mode.")
        self._run_replay()
```

`_open_ports` skips ports whose path does not exist and also returns an empty list when `pyserial` is not importable (src/csi/gui/frame_source.py:12-15, 51-57).

4. Firmware side, per frame: `probe_sender_task` broadcasts a 64-byte 802.11 probe request in a loop (src/firmware/esp32_csi_node/main/main.c:96-104). Each probe received by another node triggers `on_csi`, which copies up to 128 CSI bytes into a packet and pushes it into a ring buffer (main.c:56-75); `uart_sender_task` on core 1 pops and writes it to UART (main.c:77-86).
5. `_run_live` polls every 2 ms: for every connection it reads `in_waiting` bytes, feeds the `PacketStream`, and adds each packet to `LiveTracker` (src/csi/gui/frame_source.py:79-84).
6. At most every `1/fps` seconds (default 50 FPS, src/csi/gui/__main__.py:13) it asks the tracker for a frame:

`src/csi/gui/frames.py:124-148`
```python
    def add(self, packet: Packet):
        if self._origin_us is None:
            self._origin_us = packet.timestamp_us
        window = self._packets.setdefault(packet.node_id, deque())
        window.append(packet)
        oldest_us = packet.timestamp_us - LIVE_WINDOW_S * MICROSECONDS_PER_SECOND
        while window[0].timestamp_us < oldest_us:
            window.popleft()

    def frame(self):
        if not self._packets:
            return None
        window = max(self._packets.values(), key=len)
        if len(window) < MIN_LIVE_SAMPLES:
            return None
        analysis = analyze_recording(recording_from_packets(list(window)))
        frame = _frames(analysis, [len(analysis.motion) - 1])[0]
        elapsed_s = (window[-1].timestamp_us - self._origin_us) / MICROSECONDS_PER_SECOND
        frame = replace(frame, time_s=elapsed_s)
        if frame.alarm:
            self._latched = True
            self._latency_s = frame.latency_s
        if self._latched:
            frame = replace(frame, alarm=True, latency_s=self._latency_s)
        return frame
```

   So per update the whole 10 s window of the busiest node is re-analysed with the pipeline from the core mechanism (needs 64 packets first, `MIN_LIVE_SAMPLES`, src/csi/gui/frames.py:15), and only the newest sample becomes a `Frame`. The alarm is latched until reset (src/csi/gui/frames.py:143-148).
7. `frame_ready.emit(frame)` crosses threads; `MainWindow.show_frame` updates four widgets and calls `show_alarm` on every alarm frame until the user dismisses it:

`src/csi/gui/main_window.py:248-259`
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

8. Dismiss: the button calls `dismiss_alarm`, which hides the banner and calls `source.reset_alarm()`, setting a `threading.Event` that `_run_live` sees and uses to clear the tracker's packet windows (src/csi/gui/main_window.py:267-273; src/csi/gui/frame_source.py:48-49, 76-78; src/csi/gui/frames.py:150-153).

Errors: a serial exception inside the loop becomes a status-bar message `"Serial stream error: ..."` and the finally block closes the ports (src/csi/gui/frame_source.py:93-98). Ends at: the status bar, banner and widgets.

> Note: the position, speed and height shown in the `RoomMap` and status panel are NOT measured. `illustrative_pose(state, time_s)` returns a canned pose per state (src/csi/gui/frames.py:59-77), so the avatar only illustrates the FSM state. The Fresnel localizer in `localization.py` is not imported by the GUI (src/csi/gui/*.py imports; localization is used by `figures.py`, src/csi/figures.py:22).

> Note: `_frames` picks `peaks_hz[column]` for Doppler from a spectrogram of the mean amplitude over all subcarriers (src/csi/dsp.py:90; src/csi/gui/frames.py:83-98).

## Flow 2: replay and offline analysis (what you run first)

Entry: `python -m csi.gui --replay` (README.md:142-144). Needs no hardware.

1. `--replay` without value uses `REAL_FALL` (src/csi/gui/__main__.py:68).
2. `start_replay` starts a `FrameSource(live=False)` (src/csi/gui/main_window.py:219-224, 197-208).
3. `_run_replay` loads and analyses the whole file once, then loops forever, emitting precomputed frames at a fixed pace:

`src/csi/gui/frame_source.py:100-121`
```python
    def _run_replay(self):
        try:
            analysis = analyze_recording(load_recording(self._recording_path))
        except Exception as error:
            self.status_changed.emit(f"Replay failed: {error}")
            return
        frames = frames_from_analysis(analysis)
        step = max(1, round(analysis.recording.rate_hz / self._fps))
        interval_s = 1.0 / self._fps
        next_s = time.monotonic()
        index = 0
        while not self.isInterruptionRequested():
            self.frame_ready.emit(frames[index])
            index += step
            if index >= len(frames):
                index = 0
            next_s += interval_s
            delay_s = next_s - time.monotonic()
            if delay_s > 0:
                self.msleep(int(delay_s * 1000))
            else:
                next_s = time.monotonic()
```

4. `load_recording` picks the port key (`p1`, `p2`, `p3`) with the most rows and builds the same `Recording` (src/csi/packets.py:89-96). `.npz` files are saved by `save_recording`, which `record.py` calls (src/csi/packets.py:99-113; src/csi/record.py:58).
5. At 33.51 Hz and 50 FPS, `step = max(1, round(0.67)) = 1`, so replay plays one sample per frame at 50 FPS, i.e. about 1.5x faster than real time (computed: 33.51 / 50; inferred from src/csi/gui/frame_source.py:107-108).

Capture flow (`python -m csi.record`): one thread per serial port reads 256-byte chunks into a per-port `PacketStream` for `--duration` seconds (default 20), then `save_recording` writes `p1..pN` into a compressed `.npz` (src/csi/record.py:13-25, 41-58). Default output `src/csi/data/capture_real.npz` (src/csi/record.py:34).

## Conventions and gotchas

- **Constants at the top, named, no magic numbers.** Every threshold is a module constant (`SLOPE_ACTIVE`, `IMPACT_SLOPE`, `STILL_WINDOW_S` ...) (src/csi/fall_detector.py:23-33; src/csi/dsp.py:11-21).
- **Immutability.** Data carriers are `@dataclass(frozen=True)` or `NamedTuple` (`Packet`, `Recording`, `Detection`, `Analysis`, `Frame`) and updated with `dataclasses.replace` (src/csi/packets.py:25-39; src/csi/gui/frames.py:140, 147).
- **No comments.** The Python files under `src/csi` contain no `#` comments (checked with grep); names carry the meaning, so read the constants.
- **Two empty-room thresholds.** `EMPTY_ROOM_STD_SIMULATED = 0.20` is used if `rate_hz >= 100`, else `EMPTY_ROOM_STD_HARDWARE = 11.0` (src/csi/fall_detector.py:30-32, 75). Anything real at ~30-50 Hz uses 11.0; test A has std 9.60 and only passes as "empty" by a small margin.
- **Sampling rate is derived, not fixed.** README says ~30-50 Hz hardware (README.md:183); measured here: 52.47 (A), 27.80 (B), 33.51 (C). Firmware `vTaskDelay(1)` with `CONFIG_FREERTOS_HZ=100` is a 10 ms tick, so about 100 probes/s at most per node (src/firmware/esp32_csi_node/main/main.c:100-103; src/firmware/esp32_csi_node/sdkconfig:1045).
  > Note: `firmware/.../README.md` says 250 Hz transmission (src/firmware/esp32_csi_node/README.md:4); with a 100 Hz tick the code cannot do that (inferred).
- **Node id is a compile-time `#define`.** Flash three times, editing `NODE_ID` (main.c:16; src/firmware/esp32_csi_node/README.md:10-15). The current checkout has `NODE_ID 3`.
- **UART0 is also the console.** The firmware installs the UART driver on `UART_NUM_0` at 921600 while the console default is 115200 (main.c:18-19; sdkconfig:866). Log text (`ESP_LOGI`) can be interleaved with frames; the magic search in `PacketStream` is what makes that survivable (main.c:164) (inferred).
- **Magic-only framing, no checksum** (see the Note in layer 2).
- **Live mode has no tests.** There is no `tests/` directory; verification is the offscreen screenshot suite, which asserts the replay reaches the CALM, MOVING, IMPACT and ALARM phases (src/csi/gui/screenshots.py:16-31).
- **Stale docs.** `README.md` still mentions Hampel as step one, "Levenberg-Marquardt" (code uses `least_squares(..., method="trf")`, src/csi/localization.py:26) but its latency of 3.0 s is correct for the real recording (3.016 s); `docs/Plans/cv-patterns-integration.md:50,71` says a separate 2.54 s figure is simulation-only. Trust the code.
- **`from csi.simulator import ...` inside `localization.py`** makes the localizer depend on simulator constants (src/csi/localization.py:7).
- **Ports.** `DEFAULT_PORTS = ("/dev/ttyUSB1", "/dev/ttyUSB0", "/dev/ttyUSB2")` while `record.py` defaults to `/dev/ttyUSB0`, `/dev/ttyUSB1`, none (src/csi/packets.py:14; src/csi/record.py:30-32). The GUI `--port` default is `DEFAULT_PORTS[0]` = `/dev/ttyUSB1` while README example uses `/dev/ttyUSB0`.
- **Live window mixing nodes.** `LiveTracker` analyses only the node with the most packets in the window, never combining nodes (src/csi/gui/frames.py:136); the "3 links" geometry exists only in simulation and plots.

## Where to start

Setup (from README.md:130-166): everything runs from `src/` with the repo virtualenv.

```bash
cd src && ../.venv/bin/python -m csi.gui --replay
cd src && ../.venv/bin/python -m csi.gui.screenshots
cd src && ../.venv/bin/python -m csi.figures synthetic
cd src && ../.venv/bin/python -m csi.figures real
```

Firmware: `idf.py set-target esp32` then `idf.py -p /dev/ttyUSB0 flash monitor` after setting `NODE_ID` (src/firmware/esp32_csi_node/README.md:19-30). No unit test suite exists; use the screenshots command as the GUI check, and this snippet to check the detector against the real file:

```bash
cd src && ../.venv/bin/python -c "from csi.packets import REAL_FALL, load_recording; from csi.dsp import analyze_recording; print(analyze_recording(load_recording(REAL_FALL)).detection)"
```

Expected: `impact_time_s` about 4.3455 and `alarm_time_s` about 7.3613 (value computed from this checkout).

Exercises:

1. **Change the stillness window.** Edit `STILL_WINDOW_S` in `src/csi/fall_detector.py:28`. Latency moves with it (it is a sample count, so seconds depend on packet timing). Re-run the one-liner above and `csi.figures real`.
2. **Add a field to the GUI `Frame`** (say, RSSI-smoothed). Touch `Frame` and `_frames` in `src/csi/gui/frames.py:33-48, 92-108`, then consume it in the right widget's `show_frame` (`src/csi/gui/status_panel.py:165`, `charts.py:46, 85`, `room_map.py:53`).
3. **Re-enable Hampel filtering.** `remove_outliers` exists (src/csi/dsp.py:38-48) but `analyze_recording` does not call it (only `figures.py:100` does); call it on `recording.amplitude` before `drop_bad_subcarriers` in `analyze_recording` (src/csi/dsp.py:87) and compare the detection on tests A, B and C. Check that test A still stays under the 11.0 empty-room threshold.
4. **Use all three links on hardware.** Replace the single `{"node": motion}` in `analyze_recording` (src/csi/dsp.py:91) with a motion signal per node; `detect_fall` already accepts a dict of several links and the two-link impact rule (src/csi/fall_detector.py:71-84). The blocker is that nodes have different timestamps and rates, which the code does not align (inferred).
