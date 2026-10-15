// c3: the GUI's show_frame (src/csi/gui/main_window.py) and the try-it-yourself challenge (src/csi/fall_detector.py).
Kit.module("c3", (K) => {
  const NS = "http://www.w3.org/2000/svg";
  const ramp = (t, a, b) => (b <= a ? (t >= a ? 1 : 0) : Math.min(1, Math.max(0, (t - a) / (b - a))));
  const shade = (e, p) => e.setAttribute("opacity", String(p));
  const node = (s, tag, attrs, style) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    for (const k in (style || {})) e.style.setProperty(k, style[k]);
    s.appendChild(e);
    return e;
  };
  const label = (s, x, y, str, attrs, style) => {
    const e = node(s, "text", { x, y, ...(attrs || {}) }, { "font-size": "36px", "font-weight": "650", fill: "var(--ink)", ...(style || {}) });
    e.textContent = str;
    return e;
  };

  // A full-stage SVG drawn in the scene's group, so its coordinates are stage pixels.
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

  const S = "c3-show";
  K.scene("c3-show", () => {
    K.code({
      title: "src/csi/gui/main_window.py", lang: "python", x: 60, y: 240, font: 36,
      lines: [
        "    def show_frame(self, frame: Frame):",
        "        self.frame_count += 1",
        "",
        "        self.room_map.show_frame(frame)",
        "        self.doppler_plot.show_frame(frame)",
        "        self.waterfall.show_frame(frame)",
        "        self.status_panel.show_frame(frame)",
        "",
        "        if not frame.alarm:",
        "            self.alarm_dismissed = False",
        "        elif not self.alarm_dismissed:",
        "            self.show_alarm(frame.latency_s)",
      ],
      glow: [
        { line: 0, from: S + "|show frame runs", until: S + "|room map" },
        { line: 3, from: S + "|room map", until: S + "|two charts" },
        { line: 4, from: S + "|two charts", until: [S + "|two charts", 0.9] },
        { line: 5, from: [S + "|two charts", 0.9], until: S + "|status panel" },
        { line: 6, from: S + "|status panel", until: S + "|if the result says" },
        { line: 8, from: S + "|if the result says", until: S + "|red banner" },
        { line: 11, from: S + "|red banner" },
      ],
    });
    const callouts = [
      [S, S + "|room map", K.mono("show_frame") + " runs: a new frame has arrived", undefined],
      [S + "|room map", S + "|two charts", "Redraws the room map", undefined],
      [S + "|two charts", S + "|status panel", "Redraws the doppler chart, then the waterfall", undefined],
      [S + "|status panel", S + "|if the result says", "Updates the status panel", undefined],
      [S + "|if the result says", S + "|One honest detail", "Alarm set: the red banner appears", undefined],
      [S + "|One honest detail", S + "|does not measure", "The little figure is a drawing of the stage", undefined],
      [S + "|does not measure", undefined, "It does not measure where the person is", "warn"],
    ];
    for (const [at, until, html, tone] of callouts) {
      K.text(html, { size: "text", x: 1110, y: 260, w: 750, at, until, tone });
    }

    const g = K.group({});
    const tRoom = K.t(S + "|room map");
    const tTwo = K.t(S + "|two charts");
    const tStat = K.t(S + "|status panel");
    const tAlarm = K.t(S + "|if the result says");
    const tRed = K.t(S + "|red banner");
    const tFig = K.t(S + "|little figure");
    picture(g, (s) => {
      node(s, "rect", { x: 1110, y: 610, width: 750, height: 390, rx: 22 }, { fill: "var(--card)", stroke: "var(--border)", "stroke-width": "3" });
      const banner = node(s, "rect", { x: 1130, y: 630, width: 710, height: 56, rx: 12 }, { fill: "var(--bad)" });
      const bannerTxt = label(s, 1485, 670, "ALARM", { "text-anchor": "middle" }, { fill: "var(--bg)", "font-weight": "750", "font-size": "40px" });
      const tiles = [
        { x: 1130, y: 700, name: "room map", at: tRoom, until: tTwo },
        { x: 1500, y: 700, name: "doppler plot", at: tTwo, until: tTwo + 0.9 },
        { x: 1130, y: 856, name: "waterfall", at: tTwo + 0.9, until: tStat },
        { x: 1500, y: 856, name: "status panel", at: tStat, until: tAlarm + 3 },
      ];
      const rects = tiles.map((tile) => {
        const r = node(s, "rect", { x: tile.x, y: tile.y, width: 350, height: 136, rx: 14 }, { fill: "var(--bg2)", stroke: "var(--border)", "stroke-width": "3" });
        label(s, tile.x + 18, tile.y + 118, tile.name, {}, { "font-size": "32px", fill: "var(--muted)", "font-weight": "600" });
        return r;
      });
      const figure = node(s, "circle", { cx: 1250, cy: 760, r: 16 }, { fill: "var(--muted)" });
      return (t) => {
        const b = ramp(t, tRed, tRed + 0.4);
        banner.setAttribute("y", (630 - 40 * (1 - b)).toFixed(1));
        banner.setAttribute("opacity", String(b));
        bannerTxt.setAttribute("y", (670 - 40 * (1 - b)).toFixed(1));
        shade(bannerTxt, b);
        tiles.forEach((tile, k) => {
          const lit = t >= tile.at && t < tile.until ? 1 : 0;
          rects[k].style.setProperty("stroke", lit ? "var(--ink)" : "var(--border)");
        });
        shade(figure, ramp(t, tFig, tFig + 0.4));
      };
    });
  });

  const C = "c3-try";
  K.scene("c3-try", () => {
    K.code({
      title: "Run from the repository root", lang: "bash", x: 60, y: 240, font: 36,
      lines: ["cd src && ../.venv/bin/python -m csi.gui --replay"],
      glow: [{ line: 0, from: C + "|run the app in replay mode", until: C + "|Then a challenge" }],
      until: C + "|Then a challenge",
    });
    K.text("Replays this recorded fall on a loop, no hardware", { size: "text", x: 60, y: 440, w: 1700, at: C + "|plays this exact", until: C + "|Then a challenge" });

    K.code({
      title: "src/csi/fall_detector.py", lang: "python", x: 60, y: 240, slide: 0,
      lines: ["STILL_WINDOW_S = 2.5"],
      glow: [{ line: 0, from: C + "|in the fall detector" }],
      at: C + "|in the fall detector", until: [C + "|to 1.0 seconds", 0.35],
    });
    K.code({
      title: "src/csi/fall_detector.py", lang: "python", x: 60, y: 240, slide: 0,
      lines: ["STILL_WINDOW_S = 1.0"],
      glow: [{ line: 0, from: C + "|to 1.0 seconds" }],
      at: C + "|to 1.0 seconds",
    });
    K.text("How long to watch after the jerk before judging still", { size: "text", x: 60, y: 440, w: 1700, at: C + "|in the fall detector", until: C + "|to 1.0 seconds" });
    K.text("A shorter wait: the check comes sooner", { size: "text", x: 60, y: 440, w: 1700, at: C + "|to 1.0 seconds", until: C + "|Does the alarm come sooner" });

    K.chips([
      { text: "alarm sooner?", at: C + "|Does the alarm come sooner" },
      { text: "rings when someone sits?", at: C + "|ring when someone just sits" },
    ], { x: 60, y: 640, gap: 24 });
  });
});
