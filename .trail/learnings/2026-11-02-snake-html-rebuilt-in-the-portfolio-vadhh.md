---
title: snake.html rebuilt in the portfolio theme
author: Vadhh
date: 2026-11-02
branch: master
cost: { minutes: 16, tokens: 124762 }
touches:
  - CLAUDE.md
  - DESIGN.md
  - design-ref/build_html.py
  - design-ref/content.py
  - index.html
  - snake.html
  - ".DS_Store"
  - design-ref/__pycache__/build_html.cpython-315.pyc
  - design-ref/__pycache__/content.cpython-312.pyc
  - design-ref/__pycache__/content.cpython-315.pyc
---

## Decided
- snake.html is still hand-written and self-contained (not generated). It copies index.html's tokens, self-hosted fonts and 4-column hairline grid by hand. Cols 1-2 hold the copy, stats and keys; cols 3-4 hold a square halftone board with a --text snake and --pop food. --pop is now used in three places (glint, hovered "vadh", snake food), and DESIGN.md says so.
- Cols 1-2 let the column rules through, as the hero does. Two-column rows (stats, keys) have padding-left: var(--gut) on the second cell, so they split on the 25% rule. That's why the stats are only Score and Status, and "Hardcore" moved into the label `~/snake --hardcore`.
- Controls: arrows/WASD, Space to start, pause or resume; touch has swipe, a tap on the board to pause, and a d-pad (shown on pointer: coarse OR below 1024px). Turns go into a queue of two, each checked against the one before, so two presses in one step can't reverse the snake into itself. That bug was in the old page.

## Tried and ruled out
- Ending the game on visibilitychange: too harsh. It pauses instead.
- Showing the d-pad only under (pointer: coarse): headless Chromium with isMobile/hasTouch doesn't report a coarse pointer. Width is the fallback.

## Watch out
- Space/Enter key repeats must be preventDefault-ed and ignored. pause() focuses the Resume button, so a held Space's repeats otherwise click it on keyup and unpause.
- Keep the game-over card inside small boards (320px phones, 1280x500 windows). There's an @container (max-width: 380px) tightening, plus overflow: auto and align-content: safe center.
- No JS: html:not(.js) hides #overlay and .pad. The class is set by an inline script at the top of <head>.
