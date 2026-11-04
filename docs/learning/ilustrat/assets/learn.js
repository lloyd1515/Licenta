/* Ajutoare comune pentru paginile ilustrate. Fiecare pagină setează pe <body>: data-file (calea din src/) și data-root (calea relativă către folderul ilustrat/). */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var G = !reduce && typeof window.gsap !== "undefined" ? window.gsap : null;

  var ORDER = [
    { g: "1 · Baza pachetului csi", items: [
      ["csi/__init__.py", 1, "Marchează folderul csi ca pachet Python."],
      ["csi/gui/__init__.py", 1, "Marchează folderul gui ca subpachet."],
      ["csi/room.py", 1, "Constantele camerei și drumul în plus.", "../room-ilustrat.html"],
    ]},
    { g: "2 · Firmware ESP32", items: [
      ["firmware/esp32_csi_node/CMakeLists.txt", 1, "Declară proiectul ESP-IDF."],
      ["firmware/esp32_csi_node/main/CMakeLists.txt", 1, "Declară componenta main."],
      ["firmware/esp32_csi_node/sdkconfig.defaults", 1, "Pornește CSI în configurație."],
      ["firmware/esp32_csi_node/main/Kconfig.projbuild", 1, "Meniul pentru Wi-Fi și UDP."],
      ["firmware/esp32_csi_node/sdkconfig", 2, "Configurația completă, generată."],
      ["firmware/esp32_csi_node/README.md", 2, "Instrucțiuni și formatul pachetului."],
      ["firmware/esp32_csi_node/main/main.c", 3, "Codul care rulează pe placă."],
    ]},
    { g: "3 · Date și transport UDP", items: [
      ["csi/packets.py", 3, "Formatul pachetului de 138 de octeți."],
      ["csi/data/test_A_camera_goala.npz", 2, "Înregistrare reală: cameră goală."],
      ["csi/data/test_B_mers_normal.npz", 2, "Înregistrare reală: mers."],
      ["csi/data/test_C_cadere_reala.npz", 2, "Înregistrare reală: cădere."],
      ["csi/record.py", 2, "Captură UDP salvată pe disc."],
      ["csi/udp_sim.py", 2, "Trei noduri false care trimit UDP."],
    ]},
    { g: "4 · Simulare și procesare de semnal", items: [
      ["csi/simulator.py", 3, "Scenariul simulat și CSI-ul lui."],
      ["csi/localization.py", 2, "Poziția din trei drumuri în plus."],
      ["csi/dsp.py", 3, "Filtre, PCA și spectrogramă."],
      ["csi/fall_detector.py", 3, "Automatul de stări pentru cădere."],
    ]},
    { g: "5 · Aplicația desktop (PyQt6)", items: [
      ["csi/gui/frames.py", 3, "Cadrele pe care le afișează aplicația."],
      ["csi/gui/frame_source.py", 3, "Firul care produce cadre."],
      ["csi/gui/theme.py", 2, "Culorile și stilurile aplicației."],
      ["csi/gui/charts.py", 3, "Cascada și graficul Doppler."],
      ["csi/gui/status_panel.py", 3, "Starea, înălțimea și cardurile."],
      ["csi/gui/room_map.py", 4, "Harta camerei cu zone Fresnel."],
      ["csi/gui/main_window.py", 4, "Fereastra care leagă totul."],
      ["csi/gui/__main__.py", 2, "Pornirea aplicației din terminal."],
      ["csi/gui/screenshots.py", 2, "Capturi automate de ecran."],
    ]},
    { g: "6 · Figuri și teste", items: [
      ["csi/figures.py", 4, "Cele 7 figuri pentru lucrare."],
      ["tests/test_udp_transport.py", 3, "Testele pentru transportul UDP."],
    ]},
    { g: "7 · Video Remotion", items: [
      ["simulation-remotion/package.json", 1, "Bibliotecile și comenzile proiectului video."],
      ["simulation-remotion/package-lock.json", 1, "Versiunile exacte, generate."],
      ["simulation-remotion/tsconfig.json", 1, "Regulile compilatorului TypeScript."],
      ["simulation-remotion/src/index.ts", 1, "Punctul de intrare Remotion."],
      ["simulation-remotion/src/Root.tsx", 1, "Compoziția video: 1920 × 1080, 30 FPS."],
      ["simulation-remotion/src/MainScene.tsx", 1, "Scena 3D plus stratul de text."],
      ["simulation-remotion/src/layout.ts", 2, "Culori, noduri și link-uri 3D."],
      ["simulation-remotion/src/timeline.ts", 4, "Cele 5 acte ale videoclipului."],
      ["simulation-remotion/src/HumanModel.tsx", 2, "Omul 3D: cap, corp, inele."],
      ["simulation-remotion/src/SubcarrierStrings.tsx", 2, "Corzile care vibrează."],
      ["simulation-remotion/src/SecurityCamera.tsx", 2, "Camera video refuzată."],
      ["simulation-remotion/src/SummaryCards.tsx", 2, "Cele 4 carduri finale."],
      ["simulation-remotion/src/Scene3D.tsx", 3, "Obiectele 3D și lumina."],
      ["simulation-remotion/src/Hud.tsx", 3, "Panourile de text peste video."],
    ]},
  ];

  var FLAT = [];
  ORDER.forEach(function (grp) { grp.items.forEach(function (it) { FLAT.push({ p: it[0], lvl: it[1], d: it[2], href: it[3] || it[0] + ".html", g: grp.g }); }); });

  function el(tag, attrs, parent, txt) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (txt !== undefined) e.textContent = txt;
    if (parent) parent.appendChild(e);
    return e;
  }
  function svg(id, vb, label) {
    var host = typeof id === "string" ? document.getElementById(id) : id;
    return el("svg", { viewBox: vb, role: "img", "aria-label": label || "" }, host);
  }
  var KIND = {
    signal: ["var(--soft-signal)", "var(--signal)"], reflect: ["var(--soft-reflect)", "var(--reflect)"],
    good: ["var(--soft-good)", "var(--good)"], alert: ["var(--soft-alert)", "var(--alert)"],
    violet: ["var(--soft-violet)", "var(--violet)"], plain: ["var(--bg)", "var(--line)"], muted: ["var(--bg)", "var(--muted)"],
  };
  function text(p, x, y, str, o) {
    o = o || {};
    var t = el("text", { x: x, y: y, "text-anchor": o.a || "middle", "font-size": o.s || 13, class: o.cls, style: o.c ? "fill:" + o.c : null, "font-weight": o.b ? 600 : null }, p);
    String(str).split("\n").forEach(function (line, i) { el("tspan", { x: x, dy: i === 0 ? 0 : (o.s || 13) * 1.25 }, t, line); });
    return t;
  }
  function fit(str, w, size) { var n = Math.max.apply(null, String(str).split("\n").map(function (l) { return l.length; })); return Math.max(8.5, Math.min(size, (w - 12) / (n * 0.61))); }
  function box(p, x, y, w, h, title, o) {
    o = o || {};
    var k = KIND[o.k || "signal"];
    var g = el("g", { class: o.cls, "data-tip": o.tip }, p);
    el("rect", { x: x, y: y, width: w, height: h, rx: o.r === undefined ? 5 : o.r, fill: k[0], stroke: k[1], "stroke-width": o.sw || 1.5 }, g);
    var lines = String(title).split("\n").length + (o.sub ? String(o.sub).split("\n").length : 0);
    var y0 = y + h / 2 - (lines - 1) * 8 + 4;
    text(g, x + w / 2, y0, title, { s: fit(title, w, o.s || 14), b: true });
    if (o.sub) text(g, x + w / 2, y0 + String(title).split("\n").length * 17, o.sub, { s: fit(o.sub, w, 11.5), cls: "muted" });
    return g;
  }
  function arrow(p, x1, y1, x2, y2, o) {
    o = o || {};
    var c = o.c || "var(--muted)";
    var g = el("g", { class: o.cls }, p);
    el("line", { x1: x1, y1: y1, x2: x2, y2: y2, stroke: c, "stroke-width": o.w || 2, "stroke-dasharray": o.dash }, g);
    var a = Math.atan2(y2 - y1, x2 - x1), hl = 9;
    el("path", { d: "M" + (x2 - hl * Math.cos(a - 0.45)) + " " + (y2 - hl * Math.sin(a - 0.45)) + " L" + x2 + " " + y2 + " L" + (x2 - hl * Math.cos(a + 0.45)) + " " + (y2 - hl * Math.sin(a + 0.45)), fill: "none", stroke: c, "stroke-width": o.w || 2 }, g);
    if (o.label) text(g, (x1 + x2) / 2 + (o.lx || 0), (y1 + y2) / 2 + (o.ly === undefined ? -8 : o.ly), o.label, { s: 11.5, cls: "muted" });
    return g;
  }
  function along(pts, t) {
    var lens = [], total = 0;
    for (var i = 1; i < pts.length; i++) { var l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); lens.push(l); total += l; }
    var d = t * total;
    for (var j = 0; j < lens.length; j++) {
      if (d <= lens[j] || j === lens.length - 1) { var f = lens[j] ? Math.min(d / lens[j], 1) : 0; return [pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f]; }
      d -= lens[j];
    }
    return pts[pts.length - 1];
  }
  function travel(p, pts, o) {
    o = o || {};
    var dot = el("circle", { r: o.r || 7, fill: o.c || "var(--reflect)", cx: pts[0][0], cy: pts[0][1] }, p);
    if (!G) return dot;
    var st = { t: 0 };
    G.to(st, { t: 1, duration: o.dur || 4, ease: "none", repeat: -1, repeatDelay: o.delay || 0.6, onUpdate: function () { var q = along(pts, st.t); dot.setAttribute("cx", q[0]); dot.setAttribute("cy", q[1]); } });
    return dot;
  }
  /* Pipeline: steps = [{t, s, k}], rânduri de câte o.cols. */
  function flow(id, steps, o) {
    o = o || {};
    var W = o.w || 800, cols = o.cols || Math.min(steps.length, 4), gap = o.gap || 44, pad = 6, bh = o.bh || 72, rg = o.rg || 46;
    var bw = (W - 2 * pad - (cols - 1) * gap) / cols, rows = Math.ceil(steps.length / cols);
    var H = rows * bh + (rows - 1) * rg + 2 * pad + (o.extraH === undefined ? 14 : o.extraH);
    var s = svg(id, "0 0 " + W + " " + H, o.label);
    var centers = [];
    steps.forEach(function (st, i) {
      var r = Math.floor(i / cols), c = i % cols, x = pad + c * (bw + gap), y = pad + r * (bh + rg);
      var g = box(s, x, y, bw, bh, st.t, { k: st.k, sub: st.s, s: o.fs || 14, tip: st.tip });
      centers.push([x + bw / 2, y + bh / 2, x, y]);
      if (i > 0) {
        var pc = centers[i - 1];
        if (Math.floor((i - 1) / cols) === r) arrow(s, pc[2] + bw + 3, pc[1], x - 3, y + bh / 2, { label: st.via });
        else { el("polyline", { points: pc[0] + "," + (pc[3] + bh) + " " + pc[0] + "," + (pc[3] + bh + rg / 2) + " " + (x + bw / 2) + "," + (pc[3] + bh + rg / 2), fill: "none", stroke: "var(--muted)", "stroke-width": 2 }, s); arrow(s, x + bw / 2, pc[3] + bh + rg / 2, x + bw / 2, y - 3, { label: st.via, lx: 40, ly: 4 }); }
      }
    });
    if (o.dot !== false && steps.length > 1) {
      var pts = [];
      centers.forEach(function (c, i) {
        if (i > 0 && Math.floor((i - 1) / cols) !== Math.floor(i / cols)) { var pc = centers[i - 1]; pts.push([pc[0], pc[3] + bh + rg / 2]); pts.push([c[0], pc[3] + bh + rg / 2]); }
        pts.push([c[0], c[3] + bh + 8]);
      });
      travel(s, pts, { dur: o.dur || steps.length * 1.1, r: 5 });
    }
    if (o.tipId) tips(s, o.tipId);
    return { s: s, centers: centers, bw: bw, bh: bh };
  }
  /* Grafic: o = {w,h,xmin,xmax,ymin,ymax,xticks,yticks,xlabel,ylabel,series:[{x?,y,c,w,dash,o}],hlines,vlines,bands} */
  function plot(id, o) {
    var W = o.w || 800, H = o.h || 230, m = { l: o.ml || 52, r: 14, t: 16, b: o.mb || 36 };
    var s = svg(id, "0 0 " + W + " " + H, o.label);
    var sx = function (x) { return m.l + (x - o.xmin) / (o.xmax - o.xmin) * (W - m.l - m.r); };
    var sy = function (y) { return H - m.b - (y - o.ymin) / (o.ymax - o.ymin) * (H - m.t - m.b); };
    el("rect", { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "none", stroke: "var(--line)" }, s);
    (o.bands || []).forEach(function (b) {
      el("rect", { x: sx(b.x0), y: m.t, width: Math.max(1, sx(b.x1) - sx(b.x0)), height: H - m.t - m.b, fill: b.c || "var(--soft-reflect)" }, s);
      if (b.label) text(s, (sx(b.x0) + sx(b.x1)) / 2, m.t + 14, b.label, { s: 11.5, cls: "muted" });
    });
    (o.xticks || []).forEach(function (v) { el("line", { x1: sx(v), y1: H - m.b, x2: sx(v), y2: H - m.b + 5, stroke: "var(--muted)" }, s); text(s, sx(v), H - m.b + 18, o.xfmt ? o.xfmt(v) : v, { s: 11, cls: "muted" }); });
    (o.yticks || []).forEach(function (v) { el("line", { x1: m.l - 5, y1: sy(v), x2: m.l, y2: sy(v), stroke: "var(--muted)" }, s); text(s, m.l - 8, sy(v) + 4, o.yfmt ? o.yfmt(v) : v, { s: 11, cls: "muted", a: "end" }); });
    if (o.xlabel) text(s, W - m.r, H - 4, o.xlabel, { s: 11, cls: "muted", a: "end" });
    if (o.ylabel) text(s, m.l + 4, m.t - 4 + 0, o.ylabel, { s: 11, cls: "muted", a: "start" });
    var g = el("g", {}, s), over = el("g", {}, s);
    (o.hlines || []).forEach(function (h) {
      el("line", { x1: m.l, x2: W - m.r, y1: sy(h.y), y2: sy(h.y), stroke: h.c || "var(--alert)", "stroke-width": 2, "stroke-dasharray": h.dash || "6 4" }, over);
      if (h.label) text(over, W - m.r - 4, sy(h.y) - 5, h.label, { s: 11.5, a: "end", c: h.c || "var(--alert)" });
    });
    (o.vlines || []).forEach(function (v) {
      el("line", { x1: sx(v.x), x2: sx(v.x), y1: m.t, y2: H - m.b, stroke: v.c || "var(--alert)", "stroke-width": 2, "stroke-dasharray": v.dash || "5 4" }, over);
      if (v.label) text(over, sx(v.x) + 5, m.t + (v.ly || 28), v.label, { s: 11.5, a: "start", c: v.c || "var(--alert)" });
    });
    function draw(series) {
      while (g.firstChild) g.removeChild(g.firstChild);
      series.forEach(function (se) {
        var d = "";
        for (var i = 0; i < se.y.length; i++) {
          var xv = se.x ? se.x[i] : (se.x0 || 0) + i * (se.dx || 1);
          d += (i ? " L" : "M") + sx(xv).toFixed(1) + " " + sy(Math.max(o.ymin, Math.min(o.ymax, se.y[i]))).toFixed(1);
        }
        el("path", { d: d, fill: "none", stroke: se.c || "var(--signal)", "stroke-width": se.w || 2, "stroke-dasharray": se.dash, opacity: se.o, "stroke-linejoin": "round" }, g);
      });
    }
    draw(o.series || []);
    return { s: s, sx: sx, sy: sy, draw: draw, g: g, over: over, m: m, W: W, H: H };
  }
  /* Octeți: fields = [{n, b, k, d}] */
  function bytes(id, fields, o) {
    o = o || {};
    var total = fields.reduce(function (a, f) { return a + f.b; }, 0);
    var W = o.w || 800, pad = 8, H = o.h || 130, x = pad, minw = o.minw === undefined ? 64 : o.minw, avail = W - 2 * pad;
    var small = fields.filter(function (f) { return f.b / total * avail < minw; });
    var bigBytes = total - small.reduce(function (a, f) { return a + f.b; }, 0);
    var unit = (avail - small.length * minw) / (bigBytes || 1);
    var widths = fields.map(function (f) { return f.b / total * avail < minw ? minw : f.b * unit; });
    var s = svg(id, "0 0 " + W + " " + H, o.label);
    var off = 0;
    fields.forEach(function (f, i) {
      var w = widths[i], g = el("g", { "data-tip": f.n + " · " + f.b + (f.b === 1 ? " octet" : " octeți") + " · " + f.d, tabindex: 0, class: "bf" }, s);
      var k = KIND[f.k || "signal"];
      el("rect", { x: x, y: 30, width: w - 1, height: 44, fill: k[0], stroke: k[1], "stroke-width": 1.5, rx: 3 }, g);
      if (w > 40) { text(g, x + w / 2, 50, f.n, { s: fit(f.n, w, 12.5), b: true }); text(g, x + w / 2, 66, f.b + " B", { s: 11, cls: "muted" }); }
      else { var ly = i % 2 ? 98 : 112; el("line", { x1: x + w / 2, y1: 74, x2: x + w / 2, y2: ly - 12, stroke: k[1] }, g); text(g, x + w / 2, ly, f.n + " (" + f.b + ")", { s: 11 }); }
      if (o.offsets !== false) text(s, x + 2, 22, off, { s: 10.5, cls: "muted", a: "start" });
      x += w; off += f.b;
    });
    text(s, W - pad, 22, total, { s: 10.5, cls: "muted", a: "end" });
    if (small.length) text(s, W / 2, H - 6, "câmpurile mici sunt lărgite ca să se poată citi; lățimea nu este la scară", { s: 10.5, cls: "muted" });
    if (o.tipId) tips(s, o.tipId);
    return s;
  }
  /* Automat: nodes = [{id,label,x,y,k,w}], edges = [{a,b,label,bend,lx,ly}] */
  function states(id, nodes, edges, o) {
    o = o || {};
    var s = svg(id, o.vb || "0 0 800 300", o.label), byId = {}, gs = {};
    var defs = el("defs", {}, s), mk = el("marker", { id: "ah-" + (typeof id === "string" ? id : "x"), viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0 0 L10 5 L0 10 z", fill: "var(--muted)" }, mk);
    nodes.forEach(function (n) { byId[n.id] = n; });
    edges.forEach(function (e) {
      var a = byId[e.a], b = byId[e.b], mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2, bend = e.bend || 0;
      var dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
      var cx = mx + nx * bend, cy = my + ny * bend;
      var ra = (a.w || 120) / 2 + 4, rb = (b.w || 120) / 2 + 4;
      var sa = shrink(a.x, a.y, cx, cy, ra, 26), sb = shrink(b.x, b.y, cx, cy, rb, 26);
      el("path", { d: "M" + sa[0] + " " + sa[1] + " Q" + cx + " " + cy + " " + sb[0] + " " + sb[1], fill: "none", stroke: "var(--muted)", "stroke-width": 1.8, "marker-end": "url(#ah-" + (typeof id === "string" ? id : "x") + ")" }, s);
      if (e.label) text(s, cx + (e.lx || 0), cy + (e.ly || 0), e.label, { s: 11, cls: "muted" });
    });
    nodes.forEach(function (n) { gs[n.id] = box(s, n.x - (n.w || 120) / 2, n.y - 24, n.w || 120, 48, n.label, { k: n.k || "plain", s: 13, sub: n.sub }); });
    function shrink(x, y, tx, ty, rx, ry) { var dx = tx - x, dy = ty - y, l = Math.hypot(dx, dy) || 1, ux = dx / l, uy = dy / l; var t = Math.min(rx / Math.abs(ux || 1e-6), ry / Math.abs(uy || 1e-6)); return [x + ux * t, y + uy * t]; }
    return {
      s: s,
      set: function (id2) {
        Object.keys(gs).forEach(function (k) { var r = gs[k].querySelector("rect"); r.setAttribute("stroke-width", k === String(id2) ? 4 : 1.5); r.setAttribute("stroke", k === String(id2) ? "var(--reflect)" : (KIND[byId[k].k || "plain"])[1]); });
      },
    };
  }
  /* Hartă de culoare pe canvas: cols = [[v pe rând]...], valori 0..vmax. */
  var RAMP = [[13, 8, 135], [84, 2, 163], [139, 10, 165], [185, 50, 137], [219, 92, 104], [244, 136, 73], [254, 188, 43], [240, 249, 33]];
  function color(f) { f = Math.max(0, Math.min(1, f)); var p = f * (RAMP.length - 1), i = Math.floor(p), k = p - i, a = RAMP[i], b = RAMP[Math.min(i + 1, RAMP.length - 1)]; return "rgb(" + Math.round(a[0] + (b[0] - a[0]) * k) + "," + Math.round(a[1] + (b[1] - a[1]) * k) + "," + Math.round(a[2] + (b[2] - a[2]) * k) + ")"; }
  function heat(id, cols, o) {
    o = o || {};
    var host = document.getElementById(id), c = document.createElement("canvas");
    var nx = cols.length, ny = cols[0].length, vmin = o.vmin || 0, vmax = o.vmax || 99;
    c.width = nx; c.height = ny; c.style.width = "100%"; c.style.height = (o.h || 200) + "px"; c.style.imageRendering = "pixelated"; c.style.borderRadius = "4px"; c.setAttribute("role", "img"); c.setAttribute("aria-label", o.label || "");
    var ctx = c.getContext("2d");
    for (var x = 0; x < nx; x++) for (var y = 0; y < ny; y++) { ctx.fillStyle = color((cols[x][y] - vmin) / (vmax - vmin)); ctx.fillRect(x, ny - 1 - y, 1, 1); }
    host.appendChild(c);
    return c;
  }
  function tips(root, tipId) {
    var tip = document.getElementById(tipId);
    if (!tip) return;
    root.querySelectorAll("[data-tip]").forEach(function (n) {
      var show = function () { tip.textContent = n.getAttribute("data-tip"); };
      n.addEventListener("mouseenter", show); n.addEventListener("focus", show); n.addEventListener("click", show);
      if (!n.hasAttribute("tabindex")) n.setAttribute("tabindex", 0);
    });
  }
  function toggle(sel, cb) {
    var btns = document.querySelectorAll(sel);
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        btns.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        cb(b.dataset, b);
      });
    });
    var first = Array.prototype.filter.call(btns, function (b) { return b.getAttribute("aria-pressed") === "true"; })[0] || btns[0];
    if (first) cb(first.dataset, first);
  }
  function rng(seed) {
    var a = seed >>> 0;
    var r = function () { a |= 0; a = (a + 0x6d2b79f5) | 0; var t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    r.n = function () { var u = 1 - r(), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
    return r;
  }
  function loop(fn) { if (G) G.ticker.add(fn); else fn(0); }
  function range(n, f) { var out = []; for (var i = 0; i < n; i++) out.push(f ? f(i) : i); return out; }

  function short(p) { var a = p.split("/"); return a[a.length - 1] === "__init__.py" ? a.slice(-2).join("/") : a[a.length - 1]; }
  function chrome() {
    var b = document.body, file = b.getAttribute("data-file"), root = b.getAttribute("data-root") || "./";
    var header = document.querySelector("header.page");
    if (header && file) {
      var nav = document.createElement("div");
      nav.className = "crumbs";
      nav.innerHTML = '<a href="' + root + 'index.html">← Toate fișierele</a><span>src/' + file + "</span>";
      header.insertBefore(nav, header.firstChild);
    }
    var main = document.querySelector("main");
    var idx = FLAT.map(function (f) { return f.p; }).indexOf(file);
    if (main && idx >= 0) {
      var pg = document.createElement("nav");
      pg.className = "pager";
      pg.setAttribute("aria-label", "Fișier anterior și următor");
      var prev = FLAT[idx - 1], next = FLAT[idx + 1];
      pg.innerHTML = (prev ? '<a href="' + root + prev.href + '">← ' + short(prev.p) + "</a>" : "<span></span>") +
        (next ? '<a href="' + root + next.href + '">' + short(next.p) + " →</a>" : "<span></span>");
      main.appendChild(pg);
    }
    var list = document.getElementById("file-index");
    if (list) {
      ORDER.forEach(function (grp) {
        var sec = document.createElement("section");
        sec.className = "card";
        var h = document.createElement("h2"); h.textContent = grp.g; sec.appendChild(h);
        var wrap = document.createElement("div"); wrap.className = "tablewrap";
        var t = document.createElement("table"); t.className = "t";
        t.innerHTML = "<thead><tr><th>Fișier</th><th>Nivel</th><th>Ce face</th></tr></thead>";
        var tb = document.createElement("tbody");
        grp.items.forEach(function (it) {
          var tr = document.createElement("tr");
          tr.innerHTML = '<td class="m"><a href="' + (it[3] || it[0] + ".html") + '">' + it[0] + '</a></td><td><span class="lvl">' + "●".repeat(it[1]) + "○".repeat(4 - it[1]) + "</span></td><td>" + it[2] + "</td>";
          tb.appendChild(tr);
        });
        t.appendChild(tb); wrap.appendChild(t); sec.appendChild(wrap); list.appendChild(sec);
      });
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", chrome); else chrome();

  window.L = { heat: heat, color: color, el: el, svg: svg, text: text, box: box, arrow: arrow, along: along, travel: travel, flow: flow, plot: plot, bytes: bytes, states: states, tips: tips, toggle: toggle, rng: rng, loop: loop, range: range, G: G, reduce: reduce, ORDER: ORDER };
})();
