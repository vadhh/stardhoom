---
title: "The page closes on a traced reel's halftone flower drawn as glass tiles on the dark ground"
author: Vadhh
date: 2026-11-12
branch: master
cost: { minutes: 26, tokens: 287634 }
id: l-ed69a8df
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
---

## Decided
- The closing screen (past the footer) is a flower from a third-party reel's halftone (white squares, square size = brightness), traced cell by cell and drawn live in WebGL as frosted glass tiles, tinted cyan/blue/green after a glass-tile screenshot the user gave. It replaced the batik video.
- Dark ground (the page's #141414), chosen by the user over the screenshot's white ground, so the page doesn't flash white at its end.
- The reel's own flower is traced, chosen by the user over a flower drawn in code. The reel is someone else's work: the traced sheet and poster need the author's permission or a credit before they ship.
- Every frame is stored (64 x 36 cells x 79 frames), because the reel is not a plain zoom. Fitting each frame to the first as scale plus shift lost correlation fast (NCC 0.63 by the end), the best rotation sat at the search limit (-6 deg), and the zoom centre ran off-frame: the camera turns and drifts too.
- The reel moves one way in 5 s, so the page plays the frames forth and back on a 14 s cosine ease; looping it straight would jump.
- One tile size, with the reel's square size shown as opacity, because that reads as the screenshot's glass. A constant switches to the reel's sizes.

## Tried and ruled out
- One still of the flower plus a code zoom: ruled out by the motion fit above.
- Neon-bright tile rims: they read as outlines, not frosted glass, so they were dimmed to a thin rim lit top left plus a soft inner glow.
- Counting every square whose box is filled as lit: the 1-6 px ground squares fill their box too and showed up as stray lit tiles at the screen edges. Only 7 px and up counts as lit.

## Watch out
- The tile look is the first version the user has seen; the reel-sizes option has only been drawn in a prototype, not the real page.
- Headless Chromium here has no GPU (SwiftShader): its frame times say nothing, and a full-page screenshot stretches the 100svh screen (scroll with End and shoot the viewport instead).
- The poster is the shader's own first frame, shot from the page under reduced motion with the top mask off; re-shoot it whenever the shader changes.

In the code: design-ref/build_html.py endFlower(), FLOWER_FS (REEL_SIZES), END_FLOWER; design-ref/trace_flower.py (uv run design-ref/trace_flower.py <reel.mp4>) writes img/footer-flower.png (frames 8 to a row, 64x36 each, R = side*16, G = filled); poster img/footer-flower.jpg at 1920x1080. stage.py ships the sheet through the canvas' data-src. Reel grid: pitch 19.94 x 20 px from (0, 0), 1276x720, 15 fps, lit squares 8-16 px, hollow 1-7 px.
