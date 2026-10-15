// c2: open the envelope (packets.py _parse, PacketStream.feed), the spreadsheet (packets.py _recording),
// drop broken stations (dsp.py drop_bad_subcarriers). Code cards on top, plain callouts under them, a live picture.
Kit.module("c2", (K) => {
  const clamp = (v) => Math.max(0, Math.min(1, v));
  const ramp = (t, a, d) => clamp((t - a) / d);
  const on = (t, a, b) => (t >= a && t < b ? 1 : 0);
  const hash = (a) => {
    const s = Math.sin(a) * 43758.5453;
    return s - Math.floor(s);
  };
  const layer = (root) => {
    const el = document.createElement("div");
    el.className = "k-abs";
    el.style.cssText = "left:0px;top:0px;width:1920px;height:1080px;";
    root.appendChild(el);
    return el;
  };
  const box = (parent, x, y, w, h, bg) => {
    const d = document.createElement("div");
    d.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:${bg};border-radius:4px;`;
    parent.appendChild(d);
    return d;
  };
  const setBox = (d, x, y, w, h, bg, op) => {
    d.style.left = `${x}px`;
    d.style.top = `${y}px`;
    d.style.width = `${w}px`;
    d.style.height = `${h}px`;
    d.style.background = bg;
    d.style.opacity = `${op}`;
  };
  const INK = "#eef1f7";
  const MUTED = "#a9b3c6";
  const FAINT = "#5d6a82";
  const VIOLET = "#c3b1f2";
  const CYAN = "#7fd6e6";
  const BAD = "#ff8f87";

  // ── c2-parse: the header and the 128 reading bytes become 52 kept readings ──────────────────────
  K.scene("c2-parse", () => {
    const S = "c2-parse";
    const A = K.t(S + "|reads the address");
    const B = K.t(S + "|128 reading bytes");
    const C = K.t(S + "|paired up");
    const D = K.t(S + "|52 useful stations");
    const END = K.t(S + "|drops the rest") + 3;
    const X0 = 63;
    const P = 13;
    const TOP = 900;
    const H = 56;
    // 12 pair indexes packet.py slices away: csi[0:6], csi[32], csi[59:64]
    const DROP = new Set([0, 1, 2, 3, 4, 5, 32, 59, 60, 61, 62, 63]);
    const hdr = [];
    const iq = [];
    const pr = [];

    K.custom(
      (root) => {
        const el = layer(root);
        for (let i = 0; i < 10; i++) hdr.push(box(el, X0 + i * P, TOP, 11, H, FAINT));
        for (let j = 0; j < 128; j++) iq.push(box(el, X0 + (10 + j) * P, TOP, 11, H, FAINT));
        for (let p = 0; p < 64; p++) pr.push(box(el, X0 + 130 + p * 26, TOP, 24, H, INK));
        return el;
      },
      (t) => {
        const shown = on(t, A - 0.3, END);
        const m = ramp(t, C, 1.2);
        const d = ramp(t, D, 0.8);
        const hdrLit = t >= A;
        hdr.forEach((el, i) => setBox(el, X0 + i * P, TOP, 11, H, hdrLit ? VIOLET : FAINT, shown));
        iq.forEach((el, j) => {
          const lit = t >= B + (j / 128) * 1.0;
          setBox(el, X0 + (10 + j) * P, TOP, 11, H, lit ? INK : FAINT, shown * (1 - m));
        });
        pr.forEach((el, p) => {
          const k = DROP.has(p) ? 1 - 0.85 * d : 1;
          setBox(el, X0 + 130 + p * 26, TOP, 24, H, INK, shown * m * k);
        });
      }
    );

    K.code({
      title: "src/csi/packets.py:42-47",
      x: 60,
      y: 200,
      font: 30,
      lines: [
        "def _parse(raw):",
        "    _, node_id, rssi_dbm, timestamp_us, seq = struct.unpack(HEADER_FORMAT, raw[:HEADER_BYTES])",
        "    iq = np.frombuffer(raw[HEADER_BYTES:PACKET_BYTES], dtype=np.int8)",
        "    csi = iq[0::2] + 1j * iq[1::2]",
        "    active = np.concatenate([csi[part] for part in ACTIVE_SUBCARRIERS])",
        "    return Packet(node_id, rssi_dbm, timestamp_us, seq, active)",
      ],
      glow: [
        { line: 1, from: S + "|reads the address", until: S + "|128 reading bytes" },
        { line: 2, from: S + "|128 reading bytes", until: S + "|paired up" },
        { line: 3, from: S + "|paired up", until: S + "|52 useful stations" },
        { line: 4, from: S + "|52 useful stations", until: S + "|drops the rest" },
      ],
    });

    K.text(K.mono("node_id") + " = which board sent it", { at: S + "|board number", until: S + "|signal strength", x: 60, y: 752, size: "small" });
    K.text(K.mono("rssi_dbm") + " = how strong the signal is", { at: S + "|signal strength", until: S + "|time", x: 60, y: 752, size: "small" });
    K.text(K.mono("timestamp_us") + " = when it was sent", { at: S + "|time", until: S + "|a counter", x: 60, y: 752, size: "small" });
    K.text(K.mono("seq") + " = a counter", { at: S + "|a counter", until: S + "|small whole numbers", x: 60, y: 752, size: "small" });
    K.text(K.mono("iq") + " = the 128 reading bytes, as numbers", { at: S + "|small whole numbers", until: S + "|paired up", x: 60, y: 752, size: "small" });
    K.text(K.mono("csi") + " = pairs: first + second × j", { at: S + "|paired up", until: S + "|That j just means", x: 60, y: 752, size: "small" });
    K.text(K.mono("j") + " = marks the second number of a pair", { at: S + "|That j just means", until: S + "|52 useful stations", x: 60, y: 752, size: "small" });
    K.text(K.mono("active") + " = keep the 52 useful stations", { at: S + "|52 useful stations", x: 60, y: 752, size: "small" });
  });

  // ── c2-feed: the conveyor belt, find the stamp, wait or cut ──────────────────────────────────────
  K.scene("c2-feed", () => {
    const S = "c2-feed";
    const T0 = K.t(S);
    const STAMP = K.t(S + "|looks for the stamp");
    const DEL = K.t(S + "|gets deleted");
    const WAIT = K.t(S + "|waits for more");
    const OPEN = K.t(S + "|opens that envelope");
    const END = K.t(S + "|cuts it off the belt") + 3;
    const PITCH = 30;
    const SPEED = 40;
    const SLOTS = 64;
    const BELT_Y = 870;
    const TH = 40;
    const slots = [];
    let fillBar = null;
    let beltBg = null;
    let beltTrack = null;

    // per k (global tile index): 0-2 junk, 3-4 the stamp, the rest packet bytes; the pattern repeats every 60
    const kind = (k) => {
      const r = ((k % 60) + 60) % 60;
      if (r < 3) return "junk";
      if (r < 5) return "stamp";
      return "packet";
    };
    const colour = { junk: FAINT, stamp: INK, packet: MUTED };

    K.custom(
      (root) => {
        const el = layer(root);
        beltBg = box(el, 60, BELT_Y - 8, 1800, TH + 16, "#161d2c");
        beltBg.style.border = "3px solid #2a3448";
        for (let i = 0; i < SLOTS; i++) slots.push(box(el, 0, BELT_Y, 24, TH, MUTED));
        beltTrack = box(el, 60, 960, 1140, 14, "#2a3448");
        fillBar = box(el, 60, 960, 1, 14, INK);
        return el;
      },
      (t) => {
        const travel = Math.max(0, t - T0) * SPEED;
        const base = Math.floor(travel / PITCH);
        const sh = travel - base * PITCH;
        const dropped = ramp(t, DEL, 0.8);
        const lifted = ramp(t, OPEN, 0.8);
        const shown = on(t, T0 - 0.3, END);
        slots.forEach((el, i) => {
          const k = base + i;
          const x = 60 + i * PITCH - sh;
          const type = kind(k);
          let y = BELT_Y;
          let op = shown;
          if (type === "junk") {
            y = BELT_Y + 60 * dropped;
            op = shown * (1 - dropped);
          } else if (type === "packet") {
            y = BELT_Y - 20 * lifted;
            op = shown * (1 - 0.8 * lifted);
          }
          const visible = x >= 60 && x <= 1860 ? op : 0;
          setBox(el, x, y, 24, TH, colour[type], visible);
        });
        const fill = clamp((t - WAIT) / (OPEN - WAIT)) * 0.7;
        setBox(fillBar, 60, 960, 1140 * fill, 14, INK, shown);
        beltBg.style.opacity = `${shown}`;
        beltTrack.style.opacity = `${shown}`;
      }
    );

    K.code({
      title: "src/csi/packets.py:58-69",
      x: 60,
      y: 200,
      font: 36,
      lines: [
        "            start = self._buffer.find(_WIRE_MAGIC)",
        "            # ...",
        "            del self._buffer[:start]",
        "            if len(self._buffer) < PACKET_BYTES:",
        "                return packets",
        "            packets.append(_parse(bytes(self._buffer[:PACKET_BYTES])))",
        "            del self._buffer[:PACKET_BYTES]",
      ],
      glow: [
        { line: 0, from: S + "|looks for the stamp", until: S + "|gets deleted" },
        { line: 2, from: S + "|gets deleted", until: S + "|waits for more" },
        { line: 3, from: S + "|waits for more", until: S + "|opens that envelope" },
        { line: 5, from: S + "|opens that envelope", until: S + "|cuts it off the belt" },
        { line: 6, from: S + "|cuts it off the belt" },
      ],
    });

    K.text("stamp = 5A then A5 on the wire, starts every letter", { at: S + "|same stamp", until: S + "|looks for the stamp", x: 60, y: 790, size: "small" });
    K.text(K.mono("start") + " = where the stamp begins", { at: S + "|looks for the stamp", until: S + "|gets deleted", x: 60, y: 790, size: "small" });
    K.text("junk before the stamp: thrown away", { at: S + "|gets deleted", until: S + "|waits for more", x: 60, y: 790, size: "small" });
    K.text("fewer than 138 bytes: wait for more", { at: S + "|waits for more", until: S + "|opens that envelope", x: 60, y: 790, size: "small" });
    K.text("one whole packet: cut off the belt and parsed", { at: S + "|opens that envelope", x: 60, y: 790, size: "small" });
    K.text("138 bytes", { at: S + "|138 bytes", x: 1240, y: 955, size: "small" });
  });

  // ── c2-sheet: one row per letter, keep the arrow lengths ─────────────────────────────────────────
  K.scene("c2-sheet", () => {
    const S = "c2-sheet";
    const START = K.t(S);
    const F0 = K.t(S + "|33 rows a second");
    const F1 = K.t(S + "|669 rows");
    const ROW_HL = K.t(S + "|every row is one moment");
    const COL_HL = K.t(S + "|every column is one station");
    const END = K.t(S + "|every column is one station") + 3;
    const ROWS = 669;
    const COLS = 52;
    const GX = 1260;
    const GY = 430;
    const GW = 600;
    const GH = 570;
    const src = document.createElement("canvas");
    src.width = COLS;
    src.height = ROWS;
    const sc = src.getContext("2d");
    const img = sc.createImageData(COLS, ROWS);
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const v = clamp(0.55 * hash(c * 12.9898 + r * 78.233) + 0.45 * (0.5 + 0.5 * Math.sin(r / 9 + c / 4.5)));
        const o = (r * COLS + c) * 4;
        img.data[o] = 24 + v * 103;
        img.data[o + 1] = 33 + v * 181;
        img.data[o + 2] = 51 + v * 179;
        img.data[o + 3] = 255;
      }
    }
    sc.putImageData(img, 0, 0);
    let cv = null;
    let frame = null;
    let rowHl = null;
    let colHl = null;

    K.custom(
      (root) => {
        const el = layer(root);
        frame = box(el, GX - 2, GY - 2, GW + 4, GH + 4, "transparent");
        frame.style.border = "2px solid #2a3448";
        cv = document.createElement("canvas");
        cv.width = GW;
        cv.height = GH;
        cv.style.cssText = `position:absolute;left:${GX}px;top:${GY}px;width:${GW}px;height:${GH}px;`;
        el.appendChild(cv);
        rowHl = box(el, GX, 0, GW, 3, INK);
        colHl = box(el, GX + 26 * (GW / COLS), GY, GW / COLS, GH, "transparent");
        colHl.style.outline = `3px solid ${INK}`;
        return el;
      },
      (t) => {
        const shown = on(t, START - 0.3, END);
        const fill = clamp((t - F0) / (F1 - F0));
        const k = Math.round(fill * ROWS);
        const ctx = cv.getContext("2d");
        ctx.clearRect(0, 0, GW, GH);
        ctx.imageSmoothingEnabled = false;
        if (k > 0) ctx.drawImage(src, 0, 0, COLS, k, 0, 0, GW, (GH * k) / ROWS);
        cv.style.opacity = `${shown}`;
        frame.style.opacity = `${shown}`;
        const rowY = GY + (334 / ROWS) * GH;
        setBox(rowHl, GX, rowY, GW, 3, INK, shown * (t >= ROW_HL ? 1 : 0) * (t < END ? 1 : 0));
        colHl.style.opacity = `${shown * (t >= COL_HL ? 1 : 0)}`;
      }
    );

    K.code({
      title: "src/csi/packets.py:77",
      x: 60,
      y: 200,
      font: 36,
      lines: ["    amplitude = np.array([np.abs(row) for row in csi_rows], dtype=np.float32)"],
      glow: [{ line: 0, from: S + "|keeps only the arrow lengths" }],
    });

    K.text(K.mono("np.abs(row)") + " = the arrow length, the loudness", { at: S + "|keeps only the arrow lengths", x: 60, y: 450, size: "small" });
    K.text("about 33 rows a second", { at: S + "|33 rows a second", until: S + "|20 seconds", x: 60, y: 560, size: "small" });
    K.text("× 20 seconds", { at: S + "|20 seconds", until: S + "|669 rows", x: 60, y: 560, size: "small" });
    K.text("= 669 rows", { at: S + "|669 rows", until: S + "|52 numbers", x: 60, y: 560, size: "small" });
    K.text("52 columns", { at: S + "|52 numbers", x: 60, y: 700, size: "small" });
    K.text("one row = one moment", { at: S + "|every row is one moment", x: 60, y: 780, size: "small" });
    K.text("one column = one station", { at: S + "|every column is one station", x: 60, y: 860, size: "small" });
  });

  // ── c2-drop: measure each column's wobble, mark the broken ones, remove them ─────────────────────
  K.scene("c2-drop", () => {
    const S = "c2-drop";
    const G0 = K.t(S + "|measures how much each column wobbles");
    const MARKS = K.t(S + "|marks the columns");
    const FAR = K.t(S + "|far too much");
    const REM = K.t(S + "|removes them");
    const END = K.t(S + "|41 good ones stay") + 3;
    const BASE = 995;
    const LO = 50;
    const HI = 150;
    const BAR_W = 12;
    const PITCH = 18;
    // exact columns the recording fails: column 2 and 21-30 (11 of 52); heights are illustrative
    const isRed = (c) => c === 2 || (c >= 21 && c <= 30);
    const height = (c) => (isRed(c) ? (c === 2 ? 25 : 160 + (c % 5) * 5) : 70 + ((c * 37) % 56));
    const goods = [];
    for (let c = 0; c < 52; c++) if (!isRed(c)) goods.push(c);
    const rank = new Map(goods.map((c, g) => [c, g]));
    const bars = [];
    const lines = [];

    K.custom(
      (root) => {
        const el = layer(root);
        for (let c = 0; c < 52; c++) bars.push(box(el, 60 + c * PITCH, BASE, BAR_W, 0, FAINT));
        lines.push(box(el, 60, BASE - LO, 936, 0, "transparent"));
        lines.push(box(el, 60, BASE - HI, 936, 0, "transparent"));
        return el;
      },
      (t) => {
        const hi = on(t, G0 - 0.3, END);
        const dropK = ramp(t, REM, 0.8);
        const moveK = ramp(t, REM + 0.7, 0.8);
        bars.forEach((el, c) => {
          const grow = ramp(t, G0 + c * 0.012, 0.6);
          const h = height(c) * grow;
          const red = isRed(c) && t >= FAR;
          let x = 60 + c * PITCH;
          let y = BASE - h;
          let op = hi;
          if (isRed(c)) {
            y += 60 * dropK;
            op = hi * (1 - dropK);
          } else {
            const g = rank.get(c);
            x = (60 + c * PITCH) * (1 - moveK) + (60 + g * (936 / goods.length)) * moveK;
          }
          setBox(el, x, y, BAR_W, h, red ? BAD : MUTED, op);
        });
        const lineOn = t >= MARKS ? hi : 0;
        setBox(lines[0], 60, BASE - LO, 936, 3, FAINT, lineOn);
        setBox(lines[1], 60, BASE - HI, 936, 3, FAINT, lineOn);
      }
    );

    K.code({
      title: "src/csi/dsp.py:51-56",
      x: 60,
      y: 200,
      font: 32,
      lines: [
        "def drop_bad_subcarriers(amplitude):",
        "    variance = np.var(amplitude, axis=0)",
        "    valid = (variance >= MIN_SUBCARRIER_VARIANCE) & (variance <= MAX_SUBCARRIER_VARIANCE)",
        "    if not np.any(valid):",
        "        return amplitude",
        "    return amplitude[:, valid]",
      ],
      glow: [
        { line: 1, from: S + "|measures how much each column wobbles", until: S + "|marks the columns" },
        { line: 2, from: S + "|marks the columns", until: S + "|removes them" },
        { line: 5, from: S + "|removes them" },
      ],
    });

    K.text(K.mono("variance") + " = one wobble score per column", { at: S + "|measures how much each column wobbles", until: S + "|called the variance", x: 60, y: 735, size: "small" });
    K.text(K.term("variance") + " = how much a line wobbles", { at: S + "|called the variance", until: S + "|marks the columns", x: 60, y: 735, size: "small" });
    K.text(K.mono("valid") + " = which columns are the good ones", { at: S + "|marks the columns", until: S + "|removes them", x: 60, y: 735, size: "small" });
    K.text(K.mono("amplitude[:, valid]") + " = keep only the good columns", { at: S + "|removes them", x: 60, y: 735, size: "small" });
    K.text("11 go", { at: S + "|11 columns go", until: S + "|41 good ones stay", x: 1180, y: 800, size: "big" });
    K.text("41 stay", { at: S + "|41 good ones stay", x: 1180, y: 870, size: "big" });
    K.text("heights illustrative", { at: S + "|measures how much each column wobbles", x: 1180, y: 950, size: "small" });
  });
});
