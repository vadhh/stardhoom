---
title: Real batik Kediri cloth hanging in a slow wind replaces drawn motifs
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 12, tokens: 296386 }
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
The user rejected hand-drawn Kediri motifs: "pick one batik fabric from the internet with the motifs and pattern, the animation should look like a hanging fabric when got hit by a slow wind". Wikimedia Commons has no Kediri lidah api cloth (only Lasem/other gringsing and a faded KITLV Kediri dodot). Chose img21 from Ningrum et al., "Dahanapura as a source of regency work clothing ideas, Kediri" (ISI Surakarta Runtas 5660, CC BY-SA 4.0): the Dahanapura cloth with gringsing, lidah api crowns, sparks, Kelud and a flame border, 306x440. Shipped as img/batik-dahanapura.jpg (a <link rel=preload> makes stage.py copy it, since it only follows src/href), credited in the footer with source and licence links. The field block defines CLOTH and FIELD_READY; waves() calls FIELD_READY.then(frame) so reduced motion redraws once the texture loads. Motion: of three wind models (analytic sway+folds+gust w1, coarse Verlet cloth w2, curtain pleats w3), Verlet won 30/28/23.5 on frame strips: 40x40 nodes in cloth-width units pinned along the top row, one tall sheet covering the page, gust every ~12.5s, stepped at 30 Hz with extrapolation, print sampled in cloth UV (no z in u, so it rides instead of swimming), Lambert fold shading + gated sheen.
## Tried and ruled out
Sampling the texture at x + z (cloth0): the print swims. Three equal sine folds at different speeds: a shimmering wobble, not cloth. A luminance floor of 0.1: every cell draws a dot (coverage 1.0, 7/20 ms per frame). Real gravity in a 40-row Verlet chain with 3 iterations: it creeps and slides the print down; a weak spring to the rest pose stands in (marked ponytail:). A 3x3 max mip for phones: floods the slopes solid. Pleats (w3) foreshortened the print into mush.
## Watch out
The source is 306x440: on phones (cloth 760px wide) a cell spans ~3.5 texels and the gringsing aliases into scattered dots. A higher-res photo of a Kediri cloth would drop straight into the same pipeline. Perf has thin margin mid-gust (~6.8 ms at 1440 DPR 2, ~13 ms at 2560 against 7/14). Sim state depends on query history (a jump of >1s rebuilds from 1s before). Judge cloth motion from 8-frame strips (render4.mjs in the scratchpad), not single frames.
