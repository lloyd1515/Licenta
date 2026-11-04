/* Ajutoare și animații pentru conceptele de bază din main.c.html: octeți, copiere în C, CSI, RSSI. Datele sunt simulate. */
(function () {
  "use strict";
  var E = L.el, T = L.text;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var KIND = {
    signal: ["var(--soft-signal)", "var(--signal)"], reflect: ["var(--soft-reflect)", "var(--reflect)"],
    good: ["var(--soft-good)", "var(--good)"], alert: ["var(--soft-alert)", "var(--alert)"],
    plain: ["var(--bg)", "var(--line)"],
  };
  var A = window.A = {};
  A.reduce = !!reduce;

  A.$ = function (id) { return document.getElementById(id); };
  A.set = function (e, o) { for (var k in o) e.setAttribute(k, o[k]); };
  A.ease = function (x) { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
  A.rnd = function (n) { var x = Math.sin(n * 12.9898) * 43758.5453; return x - Math.floor(x); };
  A.paint = function (c, kind) { var K = KIND[kind || "plain"]; A.set(c.r, { fill: K[0], stroke: K[1] }); };
  A.cell = function (s, x, y, w, h, label, fs) {
    var r = E("rect", { x: x, y: y, width: w, height: h, rx: 3, fill: "var(--bg)", stroke: "var(--line)", "stroke-width": 1.5 }, s);
    return { r: r, t: T(s, x + w / 2, y + h / 2 + 4, label, { s: fs || 12 }) };
  };
  /* draw(t, first): t în secunde; first este true la început și după restart. */
  A.run = function (hostId, draw, still) {
    var host = A.$(hostId), t0 = null, vis = true, ctl = {};
    var fixed = still === undefined ? 3 : still;
    ctl.restart = function () { t0 = null; if (reduce) draw(fixed, true); };
    if (reduce) { draw(fixed, true); return ctl; }
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { vis = e[0].isIntersecting; }).observe(host);
    function tick(ts) {
      var first = t0 === null;
      if (first) t0 = ts;
      if (vis) draw((ts - t0) / 1000, first);
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    return ctl;
  };
  A.toggle = function (ids, cb) {
    var els = ids.map(A.$);
    function pick(n) { els.forEach(function (b, j) { b.setAttribute("aria-pressed", j === n); }); cb(n); }
    els.forEach(function (b, j) { b.addEventListener("click", function () { pick(j); }); });
    return pick;
  };
  A.clip = function (s, id, x, y, w, h) { var c = E("clipPath", { id: id }, s); E("rect", { x: x, y: y, width: w, height: h }, c); return "url(#" + id + ")"; };
  A.pool = function (s, n, clip, kind) {
    var K = KIND[kind], a = [];
    for (var i = 0; i < n; i++) a.push(E("rect", { rx: 3, fill: K[0], stroke: K[1], "stroke-width": 1.5, opacity: 0, "clip-path": clip }, s));
    return a;
  };
  /* Pune intervalele [a,b] (în secunde) pe o axă care curge spre stânga. xr = marginea dreaptă, pps = pixeli pe secundă. */
  A.place = function (pool, ivs, now, xr, pps, y, h) {
    pool.forEach(function (r, i) {
      var v = ivs[i];
      if (!v) { r.setAttribute("opacity", 0); return; }
      A.set(r, { x: xr - (now - v[0]) * pps, width: Math.max(1, (v[1] - v[0]) * pps), y: y, height: h, opacity: 1 });
    });
  };

  /* 1 · biți, octeți, hex */
  (function () {
    if (!A.$("c-bytes-f")) return;
    var s = L.svg("c-bytes-f", "0 0 800 300", "Biții lui 0xA55A, cifrele hex și ordinea octeților în memorie");
    var bits = "1010010101011010", hex = ["A", "5", "5", "A"], cells = [], i;
    T(s, 64, 63, "binar", { a: "end", s: 12, cls: "muted" }); T(s, 64, 115, "hex", { a: "end", s: 12, cls: "muted" });
    for (i = 0; i < 16; i++) cells.push(A.cell(s, 80 + i * 40, 40, 36, 36, bits[i], 15));
    var hx = hex.map(function (h, j) { return A.cell(s, 82 + j * 160, 92, 152, 36, h, 16); });
    T(s, 240, 152, "octet mare 0xA5", { s: 12, cls: "muted" }); T(s, 560, 152, "octet mic 0x5A", { s: 12, cls: "muted" });
    T(s, 350, 186, "adresa 0", { s: 12, cls: "muted" }); T(s, 450, 186, "adresa 1", { s: 12, cls: "muted" });
    var m0 = A.cell(s, 300, 194, 100, 44, "··", 16), m1 = A.cell(s, 400, 194, 100, 44, "··", 16);
    T(s, 280, 221, "memorie", { a: "end", s: 12, cls: "muted" });
    function token(txt) {
      var g = E("g", { opacity: 0 }, s);
      E("rect", { x: -28, y: -14, width: 56, height: 28, rx: 5, fill: "var(--soft-reflect)", stroke: "var(--reflect)", "stroke-width": 1.5 }, g);
      T(g, 0, 5, txt, { b: true, s: 14 });
      return g;
    }
    var tLow = token("5A"), tHigh = token("A5");
    var cap = T(s, 400, 276, "", { s: 13 });
    function fly(g, a, b, p, on) {
      A.set(g, { opacity: on ? 1 : 0, transform: "translate(" + (a[0] + (b[0] - a[0]) * p) + "," + (a[1] + (b[1] - a[1]) * p) + ")" });
    }
    A.run("c-bytes-f", function (t) {
      var u = t % 11, ni = u < 4.8 ? Math.floor(u / 1.2) : -1;
      cells.forEach(function (c, k) { A.paint(c, Math.floor(k / 4) === ni ? "signal" : "plain"); });
      hx.forEach(function (c, j) { A.paint(c, j === ni ? "signal" : "plain"); });
      var p0 = A.ease((u - 5.2) / 1.4), p1 = A.ease((u - 6.8) / 1.4);
      fly(tLow, [560, 58], [350, 216], p0, u >= 5.2 && p0 < 1);
      fly(tHigh, [240, 58], [450, 216], p1, u >= 6.8 && p1 < 1);
      m0.t.textContent = p0 >= 1 ? "5A" : "··"; m1.t.textContent = p1 >= 1 ? "A5" : "··";
      A.paint(m0, p0 >= 1 ? "reflect" : "plain"); A.paint(m1, p1 >= 1 ? "reflect" : "plain");
      cap.textContent = ni >= 0 ? "Grupul " + bits.substr(ni * 4, 4) + " este cifra hex " + hex[ni] + "." : "Memoria primește întâi octetul mic 5A, apoi octetul mare A5.";
    }, 8);
  })();

  /* 2 · memset și memcpy */
  (function () {
    if (!A.$("c-lang-f")) return;
    var s = L.svg("c-lang-f", "0 0 800 290", "Copierea octeților cu memset și memcpy");
    var N = 24, D = 16, W = 29, len = 10, src = [], dst = [], i;
    function val(k) { return ((k * 37 + 11) % 200) - 100; }
    T(s, 60, 28, "info->buf · de la radio · len octeți", { a: "start", s: 12, cls: "muted" });
    T(s, 60, 146, "packet.csi_iq · în pachet · capacitate 128 (aici 16 celule)", { a: "start", s: 12, cls: "muted" });
    for (i = 0; i < N; i++) src.push(A.cell(s, 60 + i * W, 40, 26, 34, "", 10));
    for (i = 0; i < D; i++) dst.push(A.cell(s, 60 + i * W, 158, 26, 34, "?", 10));
    var cut = T(s, 60 + (D + N) / 2 * W, 94, "", { s: 12, c: "var(--alert)" });
    var st = T(s, 400, 240, "", { s: 13 }), st2 = T(s, 400, 264, "", { s: 12, cls: "muted" });
    var ctl = A.run("c-lang-f", function (t) {
      var u = t % 7.5, copy = Math.min(len, D), done = u < 1.4 ? 0 : Math.min(copy, Math.floor((u - 1.4) / 0.25) + 1);
      for (var k = 0; k < N; k++) {
        var c = src[k], on = k < len;
        c.t.textContent = on ? val(k) : ""; c.r.setAttribute("opacity", on ? 1 : 0.3);
        A.paint(c, !on ? "plain" : k < done ? "signal" : k >= D && done === copy && u > 1.4 ? "alert" : "plain");
      }
      dst.forEach(function (c, j) {
        if (u < 0.6) { c.t.textContent = "?"; A.paint(c, "plain"); }
        else if (j < done) { c.t.textContent = val(j); A.paint(c, "signal"); }
        else { c.t.textContent = "0"; A.paint(c, "reflect"); }
      });
      cut.textContent = len > D && done === copy && u > 1.4 ? "↑ ignorate: depășesc capacitatea" : "";
      st.textContent = u < 0.6 ? "Memoria nouă conține valori vechi, fără sens: ?" : u < 1.4 ? "memset(&packet, 0, …): toate celulele devin 0." : "memcpy(packet.csi_iq, info->buf, copy_len)";
      st2.textContent = "copy_len = min(len, capacitate) = min(" + len + ", " + D + ") = " + copy;
    }, 7);
    A.toggle(["c-lang-a", "c-lang-b"], function (n) { len = n ? 24 : 10; ctl.restart(); });
  })();

  /* 3 · CSI și subpurtătoare */
  (function () {
    if (!A.$("c-csi-f")) return;
    var s = L.svg("c-csi-f", "0 0 800 340", "64 de poziții din buffer: 52 de subpurtătoare utile și 12 goale");
    var bars = [], person = false, k, PITCH = 11.4, X0 = 34;
    /* poziția din buffer: 0 = indice 0; 1…31 = indici +1…+31; 32…63 = indici −32…−1 */
    function valid(j) { return (j >= 1 && j <= 26) || (j >= 38 && j <= 63); }
    function kept(j) { return (j >= 6 && j <= 31) || (j >= 33 && j <= 58); }
    function kind(j) { return !valid(j) ? "empty" : kept(j) ? "kept" : "dropped"; }
    var FILL = { empty: "var(--line)", kept: "var(--signal)", dropped: "var(--reflect)" };
    function idx(j) { var v = j < 32 ? j : j - 64; return v > 0 ? "+" + v : v < 0 ? "−" + (-v) : "0"; }
    function cx(j) { return X0 + 4.5 + j * PITCH; }
    function base(j) { return 70 + 32 * Math.sin(j / 8 + 0.6) + 14 * Math.sin(j / 3); }
    E("line", { x1: 30, y1: 230, x2: 770, y2: 230, stroke: "var(--line)" }, s);
    for (k = 0; k < 64; k++) bars.push(E("rect", { x: X0 + k * PITCH, width: 9, rx: 2, fill: FILL[kind(k)] }, s));
    [0, 6, 26, 38, 58, 63].forEach(function (j) {
      T(s, cx(j), 248, "poz " + j, { s: 11, cls: "muted" });
      T(s, cx(j), 264, "ind " + idx(j), { s: 11, cls: "muted" });
    });
    T(s, cx(32), 202, "goale: poz 27–37", { s: 11, cls: "muted" });
    T(s, 400, 288, "poz = poziția în buffer (0…63) · ind = indicele subpurtătoarei", { s: 12, cls: "muted" });
    T(s, 400, 306, "Ordinea buffer-ului nu este ordinea frecvenței: după ind +31 urmează ind −32.", { s: 12, cls: "muted" });
    [["kept", "utilă, păstrată de PC (42)", 70], ["dropped", "utilă, ignorată de PC (10)", 300], ["empty", "goală (12)", 560]].forEach(function (l) {
      E("rect", { x: l[2], y: 318, width: 12, height: 12, rx: 2, fill: FILL[l[0]] }, s);
      T(s, l[2] + 18, 328, l[1], { a: "start", s: 12 });
    });
    T(s, 400, 22, "52 utile (42 păstrate de PC, 10 ignorate) + 12 goale = 64", { s: 13, b: true });
    var fr = T(s, 770, 42, "", { a: "end", s: 12, cls: "muted" });
    A.run("c-csi-f", function (t) {
      var env = 0.55 + 0.45 * Math.sin(t * 1.3);
      for (var j = 0; j < 64; j++) {
        var h = 5;
        if (valid(j)) { h = base(j) * (person ? 1 + 0.33 * Math.sin(j * 0.45 - t * 5) * env : 1 + 0.015 * Math.sin(t * 7 + j)); }
        A.set(bars[j], { y: 230 - h, height: h });
      }
      fr.textContent = "cadrul nr. " + Math.floor(t * 8);
    });
    A.toggle(["c-csi-a", "c-csi-b"], function (n) { person = n === 1; });
  })();

  /* 4 · RSSI */
  (function () {
    if (!A.$("c-rssi-f")) return;
    var s = L.svg("c-rssi-f", "0 0 800 260", "RSSI scade când receptorul se îndepărtează");
    var rings = [0, 1, 2].map(function () { return E("circle", { cx: 115, cy: 110, fill: "none", stroke: "var(--signal)", "stroke-width": 2 }, s); });
    L.box(s, 60, 80, 110, 60, "placa A", { k: "signal", sub: "emite" });
    var rx = E("g", {}, s);
    E("rect", { x: 0, y: 80, width: 110, height: 60, rx: 5, fill: "var(--soft-good)", stroke: "var(--good)", "stroke-width": 1.5 }, rx);
    T(rx, 55, 108, "placa B", { s: 14, b: true }); T(rx, 55, 126, "primește", { s: 11, cls: "muted" });
    E("rect", { x: 60, y: 190, width: 500, height: 22, rx: 4, fill: "none", stroke: "var(--line)" }, s);
    var fill = E("rect", { x: 60, y: 190, height: 22, rx: 4, fill: "var(--signal)" }, s);
    T(s, 60, 236, "slab (−90)", { a: "start", s: 12, cls: "muted" }); T(s, 560, 236, "puternic (−30)", { a: "end", s: 12, cls: "muted" });
    var val = T(s, 580, 207, "", { a: "start", s: 15, b: true });
    A.run("c-rssi-f", function (t) {
      var x = 360 + 170 * Math.sin(t * 0.7), rssi = -35 - Math.round((x - 190) / 340 * 45);
      A.set(rx, { transform: "translate(" + x + ",0)" });
      rings.forEach(function (c, i) { var p = ((t * 0.6 + i / 3) % 1); A.set(c, { r: 30 + p * 200, opacity: (1 - p) * 0.5 }); });
      A.set(fill, { width: Math.max(4, 500 * (rssi + 90) / 60) });
      val.textContent = "RSSI = " + String(rssi).replace("-", "−") + " dBm";
    });
  })();
})();
