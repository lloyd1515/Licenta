import * as THREE from "three";
import { COLORS, LINKS } from "./layout";

type Vec3 = [number, number, number];

export interface LinkReading {
  name: string;
  attenuationDb: number;
}

export interface TimelineState {
  frame: number;
  act: 1 | 2 | 3 | 4 | 5;
  camera: { position: Vec3; target: Vec3 };
  securityCamera: { opacity: number; coneOpacity: number; showBanSign: boolean };
  hardware: {
    nodesOpacity: number;
    ubertoothOpacity: number;
    stringsOpacity: number;
    fresnelTubesOpacity: number;
  };
  human: {
    visible: boolean;
    position: Vec3;
    tiltX: number;
    fallen: boolean;
    ringColor: string;
  };
  readouts: {
    x: number;
    z: number;
    speedMps: number;
    dopplerHz: number;
    stateLabel: string;
    links: LinkReading[];
    fallAlarm: boolean;
  };
  overlay: {
    title: string;
    subtitle: string;
    badgeText?: string;
    badgeColor?: string;
    showSummaryCards: boolean;
  };
}

type Changes = {
  [K in Exclude<keyof TimelineState, "frame" | "act">]?: Partial<TimelineState[K]>;
};

export const FPS = 30;
export const DURATION_S = 100;
export const TOTAL_FRAMES = FPS * DURATION_S;
export const ACT_END_FRAMES = [450, 1050, 1800, 2550, TOTAL_FRAMES] as const;
export const SUMMARY_START_FRAME = 2650;
export const FALL_START_FRAME = 1920;
export const FALL_DURATION_FRAMES = 15;
export const ALARM_DELAY_FRAMES = 15;

const FALL_END_FRAME = FALL_START_FRAME + FALL_DURATION_FRAMES;
const STANDING_HEIGHT_M = 0.9;
const FALLEN_HEIGHT_M = 0.18;
const FALL_DROP_M = 0.72;
const FALLEN_POSITION: Vec3 = [0.1, FALLEN_HEIGHT_M, 0.0];

const DEFAULT_STATE: Omit<TimelineState, "frame" | "act"> = {
  camera: { position: [0, 0, 0], target: [0, 0, 0] },
  securityCamera: { opacity: 0, coneOpacity: 0, showBanSign: false },
  hardware: { nodesOpacity: 0, ubertoothOpacity: 0, stringsOpacity: 0, fresnelTubesOpacity: 0 },
  human: { visible: false, position: [0, 0, 0], tiltX: 0, fallen: false, ringColor: COLORS.cyan },
  readouts: {
    x: 0,
    z: 0,
    speedMps: 0,
    dopplerHz: 0,
    stateLabel: "",
    links: LINKS.map((link) => ({ name: link.name, attenuationDb: 0 })),
    fallAlarm: false,
  },
  overlay: { title: "", subtitle: "", showSummaryCards: false },
};

function clamp01(v: number): number {
  return Math.max(0, Math.min(1, v));
}

function smoothstep(min: number, max: number, value: number): number {
  const x = clamp01((value - min) / (max - min));
  return x * x * (3 - 2 * x);
}

function withLinks(attenuationsDb: number[]): LinkReading[] {
  return LINKS.map((link, i) => ({ name: link.name, attenuationDb: attenuationsDb[i] }));
}

function build(frame: number, act: TimelineState["act"], changes: Changes): TimelineState {
  return {
    frame,
    act,
    camera: { ...DEFAULT_STATE.camera, ...changes.camera },
    securityCamera: { ...DEFAULT_STATE.securityCamera, ...changes.securityCamera },
    hardware: { ...DEFAULT_STATE.hardware, ...changes.hardware },
    human: { ...DEFAULT_STATE.human, ...changes.human },
    readouts: { ...DEFAULT_STATE.readouts, ...changes.readouts },
    overlay: { ...DEFAULT_STATE.overlay, ...changes.overlay },
  };
}

