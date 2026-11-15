"""Generate index.html from the page copy and content/*.csv, in the DESIGN.md style.

Run `python3 design-ref/build_html.py` after editing a sheet or the copy in content.py, then upload
index.html. The output is plain static HTML with inline CSS (no build step on the host, no runtime fetch).
"""
import re
from html import escape
from pathlib import Path

from content import *

OUT = Path(__file__).resolve().parent.parent / "index.html"


def e(s):
    return escape(s, quote=True)


def br(s):
    """Copy line breaks become <br> on wide screens only."""
    return " <br class=\"wide\">".join(e(line) for line in s.split("\n"))


# Literal arrows are decoration: screen readers would say "north-east arrow". New-tab links say so instead.
ICON = ("""<link rel="icon" href='data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">"""
        """<rect width="64" height="64" rx="12" fill="%23141414"/><path d="M18 20 L32 46 L46 20" stroke="%23F2F2F2" """
        """stroke-width="7" fill="none" stroke-linejoin="round"/></svg>'>""")
ARROW = '<span aria-hidden="true">↗</span>'
NEW_TAB = '<span class="sr-only"> (opens in new tab)</span>'


def arrow(s):
    return e(s).replace("↗", ARROW)


def ext(url, label, cls="link"):
    return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener">{arrow(label)}{NEW_TAB}</a>'


def cases():
    """{project title: (page name, fragment)} for content/cases/*.html. A fragment is the article body as plain HTML
    (h1, a .lede paragraph, h2/h3, p, ul, table); its first line names the project it belongs to."""
    out = {}
    for f in sorted((CONTENT / "cases").glob("*.html")):
        body = f.read_text()
        out[re.match(r"<!-- project: (.+?) -->", body).group(1)] = (f"case-{f.stem}.html", body)
    return out


CASES = cases()


def card(i, p):
    img = p.get("image")
    cover = (f'<div class="cover"><img src="{e(img)}" alt="{e(p["title"])} preview" width="960" height="600" loading="lazy"></div>'
             if img else f'<div class="cover ph" aria-hidden="true">{e(p["monogram"])}</div>')
    parts = [f'<span class="idx" aria-hidden="true">{i:02}</span>', cover,
             f'<h3>{e(p["title"])}</h3>',
             f'<p class="meta">{e(card_meta(p))}</p>']
    if p["summary"]:
        parts.append(f'<p class="body">{e(p["summary"])}</p>')
    if p["highlight"]:
        parts.append(f'<p class="hl">↳ {e(p["highlight"])}</p>')
    parts.append(f'<p class="tags">{e(tags(p["stack"], 3))}</p>')
    links = ([f'<a class="link live" href="{CASES[p["title"]][0]}">Case study</a>'] if p["title"] in CASES else []) + \
            ([ext(p["live"], link_label(p["live"]), "link live")] if p.get("live") else []) + \
            ([ext(p["repo"], link_label(p["repo"]))] if p["repo"] else [])
    if links:
        parts.append(f'<p class="links-row">{"".join(links)}</p>')
    return '<article class="card">' + "".join(parts) + "</article>"


def more_row(p):
    title = ext(p["repo"], p["title"] + " ↗", "title") if p["repo"] else f'<span class="title">{e(p["title"])}</span>'
    meta = " · ".join(v for v in (p["year"][:4], p["kind"].upper()) if v)
    return (f'<li class="row"><span class="c1 mono">{e(meta)}</span><span class="c2">{title}</span>'
            f'<span class="c34">{e(p["summary"])}</span></li>')


def job(r):
    details = [f'<p class="body">{e(r["summary"])}</p>']
    if r["highlight"]:
        details.append(f'<p class="hl">↳ {e(r["highlight"])}</p>')
    if r["stack"]:
        details.append(f'<p class="tags mono">{e(tags(r["stack"]))}</p>')
    if r["link"]:
        details.append(ext(r["link"], bare(r["link"]) + " ↗"))
    loc = f'<p class="loc">{e(r["location"])}</p>' if r["location"] else ""
    name = r["company"].removeprefix("PT. ").removeprefix("PT ")
    paths = [x.strip() for x in r.get("logo", "").split(";") if x.strip()]
    logo = ('<div class="logos">' + "".join(f'<img class="logo" src="{e(x)}" alt="" width="44" height="44" loading="lazy">' for x in paths)
            + "</div>" if paths else f'<span class="logo" aria-hidden="true">{e(name[:2].upper())}</span>')
    return (f'<li class="row job"><div class="c1"><p class="dates mono">{e(span(r))}</p>'
            f'<p class="type mono">{e(r["type"].upper())}</p></div>'
            f'<div class="c2">{logo}<h3>{e(r["role"])}</h3><p class="company">{e(r["company"])}</p>{loc}</div>'
            f'<div class="c34">{"".join(details)}</div></li>')


JS = ("gsap.min.js", "ScrollTrigger.min.js", "SplitText.min.js", "ScrambleTextPlugin.min.js", "lenis.min.js")
FONTS = ("inter-latin.woff2", "fira-code-400-latin.woff2")   # fonts/, both preloaded (hero name + mono labels)
# the closing flower: the reel's frames as a sheet (design-ref/trace_flower.py), which stage.py ships through the canvas'
# data-src, and the poster: the shader's first frame at 1920 x 1080, shot in a browser
END_FLOWER = ("img/footer-flower.png", "img/footer-flower.jpg")
LATIN = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, "
         "U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")  # Google's latin subset range

# Runs first, in <head>: the .js class hides the hero until GSAP takes over, and drops itself after 3s
# so a script that never loads can't leave the page blank. No class with reduced motion, so nothing hides.
HEAD_JS = """const r = document.documentElement;
if (matchMedia("(prefers-reduced-motion: no-preference)").matches) {
  r.classList.add("js"); setTimeout(() => r.classList.remove("js"), 3000);
}"""

