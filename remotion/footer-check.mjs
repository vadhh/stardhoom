// node footer-check.mjs: the footer batik renderer draws every dot of public/footer/dots.json, only in greys between
// #141414 and #F2F2F2, the ripple moves the dots, and it loops: frame 299 -> 0 changes no more than any step does.
import assert from "node:assert/strict";
import fs from "node:fs";
import { drawFooterFrame, prepareCloth } from "./src/footerDots.ts";

const dots = JSON.parse(fs.readFileSync(new URL("./public/footer/dots.json", import.meta.url), "utf8"));
const cloth = prepareCloth(dots, 1920, 1080);
const inFrame = cloth.wash.x.length + cloth.marks.x.length;
assert.equal(inFrame, dots.length, "dots.json is the frame: every dot is placed");

// a stand-in canvas: counts shapes per grey, in draw order
const record = (phase) => {
  const out = { shapes: 0, greys: new Map(), fills: [] };
  let n = 0;
  const ctx = {
    fillStyle: "",
    fillRect() {},
    beginPath() { n = 0; },
    rect(x, y, w, h) { assert(Number.isFinite(x + y + w + h) && w > 0); n++; },
    moveTo() {},
    arc(x, y, r) { assert(Number.isFinite(x + y) && r > 0); n++; },
    fill() { out.shapes += n; out.fills.push([this.fillStyle, n]); out.greys.set(this.fillStyle, (out.greys.get(this.fillStyle) ?? 0) + n); },
  };
  drawFooterFrame(ctx, cloth, phase, 0.78);
  return out;
};

const f0 = record(0);
for (const g of f0.greys.keys()) {
  const m = /^rgb\((\d+),(\d+),(\d+)\)$/.exec(g);
  assert(m && m[1] === m[2] && m[2] === m[3] && +m[1] >= 20 && +m[1] <= 242, `not a site grey: ${g}`);
}
// every dot is drawn unless its level rounds to the ground
assert(f0.shapes > 0.9 * inFrame && f0.shapes <= inFrame, `drew ${f0.shapes} of ${inFrame}`);

const diff = (a, b) => {
  const keys = new Set([...a.greys.keys(), ...b.greys.keys()]);
  let d = 0;
  for (const k of keys) d += Math.abs((a.greys.get(k) ?? 0) - (b.greys.get(k) ?? 0));
  return d;
};
const frames = [0, 1, 150, 299].map((f) => record(f / 300));
const step = diff(frames[0], frames[1]);
const wrap = diff(frames[3], frames[0]);
assert(diff(frames[0], frames[2]) > 0, "the ripple must shade the dots");
assert(wrap <= 1.5 * step + 50, `loop seam: 299->0 changes ${wrap} dots' greys vs ${step} for 0->1`);
assert.deepEqual(record(1).fills, f0.fills, "phase 1 must draw exactly phase 0");
// the ripple lifts every dot, wash and marks alike, by at most LIFT1 + LIFT2 = 6px, and differently half a loop on
const lifts = (phase) => { record(phase); return [...cloth.wash.dy, ...cloth.marks.dy]; };
const d0 = lifts(0), dHalf = lifts(0.5);
const most = [...d0, ...dHalf].reduce((m, y) => Math.max(m, Math.abs(y)), 0);
assert(most > 3 && most <= 6.0001, `lift out of range: ${most}px`);
const swing = d0.reduce((m, y, i) => Math.max(m, Math.abs(y - dHalf[i])), 0);
assert(swing > 3, `the dots must move over half a loop, moved at most ${swing}px`);

console.log(`footer batik check passed (${dots.length} dots, ${cloth.wash.x.length} wash; greys ${f0.greys.size}; ` +
  `lift up to ${most.toFixed(1)}px; step 0->1 ${step}, seam 299->0 ${wrap} dots change grey)`);