interface Caption {
  from: number;
  title: string;
  subtitle: string;
  badgeText?: string;
  badgeColor?: string;
}

function captionAt(frame: number, captions: Caption[]): Omit<Caption, "from"> {
  const { from, ...caption } = captions.filter((c) => c.from <= frame).pop() ?? captions[0];
  return caption;
}

function problemAct(frame: number): TimelineState {
  const p = frame / ACT_END_FRAMES[0];
  const s = smoothstep(0.25, 0.85, p);
  return build(frame, 1, {
    camera: {
      position: [
        THREE.MathUtils.lerp(0.3, 3.6, s),
        THREE.MathUtils.lerp(2.1, 3.8, s),
        THREE.MathUtils.lerp(1.7, 3.9, s),
      ],
      target: [0, THREE.MathUtils.lerp(2.1, 0.7, s), THREE.MathUtils.lerp(-1.0, 0.0, s)],
    },
    securityCamera: {
      opacity: frame < 200 ? 1 : 1 - smoothstep(200, 270, frame),
      coneOpacity: frame < 180 ? 0.35 : (1 - smoothstep(180, 240, frame)) * 0.35,
      showBanSign: frame >= 140 && frame < 280,
    },
    readouts: { stateLabel: "CAMERA GOALĂ" },
    overlay: captionAt(frame, [
      {
        from: 0,
        title: "CĂDEREA: PERICOLUL TĂCUT AL VÂRSTNICILOR",
        subtitle: "70% din accidente au loc acolo unde sunt singuri: în dormitor sau baie.",
      },
      {
        from: 140,
        title: "CAMERELE VIDEO? O ÎNCĂLCARE A INTIMITĂȚII.",
        subtitle: "Nimeni nu acceptă camere în baie sau dormitor. Pacienții le refuză.",
        badgeText: "CAMERA = REFUZATĂ",
        badgeColor: COLORS.pink,
      },
      {
        from: 280,
        title: "SENZORI PURTABILI? UITAȚI PE NOPTIERĂ.",
        subtitle: "Brățările de urgență nu sunt purtate noaptea. Există o cale 100% invizibilă.",
        badgeText: "SOLUȚIE INVIZIBILĂ",
        badgeColor: COLORS.cyan,
      },
    ]),
  });
}

function hardwareAct(frame: number): TimelineState {
  const p = (frame - ACT_END_FRAMES[0]) / (ACT_END_FRAMES[1] - ACT_END_FRAMES[0]);
  return build(frame, 2, {
    camera: {
      position: [
        3.6 + Math.sin(p * Math.PI) * 0.25,
        3.8 - Math.sin(p * Math.PI) * 0.15,
        3.9 - Math.sin(p * Math.PI * 0.5) * 0.2,
      ],
      target: [0, 0.7, 0],
    },
    hardware: {
      nodesOpacity: smoothstep(450, 520, frame),
      ubertoothOpacity: smoothstep(500, 580, frame),
      stringsOpacity: smoothstep(580, 720, frame),
    },
    readouts: { stateLabel: "CAMERA GOALĂ (0 dB)", links: withLinks([0.1, 0.0, -0.1]) },
    overlay: captionAt(frame, [
      {
        from: 0,
        title: "HARDWARE DE SUB 50€: TREI NODURI WI-FI",
        subtitle: "Plăcuțe comerciale ESP32 conectate într-o rețea triunghiulară sincronă.",
        badgeText: "3x ESP32 • < 50€",
        badgeColor: COLORS.green,
      },
      {
        from: 650,
        title: "WI-FI NU E O SINGURĂ UNDĂ: E O HARPĂ RADIO",
        subtitle: "52 de subpurtătoare OFDM se întind în spațiu ca 52 de filamente invizibile.",
        badgeText: "52 SUBPURTĂTOARE OFDM",
        badgeColor: COLORS.cyan,
      },
      {
        from: 850,
        title: "CÂND CAMERA E GOALĂ, CORZILE STAU NEMIȘCATE",
        subtitle: "Nivelul de referință este stabil la 0 dB. Ce se întâmplă când intră un om?",
        badgeText: "STARE: REFERINȚĂ CALMĂ",
        badgeColor: COLORS.amber,
      },
    ]),
  });
}

