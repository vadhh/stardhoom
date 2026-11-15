---
title: "The hero batik is the owner's Remotion piece, ported live to WebGL instead of shipped as a video"
author: Vadhh
date: 2026-11-08
branch: master
cost: { minutes: 1, tokens: 3451 }
id: l-e80488db
scope: repo
status: active
replaces: l-6bd9369e
src: agent
touches:
  - design-ref/build_html.py
  - DESIGN.md
---

## Decided
- The owner designs the hero background in Remotion (remotion/, the BatikHeroEntrance composition: Gringsing Lidah Api Padma batik as 19,372 monochrome dots, a 2 s entrance from the flame outwards, then a seamless 10 s breathing loop). They asked not to ship the rendered MP4 but to convert it so it reacts to the cursor, and to keep it monochrome. It runs as a WebGL point port of remotion/src/batikDots.ts; at 1920x1080 its still frame matches the video's frame 0 at SSIM 0.985 with the same mean brightness.
- WebGL points, not a Canvas2D copy of batikDots.ts: 20-35k arcs a frame (with the mirror copies at 2560) would make the pointer lens stutter. No 2D fallback; without WebGL the canvas hides and the hero sits on the flat ground.
- Intensity 0.78 (the owner's BatikHeroWithOverlay composition, made for text on top) at full opacity from 1024 up. Below 1024 the name and lead sit mid-hero where Remotion's masks (built for a name along the bottom of a 16:9 frame) don't reach, so the canvas is at 50% there.
- The 8766 taste-skill redesign branch (bg/taste-effect) was purged at the owner's request; master is the only site.

## Tried and ruled out
- Keeping master's earlier .65 opacity everywhere: it dims the owner's tuned design on desktop where the masks already protect the text. Worst-pixel text contrast (halo stripped) is low at full strength, but the stacked --bg text halo clears dots round each glyph in practice.

## Watch out
- stage.py ships only files named in src/href/url(), so the fetched img/batik-dots.bin ships because of its <link rel="preload" as="fetch" crossorigin>; check() asserts both the preload and the fetch.
- After re-extracting dots in remotion/, re-run design-ref/pack_dots.py; the bin is what the page reads, not dots.json.
- The dots come from a different photo than img/batik-dahanapura.jpg (now unused); the photo's source and licence are unknown, so the footer names only the motif until the owner says where it came from.

In the code: design-ref/build_html.py DOTS_VS / DOTS_FS / waves(), design-ref/pack_dots.py, img/batik-dots.bin (8 bytes a dot: u16 x, y, r; u8 tone, flags), .bg-waves CSS.