# The page's script, design-ref/anim.js: the hero's and the closing flower's WebGL, the snap, and the entrance and
# scroll animations (only transform, opacity and clip-path; each element plays once, the parallax is scroll-linked).
ANIM_JS = (Path(__file__).parent / "anim.js").read_text().rstrip("\n")   # inlined into the page


def gh_card(url):
    """GitHub profile card for the hero's "vadh". It sits beside the h1, not in it: SplitText's line masks clip.
    The card is a mouse shortcut only (tabindex -1, aria-hidden); the "vadh" link itself is the keyboard path and
    reads the card as its description. data-k fields are refreshed from the GitHub API by ghCard()."""
    g = GITHUB
    stats = "".join(f'<div><dt>{k}</dt><dd data-k="{key}">{g[key]}</dd></div>'
                    for k, key in (("Repos", "public_repos"), ("Followers", "followers"), ("Following", "following")))
    return (f'<a class="gh-card" id="gh-card" href="{e(url)}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">'
            f'<span class="gh-head">GitHub · Profile</span>'
            f'<span class="gh-who"><img src="{e(g["avatar_url"])}&amp;s=112" alt="" width="56" height="56" loading="lazy">'
            f'<span><strong data-k="name">{e(g["name"])}</strong><span class="mono">@{e(g["login"])}</span></span></span>'
            f'<span class="gh-bio" data-k="bio">{e(g["bio"])}</span>'
            f'<dl>{stats}</dl></a>')


