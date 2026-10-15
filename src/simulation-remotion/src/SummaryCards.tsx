import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "./layout";
import { SUMMARY_START_FRAME } from "./timeline";

interface SummaryCardsProps {
  show: boolean;
}

const CARDS = [
  { label: "COST HARDWARE", value: "< 50 €", desc: "3x ESP32 + 1x Ubertooth", color: COLORS.green },
  { label: "INTIMITATE TOTALĂ", value: "100%", desc: "Zero camere • Fără purtabile", color: COLORS.cyan },
  { label: "TIMP DE REACȚIE", value: "< 500 ms", desc: "Alertă imediată la impact", color: COLORS.amber },
  { label: "ACURATEȚE DETECȚIE", value: "> 95%", desc: "Optică ondulatorie curată", color: COLORS.pink },
];

export const SummaryCards: React.FC<SummaryCardsProps> = ({ show }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!show) return null;

  const relativeFrame = Math.max(0, frame - SUMMARY_START_FRAME);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: "50%",
        transform: "translateX(-50%)",
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 24,
        width: 1200,
        pointerEvents: "none",
      }}
    >
      {CARDS.map((card, i) => {
        const cardSpring = spring({
          frame: relativeFrame - i * 6,
          fps,
          config: { damping: 12, stiffness: 120 },
        });

        const scale = interpolate(cardSpring, [0, 1], [0.8, 1]);
        const opacity = interpolate(cardSpring, [0, 1], [0, 1]);
        const y = interpolate(cardSpring, [0, 1], [30, 0]);

        return (
          <div
            key={card.label}
            style={{
              transform: `translateY(${y}px) scale(${scale})`,
              opacity,
              background: "rgba(10, 16, 29, 0.92)",
              border: `1px solid ${card.color}55`,
              borderRadius: 16,
              padding: "20px 24px",
              boxShadow: `0 8px 32px rgba(0, 0, 0, 0.6), 0 0 16px ${card.color}22`,
              backdropFilter: "blur(12px)",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 11, color: "#8ca0ba", fontWeight: 700, letterSpacing: 1.2 }}>
              {card.label}
            </div>
            <div
              style={{
                fontSize: 32,
                fontWeight: 900,
                color: card.color,
                marginTop: 6,
                letterSpacing: -0.5,
              }}
            >
              {card.value}
            </div>
            <div style={{ fontSize: 12, color: "#cfd9e8", marginTop: 4 }}>{card.desc}</div>
          </div>
        );
      })}
    </div>
  );
};
