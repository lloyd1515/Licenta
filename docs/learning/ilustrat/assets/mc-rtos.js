/* Animații FreeRTOS pentru main.c.html: task-uri, callback urgent, coadă, steag de eveniment. Datele sunt simulate. Necesită mc-anim.js. */
(function () {
  "use strict";
  var E = L.el, T = L.text;

  /* 9 · task-uri și nuclee */
  (function () {
    if (!A.$("c-task-f")) return;
    var s = L.svg("c-task-f", "0 0 800 290", "Două nuclee: probe_sender doarme între cadre, udp_sender doarme până vine un pachet");
    var XL = 150, XR = 780, PPS = 110, Y = [64, 164], H = 44, i;
    var clip = A.clip(s, "c-task-clip", XL, 30, XR - XL, 200);
    var ticks = [];
    for (i = 0; i < 14; i++) ticks.push(E("line", { y1: 40, y2: 226, stroke: "var(--line)", "stroke-dasharray": "3 4", "clip-path": clip }, s));
    [["nucleul 0", "probe_sender · prio 5"], ["nucleul 1", "udp_sender · prio 10"]].forEach(function (n, l) {
      T(s, 12, Y[l] + 18, n[0], { a: "start", s: 13, b: true }); T(s, 12, Y[l] + 36, n[1], { a: "start", s: 11, cls: "muted" });
      E("line", { x1: XL, y1: Y[l] + H / 2, x2: XR, y2: Y[l] + H / 2, stroke: "var(--line)" }, s);
    });
    var p0 = A.pool(s, 16, clip, "reflect"), p1 = A.pool(s, 16, clip, "good");
    E("line", { x1: XR, y1: 34, x2: XR, y2: 232, stroke: "var(--ink)", "stroke-width": 2 }, s);
    T(s, XR, 24, "acum", { a: "end", s: 12, b: true });
    T(s, 400, 256, "Bloc colorat: task-ul rulează. Linie goală: task-ul doarme. Linia punctată: 1 tick (aici încetinit).", { s: 12, cls: "muted" });
    A.run("c-task-f", function (now) {
      var k0 = Math.floor((now - 6) / 0.5) - 1, k1 = Math.floor(now / 0.5), a = [], b = [], k, t0;
      for (k = k0; k <= k1; k++) {
        t0 = 0.5 * k;
        if (t0 <= now) a.push([t0, Math.min(now, t0 + 0.12)]);
        if (k % 3 !== 2 && t0 + 0.15 <= now) b.push([t0 + 0.15, Math.min(now, t0 + 0.32)]);
      }
      A.place(p0, a, now, XR, PPS, Y[0], H); A.place(p1, b, now, XR, PPS, Y[1], H);
      ticks.forEach(function (ln, j) { var x = XR - (now - 0.5 * (k0 + j)) * PPS; A.set(ln, { x1: x, x2: x }); });
    }, 4);
  })();

  /* 10 · callback urgent și IRAM_ATTR */
  (function () {
    if (!A.$("c-isr-f")) return;
    var s = L.svg("c-isr-f", "0 0 800 260", "on_csi cu și fără IRAM_ATTR: cât timp ocupă procesorul");
    var XL = 110, XR = 780, PPS = 90, Y = 90, H = 50, iram = true, i;
    var clip = A.clip(s, "c-isr-clip", XL, 50, XR - XL, 110);
    E("rect", { x: XL, y: Y, width: XR - XL, height: H, rx: 4, fill: "var(--soft-good)", stroke: "var(--good)", "stroke-width": 1.5 }, s);
    T(s, 12, Y + 22, "procesor", { a: "start", s: 13, b: true }); T(s, 12, Y + 40, "un nucleu", { a: "start", s: 11, cls: "muted" });
    var pool = A.pool(s, 8, clip, "alert"), marks = [];
    for (i = 0; i < 8; i++) marks.push(E("line", { y1: 56, y2: Y, stroke: "var(--alert)", "stroke-width": 2, "clip-path": clip }, s));
    E("line", { x1: XR, y1: 50, x2: XR, y2: 160, stroke: "var(--ink)", "stroke-width": 2 }, s);
    T(s, XR, 44, "acum", { a: "end", s: 12, b: true });
    T(s, XL, 44, "↓ cadru nou sosit", { a: "start", s: 12, c: "var(--alert)" });
    T(s, 130, 186, "verde = task-ul UDP rulează · roșu = on_csi rulează", { a: "start", s: 12, cls: "muted" });
    var pct = T(s, 400, 228, "", { s: 14, b: true });
    A.run("c-isr-f", function (now) {
      var d = iram ? 0.15 : 0.45, k0 = Math.floor((now - 8) / 1.5), k1 = Math.floor(now / 1.5), iv = [], k;
      for (k = k0; k <= k1; k++) if (1.5 * k <= now) iv.push([1.5 * k, Math.min(now, 1.5 * k + d)]);
      A.place(pool, iv, now, XR, PPS, Y, H);
      marks.forEach(function (m, j) { var x = XR - (now - 1.5 * (k0 + j)) * PPS; A.set(m, { x1: x, x2: x, opacity: k0 + j <= k1 && 1.5 * (k0 + j) <= now ? 1 : 0 }); });
      pct.textContent = (iram ? "Cu IRAM_ATTR: " : "Fără IRAM_ATTR: ") + d.toFixed(2).replace(".", ",") + " s din 1,5 s = " + Math.round(d / 1.5 * 100) + "% din timp";
    }, 5);
    A.toggle(["c-isr-a", "c-isr-b"], function (n) { iram = n === 0; });
  })();

  /* 11 · coada (ring buffer) */
  (function () {
    if (!A.$("c-queue-f")) return;
    var s = L.svg("c-queue-f", "0 0 800 330", "Coada circulară: scrie on_csi, citește udp_sender_task");
    var SL = 10, slots = [], slow = false, st = null, i;
    L.box(s, 100, 30, 170, 52, "on_csi", { k: "signal", sub: "scrie un pachet" });
    var ron = E("rect", { x: 100, y: 30, width: 170, height: 52, rx: 5, fill: "none", stroke: "var(--alert)", "stroke-width": 3, opacity: 0 }, s);
    L.box(s, 530, 30, 170, 52, "udp_sender_task", { k: "good", sub: "citește și trimite" });
    for (i = 0; i < SL; i++) slots.push(A.cell(s, 100 + i * 60, 150, 54, 54, "", 14));
    var wr = T(s, 0, 140, "scrie ↓", { s: 12, c: "var(--signal)", b: true }), rd = T(s, 0, 228, "↑ citește", { s: 12, c: "var(--good)", b: true });
    T(s, 100, 122, "coada: 10 locuri în schemă (în cod: 16 KB ≈ 110 pachete)", { a: "start", s: 12, cls: "muted" });
    var inf = T(s, 100, 278, "", { a: "start", s: 14 }), drp = T(s, 100, 304, "", { a: "start", s: 14, b: true, c: "var(--alert)" });
    function fresh() { return { slots: [], head: 0, tail: 0, count: 0, seq: 1, sent: 0, drop: 0, step: -1, flash: 0 }; }
    var ctl = A.run("c-queue-f", function (t, first) {
      if (first || !st) st = fresh();
      var steps = Math.floor(t * 10), C = slow ? 12 : 5;
      while (st.step < steps) {
        st.step++; st.flash = Math.max(0, st.flash - 1);
        if (st.step % 5 === 0) {
          if (st.count < SL) { st.slots[st.tail] = st.seq; st.tail = (st.tail + 1) % SL; st.count++; } else { st.drop++; st.flash = 4; }
          st.seq++;
        }
        if (st.step % C === 2 && st.count > 0) { st.slots[st.head] = null; st.head = (st.head + 1) % SL; st.count--; st.sent++; }
      }
      slots.forEach(function (c, j) { var v = st.slots[j]; c.t.textContent = v || ""; A.paint(c, v ? "signal" : "plain"); });
      A.set(wr, { transform: "translate(" + (127 + st.tail * 60) + ",0)" }); A.set(rd, { transform: "translate(" + (127 + st.head * 60) + ",0)" });
      ron.setAttribute("opacity", st.flash > 0 ? 1 : 0);
      inf.textContent = "În coadă: " + st.count + " din " + SL + " · trimise: " + st.sent;
      drp.textContent = "Pachete pierdute: " + st.drop + (st.flash > 0 ? "  ← coada este plină, pachetul nou se pierde" : "");
    }, 12);
    A.toggle(["c-queue-a", "c-queue-b"], function (n) { slow = n === 1; st = null; ctl.restart(); });
  })();

  /* 12 · steag de eveniment */
  (function () {
    if (!A.$("c-flag-f")) return;
    var s = L.svg("c-flag-f", "0 0 800 270", "Bitul WIFI_CONNECTED_BIT decide dacă task-ul UDP trimite");
    var manual = false, ms = false, cells = [], i;
    for (i = 0; i < 8; i++) {
      cells.push(A.cell(s, 60 + i * 52, 60, 46, 46, "0", 16));
      T(s, 83 + i * 52, 128, "bit " + (7 - i), { s: 11, cls: "muted" });
    }
    T(s, 60, 44, "grupul de steaguri wifi_events", { a: "start", s: 12, cls: "muted" });
    T(s, 447, 148, "BIT0 = WIFI_CONNECTED_BIT", { s: 12, b: true });
    var box = E("rect", { x: 590, y: 52, width: 190, height: 62, rx: 6, fill: "var(--bg)", stroke: "var(--line)", "stroke-width": 1.5 }, s);
    T(s, 685, 76, "udp_sender_task", { s: 13, b: true });
    var sub = T(s, 685, 98, "", { s: 12 });
    E("line", { x1: 474, y1: 83, x2: 588, y2: 83, stroke: "var(--muted)" }, s);
    T(s, 531, 72, "bits & BIT0", { s: 11, cls: "muted" });
    var flow = [0, 1, 2].map(function () { return E("circle", { cy: 83, r: 4, fill: "var(--good)", opacity: 0 }, s); });
    var ev = T(s, 60, 206, "", { a: "start", s: 13, cls: "muted" }), code = T(s, 60, 234, "", { a: "start", s: 14, b: true });
    A.run("c-flag-f", function (t) {
      var on = manual ? ms : Math.floor(t / 3.5) % 2 === 1;
      cells.forEach(function (c, j) {
        var bit0 = j === 7, v = bit0 && on;
        c.t.textContent = v ? "1" : "0"; A.paint(c, bit0 ? (on ? "good" : "alert") : "plain");
      });
      A.set(box, { fill: on ? "var(--soft-good)" : "var(--bg)", stroke: on ? "var(--good)" : "var(--line)" });
      sub.textContent = on ? "trimite pachete" : "așteaptă adresa IP";
      flow.forEach(function (c, j) { A.set(c, { cx: 478 + ((t * 0.8 + j / 3) % 1) * 106, opacity: on ? 1 : 0 }); });
      ev.textContent = on ? "Eveniment: IP_EVENT_STA_GOT_IP" : "Eveniment: WIFI_EVENT_STA_DISCONNECTED";
      code.textContent = on ? "xEventGroupSetBits(wifi_events, WIFI_CONNECTED_BIT);" : "xEventGroupClearBits(wifi_events, WIFI_CONNECTED_BIT);";
    }, 5);
    A.toggle(["c-flag-a", "c-flag-b"], function (n) { manual = true; ms = n === 0; });
  })();
})();
