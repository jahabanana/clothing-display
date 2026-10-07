#!/usr/bin/env python3
"""
Oberteile (Gruppe `oberteile`): T-Shirt, Longsleeve, Pullover, Kapuzenpullover, Strickjacke,
Teddyjacke, Regenjacke, Schneejacke, Winterjacke, je mit Farbvarianten.

Alle Oberteile sind 24 Kunstpixel hoch (Oberteil-Fenster 24 Zeilen = 132 pt, Layout L3), 24 oder 28 breit.
Die Kapuze ist umgeklappt: ein Ring (geschlossene Ellipse mit eigener Kontur) liegt auf den Schultern, Loch 6 x 3,
oben im Loch ein Futterband, Reißverschluss bzw. Kordeln laufen in den Ring (Entwürfe und Begründung:
.wip/art/kapuze/BERICHT.md).

Schnittstelle: build() -> {symbol_id: {(x, y): "#rrggbb"}}
Alle Raster stehen als ASCII-Art im Modul ('.' = leer), keine Abhängigkeit von index.html.
Schlüssel: Variante 1 = Hauptfarbe (`i-top-name`), weitere `-v2`, `-v3`.

Konturen: Füllung x 0,82, Schatten x 0,72 (family()). Die Raster einer Familie sind je Teil gleich groß;
Varianten sind Umfärbungen desselben Rasters (Teddyjacke v2 und Pullover-Farbblock mit eigener Palette je Zone).

Vorschau:  python3 tools/icons_oberteile.py   (schreibt .wip/art/oberteile/*.png)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxl import Canvas  # noqa: E402


# ---------- Farbhilfen ----------

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in rgb)


def tone(h, f):
    """Farbe dunkler (f < 1) oder heller (f > 1) bei gleichem Farbton."""
    return _hex(tuple(v * f for v in _rgb(h)))


def mix(h1, h2, t):
    """t = 0 -> h1, t = 1 -> h2."""
    a, b = _rgb(h1), _rgb(h2)
    return _hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


OUTLINE = 0.82    # Kontur = Füllung x 0,82 (Stilregel: etwa 0,8)
SHADE = 0.72      # Schatten / Kapuzeninneres = Füllung x 0,72


def family(fill, outline=None, shade=None):
    """Kontur (a), Füllung (b), Schatten (c) aus einer Füllfarbe."""
    return {"a": outline or tone(fill, OUTLINE), "b": fill, "c": shade or tone(fill, SHADE)}


def paint(rows, pal):
    cv = Canvas(max(len(r) for r in rows), len(rows))
    cv.art(rows, pal)
    return cv.px


# ---------- Raster ----------
# Buchstaben: a Kontur, b Füllung, c Schatten, d weiß/Streifen, übrige siehe je Teil.

# T-Shirt 28x24 (Raster wie bisher, zwei glatte Rumpfzeilen gekürzt; Logo 'd' nur für die blaue Variante)
TSHIRT = [
    "........aaaaaaaaaaaa........",
    "......aabaccccccccabaa......",
    ".....abbbaccccccccabbba.....",
    "....abbbbaccccccccabbbba....",
    "...abbbbbbaccccccabbbbbba...",
    "..abbbbbbbbaaaaaabbbbbbbba..",
    ".abbbbbbbbbbbbbbbbbbbbbbbba.",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbbbbbbbbbbbbbbddbbbbbbba",
    "abbbbabbbbbbbbbbbddbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "aaaaaabbbbbbbbbbbbbbbbaaaaaa",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....aaaaaaaaaaaaaaaaaa.....",
]

# Longsleeve 28x24: gestreift (d = Streifen). Gekürzt: der erste Streifen unter den Schultern entfällt,
# die Streifen beginnen mit dem Farbband (Schulterpasse) und enden mit weißem Saum.
LONGSLEEVE = [
    "........aaaaaaaaaaaa........",
    "......aabaccccccccabaa......",
    ".....abbbaccccccccabbba.....",
    "....abbbbaccccccccabbbba....",
    "...abbbbbbaccccccabbbbbba...",
    "..abbbbbbbbaaaaaabbbbbbbba..",
    ".abbbbbbbbbbbbbbbbbbbbbbbba.",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "addddaddddddddddddddddadddda",
    "addddaddddddddddddddddadddda",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "addddaddddddddddddddddadddda",
    "addddaddddddddddddddddadddda",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "addddaddddddddddddddddadddda",
    "aaaaaaddddddddddddddddaaaaaa",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....adddddddddddddddda.....",
    ".....adddddddddddddddda.....",
    ".....aaaaaaaaaaaaaaaaaa.....",
]

# Gestreiftes T-Shirt 28x24 (kurze Ärmel, d = Streifen): T-Shirt-Silhouette mit den Streifenzeilen des Longsleeves
# (Schulterpasse in der Hauptfarbe, dann 4 weiße Streifen zu je 2 Zeilen, weißer Saum).
STRIPED_TSHIRT = []
for _y, _row in enumerate(TSHIRT):
    _stripe = _y in (9, 10, 13, 14, 17, 18, 21, 22)
    STRIPED_TSHIRT.append("".join("d" if (_stripe and c in "bd") else ("b" if c == "d" else c) for c in _row))

# Pullover 28x24 (Bündchen = c). Farbblock: Zeile < PULLOVER_SPLIT oben, sonst unten.
PULLOVER = [
    "........aaaaaaaaaaaa........",
    "......aabaccccccccabaa......",
    ".....abbbaccccccccabbba.....",
    "....abbbbaccccccccabbbba....",
    "...abbbbbbaccccccabbbbbba...",
    "..abbbbbbbbaaaaaabbbbbbbba..",
    ".abbbbbbbbbbbbbbbbbbbbbbbba.",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbbbbbbbbbbbbbbbbbbbbbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "abbbbabbbbbbbbbbbbbbbbabbbba",
    "aaaaaabbbbbbbbbbbbbbbbaaaaaa",
    "accccabbbbbbbbbbbbbbbbacccca",
    "accccabbbbbbbbbbbbbbbbacccca",
    "aaaaaabbbbbbbbbbbbbbbbaaaaaa",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....abbbbbbbbbbbbbbbba.....",
    ".....acccccccccccccccca.....",
    ".....acccccccccccccccca.....",
    ".....aaaaaaaaaaaaaaaaaa.....",
]
PULLOVER_SPLIT = 12

# Kapuzenpullover 24x24, Kapuze umgeklappt (Ring): Kordeln (k, Ende c), Känguru-Tasche (c), Bündchen und Saum (c),
# l = Futterband oben im Loch. Ring = geschlossene Ellipse mit eigener Kontur (Kopf-Ring r0-r6).
KAPUZENPULLOVER = [
    "........aaaaaaaa........",
    ".......abbbbbbbba.......",
    "......abbllllllbba......",
    "....aaabbccccccbbaaa....",
    "...abbabbccccccbbabba...",
    "..abbbbabbbbbbbbabbbba..",
    ".abbbbbbakaaaakabbbbbba.",
    "abbbbbbbbkbbbbkbbbbbbbba",
    "abbbbbbbbkbbbbkbbbbbbbba",
    "abbbabbbbcbbbbcbbbbabbba",
    "abbbabbbbbbbbbbbbbbabbba",
    "abbbabbbbbbbbbbbbbbabbba",
    "abbbabbccccccccbbbbabbba",
    "abbbabbcbbbbbbbbcbbabbba",
    "abbbabbcbbbbbbbbcbbabbba",
    "aaaaabbcbbbbbbbbcbbaaaaa",
    "acccabbcbbbbbbbbcbbaccca",
    "acccabbcbbbbbbbbcbbaccca",
    "aaaaabbcbbbbbbbbcbbaaaaa",
    "....abbcbbbbbbbbcbba....",
    "....abbcbbbbbbbbcbba....",
    "....acccccccccccccca....",
    "....acccccccccccccca....",
    "....aaaaaaaaaaaaaaaa....",
]

# Winterjacke 24x24, Kapuze umgeklappt (Ring); l = Futterband im Loch; r = Reflex-Streifen nur in der blauen Variante
WINTERJACKE = [
    "........aaaaaaaa........",
    ".......abbbbbbbba.......",
    "......abbllllllbba......",
    "....aaabbccccccbbaaa....",
    "...abbabbccccccbbabba...",
    "..abbbbabbbabbbbabbbba..",
    ".abbbbbbaaaabaaabbbbbba.",
    "abbbbbbbbbbabbbbbbbbbbba",
    "aaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbabbbbbbabbbbbbbabbba",
    "abbbabbbbbbabbbbbbbabbba",
    "aaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbabbbbbbabbbbbbbabbba",
    "abbbabbbbbbabbbbbbbabbba",
    "aaaaaaaaaaaaaaaaaaaaaaaa",
    "abbbabbbbbbabbbbbbbabbba",
    "abbbabbbbbbabbbbbbbabbba",
    "abbbabbbbbbabbbbbbbabbba",
    "aaaaabbbbbbabbbbbbbaaaaa",
    "....abbbbbbabbbbbbba....",
    "....aaaaaaaaaaaaaaaa....",
    "....abbbbbbabbbbbbba....",
    "....abbbbbbabbbbbbba....",
    "....aaaaaaaaaaaaaaaa....",
]

# Schneejacke 24x24 (vom Schneeanzug abgeleitet, ohne Beine): dick wattiert, Kapuze umgeklappt als heller Fellring (l),
# Loch dunkel (c), Nähte (a) alle drei Zeilen mit eingekerbter Kante, Bündchen und Saum (c), z = Reißverschluss-Band.
SCHNEEJACKE = [
    "........aaaaaaaa........",
    ".......alllllllla.......",
    "......allcccccclla......",
    "....aaallccccccllaaa....",
    "...abballccccccllabba...",
    "..abbbballlazlllabbbba..",
    ".abbbbbbaaaazaaabbbbbba.",
    "abbbbbbbbbbazbbbbbbbbbba",
    "abbbabbbbbbazbbbbbbabbba",
    ".aaaaaaaaaaaaaaaaaaaaaa.",
    "abbbabbbbbbazbbbbbbabbba",
    "abbbabbbbbbazbbbbbbabbba",
    ".aaaaaaaaaaaaaaaaaaaaaa.",
    "abbbabbbbbbazbbbbbbabbba",
    "abbbabbbbbbazbbbbbbabbba",
    ".aaaaaaaaaaaaaaaaaaaaaa.",
    "acccabbbbbbazbbbbbbaccca",
    "acccabbbbbbazbbbbbbaccca",
    "aaaaaaaaaaaaaaaaaaaaaaaa",
    "....abbbbbbazbbbbbba....",
    "....abbbbbbazbbbbbba....",
    "....acccccccccccccca....",
    "....acccccccccccccca....",
    "....aaaaaaaaaaaaaaaa....",
]

# Regenjacke gelb 24x24, Kapuze umgeklappt (a Kontur, b Füllung, c Schatten, d Reißverschluss, e Glanz, l Futterband = d)
REGENJACKE_GELB = [
    "........aaaaaaaa........",
    ".......abbbbbbbba.......",
    "......abbllllllbba......",
    "....aaabbccccccbbaaa....",
    "...abbabbccccccbbabba...",
    "..abbbbabbbadbbbabbbba..",
    ".abbbbbbaaaadaaabbbbbba.",
    "abbbbbbbbcbadbcbbbbbbbba",
    "abbbbebbbbbadbbbbbbbbbba",
    "abebaebbbbbadbbbbbbabbba",
    "abebabbbbbbadbbbbbbabbba",
    "abebabbbbbbadbbbbbbabbba",
    "abbbabbbbbbadbbbbbbabbba",
    "abbbabbbbbbadbbbbbbabbba",
    "abbbabbbbbbadbbbbbbabbba",
    "aaaaabbbbbbadbbbbbbaaaaa",
    "abbbabbbbbbadbbbbbbabbba",
    "abbbaaaabbbadbbaaababbba",
    "aaaaabbbbbbadbbbbbbaaaaa",
    "....abbbbbbadbbbbbba....",
    "....abbbbbbadbbbbbba....",
    "....abbbbbbadbbbbbba....",
    "....abbbbbbadbbbbbba....",
    "....aaaaaaaaaaaaaaaa....",
]

# Regenjacke 24x24 (pink), Kapuze umgeklappt: l = helles Futter (Futterband im Loch, Bündchen, Saum),
# z = Reißverschluss hell, g = Glanz
REGENJACKE = [
    "........aaaaaaaa........",
    ".......abbbbbbbba.......",
    "......abbllllllbba......",
    "....aaabbccccccbbaaa....",
    "...abbabbccccccbbabba...",
    "..abbbbabbbazbbbabbbba..",
    ".abbbbbbaaaazaaabbbbbba.",
    "abbbbbbbbcbazbcbbbbbbbba",
    "abbbbgbbbbbazbbbbbbbbbba",
    "abgbagbbbbbazbbbbbbabbba",
    "abgbabbbbbbazbbbbbbabbba",
    "abgbabbbbbbazbbbbbbabbba",
    "abbbabbbbbbazbbbbbbabbba",
    "abbbabbbbbbazbbbbbbabbba",
    "abbbabbbbbbazbbbbbbabbba",
    "aaaaabbbbbbazbbbbbbaaaaa",
    "alllabbbbbbazbbbbbballla",
    "alllaaaabbbazbbaaaballla",
    "aaaaabbbbbbazbbbbbbaaaaa",
    "....abbbbbbazbbbbbba....",
    "....abbbbbbazbbbbbba....",
    "....allllllazlllllla....",
    "....allllllazlllllla....",
    "....aaaaaaaaaaaaaaaa....",
]


# Teddyjacke 28x24 (nach Janas Foto): Teddyfleece mit großen Blumen, pinker Reißverschluss mit gelbem Zipper,
# Kapuze umgeklappt als pinker Kragenring mit mauvefarbenem Futter, pinke Bündchen und Saum. Die Kante ist absichtlich unruhig (Fleece).
# o Außenkante, f Fleece, s Ärmelnaht, p Blüte rosa, y Blütenmitte, m Senfgelb (Tulpe/Blatt),
# z/Z Reißverschluss, Y Zipper, r pinker Rand/Bündchen/Saum, l/L Kragenfutter. Variante 2 färbt p, y, m wie Fleece.
TEDDYJACKE = [
    "..........oooooooo..........",
    ".........orrrrrrrro.........",
    "........orrllllllrro........",
    "......ooorrLLLLLLrrooo......",
    "....oofforrLLLLLLrroffoo....",
    "..ooffffforrrzZrrrofffffoo..",
    ".offffmmffoooYYooopppfffffo.",
    "ofppffmmmfmmmYYfppppppfmffmo",
    "opyypsmmmmmmmzZfppyyppsmmmmo",
    "opyypsfmmmmmfzZfppyyppsfmmfo",
    ".oppfsfppppffzZfppppppsfppfo",
    ".offmsppppppfzZffppppfspyypo",
    ".ommmsppyyppfzZmmfffmmspyypo",
    "ofmmfsppyyppfzZmmmfmmmsfppo.",
    "offffsppppppfzZmmmmmmmsfffo.",
    "orrrrsfppppffzZfmmmmmfsrrro.",
    "orrrrsmmfffmmzZfffffffsrrrro",
    "ooooofmmmfmmmzZfppppfffooooo",
    ".....ommmmmmmzZppppppfo.....",
    ".....ofmmmmmfzZppyyppo......",
    "......offffffzZppyyppo......",
    "......orrrrrrzZrrrrrrro.....",
    ".....orrrrrrrzZrrrrrrro.....",
    ".....oooooooooooooooooo.....",
]

# Strickjacke 28x24 (Mauve, V-Ausschnitt, Knopfleiste links der Mitte, Taschenbündchen): übernommen aus dem alten Sprite,
# um zwei Rumpfzeilen gekürzt; Knöpfe (c) im Abstand von 3 Zeilen.
STRICKJACKE = [
    "........aaaaaaaaaaaa........",
    "......aabaccccccccabaa......",
    ".....abbbaccccccccabbba.....",
    "....abbbbaccccccccabbbba....",
    "...abbbbbbaccccccabbbbbba...",
    "..abbbbbbbbccccccbbbbbbbba..",
    ".abbbbbbbbbbccccbbbbbbbbbba.",
    "abbbbbbbbbbbbccbbbbbbbbbbbba",
    "abbbbbbbbbbbbabbbbbbbbbbbbba",
    "abbbbbbbbbbbbabbbbbbbbbbbbba",
    "abbbbabbbbbbbabbbbbbbbabbbba",
    "abbbbabbbbbbbabcbbbbbbabbbba",
    "abbbbabbbbbbbabbbbbbbbabbbba",
    "abbbbabbbbbbbabbbbbbbbabbbba",
    "abbbbabbbbbbbabcbbbbbbabbbba",
    "abbbbabbbbbbbabbbbbbbbabbbba",
    "aaaaaabbbbbbbabbbbbbbbaaaaaa",
    "accccabbbbbbbabcbbbbbbacccca",
    "accccabbbbbbbabbbbbbbbacccca",
    "aaaaaabbbbbbbabbbbbbbbaaaaaa",
    ".....abbbbbbbabbbbbbbba.....",
    ".....acccccccacccccccca.....",
    ".....acccccccacccccccca.....",
    ".....aaaaaaaaaaaaaaaaaa.....",
]

# ---------- Paletten ----------

TSHIRT_ORIG = {"a": "#6299be", "b": "#73b3da", "c": "#56829c", "d": "#f2f2e9"}
WINTER_ORIG = {"a": "#a63e36", "b": "#c1483f", "c": "#8d352e"}
REGEN_YELLOW = {"a": "#c99a1c", "b": "#f7cf3d", "c": "#dcae26", "d": "#fff0a8", "e": "#fde886"}
STRIPE_WHITE = "#f2f2e9"

# Weiß mit kühlen blaugrauen Schatten (T-Shirt) und warmes Creme (Pullover unten, Teddy)
WHITE = {"a": "#8b99ae", "b": "#f8f9fb", "c": "#c5d0df", "s": "#e1e8f1"}
CREAM = {"a": "#b3a58e", "b": "#faf5e9", "c": "#dccfb8", "s": "#ebe2d0"}

PINK_TSHIRT = "#f3a2b4"
GREEN_DARK = "#4a7c59"
MINT = "#9ad7b6"
PINK_REGEN = "#ec8aa0"


def hood_lining(fill, t=0.30):
    """Futterband oben im Loch der umgeklappten Kapuze: heller als die Füllung (dunkle Farben stärker)."""
    return mix(fill, "#ffffff", t)


def regen_palette(fill):
    p = family(fill)
    p.update(
        l=mix(fill, "#ffffff", 0.62),     # Futter an Kapuzenrand, Bündchen, Saum
        z=mix(fill, "#ffffff", 0.85),     # Reißverschluss
        g=mix(fill, "#ffffff", 0.35),     # Glanz
    )
    return p


def snow_palette(fill, **kw):
    p = family(fill, **kw)
    p["l"] = mix(fill, "#ffffff", 0.55)   # heller Kapuzenrand
    p["z"] = tone(fill, 0.95)             # Reißverschluss-Band
    return p


def shadow(px, fill, shade, outline, right=True):
    """Weiche Schatten für helle Teile: Reihe über dem unteren Rand und (optional) Spalte vor einem rechten Rand."""
    out = dict(px)
    for (x, y), c in px.items():
        if c != fill:
            continue
        if px.get((x, y + 1)) == outline or (right and px.get((x + 1, y)) == outline):
            out[(x, y)] = shade
    return out


# ---------- Teile ----------

def tshirt(variant):
    rows = [r.replace("d", "b") for r in TSHIRT]
    if variant == 3:                                   # hellblau, wie bisher (Logo)
        return paint(TSHIRT, TSHIRT_ORIG)
    if variant == 1:                                   # pink mit kleinem Herz auf der Brust
        px = paint(rows, family(PINK_TSHIRT))
        for dx, dy, ch in HEART:
            if ch == "#":
                px[(16 + dx, 9 + dy)] = "#fff3f1"
        return px
    pal = WHITE                                        # weiß mit blaugrauer Kontur und Schatten
    px = paint(rows, pal)
    return shadow(px, pal["b"], pal["s"], pal["a"])


HEART = [(dx, dy, c) for dy, r in enumerate((".#.#.", "#####", ".###.", "..#..")) for dx, c in enumerate(r)]


def longsleeve(fill):
    pal = family(fill)
    pal["d"] = STRIPE_WHITE
    return paint(LONGSLEEVE, pal)


def striped_tshirt(fill):
    pal = family(fill)
    pal["d"] = STRIPE_WHITE
    return paint(STRIPED_TSHIRT, pal)


def pullover(top, bottom):
    """Zweifarbig: oben `top`, ab Zeile PULLOVER_SPLIT `bottom` (jeweils eigene Kontur und Schatten)."""
    ptop = family(top) if isinstance(top, str) else top
    pbot = family(bottom) if isinstance(bottom, str) else bottom
    px = {}
    for y, row in enumerate(PULLOVER):
        pal = ptop if y < PULLOVER_SPLIT else pbot
        for x, ch in enumerate(row):
            if ch != ".":
                px[(x, y)] = pal[ch]
    return px


def kapuzenpullover(fill):
    pal = family(fill)
    pal["k"] = mix(fill, "#ffffff", 0.72)    # Kordeln
    pal["l"] = hood_lining(fill)             # Futterband im Loch
    return paint(KAPUZENPULLOVER, pal)


def winterjacke(variant):
    if variant == 1:
        pal = dict(WINTER_ORIG, l=hood_lining(WINTER_ORIG["b"]))
        return paint(WINTERJACKE, pal)
    fill = "#2f808c"                              # petrol (nicht marine: die Schneejacke ist dunkelblau und soll sich nicht verwechseln lassen)
    pal = family(fill)
    pal["l"] = hood_lining(fill, 0.34)
    pal["r"] = "#e3e9f0"                          # Reflexstreifen
    rows = [list(r) for r in WINTERJACKE]
    for y in (12, 13):                            # zwei Zeilen quer über Ärmel und Rumpf (zwischen den Nähten in Zeile 11 und 14)
        for x, ch in enumerate(rows[y]):
            if ch == "b":
                rows[y][x] = "r"
    return paint(["".join(r) for r in rows], pal)


def teddyjacke(variant):
    if variant == 1:
        pal = dict(o="#b09aab", f="#f1e8ee", s="#dccdd8", p="#f08fc0", y="#faf0a3", m="#cf9b30",
                   z="#e0509c", Z="#f59ccb", Y="#f1e58a", r="#ee74b5", l="#c796bb", L="#b07fa8")
    else:                                              # einfarbig cremeweiß, ohne Blumen
        f = "#f8f2e6"
        pal = dict(o="#b3a089", f=f, s="#e4d8c6", p=f, y=f, m=f,
                   z="#e0509c", Z="#f59ccb", Y="#f1e58a", r="#ee74b5", l="#c796bb", L="#b07fa8")
    return paint(TEDDYJACKE, pal)


STRICK_MAUVE = {"a": "#996a83", "b": "#b27b98", "c": "#825a6f"}


def strickjacke():
    return paint(STRICKJACKE, STRICK_MAUVE)


def schneejacke(fill, **kw):
    return paint(SCHNEEJACKE, snow_palette(fill, **kw))


def regenjacke(variant):
    if variant == 2:
        return paint(REGENJACKE_GELB, dict(REGEN_YELLOW, l=REGEN_YELLOW["d"]))  # bisherige gelbe Regenjacke (Palette unverändert)
    return paint(REGENJACKE, regen_palette(PINK_REGEN if variant == 1 else "#f0954a"))


# ---------- Schnittstelle ----------

def build():
    cat = {}
    cat["i-top-tshirt"] = tshirt(1)
    cat["i-top-tshirt-v2"] = tshirt(2)
    cat["i-top-tshirt-v3"] = tshirt(3)
    cat["i-top-longsleeve"] = longsleeve(GREEN_DARK)
    cat["i-top-longsleeve-v2"] = striped_tshirt("#ee93aa")   # Jana: v2 als kurzes Shirt (rosa gestreift)
    cat["i-top-longsleeve-v3"] = longsleeve("#2f4a7c")
    cat["i-top-pullover"] = pullover(GREEN_DARK, MINT)
    cat["i-top-pullover-v2"] = pullover("#ee93aa", CREAM)
    cat["i-top-kapuzenpullover"] = kapuzenpullover(MINT)
    cat["i-top-kapuzenpullover-v2"] = kapuzenpullover("#c8a4dc")
    cat["i-top-teddyjacke"] = teddyjacke(1)
    cat["i-top-teddyjacke-v2"] = teddyjacke(2)
    cat["i-top-regenjacke"] = regenjacke(1)
    cat["i-top-regenjacke-v2"] = regenjacke(2)
    cat["i-top-regenjacke-v3"] = regenjacke(3)
    # Janas Schneejacke ist noch offen (tbd): dunkelblau wird gezeigt, die übrigen Farben sind Reserve (Gewicht 0 in der App)
    cat["i-top-schneejacke"] = schneejacke("#2a4278", outline=tone("#2a4278", 0.74), shade=tone("#2a4278", 0.58))   # dunkle Farbe: Kontur/Schatten etwas dunkler, damit Steppung und Loch lesbar bleiben
    cat["i-top-schneejacke-v2"] = schneejacke("#6b6fa8", outline="#5c5f90", shade="#4e517a")
    cat["i-top-schneejacke-v3"] = schneejacke("#b4559f")
    cat["i-top-schneejacke-v4"] = schneejacke("#3fb2b4")
    cat["i-top-winterjacke"] = winterjacke(1)
    cat["i-top-winterjacke-v2"] = winterjacke(2)
    cat["i-top-strickjacke"] = strickjacke()      # noch in keiner Regel benutzt, soll aber ins 24er-Fenster passen
    return cat


# ---------- Vorschau (nur beim direkten Aufruf; nutzt Kopf-, Hosen- und Schuh-Module, Layout L3 aus pxl.app_frames) ----------

def _previews(outdir=None):
    from pathlib import Path
    from pxl import sheet, app_frames
    import icons_kopf_zubehoer as kz
    import icons_schuhe_hosen as sh
    out = Path(outdir or Path(__file__).resolve().parent.parent / ".wip" / "art" / "oberteile")
    out.mkdir(parents=True, exist_ok=True)
    cat = build()
    sheet(cat, out / "oberteile-sheet.png", scale=8, cols=6)

    K, S = kz.build(), sh.build()
    cap, hat = K["i-head-sonnenhut"], K["i-head-muetze"]
    jeans, shorts, snowpants = S["i-bottom-hose-lang"], S["i-bottom-hose-kurz"], S["i-bottom-schneehose"]
    sneaker, sandal, gummi, boots = S["i-shoes-sneaker"], S["i-shoes-sandalen"], S["i-shoes-gummistiefel"], S["i-shoes-winterstiefel"]

    def f(top, band, head=None, bottom=jeans, shoes=sneaker):
        return dict(head=head, top=top, bottom=bottom, shoes=shoes, acc=[], band=band)

    t = cat
    app_frames([f(t["i-top-tshirt-v2"], 0, cap, shorts, sandal), f(t["i-top-tshirt"], 1, cap, shorts, sneaker),
                f(t["i-top-tshirt"], 1, None, shorts, sneaker), f(t["i-top-tshirt-v3"], 2, None, shorts, sneaker),
                f(t["i-top-strickjacke"], 3, None, jeans, sneaker)],
               out / "app-tshirts.png", zoom=2)
    app_frames([f(t["i-top-longsleeve"], 4), f(t["i-top-longsleeve-v2"], 1, cap, shorts, sneaker), f(t["i-top-longsleeve-v3"], 4),
                f(t["i-top-pullover"], 4), f(t["i-top-pullover-v2"], 4)],
               out / "app-streifen-pullover.png", zoom=2)
    app_frames([f(t["i-top-winterjacke"], 5, hat, jeans, boots), f(t["i-top-winterjacke-v2"], 5, hat, jeans, boots),
                f(t["i-top-schneejacke"], 6, hat, snowpants, boots), f(t["i-top-schneejacke-v2"], 6, hat, snowpants, boots),
                f(t["i-top-schneejacke-v3"], 6, hat, snowpants, boots)],
               out / "app-winter-schnee.png", zoom=2)
    app_frames([f(t["i-top-schneejacke-v4"], 6, hat, snowpants, boots), f(t["i-top-winterjacke-v2"], 6, hat, jeans, boots),
                f(t["i-top-schneejacke"], 6, hat, snowpants, boots)],
               out / "app-schnee-v4-marine-vergleich.png", zoom=2)
    app_frames([f(t["i-top-regenjacke"], 3, None, jeans, gummi), f(t["i-top-regenjacke-v2"], 2, cap, jeans, gummi),
                f(t["i-top-regenjacke-v3"], 4, None, jeans, gummi), f(t["i-top-teddyjacke"], 3, cap, jeans, sneaker),
                f(t["i-top-teddyjacke-v2"], 3, None, jeans, sneaker)],
               out / "app-regen-teddy.png", zoom=2)
    app_frames([f(t["i-top-kapuzenpullover"], 5, None, jeans, None), f(t["i-top-kapuzenpullover-v2"], 5, None, jeans, None),
                f(t["i-top-regenjacke"], 3, cap, jeans, gummi), f(t["i-top-teddyjacke"], 3, None, jeans, gummi)],
               out / "app-kapuzen.png", zoom=2)
    return out


if __name__ == "__main__":
    print("Vorschau:", _previews(sys.argv[1] if len(sys.argv) > 1 else None))
    print(len(build()), "Symbole")
