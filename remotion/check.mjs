import assert from "node:assert/strict";
import fs from "node:fs";
import { renderBatikDotsFrame } from "./src/batikDots.ts";

const dots = JSON.parse(fs.readFileSync(new URL("./dots.json", import.meta.url), "utf8"));
assert(Array.isArray(dots) && dots.length === 19372, `expected 19372 extracted dots, got ${dots.length}`);

const recordFrame = (entranceT, loopPhase) => {
  let arcs = 0;
  let rSum = 0;
  const fillColors = new Set();

  const stubCtx = {
    fillStyle: "",
    globalAlpha: 1,
    fillRect() {},
    beginPath() {},
    moveTo(x, y) {
      assert(Number.isFinite(x) && Number.isFinite(y));
    },
    arc(x, y, r) {
      assert(Number.isFinite(x) && Number.isFinite(y) && r > 0);
      arcs++;
      rSum += r;
    },
    fill() {
      fillColors.add(this.fillStyle);
    },
  };

  renderBatikDotsFrame(stubCtx, dots, {
    width: 1920,
    height: 1080,
    entranceT,
    loopPhase,
    dotScale: 1,
    maxIntensity: 0.82,
    bgColor: "#141414",
    inkColor: "#F2F2F2",
  });

  return { arcs, rSum: Math.round(rSum * 1000), fillColors: [...fillColors] };
};

const f0 = recordFrame(0, 0);
assert.equal(f0.arcs, 0, "entrance frame 0 should open on clean dark ground");

const fSettled0 = recordFrame(1, 0);
assert(fSettled0.arcs > 20000, `expected >20k viewport dots, got ${fSettled0.arcs}`);
assert.deepEqual(fSettled0.fillColors, ["#F2F2F2"], "output must remain strictly monochrome");

const fMid = recordFrame(1, Math.PI);
assert.notEqual(fMid.rSum, fSettled0.rSum, "mid-cycle ripple must modulate dot radii");

const fSettled2Pi = recordFrame(1, Math.PI * 2);
assert.equal(fSettled0.arcs, fSettled2Pi.arcs, "loopPhase 0 and 2*PI dot count must match");
assert.equal(fSettled0.rSum, fSettled2Pi.rSum, "loopPhase 0 and 2*PI dot radii must match");

console.log(
  `gringsing-lidah-api-padma check passed (${dots.length} source dots -> ${fSettled0.arcs} canvas dots, monochrome, seamless 10s loop)`,
);
