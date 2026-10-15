import React from "react";
import * as THREE from "three";
import { COLORS } from "./layout";

interface SecurityCameraProps {
  opacity: number;
  coneOpacity: number;
  showBanSign: boolean;
}

export const SecurityCamera: React.FC<SecurityCameraProps> = ({
  opacity,
  coneOpacity,
  showBanSign,
}) => {
  if (opacity <= 0.01) return null;

  return (
    <group position={[0, 2.3, -1.0]} rotation={[0.35, 0, 0]}>
      <mesh position={[0, 0.1, -0.3]}>
        <boxGeometry args={[0.7, 0.7, 0.06]} />
        <meshStandardMaterial
          color="#1e2638"
          roughness={0.5}
          metalness={0.5}
          transparent
          opacity={opacity}
          wireframe={opacity < 0.9}
        />
      </mesh>

      <mesh position={[0, 0, -0.15]}>
        <boxGeometry args={[0.16, 0.16, 0.35]} />
        <meshStandardMaterial
          color="#333a45"
          transparent
          opacity={opacity}
          wireframe={opacity < 0.9}
        />
      </mesh>

      <mesh position={[0, -0.1, 0.1]} rotation={[Math.PI / 6, 0, 0]}>
        <cylinderGeometry args={[0.15, 0.18, 0.6, 16]} />
        <meshStandardMaterial
          color="#1e2530"
          roughness={0.3}
          metalness={0.8}
          transparent
          opacity={opacity}
          wireframe={opacity < 0.9}
        />
      </mesh>

      <mesh position={[0, -0.38, 0.28]} rotation={[Math.PI / 6, 0, 0]}>
        <cylinderGeometry args={[0.14, 0.14, 0.05, 16]} />
        <meshBasicMaterial color={COLORS.cyan} transparent opacity={opacity * 0.8} />
      </mesh>

      <mesh position={[0.1, -0.35, 0.35]}>
        <sphereGeometry args={[0.03, 8, 8]} />
        <meshBasicMaterial color={COLORS.alarm} transparent opacity={opacity} />
      </mesh>

      {coneOpacity > 0.01 && (
        <group position={[0, -0.4, 0.3]} rotation={[Math.PI / 6, 0, 0]}>
          <mesh position={[0, -2.5, 0]}>
            <cylinderGeometry args={[0.15, 2.2, 5.0, 16, 1, true]} />
            <meshBasicMaterial
              color={COLORS.pink}
              transparent
              opacity={coneOpacity}
              side={THREE.DoubleSide}
              wireframe
            />
          </mesh>
        </group>
      )}

      {showBanSign && (
        <group position={[0, -0.5, 0.5]}>
          <mesh>
            <ringGeometry args={[0.4, 0.48, 32]} />
            <meshBasicMaterial color={COLORS.alarm} side={THREE.DoubleSide} />
          </mesh>
          <mesh rotation={[0, 0, Math.PI / 4]}>
            <boxGeometry args={[0.85, 0.08, 0.01]} />
            <meshBasicMaterial color={COLORS.alarm} />
          </mesh>
        </group>
      )}
    </group>
  );
};
