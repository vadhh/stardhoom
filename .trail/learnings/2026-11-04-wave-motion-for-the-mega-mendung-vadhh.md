---
title: Wave motion for the mega mendung clouds
author: Vadhh
date: 2026-11-04
branch: master
cost: { minutes: 6, tokens: 202960 }
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
- "Animate it like wave" was done in two parts. (1) A travelling swell warps every cloud's lookup by the same orbit, so a front cloud and the clouds behind it still occlude cleanly: th = x*KX + y*0.004 - 0.7t, dx = -0.5A cos th, dy = -A sin th. A = 14k px and the wavelength is 760k (520 and 10 on phones). (2) The inner bands flow outward continuously at 5px/s (rp = (5t + phase) mod P) and vanish into a fixed wax line at d in [BAND, BAND+12), while the outline band holds still. Bounding boxes are padded by A.
- A band's tone comes from the depth of its centre, so one band steps tone at a time.
- Measured: 1.4 ms per frame at 1440 in the harness, about 0.4% of cells changing dot size per frame, and no bad values at t = 0, 3.3, 77 or 5000 at 500, 1440 or 2560.

## Tried and ruled out
- Indexing band tone by floor(q/P): when rp wraps, every band brightens one step at once, a flash every period.

## Watch out
- A swell bigger than about 1.5 cells (18px) starts bending the motif out of shape on the 12px grid.
