/* Depanator vizual: redă pașii înregistrați din main.c rulat în gdb. Datele vin din dbg-data.js (generat de debug-harness/build_data.py). */
(function () {
  "use strict";
  var D = window.DBG;
  if (!D) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var KW = /^(static|const|void|if|else|while|return|typedef|struct|sizeof|continue|true|false|NULL|bool|int|unsigned|signed|char|uint8_t|int8_t|uint16_t|uint32_t|size_t|BaseType_t|do)$/;
  var STATE_LABELS = { stub_ring_items: "pachete în coadă", stub_ring_bytes: "octeți ocupați în coadă (din 16384)", stub_event_bits: "biții de eveniment", stub_sock_open: "socket deschis", next_seq: "next_seq" };

  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function span(cls, t) { return '<span class="' + cls + '">' + esc(t) + "</span>"; }
  function highlight(line) {
    var re = /("(?:[^"\\]|\\.)*")|(\/\/.*$)|(#\s*\w+)|\b(0x[0-9A-Fa-f]+|\d+)\b|\b([A-Za-z_]\w*)\b(\()?/g, out = "", last = 0, m;
    while ((m = re.exec(line))) {
      out += esc(line.slice(last, m.index));
      if (m[1]) out += span("tk-s", m[1]);
      else if (m[2] || m[3]) out += span("tk-p", m[2] || m[3]);
      else if (m[4]) out += span("tk-n", m[4]);
      else out += (KW.test(m[5]) ? span("tk-k", m[5]) : m[6] ? span("tk-f", m[5]) : esc(m[5])) + esc(m[6] || "");
      last = re.lastIndex;
    }
    return out + esc(line.slice(last));
  }
  function noteHtml(n) {
    if (!n) return esc("Fără explicație specială.");
    if (typeof n === "string") return esc(n);
    return esc(n.t) + '<span class="nt-row"><b>Vine de la:</b> ' + esc(n.from) + '</span><span class="nt-row"><b>Ce este:</b> ' + esc(n.what) + "</span>";
  }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }

  /* valori */
  function intText(d) {
    if (!d.s && d.w >= 16) return d.v + " (0x" + d.v.toString(16).toUpperCase().padStart(d.w <= 32 ? d.w / 4 : 1, "0") + ")";
    return String(d.v);
  }
  function bytesOf(d) { var a = []; for (var i = 0; i < d.h.length; i += 2) a.push(parseInt(d.h.substr(i, 2), 16)); return a; }
  function allOld(d) { return d.n >= 8 && /^(cd)+$/.test(d.h); }
  function flatten(vars, watch, fn) {
    var rows = [];
    function add(key, label, d, depth, junk) {
      if (junk || (d.k === "b" && allOld(d))) { rows.push({ key: key, label: label, depth: depth, kind: "junk", sig: "junk" }); return; }
      if (d.k === "s") { rows.push({ key: key, label: label, depth: depth, kind: "head", sig: "" }); d.f.forEach(function (f) { add(key + "." + f[0], f[0], f[1], depth + 1, false); }); return; }
      if (d.k === "b") { rows.push({ key: key, label: label, depth: depth, kind: "bytes", d: d, sig: d.h }); return; }
      var txt = d.k === "i" ? intText(d) : d.v;
      rows.push({ key: key, label: label, depth: depth, kind: "val", text: txt, sig: txt });
    }
    vars.forEach(function (v) { add(fn + ":" + v.n, v.n, v.d, 0, v.j); });
    watch.forEach(function (w) { add(fn + ":@" + w.n, w.n.replace(/^(.+)\[0\]@(\d+)$/, "conținut: $1 (primii $2 octeți)"), w.d, 0, false); });
    return rows;
  }
  function renderRows(rows, prev, box) {
    var pm = {};
    (prev || []).forEach(function (r) { pm[r.key] = r; });
    rows.forEach(function (r) {
      var old = pm[r.key], chg = !!prev && (!old || old.sig !== r.sig), sub = r.depth > 0 ? " sub" : "";
      if (r.kind === "junk") { box.appendChild(el("div", "dbg-var" + sub + (chg ? " chg" : ""), '<span class="n">' + esc(r.label) + '</span><span class="j">valori vechi, fără sens (0xCD în demonstrație)</span>')); return; }
      if (r.kind === "head") { box.appendChild(el("div", "dbg-var" + sub, '<span class="n">' + esc(r.label) + "</span><span>{</span>")); return; }
      if (r.kind === "val") { box.appendChild(el("div", "dbg-var" + sub + (chg ? " chg" : ""), '<span class="n">' + esc(r.label) + '</span><span class="v">= ' + esc(r.text) + "</span>")); return; }
      var d = r.d, all = bytesOf(d), lim = d.n <= 64 ? d.n : 32, pb = old && old.kind === "bytes" ? bytesOf(old.d) : null;
      box.appendChild(el("div", "dbg-var" + sub, '<span class="n">' + esc(r.label) + '</span><span class="v">= ' + d.n + " octeți" + (lim < d.n ? ", primii " + lim : "") + (d.s ? ", cu semn" : ", hex") + "</span>"));
      var grid = el("div", "bytes" + (d.s ? " dec" : ""));
      for (var i = 0; i < lim; i++) {
        var b = all[i], t = d.s ? (b > 127 ? b - 256 : b) : b.toString(16).toUpperCase().padStart(2, "0");
        grid.appendChild(el("i", (b === 0 ? "z " : "") + (pb && pb[i] !== b ? "c" : ""), String(t)));
      }
      box.appendChild(grid);
    });
  }
  function evHtml(lines) {
    if (!lines || !lines.length) return '<span class="dbg-empty">nicio schimbare vizibilă în exterior</span>';
    return lines.map(function (l) {
      var kind = l.charAt(0), txt = l.slice(2);
      return '<div><span class="' + (kind === "L" ? "l" : "c") + '">' + (kind === "L" ? "terminal" : "bibliotecă") + "</span> " + esc(txt) + "</div>";
    }).join("");
  }

  /* depanatorul */
  function Debugger(root, key) {
    var cfg = D.debuggers[key];
    if (!cfg) { root.textContent = "Date lipsă pentru " + key; return; }
    var sc = 0, pos = 0, timer = null, bps = {}, peek = 0, delay = 800, started = false, rows = [];
    var hasTerm = cfg.scenarios.some(function (s) { return s.steps.some(function (st) { return (st.ev || []).some(function (l) { return l.charAt(0) === "L"; }); }); });
    root.classList.add("dbg");
    root.innerHTML =
      '<div class="dbg-bar"><select class="dbg-sc" name="scenariu" aria-label="Scenariu"></select>' +
      '<button class="opt" data-a="run" aria-pressed="false">⏸ Stop</button><button class="opt" data-a="step" aria-pressed="false">Pas ▸</button>' +
      '<button class="opt" data-a="back" aria-pressed="false">◂ Înapoi</button><button class="opt" data-a="reset" aria-pressed="false">⟲ De la început</button>' +
      '<label>viteză <select class="dbg-speed" name="viteza" aria-label="Viteză"><option value="1400">lent</option><option value="800" selected>normal</option><option value="300">rapid</option></select></label>' +
      '<span class="dbg-pos"></span></div>' +
      '<div class="dbg-main"><pre class="dbg-code"></pre><div class="dbg-side"></div></div>' +
      '<div class="dbg-note">Apasă numărul unei linii ca să pui un punct de oprire (●). Apasă textul unei linii ca să vezi explicația ei. Programul a rulat pe PC, cu bibliotecile ESP-IDF simulate.</div>';
    var selSc = root.querySelector(".dbg-sc"), selSp = root.querySelector(".dbg-speed"), code = root.querySelector(".dbg-code"), side = root.querySelector(".dbg-side"), posEl = root.querySelector(".dbg-pos");
    cfg.scenarios.forEach(function (s, i) { var o = el("option", "", esc(s.label)); o.value = i; selSc.appendChild(o); });
    var codeRows = cfg.code.map(function (ln, i) {
      var r = el("div", "dbg-row" + (cfg.notes[i] ? " hasnote" : ""));
      var g = el("span", "g", String(i + 1)), t = el("span", "t", highlight(ln) || " ");
      g.addEventListener("click", function () { if (bps[i + 1]) delete bps[i + 1]; else bps[i + 1] = true; r.classList.toggle("bp", !!bps[i + 1]); });
      t.addEventListener("click", function () { peek = i + 1; show(); });
      r.appendChild(g); r.appendChild(t); code.appendChild(r);
      return r;
    });
    var bNow = el("div", "dbg-box dbg-now"), bStack = el("div", "dbg-box"), bVars = el("div", "dbg-box"), bEv = el("div", "dbg-box"), bState = el("div", "dbg-box"), bTerm = el("div", "dbg-box");
    bNow.innerHTML = "<h4>Linia curentă</h4><div></div>"; bStack.innerHTML = "<h4>Funcții active</h4><div></div>"; bVars.innerHTML = "<h4>Variabile (înainte de executarea liniei)</h4><div class=\"dbg-vars\"></div>";
    bEv.innerHTML = "<h4>Efect al liniei precedente</h4><div class=\"dbg-ev\"></div>"; bState.innerHTML = "<h4>Stare simulată a sistemului</h4><div class=\"dbg-state\"></div>"; bTerm.innerHTML = "<h4>Terminal (idf.py monitor)</h4><div class=\"dbg-term\"></div>";
    [bNow, bStack, bVars, bEv, bState].concat(hasTerm ? [bTerm] : []).forEach(function (b) { side.appendChild(b); });

    function steps() { return cfg.scenarios[sc].steps; }
    function activeGlobals() {
      var st = steps(), out = [];
      Object.keys(STATE_LABELS).forEach(function (g) { if (st.some(function (s) { return s.g[g] !== st[0].g[g] || s.g[g] !== 0; })) out.push(g); });
      return out;
    }
    function show() {
      var st = steps(), s = st[pos], prev = pos > 0 ? st[pos - 1] : null;
      posEl.textContent = "pasul " + (pos + 1) + " din " + st.length;
      codeRows.forEach(function (r, i) { r.classList.toggle("cur", !s.end && s.l === i + 1); });
      var line = peek || (s.end ? 0 : s.l), nowBody = bNow.lastChild;
      if (!s.end && !peek) {
        nowBody.innerHTML = "<code>" + esc(cfg.code[line - 1].trim()) + "</code><p>" + noteHtml(cfg.notes[line - 1]) + "</p>";
      } else if (peek) {
        nowBody.innerHTML = "<code>" + esc(cfg.code[line - 1].trim()) + "</code><p>" + noteHtml(cfg.notes[line - 1]) + "</p><p class=\"dbg-empty\">Explicație la cerere. Pasul curent rămâne neschimbat.</p>";
      } else {
        nowBody.innerHTML = "<p>Sfârșit. Funcția s-a întors, sau task-ul s-a blocat și așteaptă. Într-un program real, bucla ar continua. Apasă „De la început” sau lasă bucla să reia.</p>";
      }
      bStack.lastChild.textContent = s.end ? "—" : s.st.slice().reverse().join(" → ");
      var vbox = bVars.lastChild; vbox.innerHTML = "";
      if (s.end) vbox.appendChild(el("div", "dbg-empty", "—"));
      else {
        rows = flatten(s.v, s.w, s.fn);
        var prevRows = prev && !prev.end ? flatten(prev.v, prev.w, prev.fn) : null;
        renderRows(rows, prevRows, vbox);
      }
      bEv.lastChild.innerHTML = evHtml(s.ev);
      var act = activeGlobals(), sb = bState.lastChild; sb.innerHTML = "";
      act.forEach(function (g) {
        var v = s.g[g], txt = g === "stub_event_bits" ? "0x" + v.toString(16) + (v & 1 ? " (WIFI_CONNECTED_BIT = 1)" : "") : g === "stub_sock_open" ? (v ? "da" : "nu") : String(v);
        sb.appendChild(el("span", "", STATE_LABELS[g] + ": <b>" + esc(txt) + "</b>"));
      });
      if (!act.length) sb.appendChild(el("span", "dbg-empty", "nicio schimbare în acest scenariu"));
      if (hasTerm) {
        var lines = []; for (var i = 0; i <= pos; i++) (st[i].ev || []).forEach(function (l) { if (l.charAt(0) === "L") lines.push(l.slice(2)); });
        bTerm.lastChild.textContent = lines.join("\n") || " ";
      }
      var cr = codeRows[(s.end ? 1 : s.l) - 1];
      if (!s.end && cr) code.scrollTop = Math.max(0, cr.offsetTop - code.clientHeight / 2 + 10);
    }
    function go(n) { pos = n; peek = 0; show(); }
    function tick() {
      var st = steps(); go((pos + 1) % st.length);
      var s = st[pos];
      if (!s.end && bps[s.l]) stop();
    }
    function play() { if (timer) return; timer = setInterval(tick, delay); root.querySelector('[data-a="run"]').textContent = "⏸ Stop"; }
    function stop() { if (timer) clearInterval(timer); timer = null; root.querySelector('[data-a="run"]').textContent = "▶ Rulează"; }
    root.querySelector('[data-a="run"]').addEventListener("click", function () { if (timer) stop(); else play(); });
    root.querySelector('[data-a="step"]').addEventListener("click", function () { stop(); go((pos + 1) % steps().length); });
    root.querySelector('[data-a="back"]').addEventListener("click", function () { stop(); go(Math.max(0, pos - 1)); });
    root.querySelector('[data-a="reset"]').addEventListener("click", function () { go(0); });
    selSc.addEventListener("change", function () { sc = +selSc.value; go(0); });
    selSp.addEventListener("change", function () { delay = +selSp.value; if (timer) { stop(); play(); } });
    show();
    stop();
    if (reduce || !("IntersectionObserver" in window)) return;
    new IntersectionObserver(function (e) {
      if (e[0].isIntersecting) { if (!started) { started = true; play(); } } else if (timer) stop();
    }, { threshold: 0.35 }).observe(root);
  }

  /* fragment comentat (fără rulare) */
  function Snippet(root, key) {
    var sn = D.snippets[key];
    if (!sn) { root.textContent = "Fragment lipsă: " + key; return; }
    root.classList.add("snip");
    var pre = el("pre", "snip-code"), note = el("div", "snip-note"), sel = -1, rowEls = [];
    sn.code.forEach(function (ln, i) {
      if (ln === null) { pre.appendChild(el("div", "snip-gap", "⋯")); rowEls.push(null); return; }
      var r = el("div", "snip-row" + (sn.notes[i] ? " hasnote" : ""));
      r.appendChild(el("span", "g", "")); r.appendChild(el("span", "t", highlight(ln) || " "));
      r.addEventListener("click", function () { pick(i); });
      pre.appendChild(r); rowEls.push(r);
    });
    root.appendChild(el("div", "snip-h", "din main.c · apasă o linie ca să vezi explicația"));
    root.appendChild(pre); root.appendChild(note);
    function pick(i) {
      if (sel >= 0 && rowEls[sel]) rowEls[sel].classList.remove("sel");
      sel = i; rowEls[i].classList.add("sel");
      note.innerHTML = "<code>" + esc(sn.code[i].trim()) + "</code>" + noteHtml(sn.notes[i]);
    }
    var first = sn.notes.findIndex(function (n, i) { return n && sn.code[i] !== null; });
    pick(first >= 0 ? first : sn.code.findIndex(function (c) { return c !== null; }));
  }

  function init() {
    document.querySelectorAll("[data-dbg]").forEach(function (n) { Debugger(n, n.getAttribute("data-dbg")); });
    document.querySelectorAll("[data-snip]").forEach(function (n) { Snippet(n, n.getAttribute("data-snip")); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
