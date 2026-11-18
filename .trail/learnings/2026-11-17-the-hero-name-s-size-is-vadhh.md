---
title: "The hero name's size is a design choice and stays outside the web type rules"
author: Vadhh
date: 2026-11-17
branch: master
cost: { minutes: 1, tokens: 6743 }
id: l-213f2165
scope: repo
status: active
src: agent
touches:
  - design-ref/build_html.py
---

## Decided
The hero name is display art sized to its container, not reading text. It keeps its container-relative size even though Modern Web Guidance asks for rem font sizes and a max of 2.5x the min in clamp(). The owner overruled the guide here.

## Tried and ruled out
- clamp(4.4rem, 25.5cqw, 11rem) below 1024: it shrank the name on tablets (250.7px to 176px at 1023px wide, hero 131px shorter). Reverted.

## Watch out
Guide audits and trail check will flag this rule again. Leave it.

In the code: design-ref/build_html.py h1 rules: min(13.6cqw, 192px), and 25.5cqw below 1024.
