// d2: the equalizer, PCA, the jerk, the stages and the still check (src/csi/dsp.py, src/csi/fall_detector.py).
Kit.module("d2", (K) => {
  const NS = "http://www.w3.org/2000/svg";
  const ramp = (t, a, b) => (b <= a ? (t >= a ? 1 : 0) : Math.min(1, Math.max(0, (t - a) / (b - a))));
  const lerp = (a, b, p) => a + (b - a) * p;

  // A full-stage SVG drawn in the scene's group, so its coordinates are stage pixels. draw(svg) runs once and
  // returns render(t), a pure function of t.
  const picture = (g, draw) => {
    let render = () => {};
    K.custom(() => {
      const s = document.createElementNS(NS, "svg");
      s.setAttribute("viewBox", "0 0 1920 1080");
      s.setAttribute("width", "1920");
      s.setAttribute("height", "1080");
      s.style.position = "absolute";
      s.style.left = "0";
      s.style.top = "0";
      s.style.overflow = "visible";
      g.el.appendChild(s);
      render = draw(s);
      return s;
    }, (t) => render(t));
  };
  const node = (s, tag, attrs, style) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    for (const k in (style || {})) e.style.setProperty(k, style[k]);
    s.appendChild(e);
    return e;
  };
  const label = (s, x, y, str, attrs, style) => {
    const e = node(s, "text", { x, y, ...(attrs || {}) }, { "font-size": "44px", "font-weight": "650", fill: "var(--ink)", ...(style || {}) });
    e.textContent = str;
    return e;
  };
  const shade = (e, p) => e.setAttribute("opacity", String(p));

  const S = "d2-band";
  K.scene("d2-band", () => {
    K.code({
      title: "src/csi/dsp.py", lang: "python", x: 60, y: 240, font: 30,
      lines: [
        "def bandpass(amplitude, rate_hz, low_hz=BAND_LOW_HZ, high_hz=BAND_HIGH_HZ):",
        "    nyquist_hz = 0.5 * rate_hz",
        "    high_hz = min(high_hz, rate_hz / NYQUIST_MARGIN)",
        "    b, a = signal.butter(BAND_ORDER, [low_hz / nyquist_hz, high_hz / nyquist_hz], btype=\"band\")",
        "    return signal.filtfilt(b, a, amplitude, axis=0)",
      ],
      glow: [
        { line: 3, from: S + "|butter designs", until: S + "|between 0.2" },
        { line: 0, from: S + "|between 0.2", until: S + "|filtfilt runs" },
        { line: 4, from: S + "|filtfilt runs" },
      ],
    });
    const callouts = [
      [S + "|butter designs", S + "|between 0.2", K.mono("signal.butter") + " designs the filter: the equalizer's shape"],
      [S + "|between 0.2", S + "|Times per second", "Keeps only wobbles from 0.2 to 12 a second"],
      [S + "|Times per second", S + "|filtfilt runs", K.term("hertz") + " = times per second"],
      [S + "|filtfilt runs", undefined, K.mono("filtfilt") + " runs the filter forwards, then backwards"],
    ];
    for (const [at, until, html] of callouts) K.text(html, { size: "text", x: 1000, y: 640, w: 860, at, until });

    const g = K.group({});
    const tA = K.t(S + "|butter designs");
    const tB = K.t(S + "|keeps wobbles");
    const tF = K.t(S + "|forwards");
    picture(g, (s) => {
      node(s, "rect", { x: 60, y: 610, width: 880, height: 390, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      const before = label(s, 90, 660, "before the filter", {}, { "font-size": "40px", fill: "var(--muted)" });
      const after = label(s, 90, 660, "after the filter", {}, { "font-size": "40px", fill: "var(--muted)" });
      const pathRaw = node(s, "path", { fill: "none", "stroke-width": "5", "stroke-linejoin": "round" }, { stroke: "var(--accent)" });
      const pts = 200;
      const shape = (u, m) => {
        const drift = 55 * Math.sin(2 * Math.PI * 0.6 * u);
        const wobble = 30 * Math.sin(2 * Math.PI * 7 * u + 0.4);
        const jitter = 16 * Math.sin(2 * Math.PI * 55 * u + 1.1);
        return lerp(drift + wobble + jitter, wobble, m);
      };
      const forward = node(s, "line", { "stroke-width": "6", "stroke-linecap": "round" }, { stroke: "var(--accent)" });
      const headF = node(s, "circle", { r: 12 }, { fill: "var(--accent)" });
      const backward = node(s, "line", { "stroke-width": "6", "stroke-linecap": "round" }, { stroke: "var(--violet)" });
      const headB = node(s, "circle", { r: 12 }, { fill: "var(--violet)" });
      const fwdLabel = label(s, 120, 935, "forwards", {}, { "font-size": "40px", fill: "var(--accent)" });
      const bwdLabel = label(s, 880, 935, "backwards", { "text-anchor": "end" }, { "font-size": "40px", fill: "var(--violet)" });
      return (t) => {
        const m = ramp(t, tA, tB);
        let d = "";
        for (let k = 0; k <= pts; k++) {
          const u = k / pts;
          const x = 90 + u * 820;
          const y = 800 - shape(u, m);
          d += (k === 0 ? "M" : "L") + x.toFixed(1) + " " + y.toFixed(1) + " ";
        }
        pathRaw.setAttribute("d", d);
        shade(before, 1 - ramp(t, tB - 0.3, tB + 0.3));
        shade(after, ramp(t, tB - 0.3, tB + 0.3));
        const pF = ramp(t, tF, tF + 1.2);
        const pB = ramp(t, tF + 1.2, tF + 2.4);
        const xF = lerp(120, 880, pF);
        const xB = lerp(880, 120, pB);
        forward.setAttribute("x1", "120"); forward.setAttribute("y1", "965");
        forward.setAttribute("x2", xF.toFixed(1)); forward.setAttribute("y2", "965");
        shade(forward, pF > 0 ? 1 : 0);
        headF.setAttribute("cx", xF.toFixed(1)); headF.setAttribute("cy", "965");
        shade(headF, pF > 0 && pB === 0 ? 1 : 0);
        backward.setAttribute("x1", "880"); backward.setAttribute("y1", "965");
        backward.setAttribute("x2", xB.toFixed(1)); backward.setAttribute("y2", "965");
        shade(backward, pB > 0 ? 1 : 0);
        headB.setAttribute("cx", xB.toFixed(1)); headB.setAttribute("cy", "965");
        shade(headB, pB > 0 ? 1 : 0);
        shade(fwdLabel, ramp(t, tF, tF + 0.3));
        shade(bwdLabel, ramp(t, tF + 1.2, tF + 1.5));
      };
    });
  });

  const P = "d2-pca";
  K.scene("d2-pca", () => {
    K.code({
      title: "src/csi/dsp.py", lang: "python", x: 60, y: 240, font: 34,
      lines: [
        "def motion_signal(amplitude):",
        "    centered = amplitude - np.mean(amplitude, axis=0)",
        "    covariance = np.cov(centered, rowvar=False)",
        "    _, eigenvectors = np.linalg.eigh(covariance)",
        "    return np.dot(centered, eigenvectors[:, -1])",
      ],
      glow: [
        { line: 1, from: P + "|centres every column", until: P + "|next lines find" },
        { line: 2, from: P + "|next lines find", until: P + "|lean together most" },
        { line: 3, from: P + "|lean together most", until: P + "|projects onto it" },
        { line: 4, from: P + "|projects onto it" },
      ],
    });
    const callouts = [
      [P + "|centres every column", P + "|next lines find", "Each column shifted so its average is zero"],
      [P + "|next lines find", P + "|lean together most", K.mono("covariance") + ": how much the columns move together"],
      [P + "|lean together most", P + "|projects onto it", "The direction they lean together most"],
      [P + "|projects onto it", P + "|trick is called", "Each moment becomes one number: the motion line"],
      [P + "|trick is called", undefined, K.term("PCA") + ": find the main shared direction"],
    ];
    for (const [at, until, html] of callouts) K.text(html, { size: "text", x: 1240, y: 250, w: 620, at, until });

    const g = K.group({});
    const tS = K.t(P + "|41 lines");
    const tC = K.t(P + "|centres every column");
    const tP = K.t(P + "|projects onto it");
    const tM = K.t(P + "|the motion line");
    picture(g, (s) => {
      node(s, "rect", { x: 60, y: 640, width: 1800, height: 360, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      const countLbl = label(s, 90, 690, "41 lines", {}, { "font-size": "40px", fill: "var(--muted)" });
      const zero = node(s, "line", { x1: 90, x2: 1830, y1: 800, y2: 800, "stroke-dasharray": "10 10", "stroke-width": "2" }, { stroke: "var(--muted)" });
      const fans = [];
      const N = 41;
      for (let i = 0; i < N; i++) fans.push(node(s, "path", { fill: "none", "stroke-width": "2" }, { stroke: "var(--accent)" }));
      const bold = node(s, "path", { fill: "none", "stroke-width": "7", "stroke-linejoin": "round" }, { stroke: "var(--accent)" });
      const motionLbl = label(s, 1830, 930, "motion line", { "text-anchor": "end" }, { "font-size": "44px", fill: "var(--accent)" });
      const common = (u) => 22 * Math.sin(2 * Math.PI * 1.2 * u + 0.5) + 12 * Math.sin(2 * Math.PI * 3 * u);
      const pts = 120;
      return (t) => {
        const appear = ramp(t, tS, tS + 0.6);
        const c = ramp(t, tC, tC + 0.8);
        const p = ramp(t, tP, tP + 0.8);
        shade(countLbl, ramp(t, tS, tS + 0.3));
        shade(zero, c);
        for (let i = 0; i < N; i++) {
          const off = (((i * 37) % 41) - 20) * 5.2;
          const phase = i * 1.3;
          const freq = 2 + (i % 7) * 0.5;
          let d = "";
          for (let k = 0; k <= pts; k++) {
            const u = k / pts;
            const y = 800 + off * (1 - c) + common(u) + 14 * Math.sin(2 * Math.PI * freq * u + phase) * (1 - 0.7 * c);
            d += (k === 0 ? "M" : "L") + (90 + u * 1740).toFixed(1) + " " + y.toFixed(1) + " ";
          }
          fans[i].setAttribute("d", d);
          shade(fans[i], appear * (1 - p) * 0.6);
        }
        let db = "";
        for (let k = 0; k <= pts; k++) {
          const u = k / pts;
          db += (k === 0 ? "M" : "L") + (90 + u * 1740).toFixed(1) + " " + (800 + common(u)).toFixed(1) + " ";
        }
        bold.setAttribute("d", db);
        shade(bold, p);
        shade(motionLbl, ramp(t, tM, tM + 0.4));
      };
    });
  });

  const L = "d2-slope";
  K.scene("d2-slope", () => {
    K.code({
      title: "src/csi/fall_detector.py", lang: "python", x: 60, y: 240, font: 32,
      lines: [
        "def _normalized(motion):",
        "    return motion / (np.max(np.abs(motion)) + NORMALIZE_EPSILON)",
        "",
        "",
        "def _slopes(normalized, rate_hz):",
        "    return np.abs(np.gradient(normalized, 1.0 / rate_hz))",
      ],
      glow: [
        { line: 1, from: L + "|rescaled so its biggest", until: L + "|gradient measures" },
        { line: 5, from: L + "|gradient measures" },
      ],
    });
    const callouts = [
      [L + "|rescaled so its biggest", L + "|gradient measures", "Biggest swing set to 1: any room fits one rule"],
      [L + "|gradient measures", L + "|steeper than 17.5", K.mono("gradient") + ": how steep the line is, every moment"],
      [L + "|steeper than 17.5", L + "|hits 17.63", "Steeper than this is a hard impact"],
      [L + "|hits 17.63", L + "|only 3 moments", "Just over the line: a close call"],
      [L + "|only 3 moments", undefined, "Only 3 moments in the whole recording go this steep"],
    ];
    for (const [at, until, html] of callouts) K.text(html, { size: "text", x: 1160, y: 660, w: 700, at, until });
    K.chips([{ text: "⚙️ IMPACT_SLOPE = 17.5", at: L + "|steeper than 17.5", tone: "muted" }], { x: 1160, y: 900 });

    const g = K.group({});
    const tS = K.t(L);
    const tI = K.t(L + "|hits 17.63");
    const tE = K.t(L + "|a close call");
    const tTh = K.t(L + "|steeper than 17.5");
    const tOnly = K.t(L + "|only 3 moments");
    const uI = 0.5;
    const motion = (u) => {
      if (u < uI) return 0.3 * Math.sin(2 * Math.PI * 38 * u) + 0.1 * Math.sin(2 * Math.PI * 90 * u + 1);
      const d = u - uI;
      const spike = Math.exp(-Math.pow(d / 0.006, 2)) - 0.5 * Math.exp(-Math.pow((d - 0.012) / 0.006, 2));
      return spike + 0.04 * Math.sin(2 * Math.PI * 12 * u);
    };
    const slope = (u) => 1.2 + 1.8 * Math.abs(Math.sin(2 * Math.PI * 38 * u)) + 16.43 * Math.exp(-Math.pow((u - uI) / 0.012, 2));
    const X = (u) => 90 + u * 870;
    const Y = (m) => 820 - 110 * m;
    const yMeter = (v) => 980 - (v / 20) * 330;
    picture(g, (s) => {
      node(s, "rect", { x: 60, y: 650, width: 960, height: 350, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      const pts = 300;
      let full = "";
      for (let k = 0; k <= pts; k++) {
        const u = k / pts;
        full += (k === 0 ? "M" : "L") + X(u).toFixed(1) + " " + Y(motion(u)).toFixed(1) + " ";
      }
      node(s, "path", { d: full, fill: "none", "stroke-width": "3" }, { stroke: "var(--muted)", opacity: "0.45" });
      const done = node(s, "path", { fill: "none", "stroke-width": "4", "stroke-linejoin": "round" }, { stroke: "var(--accent)" });
      const cursor = node(s, "line", { y1: 660, y2: 990, "stroke-width": "3", "stroke-dasharray": "8 6" }, { stroke: "var(--ink)" });
      const dots = [];
      for (let k = -1; k <= 1; k++) dots.push(node(s, "circle", { r: 7, cx: X(uI + k * 0.002).toFixed(1), cy: Y(motion(uI + k * 0.002)).toFixed(1) }, { fill: "var(--warn)" }));
      node(s, "rect", { x: 1000, y: 650, width: 50, height: 330, rx: 8 }, { fill: "var(--bg2)", stroke: "var(--border)", "stroke-width": "3" });
      const fill = node(s, "rect", { x: 1000, width: 50, rx: 8 }, { fill: "var(--accent)" });
      const thY = yMeter(17.5);
      const th = node(s, "line", { x1: 990, x2: 1060, y1: thY, y2: thY, "stroke-dasharray": "8 6", "stroke-width": "3" }, { stroke: "var(--muted)" });
      const thLbl = label(s, 1066, thY + 14, "17.5", {}, { "font-size": "40px", fill: "var(--muted)" });
      const readout = label(s, 990, 690, "steepness 17.63", { "text-anchor": "end" }, { "font-size": "40px", fill: "var(--ink)" });
      return (t) => {
        const uNow = t < tI ? 0.5 * ramp(t, tS, tI) : 0.5 + 0.5 * ramp(t, tI + 1.0, tE);
        let dd = "";
        const steps = 120;
        for (let k = 0; k <= steps; k++) {
          const u = (k / steps) * uNow;
          dd += (k === 0 ? "M" : "L") + X(u).toFixed(1) + " " + Y(motion(u)).toFixed(1) + " ";
        }
        done.setAttribute("d", dd);
        cursor.setAttribute("x1", X(uNow).toFixed(1));
        cursor.setAttribute("x2", X(uNow).toFixed(1));
        const v = slope(uNow);
        const h = Math.max(0, ((v / 20) * 330));
        fill.setAttribute("y", (980 - h).toFixed(1));
        fill.setAttribute("height", h.toFixed(1));
        fill.style.setProperty("fill", v > 17.5 ? "var(--warn)" : "var(--accent)");
        shade(thLbl, ramp(t, tTh, tTh + 0.3));
        shade(th, ramp(t, tTh, tTh + 0.3));
        shade(readout, t >= tI ? 1 : 0);
        for (const d of dots) shade(d, ramp(t, tOnly, tOnly + 0.3));
      };
    });
  });

  const F = "d2-fsm";
  K.scene("d2-fsm", () => {
    K.code({
      title: "src/csi/fall_detector.py", lang: "python", x: 60, y: 240, font: 32,
      lines: [
        "    for i in range(1, count):",
        "        if state in (FallState.CALM, FallState.MOVING):",
        "            if active_links[i] >= min_links and has_impact_slope[i]:",
        "                state = FallState.IMPACT",
        "                impact_index = i",
        "        # ...",
        "        elif state == FallState.IMPACT:",
        "            state = FallState.CHECKING_STILL",
        "        elif state == FallState.CHECKING_STILL:",
        "            if i - impact_index >= still_samples:",
      ],
      glow: [
        { line: 0, from: F + "|loop over every moment", until: F + "|steep enough" },
        { line: 2, from: F + "|steep enough", until: F + "|becomes impact" },
        { line: 3, from: F + "|becomes impact", until: F + "|switches to checking" },
        { line: 7, from: F + "|switches to checking", until: F + "|Then it waits" },
        { line: 9, from: F + "|counts readings" },
      ],
    });
    const callouts = [
      [F, F + "|steep enough", "Checks each moment, one after another"],
      [F + "|steep enough", F + "|becomes impact", "Steep enough, and enough links agree"],
      [F + "|becomes impact", F + "|switches to checking", K.mono("IMPACT") + " is the new state"],
      [F + "|switches to checking", F + "|counts readings", "Next moment: now checking if still"],
      [F + "|counts readings", undefined, "Counts readings until the still window is full"],
    ];
    for (const [at, until, html] of callouts) K.text(html, { size: "small", x: 1450, y: 250, w: 400, at, until });

    K.flow({
      nodes: {
        calm: { label: "CALM", x: 60, y: 850, w: 170, tone: "accent", dimAt: F + "|becomes impact" },
        moving: { label: "MOVING", x: 390, y: 850, w: 210 },
        impact: { label: "IMPACT", x: 760, y: 850, w: 210, tone: "accent", toneAt: F + "|becomes impact", dimAt: F + "|switches to checking" },
        checking: { label: "CHECKING_STILL", x: 1090, y: 850, w: 470, tone: "accent", toneAt: F + "|switches to checking still" },
        alarm: { label: "ALARM", x: 1690, y: 850, w: 170 },
      },
      edges: [
        { from: "calm", to: "moving", label: "moving", at: F },
        { from: "moving", to: "impact", label: "steep", at: F + "|steep enough" },
        { from: "impact", to: "checking", label: "next", at: F + "|switches to checking still" },
        { from: "checking", to: "alarm", label: "still", dashed: true, at: F },
      ],
    });
  });

  const T = "d2-still";
  K.scene("d2-still", () => {
    K.code({
      title: "src/csi/fall_detector.py", lang: "python", x: 60, y: 240, font: 34,
      lines: [
        "def _is_still(normalized, impact_index, i, settle_samples):",
        "    window_start = impact_index + settle_samples",
        "    variances = [np.var(signal[window_start:i]) for signal in normalized]",
        "    return np.mean(variances) < STILL_MAX_VARIANCE",
      ],
      glow: [
        { line: 2, from: T + "|measures how much", until: T + "|far below the limit" },
        { line: 3, from: T + "|far below the limit" },
      ],
    });
    const callouts = [
      [T, T + "|Then is still", "Counting readings for the still window"],
      [T + "|Then is still", T + "|Here the wobble", "Measures how much the line wobbled since the jerk"],
      [T + "|Here the wobble", T + "|Alarm, at", "Far below 0.2: the person is not getting up"],
      [T + "|Alarm, at", T + "|From the jerk", "Alarm: a fall is confirmed"],
      [T + "|From the jerk", undefined, "From the jerk to the alarm: about 3 seconds"],
    ];
    for (const [at, until, html] of callouts) K.text(html, { size: "text", x: 60, y: 580, w: 1800, at, until });

    const g = K.group({});
    const tCount = K.t(T + "|It counts 83");
    const tCountEnd = K.t(T + "|two and a half seconds");
    const tWob = K.t(T + "|wobble is 0.06");
    const tLim = K.t(T + "|limit of 0.2");
    const tAlarm = K.t(T + "|at about seven");
    const tJerk = K.t(T + "|From the jerk");
    const tTook = K.t(T + "|took about 3");
    picture(g, (s) => {
      node(s, "rect", { x: 60, y: 640, width: 460, height: 350, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      node(s, "rect", { x: 580, y: 640, width: 700, height: 350, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      node(s, "rect", { x: 1340, y: 640, width: 520, height: 350, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });

      label(s, 90, 690, "readings", {}, { "font-size": "40px", fill: "var(--muted)" });
      const count = label(s, 90, 840, "0", {}, { "font-size": "150px", "font-weight": "750", fill: "var(--ink)" });
      const counted = label(s, 90, 930, "about 2.5 s", {}, { "font-size": "44px", fill: "var(--muted)" });

      label(s, 610, 690, "wobble", {}, { "font-size": "40px", fill: "var(--muted)" });
      node(s, "rect", { x: 610, y: 730, width: 600, height: 40, rx: 8 }, { fill: "var(--bg2)", stroke: "var(--border)", "stroke-width": "3" });
      const bar = node(s, "rect", { x: 610, y: 730, width: 0, height: 40, rx: 8 }, { fill: "var(--accent)" });
      const wobVal = label(s, 610, 800, "0.06", {}, { "font-size": "52px", "font-weight": "750", fill: "var(--ink)" });
      const limit = node(s, "line", { x1: 1210, x2: 1210, y1: 715, y2: 785, "stroke-width": "4", "stroke-dasharray": "8 6" }, { stroke: "var(--muted)" });
      const limLbl = label(s, 1210, 700, "0.2", { "text-anchor": "middle" }, { "font-size": "40px", fill: "var(--muted)" });
      const chip = label(s, 610, 900, "⚙️ STILL_MAX_VARIANCE = 0.20", {}, { "font-size": "40px", fill: "var(--muted)" });

      const alarmBox = node(s, "rect", { x: 1420, y: 650, width: 360, height: 62, rx: 18 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "4" });
      const alarmText = label(s, 1600, 694, "ALARM", { "text-anchor": "middle" }, { "font-size": "46px", "font-weight": "750", fill: "var(--ink)" });
      node(s, "line", { x1: 1380, x2: 1820, y1: 850, y2: 850, "stroke-width": "4" }, { stroke: "var(--muted)" });
      const jerkDot = node(s, "circle", { cx: 1380, cy: 850, r: 12 }, { fill: "var(--ink)" });
      const alarmDot = node(s, "circle", { cx: 1800, cy: 850, r: 12 }, { fill: "var(--bad)" });
      const jerkLbl = label(s, 1380, 910, "jerk", { "text-anchor": "middle" }, { "font-size": "40px", fill: "var(--muted)" });
      const alarmLbl = label(s, 1800, 910, "alarm", { "text-anchor": "middle" }, { "font-size": "40px", fill: "var(--muted)" });
      const bracket = node(s, "line", { x1: 1380, x2: 1800, y1: 800, y2: 800, "stroke-width": "4" }, { stroke: "var(--accent)" });
      const bracketLbl = label(s, 1590, 784, "about 3 s", { "text-anchor": "middle" }, { "font-size": "40px", fill: "var(--accent)" });

      return (t) => {
        const c = ramp(t, tCount, tCountEnd);
        count.textContent = String(Math.round(c * 83));
        shade(counted, ramp(t, tCountEnd, tCountEnd + 0.3));
        const w = ramp(t, tWob, tWob + 1.0);
        bar.setAttribute("width", (600 * (0.06 / 0.2) * w).toFixed(1));
        shade(wobVal, ramp(t, tWob, tWob + 0.3));
        shade(limit, ramp(t, tLim, tLim + 0.3));
        shade(limLbl, ramp(t, tLim, tLim + 0.3));
        shade(chip, ramp(t, tLim, tLim + 0.3));
        const a = ramp(t, tAlarm, tAlarm + 0.3);
        alarmBox.style.setProperty("fill", a > 0 ? "var(--bad)" : "var(--card)");
        alarmBox.style.setProperty("stroke", a > 0 ? "var(--bad)" : "var(--border)");
        alarmText.style.setProperty("fill", a > 0 ? "var(--bg)" : "var(--ink)");
        shade(alarmDot, a);
        shade(alarmLbl, ramp(t, tAlarm, tAlarm + 0.3));
        shade(jerkDot, ramp(t, tJerk, tJerk + 0.3));
        shade(jerkLbl, ramp(t, tJerk, tJerk + 0.3));
        shade(bracket, ramp(t, tTook, tTook + 0.3));
        shade(bracketLbl, ramp(t, tTook, tTook + 0.3));
      };
    });
  });
});
