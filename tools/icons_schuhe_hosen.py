#!/usr/bin/env python3
"""
Gruppe schuhe_hosen: Schuhe als Paar (mit Farbvarianten) und Hosen.

  python3 tools/icons_schuhe_hosen.py        # schreibt Vorschauen nach .wip/art/schuhe_hosen/

Schnittstelle: build() -> {symbol-id: {(x, y): "#rrggbb"}}
Alle Raster sind als ASCII-Art eingebettet ('.' = leer, jeder Buchstabe steht in der Palette der Sorte).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxl import Canvas  # noqa: E402


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------

def _check(rows, width, name):
    for i, r in enumerate(rows):
        assert len(r) == width, f"{name}: Zeile {i} hat {len(r)} statt {width} Zeichen: {r!r}"


def shoe_pair(rows, pal, name="shoe", overlay=None):
    """Linker Schuh gezeichnet (Spitze links), rechter gespiegelt, 2 Pixel Lücke -> Paar 26 breit.
    overlay: {(x, y): Buchstabe}, Details, die nach dem Raster auf den linken Schuh gesetzt werden."""
    _check(rows, 12, name)
    left = Canvas(12, len(rows))
    left.art(rows, pal)
    for (x, y), ch in (overlay or {}).items():
        left.px[(x, y)] = pal[ch]
    px = dict(left.px)
    px.update({(25 - x, y): c for (x, y), c in left.px.items()})
    return px


def pants(half_rows, pal, marks=None, name="pants"):
    """Hose aus der linken Hälfte (inkl. halber Lücke), rechts gespiegelt.
    marks: {(x, y): Buchstabe} für einseitige Details (z. B. Glanz), werden nach dem Spiegeln gesetzt."""
    w = len(half_rows[0])
    _check(half_rows, w, name)
    cv = Canvas(2 * w, len(half_rows))
    cv.art([r + r[::-1] for r in half_rows], pal)
    for (x, y), ch in (marks or {}).items():
        cv.px[(x, y)] = pal[ch]
    return cv.px


# ---------------------------------------------------------------------------
# Schuhe: ein Schuh = 12 Px lang (Spitze links), Schaft x 4..10 (7 breit, Mitte 7,5), Sohle x 0..11.
# Das Paar ist 26 breit, die Schaftmitten liegen bei x 7,5 und 18,5, also 5,5 links und rechts der Paarmitte (13).
# ---------------------------------------------------------------------------

#            012345678901
SNEAKER = [
    "....ooooooo.",
    "....owwwwwo.",
    "....oggwwwo.",
    "...oowwwppo.",
    "..ooggwwppo.",
    ".opppwwwppo.",
    "oppppwwwppo.",
    "oooooooooooo",
    "osssssssssso",
    "osssssssssso",
    ".oooooooooo.",
]


def sneaker_pal(cap):
    return {"o": "#8f8b85", "w": "#f6f4ef", "g": "#d6d3cb", "p": cap, "s": "#d2cccc"}


CROCS = [
    "....ooooooo.",
    "....odddddo.",
    "...oofffffo.",
    "..ooffffffo.",
    ".offfffffffo",
    "offfffffffo.",
    "offfffffffo.",
    "oppppppppppo",
    "oppppppppppo",
    "oooooooooooo",
]
# Fersenriemen nach hinten geklappt (dunkler Streifen mit hellem Niet, steht 1 Px hinter dem Schaft)
# und Lochmuster (3 + 3 Löcher) auf der Kappe
CROCS_OVER = {
    (9, 2): "o", (10, 2): "o", (11, 2): "o",
    (9, 3): "d", (10, 3): "d", (11, 3): "o",
    (9, 4): "d", (10, 4): "h", (11, 4): "o",
    (9, 5): "d", (10, 5): "d", (11, 5): "o",
    (9, 6): "o", (10, 6): "o", (11, 6): "o",
    (3, 4): "q", (5, 4): "q", (7, 4): "q", (2, 5): "q", (4, 5): "q", (6, 5): "q",
}


def crocs_pal(fill, edge, dark, hi, sole):
    """o Kontur, f Fläche, d dunkel (Öffnung, Riemen), h hell (Niet), q Löcher, p Sohle."""
    return {"o": edge, "f": fill, "d": dark, "q": edge, "h": hi, "p": sole}


GUMMI = [
    "....ooooooo.",
    "....odddddo.",
    "....odddddo.",
    "....ofhfffo.",
    "....ofhfffo.",
    "....ofhfffo.",
    "....ofhfffo.",
    "....offfffo.",
    "....offfffo.",
    "....offfffo.",
    "...ooffffso.",
    "..ooffffffo.",
    ".ooffffffffo",
    "offfffffffso",
    "oddddddddddo",
    "oddddddddddo",
    "oooooooooooo",
]


def gummi_pal(edge, fill, dark, hi):
    return {"o": edge, "f": fill, "d": dark, "h": hi, "s": dark}


WINTER = [
    "...l.ll.l.l.",
    "...lfffffffl",
    "...leeeeeeel",
    "....obbbbbo.",
    "....obdbbbo.",
    "....obbbbbo.",
    "....obdbbbo.",
    "....obbbbbo.",
    "...oobbbbbo.",
    ".oobbbbbbbo.",
    "obbbbbbbbbbo",
    "oddddddddddo",
    "ododdododdoo",
    "oooooooooooo",
]


def winter_pal(edge, fill, dark):
    return {"o": edge, "b": fill, "d": dark, "f": "#f3ead2", "e": "#d9cdb0", "l": "#c9bd9f"}


# Sneaker und Crocs gibt es nur in Janas Farben (keine Varianten, 2026-10-07)
SNEAKER_VARIANTS = {
    "i-shoes-sneaker": sneaker_pal("#ea8fa1"),     # weiß/rosa (Jana)
}
CROCS_VARIANTS = {
    "i-shoes-sandalen": crocs_pal("#f39a46", "#c4691f", "#d9782c", "#fbc78e", "#e0842f"),     # orange (Jana)
}
GUMMI_VARIANTS = {
    "i-shoes-gummistiefel": gummi_pal("#8f67b0", "#b898d8", "#7e5aa0", "#dccdf0"),     # flieder (Jana)
    "i-shoes-gummistiefel-v2": gummi_pal("#cfad36", "#f0c93f", "#af932e", "#fbe58c"),  # gelb (wie bisher)
}
WINTER_VARIANTS = {
    "i-shoes-winterstiefel": winter_pal("#77543d", "#8a6247", "#654734"),     # braun (wie bisher)
    "i-shoes-winterstiefel-v2": winter_pal("#4b5665", "#627082", "#3f4955"),  # anthrazit/blaugrau
}


def shoes():
    out = {}
    for sid, pal in SNEAKER_VARIANTS.items():
        out[sid] = shoe_pair(SNEAKER, pal, sid)
    for sid, pal in CROCS_VARIANTS.items():
        out[sid] = shoe_pair(CROCS, pal, sid, CROCS_OVER)
    for sid, pal in GUMMI_VARIANTS.items():
        out[sid] = shoe_pair(GUMMI, pal, sid)
    for sid, pal in WINTER_VARIANTS.items():
        out[sid] = shoe_pair(WINTER, pal, sid)
    return out


# ---------------------------------------------------------------------------
# Hosen. Alle Beinmitten bei +-5,5 Px von der Symbolmitte (siehe NOTES).
# Es steht nur die linke Hälfte da (inkl. der halben Lücke), rechts wird gespiegelt.
# Spalte 0 = äußerer Rand.
# ---------------------------------------------------------------------------

# Jeans / Shorts: 20 breit, Beine 9 breit (Spalten 0..8), Lücke 2 (Spalte 9)
#            0123456789
JEANS_TOP = [
    "..aaaaaaaa",
    "..abbbbbbb",
    "..abbbbbbb",
    ".aaaaaaaaa",
    "abbbbbbbbb",
    "abcbbbbbbb",
    "abbbbbbbbb",
    "abbbbbbbbb",
]
JEANS_CROTCH = "abbbbbbbba"            # Zeile mit der Lücken-Oberkante
JEANS_LEG = "abbbbbbba."
JEANS_LEG_SHADE = "auuuuuuua."
JEANS_HEM = "aaaaaaaaa."
SKIN_TOP = ".dsssssd.."                # Hautbein 7 breit (Spalten 1..7), oberste Reihe im Schatten des Saums
SKIN_LEG = ".deeeeed.."


def hose_lang_rows():
    return JEANS_TOP + ["abbbbbbbbb", JEANS_CROTCH] + [JEANS_LEG] * 15 + [JEANS_LEG_SHADE, JEANS_HEM]


def hose_kurz_rows():
    return (JEANS_TOP + [JEANS_CROTCH] + [JEANS_LEG] * 9 + [JEANS_LEG_SHADE, JEANS_HEM]
            + [SKIN_TOP] + [SKIN_LEG] * 6)


JEANS_PAL = {"a": "#5f7c9e", "b": "#6e90b8", "c": "#506986", "u": "#6585ac",
             "d": "#cf9f78", "e": "#f4cfae", "s": "#e6b990"}
SAND_PAL = {"a": "#a78c63", "b": "#c2a373", "c": "#8e7754", "u": "#b39767",
            "d": "#cf9f78", "e": "#f4cfae", "s": "#e6b990"}

# Leggings: 18 breit, Beine 7 breit (Spalten 0..6), Lücke 4 (Spalten 7, 8)
#            012345678
LEGGINGS = [
    "..ooooooo",
    "..occcccc",
    "..occcccc",
    ".oooooooo",
    "offffffff",
    "offffffff",
    "offffffff",
    "offffffff",
    "offffffff",
    "offffffff",
    "offffffoo",
] + ["offfffo.."] * 14 + ["ossssso..", "ooooooo.."]
LEGGINGS_SHINE = {(1, y): "h" for y in range(14, 18)} | {(12, y): "h" for y in range(14, 18)}


def leggings_pal(fill, edge, band, hi, shade):
    return {"o": edge, "f": fill, "c": band, "h": hi, "s": shade}


# Schneehose: 22 breit, Beine 10 breit (Spalten 0..9), Lücke 2 (Spalte 10); Latz und Träger oben.
#          01234567890
SNOW = [
    "....ofo....",
    "....ofo....",
    "...oooooooo",
    "...offfffff",
    "...offfffff",
    "...offfffff",
    ".oooooooooo",
    "offffffffff",
    "offffffffff",
    "ossssssssss",
    "offffffffff",
    "offffffffff",
    "offfffffffo",
    "offffffffo.",
    "offffffffo.",
    "osssssssso.",
    "offffffffo.",
    "offffffffo.",
    "offffffffo.",
    "osssssssso.",
    "offffffffo.",
    "offffffffo.",
    "orrrrrrrro.",
    "offffffffo.",
    "occcccccco.",
    "occcccccco.",
    "oooooooooo.",
]
SNOW_SHINE = {(2, 8): "h", (2, 13): "h", (2, 14): "h", (14, 8): "h", (14, 13): "h", (14, 14): "h"}


def snow_pal(fill, edge, shade, hi, cuff, refl):
    return {"o": edge, "f": fill, "s": shade, "h": hi, "c": cuff, "r": refl}


# Matschhose: 22 breit, Beine 10 breit (Spalten 0..9), Lücke 2 (Spalte 10); Träger-Spitzen, glatt, Gummizug unten.
#          01234567890
RAIN = [
    ".....ofo...",
    ".....ofo...",
    "..ooooooooo",
    "..occcccccc",
    "..occcccccc",
    ".oooooooooo",
    "offffffffff",
    "offffffffff",
    "offffffffff",
    "offffffffff",
    "offffffffff",
    "offffffffff",
    "offfffffffo",
] + ["offffffffo."] * 10 + ["osssssssso.", ".occccccco.", ".occccccco.", ".ooooooooo."]
RAIN_SHINE = (
    {(2, y): "h" for y in range(8, 11)} | {(2, y): "h" for y in range(14, 19)}
    | {(14, y): "h" for y in range(8, 11)} | {(14, y): "h" for y in range(14, 19)}
)


def rain_pal(fill, edge, shade, hi, band):
    return {"o": edge, "f": fill, "s": shade, "h": hi, "c": band}


def hosen():
    out = {}
    out["i-bottom-hose-kurz"] = pants(hose_kurz_rows(), SAND_PAL, name="kurz")
    out["i-bottom-hose-kurz-v2"] = pants(hose_kurz_rows(), JEANS_PAL, name="kurz-v2")
    out["i-bottom-hose-lang"] = pants(hose_lang_rows(), JEANS_PAL, name="lang")
    out["i-bottom-hose-lang-v2"] = pants(LEGGINGS, leggings_pal("#3a4d7e", "#2c3c66", "#465a90", "#6277aa", "#32426f"),
                                         LEGGINGS_SHINE, "leggings")
    out["i-bottom-hose-lang-v3"] = pants(LEGGINGS, leggings_pal("#e67fa3", "#b65a7d", "#ec92b2", "#f6bbd0", "#d96f96"),
                                         LEGGINGS_SHINE, "leggings-v3")
    out["i-bottom-schneehose"] = pants(SNOW, snow_pal("#3f7d5a", "#2f5f46", "#33684b", "#69a883", "#5b9873", "#e8e2c6"),
                                       SNOW_SHINE, "schneehose")
    out["i-bottom-matschhose"] = pants(RAIN, rain_pal("#f4a92a", "#c97a12", "#e29420", "#fcd98a", "#e39a1c"),
                                       RAIN_SHINE, "matschhose")
    out["i-bottom-matschhose-v2"] = pants(RAIN, rain_pal("#45a8ad", "#2f8388", "#37939a", "#9fdadb", "#3b979c"),
                                          RAIN_SHINE, "matschhose-v2")
    return out


NOTES = """
MASSE FÜR DIE INTEGRATION (Pixel; x von links, Symbolmitte M = Kante zwischen den beiden mittleren Pixeln)

