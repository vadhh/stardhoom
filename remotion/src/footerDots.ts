/**
 * The footer batik: public/footer/dots.json (made by footer/stipple.py --dark --frame from the photographed cloth),
 * drawn in the site's monochrome. Each dot's colour is a grey from #141414 (no light) to #F2F2F2 (full light). The
 * file holds two kinds, told apart only by size and kept in file order: the wash (r 3px at 1920 wide, first) tints the
 * gaps; the marks (r 0.56px) are the stipple. Both ride the same ripple, so the tint never parts from the pattern.
 */
export type FooterDot = {
  readonly x: number;
  readonly y: number;
  readonly r: number;
  readonly color: string;
};

// dots.json is the whole 16:9 frame (stipple.py --dark --frame): the cloth at 0.6 of its width, foot on the frame's
// foot, the photo mirrored to fill the sides and the top; x and y are 0..1 of the frame, r a share of its width
const BG = 20; // #141414
const INK = 242; // #F2F2F2
const WASH_MIN_R = 2 / 1920; // r as a share of the width: wash dots are 3px, marks 0.56px
const LEVELS = 48;
const TAU = Math.PI * 2;
// The loop: the cloth ripples as in a breeze. Two waves cross it: a long swell left to right (960px, 2 crests across
// the frame, once around the loop) and a shorter one up along the crowns' 10.5deg rise (footer/analysis.json; 540px,
// twice around). Each dot rises and falls with them (LIFT px) and each slope catches the light or turns from it
// (SHADE, the shading of a fold: cos where the lift is sin). Whole cycles per loop, so the last frame runs on into
// the first. Lengths and lifts are px at a 1920 frame.
const LEN1 = 960;
const LEN2 = 540;
const LIFT1 = 4;
const LIFT2 = 2;
const SHADE1 = 0.22;
const SHADE2 = 0.12;
const RISE = (10.5 * Math.PI) / 180;

type Layer = {
  readonly x: Float32Array;
  readonly y: Float32Array;
  readonly r: Float32Array;
  readonly level: Float32Array; // 0..1: how far the dot's grey sits above the ground
  readonly k1: Float32Array; // each wave's phase at the dot
  readonly k2: Float32Array;
  readonly dy: Float32Array; // scratch, reused every frame
  readonly shade: Float32Array;
  readonly bucket: Uint8Array;
  readonly order: Int32Array;
};

export type PreparedCloth = {
  readonly width: number;
  readonly height: number;
  readonly wash: Layer;
  readonly marks: Layer;
};

const layer = (rows: number[][]): Layer => {
  const col = (k: number) => Float32Array.from(rows, (row) => row[k]);
  const n = rows.length;
  return {
    x: col(0),
    y: col(1),
    r: col(2),
    level: col(3),
    k1: col(4),
    k2: col(5),
    dy: new Float32Array(n),
    shade: new Float32Array(n),
    bucket: new Uint8Array(n),
    order: new Int32Array(n),
  };
};

/** The dots placed in a width x height frame. */
export const prepareCloth = (
  dots: readonly FooterDot[],
  width: number,
  height: number,
): PreparedCloth => {
  const s = width / 1920;
  const wash: number[][] = [];
  const marks: number[][] = [];
  for (const d of dots) {
    const x = d.x * width;
    const y = d.y * height;
    const level = (parseInt(d.color.slice(1, 3), 16) - BG) / (INK - BG);
    const k1 = (TAU * x) / (LEN1 * s);
    const k2 = (TAU * (x * Math.cos(RISE) - y * Math.sin(RISE))) / (LEN2 * s);
    (d.r > WASH_MIN_R ? wash : marks).push([x, y, d.r * width, level, k1, k2]);
  }
  return { width, height, wash: layer(wash), marks: layer(marks) };
};

const grey = (t: number): string => {
  const v = Math.round(BG + t * (INK - BG));
  return `rgb(${v},${v},${v})`;
};

/** Each dot opaque in its grey at y + dy, LEVELS greys a frame: one path per grey, sorted by a counting sort. */
const drawLayer = (ctx: CanvasRenderingContext2D, L: Layer, intensity: number): void => {
  const n = L.x.length;
  const counts = new Int32Array(LEVELS + 1);
  for (let i = 0; i < n; i++) {
    const t = L.level[i] * intensity * L.shade[i];
    const b = Math.round((t > 1 ? 1 : t < 0 ? 0 : t) * (LEVELS - 1));
    L.bucket[i] = b;
    counts[b + 1]++;
  }
  for (let b = 0; b < LEVELS; b++) counts[b + 1] += counts[b];
  const next = counts.slice(0, LEVELS);
  for (let i = 0; i < n; i++) L.order[next[L.bucket[i]]++] = i;

  for (let b = 1; b < LEVELS; b++) {
    if (counts[b + 1] === counts[b]) continue;
    ctx.fillStyle = grey(b / (LEVELS - 1));
    ctx.beginPath();
    for (let k = counts[b]; k < counts[b + 1]; k++) {
      const i = L.order[k];
      const r = L.r[i];
      const y = L.y[i] + L.dy[i];
      // ponytail: marks under 1px radius go in as squares (a 1.1px square reads as a 1.1px disc and fills ~10x faster)
      if (r < 1) {
        ctx.rect(L.x[i] - r, y - r, 2 * r, 2 * r);
      } else {
        ctx.moveTo(L.x[i] + r, y);
        ctx.arc(L.x[i], y, r, 0, TAU);
      }
    }
    ctx.fill();
  }
};

/** One frame. `phase` 0..1 runs once around the loop; `intensity` scales every dot's light. */
export const drawFooterFrame = (
  ctx: CanvasRenderingContext2D,
  cloth: PreparedCloth,
  phase: number,
  intensity: number,
): void => {
  ctx.fillStyle = grey(0);
  ctx.fillRect(0, 0, cloth.width, cloth.height);
  const t = (phase % 1) * TAU;
  const s = cloth.width / 1920;
  for (const L of [cloth.wash, cloth.marks]) {
    for (let i = 0; i < L.x.length; i++) {
      const a = t - L.k1[i];
      const b = 2 * t - L.k2[i];
      L.dy[i] = s * (LIFT1 * Math.sin(a) + LIFT2 * Math.sin(b));
      L.shade[i] = 1 + SHADE1 * Math.cos(a) + SHADE2 * Math.cos(b);
    }
    drawLayer(ctx, L, intensity);
  }
};
