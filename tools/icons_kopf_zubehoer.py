#!/usr/bin/env python3
"""
Icon-Gruppe `kopf_zubehoer`: Kopf (Muetze, Basecap), Zubehoer (Schal, Handschuhe,
Sonnencreme, Sonnenbrille), Umschalter innen/aussen sowie neu gezeichnete Wetter-
und Hinweis-Icons (niesel, regen, bedeckt, nebel, glaette). Schnee, Gewitter, Klar
usw. bleiben unveraendert in tools/pixel_icons.py.

Schnittstelle: build() -> {symbol-id: {(x, y): "#rrggbb"}}.
Kleidung, Zubehoer und Umschalter stehen als ASCII-Art im Modul (Farben aus Paletten,
damit Varianten reine Umfaerbungen desselben Rasters sind: gleiche Groesse). Nur die
Wolken der Wetter-Icons entstehen aus Kreisen (wie in pixel_icons.py), Tropfen und
Nebelstreifen aus Rechtecken. Keine Abhaengigkeit von index.html.

Vorschau-Bilder (nach .wip/art/kopf_zubehoer/): python3 tools/icons_kopf_zubehoer.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pxl import Canvas, bbox, clip, disc, rect  # noqa: E402


# ---------------------------------------------------------------- Helfer

def art(rows, pal, ox=0, oy=0):
    """ASCII-Raster -> Canvas. '.' ist leer; alle Zeilen muessen gleich lang sein."""
    w = {len(r) for r in rows}
    assert len(w) == 1, f"ungleiche Zeilenlaenge: {[(i, len(r)) for i, r in enumerate(rows)]}"
    cv = Canvas(w.pop(), len(rows))
    cv.art(rows, pal, ox, oy)
    return cv


def mirror_pair(left, gap):
    """Linkes Teil wie gezeichnet, rechtes gespiegelt, `gap` Pixel Luecke."""
    x0, y0, w, h = bbox(left.px)
    cv = Canvas(2 * w + gap, h)
    for (x, y), c in left.px.items():
        cv.px[(x - x0, y - y0)] = c
        cv.px[(2 * w + gap - 1 - (x - x0), y - y0)] = c
    return cv


# ---------------------------------------------------------------- Muetze (Bommelmuetze)
# 16 x 15. o Kontur, f Fuellung, s Schatten, h Licht, r Rippe (Bund), p Bund-Licht

MUETZE = [
    "......oooo......",
    ".....ohhffo.....",
    ".....ohfffo.....",
    ".....offsso.....",
    ".....oooooo.....",
    "...oohhfffsoo...",
    "..ohhfffffffso..",
    ".ohhfffffffffso.",
    ".ohffffffffffso.",
    ".offfffffffffso.",
    ".osssssssssssso.",
    ".oooooooooooooo.",
    "oprprprprprprpro",
    "ofsfsfsfsfsfsfso",
    ".oooooooooooooo.",
]

# Farbtabellen: (Kontur, Fuellung, Schatten, Licht, Rippe, Bund-Licht)
MUETZE_COLORS = {
    "senf":      dict(o="#b0801f", f="#d9a73a", s="#c4952c", h="#efcd78", r="#c08f2a", p="#e6bb55"),
    "dunkelgruen": dict(o="#2f5f43", f="#3f7d58", s="#366d4c", h="#6fa686", r="#33694a", p="#4c8d66"),
    "flieder":   dict(o="#9b7fc0", f="#d0b3ed", s="#bf9fe0", h="#ece0fa", r="#b896dc", p="#e0cdf4"),
}


def head_muetze(color="senf"):
    return art(MUETZE, MUETZE_COLORS[color])


# ---------------------------------------------------------------- Basecap (i-head-sonnenhut)
# 25 x 12, Seitenansicht, Schirm nach rechts.
# o Kontur, f Fuellung, s Schatten, h Licht, p Naht, q Schirm-Kontur (und Knopf),
# w Schirm oben, d Schirm unten

CAP = [
    ".......qq................",
    ".....oooooo..............",
    "...oohffpffoo............",
    "..ohfffffpfffo...........",
    ".ohhffffffpfffo..........",
    ".ohffffffffpffo..........",
    "ohhffffffffpfffo.........",
    "offfffffffffpfqqqqqqqq...",
    "osssssssssssssqwwwwwwwqq.",
    "oooooooooooooqqddddddd" "wwq",
    "..............qqqqqqqqddq",
    "......................qq.",
]

CAP_COLORS = {
    "gruen": dict(o="#3b7f50", f="#5cac72", s="#4a9a62", h="#9bd8ac", p="#4a9a62", q="#3b7f50", w="#4c9d66", d="#3f8a57"),
    "orange": dict(o="#b25a1c", f="#ee8a3a", s="#d9742c", h="#f9bc84", p="#d9742c", q="#b25a1c", w="#d9742c", d="#c4651f"),
    "weiss": dict(o="#8794a6", f="#f7f7f3", s="#dde2e8", h="#ffffff", p="#d3dae3", q="#336da6", w="#4f93d4", d="#3f7fc0"),
}


def head_cap(color="gruen"):
    return art(CAP, CAP_COLORS[color])


# ---------------------------------------------------------------- Schal (16 x 19)
# Wickel oben, hinten ein kurzes, vorn ein langes Ende, Streifen, Fransen (2 breit).
# o/f/s/h Kontur/Fuellung/Schatten/Licht vorn, k/j Fuellung/Kontur hinten,
# c Streifen vorn, d Streifen hinten

SCHAL = [
    "..oooooooooooo..",
    ".ohhfffffffffso.",
    "ohhfffffffffffso",
    "offfffffffffffso",
    "osssssssssssssso",
    ".oooooooooooooo.",
    ".jkkkkkoffffffo.",
    ".jkkkkkoffffffo.",
    ".jkkkkkoffffffo.",
    ".jdddddocccccco.",
    ".jdddddocccccco.",
    ".jkkkkkoffffffo.",
    ".jjjjjjoffffffo.",
    ".kk..kkocccccco.",
    ".kk..kkocccccco.",
    ".......offffffo.",
    ".......oooooooo.",
    ".......ff.ff.ff.",
    ".......ss.ss.ss.",
]

SCHAL_COLORS = {
    "lila":  dict(o="#7c63b0", f="#a58bd8", s="#9275c6", h="#d3c4f0", c="#fbf1e6", k="#9272c4", j="#6a529a", d="#e6dcf2"),
    "gruen": dict(o="#4f9a5c", f="#78c183", s="#64b072", h="#bfe6c4", c="#fbf3dc", k="#66b374", j="#3f854c", d="#e3efd3"),
}


def acc_schal(color="lila"):
    return art(SCHAL, SCHAL_COLORS[color])


# ---------------------------------------------------------------- Halstuch (18 x 14)
# Dreieckiges Tuch um den Hals: oben ein zusammengelegtes Band mit zwei Zipfeln (der Knoten),
# darunter die Spitze nach unten, drei Tupfen (2 x 2).

HALS_ROWS = [14, 12, 12, 10, 8, 8, 6, 4, 2]          # Breite der Dreieckszeilen unter dem Band, mittig auf Spalte 8/9
HALS_COLORS = {
    "rosa":     dict(fill="#ef9db4", outline="#c4708a", shade="#dc86a0", dot="#fde9e0"),
    "senf":     dict(fill="#e8bb4e", outline="#b88a28", shade="#d4a23a", dot="#fdf0c8"),
    "hellblau": dict(fill="#8ec1e6", outline="#5b8db5", shade="#79b0d8", dot="#f3f7fb"),
}


def acc_halstuch(color="rosa"):
    pal = HALS_COLORS[color]
    cv = Canvas(18, 14)
    band = rect(2, 2, 14, 3)
    tails = {(0, 0), (1, 0), (2, 0), (1, 1), (2, 1), (15, 0), (16, 0), (17, 0), (15, 1), (16, 1)}
    tri = set()
    for i, w in enumerate(HALS_ROWS):
        y = 5 + i
        tri |= {(x, y) for x in range(9 - w // 2, 9 + w // 2)}
    cv.paint(tri | band | tails, pal["fill"], pal["outline"], pal["shade"])
    for dx, dy in ((5, 6), (11, 6), (8, 9)):
        cv.dots([(dx, dy), (dx + 1, dy), (dx, dy + 1), (dx + 1, dy + 1)], pal["dot"])
    for x in range(3, 15):                              # Falz zwischen Band und Dreieck
        if (x, 5) in tri:
            cv.px[(x, 4)] = pal["outline"]
    return cv


# ---------------------------------------------------------------- Faeustlinge (24 x 16)
# Linker Fausthandschuh 11 x 16, Daumen nach rechts (innen), rechter gespiegelt, 2 Pixel Luecke.
# o/f/s/h Kontur/Fuellung/Schatten/Licht, O/r/q Bund-Kontur/Bund/Rippe

MITT = [
    "..oooo.....",
    ".ohhffo....",
    "ohhffffo...",
    "ohffffffoo.",
    "offfffffffo",
    "offfffffffo",
    "offfffffsso",
    "offffffsoo.",
    "offffffo...",
    "offffffo...",
    "osssssso...",
    "OOOOOOOO...",
    "OrqrqrqO...",
    "OrqrqrqO...",
    "OrqrqrqO...",
    "OOOOOOOO...",
]

MITT_COLORS = {
    "rosa": dict(o="#c9728a", f="#ee9db3", s="#dc86a0", h="#f9cbd8", O="#a3302b", r="#d94840", q="#c03a34"),
    "senf": dict(o="#bf8a28", f="#f0bb43", s="#d9a236", h="#f9dc8a", O="#bf8a28", r="#fdf0c8", q="#e8cf8a"),
}


def acc_handschuhe(color="rosa"):
    return mirror_pair(art(MITT, MITT_COLORS[color]), 2)


# ---------------------------------------------------------------- Sonnencreme (10 x 20)
# Weisse Flasche mit blauem Schraubdeckel und grossem blauem Sonnenmotiv.
# o Kontur, w Weiss, s Schatten, b Motiv, N/H/B/M Deckel (Kontur, Licht, Flaeche, Rille)

SONNENCREME = [
    "..NNNNNN..",
    "..NHBBMN..",
    "..NHBBMN..",
    "..NNNNNN..",
    ".oooooooo.",
    "owwwwwwwso",
    "owwwwwwwso",
    "owwwwwwwso",
    "owwbwwbwso",
    "owwwbbwwso",
    "obwbbbbwbo",
    "owbbbbbbso",
    "owbbbbbbso",
    "obwbbbbwbo",
    "owwwbbwwso",
    "owwbwwbwso",
    "owwwwwwwso",
    "owwwwwwwso",
    "osssssssso",
    ".oooooooo.",
]
SONNENCREME_COLORS = dict(o="#7f8fa8", w="#fbfbf8", s="#e1e7ee", b="#4a8fd6",
                          N="#2f6aa8", H="#79b2ea", B="#4a8fd6", M="#3a76bd")


def acc_sonnencreme():
    return art(SONNENCREME, SONNENCREME_COLORS)


# ---------------------------------------------------------------- Sonnenbrille (24 x 9)
# Zwei runde Glaeser (je 9 breit), Steg 2, Buegel je 2. o Kontur, f Fassung, l Glas, k Glas unten, h Glanz

BRILLE_LENS = [
    "..ooooo..",
    ".offfffo.",
    "offhllffo",
    "ofhllllfo",
    "oflllllfo",
    "oflllllfo",
    "offllkffo",
    ".offfffo.",
    "..ooooo..",
]
BRILLE_COLORS = {
    "koralle": dict(o="#b9503f", f="#d9705e", l="#40607d", k="#34506b", h="#9db6c6"),
    "gelb":    dict(o="#b5841c", f="#f2c443", l="#40607d", k="#34506b", h="#9db6c6"),
}


def acc_sonnenbrille(color="koralle"):
    rows = []
    for i, lens in enumerate(BRILLE_LENS):
        temple = {1: "oo", 2: "ff", 3: "oo"}.get(i, "..")
        bridge = {2: "oo", 3: "ff", 4: "oo"}.get(i, "..")
        rows.append(temple + lens + bridge + lens + temple)
    return art(rows, BRILLE_COLORS[color])


# ---------------------------------------------------------------- Umschalter innen / aussen (14 x 14)
# Haus: o Dach-Kontur, r Dach, R Dach-Schatten, e Wand-Kontur, w Wand, b/B Fenster, d Tuer, y Knauf

HAUS = [
    "......oo......",
    ".....orro.....",
    "....orrrro....",
    "...orrrrrro...",
    "..orrrrrrrro..",
    ".orrrrrrrrrro.",
    "oRRRRRRRRRRRRo",
    "oooooooooooooo",
    ".ewwwwwwwwwwe.",
    ".ewbbbwwdddwe.",
    ".ewbbbwwdddwe.",
    ".ewBBBwwddywe.",
    ".ewwwwwwdddwe.",
    ".eeeeeeeeeeee.",
]
HAUS_COLORS = dict(o="#96402e", r="#c8593f", R="#b04b35", e="#a8864f", w="#f5e2b8",
                   b="#78b8e8", B="#4f8fc9", d="#8f5d3e", y="#f2c444")

# Baum mit Sonne: o Kontur, f Krone, s Schatten, h Licht, T/t Stamm, Y/y Sonne
BAUM = [
    "...........YY.",
    "...oooo...YyyY",
    ".oohhffoo.YyyY",
    ".ohhffffo..YY.",
    "ohfffffffo....",
    "offfffffso....",
    "offfffffso....",
    "offfffffso....",
    ".offffssso....",
    ".oosssssoo....",
    "...oooo.......",
    "...TttT.......",
    "...TttT.......",
    "...TTTT.......",
]
BAUM_COLORS = dict(o="#478a4c", f="#6fb26f", s="#5da061", h="#a6d9a0", T="#75492c", t="#a06b45",
                   Y="#d98a28", y="#f8cd4e")


def ui_innen():
    return art(HAUS, HAUS_COLORS)


def ui_aussen():
    return art(BAUM, BAUM_COLORS)


# ---------------------------------------------------------------- Wetter / Hinweise (16 x 16, 3 pt je Pixel)
# Grundsatz: kleineres Pixel = groeberes Motiv. Tropfen und Striche sind 2 Pixel breit, keine Einzelpunkte.
# Die Wolke ist dieselbe wie in den uebrigen Wetter-Icons (drei Woelbungen, flacher Boden).

CLOUD = dict(fill="#fbfdff", outline="#7088a0", shade="#cddbe9")
CLOUD_GREY = dict(fill="#cfdae7", outline="#657d96", shade="#aebfd1")
DROP_LIGHT = "#5aa0e0"      # Niesel
DROP = "#3f8ad6"            # Regen (etwas dunkler und kraeftiger)
FOG = "#9db0c4"


def cloud_mask(ox, oy):
    """Wolke 14 x 9: links kleine, in der Mitte grosse, rechts mittlere Woelbung, flacher Boden."""
    m = set()
    m |= disc(ox + 3.3, oy + 5.9, 2.7)
    m |= disc(ox + 7.3, oy + 4.2, 3.7)
    m |= disc(ox + 11.0, oy + 5.7, 2.9)
    m |= rect(ox + 3, oy + 6, 9, 3)
    return clip(m, y1=oy + 8)


def draw_cloud(cv, ox, oy, pal):
    cv.paint(cloud_mask(ox, oy), pal["fill"], pal["outline"], pal["shade"])


def drops(cv, cells, color, h):
    """Tropfen: 2 Pixel breit, h Pixel hoch. cells sind die linken oberen Ecken."""
    for x, y in cells:
        cv.flat(rect(x, y, 2, h), color)


def wx_niesel():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 1, CLOUD)
    drops(cv, [(3, 11), (7, 12), (11, 11)], DROP_LIGHT, 2)
    return cv


def wx_regen():
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD_GREY)
    drops(cv, [(2, 10), (7, 10), (12, 10)], DROP, 3)
    drops(cv, [(4, 13), (9, 13)], DROP, 3)
    return cv


def wx_bedeckt():
    """Zwei Wolken, deutlich gestaffelt: hinten grau links oben, vorn weiss rechts unten."""
    cv = Canvas(16, 16)
    draw_cloud(cv, 0, 0, CLOUD_GREY)
    draw_cloud(cv, 2, 6, CLOUD)
    return cv


def wx_nebel():
    """Ganze graue Wolke, darunter zwei dicke Nebelstreifen (2 Pixel hoch, versetzt)."""
    cv = Canvas(16, 16)
    draw_cloud(cv, 1, 0, CLOUD_GREY)
    cv.flat(rect(4, 10, 10, 2), FOG)
    cv.flat(rect(2, 13, 10, 2), FOG)
    return cv


# Hinweis Glaette: Winterstiefel mit Fellrand, nach hinten gekippt, auf einer Eisplatte, zwei dicke Rutschstriche dahinter.
# o Stiefel-Kontur, b Stiefel, d Sohle, c Fell, e Fell-Schatten, m Rutschstrich,
# i Eis-Kontur, j Eis, k Eis-Schatten, w Eis-Glanz

GLAETTE = [
    "................",
    "...ooooooo......",
    "...occccco......",
    "...oeeeeeo......",
    ".....obbbo......",
    "mmmm.obbbo......",
    "mmmm..obbbo.....",
    "......obbbo.....",
    ".mmm..obbbbo....",
    ".mmm..obbbbbbo..",
    "......oddddddddo",
    ".iiiiiiiiiiiiii.",
    "iijwwwjjjjjwwjjk",
    "ikkkkkkkkkkkkkki",
    ".iiiiiiiiiiiiii.",
    "................",
]
GLAETTE_COLORS = dict(o="#5e3f2b", b="#8a6247", d="#4d3426", c="#f3ead2", e="#d9cdb0", m="#8fa6ba",
                      i="#5aa6cf", j="#d4effb", k="#aedcf0", w="#ffffff")


def hint_glaette():
    return art(GLAETTE, GLAETTE_COLORS)


def build():
    out = {}
    out["i-head-muetze"] = head_muetze("senf").px
    out["i-head-muetze-v2"] = head_muetze("dunkelgruen").px
    out["i-head-muetze-v3"] = head_muetze("flieder").px
    out["i-head-sonnenhut"] = head_cap("gruen").px
    out["i-head-sonnenhut-v2"] = head_cap("orange").px
    out["i-head-sonnenhut-v3"] = head_cap("weiss").px
    out["i-acc-schal"] = acc_schal("lila").px
    out["i-acc-schal-v2"] = acc_schal("gruen").px
    out["i-acc-halstuch"] = acc_halstuch("rosa").px
    out["i-acc-halstuch-v2"] = acc_halstuch("senf").px
    out["i-acc-halstuch-v3"] = acc_halstuch("hellblau").px
    out["i-acc-handschuhe"] = acc_handschuhe("rosa").px
    out["i-acc-handschuhe-v2"] = acc_handschuhe("senf").px
    out["i-acc-sonnencreme"] = acc_sonnencreme().px
    out["i-acc-sonnenbrille"] = acc_sonnenbrille("koralle").px
    out["i-acc-sonnenbrille-v2"] = acc_sonnenbrille("gelb").px
    out["i-ui-innen"] = ui_innen().px
    out["i-ui-aussen"] = ui_aussen().px
    out["i-wx-niesel"] = wx_niesel().px
    out["i-wx-regen"] = wx_regen().px
    out["i-wx-bedeckt"] = wx_bedeckt().px
    out["i-wx-nebel"] = wx_nebel().px
    out["i-hint-glaette"] = hint_glaette().px
    return out


# ---------------------------------------------------------------- Vorschau (nur zum Ansehen, nicht fuer die App)

PREVIEW_DIR = Path(__file__).resolve().parent.parent / ".wip" / "art" / "kopf_zubehoer"


def _recolor(px, mapping):
    return {p: mapping.get(c, c) for p, c in px.items()}


def previews():
    """Schreibt Kontaktboegen und App-Massstab-Bilder nach .wip/art/kopf_zubehoer/.
    Platzhalter-Kleidung kommt aus dem Stand vor der Ueberarbeitung (pxl.original_px)."""
    from pxl import app_frames, original_px, sheet

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    d = build()
    out = lambda name: str(PREVIEW_DIR / name)

    kopf_acc = {k: v for k, v in d.items() if k.startswith(("i-head", "i-acc"))}
    ui_wx = {k: v for k, v in d.items() if k.startswith(("i-ui", "i-wx", "i-hint"))}
    sheet(kopf_acc, out("kontaktbogen-kopf-zubehoer.png"), scale=10, cols=4)
    sheet(ui_wx, out("kontaktbogen-ui-wetter.png"), scale=14, cols=4)

    tshirt = original_px("i-top-tshirt")
    pink = _recolor(tshirt, {"#73b3da": "#ee9bb0", "#6299be": "#c97a90", "#56829c": "#b8667c"})
    white = _recolor(tshirt, {"#73b3da": "#f6f4ee", "#6299be": "#b9b4a6", "#56829c": "#d8d3c4", "#f2f2e9": "#9bb6d4"})
    winter = original_px("i-top-winterjacke")
    snow = original_px("i-top-schneeanzug")
    long_pants = original_px("i-bottom-hose-lang")
    short_pants = original_px("i-bottom-hose-kurz")
    sneaker = original_px("i-shoes-sneaker")
    boots = original_px("i-shoes-winterstiefel")

    # Zubehoer-Reihe unter Platzhalter-Outfit: Trio Creme + Handschuhe + Brille, Handschuhe + Schal
    app_frames([
        dict(head=d["i-head-sonnenhut"], top=tshirt, bottom=short_pants, shoes=sneaker,
             acc=[d["i-acc-sonnencreme"], d["i-acc-sonnenbrille"]], band=1),
        dict(head=d["i-head-muetze"], top=winter, bottom=long_pants, shoes=boots,
             acc=[d["i-acc-sonnencreme"], d["i-acc-handschuhe"], d["i-acc-sonnenbrille"]], band=5),
        dict(head=d["i-head-muetze-v3"], top=snow, bottom=long_pants, shoes=boots,
             acc=[d["i-acc-handschuhe"], d["i-acc-schal"]], band=6),
        dict(head=d["i-head-muetze-v2"], top=winter, bottom=long_pants, shoes=boots,
             acc=[d["i-acc-handschuhe-v2"], d["i-acc-schal-v2"]], band=4),
    ], out("app-zubehoer.png"), zoom=2)
    app_frames([
        dict(head=d["i-head-sonnenhut-v2"], top=white, bottom=short_pants, shoes=sneaker,
             acc=[d["i-acc-sonnencreme"], d["i-acc-sonnenbrille-v2"]], band=0),
        dict(head=d["i-head-muetze-v3"], top=winter, bottom=long_pants, shoes=boots,
             acc=[d["i-acc-handschuhe-v2"], d["i-acc-schal-v3"]], band=5),
        dict(head=d["i-head-muetze-v2"], top=snow, bottom=long_pants, shoes=boots,
             acc=[d["i-acc-sonnencreme"], d["i-acc-handschuhe"], d["i-acc-sonnenbrille"]], band=6),
    ], out("app-zubehoer-2.png"), zoom=2)

    # Muetzen gegen die rote Winterjacke und den Schneeanzug
    app_frames(
        [dict(head=d[k], top=t, bottom=long_pants, shoes=boots, band=b)
         for t, b in ((winter, 5), (snow, 6)) for k in ("i-head-muetze", "i-head-muetze-v2", "i-head-muetze-v3")],
        out("app-muetzen.png"), zoom=2)

    # Cap gegen blaues, pinkes und weisses T-Shirt
    app_frames([
        dict(head=d["i-head-sonnenhut"], top=tshirt, bottom=short_pants, shoes=sneaker, band=2),
        dict(head=d["i-head-sonnenhut"], top=pink, bottom=short_pants, shoes=sneaker, band=1),
        dict(head=d["i-head-sonnenhut-v2"], top=pink, bottom=short_pants, shoes=sneaker, band=1),
        dict(head=d["i-head-sonnenhut-v2"], top=white, bottom=short_pants, shoes=sneaker, band=0),
        dict(head=d["i-head-sonnenhut-v3"], top=pink, bottom=short_pants, shoes=sneaker, band=0),
        dict(head=d["i-head-sonnenhut-v3"], top=white, bottom=short_pants, shoes=sneaker, band=0),
    ], out("app-cap-shirts.png"), zoom=2)

    # Umschalter in 3 pt je Pixel (6 Bildpixel bei zoom 2), aktiv und halbtransparent
    from PIL import Image, ImageDraw

    def blend(c, bg, a):
        return tuple(round(c[i] * a + bg[i] * (1 - a)) for i in range(3))

    def hexrgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    tints = ["#FAF7F0", "#FCF1DC", "#E3EEF6"]
    S, pad = 6, 10
    cells = []
    for tint in tints:
        bg = hexrgb(tint)
        for alpha in (1.0, 0.4):
            for k in ("i-ui-innen", "i-ui-aussen"):
                px = d[k]
                x0, y0, w, h = bbox(px)
                im = Image.new("RGB", (w * S + 2 * pad, h * S + 2 * pad), bg)
                dr = ImageDraw.Draw(im)
                for (x, y), c in px.items():
                    dr.rectangle([pad + (x - x0) * S, pad + (y - y0) * S, pad + (x - x0 + 1) * S - 1, pad + (y - y0 + 1) * S - 1],
                                 fill=blend(hexrgb(c), bg, alpha))
                cells.append(im)
    W = sum(c.width + 4 for c in cells) + 8
    img = Image.new("RGB", (W, cells[0].height + 16), (243, 239, 231))
    x = 8
    for c in cells:
        img.paste(c, (x, 8))
        x += c.width + 4
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(out("ui-umschalter-3pt.png"))
    return d


if __name__ == "__main__":
    icons = previews()
    for sid, px in icons.items():
        x0, y0, w, h = bbox(px)
        print(f"{sid:24s} {w:2d} x {h:2d}")
