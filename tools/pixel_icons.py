#!/usr/bin/env python3
"""
Pixel-Icons zeichnen und ins Sprite von index.html schreiben (Spec §12.5).

Das Skript hat vier Aufgaben:
1. Die Wetter-, Hinweis- und System-Icons (16 x 16) stehen hier in Code
   (Rundungen und Konturen entstehen aus Formen, die Kontur ist der Rand).
   Wo ein Icon-Modul dasselbe Symbol liefert, gewinnt das Modul.
2. Die Kleidung, das Zubehör und die Bedienelemente kommen aus den Modulen
   tools/icons_schuhe_hosen.py, icons_oberteile.py und icons_kopf_zubehoer.py
   (handgezeichnete ASCII-Raster mit Farbvarianten, Funktion build()).
3. Alle Kleidungs-Symbole bekommen eine enge viewBox um ihren sichtbaren
   Inhalt, damit das Layout jedes Teil ohne Leerrand platzieren kann.
4. Die Symbole werden in das Sprite von index.html geschrieben. Vorhandene
   Symbole mit derselben ID werden ersetzt, neue am Ende des Sprites angefügt.

Das Skript ist idempotent. Aufruf: python3 tools/pixel_icons.py
Mit --preview <datei.html> entsteht zusätzlich eine Kontaktbogen-Seite.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

from pxl import N4, Canvas, ascii_mask, clip, disc, rect, shift, symbol  # noqa: E402


# ---------- Palette ----------

CLOUD = dict(fill="#fbfdff", outline="#7088a0", shade="#cddbe9")
CLOUD_GREY = dict(fill="#cfdae7", outline="#657d96", shade="#aebfd1")
CLOUD_DARK = dict(fill="#97a9bd", outline="#52667c", shade="#7d90a6")
SUN = dict(fill="#f8cd4e", outline="#d98a28", shade="#f0b13c")
SUN_RAY = "#f2a63a"
DROP = "#5aa0e0"
DROP_LIGHT = "#8cc3f0"
SNOW = "#5f9fe0"
SNOW_CORE = "#cfe6fa"
BOLT = "#f7c93a"
BOLT_EDGE = "#d9922a"


# ---------- Wetter (16 x 16) ----------

def cloud_mask(ox, oy, scale=1.0):
    """Wolke mit drei Wölbungen und flachem Boden, Box ca. 14 x 9."""
    s = scale
    m = set()
    m |= disc(ox + 3.3 * s, oy + 5.9 * s, 2.7 * s)
    m |= disc(ox + 7.3 * s, oy + 4.2 * s, 3.7 * s)
    m |= disc(ox + 11.0 * s, oy + 5.7 * s, 2.9 * s)
    m |= rect(int(ox + 3 * s), int(oy + 6 * s), int(9 * s), int(3 * s))
    return clip(m, y1=int(oy + 8 * s))


def draw_cloud(cv, ox, oy, pal, scale=1.0):
    cv.paint(cloud_mask(ox, oy, scale), pal["fill"], pal["outline"], pal["shade"])


def draw_sun(cv, cx, cy, r=4.0, rays=True, ray_len=2):
    """Sonne um (cx, cy); Strahlen in 8 Richtungen."""
    if rays:
        n = int(cx - 0.5), int(cy - 0.5)
        for k in range(ray_len):
            d = int(r) + 2 + k
            cv.dots([(n[0], n[1] - d), (n[0] + 1, n[1] - d)], SUN_RAY)          # oben
            cv.dots([(n[0], n[1] + 1 + d), (n[0] + 1, n[1] + 1 + d)], SUN_RAY)  # unten
            cv.dots([(n[0] - d, n[1]), (n[0] - d, n[1] + 1)], SUN_RAY)          # links
            cv.dots([(n[0] + 1 + d, n[1]), (n[0] + 1 + d, n[1] + 1)], SUN_RAY)  # rechts
        dd = int(r * 0.72) + 2
        for k in range(ray_len):
            e = dd + k
            cv.dots([(n[0] - e, n[1] - e), (n[0] + 1 + e, n[1] - e),
                     (n[0] - e, n[1] + 1 + e), (n[0] + 1 + e, n[1] + 1 + e)], SUN_RAY)
    cv.paint(disc(cx, cy, r), SUN["fill"], SUN["outline"], SUN["shade"])
    cv.dots([(int(cx - r * 0.45), int(cy - r * 0.45)), (int(cx - r * 0.45) + 1, int(cy - r * 0.45))], "#fde9a0")
    cv.dots([(int(cx - r * 0.45), int(cy - r * 0.45) + 1)], "#fde9a0")


def draw_drops(cv, cells, color=DROP, length=2):
    for x, y in cells:
        for k in range(length):
            cv.dots([(x, y + k)], color)


def draw_flake(cv, cx, cy):
    cv.dots([(cx, cy - 1), (cx - 1, cy), (cx + 1, cy), (cx, cy + 1)], SNOW)
    cv.dots([(cx, cy)], SNOW_CORE)


def wx_klar():
    cv = Canvas(16, 16)
    draw_sun(cv, 8, 8, r=4.0)
    return cv


def wx_klar_nacht():
    cv = Canvas(16, 16)
    moon = disc(7.5, 8.5, 6.2) - disc(11.2, 6.2, 5.0)
    cv.paint(moon, "#f7e08a", "#c9a23a", "#e8c862")
    cv.dots([(4, 7), (4, 8), (5, 6)], "#fff3c4")
    # Sterne
    for sx, sy in ((11, 3), (13, 9)):
        cv.dots([(sx, sy - 1), (sx - 1, sy), (sx + 1, sy), (sx, sy + 1)], "#f2c53e")
        cv.dots([(sx, sy)], "#fff3c4")
    cv.dots([(14, 4)], "#f2c53e")
    return cv


def wx_teilweise():
    cv = Canvas(16, 16)
    draw_sun(cv, 6.5, 6.5, r=3.2, ray_len=2)
    draw_cloud(cv, 2, 6, CLOUD)
    return cv


def wx_bedeckt():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 1, CLOUD_GREY, scale=0.85)
    draw_cloud(cv, 2, 6, CLOUD)
    return cv


def wx_niesel():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 1, CLOUD)
    draw_drops(cv, [(4, 11), (8, 12), (12, 11)], DROP_LIGHT, 2)
    return cv


def wx_regen():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD_GREY)
    draw_drops(cv, [(3, 10), (6, 11), (9, 10), (12, 11)], DROP, 2)
    draw_drops(cv, [(4, 13), (7, 14), (10, 13)], DROP, 1)
    return cv


def wx_schnee():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD)
    for fx, fy in ((4, 11), (8, 13), (12, 11)):
        draw_flake(cv, fx, fy)
    return cv


def wx_nebel():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD_GREY, scale=0.95)
    for y, x0, x1 in ((10, 2, 12), (12, 4, 14), (14, 1, 9)):
        cv.flat(rect(x0, y, x1 - x0 + 1, 1), "#8fa3b8")
    cv.flat(rect(2, 11, 8, 1), "#b4c3d2")
    cv.flat(rect(4, 13, 8, 1), "#b4c3d2")
    cv.flat(rect(1, 15, 6, 1), "#b4c3d2")
    return cv


def wx_gewitter():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD_DARK)
    bolt = ascii_mask([
        "...###",
        "..###.",
        ".###..",
        "..####",
        "...##.",
        "..##..",
        ".##...",
        "##....",
    ])
    cv.flat(shift(bolt, 5, 8), BOLT)
    cv.dots([(11, 8 + 3), (10, 8 + 4), (8, 8 + 5), (6, 8 + 6)], BOLT_EDGE)
    return cv


# ---------- Hinweise und System (16 x 16) ----------

def stroke(cv, pts, color, r=0.95):
    for x, y in pts:
        cv.flat(disc(x, y, r), color)


def arc(cx, cy, rad, a0, a1, n=40):
    import math
    return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + rad * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def hint_wind():
    cv = Canvas(16, 16)
    c = "#5fa3c0"
    line = lambda x0, x1, y: [(x, y) for x in [x0 + i * 0.5 for i in range(int((x1 - x0) * 2) + 1)]]
    # obere Bahn mit Kringel nach oben, mittlere Bahn lang, untere Bahn mit Kringel nach unten (alles innerhalb 16 x 16)
    stroke(cv, line(1.5, 10.5, 5.0) + arc(10.5, 3.0, 2.0, 90, -150), c)
    stroke(cv, line(0.5, 12.5, 8.0), c)
    stroke(cv, line(2.5, 9.5, 10.9) + arc(9.5, 12.9, 2.0, -90, 150), c)
    return cv


def hint_glaette():
    """Stiefel auf einer Eisplatte, Bewegungsstriche dahinter: rutschig."""
    cv = Canvas(16, 16)
    slab = rect(0, 10, 16, 4) - {(0, 10), (15, 10), (0, 13), (15, 13)}
    cv.paint(slab, "#d4effb", "#5aa6cf", "#aedcf0")
    cv.dots([(2, 11), (3, 11), (4, 11), (9, 12), (10, 12), (11, 12)], "#ffffff")
    boot = ascii_mask([
        "...#####.",
        "...#####.",
        "...#####.",
        "...#####.",
        ".########",
        "#########",
        "#########",
    ])
    cv.paint(shift(boot, 4, 3), "#a0714f", "#6b4630", "#85593c")
    cv.dots([(13, 5), (14, 5), (15, 5), (14, 7), (15, 7)], "#8fa6ba")
    for sx, sy in ((2, 3), (13, 1)):
        cv.dots([(sx, sy - 1), (sx - 1, sy), (sx + 1, sy), (sx, sy + 1)], "#6fb6e4")
    return cv


def sys_uhr():
    cv = Canvas(16, 16)
    soft = "#9a8a7a"
    cv.paint(disc(8, 8, 7.0), "#fffaf0", soft, "#efe5d2")
    cv.dots([(7, 3), (8, 3), (7, 12), (8, 12), (3, 7), (3, 8), (12, 7), (12, 8)], soft)
    hands = "#6f625a"
    cv.dots([(7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, 8), (9, 8), (10, 8)], hands)
    return cv


def sys_fehler():
    """Ruhige Wolke mit Fragezeichen: ein Erwachsener soll nachsehen."""
    cv = Canvas(16, 16)
    cv.paint(cloud_mask(0, 1, 1.15), "#eef3f8", "#7088a0", "#cbd8e5")
    q = ["111", "001", "011", "000", "010"]
    cv.dots([(6 + x, 5 + y) for y, row in enumerate(q) for x, c in enumerate(row) if c == "1"], "#e8665a")
    return cv


def ui_flocke():
    """Schneeflocke für die Kugel des Thermometers (11 x 11, weiß auf Blau)."""
    cv = Canvas(11, 11)
    white = "#ffffff"
    for i in range(11):
        cv.dots([(5, i), (i, 5), (i, i), (i, 10 - i)], white)
    for p in ((4, 1), (6, 1), (4, 9), (6, 9), (1, 4), (1, 6), (9, 4), (9, 6)):
        cv.dots([p], white)
    cv.dots([(5, 5)], "#cfe8fb")
    return cv


# ---------- Sprite ----------

WEATHER = {
    "i-wx-klar": wx_klar, "i-wx-klar-nacht": wx_klar_nacht, "i-wx-teilweise": wx_teilweise,
    "i-wx-bedeckt": wx_bedeckt, "i-wx-niesel": wx_niesel, "i-wx-regen": wx_regen,
    "i-wx-schnee": wx_schnee, "i-wx-nebel": wx_nebel, "i-wx-gewitter": wx_gewitter,
    "i-hint-wind": hint_wind, "i-hint-glaette": hint_glaette,
    "i-sys-uhr": sys_uhr, "i-sys-fehler": sys_fehler,
}
UI = {"i-ui-flocke": (ui_flocke, "0 0 11 11")}

# Icon-Module mit je einer Funktion build() -> {Symbol-ID: Raster}. Später genannte gewinnen.
MODULES = ["icons_schuhe_hosen", "icons_oberteile", "icons_kopf_zubehoer"]
UI_VIEWBOX = {"i-ui-innen": "0 0 14 14", "i-ui-aussen": "0 0 14 14"}   # feste Fläche, Umschalter links im Bild
REMOVE = [                        # Symbole, die es nicht mehr gibt
    "i-top-kapuzenjacke",         # ist jetzt i-top-regenjacke (pink, gefüttert, A-27)
    "i-top-schneeanzug",          # ist Schneejacke + Schneehose (A-23)
    "i-shoes-sneaker-v2", "i-shoes-sneaker-v3", "i-shoes-sandalen-v2", "i-shoes-sandalen-v3",   # keine Varianten (A-30)
    "i-acc-schal-v3",             # der Schal gibt es in lila und grün (A-28)
]


def recenter(px, size=16):
    """Schiebt den Inhalt in die Mitte der size x size Fläche, damit alle Icons gleich sitzen."""
    xs = [p[0] for p in px]
    ys = [p[1] for p in px]
    dx = (size - (max(xs) - min(xs) + 1)) // 2 - min(xs)
    dy = (size - (max(ys) - min(ys) + 1)) // 2 - min(ys)
    return {(x + dx, y + dy): c for (x, y), c in px.items()}


def normalize(px):
    """Schiebt den Inhalt auf (0, 0), damit der Pfad-Parser keine negativen Koordinaten sieht."""
    x0 = min(p[0] for p in px)
    y0 = min(p[1] for p in px)
    return {(x - x0, y - y0): c for (x, y), c in px.items()}


def module_symbol(sid, px):
    px = getattr(px, "px", px)
    if sid.startswith(("i-wx-", "i-hint-", "i-sys-")):
        return symbol(sid, recenter(px), "0 0 16 16")
    if sid in UI_VIEWBOX:
        return symbol(sid, normalize(px), UI_VIEWBOX[sid])
    return fit_viewbox(symbol(sid, normalize(px), "0 0 40 40"))


SYMBOL_RE = r'<symbol id="{id}"[^>]*>.*?</symbol>'
PATH_RE = re.compile(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]{6})"/>')
RECT_RE = re.compile(r"M(\d+) (\d+)H(\d+)V(\d+)H\d+V\d+Z")
RECT2_RE = re.compile(r"M(\d+) (\d+)h(\d+)v(\d+)h-\d+z")


def grid_of(symbol_html):
    grid = {}
    for d, color in PATH_RE.findall(symbol_html):
        for x2, y, x1, _y2 in RECT_RE.findall(d):
            for x in range(int(x1), int(x2)):
                grid[(x, int(y))] = color.lower()
        for x1, y, w, h in RECT2_RE.findall(d):
            for x in range(int(x1), int(x1) + int(w)):
                for yy in range(int(y), int(y) + int(h)):
                    grid[(x, yy)] = color.lower()
    return grid


def fit_viewbox(symbol_html):
    """Setzt die viewBox eng um den gezeichneten Inhalt (ganze Kunstpixel)."""
    grid = grid_of(symbol_html)
    if not grid:
        return symbol_html
    xs = [p[0] for p in grid]
    ys = [p[1] for p in grid]
    vb = f"{min(xs)} {min(ys)} {max(xs) - min(xs) + 1} {max(ys) - min(ys) + 1}"
    return re.sub(r'viewBox="[^"]*"', f'viewBox="{vb}"', symbol_html, count=1)


def upsert(html, sid, symbol_html):
    pattern = re.compile(SYMBOL_RE.format(id=re.escape(sid)), re.S)
    if pattern.search(html):
        return pattern.sub(lambda _m: symbol_html, html, count=1)
    end = html.index("</svg>", html.index('<svg style="display:none"'))
    return html[:end] + symbol_html + "\n" + html[end:]


def remove_symbol(html, sid):
    return re.sub(SYMBOL_RE.format(id=re.escape(sid)) + r"\n?", "", html, count=1, flags=re.S)


def main():
    import importlib
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    html = INDEX.read_text()

    for sid, fn in WEATHER.items():
        html = upsert(html, sid, symbol(sid, recenter(fn().px), "0 0 16 16"))
    for sid, (fn, vb) in UI.items():
        html = upsert(html, sid, symbol(sid, fn().px, vb))

    count = 0
    for name in MODULES:
        for sid, px in importlib.import_module(name).build().items():
            html = upsert(html, sid, module_symbol(sid, px))
            count += 1

    for sid in REMOVE:
        html = remove_symbol(html, sid)

    # Alle übrigen Pixel-Kleidungsstücke (Strickjacke, Schneeanzug): enge viewBox und kompakte Pfade
    for m in list(re.finditer(r'<symbol id="(i-(?:top|bottom|shoes|head|acc)-[^"]+)"[^>]*>.*?</symbol>', html, re.S)):
        sid = m.group(1)
        grid = grid_of(m.group(0))
        if "h-" not in m.group(0) and grid:          # noch im alten Zeilenformat
            html = upsert(html, sid, fit_viewbox(symbol(sid, grid, "0 0 40 40")))
        else:
            html = upsert(html, sid, fit_viewbox(m.group(0)))

    INDEX.write_text(html)
    print("Sprite aktualisiert:", len(WEATHER) + len(UI), "Wetter/Hinweis/System,", count, "aus den Modulen,",
          "alle Kleidungs-viewBoxen angepasst")

    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        write_preview(out, html)


def write_preview(out, html):
    sprite = html[html.index('<svg style="display:none"'):html.index("</svg>", html.index('<svg style="display:none"')) + 6]
    ids = re.findall(r'<symbol id="([^"]+)"', sprite)
    cells = []
    for sid in ids:
        vb = re.search(rf'<symbol id="{re.escape(sid)}" viewBox="([^"]+)"', sprite).group(1).split()
        w, h = int(vb[2]), int(vb[3])
        scale = 8 if w <= 16 else 6
        cells.append(
            f'<div class="c"><svg width="{w * scale}" height="{h * scale}" shape-rendering="crispEdges">'
            f'<use href="#{sid}"/></svg><div>{sid}</div></div>'
        )
    out.write_text(
        '<!doctype html><meta charset="utf-8"><style>body{background:#faf7f0;margin:16px;'
        'font:11px monospace;display:flex;flex-wrap:wrap;gap:16px}.c{min-width:140px}</style>'
        + sprite.replace('style="display:none"', 'style="display:none"') + "".join(cells)
    )


if __name__ == "__main__":
    main()
