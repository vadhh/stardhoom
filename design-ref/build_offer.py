"""Build the 'What I can offer' section (DESIGN.md) in a running FigCraft via its control channel."""
import json, socket, sys

REF = "/Users/st4rdhoom/stardhoom/design-ref"
BG, LINE, TEXT, MUTED, WHITE = "#141414", "#262626", "#F2F2F2", "#8C8C8C", "#FFFFFF"

sock = socket.create_connection(("127.0.0.1", 9123))
io = sock.makefile("rw")
seq = 0


def ex(command, **params):
    global seq
    seq += 1
    io.write(json.dumps({"id": seq, "method": "engine.execute", "params": {"command": command, "params": params}}) + "\n")
    io.flush()
    r = json.loads(io.readline())
    if not r.get("ok"):
        sys.exit(f"{command} failed: {r.get('error')}\n{params}")
    return r["result"]


def text(parent, s, x, y, size, color, style="Regular", width=None, lh=None, ls="0%", align="left", name=None):
    p = dict(text=s, x=x, y=y, parent=parent,
             props=dict(fontFamily="Inter", fontStyle=style, fontSize=size, fills=[color],
                        letterSpacing=ls, textAlign=align, **({"lineHeight": lh} if lh else {}),
                        **({"name": name} if name else {})))
    if width:
        p["width"] = width
    return ex("text.create", **p)["id"]


def rect(parent, x, y, w, h, color, name):
    return ex("node.create", type="rectangle", parent=parent, x=x, y=y, width=w, height=h, name=name,
              props={"fills": [color]})["id"]


def image(parent, file, x, y, w, h, radius=0, name=None):
    i = ex("image.place", path=f"{REF}/{file}", x=x, y=y, width=w, height=h, parent=parent, mode="fill")["id"]
    ex("node.set", ids=[i], props={"cornerRadius": radius, "name": name or file})
    return i


io.write(json.dumps({"id": 0, "method": "document.inspect", "params": {"depth": 1}}) + "\n"); io.flush()
page = json.loads(io.readline())["result"]
olds = [n["id"] for pg in page["pages"] for n in pg.get("children", []) if n.get("name", "").startswith("What I can offer")]
if olds:
    ex("edit.delete", ids=olds)
root = ex("node.create", type="frame", name="What I can offer — 1440", x=0, y=0, width=1440, height=1120,
          props={"fills": [BG], "clip": True})["id"]

# portrait first so the text sits on top of it
image(root, "portrait.png", 2, 432, 611, 605, name="Portrait")
for y, h, a, b in ((432, 140, BG, BG + "00"), (917, 120, BG + "00", BG)):
    ex("node.create", type="rectangle", parent=root, x=0, y=y, width=620, height=h, name="Portrait fade",
       props={"fills": [{"type": "linearGradient", "stops": [a, b], "from": [0.5, 0], "to": [0.5, 1]}]})
ex("node.create", type="rectangle", parent=root, x=473, y=432, width=142, height=605, name="Portrait fade",
   props={"fills": [{"type": "linearGradient", "stops": [BG + "00", BG], "from": [0, 0.5], "to": [1, 0.5]}]})

for x in (379, 719, 1058):
    rect(root, x, 0, 1, 1120, LINE, "Column rule")

for x, path in ((39, "M0 13 V0 H13"), (1385, "M0 0 H13 V13")):
    ex("node.create", type="vector", parent=root, x=x, y=40, width=13, height=13, path=path, name="Corner",
       props={"fill": "none", "stroke": WHITE, "strokeWeight": 1.5})

text(root, "What I can offer", 39, 195, 80, TEXT, "SemiBold", lh=88, ls="-6%", name="Heading")
text(root, "I provide a range of photography\nservices, capturing moments\nthat matter most to you.",
     39, 325, 24, MUTED, lh=32, ls="-2%", name="Lead")
text(root, "Check out my work", 39, 1052, 20, TEXT, lh=26, ls="-2%", name="CTA")
text(root, "↗", 250, 1052, 20, TEXT, lh=26, name="CTA arrow")
rect(root, 39, 1094, 228, 2, WHITE, "CTA underline")

CARDS = [
    ("01", "Professional Headshots", "Stand out with a polished,\nprofessional look.", 719, 202),
    ("02", "Events", "Your day, your story—\ncaptured beautifully.", 719, 421),
    ("03", "Weddings", "From the first look to the final\ndance, you'll relive every moment.", 719, 640),
    ("04", "Portrait Photography", "Capture your best self with\nbeautifully composed portraits.", 1058, 421),
    ("05", "Family Sessions", "Celebrate your family's unique\nbond with heartwarming photos.", 1058, 640),
    ("06", "Lifestyle Photography", "Showcase the authentic\nmoments of your daily life\nwith story-driven images.", 1058, 859),
]
W = 339
for num, title, body, cx, cy in CARDS:
    h = 239 if num == "06" else 219
    card = ex("node.create", type="frame", parent=root, x=cx, y=cy, width=W, height=h, name=f"Card {num}",
              props={"fill": "none", "strokes": [LINE], "strokeWeight": 1, "strokeSides": [False, False, True, False]})["id"]
    image(card, f"thumb{num}.png", 30, 30, 58, 58, radius=6, name="Thumb")
    text(card, num, W - 30 - 60, 37, 14, MUTED, width=60, lh=20, align="right", name="Index")
    text(card, title, 30, 122, 20, TEXT, "SemiBold", lh=26, ls="-4%", name="Title")
    text(card, body, 30, 152, 14, MUTED, lh=20, ls="-1%", name="Body")

ex("view.zoomFit")
print("built frame", root)
