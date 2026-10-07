# Status

Stand 2026-10-07. Live unter https://jahabanana.github.io/clothing-display/ (v1.2.1, `CACHE_VERSION` v5, nach dem Aufwecken auf dem Gerät kontrollieren, dass die neue Version läuft, AC-18)

## Erledigt

- T1, T3–T11: Code, Layout, Icons, Zustände, Aktualisierung, Debug- und Testmodus.
- GitHub Pages aktiv, Repo öffentlich geprüft (keine Secrets, keine echten Koordinaten), Secret Scanning und Push Protection an.
- **T2 (Geräte-Einrichtung) und T12 (Test auf dem iPhone) abgeschlossen:** Installation, Standort, Layout, Geführter Zugriff und Einstellungen sind ok. Die Empfehlung passte grob und wird verfeinert.

## v1.2.1: Regeln, Farben, drinnen/draußen, Kapuzen (Spec v1.2, auf `main`)

Umgesetzt nach Janas Entscheidungen vom 2026-10-06 und 2026-10-07. Begründungen, Zahlen und Zwischenstände der Zeichner: `.wip/` (nicht im Repo).

- **Regeln** (A-22…A-24, A-28): Sonnenschutz in kalt, eisig, frost erst ab UV 5 (sonst ab 3). Schnee wirkt nur in kühl bis frost, in eisig und frost als Schneejacke plus grüne Schneehose, in kühl und kalt nur als Winterstiefel. Regen in der Kälte (kühl, kalt, eisig): Matschhose. Wind nutzt die pinke gefütterte Jacke. In kühl gibt es ein rosa Halstuch, in eisig und frost einen lila Schal.
- **Umschalter drinnen/draußen** (A-26): Haus und Baum links neben der Hose. Drinnen zeigt die Grundkleidung des Bandes (von kühl bis frost zufällig Pullover oder Kapuzenpullover), springt nach 60 s und beim Aufwecken zurück. Debug: `?view=in`.
- **Farbvarianten** (A-25, A-29, A-30): je Teil und Tag wählt die App eine Farbe, Nachbarn teilen nie eine Farbfamilie (`VARIANT_TAGS`). Schneejacke nur dunkelblau (Reserve-Farben mit Gewicht 0), Sneaker und Crocs ohne Varianten. Debug: `?v=2`, `?seed=x`.
- **Kapuzen umgeklappt, Oberteile 24 Zeilen** (A-32): Die Kapuze liegt als Ring auf den Schultern. Oberteil-Fenster 132 pt unten bündig, Kopf direkt darüber (11 pt Abstand zum Kragen).
- **Pixelgrafiken** (A-27): 59 Symbole aus `tools/icons_*.py` in Janas Farben (Schuhe als Paar, Teddyjacke nach Foto, pinke Regenjacke, Schneehose, Matschhose, Leggings, …).
- **Größe** (A-31): `?test` und `?overview` liegen in `tests.js` und `overview.js` und werden nur dafür nachgeladen. `index.html` + `sw.js` + `manifest.json` liegen deutlich unter 150 KB.
- `CACHE_VERSION` ist `v5`. Test: `?test` (Headless-Chrome: alle PASS).

**Auf dem iPhone noch zu prüfen:** Schärfe der Pixel-Art (AC-13), Marker überdeckt nichts (AC-20), Umschalter treffbar und gut sichtbar (AC-21), Lesbarkeit der Kapuzen-Ringe, Schuhpaare und Zubehör aus 1–2 m, Matschhose gegen Schneehose unterscheidbar, Winterjacke (rot auf rot) liest sich als Jacke.

## Nicht geprüft

- **Veraltet-Zustand (`i-sys-uhr`) auf dem Gerät** (Flugmodus, 3+ h warten, aufwecken).
- Standort Weg B (Button „Standort ermitteln“) nur teilweise.
- Echte Wetterdaten: ob Open-Meteo `uv_index` die Bewölkung schon enthält, ist nicht bestätigt.

## Als Nächstes

- v1.2 ansehen (iPhone), dann committen und veröffentlichen: Branch prüfen, pushen, nach dem zweiten Aufwecken kontrollieren, dass die neue Version läuft (AC-18).
- Offene Fragen aus dem Pixel-Art-Review stehen in `.wip/00-LIES-MICH.md`.
- Schwellen in `RULES` nach etwa einer Woche Alltagstest nachjustieren (P-17).
- Bei jeder Änderung an `index.html`: `CACHE_VERSION` in `sw.js` erhöhen.
