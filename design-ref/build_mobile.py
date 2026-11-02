"""Build the portfolio's phone layout (390 wide) next to the desktop frame, from the same copy and sheets.

Run FigCraft with `--control 9123`, then `python3 design-ref/build_mobile.py`. Re-running replaces the frame.
Single column, 20px margins; horizontal hairlines only (vertical column rules would cut through text here).
"""
from fc import *

W, M = 390, 20
CW = W - 2 * M
ORIGIN_X = 1600 + 1440 + 160  # right of the desktop frame

root = replace_frame("Portfolio — 390", "Portfolio — 390", ORIGIN_X, W)
y = 0


def t(s, size, color=TEXT, style="Regular", x=M, width=CW, lh=None, ls="0%", family="Inter", name=None, at=None):
    """Wrapped text at the running cursor (or at `at`); returns its height."""
    node = text(root, s, x, y if at is None else at, size, color, style, width=width, lh=lh, ls=ls,
                family=family, name=name)
    return height(node)


def gap(n):
    global y
    y += n


def label(num, title):
    gap(t(f"{num} / {title}", 12, MUTED, family=MONO, ls="4%", name="Section label") + 12)


def heading(s, size=48):
    gap(t(s, size, TEXT, "SemiBold", lh=round(size * 1.05), ls="-5%", name="Heading") + 20)


def rule():
    hline(root, 0, y, W)


def cta(s, width=CW):
    t(s, 18, TEXT, lh=24, ls="-2%", name="CTA")
    text(root, "↗", M + width - 14, y, 18, TEXT, lh=24, name="CTA arrow")
    rect(root, M, y + 34, width, 2, WHITE, "CTA underline")
    gap(36)


# ── hero ──────────────────────────────────────────────────────────────────────
text(root, "vadhh", M, 24, 16, TEXT, "SemiBold", ls="-2%", name="Logo")
text(root, "Start a project ↗", M, 26, 14, TEXT, width=CW, align="right", name="Nav CTA")
bracket(root, M, 72)
bracket(root, W - M - 13, 72, right=True)
gap(110)
gap(t(ASCII_LOGO, 8, "#2E2E2E", family=MONO, lh=10, name="ASCII mark") + 14)
gap(t("DHOOM@vadhh:~$ whoami", 12, MUTED, family=MONO, name="Prompt") + 2)
gap(t("full-stack · AI · security", 12, TEXT, family=MONO, name="Prompt output") + 48)
gap(t("Afridho\nTavadhu", 76, TEXT, "SemiBold", lh=72, ls="-6%", name="Name") + 20)
gap(t(flat(LEAD), 18, MUTED, lh=26, ls="-2%", name="Lead") + 32)
for k, v in META:
    rule()
    t(k, 11, MUTED, family=MONO, name=f"Meta {k}", at=y + 14)
    t(v, 15, TEXT, x=140, width=W - 140 - M, ls="-1%", name=f"Meta {k} value", at=y + 12)
    gap(44)
rule()
gap(32)
cta("Start a project")
gap(4)
gap(64)

# ── work ──────────────────────────────────────────────────────────────────────
featured, rest = projects()
rule()
gap(48)
label("01", "Work")
heading("Selected work")
gap(t(flat(WORK_LEAD), 18, MUTED, lh=26, ls="-2%", name="Lead") + 32)
for i, p in enumerate(featured):
    rule()
    top = y
    rect(root, M, y + 24, 48, 48, CARD, "Thumb", cornerRadius=6, strokes=[LINE], strokeWeight=1)
    text(root, p["monogram"], M, y + 38, 16, TEXT, "SemiBold", width=48, align="center", ls="-4%", name="Monogram")
    text(root, f"{i + 1:02}", W - M - 40, y + 28, 12, MUTED, family=MONO, width=40, align="right", name="Index")
    gap(92)
    gap(t(p["title"], 20, TEXT, "SemiBold", lh=26, ls="-4%", name="Title") + 4)
    gap(t(card_meta(p), 11, MUTED, family=MONO, ls="8%", name="Meta") + 10)
    if p["summary"]:
        gap(t(p["summary"], 15, MUTED, lh=22, ls="-1%", name="Body") + 10)
    if p["highlight"]:
        gap(t("↳ " + p["highlight"], 14, TEXT, lh=20, name="Highlight") + 8)
    gap(t(tags(p["stack"], 3), 12, TEXT, family=MONO, name="Tags") + 4)
    if p["repo"]:
        gap(t(link_label(p["repo"]), 12, MUTED, family=MONO, name="Link") + 4)
    gap(24)
