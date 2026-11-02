"""Build the full portfolio, desktop (1440), in the DESIGN.md style in a running FigCraft.

Experience and projects come from content/experience.csv and content/projects.csv, so updating the
site means editing a sheet and re-running this. Run FigCraft with `--control 9123`, then
`python3 design-ref/build_portfolio.py`. Re-running replaces the frame. The phone layout is build_mobile.py.
"""
from fc import *

W, COLS = 1440, (39, 379, 719, 1058)  # column starts; rules sit on the last three
ORIGIN_X = 1600  # to the right of the "What I can offer" frame


def corners(parent, y):
    bracket(parent, 39, y)
    bracket(parent, 1385, y, right=True)


def label(parent, num, title, y=120):
    text(parent, f"{num} / {title}", 39, y, 13, MUTED, family=MONO, ls="4%", name="Section label")


def heading(parent, s, size=72, y=150):
    return text(parent, s, 39, y, size, TEXT, "SemiBold", lh=round(size * 1.05), ls="-6%" if size > 80 else "-5%",
                name="Heading")


def cta(parent, s, x, y, width):
    text(parent, s, x, y, 20, TEXT, lh=26, ls="-2%", name="CTA")
    text(parent, "↗", x + width - 16, y, 20, TEXT, lh=26, name="CTA arrow")
    rect(parent, x, y + 42, width, 2, WHITE, "CTA underline")


# ── page ──────────────────────────────────────────────────────────────────────
root = replace_frame("Portfolio — 1440", "Portfolio — 1440", ORIGIN_X, W)
rules = [rect(root, x, 0, 1, 1000, LINE, "Column rule") for x in COLS[1:]]  # under everything
cursor = 0


def section(name, h=1000, rule=True):
    """A full-width section frame at the cursor; call done(frame, height) when its content is placed."""
    s = frame(root, 0, cursor, W, h, name, clip=True)
    if rule:
        hline(s, 0, 0, W)
    return s


def done(s, h):
    global cursor
    ex("node.set", ids=[s], props={"height": h})
    cursor += h


# ── hero ──────────────────────────────────────────────────────────────────────
s = section("Hero", rule=False)
text(s, "vadhh", 39, 34, 16, TEXT, "SemiBold", ls="-2%", name="Logo")
for x, item in zip((379, 549, 719, 889), ("Work", "Experience", "About", "Contact")):
    text(s, item, x, 34, 14, MUTED, name=f"Nav {item}")
text(s, "Start a project ↗", 1058, 34, 14, TEXT, name="Nav CTA")
corners(s, 96)

text(s, ASCII_LOGO, 760, 150, 18, "#2E2E2E", family=MONO, lh=21, name="ASCII mark")
text(s, "DHOOM@vadhh:~$ whoami", 760, 300, 13, MUTED, family=MONO, name="Prompt")
text(s, "full-stack · AI · security", 760, 320, 13, TEXT, family=MONO, name="Prompt output")

text(s, "Afridho\nTavadhu", 39, 330, 168, TEXT, "SemiBold", lh=156, ls="-6%", name="Name")
text(s, LEAD, 39, 660, 24, MUTED, lh=32, ls="-2%", name="Lead")

hline(s, 0, 780, W)
for x, (k, v) in zip(COLS, META):
    text(s, k, x, 806, 13, MUTED, family=MONO, name=f"Meta {k}")
    text(s, v, x, 830, 18, TEXT, ls="-2%", name=f"Meta {k} value")
cta(s, "Start a project", 1088, 816, 170)
done(s, 900)

# ── work (content/projects.csv) ───────────────────────────────────────────────
featured, rest = projects()

s = section("Work")
label(s, "01", "Work")
heading(s, "Selected\nwork", 96)
text(s, WORK_LEAD, 39, 420, 24, MUTED, lh=32, ls="-2%", name="Lead")

CW, PAD, BW = 339, 30, 279
cards = []
for i, p in enumerate(featured):  # build first, then size every card to the tallest one
    c = frame(s, 0, 0, CW, 300, f"Project {i + 1:02} {p['title']}",
              strokes=[LINE], strokeWeight=1, strokeSides=[False, False, True, False])
    rect(c, PAD, PAD, 58, 58, CARD, "Thumb", cornerRadius=6, strokes=[LINE], strokeWeight=1)
    text(c, p["monogram"], PAD, 48, 18, TEXT, "SemiBold", width=58, align="center", ls="-4%", name="Monogram")
    text(c, f"{i + 1:02}", CW - PAD - 40, 37, 13, MUTED, family=MONO, width=40, align="right", name="Index")
    t = text(c, p["title"], PAD, 122, 20, TEXT, "SemiBold", width=BW, lh=26, ls="-4%", name="Title")
    yy = 122 + height(t) + 4
    text(c, card_meta(p), PAD, yy, 11, MUTED, family=MONO, ls="8%", name="Meta")
    yy += 24
    if p["summary"]:
        b = text(c, p["summary"], PAD, yy, 14, MUTED, width=BW, lh=20, ls="-1%", name="Body")
        yy += height(b) + 10
    if p["highlight"]:
        text(c, "↳ " + p["highlight"], PAD, yy, 13, TEXT, width=BW, lh=18, name="Highlight")
        yy += 26
    oneline(c, tags(p["stack"], 3), PAD, yy, 12, BW, TEXT, name="Tags")
    if p["repo"]:
        oneline(c, link_label(p["repo"]), PAD, yy + 22, 12, BW, name="Link")
    cards.append((c, yy + 22 + 16 + PAD))
