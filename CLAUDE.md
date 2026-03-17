# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website with a retro terminal/cyberpunk aesthetic. Static site hosted on Neocities — no build system, no package manager, no frameworks.

## Tech Stack

- Vanilla HTML5, CSS3, JavaScript (ES6+)
- HTML5 Canvas (Snake game)
- Google Fonts (Fira Code)
- No dependencies, no build step

## Development

To develop locally, serve the files with any static file server:

```
python3 -m http.server 8000
```

There are no build, lint, or test commands — the site is pure static HTML/CSS/JS.

## Architecture

Each page is a self-contained HTML file with inline `<style>` and `<script>` blocks (no external CSS/JS files):

- **index.html** — TUI-style scrolling portfolio using Tailwind CSS (via CDN). Features a fixed sidebar file explorer with scroll-spy navigation, sections for hero/about/skills/projects/terminal/snake/contact, an inline interactive terminal (fake shell with virtual filesystem supporting `ls`, `cd`, `cat`, `help`, etc.), an embedded Snake game (canvas), and a contact form that opens mailto. Uses a deep navy/cyan color scheme (`#001b33` bg, `#00f2ff` primary, `#7fbfff` accent) with CRT scanline overlay.
- **about.html** — Profile page with green-on-black terminal aesthetic, CRT scanline overlay, CTF-style decrypt animation, and traceroute simulation.
- **snake.html** — Standalone canvas Snake game with the same green-on-black CRT theme, keyboard and mobile touch controls.

### Style notes

- `index.html` uses **Tailwind CSS** (CDN) + custom Tailwind config with a navy/cyan palette; `about.html` and `snake.html` use only vanilla CSS with green-on-black.
- All three pages independently import Fira Code from Google Fonts and define their own styles — there are no shared stylesheets.
- All three pages use a CRT scanline overlay effect.
