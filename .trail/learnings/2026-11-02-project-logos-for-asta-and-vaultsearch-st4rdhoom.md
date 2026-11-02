---
title: Project logos for ASTA and VaultSearch
author: St4rdhoom
date: 2026-11-02
branch: master
cost: { minutes: 2, tokens: 64303 }
touches:
  - CLAUDE.md
  - index.html
  - ".DS_Store"
  - AGENTS.md
  - DESIGN.md
  - content/experience.csv
  - content/projects.csv
  - design-ref/__pycache__/content.cpython-315.pyc
  - design-ref/__pycache__/fc.cpython-315.pyc
  - design-ref/build_html.py
---

## Decided
- Logos live as standalone SVG lockups (mark + wordmark) in img/projects/: asta-logo.svg, vaultsearch-logo.svg. Not wired into projects.csv; card covers stay 960x600 screenshots.
- ASTA: green squircle, cream/yellow sprout over a cupped-hand crescent, brown rounded wordmark (palette from the app UI).
- VaultSearch: dark squircle, magnifier whose lens is a vault wheel (hub, 3 spokes, 8 bolts), blue #2563EB -> cyan #22D3EE gradient; "Vault" is #F2F2F2, made for dark backgrounds.

## Tried and ruled out
- A plus-shaped crosshair inside the lens read as a gun sight, not a vault; swapped for 3 spokes + rim bolts.

## Watch out
- Wordmarks are live <text>, so they fall back to system fonts if Baloo 2 / Inter are missing. Outline them before using outside the browser.
- `qlmanage -t -s 1000 -o <dir> file.svg` renders SVG previews on this Mac without Chrome.
- Using a logo as a card cover needs a 16:10 image; a wide lockup has to be placed on a 16:10 canvas first.
