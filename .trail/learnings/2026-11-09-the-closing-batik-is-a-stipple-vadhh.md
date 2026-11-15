---
title: "The closing batik is a stipple copied from a reference by measured curves, mirrored for the dark site and shipped as a video"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 37, tokens: 271203 }
id: l-cfa39931
scope: repo
status: active
replaces: l-d0f2a5af
src: agent
touches:
  - remotion/src/footerDots.ts
  - remotion/src/FooterBatikScene.tsx
  - remotion/footer-check.mjs
  - design-ref/build_html.py
  - design-ref/stage.py
  - remotion/src/Root.tsx
  - DESIGN.md
  - CLAUDE.md
---

## Decided
- The style comes from a stippled reference image, by numbers measured from it (coverage per tone, grain, clumps, gap tint, chroma) and checked by measuring the render the same way. The reference's gaps are tinted, so a layer of large pale dots sits under the marks.
- The site's monochrome (light on #141414, like the hero) is the cream result mirrored: the batik's light parts get the densest marks.
- It closes the page as its own screen after the footer, with no text on it, so the muted footer grey keeps its contrast and the dots run at the hero's 0.78. Wheel snap rests twice by the screen's bottom edge: a marker a third down, then its foot.
- A video, not live like the hero: it answers nothing, and live would mean a million dots in the browser.

## Tried and ruled out
- Marks on bare cream came out lighter than the reference at every tone; random dot placement had no grain; the raw power spectrum's peak always lands on its lowest frequency (weight by frequency); the batik's full chroma was too saturated.
- Importing the 58 MB dots.json into Remotion like the hero's: tsc would type it. It is fetched with staticFile and delayRender.

## Watch out
- The dots are tied to the cloth drawn 1920 px wide; a different crop needs them regenerated. dots.json (58 MB) and the reference image (someone else's artwork) must never be pushed.
- stage.py only ships src, href and poster references.

In the code: remotion/footer/stipple.py --dark writes remotion/public/footer/dots.json; remotion/src/footerDots.ts + FooterBatikScene.tsx (FooterBatikLoop); footer-check.mjs; render with `npx remotion render FooterBatikLoop ../img/footer-batik.mp4` and the poster with `npx remotion still FooterBatikLoop ../img/footer-batik.jpg --frame=0`; .batik-end and endBatik() in design-ref/build_html.py.
