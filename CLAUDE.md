# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website with a retro terminal/cyberpunk aesthetic. Static site hosted on Neocities — no build system, no package manager, no frameworks.

## Tech Stack

- Vanilla HTML5, CSS3, JavaScript (ES6+)
- HTML5 Canvas (Snake game)
- Inter + Fira Code, self-hosted in `fonts/` for index.html (about.html and snake.html still load Fira Code from Google Fonts)
- No dependencies, no build step

## Development

To develop locally, serve the files with any static file server:

```
python3 -m http.server 8000
```

Nothing builds on the host: the site is plain static HTML/CSS/JS. `index.html` is regenerated locally with `python3 design-ref/build_html.py`.

## Architecture

Each page is a self-contained HTML file with inline `<style>` and `<script>` blocks (no external CSS/JS files):

- **index.html** — **Generated, don't hand-edit.** Dark editorial portfolio (see `DESIGN.md`): hero → Work → Experience → About → Contact, vanilla CSS on a 4-column hairline grid that collapses to one column below 1024px. Animations use GSAP 3.15.0 (core, ScrollTrigger, SplitText, ScrambleText) plus Lenis 1.3.27 smooth scroll, vendored in `js/`; the page is fully visible without JS or with reduced motion. Regenerate with `python3 design-ref/build_html.py` after editing `content/experience.csv`, `content/projects.csv` (its `image` column points at card covers in `img/projects/`) or the copy in `design-ref/content.py`; the script asserts the featured/hidden projects before writing.
- **about.html** — Profile page with green-on-black terminal aesthetic, CRT scanline overlay, CTF-style decrypt animation, and traceroute simulation.
- **snake.html** — Standalone canvas Snake game with the same green-on-black CRT theme, keyboard and mobile touch controls.

### Style notes

- `index.html` uses Inter + Fira Code with the `#141414` / `#F2F2F2` palette from `DESIGN.md`; `about.html` and `snake.html` still use their own vanilla green-on-black CRT styles.
- Each page defines its own styles; there are no shared stylesheets.
- `design-ref/` holds the FigCraft build scripts (`build_portfolio.py`, `build_mobile.py`, via `fc.py`) and the HTML generator; `content.py` is the shared, I/O-free copy and sheet loader.
