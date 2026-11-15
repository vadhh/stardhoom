---
title: "Hero stutter came from the haloed text being redrawn every frame, not from the batik, and only shows in a headed browser"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 57, tokens: 190244 }
id: l-8137a8d4
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
  - DESIGN.md
---

## Decided
The hero text that moves (the name's letters, its parallax, the lead, CTAs and facts) carries a six-shadow halo (two 8px blurs) and gets `will-change: transform`, so the compositor moves a layer drawn once. Without it the GPU re-rasterised the blurred shadows every frame: ~85% GPU, a third of frames dropped on reload and on scrolling out of the hero, freezes up to ~0.7 s. With it: 0-2 long frames.

## Tried and ruled out
- Headless Brave: a steady 60 fps in every scenario. The stalls are SwapBuffers in the GPU process, which headless never presents, so only a headed window on the real display reproduces them.
- The WebGL batik, its CSS mask, its canvas resolution, the column-rule intro: none changed the dropped frames (the batik is ~7 of ~35 long frames).

## Watch out
Any new moving text with a big text-shadow (or filter) needs its own layer. Measure GPU in a headed window (ioreg "Device Utilization %", PipelineReporter drops, long rAF gaps), with a warm window reloaded per variant: a fresh window's launch saturates the GPU by itself.

In the code: design-ref/build_html.py, the @media (prefers-reduced-motion: no-preference) rule after `.hero { text-shadow }`.
