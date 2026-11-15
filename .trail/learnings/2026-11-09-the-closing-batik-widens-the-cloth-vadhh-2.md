---
title: "The closing batik widens the cloth by mirroring the photo before stippling, and loops as a rippling cloth"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 6, tokens: 44456 }
id: l-81a4d826
scope: repo
status: active
replaces: l-b5db0c06
src: agent
touches:
  - remotion/src/footerDots.ts
  - remotion/footer-check.mjs
  - design-ref/build_html.py
---

## Decided
- The style is measured from a stippled reference and checked by measuring the render the same way; the reference's gaps are tinted, so pale dots sit under the marks. On the dark site it is the cream result mirrored (the cloth's light parts densest).
- Zoomed out: the cloth at 0.6 of a 16:9 frame, foot on the foot, the photo mirrored through crown 1's and crown 4's axes (each moved onto the nearest stripe centre) and over its top edge.
- The loop is a cloth ripple: two travelling waves lift every dot (tint included, so it never parts from the marks) and shade each slope. The user rejected a one-off unfold on the page: "expand" meant the framing, the animation is the loop.

## Tried and ruled out
- Mirroring the dots: the grain repeats and the axis shows as a beaded line. Crown 5 as an axis: the photo's stripes bow near its edge and the mirror made an eye.
- A light sweep alone: too subtle to read as animation. Importing the 58 MB dots.json into Remotion: tsc would type it (fetch it with staticFile).

In the code: `uv run remotion/footer/stipple.py --dark --frame`; remotion/src/footerDots.ts (FooterBatikLoop); footer-check.mjs; render to img/footer-batik.mp4 + .jpg; .batik-end and endBatik() in design-ref/build_html.py.