Alle Symbolbreiten sind gerade, alle Symbole sind symmetrisch. Die App setzt jedes Symbol über die Mitte
der eigenen Bounding-Box auf die Spaltenmitte; dann sitzen Hosen und Schuhe pixelgenau übereinander.
Der Ursprung der Koordinaten in build() ist beliebig (x/y ab 0, y wächst nach unten).

Schuhe (ein Symbol = ein Paar, 26 breit, M = x 13)
  linker Schuh x 0..11 (Spitze links), Lücke x 12..13, rechter Schuh x 14..25 (gespiegelt)
  Schaft 7 breit: x 4..10 und x 15..21, also Schaftmitte bei M -5,5 und M +5,5
  Sohle/Ferse 1 Px hinter dem Schaft, Spitze 4 Px vor dem Schaft (3 Px vor einem 9 breiten Hosenbein)
  Höhen: Sneaker 11, Crocs 10, Gummistiefel 17, Winterstiefel 14. Oberste Zeile = Schaftrand
  (Winterstiefel: Fellrand 9 breit, x 3..11). Das Schuhfenster beginnt direkt unter dem Hosenfenster.

Hosen (alle 27 hoch, oben bündig; die unterste Zeile liegt direkt über der obersten Schuhzeile)
  Beinmitte M -5,5 / M +5,5 bei allen langen Hosen und den Hautbeinen (Kante x = M-10 bis M-1 usw.):
    Jeans, Shorts    20 breit, Beine 9 breit  [M-10, M-1) und [M+1, M+10), Lücke 2
    Hautbeine        7 breit [M-9, M-2) und [M+2, M+9), 7 hoch (unter 20 hohen Shorts), Lücke 4
    Leggings         18 breit, Beine 7 breit  [M-9, M-2) und [M+2, M+9), Lücke 4 (liegt exakt auf dem Schaft)
    Schneehose       22 breit, Beine 10 breit [M-11, M-1) und [M+1, M+11), Lücke 2 (Beinmitte M -6)
    Matschhose       22 breit, Beine 10 breit wie Schneehose, unterste 3 Zeilen (Gummizug) 9 breit
                     [M-10, M-1), also Beinmitte M -5,5 und genau so breit wie ein Jeansbein
  Die Schäfte (7 breit) stehen 0 (Leggings, Hautbeine) bis 2 Px (Schneehose außen) innerhalb der Beine; die Spitzen
  ragen 3 Px (Jeans), 4 Px (Leggings, Hautbeine), 2 Px (Schneehose, Matschhose) über das jeweilige Bein hinaus.
  Der Fellrand der Winterstiefel ist 9 breit (x 3..11), also genau so breit wie ein Jeansbein.
  Breiten: Jeans 20, Leggings 18, Schneehose 22, Matschhose 22; innerhalb eines Teils (z. B. hose-lang v1..v3)
  ist nur die Leggings 2 Px schmaler als die Jeans (Auftrag: schmalere Beine). Kurze Hose v1/v2: 20 x 27.
