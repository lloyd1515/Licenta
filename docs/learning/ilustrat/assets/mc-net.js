/* Animații de rețea pentru main.c.html: mod promiscuu, adrese MAC, UDP, seq și timestamp. Datele sunt simulate. Necesită mc-anim.js. */
(function () {
  "use strict";
  var E = L.el, T = L.text;

  function dot(s, label, kind) {
    var g = E("g", { opacity: 0 }, s);
    E("circle", { r: 11, fill: "var(--soft-" + kind + ")", stroke: "var(--" + kind + ")", "stroke-width": 1.5 }, g);
    T(g, 0, 4, label, { s: 11, b: true });
    return g;
  }
  function at(g, x, y, on) { A.set(g, { opacity: on ? 1 : 0, transform: "translate(" + x + "," + y + ")" }); }

  /* 5 · mod promiscuu */
  (function () {
    if (!A.$("c-wifi-f")) return;
    var s = L.svg("c-wifi-f", "0 0 800 320", "Placa A aude un cadru trimis de placa B către placa C");
    var promisc = false;
    L.box(s, 325, 20, 150, 46, "router", { k: "muted", sub: "SSID din Kconfig" });
    [115, 400, 685].forEach(function (x) { E("line", { x1: 400, y1: 66, x2: x, y2: 200, stroke: "var(--line)", "stroke-dasharray": "4 4" }, s); });
    L.box(s, 40, 200, 150, 56, "placa B", { k: "plain", sub: "emite către C" });
    var a = L.box(s, 325, 200, 150, 56, "placa A", { k: "signal", sub: "ascultă" });
    L.box(s, 610, 200, 150, 56, "placa C", { k: "plain", sub: "destinatar" });
    var ar = a.querySelector("rect");
    var frame = dot(s, "cadru", "reflect"), ghost = E("line", { x1: 400, y1: 168, x2: 400, y2: 198, stroke: "var(--reflect)", "stroke-width": 2, "stroke-dasharray": "4 3", opacity: 0 }, s);
    var st = T(s, 400, 292, "", { s: 13, b: true });
    A.run("c-wifi-f", function (t) {
      var u = t % 3.2, p = Math.min(1, u / 2), seen = u > 1;
      at(frame, 190 + 420 * p, 168, u < 2.1);
      ghost.setAttribute("opacity", u > 0.95 && u < 1.6 ? 1 : 0);
      A.set(ar, { fill: seen ? (promisc ? "var(--soft-good)" : "var(--soft-alert)") : "var(--soft-signal)", stroke: seen ? (promisc ? "var(--good)" : "var(--alert)") : "var(--signal)" });
      st.textContent = !seen ? "Placa B trimite un cadru către placa C." : promisc ? "Mod promiscuu: A primește cadrul și calculează CSI." : "Mod normal: cadrul nu este pentru placa A. Ea îl ignoră.";
      A.set(st, { style: "fill:" + (!seen ? "var(--muted)" : promisc ? "var(--good)" : "var(--alert)") });
    });
    A.toggle(["c-wifi-a", "c-wifi-b"], function (n) { promisc = n === 1; });
  })();

  /* 6 · adrese MAC și broadcast */
  (function () {
    if (!A.$("c-mac-f")) return;
    var s = L.svg("c-mac-f", "0 0 800 320", "Un cadru cu adresa broadcast ajunge la toate plăcile");
    var bcast = true, ys = [52, 160, 268], macs = ["…:01", "…:02", "…:03"], rr = [], rt = [], ds = [];
    L.box(s, 30, 130, 170, 60, "placa emițătoare", { k: "reflect", sub: "24:0A:C4:00:00:03" });
    var hdr = L.box(s, 255, 20, 280, 56, "cadrul de sondare", { k: "plain", sub: " " });
    var hs = hdr.querySelectorAll("text")[1];
    ys.forEach(function (y, i) {
      var g = L.box(s, 590, y - 32, 180, 64, "placa " + macs[i], { k: "plain", sub: " " });
      rr.push(g.querySelector("rect")); rt.push(g.querySelectorAll("text")[1]);
      ds.push(dot(s, "", "reflect"));
    });
    A.run("c-mac-f", function (t) {
      var u = t % 3.6, p = Math.min(1, u / 1.6), arrived = u > 1.6;
      hs.textContent = "destinație: " + (bcast ? "FF:FF:FF:FF:FF:FF" : "24:0A:C4:00:00:02");
      ds.forEach(function (d, i) {
        at(d, 200 + 372 * p, 160 + (ys[i] - 160) * p, u < 1.7 && (bcast || i === 1));
        var ok = bcast || i === 1;
        A.set(rr[i], { fill: arrived ? (ok ? "var(--soft-good)" : "var(--bg)") : "var(--bg)", stroke: arrived ? (ok ? "var(--good)" : "var(--line)") : "var(--line)" });
        rt[i].textContent = arrived ? (ok ? "primit" : "ignorat") : "";
      });
    });
    A.toggle(["c-mac-a", "c-mac-b"], function (n) { bcast = n === 0; });
  })();

  /* 7 · UDP și TCP */
  (function () {
    if (!A.$("c-udp-f")) return;
    var s = L.svg("c-udp-f", "0 0 800 370", "UDP continuă după un pachet pierdut. TCP așteaptă retrimiterea");
    var Y = [100, 250], TR = 1.6, X0 = 130, X1 = 670, SEND = [0, 0.9, 1.8, 2.7, 3.6, 4.5];
    var UDP_DEL = [1.6, 2.5, null, 4.3, 5.2, 6.1], TCP_DEL = [1.6, 2.5, 6.0, 6.15, 6.3, 6.45];
    var title = ["UDP: trimite și nu așteaptă", "TCP: confirmă și retrimite"], lanes = [];
    Y.forEach(function (y, l) {
      T(s, 40, y - 46, title[l], { a: "start", s: 14, b: true });
      L.box(s, 30, y - 24, 70, 48, "placa", { k: "plain" }); L.box(s, 690, y - 24, 70, 48, "PC", { k: "plain" });
      E("line", { x1: 100, y1: y, x2: 690, y2: y, stroke: "var(--line)", "stroke-dasharray": "4 4" }, s);
      T(s, 560, y + 56, "aplicația primește:", { a: "end", s: 11, cls: "muted" });
      var dots = SEND.map(function (_, i) { return dot(s, String(i + 1), "signal"); });
      var chips = [];
      for (var c = 0; c < 6; c++) {
        var g = E("g", { opacity: 0 }, s);
        E("rect", { x: 570 + c * 30, y: y + 42, width: 26, height: 22, rx: 4, fill: "var(--soft-signal)", stroke: "var(--signal)" }, g);
        T(g, 583 + c * 30, y + 57, "", { s: 11, b: true });
        chips.push(g);
      }
      lanes.push({ y: y, dots: dots, chips: chips, x: E("text", { x: (X0 + X1) / 2, "text-anchor": "middle", "font-size": 22, fill: "var(--alert)", opacity: 0 }, s, "✕"), re: dot(s, "3", "reflect") });
    });
    T(s, 400, 352, "Pachetul 3 se pierde pe ambele linii. UDP merge mai departe. TCP oprește pachetele 4–6.", { s: 13 });
    A.run("c-udp-f", function (t) {
      var u = t % 10;
      lanes.forEach(function (ln, l) {
        SEND.forEach(function (s0, i) {
          var p = (u - s0) / TR, lost = i === 2, on = p >= 0 && p <= 1 && !(lost && p > 0.5);
          at(ln.dots[i], X0 + (X1 - X0) * p, ln.y, on);
        });
        ln.x.setAttribute("opacity", u > SEND[2] + TR * 0.5 && u < 9.2 ? 1 : 0);
        A.set(ln.x, { y: ln.y + 8 });
        if (l === 1) { var pr = (u - 4.4) / TR; at(ln.re, X0 + (X1 - X0) * pr, ln.y, pr >= 0 && pr <= 1); }
        else at(ln.re, 0, 0, false);
        var del = l === 0 ? UDP_DEL : TCP_DEL, k = 0;
        del.forEach(function (d, i) {
          if (d === null) return;
          var ch = ln.chips[k++], on = u >= d && u < 9.2;
          ch.setAttribute("opacity", on ? 1 : 0);
          ch.querySelector("text").textContent = i + 1;
          A.set(ch.querySelector("rect"), { fill: l === 1 && i > 2 ? "var(--soft-reflect)" : "var(--soft-signal)", stroke: l === 1 && i > 2 ? "var(--reflect)" : "var(--signal)" });
        });
      });
    }, 8);
  })();

  /* 8 · seq și timestamp */
  (function () {
    if (!A.$("c-seq-f")) return;
    var s = L.svg("c-seq-f", "0 0 800 300", "Câmpul seq arată pachetele lipsă");
    var N = 16, LOST = { 4: 1, 9: 1, 10: 1, 13: 1 }, slots = [], dts = [], i;
    T(s, 40, 44, "seq (câmpul din pachet)", { a: "start", s: 12, cls: "muted" });
    for (i = 0; i < N; i++) {
      slots.push(A.cell(s, 40 + i * 46, 56, 42, 40, "", 11));
      dts.push(T(s, 61 + i * 46, 116, "", { s: 11 }));
    }
    T(s, 40, 142, "diferența de timp față de pachetul primit înainte", { a: "start", s: 12, cls: "muted" });
    var l1 = T(s, 40, 190, "", { a: "start", s: 14 }), l2 = T(s, 40, 218, "", { a: "start", s: 14 }), l3 = T(s, 40, 246, "", { a: "start", s: 14 });
    A.run("c-seq-f", function (t) {
      var u = t % 11, cnt = Math.min(N, Math.floor(u / 0.5) + 1), prev = -1, lost = 0, gap = "nu există nicio pierdere", last = "—";
      for (var n = 0; n < N; n++) {
        var c = slots[n], shown = n < cnt;
        if (!shown) { c.t.textContent = ""; A.paint(c, "plain"); dts[n].textContent = ""; continue; }
        if (LOST[n]) { c.t.textContent = "lipsă"; A.paint(c, "alert"); lost++; dts[n].textContent = ""; continue; }
        c.t.textContent = 1200 + n; A.paint(c, "signal");
        var d = prev < 0 ? null : (n - prev) * 10;
        dts[n].textContent = d === null ? "—" : d + " ms";
        A.set(dts[n], { style: "fill:" + (d > 10 ? "var(--alert)" : "var(--muted)") });
        if (prev >= 0 && n - prev > 1) gap = "salt " + (1200 + prev) + " → " + (1200 + n) + (n - prev - 1 === 1 ? ": lipsește 1 pachet" : ": lipsesc " + (n - prev - 1) + " pachete");
        prev = n; last = 1200 + n;
      }
      l1.textContent = "Ultimul seq primit: " + last;
      l2.textContent = "Pachete pierdute până acum: " + lost;
      l3.textContent = "Ultimul salt: " + gap;
    }, 9);
  })();
})();
