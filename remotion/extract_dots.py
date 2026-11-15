"""Extract normalized dot data (dots.json & dots-tile.json) directly from batik pixels
and render a Phase 3 side-by-side verification image.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC_IMAGE = Path(
    "/Users/st4rdhoom/.agy-acct2/.gemini/antigravity-cli/brain/"
    "7fc77932-6b75-467c-9450-832345c44478/.user_uploaded/"
    "uploaded_media_1794159489458.jpg"
)
OUT_DIR = Path(__file__).resolve().parent
DOTS_JSON = OUT_DIR / "dots.json"
TILE_JSON = OUT_DIR / "dots-tile.json"
COMPARE_PNG = Path(
    "/Users/st4rdhoom/.agy-acct2/.gemini/antigravity-cli/brain/"
    "7fc77932-6b75-467c-9450-832345c44478/phase3_comparison.png"
)

# Measured primary repeat unit bounds in source pixels (1872x1720):
# Horizontally spans from bottom-left to bottom-right Lidah Api centers (~1808px)
# Vertically spans from top-left lower flame lobe to bottom-left crown (~1564px).
TILE_BOX = (32, 113, 1840, 1677)


def estimate_local_background(arr: np.ndarray, grid_n: int = 12) -> np.ndarray:
    """Estimate smooth local sogan-brown cloth background across fold/shadow gradients."""
    h, w, _ = arr.shape
    coarse = np.zeros((grid_n, grid_n, 3), dtype=np.float32)
    prior = np.array([164.0, 100.0, 64.0], dtype=np.float32)

    for gy in range(grid_n):
        y0 = (gy * h) // grid_n
        y1 = ((gy + 1) * h) // grid_n
        for gx in range(grid_n):
            x0 = (gx * w) // grid_n
            x1 = ((gx + 1) * w) // grid_n
            patch = arr[y0:y1, x0:x1].reshape(-1, 3)
            dist_prior = np.linalg.norm(patch - prior, axis=1)
            mask = dist_prior < 42.0
            coarse[gy, gx] = np.median(patch[mask], axis=0) if mask.sum() > 80 else prior

    coarse_img = Image.fromarray(np.clip(coarse, 0, 255).astype(np.uint8), mode="RGB")
    bg_full = coarse_img.resize((w, h), Image.Resampling.BILINEAR)
    return np.asarray(bg_full, dtype=np.float32)


def rgb_to_hex(rgb: np.ndarray) -> str:
    r, g, b = (int(np.clip(round(v), 0, 255)) for v in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_dots(
    arr: np.ndarray,
    bg: np.ndarray,
    grid_step: int = 9,
    edge_spacing: float = 7.5,
) -> list[dict[str, float | str]]:
    """Extract dots purely from image pixel measurements:
    - PASS A (LINEWORK): bright klowong/ukel wax ridges & sharp motif boundaries
      thinned via non-maximum suppression and sampled cleanly every ~edge_spacing px.
    - PASS B (HALFTONE): staggered cell grid over non-background filled motif parts
      (Gringsing pearl dots, crimson Lidah Api, green Padma leaves, ochre foliage).
    """
    h, w, _ = arr.shape
    max_dim = float(max(w, h))

    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    bg_lum = 0.299 * bg[:, :, 0] + 0.587 * bg[:, :, 1] + 0.114 * bg[:, :, 2]

    lum_img = Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8), mode="L")
    smooth_lum = np.asarray(lum_img.filter(ImageFilter.GaussianBlur(radius=1.1)), dtype=np.float32)
    local_mean = np.asarray(lum_img.filter(ImageFilter.GaussianBlur(radius=6.0)), dtype=np.float32)
    # Bright fine-line ridge response (captures pale klowong strokes over crimson/green/brown!)
    bright_ridge = smooth_lum - local_mean

    gx = np.zeros_like(smooth_lum)
    gy = np.zeros_like(smooth_lum)
    gx[:, 1:-1] = (smooth_lum[:, 2:] - smooth_lum[:, :-2]) * 0.5
    gy[1:-1, :] = (smooth_lum[2:, :] - smooth_lum[:-2, :]) * 0.5
    grad = np.hypot(gx, gy)

    lum_diff = lum - bg_lum
    # Warm tan/ochre foliage & vine lift over sogan brown
    warm_lift = (arr[:, :, 0] - bg[:, :, 0]) * 0.35 + (arr[:, :, 1] - bg[:, :, 1]) * 0.65
    # Crimson Lidah Api score
    crimson_score = np.clip((arr[:, :, 0] - arr[:, :, 1]) - 64.0, 0, 80) * np.clip(
        (82.0 - arr[:, :, 1]) / 32.0, 0, 1
    )
    # Green lotus/leaf score
    green_score = np.clip((arr[:, :, 1] - arr[:, :, 0] + 10.0) * 3.0, 0, 90) * np.clip(
        (arr[:, :, 1] - arr[:, :, 2] - 18.0) / 24.0, 0, 1
    )

    dots: list[dict[str, float | str]] = []
    occupied = np.zeros((h, w), dtype=bool)
    occ_pad = max(3, int(round(edge_spacing * 0.54)))

    # --- PASS A: LINEWORK (combined sharp gradient edges + fine bright klowong ridges) ---
    # Combines thin pale outline ridges (bright inside dark crimson/green) with motif edges
    edge_signal = np.maximum(grad, np.clip(bright_ridge * 1.45, 0, 85))
    ang = np.arctan2(gy, gx) * (180.0 / math.pi)
    ang[ang < 0] += 180.0

    q = np.zeros_like(edge_signal)
    r = np.zeros_like(edge_signal)
    dir0 = (ang < 22.5) | (ang >= 157.5)
    dir45 = (ang >= 22.5) & (ang < 67.5)
    dir90 = (ang >= 67.5) & (ang < 112.5)
    dir135 = (ang >= 112.5) & (ang < 157.5)

    q[:, 1:-1] = np.where(dir0[:, 1:-1], edge_signal[:, 2:], q[:, 1:-1])
    r[:, 1:-1] = np.where(dir0[:, 1:-1], edge_signal[:, :-2], r[:, 1:-1])
    q[1:-1, 1:-1] = np.where(dir90[1:-1, 1:-1], edge_signal[2:, 1:-1], q[1:-1, 1:-1])
    r[1:-1, 1:-1] = np.where(dir90[1:-1, 1:-1], edge_signal[:-2, 1:-1], r[1:-1, 1:-1])
    q[1:-1, 1:-1] = np.where(dir45[1:-1, 1:-1], edge_signal[2:, 2:], q[1:-1, 1:-1])
    r[1:-1, 1:-1] = np.where(dir45[1:-1, 1:-1], edge_signal[:-2, :-2], r[1:-1, 1:-1])
    q[1:-1, 1:-1] = np.where(dir135[1:-1, 1:-1], edge_signal[2:, :-2], q[1:-1, 1:-1])
    r[1:-1, 1:-1] = np.where(dir135[1:-1, 1:-1], edge_signal[:-2, 2:], r[1:-1, 1:-1])

    # Require strong edge OR clear bright/chromatic foreground contrast (suppresses pure brown cloth folds)
    fg_signal = np.maximum.reduce(
        [
            np.clip(bright_ridge, 0, 60),
            np.clip(warm_lift, 0, 60),
            crimson_score,
            green_score,
        ]
    )
    is_ridge = (edge_signal >= q) & (edge_signal >= r) & (edge_signal > 21.0) & (fg_signal > 12.0)

    ry, rx = np.where(is_ridge)
    strengths = edge_signal[ry, rx]
    order = np.argsort(-strengths)

    for idx in order:
        py = int(ry[idx])
        px = int(rx[idx])
        if py < 2 or py >= h - 2 or px < 2 or px >= w - 2:
            continue
        if occupied[py, px]:
            continue

        sig = float(edge_signal[py, px])
        # Sample brightest pigment pixel in 3x3 when tracing bright outline ridges
        # (preserves crisp ivory ukel outlines inside red Lidah Api and green leaves)
        win = arr[py - 1 : py + 2, px - 1 : px + 2]
        wlum = lum[py - 1 : py + 2, px - 1 : px + 2]
        if bright_ridge[py, px] > 6.0 or wlum.max() > bg_lum[py, px] + 18.0:
            best_i = int(np.argmax(wlum))
            color_rgb = win.reshape(-1, 3)[best_i]
        else:
            wbg = bg[py, px]
            wd = np.linalg.norm(win - wbg, axis=2)
            best_i = int(np.argmax(wd))
            color_rgb = win.reshape(-1, 3)[best_i]

        strength_norm = min(1.0, (sig - 21.0) / 36.0)
        dot_r_px = 1.9 + 1.5 * strength_norm
        dots.append(
            {
                "x": round(px / w, 5),
                "y": round(py / h, 5),
                "r": round(dot_r_px / max_dim, 5),
                "color": rgb_to_hex(color_rgb),
            }
        )
        y0 = max(0, py - occ_pad)
        y1 = min(h, py + occ_pad + 1)
        x0 = max(0, px - occ_pad)
        x1 = min(w, px + occ_pad + 1)
        occupied[y0:y1, x0:x1] = True

    # --- PASS B: HALFTONE GRID across non-background interior fills & pearls ---
    half = grid_step // 2
    for row_idx, cy in enumerate(range(half, h - half, grid_step)):
        x_off = half if (row_idx & 1) else 0
        for cx in range(half + x_off, w - half, grid_step):
            if occupied[cy, cx]:
                continue

            c_patch = arr[cy - 2 : cy + 3, cx - 2 : cx + 3]
            mean_rgb = c_patch.mean(axis=(0, 1))
            l_diff = float(lum_diff[cy - 2 : cy + 3, cx - 2 : cx + 3].mean())
            w_lift = float(warm_lift[cy - 2 : cy + 3, cx - 2 : cx + 3].mean())
            crim = float(crimson_score[cy - 2 : cy + 3, cx - 2 : cx + 3].mean())
            grn = float(green_score[cy - 2 : cy + 3, cx - 2 : cx + 3].mean())

            strength = 0.0
            if l_diff > 20.0:
                strength = max(strength, min(1.0, (l_diff - 18.0) / 88.0))
            if w_lift > 19.0:
                strength = max(strength, min(0.82, (w_lift - 17.0) / 68.0))
            if crim > 7.0:
                strength = max(strength, 0.56 + 0.44 * min(1.0, crim / 28.0))
            if grn > 15.0:
                strength = max(strength, 0.48 + 0.44 * min(1.0, grn / 42.0))

            if strength < 0.22:
                continue

            dot_r_px = 1.65 + 2.75 * strength
            dots.append(
                {
                    "x": round(cx / w, 5),
                    "y": round(cy / h, 5),
                    "r": round(dot_r_px / max_dim, 5),
                    "color": rgb_to_hex(mean_rgb),
                }
            )

    return dots


def crop_tile_dots(
    dots: list[dict[str, float | str]], w: int, h: int, box: tuple[int, int, int, int]
) -> list[dict[str, float | str]]:
    x0, y0, x1, y1 = box
    tw = float(x1 - x0)
    th = float(y1 - y0)
    full_max = float(max(w, h))
    tile_max = float(max(tw, th))
    scale_r = full_max / tile_max

    tiled: list[dict[str, float | str]] = []
    for d in dots:
        px = float(d["x"]) * w
        py = float(d["y"]) * h
        if x0 <= px <= x1 and y0 <= py <= y1:
            tiled.append(
                {
                    "x": round((px - x0) / tw, 5),
                    "y": round((py - y0) / th, 5),
                    "r": round(float(d["r"]) * scale_r, 5),
                    "color": d["color"],
                }
            )
    return tiled


def render_comparison(
    orig_img: Image.Image, dots: list[dict[str, float | str]], out_path: Path
) -> None:
    w, h = orig_img.size
    pw = int(w * 0.5)
    ph = int(h * 0.5)
    pad = 24
    header = 56
    canvas = Image.new("RGB", (pw * 2 + pad * 3, ph + header + pad), (20, 20, 20))

    left = orig_img.resize((pw, ph), Image.Resampling.LANCZOS)
    canvas.paste(left, (pad, header))

    right = Image.new("RGB", (pw, ph), (20, 20, 20))
    draw = ImageDraw.Draw(right)
    max_p = float(max(pw, ph))

    for d in dots:
        cx = float(d["x"]) * pw
        cy = float(d["y"]) * ph
        rad = max(0.85, float(d["r"]) * max_p)
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=str(d["color"]))

    canvas.paste(right, (pw + pad * 2, header))

    tdraw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    tdraw.text((pad, 20), f"Original Batik ({w}x{h})", fill=(242, 242, 242), font=font)
    tdraw.text(
        (pw + pad * 2, 20),
        f"Extracted Dots from dots.json ({len(dots):,} dots) on #141414",
        fill=(242, 242, 242),
        font=font,
    )
    canvas.save(out_path, format="PNG")


def main() -> None:
    orig_img = Image.open(SRC_IMAGE).convert("RGB")
    arr = np.asarray(orig_img, dtype=np.float32)
    h, w, _ = arr.shape

    bg = estimate_local_background(arr)
    dots = extract_dots(arr, bg, grid_step=9, edge_spacing=7.5)

    DOTS_JSON.write_text(json.dumps(dots), encoding="utf-8")
    tile_dots = crop_tile_dots(dots, w, h, TILE_BOX)
    TILE_JSON.write_text(json.dumps(tile_dots), encoding="utf-8")

    render_comparison(orig_img, dots, COMPARE_PNG)

    tw = TILE_BOX[2] - TILE_BOX[0]
    th = TILE_BOX[3] - TILE_BOX[1]
    print(f"Source image: {w}x{h}")
    print(f"Full dots.json count: {len(dots)} -> {DOTS_JSON}")
    print(f"Tile ({tw}x{th}) dots-tile.json count: {len(tile_dots)} -> {TILE_JSON}")
    print(f"Saved Phase 3 comparison: {COMPARE_PNG}")


if __name__ == "__main__":
    main()
