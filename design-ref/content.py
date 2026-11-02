"""Page copy and the content sheets, shared by the FigCraft builds and the HTML generator. No I/O at import."""
import csv
from datetime import date
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "content"

# ── copy shared by every layout ("\n" is a desktop line break; narrow layouts join it with a space) ──
LEAD = "I build AI features and web apps that hold up\nin production, from first prototype to launch."
WORK_LEAD = "Things I've shipped\nat work, for clients\nand for myself."
EXPERIENCE_LEAD = "Jobs, internships and programs.\nClient work is in Work, above."
ABOUT_HEADING = "Models die in notebooks.\nI build products."
ABOUT_BODY = (
    "I build AI systems and the software around them. At ATASK I run a pipeline that turns educational "
    "material into practice questions. At Sydeco I lead product engineering on security platforms, "
    "including an AI behavioral firewall.",
    "I graduated with a B.Eng in Informatics from Universitas Stikubank in October 2026. On the side I build "
    "web apps for clients, from a kids' wellbeing app to a retail point-of-sale system.",
)
WHOAMI = (("Location", "Yogyakarta, ID"), ("Education", "B.Eng Informatics, Univ. Stikubank (2026)"),
          ("Languages", "Python, TypeScript, SQL, Bash"), ("AI & data", "Scikit-Learn, TensorFlow, LangChain"),
          ("Web", "Next.js, React, Vue.js, FastAPI"), ("Tools", "Docker, MLflow, GitHub Actions"))
META = (("Based in", "Yogyakarta, Indonesia"), ("Education", "B.Eng Informatics, 2026"),
        ("Freelance", "One project at a time"))
OFFER = "I take one freelance project at a time: AI features and\nweb apps, from first prototype to launch."
EMAIL = "attridho@gmail.com"
LINKS = (("GitHub", "/vadhh"), ("LinkedIn", "/afr1dho"))
ASCII_LOGO = """██████╗ ██╗  ██╗ ██████╗  ██████╗ ███╗   ███╗
██╔══██╗██║  ██║██╔═══██╗██╔═══██╗████╗ ████║
██║  ██║███████║██║   ██║██║   ██║██╔████╔██║
██║  ██║██╔══██║██║   ██║██║   ██║██║╚██╔╝██║
██████╔╝██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝"""


def flat(s):
    return s.replace("\n", " ")


# ── content sheets ────────────────────────────────────────────────────────────
def sheet(name):
    return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(open(CONTENT / f"{name}.csv"))
            if (r.get("title") or r.get("role") or "").strip()]


def projects():
    """(featured, rest): `show` = featured picks the cards (else the first six not archived), `no` hides a row."""
    shown = sorted((p for p in sheet("projects") if p["show"].lower() != "no"), key=lambda p: int(p["order"] or 999))
    featured = [p for p in shown if p["show"].lower() == "featured"][:6] or \
               [p for p in shown if p["status"] != "ARCHIVED"][:6]
    rest = sorted((p for p in shown if p not in featured), key=lambda p: p["year"], reverse=True)
    return featured, rest


def jobs():
    """Experience rows newest first. Freelance rows stay in the sheet but show under Work instead."""
    return sorted((r for r in sheet("experience") if r["type"] != "Freelance"),
                  key=lambda r: (r["start"], r["type"] == "Full-time"), reverse=True)


def month(s):
    if s.lower() == "present":
        return "Present"
    parts = s.split("-")
    return date(int(parts[0]), int(parts[1]), 1).strftime("%b %Y") if len(parts) == 2 else s


def span(r):
    return month(r["start"]) if r["start"] == r["end"] else f"{month(r['start'])} to {month(r['end'])}"


def tags(stack, n=None):
    return " · ".join([t.strip() for t in stack.split(";") if t.strip()][:n])


def bare(url):
    return url.removeprefix("https://").removeprefix("http://").removeprefix("www.").rstrip("/")


def link_label(url):
    return "GitHub ↗" if "github.com" in url else bare(url) + " ↗"


def card_meta(p):
    return " · ".join(v for v in (p["status"], p["kind"].upper(), p["year"][:4]) if v)
