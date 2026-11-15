---
title: Fine-grid lit rendering for the batik Kediri background
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 11, tokens: 173070 }
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
The user called the 12px, flat-0.2-alpha Kediri field "bad" and asked for "more details, smaller dots, highlight, shadows". The composition (Kelud, 96px gringsing, lidah api crowns, sparks, motion) stayed; only the rendering changed. The field block (between `// FIELD START` / `// FIELD END` in design-ref/build_html.py) now also defines GRID (6px), TONES (10 levels of [radius, alpha], 0.5px@0.10 up to 3px@0.93), GLINT and HERO (hero canvas opacity, 0.8). The page draws level = min(N, round(s*N)), one fill per level, squares under 1.5px radius. Of three takes judged on live page shots (wax relief r1, batik wax-and-dye layers r2, fire light r3), r2 won by 32/31/23 and was refined with r3's grafts (solid spark cores, flickering inner contour). Lit side of every klowong outline near-solid, far side thin, inner double contour, cecek isen, scales shaded under the row in front, a cecek ground that flames cast down-right shadows onto. Page fixes: the pointer swell only lifts f > 0 (shadows stay dark), opacity is set in frame() so reduced motion gets HERO, glints only while playing. All text gets a stacked `--bg` text-shadow halo (4x 3px + 2x 8px); a plain 2/5/9px blur halo was too faint round thin grey strokes.
## Tried and ruled out
Wax relief with baked Lambert height maps (r1): bright flanks but shadows only read at 2x, and it fought the name (legibility 1-2). Longer cast-shadow offsets (14/22px): no visible gain. Judging on field-only sheets: last round the sheet-judged winner was still "bad" live, so judges now score live page shots and DPR 2 crops.
## Watch out
Perf at 6px: about 4.3 ms per frame at 1440 DPR 2 and 11.6 ms at 2560 (full frame, headless Brave), vs 1.1/2.6 at 12px; 2560 has about 2 ms of headroom under a 14 ms gate. Keep one object shape in the hot loop: adding properties later made it polymorphic and cost 20 ms at 2560. Shadow can't be dark paint on #141414; it's relative (dim versus near-solid, or erased ground). Harness: scratchpad clouds/render3.mjs reads GRID/TONES from the variant.
