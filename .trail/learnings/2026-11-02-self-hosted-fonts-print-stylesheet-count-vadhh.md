---
title: "Self-hosted fonts, print stylesheet, count-up and link-arrow fixes"
author: Vadhh
date: 2026-11-02
branch: portfolio-redesign
cost: { minutes: 5, tokens: 34249 }
touches:
  - CLAUDE.md
  - DESIGN.md
  - design-ref/build_html.py
  - index.html
  - ".DS_Store"
  - design-ref/__pycache__/build_html.cpython-315.pyc
  - design-ref/__pycache__/content.cpython-315.pyc
  - design-ref/__pycache__/fc.cpython-315.pyc
  - dooms_mask.jpeg
  - fonts/OFL.txt
---

## Decided
- Fonts are self-hosted in fonts/: Inter is one variable latin woff2 (weights 400–600) and Fira Code is a 400 latin woff2. Both are preloaded with font-display: swap. A size-matched local Arial "Inter Fallback" sits in --sans. build_html.py's FONTS/LATIN constants drive the @font-face rules, and the build asserts the files exist and that no fonts.googleapis link comes back. fonts/ must be uploaded to Neocities.
- The ↳ count-ups zero their text only in the tween's onStart; the DOM keeps the real text until the trigger fires. Before this, cards could show "almost 0x faster" / "Built in 0 days".
- @media print switches to black on white, forces GSAP-hidden .card/.job/.cover/hero parts visible with !important, and hides the canvas and skip link. Covers keep a dark panel because the logos are light.
- Literal ↗ characters in links are aria-hidden spans, _blank links get an .sr-only " (opens in new tab)", and .cta::after uses content: "↗" / "". The contact rule became `.links a > span` so the new spans don't pick up its padding.

## Tried and ruled out
- latin-ext subset: not needed. ↗ and ↳ are in neither font (not in Google's either), so they always come from the system face.

## Watch out
- In zsh, a bare `======` line in a Bash call is parsed as =cmd expansion and aborts the command. Use `echo ---`.
- about.html and snake.html still load Fira Code from Google Fonts.
