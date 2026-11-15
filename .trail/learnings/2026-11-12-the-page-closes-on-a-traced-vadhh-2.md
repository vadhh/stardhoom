---
title: "The page closes on a traced reel's halftone flower drawn as glass tiles on the dark ground"
author: Vadhh
date: 2026-11-12
branch: master
cost: { minutes: 6, tokens: 54196 }
id: l-8b93e83a
scope: repo
status: active
replaces: l-ed69a8df
src: agent
touches:
  - design-ref/build_html.py
---

## Decided
- The closing screen is a third-party reel's halftone flower (square size = brightness), traced cell by cell and drawn live in WebGL as frosted glass tiles after a glass-tile screenshot. The user chose the dark page ground over the screenshot's white, and the reel's own flower over one drawn in code; it needs the reel author's permission or credit before it ships.
- Brightness and colour both follow the reel's tone (its square's area): deep blue where it is dim, cyan, ice white where it is brightest, with the screenshot's blue/green backdrop mixed in a third of the way. That is what makes it read as a flower: a glowing centre, petals dimming to their tips, dark seams between them.
- Every frame is stored and played forth and back on a 14 s ease: the reel is not a plain zoom (a scale-and-shift fit fell to NCC 0.63, the rotation pinned at the -6 deg search limit) and it moves one way in 5 s.

## Tried and ruled out
- Colour by screen position (blue left, green right) with tone only as a 0.35-1 opacity: it painted across the petals and the flower read as a flat silhouette, like a map. Per-cell luminance against the reel's correlated 0.76 over the flower; tone-driven, 0.97.
- One still plus a code zoom (the motion fit above), and neon tile rims (they read as outlines, not frosted glass).

## Watch out
- Squares under 7 px fill their box, so only 7 px and up count as lit; otherwise stray lit tiles appear at the edges.
- The headless browser here has no GPU, so its frame times mean nothing. A full-page screenshot also stretches the 100svh screen.
- The poster is the shader's first frame, shot from the page under reduced motion; re-shoot it whenever the shader changes.

In the code: design-ref/build_html.py FLOWER_FS (tone(), REEL_SIZES), endFlower(), END_FLOWER; design-ref/trace_flower.py writes img/footer-flower.png; poster img/footer-flower.jpg at 1920x1080. QA: render FLOWER_FS at the reel's 1276x720 and frames 0/39/78, then correlate 64x36 cell means against the reel's frames.
