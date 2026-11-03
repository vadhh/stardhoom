---
title: "Animation review of index.html: what to add, what was ruled out"
author: Vadhh
date: 2026-11-03
branch: master
cost: { minutes: 11, tokens: 144245 }
touches:
  - dooms_mask.jpeg
  - img/projects/asta-logo.png
  - img/projects/atask.png
  - img/projects/custseg.png
  - img/projects/minifw.png
  - img/projects/nids.png
  - img/projects/vaultsearch-logo.png
  - opencode.json
  - snake.html
---

## Decided
- Motion is front-loaded: the intro (~2s, CLS 0) and the Work cards carry it, while About and Contact are nearly static. The fix is one closing beat at Contact (h2.xl rises char by char like the h1, then the email underline draws in via a --u custom property -> scaleX on .email::after), not reveals on every section.
- Current-motion bugs found: count-ups of single digits show false values mid-count ("Retrieval under 0 second"), so the .hl filter should be /\d\d/ (only $22.4M counts). gsap.set autoAlpha:0 on .card/.job takes their links out of the Tab order until they scroll in. .cta.down:hover::after (0,3,1) beats the reduce block's .cta:hover::after null, so the arrow still jumps under reduced motion. At 1440x1200 the GitHub card opens over both hero CTAs; a .15s hover delay fixes it.
- Keyboard twins for hovers should use :has(:focus-visible), not :focus-within (a mouse click would leave the card lit).

## Tried and ruled out
- All four h2s rising on scroll: it turns the hero's signature gesture into a template, and it flashes headings that are already on screen.
- A fade-up batch for leads/prose/offer: .offer never reaches the 85% line on tall viewports (stays at opacity 0), and it would be the fourth use of the same verb.
- Per-section hairline/rule draws: #262626 on #141414 under the canvas is barely visible.
- a:active { opacity: .6 }: the inline opacity GSAP's autoAlpha leaves on .paths .cta beats it.
- @view-transition into snake.html: on the way back it lands on the .js-hidden hero mid-intro. Low value.

## Watch out
- SplitText line masks (overflow: clip) cut descenders at h2 line-heights (the g in "something.", the p in "products."). Pad the masks: padding-bottom .2em; margin-bottom -.2em.
- SplitText aria:'auto' sets aria-label from textContent, so "Let's build<br>something." reads as "buildsomething". Put a space before the <br>.
- autoSplit re-splits on resize. Keep a fired flag so onSplit doesn't replay a scroll-triggered rise.
- `a [aria-hidden="true"]` also matches SplitText's char divs inside a.gh. Give the ARROW span a class instead.
- The reduce block's `*, ::before, ::after` doesn't reach ::view-transition-* pseudos, and its transition-property list leaves out visibility.
- The footer never reaches the `top 85%` once trigger, so a reveal there would stay hidden forever.
- Headless Brave via playwright-core from an old scratchpad (node_modules/playwright-core, executablePath Brave) works for timed screenshots. It hung once with a process-singleton lock when two agents launched it at the same time.
