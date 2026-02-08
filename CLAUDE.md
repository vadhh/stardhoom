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

Each page is a self-contained HTML file with inline CSS and JS:

- **index.html** — Main portfolio page: ASCII banner, skills tree, project logs, contact links
- **about.html** — Profile page with interactive animations (CTF-style decrypt reveal, traceroute simulation)
- **snake.html** — Canvas-based Snake game with keyboard and mobile touch controls

All styling follows a shared retro terminal theme (CRT scanline effects, green-on-dark color scheme, Fira Code monospace font). Styles and scripts are embedded directly in each HTML file rather than shared via external files.
