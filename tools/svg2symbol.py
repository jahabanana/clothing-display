#!/usr/bin/env python3
"""
Einmalige Asset-Konvertierung (Spec §12.1), zur Laufzeit nicht benutzt.

Liest die Quell-SVGs aus assets/clothes und assets/icons, wandelt sie in
<symbol>-Elemente nach §12 um und schreibt das komplette Sprite (inkl.
Platzhaltern nach §12.4) nach build/sprite.svg. Der Inhalt des <svg>-Tags
aus build/sprite.svg wird danach von Hand in index.html eingefügt.

Aufruf: python3 tools/svg2symbol.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOTHES = ROOT / "assets" / "clothes"
ICONS = ROOT / "assets" / "icons"
OUT = ROOT / "build" / "sprite.svg"

PIXEL_PATH = re.compile(
    r'<path d="M([\d.]+) ([\d.]+)H([\d.]+)V([\d.]+)H[\d.]+V[\d.]+Z" fill="(#[0-9A-Fa-f]{6})"/>'
)
GROUP_RECT = re.compile(r'<g id="[^"]*" fill="(#[0-9A-Fa-f]{6})">(.*?)</g>', re.S)
RECT = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="20" height="20"/>')

# Symbol-ID -> Quelldatei, Pixel-Art 32x32 (§12.2)
PIXEL_ICONS = [
    ("i-top-tshirt", "t-shirt_blau_32x32.svg"),
    ("i-top-longsleeve", "longsleeve_oliv-gestreift_32x32.svg"),
    ("i-top-strickjacke", "strickjacke_mauve_32x32.svg"),
    ("i-top-pullover", "pullover_gelb_32x32.svg"),
    ("i-top-kapuzenpullover", "kapuzenpullover_gelb_32x32.svg"),
    ("i-top-teddyjacke", "teddyjacke_creme_32x32.svg"),
    ("i-top-kapuzenjacke", "kapuzenjacke_pink_32x32.svg"),
    ("i-top-winterjacke", "winterjacke_rot_32x32.svg"),
    ("i-top-schneeanzug", "schneeanzug_blauviolett_32x32.svg"),
    ("i-bottom-hose-kurz", "hose-kurz_khaki_32x32.svg"),
    ("i-bottom-hose-lang", "hose-lang_denim_32x32.svg"),
    ("i-shoes-sandalen", "sandalen_orange_32x32.svg"),
    ("i-shoes-sneaker", "sneaker_weiss_32x32.svg"),
    ("i-shoes-gummistiefel", "gummistiefel_gelb_32x32.svg"),
    ("i-shoes-winterstiefel", "winterstiefel_braun_32x32.svg"),
    ("i-head-muetze", "muetze_rot_32x32.svg"),
    ("i-head-sonnenhut", "sonnenhut_stroh_32x32.svg"),
    ("i-acc-schal", "schal_petrol_32x32.svg"),
    ("i-acc-sonnenbrille", "sonnenbrille_koralle_32x32.svg"),
]

# Symbol-ID -> Quelldatei, Line-Icons 24x24 (§12.3)
LINE_ICONS = [
    ("i-wx-klar", "weather-icons-7.svg"),
    ("i-wx-klar-nacht", "weather-icons-4.svg"),
    ("i-wx-teilweise", "weather-icons-3.svg"),
    ("i-wx-bedeckt", "weather-icons.svg"),
    ("i-wx-niesel", "weather-icons-2.svg"),
    ("i-wx-regen", "weather-icons-1.svg"),
    ("i-wx-schnee", "weather-icons-5.svg"),
    ("i-hint-wind", "weather-icons-11.svg"),
]


def pixel_symbol(symbol_id, filename):
    src = (CLOTHES / filename).read_text()
    by_color = {}

    groups = GROUP_RECT.findall(src)
    if groups:
        # Format A: <g id="…" fill="#…"><rect x=".." y=".." width="20" height="20"/>…</g>
        for color, body in groups:
            color = color.lower()
            for xu, yu in RECT.findall(body):
                x, y = int(float(xu)) // 20, int(float(yu)) // 20
                by_color.setdefault(color, []).append((y, x, x + 1))
    else:
        # Format B: ein <path> pro Pixel, M x2 y1 H x1 V y2 H x2 V y1 Z
        for x2u, y1u, x1u, y2u, color in PIXEL_PATH.findall(src):
            x1, y1 = int(float(x1u)) // 20, int(float(y1u)) // 20
            x2 = int(float(x2u)) // 20
            by_color.setdefault(color.lower(), []).append((y1, x1, x2))

    parts = []
    for color, rects in by_color.items():
        by_row = {}
        for y, x1, x2 in rects:
            by_row.setdefault(y, []).append((x1, x2))

        d = []
        for y in sorted(by_row):
            runs = sorted(by_row[y])
            merged = []
            for x1, x2 in runs:
                if merged and merged[-1][1] == x1:
                    merged[-1] = (merged[-1][0], x2)
                else:
                    merged.append((x1, x2))
            for x1, x2 in merged:
                d.append(f"M{x2} {y}H{x1}V{y + 1}H{x2}V{y}Z")
        parts.append(f'<path d="{"".join(d)}" fill="{color}"/>')

    return f'<symbol id="{symbol_id}" viewBox="0 0 32 32">{"".join(parts)}</symbol>'


def line_symbol(symbol_id, filename):
    src = (ICONS / filename).read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1).strip()
    inner = inner.replace('stroke="black"', 'stroke="currentColor"')
    return f'<symbol id="{symbol_id}" viewBox="0 0 24 24">{inner}</symbol>'


# Platzhalter nach §12.4. Jede ⏳-ID existiert von Anfang an, data-placeholder
# markiert sie, damit ?test sie als Warnung listen kann (AC-19).
def placeholder_symbols():
    thermometer_inner = re.search(
        r"<svg[^>]*>(.*)</svg>", (ICONS / "weather-icons-9.svg").read_text(), re.S
    ).group(1).strip().replace('stroke="black"', 'stroke="currentColor"')

    return [
        '<symbol id="i-top-regenjacke" viewBox="0 0 32 32" data-placeholder>'
        '<use href="#i-top-kapuzenjacke"/></symbol>',

        '<symbol id="i-acc-handschuhe" viewBox="0 0 32 32" data-placeholder>'
        '<rect x="4" y="4" width="24" height="24" rx="3" fill="none" '
        'stroke="var(--ink-soft)" stroke-width="2" stroke-dasharray="4 3"/></symbol>',

        '<symbol id="i-acc-sonnencreme" viewBox="0 0 32 32" data-placeholder>'
        '<rect x="4" y="4" width="24" height="24" rx="3" fill="none" '
        'stroke="var(--ink-soft)" stroke-width="2" stroke-dasharray="4 3"/></symbol>',

        '<symbol id="i-wx-nebel" viewBox="0 0 24 24" data-placeholder>'
        '<use href="#i-wx-bedeckt"/></symbol>',

        '<symbol id="i-wx-gewitter" viewBox="0 0 24 24" data-placeholder>'
        '<use href="#i-wx-regen"/></symbol>',

        f'<symbol id="i-hint-glaette" viewBox="0 0 24 24" data-placeholder>{thermometer_inner}</symbol>',

        '<symbol id="i-sys-uhr" viewBox="0 0 24 24" data-placeholder>'
        '<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>'
        '<path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" fill="none"/></symbol>',

        '<symbol id="i-sys-fehler" viewBox="0 0 24 24" data-placeholder>'
        '<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>'
        '<path d="M12 7v6M12 17h.01" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" fill="none"/></symbol>',
    ]


def main():
    symbols = []
    for symbol_id, filename in PIXEL_ICONS:
        symbols.append(pixel_symbol(symbol_id, filename))
    for symbol_id, filename in LINE_ICONS:
        symbols.append(line_symbol(symbol_id, filename))
    symbols.extend(placeholder_symbols())

    sprite = '<svg style="display:none" aria-hidden="true">\n  ' + "\n  ".join(symbols) + "\n</svg>\n"

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(sprite)
    print(f"{len(symbols)} Symbole, {len(sprite.encode())} Bytes -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
