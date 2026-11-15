---
title: "Hero-only background via taste-skill, with a dealt-effect branch to compare"
author: Vadhh
date: 2026-11-08
branch: master
cost: { minutes: 27, tokens: 309655 }
id: l-6bd9369e
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
---

## Decided
- taste-skill (design-taste-frontend, installed in .claude/skills/) allows one effect, in the hero only, never a fixed or page-long canvas behind body copy. The owner kept the batik and chose hero-only: the canvas is absolute at the page top, as tall as `.hero` (a ResizeObserver keeps it in step), full width, 65% opacity, masked out over its last 30%. MOODS, the 0.3x field parallax and the glint are gone. Pixel ratio is capped at 1.5, nothing draws once scrollY passes the hero, a 44px pause button (`.bg-pause`, `aria-pressed`) sits under the right corner bracket, and `pointer: coarse` gets the STILL frame.
- For comparison, branch `bg/taste-effect` lives in a worktree at ../stardhoom-taste (uncommitted, per the push-only rule). It uses the effect the skill's picker dealt (`effects.mjs pick --page software --palette dark --slots hero --quiet --seed 6127` gave painterly-landscape). fx.js and the effect are vendored in js/fx/ with the MIT notice and `modulepreload`ed, because stage.py only ships files referenced by src/href/url() and fx.js imports `<id>/effect.js` dynamically.
- The skill's gate (`gate.mjs --start`) was never armed in the repo. The page isn't built to the skill's company-site rules (copy, one section per screen), so its checker would block every stop.

## Tried and ruled out
- painterly-landscape at full strength: the grey nav links measured 2.1-2.5:1 on the dusk sky. Dimming it to 45% and fading it in from 40px to 220px brings every hero label to 4.54:1 or more at 390-2560 across the drift cycle (sampled with fx `setClock`).
- The pause button at z-index auto: `.intro`'s padding box covers it and takes the clicks. It needs `z-index: 2`.

## Watch out
- Worst-pixel contrast (text hidden, brightest ground pixel in each text box) reads 2.4:1 on the batik, because one bright dot in a box counts and the `--bg` halo is removed for the measurement. It is not comparable to the smooth ground's number.
- At 1440 the hero-only batik shows only the crowns, sparks and the top of the scales. The fungus, band and bloom from the per-element work sit below the first screen.
- In zsh, `for w in "1440 900"` passes one argument (no word splitting); use `for w h in 1440 900 ...`.
