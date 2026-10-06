#!/usr/bin/env python3
"""
Pixel-Icons zeichnen und ins Sprite von index.html schreiben (Spec §12.5).

Das Skript hat drei Aufgaben:
1. Die Wetter-, Hinweis- und System-Icons (16 x 16) sowie die neuen
   Kleidungsstücke (Basecap, Handschuhe, Sonnencreme, Regenjacke) werden hier
   in Code gezeichnet. Rundungen und Konturen entstehen aus Formen ("Masken"),
   die Kontur ist der Rand der Form.
2. Alle Kleidungs-Symbole bekommen eine enge viewBox um ihren sichtbaren
   Inhalt, damit das Layout jedes Teil ohne Leerrand platzieren kann.
3. Die Symbole werden in das Sprite von index.html geschrieben. Vorhandene
   Symbole mit derselben ID werden ersetzt, neue am Ende des Sprites angefügt.

Das Skript ist idempotent. Aufruf: python3 tools/pixel_icons.py
Mit --preview <datei.html> entsteht zusätzlich eine Kontaktbogen-Seite.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ---------- Zeichenwerkzeug ----------

def ascii_mask(rows, ch="#"):
    return {(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c == ch}


def disc(cx, cy, r):
    return {
        (x, y)
        for x in range(int(cx - r) - 1, int(cx + r) + 2)
        for y in range(int(cy - r) - 1, int(cy + r) + 2)
        if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r
    }


def rect(x, y, w, h):
    return {(i, j) for i in range(x, x + w) for j in range(y, y + h)}


def shift(mask, dx, dy):
    return {(x + dx, y + dy) for x, y in mask}


def clip(mask, x0=-999, y0=-999, x1=999, y1=999):
    return {(x, y) for x, y in mask if x0 <= x <= x1 and y0 <= y <= y1}


class Canvas:
    def __init__(self, w, h):
        self.w, self.h, self.px = w, h, {}

    def paint(self, mask, fill, outline, shade=None):
        """Füllt die Form, der Rand (4er-Nachbarschaft) wird zur Kontur,
        die Reihe über dem unteren Rand optional zum Schatten."""
        edge = {p for p in mask if any((p[0] + dx, p[1] + dy) not in mask for dx, dy in N4)}
        for p in mask:
            self.px[p] = outline if p in edge else fill
        if shade:
            for x, y in mask - edge:
                if (x, y + 1) in edge:
                    self.px[(x, y)] = shade

    def flat(self, mask, color):
        for p in mask:
            self.px[p] = color

    def dots(self, cells, color):
        for p in cells:
            self.px[p] = color

    def art(self, rows, palette, ox=0, oy=0):
        """Handgezeichnete Reihen. '.' ist leer, jedes andere Zeichen steht in der Palette."""
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c != ".":
                    self.px[(x + ox, y + oy)] = palette[c]


def symbol(sid, px, viewbox):
    by_color = {}
    for (x, y), color in px.items():
        by_color.setdefault(color.lower(), []).append((y, x))
    parts = []
    for color, cells in by_color.items():
        by_row = {}
        for y, x in cells:
            by_row.setdefault(y, []).append(x)
        d = []
        for y in sorted(by_row):
            xs = sorted(by_row[y])
            runs = []
            for x in xs:
                if runs and runs[-1][1] == x:
                    runs[-1][1] = x + 1
                else:
                    runs.append([x, x + 1])
            for x1, x2 in runs:
                d.append(f"M{x2} {y}H{x1}V{y + 1}H{x2}V{y}Z")
        parts.append(f'<path d="{"".join(d)}" fill="{color}"/>')
    return f'<symbol id="{sid}" viewBox="{viewbox}">{"".join(parts)}</symbol>'


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
    draw_sun(cv, 5.5, 5.5, r=3.2, ray_len=2)
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
    # obere Bahn mit Kringel nach oben
    stroke(cv, line(1.5, 10.5, 5.0) + arc(10.5, 2.9, 2.1, 90, -150), c)
    # mittlere Bahn, lang
    stroke(cv, line(0.5, 12.5, 8.5), c)
    # untere Bahn mit Kringel nach unten
    stroke(cv, line(2.5, 9.5, 12.0) + arc(9.5, 14.1, 2.1, -90, 150), c)
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


SKIN, SKIN_EDGE = "#f4cfae", "#cf9f78"


# ---------- Kleidung (Koordinaten frei, die viewBox wird eng um den Inhalt gelegt) ----------

def head_cap():
    """Basecap von der Seite, Schirm nach rechts, mit Knopf, Naht und Glanz."""
    cv = Canvas(27, 17)
    fill, edge, shade, hi = "#5cac72", "#3b7f50", "#4a9a62", "#9bd8ac"
    visor_fill, visor_shade = "#3f8a57", "#357a4b"
    dome = clip(disc(9.5, 10.0, 8.8), y1=11)
    visor = set()
    for x in range(12, 25):
        top = 9 + (x - 12) // 6
        visor |= {(x, top + k) for k in range(4)}
    visor -= {(24, 9 + 12 // 6), (24, 9 + 12 // 6 + 3)}
    cv.paint(dome | visor, fill, edge, shade)
    for p in visor - dome:
        if cv.px.get(p) == fill:
            cv.px[p] = visor_fill
        elif cv.px.get(p) == shade:
            cv.px[p] = visor_shade
    cv.dots([(20, 11), (21, 11), (22, 12), (23, 12)], "#58a470")
    cv.dots([(10, 2), (10, 3), (11, 4), (11, 5), (12, 6), (12, 7), (13, 8), (13, 9)], shade)
    cv.dots([(9, 0), (10, 0), (9, 1)], edge)
    cv.dots([(10, 1)], shade)
    cv.dots([(3, 7), (3, 8), (4, 5), (5, 4)], hi)
    return cv


def acc_handschuhe():
    """Zwei Fäustlinge, der linke mit Daumen nach rechts, der rechte gespiegelt."""
    fill, edge, shade = "#f0bb43", "#bf8a28", "#d9a236"
    cuff, cuff_rib = "#fdf0c8", "#e8cf8a"
    W = 26
    cv = Canvas(W, 16)
    body = disc(4.8, 4.8, 4.5) | rect(1, 4, 8, 7)
    body = {p for p in body if p[1] <= 10}
    thumb = disc(10.0, 7.4, 2.0)
    cv.paint(body | thumb, fill, edge, shade)
    cv.dots([(3, 2), (3, 3), (4, 1)], "#f9dc8a")
    cv.paint(rect(1, 11, 8, 5), cuff, edge)
    for x in (3, 5, 7):
        for y in range(12, 15):
            cv.dots([(x, y)], cuff_rib)
    cv.px.update({(W - 1 - x, y): c for (x, y), c in list(cv.px.items())})
    return cv


def acc_sonnencreme():
    """Sonnencreme-Flasche, orange, mit großer Sonne auf dem Etikett."""
    cv = Canvas(12, 20)
    cv.paint(rect(3, 0, 6, 4), "#fff1c9", "#c9a64e", "#ecd896")
    cv.paint(rect(4, 4, 4, 2), "#fde7c8", "#bf6f2c")
    body = clip(rect(1, 6, 10, 14) | disc(6.0, 9.0, 5.0), y0=6) - {(1, 19), (10, 19)}
    cv.paint(body, "#f4a259", "#bf6f2c", "#e08a3f")
    cv.dots([(2, 8), (2, 9), (2, 10)], "#f9c490")
    cv.flat(rect(3, 10, 6, 7), "#fff6e0")
    cv.paint(disc(6, 13.5, 2.3), "#f8cd4e", "#e09a2c")
    cv.dots([(6, 10), (6, 16), (3, 13), (8, 13)], "#f2a63a")
    return cv


def acc_schal():
    """Gestreifter Schal: dicker Wickel, ein langes Ende vorn, ein kürzeres dahinter, Fransen."""
    cv = Canvas(16, 19)
    base, edge, shade, stripe = "#5e8c8a", "#3f6867", "#4d7a78", "#f3ead2"
    back = rect(2, 4, 6, 10)
    front = rect(7, 4, 7, 14)
    band = rect(0, 0, 16, 6) - {(0, 0), (15, 0), (0, 5), (15, 5)}
    cv.paint(back, "#4d7a78", "#3a5f5e", "#436e6c")
    cv.paint(front, base, edge, shade)
    cv.paint(band, base, edge, shade)
    for y in (9, 10, 13, 14):
        cv.dots([(x, y) for x in range(8, 13)], stripe)
    for y in (8, 9):
        cv.dots([(x, y) for x in range(3, 7)], "#d7cdb4")
    cv.dots([(7, 18), (9, 18), (11, 18), (13, 18), (3, 14), (5, 14), (7, 14)], shade)
    cv.dots([(2, 1), (3, 1), (2, 2), (6, 2), (7, 2)], "#8fb8b5")
    return cv


def shoes_sandalen():
    """Offene Sandale von der Seite: Fuß, drei orange Riemen, Sohle. Spitze nach links."""
    cv = Canvas(19, 10)
    foot = ascii_mask([
        "..........####.....",
        ".........######....",
        "......#########....",
        "....###########....",
        "..##############...",
        ".################..",
        "###################",
    ])
    cv.paint(foot, SKIN, SKIN_EDGE)
    for x0, x1, y0 in ((5, 7, 3), (10, 12, 0), (15, 17, 3)):
        cv.paint(rect(x0, y0, x1 - x0 + 1, 7 - y0), "#ec8c3f", "#b85f1f")
    sole = rect(0, 7, 19, 3) - {(0, 7), (18, 7), (0, 9), (18, 9)}
    cv.paint(sole, "#d9732f", "#a85620", "#c4651f")
    return cv


def rain_jacket_from(grid):
    """Regenjacke: Kapuzen-Silhouette (Kapuzenpullover) in Regengelb, mit Reißverschluss und Taschen."""
    pal = {"#c6a34d": "#c99a1c", "#e5be5b": "#f7cf3d", "#a78a41": "#dcae26"}
    cv = Canvas(24, 28)
    for p, c in grid.items():
        cv.px[p] = pal[c]
    xs = [p[0] for p in grid]
    ys = [p[1] for p in grid]
    x0, y0 = min(xs), min(ys)
    edge = "#c99a1c"
    mid = x0 + 11
    # Reißverschluss
    for y in range(y0 + 9, y0 + 27):
        cv.px[(mid, y)] = edge
        cv.px[(mid + 1, y)] = "#fff0a8"
    # Taschenschlitze
    for x in (mid - 6, mid - 5, mid - 4, mid + 4, mid + 5, mid + 6):
        cv.px[(x, y0 + 21)] = edge
    # Glanz auf der linken Schulter und dem linken Ärmel
    for p in ((x0 + 5, y0 + 12), (x0 + 5, y0 + 13), (x0 + 2, y0 + 13), (x0 + 2, y0 + 14), (x0 + 2, y0 + 15)):
        cv.px[p] = "#fde886"
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
NEW_CLOTHES = {
    "i-head-sonnenhut": head_cap,       # ID bleibt (RULES), die Grafik ist jetzt eine Basecap
    "i-acc-schal": acc_schal,
    "i-shoes-sandalen": shoes_sandalen,
    "i-acc-handschuhe": acc_handschuhe,
    "i-acc-sonnencreme": acc_sonnencreme,
}

def recenter(px, size=16):
    """Schiebt den Inhalt in die Mitte der size x size Fläche, damit alle Icons gleich sitzen."""
    xs = [p[0] for p in px]
    ys = [p[1] for p in px]
    dx = (size - (max(xs) - min(xs) + 1)) // 2 - min(xs)
    dy = (size - (max(ys) - min(ys) + 1)) // 2 - min(ys)
    return {(x + dx, y + dy): c for (x, y), c in px.items()}


SNEAKER_COLORS = {"#babab4": "#8d8d86", "#d8d8d2": "#f4f4ef", "#9e9e99": "#74746e"}


def with_legs(symbol_html):
    """Hängt der kurzen Hose zwei Beine in Hautfarbe an, damit zwischen Hose und Schuh keine Lücke bleibt."""
    grid = grid_of(symbol_html)
    last = max(y for _, y in grid)
    if last >= 30:
        return symbol_html            # schon erledigt
    xs = sorted(x for x, y in grid if y == last)
    runs, start = [], xs[0]
    for a, b in zip(xs, xs[1:] + [None]):
        if b != a + 1:
            runs.append((start, a))
            start = b
    px = dict(grid)
    for x0, x1 in runs:
        lx = (x0 + x1) // 2 - 2
        for y in range(last + 1, last + 10):
            for x in range(lx, lx + 5):
                px[(x, y)] = SKIN_EDGE if x in (lx, lx + 4) else SKIN
    sid = re.search(r'id="([^"]+)"', symbol_html).group(1)
    return symbol(sid, px, "0 0 32 33")


SYMBOL_RE = r'<symbol id="{id}"[^>]*>.*?</symbol>'
PATH_RE = re.compile(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]{6})"/>')
RECT_RE = re.compile(r"M(\d+) (\d+)H(\d+)V(\d+)H\d+V\d+Z")


def grid_of(symbol_html):
    grid = {}
    for d, color in PATH_RE.findall(symbol_html):
        for x2, y, x1, _y2 in RECT_RE.findall(d):
            for x in range(int(x1), int(x2)):
                grid[(x, int(y))] = color.lower()
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


def main():
    html = INDEX.read_text()

    for sid, fn in WEATHER.items():
        html = upsert(html, sid, symbol(sid, recenter(fn().px), "0 0 16 16"))

    for sid, (fn, vb) in UI.items():
        html = upsert(html, sid, symbol(sid, fn().px, vb))

    for sid, fn in NEW_CLOTHES.items():
        html = upsert(html, sid, fit_viewbox(symbol(sid, fn().px, "0 0 32 32")))

    base = re.search(SYMBOL_RE.format(id="i-top-kapuzenpullover"), html, re.S).group(0)
    rain = rain_jacket_from(grid_of(base))
    html = upsert(html, "i-top-regenjacke", fit_viewbox(symbol("i-top-regenjacke", rain.px, "0 0 32 32")))

    # Bestehende Grafiken nachbessern: Sneaker mit mehr Kontrast, kurze Hose mit Beinen
    m = re.search(SYMBOL_RE.format(id="i-shoes-sneaker"), html, re.S)
    sneaker = m.group(0)
    for old, new in SNEAKER_COLORS.items():
        sneaker = sneaker.replace(f'fill="{old}"', f'fill="{new}"')
    html = upsert(html, "i-shoes-sneaker", sneaker)
    m = re.search(SYMBOL_RE.format(id="i-bottom-hose-kurz"), html, re.S)
    html = upsert(html, "i-bottom-hose-kurz", with_legs(m.group(0)))

    # Alle übrigen Pixel-Kleidungsstücke: enge viewBox
    for m in list(re.finditer(r'<symbol id="(i-(?:top|bottom|shoes|head|acc)-[^"]+)"[^>]*>.*?</symbol>', html, re.S)):
        sid = m.group(1)
        html = upsert(html, sid, fit_viewbox(re.search(SYMBOL_RE.format(id=re.escape(sid)), html, re.S).group(0)))

    INDEX.write_text(html)
    print("Sprite aktualisiert:", len(WEATHER) + len(UI) + len(NEW_CLOTHES) + 1, "neu gezeichnet,",
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
