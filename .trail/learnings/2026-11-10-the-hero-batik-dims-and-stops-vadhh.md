---
title: "The hero batik dims and stops when the pointer is off the hero, instead of a stronger loop"
author: Vadhh
date: 2026-11-10
branch: master
cost: { minutes: 14, tokens: 454921 }
id: l-b4d5f709
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
  - DESIGN.md
---

## Decided
- The owner found the hero's breathing loop barely visible outside the cursor's glow, and chose "dim + still without the cursor" over a stronger loop. With no pointer on the hero, the light eases to 45% and the loop's clock slows with it to a stop; then nothing draws (0 draw calls a second against 180), which saves the GPU the loop costs. The pointer coming back eases both up in about a second. The 2 s entrance always plays at full light; touch and reduced motion keep the full-light still frame.

## Watch out
- After a reload there is no pointer event until the mouse moves, so the hero dims after its entrance even with the cursor resting on it. That is accepted.
- To measure the canvas's brightness, use screenshots. gl.readPixels returns zeros once the frame is composited, because there is no preserveDrawingBuffer.

In the code: design-ref/build_html.py, `lit` in waves() (eased toward aim[2] at 2.5/s once t >= 2, which also scales the clock), `DIM` and `u_lit` in DOTS_VS. DESIGN.md, the hero's Loop and Cost bullets.
