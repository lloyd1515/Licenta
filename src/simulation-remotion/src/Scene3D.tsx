import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { useVideoConfig } from "remotion";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { COLORS, LINKS, NODES, Node, placeBetween } from "./layout";
import { TimelineState } from "./timeline";
import { SecurityCamera } from "./SecurityCamera";
import { SubcarrierStrings } from "./SubcarrierStrings";
import { HumanModel } from "./HumanModel";

interface Scene3DProps {
  timeline: TimelineState;
}

const BLOCKED_ATTENUATION_DB = 8;

const EspNode: React.FC<{ node: Node; index: number; frame: number; opacity: number }> = ({
  node,
  index,
  frame,
  opacity,
}) => (
  <group position={node.position}>
    <mesh>
      <boxGeometry args={[0.25, 0.15, 0.25]} />
      <meshStandardMaterial
        color="#0d1b2a"
        roughness={0.2}
        metalness={0.9}
        transparent
        opacity={opacity}
      />
    </mesh>
    <mesh position={[0, 0.18, 0]}>
      <cylinderGeometry args={[0.02, 0.02, 0.22, 12]} />
      <meshBasicMaterial color={node.color} transparent opacity={opacity} />
    </mesh>
    <mesh position={[0, -0.06, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry
        args={[0.2, 0.28 + (Math.sin((frame + index * 20) * 0.15) * 0.05 + 0.05), 32]}
      />
      <meshBasicMaterial
        color={node.color}
        transparent
        opacity={opacity * 0.6}
        side={THREE.DoubleSide}
      />
    </mesh>
    <pointLight color={node.color} intensity={1.5 * opacity} distance={3} />
  </group>
);

const Ubertooth: React.FC<{ frame: number; opacity: number }> = ({ frame, opacity }) => (
  <group position={[2.6, 0.12, 2.0]}>
    <mesh>
      <boxGeometry args={[0.3, 0.1, 0.18]} />
      <meshStandardMaterial color="#1a1c22" metalness={0.9} transparent opacity={opacity} />
    </mesh>
    <mesh position={[0.12, 0.2, 0]} rotation={[0, 0, -0.2]}>
      <cylinderGeometry args={[0.015, 0.015, 0.35, 8]} />
      <meshBasicMaterial color={COLORS.amber} transparent opacity={opacity} />
    </mesh>
    <mesh position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, frame * 0.05]}>
      <ringGeometry args={[0.3, 0.36, 24]} />
      <meshBasicMaterial
        color={COLORS.amber}
        transparent
        opacity={opacity * 0.5}
        side={THREE.DoubleSide}
      />
    </mesh>
  </group>
);

const FresnelTube: React.FC<{
  from: THREE.Vector3;
  to: THREE.Vector3;
  color: string;
  attenuationDb: number;
  opacity: number;
}> = ({ from, to, color, attenuationDb, opacity }) => {
  const { position, length, quaternion } = placeBetween(from, to);
  const blocked = Math.abs(attenuationDb) > BLOCKED_ATTENUATION_DB;

  return (
    <group position={position} quaternion={quaternion}>
      <mesh>
        <cylinderGeometry args={[0.38, 0.38, length * 0.95, 24, 1, true]} />
        <meshStandardMaterial
          color={blocked ? COLORS.pink : color}
          transparent
          opacity={opacity * (blocked ? 0.9 : 0.4)}
          wireframe
        />
      </mesh>
    </group>
  );
};

const SceneContent: React.FC<Scene3DProps> = ({ timeline }) => {
  const { camera } = useThree();
  const { hardware, human, readouts } = timeline;

  React.useLayoutEffect(() => {
    camera.position.set(...timeline.camera.position);
    camera.lookAt(...timeline.camera.target);
    camera.updateProjectionMatrix();
  }, [camera, timeline.camera.position, timeline.camera.target]);

  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 10, 5]} intensity={1.2} />
      <pointLight position={[0, 4, 0]} intensity={2.0} color={COLORS.cyan} distance={15} />

      <SecurityCamera {...timeline.securityCamera} />

      <gridHelper args={[10, 20, COLORS.cyan, "#152238"]} position={[0, 0, 0]} />

      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[6, 6]} />
        <meshStandardMaterial
          color="#0a101d"
          transparent
          opacity={0.8}
          roughness={0.4}
          metalness={0.8}
        />
      </mesh>

      {hardware.nodesOpacity > 0.01 &&
        NODES.map((node, i) => (
          <EspNode
            key={node.id}
            node={node}
            index={i}
            frame={timeline.frame}
            opacity={hardware.nodesOpacity}
          />
        ))}

      {hardware.ubertoothOpacity > 0.01 && (
        <Ubertooth frame={timeline.frame} opacity={hardware.ubertoothOpacity} />
      )}

      <SubcarrierStrings
        opacity={hardware.stringsOpacity}
        frame={timeline.frame}
        humanPosition={human.position}
        fallen={human.fallen}
      />

      {hardware.fresnelTubesOpacity > 0.01 &&
        LINKS.map((link, i) => (
          <FresnelTube
            key={link.name}
            from={link.from.position}
            to={link.to.position}
            color={link.color}
            attenuationDb={readouts.links[i].attenuationDb}
            opacity={hardware.fresnelTubesOpacity}
          />
        ))}

      {human.visible && (
        <HumanModel human={human} fallAlarm={readouts.fallAlarm} frame={timeline.frame} />
      )}
    </>
  );
};

export const Scene3D: React.FC<Scene3DProps> = ({ timeline }) => {
  const { width, height } = useVideoConfig();

  return (
    <ThreeCanvas
      width={width}
      height={height}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
      }}
      camera={{
        fov: 45,
        position: timeline.camera.position,
        near: 0.1,
        far: 100,
      }}
    >
      <SceneContent timeline={timeline} />
    </ThreeCanvas>
  );
};
