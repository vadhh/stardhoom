"""Shared pieces for the FigCraft build scripts: the control-channel client, drawing helpers, page copy
and the content sheets. Needs FigCraft running with `--control 9123`."""
import json, socket, sys

from content import *

BG, LINE, TEXT, MUTED, WHITE, CARD = "#141414", "#262626", "#F2F2F2", "#8C8C8C", "#FFFFFF", "#1B1B1B"
MONO = "FiraCode Nerd Font Mono"

# ── control channel ───────────────────────────────────────────────────────────
sock = socket.create_connection(("127.0.0.1", 9123))
io = sock.makefile("rw")
seq = 0


def call(method, params):
    global seq
    seq += 1
    io.write(json.dumps({"id": seq, "method": method, "params": params}) + "\n")
    io.flush()
    r = json.loads(io.readline())
    if not r.get("ok"):
        sys.exit(f"{method} failed: {r.get('error')}\n{params}")
    return r["result"]


def ex(command, **params):
    return call("engine.execute", {"command": command, "params": params})


def height(node):
    return call("node.get", {"id": node})["height"]


def replace_frame(prefix, name, x, width):
    """Delete earlier top-level frames whose name starts with `prefix`, then create a fresh one."""
    doc = call("document.inspect", {"depth": 1})
    olds = [n["id"] for pg in doc["pages"] for n in pg.get("children", []) if n.get("name", "").startswith(prefix)]
    if olds:
        ex("edit.delete", ids=olds)
    return ex("node.create", type="frame", name=name, x=x, y=0, width=width, height=1000,
              props={"fills": [BG], "clip": True})["id"]


# ── drawing ───────────────────────────────────────────────────────────────────
def text(parent, s, x, y, size, color=TEXT, style="Regular", width=None, lh=None, ls="0%", align="left",
         family="Inter", name=None):
    props = dict(fontFamily=family, fontStyle=style, fontSize=size, fills=[color], letterSpacing=ls, textAlign=align)
    if lh:
        props["lineHeight"] = lh
    if name:
        props["name"] = name
    p = dict(text=s, x=x, y=y, parent=parent, props=props)
    if width:
        p["width"] = width
    return ex("text.create", **p)["id"]


def oneline(parent, s, x, y, size, width, color=MUTED, family=MONO, name=None):
    """Single-line text cut off with an ellipsis at `width`."""
    t = text(parent, s, x, y, size, color, family=family, width=width, name=name)
    ex("node.set", ids=[t], props={"textAutoResize": "truncate", "height": round(size * 1.35)})
    return t


def rect(parent, x, y, w, h, fill, name, **props):
    return ex("node.create", type="rectangle", parent=parent, x=x, y=y, width=w, height=h, name=name,
              props={"fills": [fill], **props})["id"]


def frame(parent, x, y, w, h, name, **props):
    return ex("node.create", type="frame", parent=parent, x=x, y=y, width=w, height=h, name=name,
              props={"fill": "none", **props})["id"]


def hline(parent, x, y, w):
    rect(parent, x, y, w, 1, LINE, "Divider")


def bracket(parent, x, y, right=False):
    ex("node.create", type="vector", parent=parent, x=x, y=y, width=13, height=13, name="Corner",
       path="M0 0 H13 V13" if right else "M0 13 V0 H13",
       props={"fill": "none", "stroke": WHITE, "strokeWeight": 1.5})
