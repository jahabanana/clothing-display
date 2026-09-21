#!/usr/bin/env python3
"""
Erzeugt icon-180.png aus dem T-Shirt-Icon (A-12, §11.3):
T-Shirt-Pixel-Art x5 (160 px), mittig auf #FAF7F0, 180x180, ohne Transparenz.
Einmaliger Handgriff, zur Laufzeit nicht benutzt.

Aufruf: python3 tools/gen_icon.py
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "clothes" / "t-shirt_blau_32x32.svg"
OUT = ROOT / "icon-180.png"

PIXEL_PATH = re.compile(
    r'<path d="M([\d.]+) ([\d.]+)H([\d.]+)V([\d.]+)H[\d.]+V[\d.]+Z" fill="(#[0-9A-Fa-f]{6})"/>'
)

BG = "#FAF7F0"
SCALE = 5
CANVAS = 180
ART = 32 * SCALE  # 160
OFFSET = (CANVAS - ART) // 2  # 10


def main():
    src = SRC.read_text()
    img = Image.new("RGB", (CANVAS, CANVAS), BG)
    draw = ImageDraw.Draw(img)

    for x2u, y1u, x1u, y2u, color in PIXEL_PATH.findall(src):
        x1, y1 = int(float(x1u)) // 20, int(float(y1u)) // 20
        x2, y2 = int(float(x2u)) // 20, int(float(y2u)) // 20
        px1 = OFFSET + x1 * SCALE
        py1 = OFFSET + y1 * SCALE
        px2 = OFFSET + x2 * SCALE
        py2 = OFFSET + y2 * SCALE
        draw.rectangle([px1, py1, px2 - 1, py2 - 1], fill=color)

    img.save(OUT)
    print(f"geschrieben: {OUT.relative_to(ROOT)} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
