import React from "react";
import * as THREE from "three";
import { COLORS } from "./layout";
import { TimelineState } from "./timeline";

interface HumanModelProps {
  human: TimelineState["human"];
  fallAlarm: boolean;
  frame: number;
}

export const HumanModel: React.FC<HumanModelProps> = ({ human, fallAlarm, frame }) => (
  <group position={human.position} rotation={[human.tiltX, 0, 0]}>
    <mesh position={[0, 0.55, 0]}>
      <sphereGeometry args={[0.13, 16, 16]} />
      <meshStandardMaterial
        color={fallAlarm ? COLORS.alarm : COLORS.cyan}
        emissive={fallAlarm ? COLORS.alarm : "#003355"}
        emissiveIntensity={fallAlarm ? 0.8 : 0.3}
        roughness={0.2}
      />
    </mesh>
    <mesh position={[0, 0.15, 0]}>
      <capsuleGeometry args={[0.18, 0.45, 8, 16]} />
      <meshStandardMaterial
        color={fallAlarm ? COLORS.pink : "#1a2c42"}
        roughness={0.3}
        metalness={0.7}
      />
    </mesh>
    <mesh position={[0, 0.12, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.22, 0.27, 24]} />
      <meshBasicMaterial color={human.ringColor} transparent opacity={0.8} side={THREE.DoubleSide} />
    </mesh>
    {human.fallen && (
      <mesh position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.3, 0.8 + Math.sin(frame * 0.2) * 0.1, 32]} />
        <meshBasicMaterial color={COLORS.alarm} transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>
    )}
  </group>
);
