---
title: GitHub hover card on vadh in the hero name
author: Vadhh
date: 2026-11-02
branch: master
cost: { minutes: 7, tokens: 133395 }
touches:
  - CLAUDE.md
  - DESIGN.md
  - design-ref/build_html.py
  - design-ref/content.py
  - index.html
  - ".DS_Store"
  - design-ref/__pycache__/build_html.cpython-315.pyc
  - design-ref/__pycache__/content.cpython-312.pyc
  - design-ref/__pycache__/content.cpython-315.pyc
  - design-ref/__pycache__/fc.cpython-315.pyc
---

## Decided
- "vadh" in the h1 is a real link to github.com/vadhh; hovering it (only in `@media (hover: hover)`) or focusing it with the keyboard shows a GitHub profile card in the site style. On a phone, a tap just follows the link.
- The card (`gh_card()` in design-ref/build_html.py) is a sibling of the h1, not a child: SplitText's line masks would clip it, and its text would end up in the heading. CSS `:has()` shows and hides it. JS (`ghCard()`) only positions it below the link, or above when there's no room below, and refreshes the `data-k` fields from api.github.com/users/vadhh the first time it opens.
- The snapshot in content.py `GITHUB` is the fallback when there's no JS or the API rate limit (60/h per IP) is hit. Refresh it by hand now and then.

## Tried and ruled out
- Embedding the real profile in an iframe: GitHub sends X-Frame-Options: deny and frame-ancestors 'none'.
- SplitText with the default `deepSlice: true`: it slices the nested link and leaves an empty, focusable `<a class="gh">` clone before it. `deepSlice: false` fixes it.

## Watch out
- Listeners are delegated (pointerover/focusin on document) because autoSplit rebuilds the h1's innerHTML on resize, so element references go stale.
- Print hides `.gh-card` explicitly, because the print rule forces everything visible.
- Playwright MCP needs Google Chrome, which isn't installed. Drive Brave with playwright-core from the scratchpad instead.
