export type BatikDot = {
  readonly x: number;
  readonly y: number;
  readonly r: number;
  readonly color: string;
};

export type RenderBatikFrameOptions = {
  readonly width: number;
  readonly height: number;
  readonly entranceT: number;
  readonly loopPhase: number;
  readonly dotScale: number;
  readonly maxIntensity: number;
  readonly bgColor: string;
  readonly inkColor: string;
};

type ProjectedDot = {
  readonly px: number;
  readonly py: number;
  readonly baseR: number;
  readonly baseAlpha: number;
  readonly dist: number;
  readonly sheen: number;
  readonly isHighlight: boolean;
  readonly isDarkFill: boolean;
  readonly revealAt: number;
};

const SRC_W = 1872;
const SRC_H = 1720;
// Horizontal center axis of upper Padma crown & star Gringsing in normalized image x.
const MOTIF_CENTER_X = 0.483;
// Edge mirror planes align through the left/right corner Lidah Api centers so
// wide 16:9 viewports extend from loaded dots with zero seam discontinuity.
const MIRROR_LEFT_X = 0.008;
const MIRROR_RIGHT_X = 0.992;
const ZOOM = 1.14;
const Y_SHIFT_RATIO = -105 / 1080;
const ALPHA_BUCKETS = 16;

const cachedKey = {
  source: null as readonly BatikDot[] | null,
  width: 0,
  height: 0,
  projected: [] as ProjectedDot[],
};

const clamp01 = (v: number): number => (v < 0 ? 0 : v > 1 ? 1 : v);

/** Convert extracted photo hex pigment to a calibrated monochrome luminance weight [0.22..0.98]. */
const pigmentTone = (hexColor: string): { readonly tone: number; readonly lum: number } => {
  const clean = hexColor.charCodeAt(0) === 35 ? hexColor.slice(1) : hexColor;
  const r = parseInt(clean.slice(0, 2), 16) || 0;
  const g = parseInt(clean.slice(2, 4), 16) || 0;
  const b = parseInt(clean.slice(4, 6), 16) || 0;
  const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  const t = clamp01((lum - 0.2) / 0.74);
  let tone = 0.2 + 0.78 * Math.pow(t, 1.3);

  // Lift deep crimson (Lidah Api) and dark foliage fills so silhouettes read on #141414
  // while keeping crisp separation under their silver ukel outlines.
  if (lum < 0.42) {
    const lift = 0.27 + 0.08 * t;
    if (lift > tone) tone = lift;
  }

  return { tone, lum };
};

const projectDots = (
  dots: readonly BatikDot[],
  width: number,
  height: number,
): ProjectedDot[] => {
  if (
    cachedKey.source === dots &&
    cachedKey.width === width &&
    cachedKey.height === height
  ) {
    return cachedKey.projected;
  }

  const baseScale = height / SRC_H;
  const scale = baseScale * ZOOM;
  const tW = SRC_W * scale;
  const tH = SRC_H * scale;
  const maxTileDim = tW > tH ? tW : tH;
  const leftSeam = width * 0.5 - MOTIF_CENTER_X * tW;
  const yShift = height * Y_SHIFT_RATIO;

  // Focal center inside the Lidah Api heart for calm outward ripple timing.
  const cx = width * 0.5;
  const cy = height * 0.51;
  const normRx = width * 0.52;
  const normRy = height * 0.58;

  const out: ProjectedDot[] = [];
  const margin = 6;

  const pushPass = (
    dotsArr: readonly BatikDot[],
    mode: 0 | 1 | 2, // 0: center, 1: left mirror, 2: right mirror
  ) => {
    for (let i = 0; i < dotsArr.length; i++) {
      const d = dotsArr[i];
      if (mode === 1 && d.x <= MIRROR_LEFT_X + 0.004) continue;
      if (mode === 2 && d.x >= MIRROR_RIGHT_X - 0.004) continue;

      const nxSrc =
        mode === 0
          ? d.x
          : mode === 1
            ? 2 * MIRROR_LEFT_X - d.x
            : 2 * MIRROR_RIGHT_X - d.x;
      const px = leftSeam + nxSrc * tW;
      if (px < -margin || px > width + margin) continue;

      const py = d.y * tH + yShift;
      if (py < -margin || py > height + margin) continue;

      const { tone, lum } = pigmentTone(d.color);
      const ny = py / height;
      const nx = px / width;

      // Keep top nav & bottom hero typography headline completely readable.
      const topMask = 0.34 + 0.66 * clamp01(ny / 0.085);
      const textMask = 1.0 - 0.52 * clamp01((ny - 0.57) / 0.26);
      const edgeDist = Math.abs(nx - 0.5) * 2.0;
      const edgeFactor = clamp01((edgeDist - 0.55) / 0.45);
      const sideFade = 1.0 - 0.36 * Math.pow(edgeFactor, 1.5);

      const baseR = Math.max(0.85, d.r * maxTileDim * (0.82 + 0.18 * tone));
      const baseAlpha = tone * topMask * textMask * sideFade;

      const dxN = (px - cx) / normRx;
      const dyN = (py - cy) / normRy;
      const dist = Math.sqrt(dxN * dxN + dyN * dyN);
      const sheen = nx * 0.72 + ny * 0.45;
      // Bright crest highlights awaken first from central flame outward on entrance.
      const revealAt = clamp01(dist / 1.22) * 0.78 + (1 - tone) * 0.22;

      out.push({
        px,
        py,
        baseR,
        baseAlpha,
        dist,
        sheen,
        isHighlight: tone >= 0.68,
        isDarkFill: lum < 0.42,
        revealAt,
      });
    }
  };

  pushPass(dots, 0);
  pushPass(dots, 1);
  pushPass(dots, 2);

  cachedKey.source = dots;
  cachedKey.width = width;
  cachedKey.height = height;
  cachedKey.projected = out;
  return out;
};

