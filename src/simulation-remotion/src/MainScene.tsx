import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { getTimelineState } from "./timeline";
import { Scene3D } from "./Scene3D";
import { Hud } from "./Hud";

export const MainScene: React.FC = () => {
  const frame = useCurrentFrame();
  const timeline = useMemo(() => getTimelineState(frame), [frame]);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        backgroundColor: "#070b14",
        overflow: "hidden",
      }}
    >
      <Scene3D timeline={timeline} />
      <Hud timeline={timeline} />
    </div>
  );
};