def page():
    featured, rest = projects()
    mailto = f"mailto:{EMAIL}?subject=Project%20inquiry"
    links = {"GitHub": "https://github.com/vadhh", "LinkedIn": "https://linkedin.com/in/afr1dho"}
    return f"""<!doctype html>
<!-- Generated by design-ref/build_html.py from content.py and content/*.csv. Edit those, then re-run. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Afridho Tavadhu · AI features and web apps</title>
<meta name="description" content="{e(flat(LEAD))}">
{ICON}
{"".join(f'<link rel="preload" href="fonts/{f}" as="font" type="font/woff2" crossorigin>' for f in FONTS)}
<link rel="preload" href="img/batik-dots.bin" as="fetch" crossorigin>
<script>{HEAD_JS}</script>
{"".join(f'<script src="js/{f}" defer></script>' for f in JS)}
<style>
/* self-hosted latin subsets (SIL OFL, see fonts/OFL.txt); Inter is one variable file for 400 and 600.
   ↗ and ↳ aren't in either font (nor in Google's), so they fall back to the system face as before. */
@font-face {{ font-family: "Inter"; font-weight: 400 600; font-display: swap; src: url(fonts/{FONTS[0]}) format("woff2");
  unicode-range: {LATIN}; }}
@font-face {{ font-family: "Fira Code"; font-weight: 400; font-display: swap; src: url(fonts/{FONTS[1]}) format("woff2");
  unicode-range: {LATIN}; }}
/* size-matched Arial while Inter loads, so the swap barely shifts layout; no weight range, so 600 gets synthetic bold */
@font-face {{ font-family: "Inter Fallback"; src: local("Arial"); size-adjust: 107.31%; ascent-override: 90.27%;
  descent-override: 22.48%; line-gap-override: 0%; }}
:root {{
  --bg: #141414; --line: #262626; --text: #F2F2F2; --muted: #8C8C8C; --white: #FFFFFF; --card: #1B1B1B; --stripe: #181818;
  --pad: 39px; --gut: 30px;
  color-scheme: dark;
  --pop: #F2C230; --sans: "Inter", "Inter Fallback", system-ui, sans-serif; --mono: "Fira Code", ui-monospace, monospace;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }} html.lenis {{ scroll-behavior: auto; }}
body {{ background: var(--bg); color: var(--text); font: 16px/1.5 var(--sans); -webkit-font-smoothing: antialiased; }}
/* a stacked halo of page colour (blurs alone are too faint round thin strokes) clears the batik dots right round each glyph, so small grey copy reads over the bright tones */
.hero {{ text-shadow: 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 8px var(--bg), 0 0 8px var(--bg); }} .gh-card, .card {{ text-shadow: none; }}
/* the haloed hero text that moves (the name's letters rising and its parallax; the lead, paths and facts fading up) gets
   its own compositor layers, drawn once and then moved. Redrawn every frame, its six blurred shadows on 192px letters kept
   the GPU at ~75% and dropped about a third of the frames on load and on scrolling out (measured on an M1, headed) */
@media (prefers-reduced-motion: no-preference) {{ h1, h1 div, .intro .lead span, .paths .cta, .facts > * {{ will-change: transform; }} }}
a {{ color: inherit; text-decoration: none; }}
ul {{ list-style: none; }}
:focus-visible {{ outline: 2px solid var(--white); outline-offset: 3px; }}
/* anchor targets take focus (tabindex=-1) so Tab continues from there; they never show a ring */
[tabindex="-1"]:focus {{ outline: none; }}
.skip {{ position: absolute; z-index: 10; top: 12px; left: var(--pad); padding: 13px 16px; font: 13px var(--mono);
  color: var(--text); background: var(--bg); border: 1px solid var(--line); transform: translateY(-200%); }}
.skip:focus {{ transform: none; }}
.sr-only {{ position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0);
  white-space: nowrap; border: 0; }}
.mono {{ font-family: var(--mono); }}
.muted {{ color: var(--muted); }}

/* 4-column grid with hairline rules at the column boundaries; spanning text blocks mask the rule */
.wrap {{ position: relative; max-width: 1440px; margin: 0 auto; padding-inline: var(--pad); }}
.wrap::before {{ content: ""; position: absolute; inset: 0 var(--pad); pointer-events: none;
  background: linear-gradient(var(--line), var(--line)) 25% 0 / 1px 100% no-repeat,
    linear-gradient(var(--line), var(--line)) 50% 0 / 1px 100% no-repeat,
    linear-gradient(var(--line), var(--line)) 75% 0 / 1px 100% no-repeat;
  transform: scaleY(var(--rule, 1)); transform-origin: top; }}
.wrap > * {{ position: relative; }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.c1 {{ grid-column: 1; }} .c2 {{ grid-column: 2; padding-left: var(--gut); }}
.c34 {{ grid-column: 3 / 5; padding-left: var(--gut); background: var(--bg); }}
.rule-top {{ border-top: 1px solid var(--line); }}
section.wrap {{ border-top: 1px solid var(--line); padding-top: 120px; padding-bottom: 120px; }}

.label {{ font: 13px var(--mono); letter-spacing: .04em; color: var(--muted); margin-bottom: 14px; }}
h2 {{ font-weight: 600; font-size: clamp(48px, 6.7vw, 96px); line-height: 1.04; letter-spacing: -.06em; }}
h2.m {{ font-size: clamp(36px, 5vw, 72px); letter-spacing: -.05em; }}
h2.xl {{ font-size: clamp(56px, 8.3vw, 120px); letter-spacing: -.06em; line-height: .97; }}
/* SplitText's line masks clip (overflow: clip); at line-height .97 they'd cut the g's tail. Padding plus an equal
   negative margin gives it room without moving the layout. */
.ln-mask {{ padding-bottom: .2em; margin-bottom: -.2em; }}
.lead {{ font-size: clamp(18px, 1.7vw, 24px); line-height: 1.33; letter-spacing: -.02em; color: var(--muted); }}
.cta {{ display: inline-flex; justify-content: space-between; gap: 24px; min-width: 170px; padding-bottom: 14px;
  font-size: 20px; letter-spacing: -.02em; background: linear-gradient(var(--white), var(--white)) 0 100% / 100% 2px no-repeat;
  transition: background-size .3s; }}
.cta::after {{ content: "↗"; content: "↗" / ""; transition: transform .2s; }}
/* keyboard focus gets the same feedback as hover, here and on every link style below */
.cta:hover, .cta:focus-visible {{ background-size: 0 2px; }}
.cta:hover::after, .cta:focus-visible::after {{ transform: translate(2px, -2px); }}

/* hero */
.nav {{ padding-top: 30px; font-size: 14px; align-items: baseline; }}
.nav .logo {{ font-weight: 600; font-size: 16px; letter-spacing: -.02em; }}
.nav ul {{ grid-column: 2 / 4; display: flex; padding-left: 0; }}
.nav li {{ flex: 1; }} .nav li a {{ color: var(--muted); }} .nav li a:hover, .nav li a:focus-visible {{ color: var(--text); }}
.nav .go {{ grid-column: 4; padding-left: 0; }}
.corner {{ position: absolute; top: 96px; width: 13px; height: 13px; border: 1.5px solid var(--white); }}
.corner.l {{ left: var(--pad); border-width: 1.5px 0 0 1.5px; }} .corner.r {{ right: var(--pad); border-width: 1.5px 1.5px 0 0; }}
/* the batik sits behind the hero only and fades out over its last 30%; full strength, as rendered in Remotion (its
   own masks already dim the dots under the nav and the name) */
.bg-waves {{ position: absolute; top: 0; left: 0; width: 100%; z-index: -1; pointer-events: none;
  -webkit-mask-image: linear-gradient(#000 70%, transparent); mask-image: linear-gradient(#000 70%, transparent); }}
/* below 1024 the name sits under the nav and the lead mid-hero, out of reach of the masks made for a name along the
   bottom, so the dots stay at half strength there */
@media (max-width: 1023px) {{ .bg-waves {{ opacity: .5; }} }}
/* pause for the batik: a 30px ring in a 44px target under the right corner bracket; two bars, a triangle when paused */
.bg-pause {{ position: absolute; z-index: 2; top: 116px; right: calc(var(--pad) - 7px); width: 44px; height: 44px; padding: 0; border: 0;
  background: none; color: var(--muted); cursor: pointer; display: grid; place-items: center; }}
.bg-pause[hidden] {{ display: none; }}
.bg-pause::before {{ content: ""; grid-area: 1 / 1; width: 30px; height: 30px; border: 1px solid var(--line); border-radius: 50%; }}
.bg-pause::after {{ content: ""; grid-area: 1 / 1; width: 9px; height: 10px; box-sizing: border-box; border-inline: 3px solid currentColor; }}
.bg-pause[aria-pressed="true"]::after {{ width: 0; height: 0; margin-left: 3px; border: solid transparent; border-width: 5px 0 5px 9px; border-left-color: currentColor; }}
.bg-pause:hover, .bg-pause:focus-visible {{ color: var(--text); }} .bg-pause:hover::before {{ border-color: var(--muted); }}
/* the first viewport holds name, offer, both paths and the facts row; the facts sit on its bottom edge */
.hero {{ display: flex; flex-direction: column; min-height: min(100svh, 1080px); container-type: inline-size; }}
.intro {{ margin-top: auto; padding: 120px 0 56px; align-items: end; }}
h1 {{ grid-column: 1 / -1; font-weight: 600; font-size: min(13.6cqw, 192px); line-height: .9; letter-spacing: -.06em;
  white-space: nowrap; margin-left: -.04em; }}
.hero .lead {{ grid-column: 1 / 3; margin-top: clamp(32px, 5vh, 56px); padding-right: var(--gut);
  font-size: clamp(22px, 2.2vw, 32px); line-height: 1.25; letter-spacing: -.03em; text-wrap: balance; }}
.hero .lead span:first-child {{ color: var(--text); display: block; }}   /* the focus line sits on its own line */
.paths {{ grid-column: 3 / 5; display: grid; grid-template-columns: 1fr 1fr; }}
.paths .cta {{ margin-left: var(--gut); justify-self: start; white-space: nowrap; font-size: clamp(16px, 1.45vw, 20px); }}
.cta.down::after {{ content: "↓"; content: "↓" / ""; }} .cta.down:hover::after, .cta.down:focus-visible::after {{ transform: translateY(3px); }}
.facts {{ border-top: 1px solid var(--line); padding: 24px 0 36px; align-items: end; }}
.facts dl + dl {{ padding-left: var(--gut); }} .facts dl:first-child {{ grid-column: 1 / 3; }}
.facts dt {{ font: 13px var(--mono); color: var(--muted); }} .facts dd {{ font-size: 18px; letter-spacing: -.02em; }}
/* "vadh" in the name opens a GitHub card on hover (mouse only, so a tap on a phone just follows the link) or keyboard
   focus. It lingers .2s after the pointer leaves, so the pointer can cross the gap onto it (::before bridges it, above or below). */
/* the hint: a faint underline that blinks twice like a cursor every 9s (reduced motion: no blink). It's set on the
   SplitText char divs too, because decoration doesn't reach inline-blocks, and kept close to the baseline so the
   line masks don't clip it. */
.gh, .gh > div {{ text-decoration: underline var(--line); text-decoration-thickness: .02em; text-underline-offset: .02em;
  transition: color .2s, text-decoration-color .2s; animation: gh-blink 9s -6.78s step-end infinite; }}
/* the negative delay starts the cycle 6.78s in, so the first blink (at 92% = 8.28s) comes 1.5s after load */
@keyframes gh-blink {{ 0% {{ text-decoration-color: var(--line); }} 92%, 96% {{ text-decoration-color: var(--muted); }}
  94%, 98% {{ text-decoration-color: var(--line); }} }}
/* while the batik plays, the first blink waits for it to enter and dim (waves() sets data-hint, "go" 1.5s after the
   entrance); "go" starts the cycle 8.1s in, so the blink comes 0.2s later, then every 9s */
.hero[data-hint="wait"] .gh, .hero[data-hint="wait"] .gh > div {{ animation: none; }}
.hero[data-hint="go"] .gh, .hero[data-hint="go"] .gh > div {{ animation-delay: -8.1s; }}
.gh:hover, .gh:focus-visible {{ color: var(--pop); }}
.gh:hover, .gh:focus-visible, .gh:hover > div, .gh:focus-visible > div {{ text-decoration-color: currentColor; animation: none; }}
.gh-card {{ position: absolute; z-index: 5; top: 0; left: 0; width: min(340px, 100%); padding: 20px;
  display: grid; gap: 16px; background: var(--card); border: 1px solid var(--line); border-radius: 6px;
  box-shadow: 0 24px 64px rgb(0 0 0 / .5); visibility: hidden; opacity: 0; transform: translateY(6px);
  transition: opacity .2s, transform .2s, visibility 0s .2s, border-color .2s; }}
.gh-card::before {{ content: ""; position: absolute; inset: -16px 0; }}
.intro:has(.gh:focus-visible, .gh-card:hover) .gh-card:not(.off) {{ visibility: visible; opacity: 1; transform: none; transition-delay: 0s; }}
/* hover waits .15s, so a pointer passing over "vadh" (say, from the nav down to the CTAs) doesn't open the card */
@media (hover: hover) {{ .intro:has(.gh:hover) .gh-card:not(.off) {{ visibility: visible; opacity: 1; transform: none; transition-delay: .15s; }} }}
.gh-card:hover {{ border-color: var(--muted); }}
.gh-head {{ display: flex; justify-content: space-between; font: 12px var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
.gh-head::after {{ content: "↗"; content: "↗" / ""; transition: transform .2s; }} .gh-card:hover .gh-head::after {{ transform: translate(2px, -2px); }}
.gh-who {{ display: flex; gap: 14px; align-items: center; }}
.gh-who img {{ border: 1px solid var(--line); border-radius: 6px; background: var(--bg); }}
.gh-who > span {{ display: grid; }}
.gh-who strong {{ font-weight: 600; font-size: 20px; line-height: 1.3; letter-spacing: -.04em; }}
.gh-who .mono {{ font-size: 13px; color: var(--muted); }}
.gh-bio {{ font-size: 14px; line-height: 1.43; letter-spacing: -.01em; color: var(--muted); }}
.gh-card dl {{ display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--line); padding-top: 14px; }}
.gh-card dl div + div {{ padding-left: 14px; border-left: 1px solid var(--line); }}
.gh-card dt {{ font: 12px var(--mono); color: var(--muted); }} .gh-card dd {{ font-size: 18px; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }}

/* work */
.work-body {{ margin-top: 70px; align-items: start; }}
.cards {{ grid-column: 2 / 5; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.card {{ position: relative; padding: 30px var(--gut) 30px; border-bottom: 1px solid var(--line); }}
.idx {{ display: block; text-align: right; margin-bottom: 12px; font: 13px var(--mono); color: var(--muted); }}
.cover {{ aspect-ratio: 16 / 10; overflow: hidden; background: var(--card); border: 1px solid var(--line); border-radius: 6px;
  transition: border-color .2s; }}
.cover img {{ display: block; width: 100%; height: 100%; object-fit: cover; filter: brightness(.88); transition: filter .2s; }}
.cover.ph {{ display: grid; place-items: center; font-weight: 600; font-size: 32px; letter-spacing: -.04em; color: var(--muted);
  background: repeating-linear-gradient(135deg, var(--card) 0 10px, var(--stripe) 10px 20px); }}
.card h3, .job h3 {{ font-weight: 600; font-size: 20px; line-height: 1.3; letter-spacing: -.04em; transition: color .2s; }}
.card h3 {{ margin-top: 24px; }}
/* :has(:focus-visible), not :focus-within, so a mouse click on a card link doesn't leave the card lit afterwards */
.card:hover h3, .card:has(:focus-visible) h3 {{ color: var(--white); }}
.card:hover .cover, .card:has(:focus-visible) .cover {{ border-color: var(--muted); }}
.card:hover .cover img, .card:has(:focus-visible) .cover img {{ filter: none; }}
.card .meta-line, p.meta {{ font: 12px var(--mono); letter-spacing: .08em; color: var(--muted); margin: 4px 0 10px; }}
.body {{ font-size: 14px; line-height: 1.43; color: var(--muted); letter-spacing: -.01em; }}
.hl {{ font-variant-numeric: tabular-nums; font-size: 13px; line-height: 1.4; margin-top: 10px; }}
.tags {{ font: 12px/1.5 var(--mono); margin-top: 8px; }}
.link {{ display: inline-block; font: 12px var(--mono); color: var(--muted); margin-top: 4px; }}
.link:hover, .title:hover, .link:focus-visible, .title:focus-visible {{ color: var(--text); }}
.links-row {{ display: flex; flex-wrap: wrap; gap: 0 18px; }} .link.live {{ color: var(--text); }}
.more {{ margin-top: 120px; }}
.more h3 {{ font-weight: 600; font-size: 32px; letter-spacing: -.04em; }}
.more .count {{ font-size: 14px; color: var(--muted); margin-bottom: 24px; }}
.rows .row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--line); padding: 13px 0; }}
.rows .row:last-child {{ border-bottom: 1px solid var(--line); }}
.rows .row > .c1 {{ font-size: 12px; color: var(--muted); padding-top: 3px; }}
.rows .row > .c2 {{ padding-left: 21px; }}
.rows .row > .c34 {{ font-size: 14px; color: var(--muted); padding-top: 1px; }}
.more .cta {{ margin-top: 56px; }}

/* experience */
.exp-head {{ align-items: start; }} .exp-head .lead {{ grid-column: 3 / 5; padding: 18px 0 0 var(--gut); }}
.jobs {{ margin-top: 72px; }}
.jobs .row.job {{ padding: 30px 0; }}
.dates {{ font-size: 14px; }} .type {{ font-size: 12px; letter-spacing: .08em; color: var(--muted); margin-top: 6px; }}
.job .c2 {{ padding-left: 21px; }}
.job .logo {{ display: grid; place-items: center; width: 44px; height: 44px; margin-bottom: 16px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--card); object-fit: cover; font-weight: 600; font-size: 14px; letter-spacing: -.02em; color: var(--muted); }}
.job .logos {{ display: flex; gap: 8px; }}
.job img.logo {{ padding: 0; opacity: .8; transition: opacity .2s; }} .job:hover img.logo, .job:has(:focus-visible) img.logo {{ opacity: 1; }}
.company {{ margin-top: 6px; }} .loc {{ font-size: 14px; color: var(--muted); }}
.job .body {{ font-size: 16px; line-height: 1.5; }} .job .hl {{ font-size: 14px; }} .job .tags {{ color: var(--muted); }}

/* about */
.about-body {{ margin-top: 80px; align-items: start; }}
.who {{ grid-column: 1 / 3; }}
.who dl {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 18px; }}
.who dt, .who dd {{ border-top: 1px solid var(--line); padding: 12px 0; }}
.who dt {{ font-size: 14px; color: var(--muted); }} .who dd {{ padding-left: 21px; font-size: 15px; letter-spacing: -.01em; }}
.who dl > :nth-last-child(-n+2) {{ border-bottom: 1px solid var(--line); }}
.who .label {{ margin: 0; }}
.prose {{ display: grid; gap: 30px; padding-top: 34px; }}
.prose p {{ font-size: 20px; line-height: 1.5; letter-spacing: -.01em; color: var(--muted); max-width: 620px; }}

/* contact */
.contact-body {{ align-items: start; }}
.contact-body .left {{ grid-column: 1 / 3; }}
.email {{ display: inline-block; margin-top: 70px; font-size: 32px; letter-spacing: -.03em; }}
/* the 2px underline is a pseudo-element, so it can draw in (GSAP tweens --u) and retract to the left on hover or focus
   like the CTA's; a border, not a background, so it still prints. Hover only where hover is real: a tap opens Mail. */
.email::after {{ content: ""; display: block; border-top: 2px solid var(--white); transform: scaleX(var(--u, 1));
  transform-origin: left; transition: transform .3s; }}
.email.drawing::after {{ transition: none; }}
.email:focus-visible::after {{ transform: scaleX(0); }}
@media (hover: hover) {{ .email:hover::after {{ transform: scaleX(0); }} }}
.offer {{ margin-top: 22px; font-size: 18px; color: var(--muted); letter-spacing: -.01em; max-width: 520px; }}
.links {{ grid-column: 3 / 5; padding-top: 30px; }}
.links li {{ border-top: 1px solid var(--line); background: var(--bg); }}
.links li:last-child {{ border-bottom: 1px solid var(--line); }}
.links a {{ display: grid; grid-template-columns: 1fr 1fr; padding: 22px 0 22px var(--gut); align-items: baseline; }}
.links strong {{ font-weight: 600; font-size: 20px; letter-spacing: -.04em; }}
.links a > span {{ font: 14px var(--mono); color: var(--muted); padding-left: var(--gut); }}
.links a:hover span, .links a:focus-visible span {{ color: var(--text); }}
footer.wrap {{ border-top: 1px solid var(--line); }}
footer .grid {{ padding: 30px 0 40px; font: 13px var(--mono); color: var(--muted); }}
footer .c4 {{ grid-column: 4; padding-left: 0; }}
footer a:hover, footer a:focus-visible {{ color: var(--text); }}
/* the flower closes the page: a screen of it past the footer, fading in from the ground, with no text on it. The wheel
   rests first with its top third showing (.third), then on the whole screen; the canvas draws over its poster, and its
   pause sits bottom right on a page-colour disc */
.flower-end {{ position: relative; height: 100svh;
  -webkit-mask-image: linear-gradient(transparent, #000 15%); mask-image: linear-gradient(transparent, #000 15%); }}
.flower-end img, .flower-end canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.flower-end .third {{ position: absolute; top: 33.333%; }}
.flower-end .bg-pause {{ top: auto; bottom: 24px; }} .flower-end .bg-pause::before {{ background: var(--bg); }}

/* phone and tablet: one column, horizontal hairlines only */
@media (max-width: 1023px) {{
  :root {{ --pad: 20px; }}
  .wrap::before, br.wide {{ display: none; }}
  .grid, .rows .row, .cards {{ grid-template-columns: minmax(0, 1fr); }}
  .grid > *, .rows .row > *, .cards {{ grid-column: 1 / -1 !important; padding-left: 0 !important; }}
  .grid > .gh-card {{ padding-left: 20px !important; }}
  section.wrap {{ padding-top: 48px; padding-bottom: 64px; }}
  .nav {{ grid-template-columns: 1fr auto; }} .nav ul {{ display: none; }} .nav .logo {{ grid-column: 1 !important; }} .nav .go {{ grid-column: 2 !important; }}
  .corner {{ top: 72px; }}
  .hero {{ min-height: 0; }}
  .intro {{ padding: 112px 0 40px; }}
  h1 {{ font-size: 25.5cqw; line-height: .88; white-space: normal; }}
  .hero .lead {{ margin-top: 28px; padding-right: 0; font-size: 20px; line-height: 1.3; }}
  .paths {{ display: flex; flex-wrap: wrap; gap: 14px 32px; margin-top: 32px; }}
  .paths .cta {{ margin: 0; min-width: 0; font-size: 18px; padding-bottom: 10px; }}
  .facts {{ padding: 0 0 48px; border-top: 0; }}
  .facts > dl {{ display: grid; grid-template-columns: 120px 1fr; border-top: 1px solid var(--line); padding: 12px 0 !important; }}
  .facts > dl:last-child {{ border-bottom: 1px solid var(--line); }}
  .work-body {{ margin-top: 28px; }} .cards {{ margin-top: 32px; border-top: 1px solid var(--line); }}
  .card {{ padding: 24px 0; }} .card h3 {{ margin-top: 20px; }}
  .more {{ margin-top: 48px; }} .more h3 {{ font-size: 26px; }}
  .rows .row {{ gap: 4px; padding: 14px 0; }}
  .exp-head .lead {{ padding: 20px 0 0 !important; }} .jobs {{ margin-top: 32px; }}
  .job .c1 {{ display: flex; justify-content: space-between; align-items: baseline; }} .type {{ margin: 0; }}
  .job .c2 {{ margin: 12px 0; }} .job .body {{ font-size: 15px; }}
  .about-body {{ margin-top: 20px; }} .prose {{ order: -1; padding: 0 0 32px; gap: 18px; }} .prose p {{ font-size: 17px; }}
  .who dl {{ grid-template-columns: 100px minmax(0, 1fr); }} .who dd {{ padding-left: 0; }}
  .email {{ margin-top: 36px; font-size: 24px; }} .offer {{ font-size: 16px; }}
  .links {{ padding-top: 40px; }} .links a {{ padding-left: 0; }} .links a > span {{ text-align: right; }}
  footer .grid {{ gap: 6px; }}
  /* ~44px hit areas for thumbs; padding and negative margin cancel out, so the rhythm doesn't move */
  .link {{ padding: 14px 0; margin: -10px 0 -14px; }}
  .rows .title {{ padding: 12px 0; }}
  footer a {{ justify-self: start; padding: 13px 0; margin: -13px 0; }}
  .nav a {{ padding: 11px 0; margin: -11px 0; }}
  .paths .cta {{ padding-top: 8px; margin-top: -8px; }}
  .email {{ padding-top: 6px; margin-top: 30px; }}
}}
/* hidden until the GSAP intro starts; the class only exists while JS runs with motion allowed */
.js h1, .js .intro .lead, .js .paths, .js .facts > *, .js .corner {{ visibility: hidden; }} .js .wrap {{ --rule: 0; }}
/* reduced motion: no movement, but the short (≤200ms) colour, border and opacity fades stay as hover feedback */
@media (prefers-reduced-motion: reduce) {{
  /* visibility is listed so the GitHub card's .15s hover delay holds here too; without it the card turns visible (and
     catches the pointer) at once, while its opacity still waits */
  *, ::before, ::after {{ transition-property: color, background-color, border-color, opacity, filter, visibility !important;
    animation: none !important; scroll-behavior: auto !important; }}
  /* !important: .cta.down:hover::after is more specific and would still drop the arrow */
  .cta::after, .gh-head::after {{ transform: none !important; }}
}}
/* print: black on white, and everything GSAP keeps hidden until it scrolls into view is shown (!important beats inline) */
@media print {{
  :root {{ --bg: #FFFFFF; --text: #000000; --muted: #444444; --white: #000000; --line: #CCCCCC; --card: #F2F2F2; --stripe: #E6E6E6;
    color-scheme: light; }}
  *, ::before, ::after {{ opacity: 1 !important; visibility: visible !important; transform: none !important; clip-path: none !important; }}
  .bg-waves, .bg-pause, .skip, .gh-card, .flower-end {{ display: none !important; }}
  /* the covers are light logos on transparent images, so they keep their dark panel */
  .cover {{ background: #1B1B1B; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  section.wrap {{ padding-top: 48px; padding-bottom: 48px; }}
  .card, .job, .rows .row {{ break-inside: avoid; }}
}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<canvas class="bg-waves" aria-hidden="true"></canvas>
<header class="wrap hero">
  <nav class="grid nav" aria-label="Main">
    <a class="logo" href="#top">vadhh</a>
    <ul><li><a href="#work">Work</a></li><li><a href="#experience">Experience</a></li><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul>
    <a class="go" href="{mailto}">Start a project {ARROW}</a>
  </nav>
  <span class="corner l" aria-hidden="true"></span><span class="corner r" aria-hidden="true"></span>
  <button class="bg-pause" type="button" aria-label="Pause background animation" aria-pressed="false" hidden></button>
  <div class="grid intro" id="top" tabindex="-1">
    <h1>Afridho Ta<a class="gh" href="{e(links["GitHub"])}" target="_blank" rel="noopener" aria-describedby="gh-card">vadh</a>u</h1>
    {gh_card(links["GitHub"])}
    <p class="lead">{"".join(f'<span>{e(x)}</span> ' for x in LEAD.split(chr(10)))}</p>
    <div class="paths"><a class="cta" href="{mailto}">Start a project</a><a class="cta down" href="#work">See selected work</a></div>
  </div>
  <div class="grid facts">
    {"".join(f'<dl><dt>{e(k)}</dt><dd>{e(v)}</dd></dl>' for k, v in META)}
  </div>
</header>

<main id="main" tabindex="-1">
<section class="wrap" id="work" tabindex="-1" aria-labelledby="work-h">
  <p class="label">01 / Work</p>
  <h2 id="work-h">Selected<br>work</h2>
  <div class="grid work-body">
    <p class="lead c1">{br(WORK_LEAD)}</p>
    <div class="cards">{"".join(card(i + 1, p) for i, p in enumerate(featured))}</div>
  </div>
  <div class="more">
    <h3>More projects</h3>
    <p class="count">{len(rest)} more on GitHub</p>
    <ul class="rows">{"".join(more_row(p) for p in rest)}</ul>
    <a class="cta" href="https://github.com/vadhh" target="_blank" rel="noopener">All repositories on GitHub{NEW_TAB}</a>
  </div>
</section>

<section class="wrap" id="experience" tabindex="-1" aria-labelledby="exp-h">
  <div class="grid exp-head">
    <div class="c1" style="grid-column: 1 / 3"><p class="label">02 / Experience</p><h2 id="exp-h">Where I've<br>worked</h2></div>
    <p class="lead">{br(EXPERIENCE_LEAD)}</p>
  </div>
  <ul class="rows jobs">{"".join(job(r) for r in jobs())}</ul>
</section>

<section class="wrap" id="about" tabindex="-1" aria-labelledby="about-h">
  <p class="label">03 / About</p>
  <h2 class="m" id="about-h">{br(ABOUT_HEADING)}</h2>
  <div class="grid about-body">
    <div class="who"><p class="label">~/whoami</p><dl>{"".join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in WHOAMI)}</dl></div>
    <div class="c34 prose">{"".join(f'<p>{e(b)}</p>' for b in ABOUT_BODY)}</div>
  </div>
</section>

<section class="wrap" id="contact" tabindex="-1" aria-labelledby="contact-h">
  <div class="grid contact-body">
    <div class="left">
      <p class="label">04 / Contact</p>
      <h2 class="xl" id="contact-h">Let's build <br>something.</h2>
      <a class="email" href="{mailto}">{e(EMAIL)}</a>
      <p class="offer">{br(OFFER)}</p>
    </div>
    <ul class="links">{"".join(f'<li><a href="{e(links[k])}" target="_blank" rel="noopener"><strong>{e(k)}</strong><span>{e(v)}  {ARROW}</span>{NEW_TAB}</a></li>' for k, v in LINKS)}</ul>
  </div>
</section>
</main>

<footer class="wrap">
  <div class="grid"><span class="c1">© 2026 Afridho Tavadhu</span><span class="c2">Batik: Gringsing Lidah Api Padma, photo <a href="https://www.instagram.com/katalogsuminarkediri/">@katalogsuminarkediri</a></span><span class="c4">Built by hand, no frameworks</span></div>
</footer>
<div class="flower-end">
  <img src="{END_FLOWER[1]}" alt="" width="1920" height="1080" loading="lazy" decoding="async">
  <canvas data-src="{END_FLOWER[0]}" aria-hidden="true"></canvas>
  <span class="third"></span>
  <button class="bg-pause" type="button" aria-label="Pause flower animation" aria-pressed="false" hidden></button>
</div>
<script>
{ANIM_JS}
</script>
</body>
</html>
"""


