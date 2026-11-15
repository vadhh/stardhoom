---
title: "Section snap is one swipe, one stop, from a hook on Lenis' wheel input, not Lenis' snap module"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 21, tokens: 216305 }
id: l-dbaa6c9f
scope: repo
status: active
src: agent
touches:
  - DESIGN.md
  - design-ref/build_html.py
  - CLAUDE.md
---

## Decided
- The user asked for a snappier snap that "only pulls once" and chose "one swipe = one stop": each swipe glides at once to the next stop in its direction and never pulls back. The batik keeps both rests (top third, then the whole cloth) in both directions.
- A stop counts only when it is at most a screen from where the swipe began, so a glide never skips content that hasn't been on screen; inside Work and Experience (taller than a screen) the page scrolls freely until the next section's top is in view.
- The rest of the swipe, momentum included, is swallowed until the wheel rests 150ms. Without that, one long trackpad flick took two stops.

## Tried and ruled out
- Lenis' snap module, proximity (what shipped before): it waits for the wheel to rest (500ms debounce, after the whole momentum tail) and then picks the nearest stop, so a 300px swipe from the hero or from the batik's foot was pulled straight back, every time. About 1.3s from letting go to settled.
- Its lock mode: it aims at the next stop past where the swipe *ends*, and its 50% threshold is global, so a long swipe skips the batik's one-third rest, and a short one from the hero rests a third of the way down the hero.
- Shortening the module's debounce: it picks from the lerped position (lenis.scroll), which still lags the swipe, so a short debounce pulls back more often.

## Watch out
- Lenis' virtualScroll hook returning false skips Lenis' own preventDefault: call event.preventDefault() yourself, or the browser scrolls natively under the glide.
- Check "already gliding" before any pass-through filter: the momentum tail is mostly deltas under 4px, and letting those through overshot every stop by ~40px.
- Snap positions are a headless check (scratchpad snaptrace2.mjs pattern: synthetic swipes with an exponential momentum tail plus mouse notches); frame timing still needs a headed window.

In the code: design-ref/build_html.py, the `snap` function passed as `virtualScroll` to `new Lenis(...)`; `stops()` lists section tops and the `.batik-end .third` / `.batik-end` feet. js/lenis-snap.min.js was dropped from JS and deleted. DESIGN.md "Snap per section".