"""


def build():
    out = shoes()
    out.update(hosen())
    return out


# ---------------------------------------------------------------------------
# Prüfung und Vorschau
# ---------------------------------------------------------------------------

def check(icons=None):
    """Prüft die Registrierung: gerade Breiten, Höhen, Beinmitten, Schaftmitten. Gibt Fehlerliste zurück."""
    from pxl import bbox
    icons = icons or build()
    errors = []

    def runs(px, y, x0, w):
        xs = sorted(x for (x, yy) in px if yy == y)
        out, start = [], None
        for a, b in zip(xs, xs[1:] + [None]):
            if start is None:
                start = a
            if b != a + 1:
                out.append((start, a))
                start = None
        return out

    for sid, px in icons.items():
        x0, y0, w, h = bbox(px)
        mid = x0 + w / 2
        if w % 2:
            errors.append(f"{sid}: Breite {w} ist ungerade")
        if sid.startswith("i-shoes"):
            if (w, y0) != (26, 0) or h > 17:
                errors.append(f"{sid}: Paar {w}x{h}")
            y = next(y for y in range(h) if any(b - a + 1 >= 7 for a, b in runs(px, y, x0, w)))
            left = [r for r in runs(px, y, x0, w) if r[1] < mid][-1]
            c = (left[0] + left[1] + 1) / 2 - mid
            if c != -5.5:
                errors.append(f"{sid}: Schaftmitte {c} statt -5,5")
        else:
            if h != 27:
                errors.append(f"{sid}: Hose {h} hoch statt 27")
            left = [r for r in runs(px, y0 + h - 1, x0, w) if r[1] < mid][-1]
            c = (left[0] + left[1] + 1) / 2 - mid
            if c not in (-5.5, -6.0):
                errors.append(f"{sid}: Beinmitte {c}")
    return errors


def _labels_grid(icons, pants_ids, shoe_ids, out, scale=6, bg="#f8f4e5"):
    from PIL import Image, ImageDraw
    from pxl import bbox, _draw, _hex
    cw, pad, top, left = 30 * scale, 8, 30, 150
    ch = (27 + 17) * scale + 2 * pad
    img = Image.new("RGB", (left + cw * len(pants_ids), top + ch * len(shoe_ids)), _hex(bg))
    d = ImageDraw.Draw(img)
    for c, p in enumerate(pants_ids):
        d.text((left + c * cw + 4, 6), p.replace("i-bottom-", ""), fill=(90, 80, 70))
    for r, s in enumerate(shoe_ids):
        y = top + r * ch + pad
        d.text((4, y + 27 * scale), s.replace("i-shoes-", ""), fill=(90, 80, 70))
        for c, p in enumerate(pants_ids):
            ox = left + c * cw
            _draw(img, icons[p], ox + (cw - bbox(icons[p])[2] * scale) // 2, y, scale)
            _draw(img, icons[s], ox + (cw - bbox(icons[s])[2] * scale) // 2, y + 27 * scale, scale)
    img.save(out)


def previews(outdir=None):
    from pxl import sheet, app_frames, original_px
    outdir = Path(outdir or Path(__file__).resolve().parent.parent / ".wip" / "art" / "schuhe_hosen")
    outdir.mkdir(parents=True, exist_ok=True)
    I = build()
    shoes_, hosen_ = [k for k in I if k.startswith("i-shoes")], [k for k in I if k.startswith("i-bottom")]
    sheet({k: I[k] for k in shoes_}, outdir / "kontaktbogen-schuhe.png", scale=10, cols=4)
    sheet({k: I[k] for k in hosen_}, outdir / "kontaktbogen-hosen.png", scale=10, cols=4)
    _labels_grid(I, hosen_, shoes_, outdir / "kombinationen-hosen-x-schuhe.png")
    O = original_px      # Platzhalter für Oberteile, Kopf und Zubehör (aus dem alten Stand)
    acc = [O("i-acc-handschuhe"), O("i-acc-schal")]
    f1 = [
        dict(head=O("i-head-sonnenhut"), top=O("i-top-tshirt"), bottom=I["i-bottom-hose-kurz"], shoes=I["i-shoes-sandalen"], band=0),
        dict(top=O("i-top-tshirt"), bottom=I["i-bottom-hose-kurz-v2"], shoes=I["i-shoes-sneaker"], band=1),
        dict(top=O("i-top-pullover"), bottom=I["i-bottom-hose-lang"], shoes=I["i-shoes-sneaker"], band=2),
        dict(top=O("i-top-regenjacke"), bottom=I["i-bottom-hose-lang-v2"], shoes=I["i-shoes-sneaker"], band=3),
        dict(top=O("i-top-regenjacke"), bottom=I["i-bottom-hose-lang"], shoes=I["i-shoes-gummistiefel"], band=4),
        dict(head=O("i-head-muetze"), top=O("i-top-winterjacke"), bottom=I["i-bottom-matschhose"], shoes=I["i-shoes-winterstiefel"], acc=acc, band=5),
        dict(head=O("i-head-muetze"), top=O("i-top-winterjacke"), bottom=I["i-bottom-schneehose"], shoes=I["i-shoes-winterstiefel"], acc=acc, band=6),
    ]
    app_frames(f1, outdir / "app-outfits-1.png", zoom=2, labels=[
        "heiss: kurz + Crocs", "warm: kurz-v2 + Sneaker", "mild: Jeans + Sneaker-v2", "kuehl: Leggings + Sneaker",
        "kalt: Jeans + Gummistiefel", "eisig: Matschhose + Winter", "frost: Schneehose + Winter"])
    f2 = [
        dict(head=O("i-head-sonnenhut"), top=O("i-top-tshirt"), bottom=I["i-bottom-hose-kurz-v2"], shoes=I["i-shoes-sandalen"], band=0),
        dict(top=O("i-top-tshirt"), bottom=I["i-bottom-hose-kurz"], shoes=I["i-shoes-sneaker"], band=1),
        dict(top=O("i-top-pullover"), bottom=I["i-bottom-hose-lang-v3"], shoes=I["i-shoes-sneaker"], band=2),
        dict(top=O("i-top-regenjacke"), bottom=I["i-bottom-hose-lang"], shoes=I["i-shoes-gummistiefel-v2"], band=3),
        dict(top=O("i-top-regenjacke"), bottom=I["i-bottom-matschhose-v2"], shoes=I["i-shoes-gummistiefel"], band=4),
        dict(head=O("i-head-muetze"), top=O("i-top-winterjacke"), bottom=I["i-bottom-hose-lang-v2"], shoes=I["i-shoes-winterstiefel-v2"], acc=acc, band=5),
        dict(head=O("i-head-muetze"), top=O("i-top-winterjacke"), bottom=I["i-bottom-schneehose"], shoes=I["i-shoes-winterstiefel-v2"], acc=acc, band=6),
    ]
    app_frames(f2, outdir / "app-outfits-2.png", zoom=2, labels=[
        "heiss: kurz-v2 + Crocs rosa", "warm: kurz + Sneaker blau", "mild: Leggings rosa + Sneaker blau",
        "kuehl: Jeans + Gummi gelb", "kalt+Regen: Matsch-v2 + Gummi flieder", "eisig: Leggings navy + Winter-v2",
        "frost: Schneehose + Winter-v2"])
    return outdir


if __name__ == "__main__":
    errs = check()
    print(len(build()), "Symbole,", "Registrierung ok" if not errs else errs)
    if "--no-preview" not in sys.argv:
        print("Vorschauen:", previews())
