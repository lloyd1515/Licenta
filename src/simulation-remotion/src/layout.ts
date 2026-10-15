import * as THREE from "three";

export const COLORS = {
  cyan: "#00f0ff",
  green: "#00ff88",
  amber: "#ffb700",
  gold: "#ffaa00",
  orange: "#ff5500",
  pink: "#ff2a55",
  alarm: "#ff0033",
  white: "#ffffff",
  fieldLabel: "#8ca0ba",
  subtitle: "#9bb0cb",
  linkName: "#d0d9e5",
  footnote: "#61758f",
  barTrack: "#1a2639",
  alarmSubtitle: "#ffe0e5",
} as const;

export interface Node {
  id: number;
  position: THREE.Vector3;
  color: string;
}

export interface Link {
  name: string;
  from: Node;
  to: Node;
  color: string;
}

export const NODES: readonly Node[] = [
  { id: 1, position: new THREE.Vector3(-2.0, 1.2, 2.0), color: COLORS.cyan },
  { id: 2, position: new THREE.Vector3(-2.0, 1.2, -2.0), color: COLORS.green },
  { id: 3, position: new THREE.Vector3(2.0, 1.2, -2.0), color: COLORS.amber },
];

export const LINKS: readonly Link[] = NODES.map((from, i) => {
  const to = NODES[(i + 1) % NODES.length];
  return { name: `Link ${from.id}-${to.id}`, from, to, color: from.color };
});

export function placeBetween(a: THREE.Vector3, b: THREE.Vector3) {
  const position = new THREE.Vector3().addVectors(a, b).multiplyScalar(0.5);
  const length = a.distanceTo(b);
  const direction = new THREE.Vector3().subVectors(b, a).normalize();
  const quaternion = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction
  );
  return { position, length, quaternion };
}