CH = max(h for _, h in cards)
for i, (c, _) in enumerate(cards):  # three per row across columns 2-4
    ex("node.set", ids=[c], props={"x": COLS[1 + i % 3], "y": 420 + i // 3 * CH, "height": CH})
grid_bottom = 420 + -(-len(cards) // 3) * CH

y = grid_bottom + 120
text(s, "More projects", 39, y, 32, TEXT, "SemiBold", lh=38, ls="-4%", name="More heading")
text(s, f"{len(rest)} more on GitHub", 39, y + 46, 14, MUTED, name="More count")
y += 100
for p in rest:
    rect(s, 720, y, 680, 48, BG, "Rule mask")  # the summary spans columns 3-4
    hline(s, 39, y, W - 78)
    text(s, " · ".join(v for v in (p["year"][:4], p["kind"].upper()) if v), 39, y + 16, 12, MUTED, family=MONO,
         name="Year")
    oneline(s, p["title"] + (" ↗" if p["repo"] else ""), 400, y + 13, 16, 300, TEXT, "Inter", name="Title")
    oneline(s, p["summary"], 749, y + 15, 14, 610, MUTED, "Inter", name="Summary")
    y += 48
hline(s, 39, y, W - 78)
cta(s, "All repositories on GitHub", 39, y + 60, 280)
done(s, y + 200)

# ── experience (content/experience.csv) ───────────────────────────────────────
s = section("Experience")
label(s, "02", "Experience")
heading(s, "Where I've\nworked", 96)
text(s, EXPERIENCE_LEAD, 749, 168, 24, MUTED, lh=32, ls="-2%", name="Lead")
y = 400
for r in jobs():
    row = frame(s, 0, y, W, 100, f"Job {r['company']}")
    mask = rect(row, 720, 0, 720, 100, BG, "Rule mask")  # the summary spans columns 3-4
    hline(row, 0, 0, W)
    text(row, span(r), 39, 32, 14, TEXT, family=MONO, name="Dates")
    text(row, r["type"].upper(), 39, 56, 11, MUTED, family=MONO, ls="8%", name="Type")
    role = text(row, r["role"], 400, 28, 20, TEXT, "SemiBold", width=290, lh=26, ls="-4%", name="Role")
    ry = 28 + height(role) + 6
    text(row, r["company"], 400, ry, 16, TEXT, ls="-1%", name="Company")
    left_h = ry + 24
    if r["location"]:
        text(row, r["location"], 400, ry + 24, 14, MUTED, name="Location")
        left_h += 22
    body = text(row, r["summary"], 749, 30, 16, MUTED, width=610, lh=24, ls="-1%", name="Summary")
    by = 30 + height(body) + 14
    if r["highlight"]:
        text(row, "↳ " + r["highlight"], 749, by, 14, TEXT, width=610, lh=20, name="Highlight")
        by += 28
    if r["stack"]:
        oneline(row, tags(r["stack"]), 749, by, 12, 610, name="Stack")
        by += 20
    if r["link"]:
        oneline(row, bare(r["link"]) + " ↗", 749, by, 12, 610, name="Link")
        by += 20
    h = max(left_h, by) + 32
    ex("node.set", ids=[row], props={"height": h})
    ex("node.set", ids=[mask], props={"height": h})
    y += h
hline(s, 0, y, W)
done(s, y + 80)

# ── about ─────────────────────────────────────────────────────────────────────
s = section("About")
label(s, "03", "About")
heading(s, ABOUT_HEADING)
text(s, ABOUT_BODY[0], 749, 380, 20, MUTED, width=620, lh=30, ls="-1%", name="Body 1")
text(s, ABOUT_BODY[1], 749, 560, 20, MUTED, width=620, lh=30, ls="-1%", name="Body 2")

text(s, "~/whoami", 39, 380, 13, MUTED, family=MONO, name="whoami label")
for i, (k, v) in enumerate(WHOAMI):
    ry = 412 + i * 44
    hline(s, 39, ry, 640)
    text(s, k, 39, ry + 13, 14, MUTED, name=f"{k} key")
    text(s, v, 400, ry + 12, 15, TEXT, ls="-1%", name=f"{k} value")
hline(s, 39, 412 + len(WHOAMI) * 44, 640)
done(s, max(412 + len(WHOAMI) * 44, 680) + 120)

# ── contact ───────────────────────────────────────────────────────────────────
s = section("Contact")
label(s, "04", "Contact")
heading(s, "Let's build\nsomething.", 120)
text(s, EMAIL, 39, 440, 32, TEXT, ls="-3%", name="Email")
rect(s, 39, 488, 300, 2, WHITE, "Email underline")
text(s, OFFER, 39, 512, 18, MUTED, ls="-1%", name="Email note")
for i, (k, v) in enumerate(LINKS):
    ly = 150 + i * 72
    hline(s, 719, ly, 679)
    text(s, k, 749, ly + 24, 20, TEXT, "SemiBold", lh=26, ls="-4%", name=f"{k} link")
    text(s, f"{v}  ↗", 1058 + 30, ly + 28, 14, MUTED, family=MONO, name=f"{k} handle")
hline(s, 719, 150 + len(LINKS) * 72, 679)
hline(s, 0, 700, W)
text(s, "© 2026 Afridho Tavadhu", 39, 732, 13, MUTED, family=MONO, name="Footer left")
text(s, "Bored? Play snake ↗", 719, 732, 13, MUTED, family=MONO, name="Footer snake")
text(s, "Built by hand, no frameworks", 1058, 732, 13, MUTED, family=MONO, name="Footer right")
done(s, 780)

ex("node.set", ids=[root], props={"height": cursor})
ex("node.set", ids=rules, props={"height": cursor})
ex("view.zoomFit")
print(root)
