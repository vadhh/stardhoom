---
title: "The closing batik's photo leans, so it is straightened before it is mirrored"
author: Vadhh
date: 2026-11-11
branch: master
cost: { minutes: 33, tokens: 263724 }
id: l-831f1bf2
scope: repo
status: active
src: agent
touches:
  - DESIGN.md
  - design-ref/build_html.py
  - remotion/footer/stipple.py
---

## Decided
- The footer batik's source photo was shot leaning: its stripes lean 0.5 deg at the left to 4.5 deg at the right, and the weave leans 0 to 4 deg. Mirroring the photo to widen the frame flipped that lean on each side, so it read as chevrons and as a pinched "eye" at crown 4's mirror axis. The user asked for the vertical lines to be straight.
- The photo is straightened before it is mirrored and stippled. Each column slides sideways by the measured lean until its lines stand plumb; rows keep their height, so the crowns' 10.5 deg rise and the ripple are untouched. The slide is measured from the crowns' line (through their centroids), so the crowns stay where analysis.json found them.
- The lean is measured per 64px block as the median slope of near-vertical edges (structure tensor). Blocks that differ from the 5x5 around them by more than 0.03, which are the crowns' and the wave band's curves, are dropped, then the gaps are filled and smoothed. After straightening, the lean is within about 0.3 deg across the stripes. The style check barely moved.
- The mirror axes moved to the bar centres of the straightened stripes, 286 and 1971 (were 271 and 1972).

## Tried and ruled out
- Tracking the stripes' phase per column against each column's lowest stripe row: that foot is ragged (it jumps at every crown), so the shift jumped between neighbouring columns.
- Tracking the weave's 127px and 131px repeats by phase: the signal was too weak, and the results were noise. The structure tensor reads the weave's vertical bars directly.
- The old comment claiming the stripes lean only 0.12 deg at crown 4 was wrong; they lean about 3.5-4.5 deg there.

## Watch out
- The weave leans less than the stripes over the middle of the photo, so a warp fitted on the stripes alone would tip the weave the other way. That is why the lean is measured per block in both bands.

In the code: straighten() and AXES in remotion/footer/stipple.py (framed() calls it, so stipple_check.py's photo panel is straightened too); STRAIGHT_BLOCK = 64; then `uv run remotion/footer/stipple.py --dark --frame` and the render steps in DESIGN.md (Building).
