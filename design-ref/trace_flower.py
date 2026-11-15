# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""The closing screen's flower: a reel's halftone (64 x 36 squares on a ~20px grid, 79 frames at 15 fps) traced cell by
cell into img/footer-flower.png, which the page draws as glass tiles (endFlower() in build_html.py). Offline, not part of
the build; the reel is third-party and stays out of the repo.
Run: uv run design-ref/trace_flower.py <reel.mp4>

Per cell and frame: the side of its bright square's bounding box (0-16 px) and whether it is filled (lit) or a hollow
outline (the reel's ground). Measured on the reel: pitch 19.94 x 20.00 px from (0, 0); filled squares are 8-16 px, hollow
ones 1-7 px (their fill share of side^2 is ~0.5, the filled ones' ~0.99); under 7 px counts as hollow, as the smallest fill their box.
PNG layout: frames left to right, 8 to a row, each 64 x 36 px; R = side * 16 (clamped to 255), G = 255 if filled.
"""
import subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

W, H, NX, NY, PER_ROW = 1276, 720, 64, 36, 8
OUT = Path(__file__).resolve().parent.parent / "img/footer-flower.png"

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                     capture_output=True, check=True).stdout
lit = np.frombuffer(raw, np.uint8).reshape(-1, H, W) > 76          # 0.3 of white
n = len(lit)
side = np.zeros((n, NY, NX)); filled = np.zeros((n, NY, NX), bool)
for j in range(NY):
    y0, y1 = round(j * H / NY), round((j + 1) * H / NY)
    for i in range(NX):
        x0, x1 = round(i * W / NX), round((i + 1) * W / NX)
        c = lit[:, y0:y1, x0:x1]
        rows, cols = c.any(2), c.any(1)
        span = lambda m: np.where(m.any(1), m.shape[1] - np.argmax(m[:, ::-1], 1) - np.argmax(m, 1), 0)
        s = (span(rows) + span(cols)) / 2
        side[:, j, i] = s
        filled[:, j, i] = (s >= 7) & (c.sum((1, 2)) > 0.8 * s ** 2)   # a 1-6 px square fills its box too: hollow
assert side.max() <= 17, f"a cell spans two squares (side {side.max()}): the grid moved"
sheet = np.zeros((-(-n // PER_ROW) * NY, PER_ROW * NX, 3), np.uint8)
for k in range(n):
    y, x = k // PER_ROW * NY, k % PER_ROW * NX
    sheet[y:y + NY, x:x + NX, 0] = np.clip(side[k] * 16, 0, 255)
    sheet[y:y + NY, x:x + NX, 1] = filled[k] * 255
Image.fromarray(sheet).save(OUT, optimize=True)
print(f"wrote {OUT.relative_to(OUT.parent.parent)}: {n} frames, {sheet.shape[1]}x{sheet.shape[0]}, "
      f"{OUT.stat().st_size // 1024} KB; filled share {filled.mean():.2f}")