# Case-study pages: static, no script. Same tokens and fonts as the index, copied by hand like snake.html; the article
# sits on the index grid's second and third columns.
CASE_CSS = """
:root { --bg: #141414; --line: #262626; --text: #F2F2F2; --muted: #8C8C8C; --white: #FFFFFF; --pad: 39px; color-scheme: dark;
  --sans: "Inter", "Inter Fallback", system-ui, sans-serif; --mono: "Fira Code", ui-monospace, monospace; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font: 17px/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--white); outline-offset: 3px; }
.skip { position: absolute; top: 12px; left: var(--pad); padding: 13px 16px; font: 13px var(--mono); background: var(--bg);
  border: 1px solid var(--line); transform: translateY(-200%); } .skip:focus { transform: none; }
.wrap { max-width: 1440px; margin: 0 auto; padding-inline: var(--pad); }
nav, footer { display: flex; justify-content: space-between; gap: 24px; padding-block: 30px; font-size: 14px; }
nav a, footer a { text-decoration: none; color: var(--muted); } nav .logo { color: var(--text); font-weight: 600; font-size: 16px; }
nav a:hover, nav a:focus-visible, footer a:hover, footer a:focus-visible { color: var(--text); }
footer { border-top: 1px solid var(--line); color: var(--muted); }
article { max-width: 760px; padding-block: 80px 120px; }
.label { font: 13px var(--mono); letter-spacing: .04em; color: var(--muted); margin-bottom: 14px; text-transform: uppercase; }
h1 { font-weight: 600; font-size: clamp(36px, 5vw, 64px); line-height: 1.04; letter-spacing: -.05em; text-wrap: balance; }
.lede { font-size: clamp(19px, 1.8vw, 22px); line-height: 1.45; margin-top: 32px; }
h2 { font-weight: 600; font-size: 28px; line-height: 1.15; letter-spacing: -.03em; margin-top: 72px; padding-top: 24px;
  border-top: 1px solid var(--line); }
h3 { font-weight: 600; font-size: 18px; margin-top: 36px; }
p, ul, .tbl { margin-top: 18px; }
ul { padding-left: 1.2em; } li + li { margin-top: 8px; }
code { font: .88em var(--mono); }
/* wide tables scroll inside their own box on phones; the box takes focus so the keyboard can scroll it */
.tbl { overflow-x: auto; }
table { width: 100%; min-width: 560px; border-collapse: collapse; font-size: 14px; line-height: 1.45; }
th, td { text-align: left; vertical-align: top; padding: 12px 20px 12px 0; border-bottom: 1px solid var(--line); }
th { font: 12px var(--mono); letter-spacing: .04em; color: var(--muted); text-transform: uppercase; }
@media (min-width: 1024px) { article { margin-left: 25%; } }
@media (max-width: 640px) { :root { --pad: 20px; } article { padding-block: 48px 80px; } h2 { margin-top: 56px; } }
@media print { :root { --bg: #fff; --text: #000; --muted: #444; --line: #bbb; --white: #000; color-scheme: light; }
  nav, footer { display: none; } article { margin: 0; max-width: none; padding: 0; } table { min-width: 0; } }
"""


