---
title: Per-element animations on the batik Kediri cloth background
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 25, tokens: 186169 }
touches:
  - DESIGN.md
  - design-ref/build_html.py
  - index.html
  - dooms_mask.jpeg
  - img/batik-dahanapura.jpg
  - img/projects/asta-logo.png
  - img/projects/atask.png
  - img/projects/custseg.png
  - img/projects/minifw.png
  - img/projects/nids.png
---

## Decided
- The cloth lies flat; each label of the print gets its own `FX[label](u, v, t, k, rep)` in the FIELD block of design-ref/build_html.py (base labeller + fire for labels 1 and 4, scales 2, fungus 3, bloom 5). Each FX is a pure function of t, with prefixed globals so the files concatenate safely.
- t = STILL (40) is a settled print for every element (scales and bloom match the print exactly, fire is within about 15%). waves() starts at t = STILL and play() resets t = 0, so reduced motion (which never calls play or stop) draws the settled frame, not an empty pre-entrance one.
- Tones are capped at 0.92, so the --pop glint never fires; the code is left in place.
- Combined cost is about the same as the old Verlet cloth: 6.6 ms/frame at 1440@2 and 12.6 ms at 2560@1 (1x CPU). It is cheaper than the cloth at 4x and 6x CPU throttling.

## Tried and ruled out
- Starting t at 0 for everyone: reduced-motion users saw no crowns, sparks or ornaments, because those entrances start from empty.
- The first band burn: 14-19% of cells changed per frame, which brought back the "too distracting" complaint. It was cut to 0.3-4.5%.
- The first crown burn barely moved (horizontal kymograph). It needed upward advection of the tips, not more sway.

## Watch out
- render5's perf numbers sample sy 0-90 and t 0-1, so they never see Kelud, the band or the ornaments, or the steady state. Time each element with it on screen (the builders' fz-perf, bperf and crit/perf scripts in the scratchpad).
- 2560@1 in the band and ornament view sits at about 14 ms/frame; the margin is in the band and the bloom.
- The fungus builds its maps in requestIdleCallback after FIELD_READY (about 13 ms here).