function walkingAct(frame: number): TimelineState {
  const walk = smoothstep(1100, 1750, frame);
  const x = 2.0 - 2.2 * Math.sin(walk * Math.PI * 0.5);
  const z = 2.0 - 2.4 * walk;
  const y = STANDING_HEIGHT_M + Math.sin(frame * 0.3) * 0.04;
  const distance12 = Math.hypot(x - -2.0, z - 0.0);
  const distance31 = Math.hypot(x - 0.0, z - 0.0);
  const attenuation12 = Number((-14.5 * Math.exp(-(distance12 * distance12) / 0.8)).toFixed(1));
  const attenuation31 = Number((-17.2 * Math.exp(-(distance31 * distance31) / 0.6)).toFixed(1));
  return build(frame, 3, {
    camera: {
      position: [3.6 - walk * 0.4, 3.8, 3.9 - walk * 0.3],
      target: [x * 0.5, 0.7, z * 0.5],
    },
    hardware: {
      nodesOpacity: 1,
      ubertoothOpacity: 1,
      stringsOpacity: 1,
      fresnelTubesOpacity: smoothstep(1150, 1300, frame) * 0.4,
    },
    human: { visible: true, position: [x, y, z] },
    readouts: {
      x: Number(x.toFixed(2)),
      z: Number(z.toFixed(2)),
      speedMps: 0.95,
      dopplerHz: 15.4,
      stateLabel: "MERS NORMAL",
      links: withLinks([attenuation12, 1.2, attenuation31]),
    },
    overlay: captionAt(frame, [
      {
        from: 0,
        title: "CORPUL UMAN: 70% APĂ, OBSTACOL RADIO MASIV",
        subtitle: "Unda directă se reflectă și se refractă la fiecare pas.",
        badgeText: "PERSOANĂ ÎN MIȘCARE",
        badgeColor: COLORS.cyan,
      },
      {
        from: 1300,
        title: "ZONA FRESNEL: TUNELUL INVIZIBIL DE SENSIBILITATE",
        subtitle: "Pășirea în elipsă produce oscilații sinusoidale deterministe pe 52 de frecvențe.",
        badgeText: "DIFRACȚIE FRESNEL (15-20 dB)",
        badgeColor: COLORS.gold,
      },
      {
        from: 1550,
        title: "LOCALIZARE 2D PUR GEOMETRICĂ: COORDONATE (X, Z)",
        subtitle: "Intersecția celor 3 elipse dă poziția exactă a pasului, fără camere.",
        badgeText: "TRAIECTORIE ACTIVĂ",
        badgeColor: COLORS.green,
      },
    ]),
  });
}

