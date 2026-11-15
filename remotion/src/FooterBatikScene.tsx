import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  cancelRender,
  continueRender,
  delayRender,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FooterDot, drawFooterFrame, prepareCloth } from "./footerDots";

export type FooterBatikProps = {
  readonly intensity: number;
};

// dots.json is ~58 MB (a million dots), so it is fetched once per tab rather than bundled like the hero's.
let loading: Promise<readonly FooterDot[]> | null = null;
const loadDots = (): Promise<readonly FooterDot[]> => {
  loading ??= fetch(staticFile("footer/dots.json")).then((res) => {
    if (!res.ok) throw new Error(`footer/dots.json: HTTP ${res.status}`);
    return res.json() as Promise<readonly FooterDot[]>;
  });
  return loading;
};

export const FooterBatikScene: React.FC<FooterBatikProps> = ({ intensity }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [handle] = useState(() => delayRender("Loading footer/dots.json"));
  const ready = useRef(false);
  const [dots, setDots] = useState<readonly FooterDot[] | null>(null);

  useEffect(() => {
    loadDots().then(setDots).catch((err) => cancelRender(err));
  }, []);

  const cloth = useMemo(
    () => (dots ? prepareCloth(dots, width, height) : null),
    [dots, width, height],
  );

  useLayoutEffect(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx || !cloth) return;
    drawFooterFrame(ctx, cloth, frame / durationInFrames, intensity);
    if (!ready.current) {
      ready.current = true;
      continueRender(handle);
    }
  }, [cloth, frame, durationInFrames, intensity, handle]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ display: "block", width: "100%", height: "100%" }}
    />
  );
};
