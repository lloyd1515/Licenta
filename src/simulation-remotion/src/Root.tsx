import React from "react";
import { Composition } from "remotion";
import { MainScene } from "./MainScene";
import { FPS, TOTAL_FRAMES } from "./timeline";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="MainScene"
    component={MainScene}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
