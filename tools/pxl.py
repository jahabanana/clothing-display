#!/usr/bin/env python3
"""
Zeichenwerkzeug für die Pixel-Icons (Spec §12.5): Masken, Canvas, Symbol-Ausgabe
und Vorschau-Bilder. Wird von tools/pixel_icons.py und den Icon-Modulen benutzt.

Vorschau ohne Browser (braucht Pillow):
  from pxl import sheet, app_frames
  sheet({"i-top-tshirt": canvas.px, ...}, "out.png", scale=10)
  app_frames([dict(top=px, bottom=px, shoes=px, head=None, acc=[px, ...], band=3)], "out.png")

original_px() und die Vorschauen der icons_*.py-Module brauchen einen älteren Stand von index.html unter
.wip/backup-vor-umsetzung/ (nicht im Repo). Die Raster selbst (build()) und pixel_icons.py brauchen ihn nicht.
"""
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
    """<symbol> aus einem Raster. Je Farbe ein <path> aus Rechtecken: waagerechte Läufe, gleiche Läufe in
    aufeinanderfolgenden Zeilen werden zu einem höheren Rechteck zusammengefasst (kürzer, gleiches Bild)."""
    by_color = {}
    for (x, y), color in px.items():
        by_color.setdefault(color.lower(), set()).add((x, y))
    parts = []
    for color, cells in by_color.items():
        runs = {}                                   # (x1, x2) -> Zeilen
        rows = {}
        for x, y in cells:
            rows.setdefault(y, []).append(x)
        spans = {}                                  # y -> [(x1, x2)]
        for y, xs in rows.items():
            xs.sort()
            cur = []
            for x in xs:
                if cur and cur[-1][1] == x:
                    cur[-1][1] = x + 1
                else:
                    cur.append([x, x + 1])
            spans[y] = [tuple(c) for c in cur]
        done = set()
        d = []
        for y in sorted(spans):
            for (x1, x2) in spans[y]:
                if (y, x1, x2) in done:
                    continue
                h = 1
                while (x1, x2) in spans.get(y + h, ()):
                    done.add((y + h, x1, x2))
                    h += 1
                d.append(f"M{x1} {y}h{x2 - x1}v{h}h-{x2 - x1}z")
        parts.append(f'<path d="{"".join(d)}" fill="{color}"/>')
    return f'<symbol id="{sid}" viewBox="{viewbox}">{"".join(parts)}</symbol>'


# ---------- Hilfen zum Übernehmen und Betrachten ----------

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_HTML = _ROOT / ".wip" / "backup-vor-umsetzung" / "index.html"   # Stand vor der Überarbeitung
_PATH_RE = re.compile(r'<path d="([^"]+)" fill="(#[0-9a-fA-F]{6})"/>')
_RECT_RE = re.compile(r"M(\d+) (\d+)H(\d+)V(\d+)H\d+V\d+Z")          # altes Format (Zeile für Zeile, rückwärts)
_RECT2_RE = re.compile(r"M(\d+) (\d+)h(\d+)v(\d+)h-\d+z")             # kompaktes Format


def original_px(sid, html_path=ORIGINAL_HTML):
    """Liest ein Symbol aus einem index.html als {(x, y): '#rrggbb'}. Zum einmaligen Übernehmen in ein Icon-Modul."""
    html = Path(html_path).read_text()
    m = re.search(rf'<symbol id="{re.escape(sid)}"[^>]*>.*?</symbol>', html, re.S)
    grid = {}
    for d, color in _PATH_RE.findall(m.group(0)):
        for x2, y, x1, _ in _RECT_RE.findall(d):
            for x in range(int(x1), int(x2)):
                grid[(x, int(y))] = color.lower()
        for x1, y, w, h in _RECT2_RE.findall(d):
            for x in range(int(x1), int(x1) + int(w)):
                for yy in range(int(y), int(y) + int(h)):
                    grid[(x, yy)] = color.lower()
    return grid


