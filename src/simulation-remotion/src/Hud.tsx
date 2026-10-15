import React from "react";
import { COLORS } from "./layout";
import { TimelineState } from "./timeline";
import { SummaryCards } from "./SummaryCards";

interface HudProps {
  timeline: TimelineState;
}

const CRITICAL_ATTENUATION_DB = 10;
const BAR_FULL_SCALE_DB = 20;
const MIN_BAR_PERCENT = 8;

const LABEL_STYLE: React.CSSProperties = {
  fontSize: 11,
  color: COLORS.cyan,
  fontWeight: 700,
  letterSpacing: 1.2,
  textTransform: "uppercase",
};

const FIELD_LABEL_STYLE: React.CSSProperties = { fontSize: 11, color: COLORS.fieldLabel };

const PANEL_BORDER = "1px solid rgba(255, 255, 255, 0.12)";

const VALUE_STYLE: React.CSSProperties = { fontSize: 17, fontWeight: 700 };

const Card: React.FC<{ style: React.CSSProperties; children: React.ReactNode }> = ({
  style,
  children,
}) => (
  <div
    style={{
      position: "absolute",
      background: "rgba(10, 16, 29, 0.88)",
      borderRadius: 14,
      backdropFilter: "blur(12px)",
      boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
      ...style,
    }}
  >
    {children}
  </div>
);

const TitleCard: React.FC<{ overlay: TimelineState["overlay"]; fallAlarm: boolean }> = ({
  overlay,
  fallAlarm,
}) => {
  const dotColor = fallAlarm ? COLORS.alarm : COLORS.cyan;
  const badgeColor = overlay.badgeColor || COLORS.cyan;

  return (
    <Card
      style={{
        top: 28,
        left: 36,
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "14px 24px",
        border: "1px solid rgba(0, 240, 255, 0.3)",
        maxWidth: 960,
      }}
    >
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: dotColor,
          boxShadow: `0 0 12px ${dotColor}`,
          flexShrink: 0,
        }}
      />
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: -0.5 }}>{overlay.title}</span>
          {overlay.badgeText && (
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                padding: "3px 8px",
                borderRadius: 6,
                backgroundColor: `${badgeColor}22`,
                color: badgeColor,
                border: `1px solid ${badgeColor}55`,
                textTransform: "uppercase",
              }}
            >
              {overlay.badgeText}
            </span>
          )}
        </div>
        <div style={{ fontSize: 13, color: COLORS.subtitle, marginTop: 4 }}>{overlay.subtitle}</div>
      </div>
    </Card>
  );
};

const ReadoutsCard: React.FC<{ readouts: TimelineState["readouts"] }> = ({ readouts }) => (
  <Card
    style={{
      top: 28,
      right: 36,
      padding: "16px 20px",
      border: PANEL_BORDER,
      minWidth: 260,
    }}
  >
    <div style={LABEL_STYLE}>TELEMETRIE RADAR 2D</div>

    <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      <div>
        <div style={FIELD_LABEL_STYLE}>Poziție (X, Z)</div>
        <div style={{ ...VALUE_STYLE, color: COLORS.white }}>
          {readouts.x.toFixed(2)}m, {readouts.z.toFixed(2)}m
        </div>
      </div>
      <div>
        <div style={FIELD_LABEL_STYLE}>Viteză (v)</div>
        <div
          style={{
            ...VALUE_STYLE,
            color: readouts.speedMps > 2 ? COLORS.orange : COLORS.white,
          }}
        >
          {readouts.speedMps.toFixed(2)} m/s
        </div>
      </div>
      <div>
        <div style={FIELD_LABEL_STYLE}>Doppler Shift</div>
        <div
          style={{
            ...VALUE_STYLE,
            color: readouts.dopplerHz > 30 ? COLORS.pink : COLORS.green,
          }}
        >
          {readouts.dopplerHz.toFixed(1)} Hz
        </div>
      </div>
      <div>
        <div style={FIELD_LABEL_STYLE}>Stare Persoană</div>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: readouts.fallAlarm ? COLORS.alarm : COLORS.cyan,
          }}
        >
          {readouts.stateLabel}
        </div>
      </div>
    </div>
  </Card>
);

