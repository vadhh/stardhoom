---
title: "Hero redesign: name, offer and CTAs in one viewport, DHOOM mark removed"
author: St4rdhoom
date: 2026-11-02
branch: master
cost: { minutes: 9, tokens: 164672 }
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
- Hero is for clients and recruiters equally: one-line name across all 4 columns, LEAD as the offer, two CTAs (Start a project mailto, See selected work #work), and the META facts row plus a résumé link at the bottom. All of it fits in 1440x900, 1024x768 and 390x844.
- The DHOOM ASCII mark and its afriDHO / MF DOOM captions were removed from the page by the owner's choice. ASCII_LOGO stays in content.py because build_portfolio.py and build_mobile.py still use it. --pop now only appears in the background glint.

## Tried and ruled out
- `<br class="narrow">` hidden on desktop to force a 2-line name on mobile: SplitText (lines,chars) turns the br into a real break during the intro, so the name jumps to 2 lines mid-animation. Mobile wraps on its own at `(100vw - 40px) / 3.85`, so there's no br.

## Watch out
- Screenshots with --force-prefers-reduced-motion never run the intro. Also capture without it at --virtual-time-budget=1300 to catch mid-animation layout bugs.
