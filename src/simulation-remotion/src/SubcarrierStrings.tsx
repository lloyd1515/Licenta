import React from "react";
import * as THREE from "three";
import { COLORS, LINKS, placeBetween } from "./layout";

const SAMPLED_SUBCARRIERS_PER_LINK = 18;
const SUBCARRIER_INDICES = Array.from({ length: SAMPLED_SUBCARRIERS_PER_LINK }, (_, i) => i - 9);

interface SubcarrierStringsProps {
  opacity: number;
  frame: number;
  humanPosition: [number, number, number];
  fallen: boolean;
}

export const SubcarrierStrings: React.FC<SubcarrierStringsProps> = ({
  opacity,
  frame,
  humanPosition,
  fallen,
}) => {
  if (opacity <= 0.01) return null;

  const human = new THREE.Vector3(...humanPosition);

  return (
    <group>
      {LINKS.map((link, linkIdx) => {
        const { position, length, quaternion } = placeBetween(link.from.position, link.to.position);
        const perturbed = human.distanceTo(position) < 1.6;
        const stringColor = fallen ? COLORS.alarm : perturbed ? COLORS.gold : link.color;

        return (
          <group key={link.name} position={position} quaternion={quaternion}>
            {SUBCARRIER_INDICES.map((k) => {
              const offset = (k / 9) * 0.18;
              const vibration = Math.sin(frame * 0.2 + k * 0.5 + linkIdx * 2.0) * (perturbed ? 0.08 : 0.02);

              return (
                <mesh key={k} position={[vibration + offset * 0.5, 0, offset]}>
                  <cylinderGeometry args={[0.005, 0.005, length * 0.98, 8]} />
                  <meshBasicMaterial
                    color={stringColor}
                    transparent
                    opacity={opacity * (perturbed ? 0.85 : 0.45)}
                  />
                </mesh>
              );
            })}
          </group>
        );
      })}
    </group>
  );
};