const CsiBarsCard: React.FC<{ links: TimelineState["readouts"]["links"] }> = ({ links }) => (
  <Card
    style={{
      bottom: 36,
      left: 36,
      padding: "16px 20px",
      border: PANEL_BORDER,
      width: 380,
    }}
  >
    <div style={LABEL_STYLE}>ANVELOPĂ CSI PE 52 SUBPURTĂTOARE OFDM</div>

    <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10 }}>
      {links.map((link) => {
        const barPercent = Math.min(
          100,
          Math.max(MIN_BAR_PERCENT, (Math.abs(link.attenuationDb) / BAR_FULL_SCALE_DB) * 100)
        );
        const critical = Math.abs(link.attenuationDb) > CRITICAL_ATTENUATION_DB;
        return (
          <div key={link.name}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 12,
                marginBottom: 4,
              }}
            >
              <span style={{ color: COLORS.linkName }}>{link.name}</span>
              <span style={{ color: critical ? COLORS.pink : COLORS.green, fontWeight: 600 }}>
                {link.attenuationDb > 0 ? "+" : ""}
                {link.attenuationDb} dB
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: 8,
                background: COLORS.barTrack,
                borderRadius: 4,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${barPercent}%`,
                  height: "100%",
                  background: critical
                    ? `linear-gradient(90deg, ${COLORS.orange}, ${COLORS.alarm})`
                    : `linear-gradient(90deg, ${COLORS.cyan}, ${COLORS.green})`,
                  borderRadius: 4,
                  transition: "width 0.05s ease-out",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>

    <div
      style={{
        fontSize: 11,
        color: COLORS.footnote,
        marginTop: 10,
        display: "flex",
        justifyContent: "space-between",
      }}
    >
      <span>Frecvență eșantionare: 500 Hz</span>
      <span>Zonă Fresnel: λ/2 = 6.15 cm</span>
    </div>
  </Card>
);

const AlarmBanner: React.FC<{ dopplerHz: number }> = ({ dopplerHz }) => (
  <div
    style={{
      position: "absolute",
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
      background: "rgba(220, 0, 40, 0.94)",
      border: `2px solid ${COLORS.white}`,
      borderRadius: 16,
      padding: "24px 48px",
      textAlign: "center",
      boxShadow: "0 0 70px rgba(255, 0, 50, 0.85)",
    }}
  >
    <div style={{ fontSize: 36, fontWeight: 900, letterSpacing: -1, color: COLORS.white }}>
      🚨 ALERTA: CĂDERE DETECTATĂ
    </div>
    <div style={{ fontSize: 16, fontWeight: 500, color: COLORS.alarmSubtitle, marginTop: 8 }}>
      Colaps simultan CSI pe 3 legături • Vârf Doppler {dopplerHz.toFixed(1)} Hz • Imobilitate Sol
    </div>
  </div>
);

export const Hud: React.FC<HudProps> = ({ timeline }) => {
  const { overlay, readouts, frame, act } = timeline;
  const alarmPulse = Math.sin(frame * 0.4) * 0.3 + 0.7;
  const showPanels = act >= 2 && !overlay.showSummaryCards;

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        fontFamily: "'Inter', -apple-system, sans-serif",
        color: COLORS.white,
        overflow: "hidden",
      }}
    >
      {readouts.fallAlarm && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: `inset 0 0 140px rgba(255, 0, 50, ${0.45 * alarmPulse})`,
            border: `6px solid rgba(255, 0, 50, ${0.85 * alarmPulse})`,
            transition: "all 0.08s ease-out",
          }}
        />
      )}

      <TitleCard overlay={overlay} fallAlarm={readouts.fallAlarm} />
      {showPanels && <ReadoutsCard readouts={readouts} />}
      {showPanels && <CsiBarsCard links={readouts.links} />}
      {readouts.fallAlarm && <AlarmBanner dopplerHz={readouts.dopplerHz} />}
      <SummaryCards show={overlay.showSummaryCards} />
    </div>
  );
};
