import React, { useLayoutEffect, useRef } from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import rawDots from "../dots.json";
import { BatikDot, renderBatikDotsFrame } from "./batikDots";

const BATIK_DOTS: readonly BatikDot[] = rawDots;

export type BatikHeroProps = {
  readonly mode: "entrance" | "loop";
  readonly bgColor: string;
  readonly inkColor: string;
  readonly stippleDensity: number;
  readonly maxIntensity: number;
  readonly showHeroOverlay: boolean;
};

const BatikCanvasLayer: React.FC<{
  readonly mode: "entrance" | "loop";
  readonly bgColor: string;
  readonly inkColor: string;
  readonly stippleDensity: number;
  readonly maxIntensity: number;
}> = ({ mode, bgColor, inkColor, stippleDensity, maxIntensity }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const entranceT =
    mode === "loop"
      ? 1
      : interpolate(frame, [0, 2 * fps], [0, 1], {
          easing: Easing.bezier(0.32, 0.08, 0.45, 1),
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const loopFrames = mode === "loop" ? Math.max(1, durationInFrames) : 10 * fps;
  const loopPhase =
    mode === "loop"
      ? ((frame % loopFrames) / loopFrames) * Math.PI * 2
      : ((frame - 2 * fps) / loopFrames) * Math.PI * 2;

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    renderBatikDotsFrame(ctx, BATIK_DOTS, {
      width,
      height,
      entranceT,
      loopPhase,
      dotScale: Math.max(0.55, Math.min(1.45, stippleDensity)),
      maxIntensity: Math.max(0.2, Math.min(1, maxIntensity)),
      bgColor,
      inkColor,
    });
  }, [width, height, entranceT, loopPhase, stippleDensity, maxIntensity, bgColor, inkColor]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        display: "block",
        width: "100%",
        height: "100%",
      }}
    />
  );
};

