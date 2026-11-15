"""Pack remotion/dots.json (the Gringsing Lidah Api Padma batik as stipple dots, from remotion/extract_dots.py) into
img/batik-dots.bin, the hero's WebGL dot buffer. Run `python3 design-ref/pack_dots.py` after re-extracting the dots.

8 bytes a dot, little-endian, read straight into one GL buffer:
  u16 x, u16 y   position in the source photo, 0..1
  u16 r          radius / R_MAX (0..1), the photo's own dot size
  u8  tone       pigmentTone() from remotion/src/batikDots.ts, 0..1
  u8  flags      1 = dark fill (lum < 0.42, gets the inner breath), 2 = highlight (tone >= 0.68, swells more)
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "remotion" / "dots.json", ROOT / "img" / "batik-dots.bin"
R_MAX = 0.01   # every extracted radius is under 0.002 of the tile


def pigment(hex_color):
    """(tone, lum): the photo's pigment as a monochrome weight, as pigmentTone() in batikDots.ts."""
    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    t = min(1.0, max(0.0, (lum - 0.2) / 0.74))
    tone = 0.2 + 0.78 * t ** 1.3
    if lum < 0.42:   # lift the deep crimson and dark foliage fills so they read on #141414
        tone = max(tone, 0.27 + 0.08 * t)
    return tone, lum


def main():
    dots = json.loads(SRC.read_text())
    out = bytearray()
    for d in dots:
        assert 0 <= d["x"] <= 1 and 0 <= d["y"] <= 1 and 0 < d["r"] < R_MAX, d
        tone, lum = pigment(d["color"])
        flags = (lum < 0.42) | (tone >= 0.68) << 1
        out += struct.pack("<HHHBB", round(d["x"] * 65535), round(d["y"] * 65535), round(d["r"] / R_MAX * 65535),
                           round(tone * 255), flags)
    assert len(out) == 8 * len(dots) > 0
    OUT.write_bytes(out)
    print(f"wrote {OUT} ({len(dots)} dots, {len(out) // 1024} KB)")


if __name__ == "__main__":
    main()
