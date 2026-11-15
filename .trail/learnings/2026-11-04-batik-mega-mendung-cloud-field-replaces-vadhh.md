---
title: Batik mega mendung cloud field replaces the cumulonimbus
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 6, tokens: 182241 }
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
- The user asked for the clouds to look like batik mega mendung (Cirebon). field() in ANIM_JS (build_html.py) is now four hand-drawn cloud units: scalloped top and belly, and tails that curl into an eye. Each unit's inside distance is computed once per screen width into a 5px-per-texel sprite with a Felzenszwalb distance transform, about 28ms. That distance is stepped into nested bands: a bucket-5 outline, then bucket 4, 4, 3, 3... toward the core, with a one-cell empty "wax line" between bands (24px band, 36px period). Front clouds cut out of the ones behind with a 12px halo. Phones (<700px) get their own layout. Inner bands breathe and clusters sway. Only the crown of each top bulge can glint.
- Picked by 2 judges out of 3 approaches: authored units (m2) beat signed-distance unions of circles (m1) and the cumulonimbus layout redrawn in bands (m3). One agent then refined it (mm.js). Field cost is 0.65 ms per frame at 1440 and 2.1 at 2560, with no dot flicker.

## Tried and ruled out
- Bands of 2+ cells of solid tone: they look muddy at 0.2 alpha. One-cell lines with empty gaps read as batik contours.
- SDF circle unions: the inner rings form "targets" on each lobe, and the clouds read as generic blobs.
- Any 3D shading (the earlier cumulonimbus lobes): mega mendung is flat and graphic.

## Watch out
- build() must reset the per-t cache. Otherwise a width change at the same t (reduced motion plus a resize or phone rotation) turns every cloud into solid max-size dots.
- At 50% hero opacity the core bands (bucket 3) nearly vanish; the motif reads from the ring structure.
- The scratchpad harness swaps the block between `// FIELD START` and `// FIELD END` markers. They are not in build_html.py, so re-add them before reusing it.
