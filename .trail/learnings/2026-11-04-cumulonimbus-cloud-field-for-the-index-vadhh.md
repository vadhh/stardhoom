---
title: Cumulonimbus cloud field for the index.html background
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 29, tokens: 551721 }
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
- The background's dot size now comes from one pure `field(x, y, t, W)` in ANIM_JS (build_html.py). It returns 0..1, and values above 0.93 get the --pop glint. The grid, ink, alpha, buckets, parallax, pointer swell, sweep-in, MOODS and stop() are unchanged, so the look is swapped in one place.
- Picked from 4 approaches by 3 judges looking at screenshots: sphere-shaded lobe stacks (v4, "illustrator"), refined to v5. One hero cumulonimbus with an unbroken wedge anvil, flat top, small overshooting dome and a tower about 1.45x as tall as it is wide. Then congestus and fair-weather cumulus, a second storm around field y 2200-2900, and reps every 4600*v. The layout is rebuilt only when W changes, and lobes move once per t.
- Costs 1.6 ms of field time per frame at 1440 and 3.4 at 2560. Cells change dot size on about 0.1% of frames.

## Tried and ruled out
- Puff metaballs (v1): mushroom or hat silhouette, striped tower, and 9 ms at 2560.
- A billow-fBm threshold against an analytic envelope (v2): hammerhead dome, plank anvil, near-empty sky lower down.
- Baked sprites with lookup boil (v3): turrets never form or dissolve, the towers visibly repeat, and the anvil crowds the nav.

## Watch out
- At 0.2 alpha the eye reads only the silhouette. Judge it on screenshots, not on numbers.
- Scratchpad harness: clouds/render.mjs swapped the block between `// FIELD START` and `// FIELD END`. Those markers are gone from build_html.py now, so add them back before reusing it.
- Headless Brave renders 390 as 500 wide.
