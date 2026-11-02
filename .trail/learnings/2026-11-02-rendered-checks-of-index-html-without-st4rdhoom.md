---
title: Rendered checks of index.html without Playwright Chrome
author: St4rdhoom
date: 2026-11-02
branch: master
cost: { minutes: 3, tokens: 97550 }
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
- The audit of index.html scored it 15/20. The open items are: move focus after Lenis anchor jumps, let the background canvas rest, make the mono links bigger tap targets, and rewrite DESIGN.md, which still describes the photography reference frame.
- Rendered checks use headless Brave (/Applications/Brave Browser.app) with --dump-dom. A tiny python server injects a measuring script into index.html, the script writes JSON to a body attribute, and the dump is grepped for it.

## Tried and ruled out
- The Playwright MCP fails because Google Chrome isn't installed, and the python playwright module isn't installed either.

## Watch out
- Headless Brave won't make a window narrower than 500px, so 360 and 390 render as 500. Mobile below 500px needs a real device or another engine.
- Cards and jobs are hidden by GSAP until ScrollTrigger fires. Wait 4s or more (--virtual-time-budget=8000) before measuring.