const HeroTypographyOverlay: React.FC<{ readonly mode: "entrance" | "loop" }> = ({
  mode,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const isLoop = mode === "loop";

  const ruleScale = isLoop
    ? 1
    : interpolate(frame, [0, 1.6 * fps], [0, 1], {
        easing: Easing.bezier(0.45, 0, 0.55, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const titleY = isLoop
    ? 0
    : interpolate(frame, [0.15 * fps, 1.35 * fps], [120, 0], {
        easing: Easing.bezier(0.16, 1, 0.3, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const titleOpacity = isLoop
    ? 1
    : interpolate(frame, [0.15 * fps, 0.65 * fps], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const leadOpacity = isLoop
    ? 1
    : interpolate(frame, [0.7 * fps, 1.45 * fps], [0, 1], {
        easing: Easing.bezier(0.16, 1, 0.3, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const leadY = isLoop
    ? 0
    : interpolate(frame, [0.7 * fps, 1.45 * fps], [24, 0], {
        easing: Easing.bezier(0.16, 1, 0.3, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const cornerScale = isLoop
    ? 1
    : interpolate(frame, [1.45 * fps, 1.9 * fps], [0, 1], {
        easing: Easing.bezier(0.34, 1.56, 0.64, 1),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  const textHalo =
    "0 0 4px #141414, 0 0 4px #141414, 0 0 4px #141414, 0 0 10px #141414, 0 0 10px #141414";

  return (
    <AbsoluteFill
      style={{
        paddingLeft: 240,
        paddingRight: 240,
        fontFamily: "Inter, system-ui, -apple-system, sans-serif",
        color: "#F2F2F2",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          paddingLeft: 39,
          paddingRight: 39,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {[0.25, 0.5, 0.75].map((pos) => (
          <div
            key={pos}
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `calc(39px + (100% - 78px) * ${pos})`,
              width: 1,
              backgroundColor: "#262626",
              transformOrigin: "top",
              scale: `1 ${ruleScale}`,
            }}
          />
        ))}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            paddingTop: 30,
            fontSize: 14,
            alignItems: "baseline",
            textShadow: textHalo,
          }}
        >
          <span style={{ fontWeight: 600, fontSize: 16, letterSpacing: "-0.02em" }}>
            vadhh
          </span>
          <div
            style={{
              gridColumn: "2 / 4",
              display: "flex",
              justifyContent: "space-between",
              paddingRight: 60,
              color: "#8C8C8C",
            }}
          >
            <span>Work</span>
            <span>Experience</span>
            <span>About</span>
            <span>Contact</span>
          </div>
          <span style={{ justifySelf: "start" }}>Start a project ↗</span>
        </div>

        <div
          style={{
            position: "absolute",
            top: 96,
            left: 39,
            width: 13,
            height: 13,
            borderTop: "1.5px solid #FFFFFF",
            borderLeft: "1.5px solid #FFFFFF",
            scale: cornerScale,
            opacity: cornerScale,
          }}
        />
        <div
          style={{
            position: "absolute",
            top: 96,
            right: 39,
            width: 13,
            height: 13,
            borderTop: "1.5px solid #FFFFFF",
            borderRight: "1.5px solid #FFFFFF",
            scale: cornerScale,
            opacity: cornerScale,
          }}
        />

        <div
          style={{
            marginTop: "auto",
            paddingBottom: 56,
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            alignItems: "end",
            textShadow: textHalo,
          }}
        >
          <div style={{ gridColumn: "1 / -1", overflow: "hidden" }}>
            <h1
              style={{
                margin: 0,
                fontWeight: 600,
                fontSize: 185,
                lineHeight: 0.9,
                letterSpacing: "-0.06em",
                whiteSpace: "nowrap",
                translate: `0px ${titleY}px`,
                opacity: titleOpacity,
              }}
            >
              Afridho Tavadhu
            </h1>
          </div>

          <p
            style={{
              gridColumn: "1 / 3",
              marginTop: 44,
              marginBottom: 0,
              paddingRight: 30,
              fontSize: 30,
              lineHeight: 1.25,
              letterSpacing: "-0.03em",
              color: "#8C8C8C",
              opacity: leadOpacity,
              translate: `0px ${leadY}px`,
            }}
          >
            <span style={{ color: "#F2F2F2" }}>
              I build AI features and web apps that hold up
            </span>{" "}
            in production, from first prototype to launch.
          </p>

          <div
            style={{
              gridColumn: "3 / 5",
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              opacity: leadOpacity,
              translate: `0px ${leadY}px`,
            }}
          >
            <span
              style={{
                marginLeft: 30,
                fontSize: 20,
                paddingBottom: 14,
                borderBottom: "2px solid #FFFFFF",
                justifySelf: "start",
              }}
            >
              Start a project &nbsp; ↗
            </span>
            <span
              style={{
                marginLeft: 30,
                fontSize: 20,
                paddingBottom: 14,
                borderBottom: "2px solid #FFFFFF",
                justifySelf: "start",
              }}
            >
              See selected work &nbsp; ↓
            </span>
          </div>
        </div>

        <div
          style={{
            borderTop: "1px solid #262626",
            padding: "24px 0 36px",
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            opacity: leadOpacity,
            translate: `0px ${leadY}px`,
            textShadow: textHalo,
          }}
        >
          <div style={{ gridColumn: "1 / 3" }}>
            <div style={{ fontSize: 13, fontFamily: "monospace", color: "#8C8C8C" }}>
              Based in
            </div>
            <div style={{ fontSize: 18 }}>Yogyakarta, Indonesia</div>
          </div>
          <div style={{ paddingLeft: 30 }}>
            <div style={{ fontSize: 13, fontFamily: "monospace", color: "#8C8C8C" }}>
              Education
            </div>
            <div style={{ fontSize: 18 }}>B.Eng Informatics, 2026</div>
          </div>
          <div style={{ paddingLeft: 30 }}>
            <div style={{ fontSize: 13, fontFamily: "monospace", color: "#8C8C8C" }}>
              Freelance
            </div>
            <div style={{ fontSize: 18 }}>One project at a time</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const BatikHeroScene: React.FC<BatikHeroProps> = ({
  mode,
  bgColor,
  inkColor,
  stippleDensity,
  maxIntensity,
  showHeroOverlay,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: bgColor }}>
      <BatikCanvasLayer
        mode={mode}
        bgColor={bgColor}
        inkColor={inkColor}
        stippleDensity={stippleDensity}
        maxIntensity={maxIntensity}
      />
      {showHeroOverlay ? <HeroTypographyOverlay mode={mode} /> : null}
    </AbsoluteFill>
  );
};