function fallAct(frame: number): TimelineState {
  const falling = frame >= FALL_START_FRAME && frame < FALL_END_FRAME;
  const landed = frame >= FALL_END_FRAME;
  const fallen = falling || landed;
  const fallAlarm = frame >= FALL_END_FRAME + ALARM_DELAY_FRAMES;
  const t = (frame - FALL_START_FRAME) / FALL_DURATION_FRAMES;

  let y = STANDING_HEIGHT_M;
  let tiltX = 0;
  let speedMps = 0.8;
  let dopplerHz = 14.0;
  if (falling) {
    y = STANDING_HEIGHT_M - FALL_DROP_M * (t * t);
    tiltX = (Math.PI / 2) * t;
    speedMps = 2.8;
    dopplerHz = 48.5;
  } else if (landed) {
    y = FALLEN_HEIGHT_M;
    tiltX = Math.PI / 2;
    speedMps = 0.0;
    dopplerHz = 0.4;
  }

  return build(frame, 4, {
    camera: { position: [3.2, landed ? 3.0 : 3.8, landed ? 3.2 : 3.9], target: [0, 0.3, 0] },
    hardware: { nodesOpacity: 1, ubertoothOpacity: 1, stringsOpacity: 1, fresnelTubesOpacity: 0.5 },
    human: {
      visible: true,
      position: [0.1, y, 0.0],
      tiltX,
      fallen,
      ringColor: fallAlarm ? COLORS.alarm : COLORS.orange,
    },
    readouts: {
      x: 0.1,
      z: 0.0,
      speedMps,
      dopplerHz,
      stateLabel: fallAlarm ? "🚨 CĂDERE LA SOL" : fallen ? "IMPACT CĂDERE" : "CLĂTINARE",
      links: withLinks(fallen ? [-18.2, -17.8, -19.4] : [-4.5, -2.1, -3.8]),
      fallAlarm,
    },
    overlay: captionAt(frame, [
      {
        from: 0,
        title: "O CĂDERE DUREAZĂ SUB 400 MS: VÂRF DOPPLER > 45 HZ",
        subtitle: "Gravitația prăbușește corpul spre podea. Semnătură fizică inconfundabilă.",
        badgeText: "IMPACT ACCELERAT",
        badgeColor: COLORS.orange,
      },
      {
        from: 1950,
        title: "COLAPS SIMULTAN PE TOATE CELE 3 LEGĂTURI",
        subtitle: "Mersul atinge o legătură pe rând. Căderea la sol taie baza întregului spațiu radio.",
        badgeText: "COLAPS SIMULTAN CSI (-18 dB)",
        badgeColor: COLORS.alarm,
      },
      {
        from: 2250,
        title: "ALERTĂ DE SALVARE TRANSMISĂ ÎN TIMP REAL",
        subtitle: "Impact violent confirmat + 3 secunde de imobilitate la sol = 0 alarme false.",
        badgeText: "NOTIFICARE URGENȚĂ",
        badgeColor: COLORS.alarm,
      },
    ]),
  });
}

function summaryAct(frame: number): TimelineState {
  const p = (frame - ACT_END_FRAMES[3]) / (ACT_END_FRAMES[4] - ACT_END_FRAMES[3]);
  const s = smoothstep(0, 0.8, p);
  return build(frame, 5, {
    camera: {
      position: [
        THREE.MathUtils.lerp(3.2, 4.8, s),
        THREE.MathUtils.lerp(3.0, 5.2, s),
        THREE.MathUtils.lerp(3.2, 4.8, s),
      ],
      target: [0, 0.5, 0],
    },
    hardware: { nodesOpacity: 1, ubertoothOpacity: 1, stringsOpacity: 0.6, fresnelTubesOpacity: 0.2 },
    human: { visible: true, position: FALLEN_POSITION, tiltX: Math.PI / 2, fallen: true },
    readouts: {
      x: 0.1,
      dopplerHz: 0.2,
      stateLabel: "SISTEM ACTIV",
      links: withLinks([-18.2, -17.8, -19.4]),
    },
    overlay: {
      title: "WI-FI CSI FRESNEL CARTOGRAPHY & FALL DETECTION",
      subtitle: "Lucrare de Licență • Hardware < 50€ • 100% Intimitate Protejată",
      badgeText: "PROIECT DE LICENȚĂ VALIDAT",
      badgeColor: COLORS.cyan,
      showSummaryCards: frame >= SUMMARY_START_FRAME,
    },
  });
}

export function getTimelineState(frame: number): TimelineState {
  if (frame < ACT_END_FRAMES[0]) return problemAct(frame);
  if (frame < ACT_END_FRAMES[1]) return hardwareAct(frame);
  if (frame < ACT_END_FRAMES[2]) return walkingAct(frame);
  if (frame < ACT_END_FRAMES[3]) return fallAct(frame);
  return summaryAct(frame);
}
