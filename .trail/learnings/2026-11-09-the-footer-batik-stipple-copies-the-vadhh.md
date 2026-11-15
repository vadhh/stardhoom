---
title: "The footer batik stipple copies the reference's style through measured curves, and needs a tinted layer under the marks"
author: Vadhh
date: 2026-11-09
branch: master
cost: { minutes: 1, tokens: 2741 }
id: l-d0f2a5af
scope: repo
status: active
src: agent
---

## Decided
The footer batik dots follow a style reference (a stippled portrait the user supplied), not a look picked by eye. Every style number is measured from the reference, and the dots are checked by measuring the render the same way: coverage per tone, grain period, clump spacing and depth, chroma of marks and gaps, tone error. The batik's luminance p5..p95 is mapped onto the reference's tone range, and its chroma p90 onto the reference's (marks and gaps separately), keeping the batik's hue. Why: the user asked for the batik's motif to be followed faithfully and the style to match the reference, so both sides are measured rather than eyeballed.

## Tried and ruled out
- Marks only, on bare cream: the render came out much lighter than the reference at every tone, and calibrating density to the overall coverage only made it sparser. The reference's gaps are tinted (lum 184-245 on a 251 ground), so a layer of large pale dots under the marks is needed; with it, density 1.0 matches the per-tone coverage within 0.03 with no calibration factor.
- Uniform random dot placement: no grain. The reference's marks chain into strokes at about 4.9px (2x); putting the dots on the upper half of noise band-passed at that period reproduces it (5.1px).
- Peak of the raw power spectrum for the grain: it always lands on the lowest frequency of the band (both images gave 7.84px). Weight by frequency (power per octave).
- The batik's full chroma: about 1.6x too saturated against the reference.

## Watch out
- The stipple density is tied to the cloth drawn 1920 CSS px wide: about 1.06M dots, 60 MB of JSON. A footer crop needs the dots regenerated for that crop; pack binary like the hero before shipping.
- dots.json holds two kinds: the wash (r 3px, drawn first) and the marks (r 0.56px). Animating the wash dots one by one shows them as blobs.
- The global chroma mapping mutes the crown red most; the crowns lose contrast against the stripes.
- reference.png is someone else's signed artwork: never push it.

In the code: remotion/footer/stipple.py (measure(), grain_period(), bandpass_noise(), cloth(), WASH_PX=4), remotion/footer/stipple_check.py (writes compare-stipple*.png and stipple-check.json); run with `uv run remotion/footer/stipple.py [--seed 7 --density 1.0]` then `uv run remotion/footer/stipple_check.py`. The first extraction lives on as extract.py -> dots-v1.json.
