
const Sim = (() => {
  const C = 299792458, FC = 2.437e9, DF = 312500;
  const KS = [];
  for (let k = -26; k <= 26; k++) if (k !== 0) KS.push(k);
  const N = KS.length;
  const FREQS = KS.map(k => FC + k * DF);
  const LAMBDA = C / FC;
  const ROOM = { w: 8, h: 5 };
  const TX = { x: 0.6, y: 2.0 }, RX = { x: 7.4, y: 2.9 };
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const mY = (p, w) => ({ x: p.x, y: 2 * w - p.y });
  const mX = (p, w) => ({ x: 2 * w - p.x, y: p.y });
  const iY = (a, b, w) => { const t = (w - a.y) / (b.y - a.y); return { x: a.x + t * (b.x - a.x), y: w }; };
  const iX = (a, b, w) => { const t = (w - a.x) / (b.x - a.x); return { x: w, y: a.y + t * (b.y - a.y) }; };

  const PATHS = (() => {
    const out = [{ kind: 'direct', a: 1, d: dist(TX, RX), pts: [TX, RX] }];
    for (const w of [0, ROOM.h]) {
      const im = mY(TX, w);
      out.push({ kind: 'wall', a: 0.6, d: dist(im, RX), pts: [TX, iY(im, RX, w), RX] });
    }
    const imx = mX(TX, ROOM.w);
    out.push({ kind: 'wall', a: 0.6, d: dist(imx, RX), pts: [TX, iX(imx, RX, ROOM.w), RX] });
    for (const [w1, w2] of [[0, ROOM.h], [ROOM.h, 0]]) {
      const t1 = mY(TX, w1), t2 = mY(t1, w2), B = iY(t2, RX, w2), A = iY(t1, B, w1);
      out.push({ kind: 'double', a: 0.4, d: dist(t2, RX), pts: [TX, A, B, RX] });
    }
    return out;
  })();

  const SRE = new Float64Array(N), SIM = new Float64Array(N);
  for (let i = 0; i < N; i++) {
    for (const p of PATHS) {
      const amp = p.a / p.d, ph = -2 * Math.PI * FREQS[i] * p.d / C;
      SRE[i] += amp * Math.cos(ph);
      SIM[i] += amp * Math.sin(ph);
    }
  }
  const personD = P => dist(TX, P) + dist(P, RX);

  let spare = null;
  function gauss() {
    if (spare !== null) { const s = spare; spare = null; return s; }
    let u = 0;
    while (u === 0) u = Math.random();
    const v = Math.random(), r = Math.sqrt(-2 * Math.log(u));
    spare = r * Math.sin(2 * Math.PI * v);
    return r * Math.cos(2 * Math.PI * v);
  }

  function amps(extras, noise, out) {
    for (let i = 0; i < N; i++) {
      let re = SRE[i], im = SIM[i];
      const f = FREQS[i];
      for (let j = 0; j < extras.length; j++) {
        const e = extras[j], amp = e.a / e.d, ph = -2 * Math.PI * f * e.d / C;
        re += amp * Math.cos(ph);
        im += amp * Math.sin(ph);
      }
      if (noise) { re += noise * gauss(); im += noise * gauss(); }
      out[i] = Math.hypot(re, im);
    }
    return out;
  }

  const clampPos = p => ({ x: Math.min(7.3, Math.max(0.7, p.x)), y: Math.min(4.5, Math.max(0.5, p.y)) });

  function makeScenario() {
    const s = { mode: 'empty', t: 0, pos: { x: 3.6, y: 3.8 }, head: 0.4, coef: 0.6, br: 0.25, brAmp: 0.007, fallStart: 0, fallDir: 0, fallFrom: null };
    function set(mode) {
      if (mode === 'fall') {
        if (s.mode === 'empty' || s.mode === 'falling' || s.mode === 'down') return;
        s.mode = 'falling'; s.fallStart = s.t; s.fallDir = s.head; s.fallFrom = { ...s.pos };
        return;
      }
      if (mode === 'walk' && s.mode === 'empty') { s.pos = { x: 1.4, y: 4.2 }; s.head = -0.3; }
      if (mode === 'still') {
        if (s.mode === 'empty') s.pos = { x: 3.6, y: 3.8 };
        s.br = 0.22 + Math.random() * 0.08; s.brAmp = 0.007;
      }
      s.coef = 0.6; s.mode = mode;
    }
    function step(dt) {
      s.t += dt;
      const ex = [];
      if (s.mode === 'empty') return ex;
      if (s.mode === 'walk') {
        s.head += gauss() * 1.6 * Math.sqrt(dt);
        s.pos.x += 0.75 * dt * Math.cos(s.head);
        s.pos.y += 0.75 * dt * Math.sin(s.head);
        if (s.pos.x < 1.2 || s.pos.x > 6.8) { s.head = Math.PI - s.head; s.pos.x = Math.min(6.8, Math.max(1.2, s.pos.x)); }
        if (s.pos.y < 0.6 || s.pos.y > 4.4) { s.head = -s.head; s.pos.y = Math.min(4.4, Math.max(0.6, s.pos.y)); }
        const d = personD(s.pos);
        ex.push({ d, a: s.coef }, { d: d + 0.15 * Math.sin(2 * Math.PI * 1.8 * s.t), a: 0.3 });
        return ex;
      }
      if (s.mode === 'falling') {
        const u = (s.t - s.fallStart) / 0.9;
        if (u >= 1) {
          s.mode = 'down'; s.coef = 0.45; s.br = 0.31 + Math.random() * 0.05; s.brAmp = 0.008;
        } else {
          const m = Math.min(1, u / 0.55);
          s.pos = clampPos({ x: s.fallFrom.x + 0.8 * m * Math.cos(s.fallDir), y: s.fallFrom.y + 0.8 * m * Math.sin(s.fallDir) });
          s.coef = 0.6 - 0.15 * m;
          ex.push({ d: personD(s.pos), a: s.coef });
          if (u > 0.55) ex.push({ d: 6 + 3 * Math.random(), a: 2.4 });
          return ex;
        }
      }
      ex.push({ d: personD(s.pos) + s.brAmp * Math.sin(2 * Math.PI * s.br * s.t), a: s.coef });
      return ex;
    }
    return { s, set, step };
  }

  function makeBuffer(len) {
    const data = new Float32Array(len * N);
    let head = 0, count = 0;
    return {
      len,
      push(a) { data.set(a, head * N); head = (head + 1) % len; if (count < len) count++; },
      count: () => count,
      at(back, k) { const idx = (head - 1 - back + len * 2) % len; return data[idx * N + k]; }
    };
  }
  function varK(buf, n, k) {
    n = Math.min(n, buf.count());
    if (n < 2) return 0;
    let s = 0, s2 = 0;
    for (let b = 0; b < n; b++) { const v = buf.at(b, k); s += v; s2 += v * v; }
    const m = s / n;
    return Math.max(0, s2 / n - m * m);
  }
  function meanVar(buf, n) { let t = 0; for (let k = 0; k < N; k++) t += varK(buf, n, k); return t / N; }
  function topVar(buf, n) {
    let best = 0, bk = 0;
    for (let k = 0; k < N; k++) { const v = varK(buf, n, k); if (v > best) { best = v; bk = k; } }
    return { v: best, k: bk };
  }
  function topKs(buf, n, m) {
    const v = [];
    for (let k = 0; k < N; k++) v.push([varK(buf, n, k), k]);
    return v.sort((a, b) => b[0] - a[0]).slice(0, m).map(x => x[1]);
  }
  function breath(buf, n, ks, fs) {
    n = Math.min(n, buf.count());
    const means = ks.map(k => { let m = 0; for (let b = 0; b < n; b++) m += buf.at(b, k); return m / n; });
    const power = f => {
      let p = 0;
      ks.forEach((k, j) => {
        let re = 0, im = 0;
        for (let b = 0; b < n; b++) {
          const x = buf.at(b, k) - means[j], ph = 2 * Math.PI * f * b / fs;
          re += x * Math.cos(ph); im += x * Math.sin(ph);
        }
        p += re * re + im * im;
      });
      return p;
    };
    let bestF = 0, bestP = 0;
    for (let f = 0.1; f <= 0.6001; f += 0.005) { const p = power(f); if (p > bestP) { bestP = p; bestF = f; } }
    if (bestF / 2 >= 0.1 && power(bestF / 2) > 0.12 * bestP) bestF /= 2;
    return { f: bestF, perMin: bestF * 60 };
  }

  const TH = { move: 3e-4, moveOff: 1.5e-4, fall: 5e-3, pres: 2e-5 };
  function makeClassifier(fs) {
    const st = { moving: false, lastImpact: -99, fallen: false, stillSince: 0, label: 'GOL', v1: 0, v05: 0, top: { v: 0, k: 0 }, br: null, nextBr: 0, stillFor: 0 };
    function update(buf, t) {
      st.v1 = meanVar(buf, fs);
      st.v05 = meanVar(buf, Math.round(fs / 2));
      st.top = topVar(buf, fs * 3);
      if (st.v05 > TH.fall) st.lastImpact = t;
      const mv = st.moving ? st.v1 > TH.moveOff : st.v1 > TH.move;
      if (mv && !st.moving) { st.fallen = false; st.br = null; }
      if (!mv && st.moving) { st.fallen = t - st.lastImpact < 2.5; st.stillSince = t; }
      st.moving = mv;
      const prev = st.label;
      if (st.moving) st.label = 'MISCARE';
      else if (st.top.v > TH.pres) st.label = st.fallen ? 'LA_SOL' : 'NEMISCAT';
      else st.label = 'GOL';
      if (prev === 'GOL' && st.label !== 'GOL' && !st.moving) st.stillSince = t;
      st.stillFor = st.moving ? 0 : t - st.stillSince;
      if (st.label === 'GOL' || st.moving) st.br = null;
      else if (st.stillFor >= 8 && t >= st.nextBr) {
        st.br = breath(buf, Math.min(fs * 12, Math.floor(st.stillFor * fs)), topKs(buf, fs * 3, 3), fs);
        st.nextBr = t + 0.5;
      }
      return st;
    }
    return { st, update };
  }

  return { C, FC, DF, KS, N, FREQS, LAMBDA, ROOM, TX, RX, PATHS, TH, dist, personD, amps, makeScenario, makeBuffer, makeClassifier, meanVar, topVar };
})();
const FS=50, DT=1/FS;
function run(plan){
  const sc=Sim.makeScenario(), buf=Sim.makeBuffer(1000), clf=Sim.makeClassifier(FS), tmp=new Float32Array(Sim.N);
  let t=0; const out=[];
  for(const [mode,dur] of plan){ sc.set(mode); const n=Math.round(dur*FS);
    for(let i=0;i<n;i++){ Sim.amps(sc.step(DT),0.0015,tmp); buf.push(tmp); t+=DT; const st=clf.update(buf,t);
      if(i%25===24) out.push(`${t.toFixed(1)} ${mode.padEnd(5)} ${sc.s.mode.padEnd(7)} v1=${st.v1.toExponential(1)} v05=${st.v05.toExponential(1)} top=${st.top.v.toExponential(1)} -> ${st.label}${st.br?' br='+st.br.perMin.toFixed(1)+' true='+(sc.s.br*60).toFixed(1):''}`);
    }}
  return out;
}
const lines=run([['walk',3],['still',14],['walk',6],['fall',10],['empty',4],['walk',5],['still',3],['fall',11]]);
// summarize label transitions
let prev=''; for(const l of lines){ const lab=l.split('-> ')[1]; if(lab!==prev||/br=/.test(l)&&Math.random()<0.15){console.log(l);prev=lab;} }
