/* Redă scenariul simulat al proiectului: persoana în cameră, amplitudinea CSI, semnalul de mișcare și starea detectorului.
   Datele vin din mc-sim-data.js (generat din simulatorul proiectului). Necesită mc-anim.js. */
(function () {
  "use strict";
  var D = window.SIMDATA;
  if (!D || !A.$("c-sim-f")) return;
  var E = L.el, T = L.text;
  var X0 = 60, X1 = 780, W = X1 - X0, DUR = D.dur;
  var STATE_NAME = ["CALM", "MERS", "IMPACT", "VERIFICARE", "ALARMĂ"];
  var STATE_COL = ["var(--line)", "var(--signal)", "var(--alert)", "var(--reflect)", "var(--alert)"];
  var LINK_COL = ["var(--signal)", "var(--reflect)", "var(--good)"];
  var s = L.svg("c-sim-f", "0 0 800 630", "Scenariul simulat: persoana, amplitudinea CSI, semnalul de mișcare și starea detectorului");
  var clip = A.clip(s, "c-sim-clip", X0, 0, 0, 630), clipRect = s.querySelector("#c-sim-clip rect");
  function tx(t) { return X0 + t / DUR * W; }

  /* harta camerei */
  var SC = 40, CX = 145, CY = 125;
  function mx(x) { return CX + x * SC; } function my(y) { return CY - y * SC; }
  E("rect", { x: CX - 2.5 * SC, y: CY - 2.5 * SC, width: 5 * SC, height: 5 * SC, fill: "var(--bg)", stroke: "var(--line)", "stroke-width": 1.5 }, s);
  T(s, CX, 16, "camera 5 × 5 m", { s: 12, cls: "muted" });
  var N = D.nodes, links = [["1", "2"], ["2", "3"], ["3", "1"]];
  links.forEach(function (l, i) { E("line", { x1: mx(N[l[0]][0]), y1: my(N[l[0]][1]), x2: mx(N[l[1]][0]), y2: my(N[l[1]][1]), stroke: LINK_COL[i], "stroke-dasharray": "4 4", "stroke-width": 1.5 }, s); });
  Object.keys(N).forEach(function (k) {
    E("circle", { cx: mx(N[k][0]), cy: my(N[k][1]), r: 9, fill: "var(--soft-violet)", stroke: "var(--violet)", "stroke-width": 1.5 }, s);
    T(s, mx(N[k][0]), my(N[k][1]) + 4, k, { s: 11, b: true });
  });
  E("polyline", { points: D.x.map(function (x, i) { return mx(x).toFixed(1) + "," + my(D.y[i]).toFixed(1); }).join(" "), fill: "none", stroke: "var(--muted)", "stroke-width": 1, "stroke-dasharray": "2 3" }, s);
  var person = E("circle", { r: 8, fill: "var(--signal)", stroke: "var(--ink)", "stroke-width": 1.5 }, s);
  /* înălțimea */
  E("rect", { x: 266, y: 25, width: 12, height: 200, fill: "var(--bg)", stroke: "var(--line)" }, s);
  var hbar = E("rect", { x: 266, width: 12, fill: "var(--signal)" }, s);
  T(s, 272, 240, "înălțime", { s: 11, cls: "muted" });

  /* text de stare */
  var phase = T(s, 310, 50, "", { a: "start", s: 20, b: true }), clock = T(s, 310, 80, "", { a: "start", s: 14, cls: "muted" });
  var stLbl = T(s, 310, 126, "", { a: "start", s: 22, b: true }), hLbl = T(s, 310, 154, "", { a: "start", s: 13, cls: "muted" });
  var expl = T(s, 310, 172, "", { a: "start", s: 13 }), alarm = T(s, 310, 230, "", { a: "start", s: 15, b: true, c: "var(--alert)" });
  T(s, 310, 106, "starea detectorului:", { a: "start", s: 12, cls: "muted" });

  /* heatmap amplitudine */
  var HY = 270, HH = 110;
  T(s, X0, HY - 8, "1 · amplitudine brută, 52 subpurtătoare × timp (legătura 1–2, cu zgomot și vârfuri)", { a: "start", s: 12, b: true });
  var raw = atob(D.amp), cv = document.createElement("canvas"); cv.width = D.frames; cv.height = D.subs;
  var g = cv.getContext("2d"), img = g.createImageData(D.frames, D.subs), STOPS = [[13, 8, 135], [156, 23, 158], [237, 121, 83], [240, 249, 33]], f, k;
  function color(v) { var p = v / 255 * 3, i = Math.min(2, Math.floor(p)), u = p - i, a = STOPS[i], b = STOPS[i + 1]; return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]; }
  for (f = 0; f < D.frames; f++) for (k = 0; k < D.subs; k++) {
    var c = color(raw.charCodeAt(f * D.subs + k)), o = ((D.subs - 1 - k) * D.frames + f) * 4;
    img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2]; img.data[o + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  E("rect", { x: X0, y: HY, width: W, height: HH, fill: "var(--bg)", stroke: "var(--line)" }, s);
  E("image", { href: cv.toDataURL(), x: X0, y: HY, width: W, height: HH, preserveAspectRatio: "none", "clip-path": clip, style: "image-rendering:auto" }, s);
  T(s, X0 - 6, HY + 12, "+26", { a: "end", s: 10, cls: "muted" }); T(s, X0 - 6, HY + HH, "−26", { a: "end", s: 10, cls: "muted" });

  /* semnal de mișcare */
  var MY = 420, MH = 110;
  T(s, X0, MY - 8, "2 · semnalul de mișcare după filtre, pe cele 3 legături", { a: "start", s: 12, b: true });
  E("rect", { x: X0, y: MY, width: W, height: MH, fill: "var(--bg)", stroke: "var(--line)" }, s);
  E("line", { x1: X0, y1: MY + MH / 2, x2: X1, y2: MY + MH / 2, stroke: "var(--line)" }, s);
  Object.keys(D.motion).forEach(function (name, i) {
    var arr = D.motion[name], pts = arr.map(function (v, j) { return (X0 + j / (arr.length - 1) * W).toFixed(1) + "," + (MY + MH / 2 - v / 1000 * (MH / 2 - 4)).toFixed(1); }).join(" ");
    E("polyline", { points: pts, fill: "none", stroke: LINK_COL[i], "stroke-width": 1.4, opacity: 0.9, "clip-path": clip }, s);
    T(s, X1 - 4, MY + 12 + i * 13, name, { a: "end", s: 10, c: LINK_COL[i] });
  });

  /* starea detectorului și fazele */
  var SY = 562;
  T(s, X0, SY - 8, "3 · starea detectorului de cădere și ce face persoana", { a: "start", s: 12, b: true });
  E("rect", { x: X0, y: SY, width: W, height: 22, fill: "var(--bg)", stroke: "var(--line)" }, s);
  var runs = [], st = D.states, i0 = 0, j;
  for (j = 1; j <= st.length; j++) if (j === st.length || st[j] !== st[i0]) { runs.push([i0, j, +st[i0]]); i0 = j; }
  runs.forEach(function (r) {
    var x = X0 + r[0] / st.length * W, w = Math.max(3, (r[1] - r[0]) / st.length * W);
    E("rect", { x: x, y: SY, width: w, height: 22, fill: STATE_COL[r[2]], opacity: r[2] === 0 ? 0.35 : 0.9, "clip-path": clip }, s);
  });
  var PH = [["stă pe loc", 0, D.phases.still, "var(--soft-signal)"], ["merge", D.phases.still, D.phases.walk, "var(--soft-good)"], ["cade", D.phases.walk, D.phases.fall, "var(--soft-alert)"], ["întinsă", D.phases.fall, DUR, "var(--soft-reflect)"]];
  PH.forEach(function (p) {
    E("rect", { x: tx(p[1]), y: SY + 28, width: Math.max(2, tx(p[2]) - tx(p[1])), height: 20, fill: p[3], stroke: "var(--line)" }, s);
    if (tx(p[2]) - tx(p[1]) > 40) T(s, (tx(p[1]) + tx(p[2])) / 2, SY + 42, p[0], { s: 11 });
  });
  T(s, X0, SY + 66, "0 s", { s: 11, cls: "muted" }); T(s, X1, SY + 66, DUR.toFixed(0) + " s", { s: 11, cls: "muted" });
  if (D.impact !== null) T(s, tx(D.impact), SY - 24, "impact " + D.impact.toFixed(1).replace(".", ",") + " s", { s: 11, c: "var(--alert)", b: true });

  /* cursorul de redare */
  var head = E("line", { y1: HY - 2, y2: SY + 50, stroke: "var(--ink)", "stroke-width": 2 }, s);

  var cur = A.reduce ? 13 : 0, playing = true, last = 0, range = A.$("c-sim-range"), playBtn = A.$("c-sim-play");
  var EXPL = ["Corpul stă pe loc. Amplitudinea este stabilă.\nMișcarea măsurată este aproape 0.", "Persoana merge. Amplitudinea variază.\nSemnalul de mișcare oscilează.", "Persoana cade. Cele 3 legături se schimbă\nbrusc, în același timp.", "Persoana nu se mișcă. Detectorul verifică\n2,5 s de liniște, apoi dă alarma."], shown = -1;
  function setExpl(i) {
    if (i === shown) return;
    shown = i; while (expl.firstChild) expl.removeChild(expl.firstChild);
    EXPL[i].split("\n").forEach(function (line, n) { E("tspan", { x: 310, dy: n ? 17 : 0 }, expl, line); });
  }
  function render(t) {
    var tt = Math.min(t, DUR), fi = Math.min(D.frames - 1, Math.floor(tt * 25)), si = Math.min(st.length - 1, Math.floor(tt * D.motionRate));
    var h = D.h[fi], state = +st[si], ph = tt < D.phases.still ? 0 : tt < D.phases.walk ? 1 : tt < D.phases.fall ? 2 : 3;
    A.set(person, { cx: mx(D.x[fi]), cy: my(D.y[fi]), fill: h < 0.6 ? "var(--alert)" : "var(--signal)" });
    A.set(hbar, { y: 225 - h * 100, height: h * 100, fill: h < 0.6 ? "var(--alert)" : "var(--signal)" });
    clipRect.setAttribute("width", tt / DUR * W);
    A.set(head, { x1: tx(tt), x2: tx(tt) });
    phase.textContent = ["Persoana stă pe loc", "Persoana merge", "Persoana cade", "Persoana este întinsă"][ph];
    clock.textContent = "t = " + tt.toFixed(1).replace(".", ",") + " s din " + DUR.toFixed(0) + " s";
    stLbl.textContent = STATE_NAME[state]; A.set(stLbl, { style: "fill:" + STATE_COL[state] });
    hLbl.textContent = "înălțimea corpului: " + h.toFixed(2).replace(".", ",") + " m";
    setExpl(ph);
    alarm.textContent = state === 4 ? "ALARMĂ la t = " + D.alarm.toFixed(1).replace(".", ",") + " s · întârziere " + (D.alarm - D.impact).toFixed(1).replace(".", ",") + " s după impact" : "";
    if (document.activeElement !== range) range.value = tt;
  }
  A.run("c-sim-f", function (t, first) {
    var dt = first ? 0 : t - last; last = t;
    if (A.reduce) { render(cur); return; }
    if (playing) cur += dt;
    if (cur > DUR + 2) cur = 0;
    render(cur);
  }, 13);
  range.addEventListener("input", function () { cur = parseFloat(range.value); render(cur); });
  playBtn.addEventListener("click", function () { playing = !playing; playBtn.textContent = playing ? "Pauză" : "Redă"; playBtn.setAttribute("aria-pressed", !playing); });
  A.$("c-sim-reset").addEventListener("click", function () { cur = 0; render(cur); });
})();
