---
title: "Parallax and section moods on index.html: fixes from the verify pass"
author: Vadhh
date: 2026-11-03
branch: master
cost: { minutes: 27, tokens: 356263 }
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
- The user asked for parallax and a section-reactive background even though the animation review had dropped both. Built as: the halftone field scrolls at 0.3x under a FIXED dot grid (moving the grid strobes/aliases); the h1 lifts up to 25% of hero height, desktop only; MOODS table (amp/speed/glint) eased with an integrated clock.
- The desktop-only lift uses ONE no-preference mm.add with `y: () => innerWidth < 1024 ? 0 : ...`, not a `(min-width: 1024px)` query.
- Section moods use one page-long ScrollTrigger (start 0, end "max") whose probe line slides 25%→75% of the screen with progress; pick() is also called once at creation.
- GitHub card prefers ABOVE the name (`flip = r.top - 10 - h > 0`); below it covers "See selected work" on screens ≥ ~1105px tall. A wheel closes it (not scroll: focusing the link fires scroll).
- Contact h2 rise starts at yPercent 125, not the h1's 110: its .ln-mask has .2em bottom padding and 110% leaves i tittles visible.
- The email underline trigger is `start: "clamp(top 85%)"`, plus one `ScrollTrigger.refresh()` before removing .js.

## Tried and ruled out
- A width-gated matchMedia context: it is created during ScrollTrigger's resize refresh, the scroll restore is skipped, and the page jumps to the top when the window widens past 1024px.
- clamp() on the shared `once` object: it leaves all work cards hidden at load on tall screens.
- clamp() on per-section mood start/end: it collapses Contact to a 1px range and drops the hero at scroll 0.
- Fixed "top 50%"/"bottom 50%" mood toggles: Contact never activates on screens ≥ ~1600 tall, and the hero is skipped above 2160px.

## Watch out
- In ScrollTrigger 3.15, the max side of clamp() resolves only in a global refresh. If document.fonts.ready resolves after window load, no global refresh happens, hence the explicit refresh().
- Exponential easing never reaches 0: About's glint needs the `cur.glint > 0.1` gate, or glints linger ~3s.
- The reduced-motion arrow rule must name `.gh-head::after` too, but never every ::after (.email::after needs its transform).
- Headless test recipe: playwright-core + Brave executablePath, page.route rewriting index.html to log `bg.mood` calls.
