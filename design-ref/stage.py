"""Copy the public site into public/: the pages plus every local file they reference, nothing else.

design-ref/, content/ and unreferenced images never ship (design-ref holds crops of a third-party screenshot).
Run after build_html.py. Preview with: python3 -m http.server -d public 8000
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
PAGES = ("index.html", "about.html", "snake.html")
EXTRA = ("fonts/OFL.txt",)   # font licence travels with the fonts
REF = re.compile(r'''(?:src|href)="([^"]+)"|url\(['"]?([^'")]+)''')


def local_refs(html):
    for m in REF.finditer(html):
        ref = (m.group(1) or m.group(2)).split("#")[0].split("?")[0]
        if ref and ":" not in ref and not ref.startswith("//"):   # skips http(s):, mailto:, data:
            yield ref


def main():
    files = set(PAGES) | set(EXTRA)
    for page in PAGES:
        files |= set(local_refs((ROOT / page).read_text()))
    missing = sorted(f for f in files if not (ROOT / f).is_file())
    assert not missing, f"referenced but missing: {missing}"
    shutil.rmtree(OUT, ignore_errors=True)
    for f in sorted(files):
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, OUT / f)
    print(f"staged {len(files)} files in {OUT.name}/")


if __name__ == "__main__":
    main()
