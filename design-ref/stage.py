"""Copy the public site into public/: the pages plus every local file they reference, nothing else.

design-ref/, content/ and unreferenced images never ship (design-ref holds crops of a third-party screenshot).
Run after build_html.py. Preview with: python3 -m http.server -d public 8000
"""
import base64
import hashlib
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
PAGES = ("index.html", "about.html", "snake.html", *sorted(p.name for p in ROOT.glob("case-*.html")))   # + case studies
EXTRA = ("fonts/OFL.txt",)   # font licence travels with the fonts
REF = re.compile(r'''(?:src|href|poster)="([^"]+)"|url\(['"]?([^'")]+)|srcset="([^"]+)"''')
INLINE_JS = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)


def local_refs(html):
    for m in REF.finditer(html):
        refs = [c.split()[0] for c in m.group(3).split(",") if c.strip()] if m.group(3) else [m.group(1) or m.group(2)]
        for ref in refs:
            ref = ref.split("#")[0].split("?")[0]
            if ref and ":" not in ref and not ref.startswith("//"):   # skips http(s):, mailto:, data:
                yield ref


def with_csp(html):
    """Add a hash-based script-src (the security guide's CSP for static HTML) for this page's own inline scripts.
    'self' admits the same-origin vendor <script src defer> tags; frame-ancestors and the other headers are in vercel.json.
    ponytail: no 'strict-dynamic' or report-to: it would block those parser-inserted tags, and there is no report endpoint."""
    hashes = ["'sha256-%s'" % base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() for s in INLINE_JS.findall(html)]
    src = " ".join((["'self'"] if re.search(r"<script[^>]*\bsrc=", html) else []) + hashes) or "'none'"
    charset, first_script = re.search(r"<meta charset[^>]*>", html, re.I), html.find("<script")
    assert charset and "Content-Security-Policy" not in html and (first_script == -1 or charset.start() < first_script)
    meta = f'<meta http-equiv="Content-Security-Policy" content="script-src {src}; object-src \'none\'; base-uri \'none\'">'
    return html[:charset.end()] + "\n" + meta + html[charset.end():]


def main():
    assert list(local_refs('<img srcset="img/a.webp 180w, img/b.webp 2x" src="x.jpg">')) == ["img/a.webp", "img/b.webp", "x.jpg"]
    files = set(PAGES) | set(EXTRA)
    for page in PAGES:
        files |= set(local_refs((ROOT / page).read_text()))
    missing = sorted(f for f in files if not (ROOT / f).is_file())
    assert not missing, f"referenced but missing: {missing}"
    shutil.rmtree(OUT, ignore_errors=True)
    for f in sorted(files):
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        if f in PAGES:
            (OUT / f).write_text(with_csp((ROOT / f).read_text()))
        else:
            shutil.copy2(ROOT / f, OUT / f)
    print(f"staged {len(files)} files in {OUT.name}/")


if __name__ == "__main__":
    main()
