---
title: "Section snap is one swipe, one stop, from a hook on Lenis' wheel input, not Lenis' snap module"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 1, tokens: 4121 }
id: l-e668dabb
scope: repo
status: active
replaces: l-dbaa6c9f
src: agent
touches:
  - design-ref/build_html.py
  - DESIGN.md
---

## Decided
- The user asked for a snappier snap that "only pulls once" and chose "one swipe = one stop": a swipe glides at once to the next stop in its direction and never pulls back. The batik keeps both rests (top third, then whole cloth) both ways.
- A stop counts only within a screen of where the swipe began, so a glide never skips unseen content; Work and Experience (taller than a screen) scroll freely until the next top is in view.
- The rest of the swipe, momentum included, is swallowed until the wheel rests 150ms.

## Tried and ruled out
- Lenis' snap module, proximity (shipped before; measured): it snaps only after the wheel and its momentum rest plus 500ms, to the nearest stop, so a 300px swipe from the hero or the batik's foot was pulled straight back every time.
- Its lock mode, from reading the source (not run): it aims past where a swipe ends with a global 50% threshold, so a long swipe would skip the batik's one-third rest.

## Watch out
- Lenis' virtualScroll hook returning false skips Lenis' preventDefault: call event.preventDefault() yourself.
- Check "already gliding" before any pass-through filter: the momentum tail is mostly deltas under 4px, and letting them through overshot every stop by ~40px (measured).
- Tuned on synthetic Playwright swipes, not real macOS momentum. Knobs: 0.6s glide, 150ms rest, 4px jitter floor, one-screen reach.

In the code: design-ref/build_html.py, `snap` passed as `virtualScroll` to `new Lenis(...)`, `stops()`; js/lenis-snap.min.js deleted. DESIGN.md "Snap per section".