def dump_ascii(px, letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    """Zeigt ein Raster als Text und liefert die Palette {Buchstabe: Farbe}, passend für Canvas.art()."""
    xs = [p[0] for p in px]; ys = [p[1] for p in px]
    x0, y0 = min(xs), min(ys)
    pal = {}
    for c in dict.fromkeys(px[p] for p in sorted(px, key=lambda p: (p[1], p[0]))):
        pal[letters[len(pal)]] = c
    inv = {v: k for k, v in pal.items()}
    rows = ["".join(inv[px[(x, y)]] if (x, y) in px else "." for x in range(x0, max(xs) + 1)) for y in range(y0, max(ys) + 1)]
    return rows, pal


def bbox(px):
    xs = [p[0] for p in px]; ys = [p[1] for p in px]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _draw(img, px, x, y, s):
    """Zeichnet ein Raster mit der linken oberen Ecke seiner Bounding-Box auf (x, y), s Bildpixel pro Kunstpixel."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    x0, y0, _, _ = bbox(px)
    for (px_, py_), c in px.items():
        X = x + (px_ - x0) * s
        Y = y + (py_ - y0) * s
        d.rectangle([X, Y, X + s - 1, Y + s - 1], fill=_hex(c))


def sheet(icons, out, scale=10, bg="#faf7f0", cols=6, pad=14, label=True):
    """Kontaktbogen: {name: px oder Canvas} -> PNG, jedes Icon in ganzen Bildpixeln pro Kunstpixel."""
    from PIL import Image, ImageDraw
    items = [(k, getattr(v, "px", v)) for k, v in icons.items()]
    dims = [(bbox(p)[2] * scale, bbox(p)[3] * scale) for _, p in items]
    cw = max(w for w, _ in dims) + pad * 2
    rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    rh = [max(dims[items.index(it)][1] for it in r) + pad * 2 + (14 if label else 0) for r in rows]
    img = Image.new("RGB", (cw * min(cols, len(items)), sum(rh)), _hex(bg))
    d = ImageDraw.Draw(img)
    y = 0
    for r, h in zip(rows, rh):
        for i, (name, p) in enumerate(r):
            w_, h_ = bbox(p)[2] * scale, bbox(p)[3] * scale
            _draw(img, p, i * cw + (cw - w_) // 2, y + pad + (h - pad * 2 - (14 if label else 0) - h_), scale)
            if label:
                d.text((i * cw + 4, y + h - 14), name, fill=(90, 80, 70))
        y += h
    img.save(out)
    return out


# Layout wie in index.html: Fenster in pt (top, Höhe, Ausrichtung), Spaltenmitte x = 124 pt, Pixel 5,5 pt, Zubehör 3,5 pt (3 pt, wenn zu breit)
BAND_TINTS = ["#FCEADB", "#FCF1DC", "#F8F4E5", "#EFF3EC", "#E9F1F2", "#E3EEF6", "#DDE8F5"]   # heiss … frost
_SLOTS = {"head": (86.5, 82.5, "bottom"), "top": (180, 132, "bottom"), "bottom": (317.5, 148.5, "top"), "shoes": (466, 93.5, "top")}


def app_frames(frames, out, zoom=2, column_only=True, gap=16, labels=None):
    """Setzt Outfits so zusammen wie die App (Spaltenbreite 240 pt, ohne Thermometer).
    frames: Liste von dict(head=px|None, top=px, bottom=px, shoes=px, acc=[px, ...], band=0..6)
    zoom: Bildpixel pro pt (2 = Gerätepixel, die Kunstpixel sind dann 11 Bildpixel)."""
    from PIL import Image, ImageDraw
    W = (240 if column_only else 375) * zoom
    H = 667 * zoom
    img = Image.new("RGB", ((W + gap) * len(frames) - gap, H + (16 if labels else 0)), (243, 239, 231))
    d = ImageDraw.Draw(img)
    for n, f in enumerate(frames):
        ox = n * (W + gap)
        d.rectangle([ox, 0, ox + W - 1, H - 1], fill=_hex(BAND_TINTS[f.get("band", 2)]))
        cx = 124
        for kind, (top, height, align) in _SLOTS.items():
            px = f.get(kind)
            if not px:
                continue
            px = getattr(px, "px", px)
            _, _, w, h = bbox(px)
            sw, sh = w * 5.5, h * 5.5
            y = top + (height - sh if align == "bottom" else (height - sh) / 2 if align == "center" else 0)
            _draw(img, px, ox + round((cx - sw / 2) * zoom), round(y * zoom), int(5.5 * zoom))
        acc = [getattr(a, "px", a) for a in f.get("acc", [])]
        if acc:
            def width(p): return sum(bbox(a)[2] * p + (10 if i else 0) for i, a in enumerate(acc))
            p = 3.5 if width(3.5) <= 224 else 3
            total = width(p)
            x = cx - total / 2
            for a in acc:
                _, _, w, h = bbox(a)
                _draw(img, a, ox + round(x * zoom), round((568 + 70 - h * p) * zoom), max(1, round(p * zoom)))
                x += w * p + 10
        if labels:
            d.text((ox + 4, H + 2), labels[n], fill=(90, 80, 70))
    img.save(out)
    return out
