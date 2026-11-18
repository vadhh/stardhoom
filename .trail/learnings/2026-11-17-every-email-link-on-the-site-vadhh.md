---
title: Every email link on the site pre-fills the Project inquiry subject
author: Vadhh
date: 2026-11-17
branch: master
cost: { minutes: 1, tokens: 56542 }
id: l-19ed6944
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
---

## Decided
All mail links, including the visible address in the contact section, open with the subject "Project inquiry". The owner wants every message from the site tagged the same way.

## Tried and ruled out
A web-guidance audit changed the contact-section address to a bare mailto (no subject). The owner asked for the subject back.

## Watch out
Don't strip the subject from the visible email link in a future audit or cleanup pass.

In the code: design-ref/build_html.py builds `mailto = f"mailto:{EMAIL}?subject=Project%20inquiry"`; the `.email` link, the "Start a project" CTAs and the case-page footer all use it.