rule()
gap(48)
gap(t("More projects", 26, TEXT, "SemiBold", lh=32, ls="-4%", name="More heading") + 4)
gap(t(f"{len(rest)} more on GitHub", 14, MUTED, name="More count") + 20)
for p in rest:
    rule()
    gap(14)
    gap(t(" · ".join(v for v in (p["year"][:4], p["kind"].upper()) if v), 11, MUTED, family=MONO, name="Year") + 4)
    gap(t(p["title"] + (" ↗" if p["repo"] else ""), 16, TEXT, ls="-1%", name="Title") + 4)
    if p["summary"]:
        gap(t(p["summary"], 14, MUTED, lh=20, ls="-1%", name="Summary"))
    gap(14)
rule()
gap(32)
cta("All repositories on GitHub")
gap(64)

# ── experience ────────────────────────────────────────────────────────────────
rule()
gap(48)
label("02", "Experience")
heading("Where I've worked")
gap(t(flat(EXPERIENCE_LEAD), 18, MUTED, lh=26, ls="-2%", name="Lead") + 32)
for r in jobs():
    rule()
    gap(22)
    t(span(r), 12, TEXT, family=MONO, name="Dates")
    text(root, r["type"].upper(), M, y + 2, 10, MUTED, family=MONO, ls="8%", width=CW, align="right", name="Type")
    gap(26)
    gap(t(r["role"], 20, TEXT, "SemiBold", lh=26, ls="-4%", name="Role") + 4)
    gap(t(r["company"], 15, TEXT, ls="-1%", name="Company") + 2)
    if r["location"]:
        gap(t(r["location"], 13, MUTED, name="Location"))
    gap(12)
    gap(t(r["summary"], 15, MUTED, lh=22, ls="-1%", name="Summary") + 10)
    if r["highlight"]:
        gap(t("↳ " + r["highlight"], 14, TEXT, lh=20, name="Highlight") + 8)
    if r["stack"]:
        gap(t(tags(r["stack"]), 12, MUTED, family=MONO, lh=18, name="Stack") + 4)
    if r["link"]:
        gap(t(bare(r["link"]) + " ↗", 12, MUTED, family=MONO, name="Link") + 4)
    gap(22)
rule()
gap(64)

# ── about ─────────────────────────────────────────────────────────────────────
rule()
gap(48)
label("03", "About")
heading(flat(ABOUT_HEADING), 36)
for b in ABOUT_BODY:
    gap(t(b, 17, MUTED, lh=26, ls="-1%", name="Body") + 18)
gap(14)
gap(t("~/whoami", 12, MUTED, family=MONO, name="whoami label") + 12)
for k, v in WHOAMI:
    rule()
    t(k, 13, MUTED, name=f"{k} key", at=y + 13)
    h = t(v, 14, TEXT, x=120, width=W - 120 - M, lh=20, ls="-1%", name=f"{k} value", at=y + 12)
    gap(max(44, h + 24))
rule()
gap(64)

# ── contact ───────────────────────────────────────────────────────────────────
rule()
gap(48)
label("04", "Contact")
heading("Let's build\nsomething.", 56)
gap(t(EMAIL, 24, TEXT, ls="-3%", name="Email") + 6)
rect(root, M, y, 224, 2, WHITE, "Email underline")
gap(18)
gap(t(flat(OFFER), 16, MUTED, lh=24, ls="-1%", name="Email note") + 32)
for k, v in LINKS:
    rule()
    t(k, 18, TEXT, "SemiBold", ls="-4%", name=f"{k} link", at=y + 20)
    text(root, f"{v}  ↗", M, y + 24, 13, MUTED, family=MONO, width=CW, align="right", name=f"{k} handle")
    gap(64)
rule()
gap(48)
rule()
gap(20)
gap(t("© 2026 Afridho Tavadhu", 12, MUTED, family=MONO, name="Footer left") + 6)
gap(t("Bored? Play snake ↗", 12, MUTED, family=MONO, name="Footer snake") + 6)
gap(t("Built by hand, no frameworks", 12, MUTED, family=MONO, name="Footer right") + 28)

ex("node.set", ids=[root], props={"height": y})
print(root)
