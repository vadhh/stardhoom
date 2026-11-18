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


def sr(s):
    return f'<span class="sr-only">{e(s)}</span>' if s else ""


def ext(url, label, cls="link", before="", after=""):
    """A new-tab link; before/after are visually hidden context around the visible label, so links to different
    targets get different names and links to the same target the same one (a repo reads "GitHub github.com/vadhh/x"
    whether it shows "GitHub" on a card or the bare URL on a job row)."""
    return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener">{sr(before)}{arrow(label)}{sr(after)}{NEW_TAB}</a>'


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
    links = ([f'<a class="link live" href="{CASES[p["title"]][0]}">Case study{sr(" (" + p["title"] + ")")}</a>'] if p["title"] in CASES else []) + \
            ([ext(p["live"], link_label(p["live"]), "link live")] if p.get("live") else []) + \
            ([ext(p["repo"], link_label(p["repo"]), after=bare(p["repo"]) if "github.com/" in p["repo"] else "")] if p["repo"] else [])
    if links:
        parts.append(f'<p class="links-row">{"".join(links)}</p>')
    return '<li><article class="card">' + "".join(parts) + "</article></li>"


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
        details.append(ext(r["link"], bare(r["link"]) + " ↗", before="GitHub " if "github.com/" in r["link"] else ""))
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
FONT_PRELOADS = "".join(f'<link rel="preload" href="fonts/{f}" as="font" type="font/woff2" crossorigin>' for f in FONTS)
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
    The card is a mouse shortcut, off the Tab path (tabindex -1) and out of the accessibility tree while it's hidden
    (visibility); the "vadh" link itself is the keyboard path and reads the card as its description. data-k fields are
    refreshed from the GitHub API by ghCard()."""
    g = GITHUB
    stats = "".join(f'<div><dt>{k}</dt><dd data-k="{key}">{g[key]}</dd></div>'
                    for k, key in (("Repos", "public_repos"), ("Followers", "followers"), ("Following", "following")))
    return (f'<a class="gh-card" id="gh-card" href="{e(url)}" target="_blank" rel="noopener" tabindex="-1">'
            f'<span class="gh-head">GitHub · Profile</span>'
            f'<span class="gh-who"><img src="{e(g["avatar_url"])}&amp;s=112" alt="" width="56" height="56" loading="lazy" fetchpriority="low">'
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
<meta name="color-scheme" content="dark">
<title>Afridho Tavadhu · AI features and web apps</title>
<meta name="description" content="{e(flat(LEAD))}">
{ICON}
{FONT_PRELOADS}
<link rel="preload" href="img/batik-dots.bin" as="fetch" crossorigin fetchpriority="low">
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
/* priority zones, lowest first: element resets, tokens and base styles, the page's components, and the one-column
   collapse below 1024px, which has to beat every component's placement */
@layer reset, base, components, overrides;
@layer reset {{
  body, h1, h2, h3, p, ul, dl, dd {{ margin: 0; }} ul {{ padding: 0; }}
}}
@layer base {{
:root {{
  --bg: #141414; --line: #262626; --text: #F2F2F2; --muted: #8C8C8C; --white: #FFFFFF; --card: #1B1B1B; --stripe: #181818;
  --hint: #666666;   /* the "vadh" underline: the faintest grey with 3:1 on --bg */
  --pad: 39px; --gut: 30px;
  color-scheme: dark;
  --pop: #F2C230; --sans: "Inter", "Inter Fallback", system-ui, sans-serif; --mono: "Fira Code", ui-monospace, monospace;
}}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior: smooth; }} html.lenis {{ scroll-behavior: auto; }} }}
body {{ background: var(--bg); color: var(--text); font: 1rem/1.5 var(--sans); -webkit-font-smoothing: antialiased; }}
/* a stacked halo of page colour (blurs alone are too faint round thin strokes) clears the batik dots right round each glyph, so small grey copy reads over the bright tones */
.hero {{ text-shadow: 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 3px var(--bg), 0 0 8px var(--bg), 0 0 8px var(--bg); }} .gh-card, .card {{ text-shadow: none; }}
/* the haloed hero text that moves (the name's letters rising and its parallax; the lead, paths and facts fading up) gets
   its own compositor layers, drawn once and then moved. Redrawn every frame, its six blurred shadows on 192px letters kept
   the GPU at ~75% and dropped about a third of the frames on load and on scrolling out (measured on an M1, headed) */
@media (prefers-reduced-motion: no-preference) {{ h1, h1 div, .intro .lead span, .paths .cta, .facts > * {{ will-change: transform; }} }}
a {{ color: inherit; text-decoration: none; }}
/* press: text links dim while held (hover brightens them, focus rings them); CTAs turn grey instead, since GSAP leaves
   an inline opacity (and scale: none) on the hero CTAs, and the pause buttons shrink */
a:active:not(.cta) {{ opacity: .6; }}
ul {{ list-style: none; }}
:focus-visible {{ outline: 2px solid var(--white); outline-offset: 3px; }}
/* anchor targets take focus (tabindex=-1) so Tab continues from there; a mouse jump shows no ring, a keyboard one does */
[tabindex="-1"]:focus:not(:focus-visible) {{ outline: none; }}
.skip {{ position: absolute; z-index: 10; top: 12px; inset-inline-start: var(--pad); padding: 13px 16px; font: .8125rem var(--mono);
  color: var(--text); background: var(--bg); border: 1px solid var(--line); transform: translateY(-200%); }}
.skip:focus {{ transform: none; }}
.sr-only {{ position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0);
  white-space: nowrap; border: 0; }}
.mono {{ font-family: var(--mono); }}
.muted {{ color: var(--muted); }}
}}

@layer components {{
/* 4-column grid with hairline rules at the column boundaries; spanning text blocks mask the rule */
.wrap {{ position: relative; box-sizing: border-box; max-width: 1440px; margin: 0 auto; padding-inline: var(--pad); }}
.wrap::before {{ content: ""; position: absolute; inset: 0 var(--pad); pointer-events: none;
  background: linear-gradient(var(--line), var(--line)) 25% 0 / 1px 100% no-repeat,
    linear-gradient(var(--line), var(--line)) 50% 0 / 1px 100% no-repeat,
    linear-gradient(var(--line), var(--line)) 75% 0 / 1px 100% no-repeat;
  transform: scaleY(var(--rule, 1)); transform-origin: top; }}
/* forced colors drop gradient backgrounds: the rules keep theirs, drawn in the system text colour */
@media (forced-colors: active) {{ .wrap::before {{ forced-color-adjust: none; --line: CanvasText; }} }}
.wrap > * {{ position: relative; }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.c1 {{ grid-column: 1; }} .c12 {{ grid-column: 1 / 3; }} .c2 {{ grid-column: 2; padding-inline-start: var(--gut); }}
.c34 {{ grid-column: 3 / 5; padding-inline-start: var(--gut); background: var(--bg); }}
.rule-top {{ border-top: 1px solid var(--line); }}
section.wrap {{ border-top: 1px solid var(--line); padding-top: 120px; padding-bottom: 120px; }}

.label {{ font: .8125rem var(--mono); letter-spacing: .04em; color: var(--muted); margin-bottom: 14px; }}
/* fluid type: rem bounds (max at most 2.5x min) and a small rem share in the slope, so zoom and the reader's font size
   reach it; equal to the old px/vw clamps at 390 and 1440 and within ~2px between */
h2 {{ font-weight: 600; font-size: clamp(3rem, .25rem + 6.42vw, 6rem); line-height: 1.04; letter-spacing: -.06em; }}
h2.m {{ font-size: clamp(2.25rem, .25rem + 4.73vw, 4.5rem); letter-spacing: -.05em; }}
h2.xl {{ font-size: clamp(3.5rem, .27rem + 8vw, 7.5rem); letter-spacing: -.06em; line-height: .97; }}
/* SplitText's line masks clip (overflow: clip); at line-height .97 they'd cut the g's tail. Padding plus an equal
   negative margin gives it room without moving the layout. */
.ln-mask {{ padding-bottom: .2em; margin-bottom: -.2em; }}
.lead {{ font-size: clamp(1.125rem, .25rem + 1.42vw, 1.5rem); line-height: 1.33; letter-spacing: -.02em; color: var(--muted); }}
/* the 2px underline is a pseudo-element like the email's: it scales (GSAP tweens --u in the intro), and as a border it
   survives forced colours and print */
.cta {{ position: relative; display: inline-flex; justify-content: space-between; gap: 24px; min-width: 170px; padding-bottom: 14px;
  font-size: 1.25rem; letter-spacing: -.02em; }}
.cta::before {{ content: ""; position: absolute; inset: auto 0 0; border-top: 2px solid var(--white);
  transform: scaleX(var(--u, 1)); transform-origin: left; }}
.cta::after {{ content: "↗"; content: "↗" / ""; }}
/* keyboard focus gets the same feedback as hover, here and on every link style below */
.cta:hover::before, .cta:focus-visible::before {{ transform: scaleX(0); }}
.cta:active {{ color: var(--muted); }} .bg-pause:active {{ scale: .9; }}
@media (prefers-reduced-motion: no-preference) {{
  .cta::before {{ transition: transform .3s; }} .cta::after {{ transition: transform .2s; }}
  .cta:hover::after, .cta:focus-visible::after {{ transform: translate(2px, -2px); }}
}}

/* hero */
.nav {{ padding-top: 30px; font-size: .875rem; align-items: baseline; }}
.nav .logo {{ font-weight: 600; font-size: 1rem; letter-spacing: -.02em; }}
.nav ul {{ grid-column: 2 / 4; display: flex; padding-inline-start: 0; }}
.nav li {{ flex: 1; }} .nav li a {{ color: var(--muted); }} .nav li a:hover, .nav li a:focus-visible {{ color: var(--text); }}
.nav .go {{ grid-column: 4; padding-inline-start: 0; }}
.corner {{ position: absolute; top: 96px; box-sizing: border-box; width: 13px; height: 13px; border: 1.5px solid var(--white); }}
.corner.l {{ inset-inline-start: var(--pad); border-width: 1.5px 0 0; border-inline-start-width: 1.5px; }}
.corner.r {{ inset-inline-end: var(--pad); border-width: 1.5px 0 0; border-inline-end-width: 1.5px; }}
/* the batik sits behind the hero only and fades out over its last 30%; full strength, as rendered in Remotion (its
   own masks already dim the dots under the nav and the name) */
.bg-waves {{ position: absolute; top: 0; inset-inline-start: 0; width: 100%; z-index: -1; pointer-events: none;
  -webkit-mask-image: linear-gradient(#000 70%, transparent); mask-image: linear-gradient(#000 70%, transparent); }}
/* below 1024 the name sits under the nav and the lead mid-hero, out of reach of the masks made for a name along the
   bottom, so the dots stay at half strength there */
@media (max-width: 1023px) {{ .bg-waves {{ opacity: .5; }} }}
/* pause for the batik: a 30px ring in a 44px target under the right corner bracket; two bars, a triangle when paused
   (a play triangle points right in any direction, so it stays physical) */
.bg-pause {{ position: absolute; z-index: 2; top: 116px; inset-inline-end: calc(var(--pad) - 7px); width: 44px; height: 44px; padding: 0; border: 0;
  background: none; color: var(--muted); cursor: pointer; display: grid; place-items: center; scale: 1; }}
.bg-pause[hidden] {{ display: none; }}
.bg-pause::before {{ content: ""; grid-area: 1 / 1; box-sizing: border-box; width: 30px; height: 30px; border: 1px solid var(--line); border-radius: 50%; }}
.bg-pause::after {{ content: ""; grid-area: 1 / 1; width: 9px; height: 10px; box-sizing: border-box; border-inline: 3px solid currentColor; }}
.bg-pause[aria-pressed="true"]::after {{ width: 0; height: 0; margin-left: 3px; border: solid transparent; border-width: 5px 0 5px 9px; border-left-color: currentColor; }}
.bg-pause:hover, .bg-pause:focus-visible {{ color: var(--text); }} .bg-pause:hover::before {{ border-color: var(--muted); }}
/* the first viewport holds name, offer, both paths and the facts row; the facts sit on its bottom edge */
.hero {{ display: flex; flex-direction: column; min-height: min(100svh, 1080px); container-type: inline-size; }}
.intro {{ margin-top: auto; padding: 120px 0 56px; align-items: end; }}
/* sized by the hero's width so the name fits it on one line. A design choice, kept off the type rules' rem and 2.5x
   clamp: the name is display art sized to the container, not reading text */
h1 {{ grid-column: 1 / -1; font-weight: 600; font-size: min(13.6cqw, 192px); line-height: .9; letter-spacing: -.06em;
  white-space: nowrap; margin-inline-start: -.04em; }}
/* parallax, desktop only: the name lifts out a quarter faster than the page as the hero scrolls away, up to a quarter of
   the hero's height (min(100svh, 1080px) whenever its content fits). A scroll-driven animation, run by the compositor;
   where it isn't supported anim.js scrubs the same lift with GSAP. translate, so it adds to any transform on the h1 */
@media (prefers-reduced-motion: no-preference) and (min-width: 1024px) {{
  @supports ((animation-timeline: view()) and (animation-range: entry)) {{
    h1 {{ animation: lift linear both; animation-timeline: scroll(root); animation-range: 0 min(100svh, 1080px); }}
  }}
}}
@keyframes lift {{ to {{ translate: 0 calc(min(100svh, 1080px) * -.25); }} }}
.hero .lead {{ grid-column: 1 / 3; margin-top: clamp(32px, 5dvh, 56px); padding-inline-end: var(--gut);
  font-size: clamp(1.375rem, .18rem + 2vw, 2rem); line-height: 1.25; letter-spacing: -.03em; text-wrap: balance; }}
.hero .lead span:first-child {{ color: var(--text); display: block; }}   /* the focus line sits on its own line */
.paths {{ grid-column: 3 / 5; display: grid; grid-template-columns: 1fr 1fr; }}
.paths .cta {{ margin-inline-start: var(--gut); justify-self: start; white-space: nowrap; font-size: clamp(1rem, .25rem + 1.16vw, 1.25rem); }}
.cta.down::after {{ content: "↓"; content: "↓" / ""; }}
@media (prefers-reduced-motion: no-preference) {{ .cta.down:hover::after, .cta.down:focus-visible::after {{ transform: translateY(3px); }} }}
.facts {{ border-top: 1px solid var(--line); padding: 24px 0 36px; align-items: end; }}
.facts dl + dl {{ padding-inline-start: var(--gut); }} .facts dl:first-child {{ grid-column: 1 / 3; }}
.facts dt {{ font: .8125rem var(--mono); color: var(--muted); }} .facts dd {{ font-size: 1.125rem; letter-spacing: -.02em; }}
/* "vadh" in the name opens a GitHub card on hover (mouse only, so a tap on a phone just follows the link) or keyboard
   focus. It lingers .2s after the pointer leaves, so the pointer can cross the gap onto it (::before bridges it, above or below). */
/* the hint: an underline at 3:1 (--hint) that blinks twice like a cursor, once, soon after load (reduced motion: no
   blink). It's set on the SplitText char divs too, because decoration doesn't reach inline-blocks, and kept close to
   the baseline so the line masks don't clip it. */
.gh, .gh > div {{ text-decoration: underline var(--hint); text-decoration-thickness: .02em; text-underline-offset: .02em;
  transition: color .2s, text-decoration-color .2s; }}
/* one 9s cycle started 6.78s in, so the two blinks (92% to 98% = 8.28s to 8.82s) come 1.5s after load and it's over
   by 2.2s */
@media (prefers-reduced-motion: no-preference) {{ .gh, .gh > div {{ animation: gh-blink 9s -6.78s step-end; }} }}
@keyframes gh-blink {{ 0% {{ text-decoration-color: var(--hint); }} 92%, 96% {{ text-decoration-color: var(--muted); }}
  94%, 98% {{ text-decoration-color: var(--hint); }} }}
/* while the batik plays, the blink waits for it to enter and dim (waves() sets data-hint, "go" 1.5s after the
   entrance); "go" starts the cycle 8.1s in, so the blinks come 0.2s later and end 0.9s after it */
.hero[data-hint="wait"] .gh, .hero[data-hint="wait"] .gh > div {{ animation: none; }}
.hero[data-hint="go"] .gh, .hero[data-hint="go"] .gh > div {{ animation-delay: -8.1s; }}
.gh:hover, .gh:focus-visible {{ color: var(--pop); }}
.gh:hover, .gh:focus-visible, .gh:hover > div, .gh:focus-visible > div {{ text-decoration-color: currentColor; animation: none; }}
/* left/top stay physical: ghCard() sets them from getBoundingClientRect() */
.gh-card {{ position: absolute; z-index: 5; top: 0; left: 0; box-sizing: border-box; width: min(340px, 100%); padding: 20px;
  display: grid; gap: 16px; background: var(--card); border: 1px solid var(--line); border-radius: 6px;
  box-shadow: 0 24px 64px rgb(0 0 0 / .5); visibility: hidden; opacity: 0;
  transition: opacity .2s, transform .2s, visibility 0s .2s, border-color .2s; }}
@media (prefers-reduced-motion: no-preference) {{ .gh-card {{ transform: translateY(6px); }} }}
.gh-card::before {{ content: ""; position: absolute; inset: -16px 0; }}
.intro:has(.gh:focus-visible, .gh-card:hover) .gh-card:not(.off) {{ visibility: visible; opacity: 1; transform: none; transition-delay: 0s; }}
/* hover waits .15s, so a pointer passing over "vadh" (say, from the nav down to the CTAs) doesn't open the card */
@media (hover: hover) {{ .intro:has(.gh:hover) .gh-card:not(.off) {{ visibility: visible; opacity: 1; transform: none; transition-delay: .15s; }} }}
.gh-card:hover {{ border-color: var(--muted); }}
.gh-head {{ display: flex; justify-content: space-between; font: .75rem var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
.gh-head::after {{ content: "↗"; content: "↗" / ""; }}
@media (prefers-reduced-motion: no-preference) {{
  .gh-head::after {{ transition: transform .2s; }} .gh-card:hover .gh-head::after {{ transform: translate(2px, -2px); }}
}}
.gh-who {{ display: flex; gap: 14px; align-items: center; }}
.gh-who img {{ box-sizing: border-box; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); }}
.gh-who > span {{ display: grid; }}
.gh-who strong {{ font-weight: 600; font-size: 1.25rem; line-height: 1.3; letter-spacing: -.04em; }}
.gh-who .mono {{ font-size: .8125rem; color: var(--muted); }}
.gh-bio {{ font-size: .875rem; line-height: 1.43; letter-spacing: -.01em; color: var(--muted); }}
.gh-card dl {{ display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--line); padding-top: 14px; }}
.gh-card dl div + div {{ padding-inline-start: 14px; border-inline-start: 1px solid var(--line); }}
.gh-card dt {{ font: .75rem var(--mono); color: var(--muted); }} .gh-card dd {{ font-size: 1.125rem; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }}

/* work */
.work-body {{ margin-top: 70px; align-items: start; }}
.cards {{ grid-column: 2 / 5; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.cards > li {{ display: grid; }}   /* the card fills its row, so the bottom hairlines line up */
.card {{ position: relative; padding: 30px var(--gut) 30px; border-bottom: 1px solid var(--line); }}
.idx {{ display: block; text-align: end; margin-bottom: 12px; font: .8125rem var(--mono); color: var(--muted); }}
.cover {{ box-sizing: border-box; aspect-ratio: 16 / 10; overflow: clip; background: var(--card); border: 1px solid var(--line); border-radius: 6px;
  transition: border-color .2s; }}
.cover img {{ display: block; width: 100%; height: 100%; object-fit: cover; filter: brightness(.88); transition: filter .2s; }}
.cover.ph {{ display: grid; place-items: center; font-weight: 600; font-size: 2rem; letter-spacing: -.04em; color: var(--muted);
  background: repeating-linear-gradient(135deg, var(--card) 0 10px, var(--stripe) 10px 20px); }}
.card h3, .job h3 {{ font-weight: 600; font-size: 1.25rem; line-height: 1.3; letter-spacing: -.04em; transition: color .2s; }}
.card h3 {{ margin-top: 24px; }}
/* :has(:focus-visible), not :focus-within, so a mouse click on a card link doesn't leave the card lit afterwards */
.card:hover h3, .card:has(:focus-visible) h3 {{ color: var(--white); }}
.card:hover .cover, .card:has(:focus-visible) .cover {{ border-color: var(--muted); }}
.card:hover .cover img, .card:has(:focus-visible) .cover img {{ filter: none; }}
.card .meta-line, p.meta {{ font: .75rem var(--mono); letter-spacing: .08em; color: var(--muted); margin: 4px 0 10px; }}
.body {{ font-size: .875rem; line-height: 1.43; color: var(--muted); letter-spacing: -.01em; }}
.hl {{ font-variant-numeric: tabular-nums; font-size: .8125rem; line-height: 1.4; margin-top: 10px; }}
.tags {{ font: .75rem/1.5 var(--mono); margin-top: 8px; }}
.link {{ display: inline-block; font: .75rem var(--mono); color: var(--muted); margin-top: 4px; }}
.link:hover, .title:hover, .link:focus-visible, .title:focus-visible {{ color: var(--text); }}
.links-row {{ display: flex; flex-wrap: wrap; gap: 0 18px; }} .link.live {{ color: var(--text); }}
.more {{ margin-top: 120px; }}
.more h3 {{ font-weight: 600; font-size: 2rem; letter-spacing: -.04em; }}
.more .count {{ font-size: .875rem; color: var(--muted); margin-bottom: 24px; }}
.rows .row {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--line); padding: 13px 0; }}
.rows .row:last-child {{ border-bottom: 1px solid var(--line); }}
.rows .row > .c1 {{ font-size: .75rem; color: var(--muted); padding-top: 3px; }}
.rows .row > .c2 {{ padding-inline-start: 21px; }}
.rows .row > .c34 {{ font-size: .875rem; color: var(--muted); padding-top: 1px; }}
.more .cta {{ margin-top: 56px; }}

/* experience */
.exp-head {{ align-items: start; }} .exp-head .lead {{ grid-column: 3 / 5; padding: 18px 0 0; padding-inline-start: var(--gut); }}
.jobs {{ margin-top: 72px; }}
.jobs .row.job {{ padding: 30px 0; }}
.dates {{ font-size: .875rem; }} .type {{ font-size: .75rem; letter-spacing: .08em; color: var(--muted); margin-top: 6px; }}
.job .c2 {{ padding-inline-start: 21px; }}
.job .logo {{ display: grid; place-items: center; box-sizing: border-box; width: 44px; height: 44px; margin-bottom: 16px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--card); object-fit: cover; font-weight: 600; font-size: .875rem; letter-spacing: -.02em; color: var(--muted); }}
.job .logos {{ display: flex; gap: 8px; }}
.job img.logo {{ padding: 0; opacity: .8; transition: opacity .2s; }} .job:hover img.logo, .job:has(:focus-visible) img.logo {{ opacity: 1; }}
.company {{ margin-top: 6px; }} .loc {{ font-size: .875rem; color: var(--muted); }}
.job .body {{ font-size: 1rem; line-height: 1.5; }} .job .hl {{ font-size: .875rem; }} .job .tags {{ color: var(--muted); }}

/* about */
.about-body {{ margin-top: 80px; align-items: start; }}
.who {{ grid-column: 1 / 3; }}
.who dl {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 18px; }}
.who dt, .who dd {{ border-top: 1px solid var(--line); padding: 12px 0; }}
.who dt {{ font-size: .875rem; color: var(--muted); }} .who dd {{ padding-inline-start: 21px; font-size: .9375rem; letter-spacing: -.01em; }}
.who dl > :nth-last-child(-n+2) {{ border-bottom: 1px solid var(--line); }}
.who .label {{ margin: 0; }}
.prose {{ display: grid; gap: 30px; padding-top: 34px; }}
.prose p {{ font-size: 1.25rem; line-height: 1.5; letter-spacing: -.01em; color: var(--muted); max-width: 620px; }}

/* contact */
.contact-body {{ align-items: start; }}
.contact-body .left {{ grid-column: 1 / 3; }}
.email {{ display: inline-block; margin-top: 70px; font-size: 2rem; letter-spacing: -.03em; }}
/* the 2px underline is a pseudo-element, so it can draw in (GSAP tweens --u) and retract to the left on hover or focus
   like the CTA's; a border, not a background, so it still prints. Hover only where hover is real: a tap opens Mail.
   .drawing holds off the transition while GSAP draws an underline in, so it doesn't chase the tween */
.email::after {{ content: ""; display: block; border-top: 2px solid var(--white); transform: scaleX(var(--u, 1));
  transform-origin: left; }}
@media (prefers-reduced-motion: no-preference) {{ .email::after {{ transition: transform .3s; }} }}
.email.drawing::after, .cta.drawing::before {{ transition: none; }}
.email:focus-visible::after {{ transform: scaleX(0); }}
@media (hover: hover) {{ .email:hover::after {{ transform: scaleX(0); }} }}
.offer {{ margin-top: 22px; font-size: 1.125rem; color: var(--muted); letter-spacing: -.01em; max-width: 520px; }}
.links {{ grid-column: 3 / 5; padding-top: 30px; }}
.links li {{ border-top: 1px solid var(--line); background: var(--bg); }}
.links li:last-child {{ border-bottom: 1px solid var(--line); }}
.links a {{ display: grid; grid-template-columns: 1fr 1fr; padding: 22px 0; padding-inline-start: var(--gut); align-items: baseline; }}
.links strong {{ font-weight: 600; font-size: 1.25rem; letter-spacing: -.04em; }}
.links a > span {{ font: .875rem var(--mono); color: var(--muted); padding-inline-start: var(--gut); }}
.links a:hover span, .links a:focus-visible span {{ color: var(--text); }}
footer > .wrap {{ border-top: 1px solid var(--line); }}
footer .grid {{ padding: 30px 0 40px; font: .8125rem var(--mono); color: var(--muted); }}
footer .c4 {{ grid-column: 4; padding-inline-start: 0; }}
footer a:hover, footer a:focus-visible {{ color: var(--text); }}
/* the flower closes the page (inside the footer landmark): a screen of it past the footer's text, fading in from the ground, with no text on it. The wheel
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
  /* the collapse itself (every grid child across, no gutter) is in @layer overrides, at the end */
  section.wrap {{ padding-top: 48px; padding-bottom: 64px; }}
  .nav {{ grid-template-columns: 1fr auto; }} .nav ul {{ display: none; }}
  .corner {{ top: 72px; }}
  .hero {{ min-height: 0; }}
  .intro {{ padding: 112px 0 40px; }}
  /* each word about the container's width, at every width below 1024 (design choice, see the h1 rule above) */
  h1 {{ font-size: 25.5cqw; line-height: .88; white-space: normal; }}
  .hero .lead {{ margin-top: 28px; padding-inline-end: 0; font-size: 1.25rem; line-height: 1.3; }}
  .paths {{ display: flex; flex-wrap: wrap; gap: 14px 32px; margin-top: 32px; }}
  .paths .cta {{ margin: 0; min-width: 0; font-size: 1.125rem; padding-bottom: 10px; }}
  .facts {{ padding: 0 0 48px; border-top: 0; }}
  .facts > dl {{ display: grid; grid-template-columns: 120px 1fr; border-top: 1px solid var(--line); padding: 12px 0; }}
  .facts > dl:last-child {{ border-bottom: 1px solid var(--line); }}
  .work-body {{ margin-top: 28px; }} .cards {{ margin-top: 32px; border-top: 1px solid var(--line); }}
  .card {{ padding: 24px 0; }} .card h3 {{ margin-top: 20px; }}
  .more {{ margin-top: 48px; }} .more h3 {{ font-size: 1.625rem; }}
  .rows .row {{ gap: 4px; padding: 14px 0; }}
  .exp-head .lead {{ padding: 20px 0 0; }} .jobs {{ margin-top: 32px; }}
  .job .c1 {{ display: flex; justify-content: space-between; align-items: baseline; }} .type {{ margin: 0; }}
  .job .c2 {{ margin: 12px 0; }} .job .body {{ font-size: .9375rem; }}
  .about-body {{ margin-top: 20px; }} .prose {{ order: -1; padding: 0 0 32px; gap: 18px; }} .prose p {{ font-size: 1.0625rem; }}
  .who dl {{ grid-template-columns: 100px minmax(0, 1fr); }} .who dd {{ padding-inline-start: 0; }}
  .email {{ margin-top: 36px; font-size: 1.5rem; }} .offer {{ font-size: 1rem; }}
  .links {{ padding-top: 40px; }} .links a {{ padding-inline-start: 0; }} .links a > span {{ text-align: end; }}
  footer .grid {{ gap: 6px; }}
  .email {{ padding-top: 6px; margin-top: 30px; }}   /* a ~40px target, like the 32px email above 1024 */
}}
/* ~44px hit areas for thumbs, on phones and on any coarse pointer; padding and negative margin cancel out, so the
   rhythm doesn't move */
@media (max-width: 1023px), (pointer: coarse) {{
  .link {{ padding: 14px 0; margin: -10px 0 -14px; }}
  .rows .title {{ padding: 12px 0; }}
  footer a {{ justify-self: start; padding: 13px 0; margin: -13px 0; }}
  .nav a {{ padding: 11px 0; margin: -11px 0; }}
  .paths .cta {{ padding-top: 8px; margin-top: -8px; }}
}}
/* hidden until the GSAP intro starts; the class only exists while JS runs with motion allowed */
.js h1, .js .intro .lead, .js .paths, .js .facts > *, .js .corner {{ visibility: hidden; }} .js .wrap {{ --rule: 0; }}
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
}}

/* below 1024px every grid child spans the one column with no gutter, whatever its component placed it at */
@layer overrides {{ @media (max-width: 1023px) {{
  .grid > *, .rows .row > *, .cards {{ grid-column: 1 / -1; padding-inline-start: 0; }}
  .grid > .gh-card {{ padding-inline-start: 20px; }}
  .nav .logo {{ grid-column: 1; }} .nav .go {{ grid-column: 2; }}
}} }}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<canvas class="bg-waves" aria-hidden="true"></canvas>
<header class="wrap hero">
  <nav class="grid nav" aria-label="Main">
    <a class="logo" href="#top">vadhh</a>
    <ul><li><a href="#work">Work</a></li><li><a href="#experience">Experience</a></li><li><a href="#about">About</a></li><li><a href="#contact">Contact</a></li></ul>
    <a class="go" href="{mailto}">Start a project<span aria-hidden="true"> ↗</span></a>
  </nav>
  <span class="corner l" aria-hidden="true"></span><span class="corner r" aria-hidden="true"></span>
  <button class="bg-pause" type="button" aria-label="Pause background animation" aria-pressed="false" hidden></button>
  <div class="grid intro" id="top" tabindex="-1">
    <h1>Afridho Ta<a class="gh" href="{e(links["GitHub"])}" target="_blank" rel="noopener" aria-label="vadh" aria-describedby="gh-card">vadh</a>u</h1>
    {gh_card(links["GitHub"])}
    <p class="lead">{"".join(f'<span>{e(x)}</span> ' for x in LEAD.split(chr(10)))}</p>
    <div class="paths"><a class="cta" href="{mailto}">Start a project</a><a class="cta down" href="#work">See selected work</a></div>
  </div>
  <div class="grid facts">
    {"".join(f'<dl><dt>{e(k)}</dt><dd>{e(v)}</dd></dl>' for k, v in META)}
  </div>
</header>

<main id="main" tabindex="-1">
<section class="wrap" id="work" tabindex="-1">
  <p class="label">01 / Work</p>
  <h2>Selected<br>work</h2>
  <div class="grid work-body">
    <p class="lead c1">{br(WORK_LEAD)}</p>
    <ul class="cards" role="list">{"".join(card(i + 1, p) for i, p in enumerate(featured))}</ul>
  </div>
  <div class="more">
    <h3>More projects</h3>
    <p class="count">{len(rest)} more on GitHub</p>
    <ul class="rows" role="list">{"".join(more_row(p) for p in rest)}</ul>
    <a class="cta" href="https://github.com/vadhh?tab=repositories" target="_blank" rel="noopener">All repositories on GitHub{NEW_TAB}</a>
  </div>
</section>

<section class="wrap" id="experience" tabindex="-1">
  <div class="grid exp-head">
    <div class="c12"><p class="label">02 / Experience</p><h2>Where I've<br>worked</h2></div>
    <p class="lead">{br(EXPERIENCE_LEAD)}</p>
  </div>
  <ul class="rows jobs" role="list">{"".join(job(r) for r in jobs())}</ul>
</section>

<section class="wrap" id="about" tabindex="-1">
  <p class="label">03 / About</p>
  <h2 class="m">{br(ABOUT_HEADING)}</h2>
  <div class="grid about-body">
    <div class="who"><p class="label">~/whoami</p><dl>{"".join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in WHOAMI)}</dl></div>
    <div class="c34 prose">{"".join(f'<p>{e(b)}</p>' for b in ABOUT_BODY)}</div>
  </div>
</section>

<section class="wrap" id="contact" tabindex="-1">
  <div class="grid contact-body">
    <div class="left">
      <p class="label">04 / Contact</p>
      <h2 class="xl" id="contact-h">Let's build <br>something.</h2>
      <a class="email" href="{mailto}">{e(EMAIL)}</a>
      <p class="offer">{br(OFFER)}</p>
    </div>
    <ul class="links" role="list">{"".join(f'<li><a href="{e(links[k])}" target="_blank" rel="noopener"><strong>{e(k)}</strong><span>{e(v)}  {ARROW}</span>{NEW_TAB}</a></li>' for k, v in LINKS)}</ul>
  </div>
</section>
</main>

<footer>
  <div class="wrap"><div class="grid"><span class="c1">© 2026 Afridho Tavadhu</span><span class="c2">Batik: Gringsing Lidah Api Padma, photo <a href="https://www.instagram.com/katalogsuminarkediri/">@katalogsuminarkediri</a></span><span class="c4">Built by hand, no frameworks</span></div></div>
  <div class="flower-end">
    <img src="{END_FLOWER[1]}" alt="" width="1920" height="1080" loading="lazy" decoding="async">
    <canvas data-src="{END_FLOWER[0]}" aria-hidden="true"></canvas>
    <span class="third"></span>
    <button class="bg-pause" type="button" aria-label="Pause flower animation" aria-pressed="false" hidden></button>
  </div>
</footer>
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
body, h1, h2, h3, p, ul { margin: 0; }
body { background: var(--bg); color: var(--text); font: 1.0625rem/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
a { color: inherit; }
:focus-visible { outline: 2px solid var(--white); outline-offset: 3px; }
.skip { position: absolute; top: 12px; inset-inline-start: var(--pad); padding: 13px 16px; font: .8125rem var(--mono); background: var(--bg);
  border: 1px solid var(--line); transform: translateY(-200%); } .skip:focus { transform: none; }
.wrap { box-sizing: border-box; max-width: 1440px; margin: 0 auto; padding-inline: var(--pad); }
nav, footer { display: flex; justify-content: space-between; gap: 24px; padding-block: 30px; font-size: .875rem; }
nav a, footer a { text-decoration: none; color: var(--muted); } nav .logo { color: var(--text); font-weight: 600; font-size: 1rem; }
nav a:hover, nav a:focus-visible, footer a:hover, footer a:focus-visible { color: var(--text); }
footer { border-top: 1px solid var(--line); color: var(--muted); }
article { max-width: 760px; padding-block: 80px 120px; }
.label { font: .8125rem var(--mono); letter-spacing: .04em; color: var(--muted); margin-bottom: 14px; text-transform: uppercase; }
h1 { font-weight: 600; font-size: clamp(2.25rem, .25rem + 4.69vw, 4rem); line-height: 1.04; letter-spacing: -.05em; text-wrap: balance; }
.lede { font-size: clamp(1.1875rem, .25rem + 1.47vw, 1.375rem); line-height: 1.45; margin-top: 32px; }
h2 { font-weight: 600; font-size: 1.75rem; line-height: 1.15; letter-spacing: -.03em; margin-top: 72px; padding-top: 24px;
  border-top: 1px solid var(--line); }
h3 { font-weight: 600; font-size: 1.125rem; margin-top: 36px; }
p, ul, .tbl { margin-top: 18px; }
ul { padding-inline-start: 1.2em; } li + li { margin-top: 8px; }
code { font: .88em var(--mono); }
/* tables fit the column (tighter cells on phones); each sits in a box that scrolls sideways only if it must, see
   case_page() */
.tbl { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .875rem; line-height: 1.45; }
caption { caption-side: top; text-align: start; padding-bottom: 12px; font: .8125rem var(--mono); color: var(--muted); }
th, td { text-align: start; vertical-align: top; padding: 12px 0; padding-inline-end: 20px; border-bottom: 1px solid var(--line); }
th { font: .75rem var(--mono); letter-spacing: .04em; color: var(--muted); text-transform: uppercase; }
@media (min-width: 1024px) { article { margin-inline-start: 25%; } }
@media (max-width: 640px) { :root { --pad: 20px; } article { padding-block: 48px 80px; } h2 { margin-top: 56px; }
  th, td { padding-inline-end: 12px; } }
@media print { :root { --bg: #fff; --text: #000; --muted: #444; --line: #bbb; --white: #000; color-scheme: light; }
  nav, footer { display: none; } article { margin: 0; max-width: none; padding: 0; } }
"""


def case_page(body, p):
    title = re.search(r"<h1>(.*?)</h1>", body).group(1)
    lede = re.sub(r"<[^>]+>", "", re.search(r'<p class="lede">(.*?)</p>', body, re.S).group(1))
    # each table sits in a .tbl box that scrolls sideways if it has to. They all fit a 320px phone except one whose
    # caption has an id: that one must scroll there, so its box is a region named by the caption and takes focus, so
    # the keyboard can scroll it
    body = re.sub(r'<table>(\s*<caption id="([^"]+)")?', lambda m: (f'<div class="tbl" role="region" aria-labelledby="{m[2]}" tabindex="0">'
                  if m[2] else '<div class="tbl">') + m[0], body).replace("</table>", "</table></div>")
    return f"""<!doctype html>
<!-- Generated by design-ref/build_html.py from content/cases/. Edit the fragment there, then re-run. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{title} · Afridho Tavadhu</title>
<meta name="description" content="{e(lede)}">
{ICON}
{FONT_PRELOADS}
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
<main class="wrap" id="main" tabindex="-1">
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
