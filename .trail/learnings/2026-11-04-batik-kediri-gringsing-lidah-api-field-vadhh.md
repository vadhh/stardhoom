---
title: "Batik Kediri gringsing + lidah api field (the user's hometown motif)"
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 8, tokens: 59803 }
touches:
  - DESIGN.md
  - design-ref/build_html.py
  - index.html
  - dooms_mask.jpeg
  - img/projects/asta-logo.png
  - img/projects/atask.png
  - img/projects/custseg.png
  - img/projects/minifw.png
  - img/projects/nids.png
  - img/projects/vaultsearch-logo.png
---

## Decided
- The user rejected mega mendung and asked for batik Kediri gringsing + lidah api (Dahanapura), from their hometown, so authenticity matters. The ground truth is the reference plates in Ningrum et al., "Dahanapura as a source of Kediri Regency work clothing ideas" (ISI Surakarta 2024, jurnal.isi-ska.ac.id Runtas/article/view/5660). The lidah api line art and the Kelud composition are images 3, 8 and 21 of its PDF; extract them by cutting the DCTDecode JPEG streams out of the PDF with stdlib Python, since poppler isn't installed.
- field() (build_html.py, ANIM_JS) treats the page as one cloth:
  - The hero is Mount Kelud: gringsing on its shoulders and crater (scales 96px wide, a dotted arc plus one bold centre dot, lower rows in front), crowned by lidah api clusters (tongues hooking outward from a spiral root, drawn as an outline plus an inner wax line from distance sprites).
  - Below the hero come borders, a crowned hill, a sloping band and a second peak; the cloth then repeats mirrored.
  - S-shaped spark tongues rise over the plain ground. The --pop glint lands only on flame tips and some sparks.
- Motion: a swell rolls through the scale rows, and waves lick up each tongue (the root holds, the tip moves most).
- Chosen from 3 approaches by 2 judges: the whole-cloth composition (k3) over flame units first (k2) and gringsing ground first (k1), then refined into kd.js. Field cost is 0.97 ms per frame at 1440 and 2.25 at 2560, with 1.5% of cells changing bucket per frame and about 37 ms of sprite build at load.

## Tried and ruled out
- Scales 60-84px wide: at a radius of 3 cells they don't read as round, and 7-cell pitches don't snap at the half offset. 96px (radius 4 cells) works.
- The k2 spark's side barb: on the grid it reads as "ξ".

## Watch out
- At the hero's 50% canvas opacity the motif is very faint; it reads properly one screen down.
- Every pattern locked to field y shimmers while scrolling (field y = scroll*0.3 is not cell-snapped) and settles when still.
- Tongues narrower than 2 cells come out solid; wide tongues with an inner line can read as vertical bars.