export const renderBatikDotsFrame = (
  ctx: CanvasRenderingContext2D,
  dots: readonly BatikDot[],
  options: RenderBatikFrameOptions,
): void => {
  const {
    width,
    height,
    entranceT,
    loopPhase,
    dotScale,
    maxIntensity,
    bgColor,
    inkColor,
  } = options;

  ctx.globalAlpha = 1;
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, width, height);

  const clampedEntrance = clamp01(entranceT);
  if (clampedEntrance <= 0) {
    return;
  }

  const projected = projectDots(dots, width, height);
  const bucketsX: number[][] = [];
  const bucketsY: number[][] = [];
  const bucketsR: number[][] = [];
  for (let b = 0; b < ALPHA_BUCKETS; b++) {
    bucketsX.push([]);
    bucketsY.push([]);
    bucketsR.push([]);
  }

  const twoPi = Math.PI * 2;
  const maxAlpha = clamp01(maxIntensity);

  for (let i = 0; i < projected.length; i++) {
    const p = projected[i];
    const localEntrance =
      clampedEntrance >= 0.999
        ? 1
        : clamp01((clampedEntrance - p.revealAt * 0.8) / 0.2);
    if (localEntrance <= 0.01) continue;

    // Gentle outward radial breathing wave (one cycle per seamless loop).
    const radialWave = Math.sin(loopPhase - p.dist * Math.PI * 2.8);
    // Slow diagonal shimmer sweeping softly across the cloth.
    const sheenWave = Math.sin(loopPhase - p.sheen * twoPi + 0.85);
    // Subtle secondary harmonic on inner flame fills, keeping motion calm.
    const innerBreath = p.isDarkFill
      ? Math.sin(loopPhase + p.dist * 2.2 - (p.py / height) * 5.0) * 0.08
      : 0;

    // Damp modulation over bottom typography zone so text sits steady.
    const ny = p.py / height;
    const motionDamp = 1.0 - 0.55 * clamp01((ny - 0.56) / 0.25);

    const modScale =
      1.0 +
      motionDamp *
        ((p.isHighlight ? 0.13 : 0.09) * radialWave +
          0.05 * sheenWave +
          innerBreath);
    const modAlpha =
      1.0 +
      motionDamp * (0.13 * radialWave + 0.07 * sheenWave + innerBreath * 1.1);

    const radius = p.baseR * dotScale * modScale * (0.35 + 0.65 * localEntrance);
    if (radius <= 0.2) continue;

    const alpha = clamp01(p.baseAlpha * maxAlpha * modAlpha * localEntrance);
    if (alpha <= 0.02) continue;

    let bucket = Math.floor(alpha * (ALPHA_BUCKETS - 1) + 0.5);
    if (bucket < 0) bucket = 0;
    if (bucket >= ALPHA_BUCKETS) bucket = ALPHA_BUCKETS - 1;

    bucketsX[bucket].push(p.px);
    bucketsY[bucket].push(p.py);
    bucketsR[bucket].push(radius);
  }

  ctx.fillStyle = inkColor;
  for (let b = 0; b < ALPHA_BUCKETS; b++) {
    const xs = bucketsX[b];
    if (xs.length === 0) continue;
    const ys = bucketsY[b];
    const rs = bucketsR[b];

    ctx.globalAlpha = Math.max(0.04, b / (ALPHA_BUCKETS - 1));
    ctx.beginPath();
    for (let j = 0; j < xs.length; j++) {
      const x = xs[j];
      const y = ys[j];
      const r = rs[j];
      ctx.moveTo(x + r, y);
      ctx.arc(x, y, r, 0, twoPi);
    }
    ctx.fill();
  }

  ctx.globalAlpha = 1;
};
