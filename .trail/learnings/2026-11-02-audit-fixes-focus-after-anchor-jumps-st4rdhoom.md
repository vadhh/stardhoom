---
title: "Audit fixes: focus after anchor jumps, canvas throttle, WebP covers"
author: St4rdhoom
date: 2026-11-02
branch: master
cost: { minutes: 6, tokens: 24413 }
touches:
  - CLAUDE.md
  - index.html
  - ".DS_Store"
  - AGENTS.md
  - DESIGN.md
  - content/experience.csv
  - content/projects.csv
  - design-ref/__pycache__/build_html.cpython-315.pyc
  - design-ref/__pycache__/content.cpython-315.pyc
  - design-ref/__pycache__/fc.cpython-315.pyc
---

## Decided
- Lenis `anchors: true` is off. A custom click handler in design-ref/build_html.py calls lenis.scrollTo, then focuses the target with preventScroll and pushStates the hash. The targets (#top, main#main, the 4 sections) have tabindex="-1". A skip link to #main comes first in <body>.
- The background canvas draws at about 30fps and skips frames while the tab is hidden. It does NOT pause on idle, because the time-based drift is the effect.
- Project covers are lossless WebP. The PNGs are mostly transparent, so JPEG would lose the alpha. projects.csv points at the .webp files; the old PNGs are still on disk but unreferenced.
- The hero facts row: "Based in" spans cols 1–2, and the other two facts sit under the CTAs in cols 3 and 4.

## Tried and ruled out
- Measuring the h1 line count with a Range width or getClientRects: it reported 1 line at 768px, but the name really wraps to 2 there. Check the h1 height against its line-height instead.

## Watch out
- The ASTA and VaultSearch logo covers are deliberate. Don't swap them for the unused asta.jpg or vaultsearch.jpg screenshots.
- Upload to Neocities: index.html, js/, img/ and snake.html, not just index.html.