def case_page(body, p):
    title = re.search(r"<h1>(.*?)</h1>", body).group(1)
    lede = re.sub(r"<[^>]+>", "", re.search(r'<p class="lede">(.*?)</p>', body, re.S).group(1))
    body = body.replace("<table>", '<div class="tbl" tabindex="0" role="region" aria-label="Table"><table>').replace("</table>", "</table></div>")
    return f"""<!doctype html>
<!-- Generated by design-ref/build_html.py from content/cases/. Edit the fragment there, then re-run. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Afridho Tavadhu</title>
<meta name="description" content="{e(lede)}">
{ICON}
<style>
@font-face {{ font-family: "Inter"; font-weight: 400 600; font-display: swap; src: url(fonts/{FONTS[0]}) format("woff2");
  unicode-range: {LATIN}; }}
@font-face {{ font-family: "Fira Code"; font-weight: 400; font-display: swap; src: url(fonts/{FONTS[1]}) format("woff2");
  unicode-range: {LATIN}; }}
@font-face {{ font-family: "Inter Fallback"; src: local("Arial"); size-adjust: 107.31%; ascent-override: 90.27%;
  descent-override: 22.48%; line-gap-override: 0%; }}{CASE_CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<nav class="wrap" aria-label="Main"><a class="logo" href="index.html">vadhh</a><a href="index.html#work">← All work</a></nav>
<main class="wrap" id="main">
<article>
<p class="label">Case study · {e(p["title"])} · {e(p["kind"])}</p>
{body}</article>
</main>
<footer class="wrap"><a href="index.html#work">← All work</a><a href="mailto:{EMAIL}?subject=Project%20inquiry">{EMAIL}</a></footer>
</body>
</html>
"""


