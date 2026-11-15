---
title: "The closing batik widens the cloth by mirroring the photo before stippling, and unfolds from the cloth on the page"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 16, tokens: 125215 }
id: l-b5db0c06
scope: repo
status: active
replaces: l-cfa39931
src: agent
touches:
  - CLAUDE.md
  - remotion/src/footerDots.ts
  - remotion/footer-check.mjs
  - design-ref/build_html.py
  - DESIGN.md
---

## Decided
- The style is measured from a stippled reference and checked by measuring the render the same way; the reference's gaps are tinted, so pale dots sit under the marks. On the dark site it is the cream result mirrored (the cloth's light parts densest).
- The frame is zoomed out: the cloth at 0.6 of a 16:9 frame, foot on the foot, the photo mirrored through crown 1's and crown 4's axes and over its top edge. Each axis sits on the nearest stripe centre, so stripes continue.
- On the page it is its own screen after the footer (no text on it), a video. It starts clipped to the cloth and unfolds once, sideways then upward; the one-third snap stop is a third down the cloth, not the screen.

## Tried and ruled out
- Mirroring the dots: the grain repeats and the axis shows as a beaded line. Mirror the photo, then stipple.
- Crown 5 as the right axis: the photo's stripes bow near its edge and the mirror made an eye.
- Importing the 58 MB dots.json into Remotion: tsc would type it; it is fetched with staticFile and delayRender.

## Watch out
- CLOTH_BOX in the page JS must match stipple.py's framing (cloth edges in video px). dots.json and the reference image are never pushed.

In the code: `uv run remotion/footer/stipple.py --dark --frame` -> remotion/public/footer/dots.json; remotion/src/footerDots.ts (FooterBatikLoop); footer-check.mjs; `npx remotion render FooterBatikLoop ../img/footer-batik.mp4` and the poster still; .batik-end, endBatik() and CLOTH_BOX in design-ref/build_html.py.
