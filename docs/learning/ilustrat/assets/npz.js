/* Desenează paginile pentru fișierele .npz din window.DATA["rec" + cheie]. */
window.NPZ = function (key) {
  "use strict";
  var d = window.DATA && window.DATA["rec" + key];
  if (!d) return;
  var set = function (id, v) { var e = document.getElementById(id); if (e) e.textContent = v; };
  var fmt = function (v) { return String(v).replace("-", "−"); };

  set("n-rows", d.n); set("n-rate", d.rate.toFixed(1) + " Hz"); set("n-dur", d.dur.toFixed(1) + " s"); set("n-rssi", fmt(d.rssi) + " dBm");
  var tb = document.getElementById("ports");
  if (tb) Object.keys(d.ports).forEach(function (k) {
    var tr = document.createElement("tr");
    tr.innerHTML = '<td class="m">' + k + "</td><td>nodul " + k.slice(1) + '</td><td class="m">' + d.ports[k] + "</td><td>" + (d.ports[k] === Math.max.apply(null, Object.keys(d.ports).map(function (q) { return d.ports[q]; })) ? "folosit de analiză" : "ignorat de load_recording") + "</td>";
    tb.appendChild(tr);
  });
  var fr = document.getElementById("first");
  if (fr) {
    var f = d.first;
    [["timestamp_s", f.timestamp_s + " s", "ceasul plăcii, de la pornirea ei"], ["node_id", f.node_id, "nodul care a primit cadrul"], ["rssi", fmt(f.rssi) + " dBm", "puterea semnalului"], ["seq", f.seq, "contorul plăcii"], ["csi", "52 de valori complexe", "prima: " + fmt(f.csi0[0]) + (f.csi0[1] < 0 ? " − " : " + ") + Math.abs(f.csi0[1]) + "j"]].forEach(function (r) {
      var tr = document.createElement("tr"); tr.innerHTML = '<td class="m">' + r[0] + '</td><td class="m">' + r[1] + "</td><td>" + r[2] + "</td>"; fr.appendChild(tr);
    });
  }

  L.heat("heat", d.heat, { h: 210, label: "Amplitudinea celor 52 de subpurtătoare în timp" });
  var ax = L.svg("heat-ax", "0 0 800 26", "Axa timpului");
  for (var t = 0; t <= Math.floor(d.dur); t += 5) L.text(ax, t / d.dur * 800, 16, t + " s", { s: 11, cls: "muted", a: t === 0 ? "start" : "middle" });

  var vl = [];
  if (d.impact !== null) vl.push({ x: d.impact, label: "impact " + d.impact + " s", c: "var(--alert)" });
  if (d.alarm !== null) vl.push({ x: d.alarm, label: "alarmă " + d.alarm + " s", c: "var(--good)", ly: 46 });
  var bands = d.impact !== null ? [{ x0: d.impact, x1: d.alarm, c: "var(--soft-reflect)" }] : [];
  var mx = Math.max.apply(null, d.mean), mn = Math.min.apply(null, d.mean);
  L.plot("mean", { w: 800, h: 220, xmin: 0, xmax: d.dur, ymin: Math.floor(mn - 0.5), ymax: Math.ceil(mx + 0.5), xticks: [0, 5, 10, 15, 20].filter(function (v) { return v <= d.dur; }), yticks: [Math.floor(mn - 0.5), Math.ceil(mx + 0.5)], xlabel: "timp (s)", ylabel: "amplitudine medie", vlines: vl, bands: bands, series: [{ x: d.t, y: d.mean, c: "var(--signal)", w: 1.6 }], label: "Amplitudinea medie în timp" });
  var am = Math.max.apply(null, d.motion.map(Math.abs));
  L.plot("motion", { w: 800, h: 200, xmin: 0, xmax: d.dur, ymin: -am, ymax: am, xticks: [0, 5, 10, 15, 20].filter(function (v) { return v <= d.dur; }), yticks: [-Math.round(am), 0, Math.round(am)], xlabel: "timp (s)", ylabel: "semnal de mișcare (PC1)", vlines: vl, bands: bands, series: [{ x: d.t, y: d.motion, c: "var(--reflect)", w: 1.6 }], label: "Semnalul de mișcare" });

  var vs = L.svg("var", "0 0 800 200", "Varianța fiecărei subpurtătoare");
  var vmax = Math.max(60, Math.max.apply(null, d["var"]) * 1.1), bw = 760 / d["var"].length;
  d["var"].forEach(function (v, i) {
    var h = v / vmax * 150, bad = v < 0.05 || v > 350;
    L.el("rect", { x: 30 + i * bw + 1, y: 170 - h, width: bw - 2, height: h, fill: bad ? "var(--alert)" : "var(--signal)", rx: 1, "data-tip": "Subpurtătoarea " + i + ": varianță " + v.toFixed(1) + (bad ? " · eliminată" : " · păstrată") }, vs);
  });
  var mean = d["var"].reduce(function (a, b) { return a + b; }, 0) / d["var"].length;
  L.el("line", { x1: 30, x2: 790, y1: 170 - mean / vmax * 150, y2: 170 - mean / vmax * 150, stroke: "var(--reflect)", "stroke-dasharray": "5 4", "stroke-width": 2 }, vs);
  L.text(vs, 788, 164 - mean / vmax * 150, "medie " + mean.toFixed(1), { s: 11.5, a: "end", c: "var(--reflect)" });
  L.text(vs, 30, 190, "0", { s: 11, cls: "muted", a: "start" }); L.text(vs, 790, 190, "51", { s: 11, cls: "muted", a: "end" });
  L.text(vs, 400, 190, "indicele subpurtătoarei", { s: 11, cls: "muted" });
  L.tips(vs, "var-tip");

  set("d-std", d.motionStd.toFixed(1)); set("d-kept", d.kept + " / 52");
  set("d-alarm", d.alarm === null ? "nu" : "da, la " + d.alarm + " s");
  set("d-lat", d.latency === null ? "—" : d.latency.toFixed(2) + " s");
};