def check(html):
    """The page shows exactly the featured cards and nothing marked show=no."""
    featured, rest = projects()
    hidden = [p["title"] for p in sheet("projects") if p["show"].lower() == "no"]
    assert html.count('<article class="card">') == len(featured), "card count"
    for p in featured + rest:
        assert e(p["title"]) in html, p["title"]
    for p in featured:
        assert not p.get("image") or (CONTENT.parent / p["image"]).is_file(), f"missing image: {p['image']}"
    for r in jobs():
        for x in filter(None, (x.strip() for x in r.get("logo", "").split(";"))):
            assert (CONTENT.parent / x).is_file(), f"missing logo: {x}"
    for t in hidden:
        assert f">{e(t)}<" not in html and f">{e(t)} {ARROW}" not in html, f"hidden project shown: {t}"
    for r in jobs():
        assert e(r["role"]) in html, r["role"]
    for f in JS:
        assert (OUT.parent / "js" / f).is_file() and f'<script src="js/{f}" defer>' in html, f"missing script: js/{f}"
    for f in FONTS:
        assert (OUT.parent / "fonts" / f).is_file() and f"url(fonts/{f})" in html, f"missing font: fonts/{f}"
    assert "fonts.googleapis" not in html, "Google Fonts link is back"
    # the hero's dots: the preload is what makes stage.py ship the file the script fetches
    assert (OUT.parent / "img/batik-dots.bin").is_file() and 'href="img/batik-dots.bin"' in html \
        and 'fetch("img/batik-dots.bin")' in html, "missing img/batik-dots.bin (python3 design-ref/pack_dots.py)"
    for t, (name, _) in CASES.items():
        assert t in [p["title"] for p in featured] and f'href="{name}"' in html, f"case study without a featured card: {t}"
    assert '<a class="gh"' in html and 'id="gh-card"' in html, "GitHub hover card missing"
    for f in END_FLOWER:
        assert (OUT.parent / f).is_file() and f'"{f}"' in html, f"missing {f} (uv run design-ref/trace_flower.py <reel>)"


if __name__ == "__main__":
    html = page()
    check(html)
    OUT.write_text(html)
    print(f"wrote {OUT} ({len(html) // 1024} KB)")
    by_title = {p["title"]: p for p in sheet("projects")}
    for t, (name, body) in CASES.items():
        (OUT.parent / name).write_text(case_page(body, by_title[t]))
        print(f"wrote {name}")
