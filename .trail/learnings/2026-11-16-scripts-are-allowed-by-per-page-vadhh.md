---
title: "Scripts are allowed by per-page hashes added at staging, so a new inline handler or script breaks only in production"
author: Vadhh
date: 2026-11-16
branch: master
cost: { minutes: 12, tokens: 206376 }
id: l-0cea416a
scope: repo
status: active
src: agent
touches:
  - design-ref/stage.py
  - vercel.json
---

## Decided
Each shipped page gets a Content-Security-Policy meta whose script-src lists the sha256 of that page's own inline scripts ('self' only where the page loads same-origin script files, 'none' on the script-free case pages). The site-wide headers (frame-ancestors, X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy, COOP) stay static in the Vercel config. This follows Google's Modern Web Guidance security guide (script hashes for static HTML).

## Tried and ruled out
- 'strict-dynamic': it blocks the parser-inserted vendor script tags (GSAP, Lenis), so the page would lose its animation.
- Putting the hashes in the Vercel header config: Vercel reads that file before the build runs, so per-build hashes can't go there.
- focus-without-user-activation in Permissions-Policy: Brave/Chrome log an origin-trial warning on every page, and the site has no iframes.

## Watch out
- A wrong hash, an inline onclick=, a javascript: link or eval does not fail the build. It ships, and the browser blocks it silently in production. Convert handlers to addEventListener, and check every new page in a browser console.
- On Vercel preview deployments the toolbar script from vercel.live is blocked too. A violation whose blocked URI is vercel.live is that toolbar, not a bug. One that reads "inline" (script-src-elem) is a real hash failure.
- A check that can't fail proves nothing: corrupting one hash in a copy of the staged page must produce a script-src-elem violation.

In the code: design-ref/stage.py with_csp() (INLINE_JS regex, meta inserted right after <meta charset>); vercel.json "headers". Verified on 2026-11-16 by recomputing the hashes with Python's html.parser on all 5 pages (system Python and uv --python 3.12), plus 0 CSP violations in headless Brave with the production headers. A cheap guard not yet added: assert in with_csp that no page has <tag on*=...> or href="javascript:".
