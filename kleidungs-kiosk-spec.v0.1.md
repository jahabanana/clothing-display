# Kleidungs-Kiosk — Spec v0.1

> Status: **Entwurf.** Alle Stellen mit `OFFEN-xx` warten auf die Kleidungslogik-Datei, die SVGs und den Styleguide. Die Sammelliste steht in [§14](#14-offene-punkte).

---

## 1. Ziel

Ein altes iPhone 8 hängt als Single-Purpose-Kiosk im Flur. Beim Aufwecken zeigt es dem Kind **auf einen Blick**, was es heute anziehen soll: Kopf, Oberteil, Hose, Schuhe und Zubehör, abgeleitet aus dem Wetter der nächsten Stunden. Das Kind soll sich damit **selbstständig und wettergerecht** anziehen können, ohne lesen zu müssen.

## 2. Scope

**In Scope (v1)**
- Genau ein Screen mit einer Outfit-Empfehlung für die nächsten ~4 Stunden
- Wetterzeile: Zustand, Temperatur, bis zu 2 Hinweis-Icons
- Wärmeskala mit Positionspunkt
- Offline-Fähigkeit (letzter Stand bleibt sichtbar)
- Debug-Modus per URL

**Out of Scope (v1)**
- Mehrere Screens oder Tabs (Nachmittag, Morgen). Das Layout soll die Erweiterung aber nicht verbauen.
- Schichten-Darstellung. Beim Oberteil wird nur das äußerste Teil gezeigt.
- Mehrere Kinder oder Profile
- Interaktion außer Aufwecken (keine Taps, nichts zum Verschieben)
- Server, Accounts, Build-Pipeline

## 3. Zielgerät & Plattform

| | |
|---|---|
| Gerät | iPhone 8, 375 × 667 pt, 2× Dichte (750 × 1334 px), kein Notch |
| OS | iOS 16.x, jailbroken (palera1n). `OFFEN-01`: Version bestätigen |
| Laufzeit | Safari-Web-App vom Homescreen, `display: standalone` |
| Orientierung | Hochformat, gesperrt |
| Bildschirm | normale Auto-Sperre, kein Wach-halten-Tweak |
| Hosting | GitHub Pages (statisch, öffentliches Repo) |

## 4. Architektur

### 4.1 Dateien

```
/index.html      – Markup, CSS, JS, SVG-Sprite (<symbol>), Logik-Konfig
/sw.js           – Service Worker (muss eigene Datei sein)
/manifest.json   – Web-App-Manifest (Name, Icon, standalone, Farben)
/icon-180.png    – Apple Touch Icon. OFFEN-02: Motiv
```

- **Kein Build-Schritt.** Vanilla HTML/CSS/JS (ES2020), keine Abhängigkeiten.
- Alle Icons liegen als `<symbol>` in einem Sprite in `index.html` und werden über `<use href="#…">` eingebunden.
- Die **Logik-Konfiguration** steht als klar abgegrenzter, kommentierter Block **ganz oben** im Script (siehe §7.1), damit sich Schwellenwerte ohne Code-Suche ändern lassen.

### 4.2 Service Worker

- **App-Shell** (`index.html`, `manifest.json`, Icon): cache-first, versioniert über eine `CACHE_VERSION`-Konstante.
- **Open-Meteo-Requests** gehen nicht über den SW-Cache. Die letzte erfolgreiche Antwort wird mit Zeitstempel in `localStorage` (`kiosk.lastForecast`) abgelegt.
- Ein Update der App wird beim nächsten Aufwecken aktiv (`skipWaiting` + `clients.claim`).

### 4.3 Konfiguration (Standort)

- Der Standort gehört **nicht** ins Repo.
- Einrichtung einmalig über `index.html?lat=<lat>&lon=<lon>`. Die App speichert die Werte in `localStorage` (`kiosk.location`) und entfernt die Parameter per `history.replaceState` aus der URL.
- Danach wird die App vom Homescreen gestartet und liest den Standort aus `localStorage`.
- Ohne gespeicherten Standort erscheint der Setup-Zustand (§9).
- ⚠️ Der Homescreen-Kontext hat unter iOS einen eigenen Speicher. Die Parameter-URL muss daher **im Homescreen-App-Kontext** geöffnet werden, oder die Homescreen-Verknüpfung wird direkt mit Parametern angelegt. Das muss in T2 verifiziert werden.

## 5. Datenquelle

**Open-Meteo Forecast API** (kein Key, CORS ok).

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}&longitude={lon}
  &current=temperature_2m,apparent_temperature,weather_code
  &hourly=temperature_2m,apparent_temperature,precipitation_probability,
          precipitation,snowfall,weather_code,uv_index,wind_gusts_10m
  &timezone=auto
  &forecast_days=2
```

`forecast_days=2` stellt sicher, dass das 4-Stunden-Fenster auch am späten Abend vollständig ist.

## 6. Aggregation: Wetterfenster

**Fenster:** die aktuelle Stunde plus die 3 folgenden Stunden, also **4 Stundenwerte**. Das Fenster ist rollierend und hängt nicht von der Tageszeit ab.

Aus dem Fenster wird ein `Conditions`-Objekt berechnet:

| Feld | Berechnung | Wofür |
|---|---|---|
| `tempDisplay` | `current.temperature_2m`. `OFFEN-03`: aktueller Wert oder Minimum im Fenster? | Zahl in der Wetterzeile |
| `feltMin` | min(`apparent_temperature`) | Band, Kleidung, Skala |
| `rainProbMax` | max(`precipitation_probability`) | Regen-Override |
| `rainSum` | Summe(`precipitation`) | Regen-Override |
| `snowSum` | Summe(`snowfall`) | Schnee-Override |
| `uvMax` | max(`uv_index`) | Sonnenschutz |
| `gustMax` | max(`wind_gusts_10m`) | Wind-Hinweis |
| `tempMin` | min(`temperature_2m`) | Glätte-Hinweis |
| `code` | „schwerster“ `weather_code` im Fenster (Rangfolge §8.1) | Wetter-Icon, Gewitter |

**Leitregel:** Die Kleidung richtet sich nach der **kältesten gefühlten** Stunde. Regen und UV richten sich nach dem **Maximum** im Fenster.

## 7. Entscheidungslogik

### 7.1 Konfig-Block (Struktur, Werte offen)

```js
// ===== KLEIDUNGSLOGIK — hier anpassen =====
const RULES = {
  // Wärmebänder, von warm nach kalt. Grenze = untere Schwelle feltMin (°C), inklusiv.
  // OFFEN-10: Anzahl Bänder, Schwellen und Outfits aus der Logik-Datei übernehmen
  bands: [
    { id: 'heiss',  min:  25, head: null, top: 'tshirt', bottom: 'shorts', shoes: 'sandalen' },
    { id: '…',      min:  ??, head: …,    top: …,        bottom: …,        shoes: … },
    { id: 'frost',  min: -99, head: 'muetze', top: '…',  bottom: '…',      shoes: 'winterstiefel',
      accessories: ['handschuhe', 'schal'] },
  ],
  scale: { max: 30, min: -5 },  // OFFEN-11: Enden der Skala für die Punktposition

  sun: {                         // unabhängig von Temperatur und Bewölkung
    uvThreshold: 3,              // OFFEN-12
    head: 'sonnenhut',           // ersetzt Kopf nur, wenn das Band keine Mütze verlangt. OFFEN-13
    accessories: ['sonnenbrille', 'sonnencreme'],
  },
  rain: {
    probThreshold: 50, sumThreshold: 0.5,   // OFFEN-14: Kombination UND/ODER, Werte
    shoes: 'gummistiefel',
    top: 'regenjacke',            // OFFEN-15: gibt es eine Regenjacke / Matschhose?
    accessories: ['schirm'],      // OFFEN-16: Schirm fürs Kind ja/nein
  },
  snow: {
    sumThreshold: 0.1,            // cm, OFFEN-17
    shoes: 'winterstiefel',
    top: '…',                     // OFFEN-18
  },
  hints: {
    windGust: 40,                 // km/h, OFFEN-19
    iceTempMax: 1,                // °C, Glätte wenn tempMin ≤ Wert UND (Niederschlag ODER vorher nass). OFFEN-20
  },
  maxAccessories: 3,
  accessoryPriority: ['schirm', 'sonnencreme', 'sonnenbrille', 'handschuhe', 'schal'], // OFFEN-21
};
```

### 7.2 Auswertungsreihenfolge

1. **Band bestimmen:** das erste Band in `bands`, für das `feltMin >= band.min` gilt.
2. **Basis-Outfit** aus dem Band übernehmen: Kopf, Oberteil (äußerstes Teil), Hose, Schuhe, Zubehör.
3. **Sonnenschutz** (`uvMax >= sun.uvThreshold`): Zubehör ergänzen. Den Kopf nur setzen, wenn er leer ist (`OFFEN-13`).
4. **Regen-Override:** Schuhe und ggf. Oberteil ersetzen, Zubehör ergänzen.
5. **Schnee-Override:** hat Vorrang vor Regen bei den Schuhen (Winterstiefel schlagen Gummistiefel). `OFFEN-22`: Was gilt bei Schneematsch über 0 °C?
6. **Zubehör deduplizieren**, nach `accessoryPriority` sortieren und auf `maxAccessories` kürzen.
7. **Hinweise** für die Wetterzeile bestimmen (§8.2).

Die Logik ist eine **reine Funktion** `recommend(conditions, RULES) → Outfit` ohne DOM- oder Netzwerkzugriff und damit direkt testbar.

### 7.3 Datenmodell

```ts
type Outfit = {
  band: string;
  head: IconId | null;
  top: IconId;              // nur äußerstes Teil
  bottom: IconId;
  shoes: IconId;
  accessories: IconId[];    // 0–3
  weatherIcon: IconId;
  hints: IconId[];          // 0–2
  scalePos: number;         // 0 (oben, warm) … 1 (unten, kalt)
};
```

## 8. Wetterzeile

### 8.1 Wetter-Icon (WMO-Code → Icon)

| WMO-Codes | Gruppe | Rang (höher = schwerer) | Icon |
|---|---|---|---|
| 0, 1 | klar | 0 | `OFFEN-30` |
| 2 | teilweise bewölkt | 1 | `OFFEN-30` |
| 3 | bedeckt | 2 | `OFFEN-30` |
| 45, 48 | Nebel | 3 | `OFFEN-30` |
| 51–57 | Niesel | 4 | `OFFEN-30` |
| 61–67, 80–82 | Regen | 5 | `OFFEN-30` |
| 71–77, 85, 86 | Schnee | 6 | `OFFEN-30` |
| 95–99 | Gewitter | 7 | `OFFEN-30` |

`OFFEN-31`: Gibt es Nacht-Varianten (Mond)? Wenn nicht, wird tagsüber und nachts dasselbe Icon verwendet.

### 8.2 Hinweis-Icons (max. 2)

Die Priorität ist absteigend:
1. **Gewitter**, wenn `code` in 95–99 liegt
2. **Glätte** nach der Regel in `hints.iceTempMax`
3. **Wind**, wenn `gustMax >= hints.windGust`

Zusätzlich gibt es den Systemzustand **„Daten alt“** (Uhr-Icon, §9). Er belegt keinen der 2 Hinweis-Plätze, sondern steht am rechten Rand der Zeile.

Schirm und Sonnencreme sind **keine** Hinweise, sie gehören ins Zubehör. Jedes Icon hat genau einen Ort.

## 9. Zustände

| Zustand | Bedingung | Anzeige |
|---|---|---|
| Setup | kein Standort in `localStorage` | Hinweis-Screen mit Beispiel-URL (Text ok, der Screen ist für Eltern) |
| Erstes Laden | Standort vorhanden, kein Cache, Request läuft | Layout mit leeren Slots, dezenter Ladeindikator |
| Normal | frische Daten (< 3 h) | vollständige Empfehlung |
| Veraltet | letzte erfolgreiche Daten ≥ 3 h alt | letzte Empfehlung plus Uhr-Icon in der Wetterzeile |
| Fehler | Request fehlgeschlagen, kein Cache | leere Slots plus Fehler-Icon. `OFFEN-32`: Icon |

Nach 3 h wird das Fenster **nicht** neu aus alten Daten berechnet. Es bleibt die letzte Empfehlung stehen, damit keine Stunden außerhalb des Datenbereichs verwendet werden.

## 10. Aktualisierung

- Neu laden bei `visibilitychange` → `visible` und bei `pageshow` (Aufwecken).
- Zusätzlich alle **30 min** per `setInterval`, solange die Seite sichtbar ist.
- Die Wetterdaten werden bei jedem Laden neu abgerufen. Das Fenster wird immer relativ zur aktuellen Stunde berechnet.

## 11. Layout & Visuelles

### 11.1 Raster (iPhone 8, 375 × 667 pt)

```
┌───────────────────────────────────────────┐  Statusleiste 20 pt
│ [Wetter]            [23 °C]   [H1][H2][⏱] │  Wetterzeile ~72 pt
├──────┬─────────────────────────────┬──────┤
│ [Z1] │          [ KOPF ]           │ ┌──┐ │
│ [Z2] │                             │ │  │ │
│ [Z3] │         [ OBERTEIL ]        │ │ ●│ │  Wärmeskala
│      │                             │ │  │ │
│      │           [ HOSE ]          │ │  │ │
│      │                             │ │  │ │
│      │          [ SCHUHE ]         │ └──┘ │
└──────┴─────────────────────────────┴──────┘
 ~56 pt        flexibel (~247 pt)     ~40 pt    Außenrand 16 pt
```

- **Kleidungs-Slots:** 4 gleich hohe Zeilen (~135 pt). Das Raster ist **fix**, leere Slots bleiben leer und nichts rückt nach.
- **Kleidungs-Icons:** 32 × 32 Kunstpixel bei **4 pt/Pixel = 128 pt** (8 Gerätepixel pro Kunstpixel, ganzzahlig).
- **Zubehör-Spalte:** bis zu 3 Icons von oben, beginnend auf Höhe des Kopf-Slots, **48 pt** (1,5 pt = 3 Gerätepixel pro Kunstpixel). `OFFEN-33`: Raster der Zubehör-Icons (auch 32 × 32?).
- **Wetter-Icon und Hinweise:** Größe hängt vom Icon-Raster ab, `OFFEN-34`. Es gilt immer eine ganzzahlige Gerätepixel-Skalierung.
- **Keine sichtbaren Slot-Rahmen.** Nur die Wärmeskala hat eine Kontur.
- Pixel-Art-Rendering: `shape-rendering="crispEdges"` auf den Sprites, keine Antialiasing-Kanten.

### 11.2 Wärmeskala

- Vertikal, **oben warm, unten kalt**.
- Anzahl der Segmente = Anzahl der Bänder. Die Trennlinien liegen an den Bandgrenzen, **proportional zur Temperatur** zwischen `scale.max` und `scale.min`.
- **Punkt stufenlos:** `scalePos = (scale.max − clamp(feltMin)) / (scale.max − scale.min)`.
- Reine Anzeige ohne Interaktion.
- `OFFEN-35`: Segmente nur als Linien (wie in der Skizze) oder farbig abgestuft warm → kalt?

### 11.3 Farbe & Typografie

- Hintergrund: off-white, fest (kein Dark Mode). Vorschlag `#FAF7F0`, `OFFEN-36`: final aus dem Styleguide.
- Linien- und Textfarbe: `OFFEN-36`.
- Temperatur in **echter Schrift**: `font-family: ui-rounded, -apple-system, system-ui, sans-serif`. Die Systemschrift wird nicht nachgeladen. Größe ~40 pt, Gewicht semibold. `OFFEN-37`: Schrift bestätigen.
- Format: `23°C`, bei Minusgraden echtes Minuszeichen (`−3°C`).
- Außer der Temperatur gibt es keinen Text auf dem Hauptscreen.

## 12. Icon-Inventar

Namenskonvention der Symbol-IDs: `i-<slot>-<name>`, z. B. `i-top-tshirt`, `i-acc-sonnenbrille`, `i-wx-regen`.

| Slot | Icon | Status |
|---|---|---|
| Oberteil | T-Shirt | ✅ fertig |
| Oberteil | Longsleeve | ✅ fertig |
| Oberteil | Pullover | ✅ fertig |
| Oberteil | Strickjacke | ✅ fertig |
| Oberteil | Kapuzenjacke | ✅ fertig |
| Oberteil | Regenjacke / Winterjacke | `OFFEN-15/18` |
| Hose | kurze Hose, lange Hose, … | `OFFEN-40` |
| Schuhe | Sandalen, Sneaker, Gummistiefel, Winterstiefel | `OFFEN-41`: SVG-Status |
| Kopf | Sonnenhut, Mütze, … | `OFFEN-42` |
| Zubehör | Sonnenbrille, Sonnencreme, Schirm, Handschuhe, Schal | `OFFEN-43` |
| Wetter | 8 Gruppen aus §8.1 | `OFFEN-30` |
| Hinweis | Gewitter, Glätte, Wind | `OFFEN-44` |
| System | Uhr (veraltet), Fehler | `OFFEN-32/45` |

Jedes Kleidungsstück, das `RULES` referenziert, **muss** im Sprite existieren (siehe AC-12).

## 13. Debug-Modus

Aktiv mit `?debug`. Einzelne Parameter überschreiben die berechneten `Conditions`:

| Parameter | überschreibt |
|---|---|
| `temp` | `tempDisplay` |
| `felt` | `feltMin` (Default: gleich `temp`, falls nur `temp` gesetzt ist) |
| `rain` | `rainProbMax` (%) |
| `rainsum` | `rainSum` (mm) |
| `snow` | `snowSum` (cm) |
| `uv` | `uvMax` |
| `gust` | `gustMax` (km/h) |
| `code` | `code` (WMO) |
| `age` | Datenalter in Minuten (zum Testen von „veraltet“) |

Im Debug-Modus erscheint ein halbtransparentes Overlay unten mit den berechneten Werten (Band, feltMin, aktive Overrides). Ohne Netz funktioniert der Debug-Modus mit Overrides vollständig.

## 14. Offene Punkte

| ID | Thema | Quelle für die Antwort |
|---|---|---|
| OFFEN-01 | iOS-Version bestätigen | Jana |
| OFFEN-02 | Motiv Homescreen-Icon | Jana |
| OFFEN-03 | Angezeigte Temperatur: aktuell oder Minimum im Fenster | Jana (Empfehlung: aktuell) |
| OFFEN-10 | Bänder: Anzahl, Schwellen, Outfits | Logik-Datei |
| OFFEN-11 | Enden der Wärmeskala | Logik-Datei / Jana |
| OFFEN-12/13 | UV-Schwelle; Sonnenhut vs. Mütze | Logik-Datei |
| OFFEN-14–16 | Regen: Schwellen, Regenjacke/Matschhose, Schirm | Logik-Datei |
| OFFEN-17/18/22 | Schnee: Schwelle, Oberteil, Schneematsch | Logik-Datei |
| OFFEN-19/20 | Wind- und Glätte-Schwellen | Jana |
| OFFEN-21 | Priorität beim Zubehör | Jana |
| OFFEN-30/31 | Wetter-Icons: Zuordnung, Nacht-Varianten | Icon-Ordner |
| OFFEN-32/45 | Fehler- und Uhr-Icon | Icon-Ordner / neu zeichnen |
| OFFEN-33/34 | Raster der Zubehör-, Wetter- und Hinweis-Icons | Styleguide |
| OFFEN-35 | Skala: Linien oder Farbverlauf | Jana |
| OFFEN-36/37 | Farben, Schrift final | Styleguide |
| OFFEN-40–44 | SVG-Status Hose, Schuhe, Kopf, Zubehör, Hinweise | Icon-Ordner |

## 15. Akzeptanzkriterien

- **AC-1** Beim Öffnen vom Homescreen läuft die App im Vollbild ohne Safari-UI im Hochformat.
- **AC-2** Mit `?lat&lon` wird der Standort gespeichert, die Parameter verschwinden aus der URL, und beim nächsten Start wird er ohne Parameter geladen.
- **AC-3** Ohne gespeicherten Standort erscheint der Setup-Screen.
- **AC-4** Die Empfehlung basiert auf der aktuellen plus den 3 folgenden Stunden. Die Kleidung folgt `min(apparent_temperature)` im Fenster.
- **AC-5** Für jedes Band in `RULES` zeigt `?debug&felt=<Wert im Band>` genau das Outfit dieses Bands.
- **AC-6** `?debug&felt=<warm>&uv=<≥Schwelle>` zeigt die Sonnenschutz-Icons im Zubehör, unabhängig vom Wetter-Code.
- **AC-7** `?debug&rain=<≥Schwelle>` ersetzt die Schuhe durch Gummistiefel. Mit zusätzlichem `snow` erscheinen Winterstiefel.
- **AC-8** Es werden nie mehr als 3 Zubehör-Icons und nie mehr als 2 Hinweis-Icons angezeigt.
- **AC-9** Leere Slots verändern die Position der übrigen Slots nicht.
- **AC-10** Der Skalenpunkt liegt bei `felt=scale.max` ganz oben und bei `felt=scale.min` ganz unten, dazwischen linear. Werte außerhalb werden begrenzt.
- **AC-11** Im Flugmodus zeigt die App nach vorherigem Laden den letzten Stand. Mit `age≥180` erscheint das Uhr-Icon.
- **AC-12** Ein Test prüft, dass jede in `RULES` referenzierte Icon-ID als `<symbol>` existiert.
- **AC-13** Pixel-Art-Icons werden auf dem iPhone 8 ohne weiche Kanten dargestellt (Sichtprüfung).
- **AC-14** Nach dem Aufwecken des Geräts werden die Daten neu geladen, ohne Nutzeraktion.
- **AC-15** Der gesamte Auslieferungsumfang (`index.html` + `sw.js` + `manifest.json`) bleibt klein. `OFFEN`: Zielgröße, Vorschlag < 150 KB.

## 16. Tasks

| # | Task | Abhängig von |
|---|---|---|
| T1 | Repo anlegen, GitHub Pages aktivieren, Grundgerüst `index.html` / `manifest.json` / `sw.js` | – |
| T2 | Standort-Setup und Verifikation des Homescreen-Speicherkontexts auf dem iPhone 8 | T1 |
| T3 | Open-Meteo-Abruf, Fensterberechnung → `Conditions` | T1 |
| T4 | `RULES`-Block und reine Funktion `recommend()` inkl. Overrides | OFFEN-10…22 |
| T5 | Tests für `recommend()` (Bänder, Overrides, Limits) und Icon-Existenz (AC-12) | T4 |
| T6 | Layout-Raster, Slots, Wärmeskala mit Punkt | OFFEN-33…37 |
| T7 | SVG-Sprite zusammenstellen, IDs nach Konvention | Icon-Ordner |
| T8 | Wetterzeile: Icon-Mapping, Hinweise, Uhr | T3, T7 |
| T9 | Zustände (Setup, Laden, Veraltet, Fehler) und Caching | T3 |
| T10 | Aktualisierung (Aufwecken, 30-min-Intervall) | T3 |
| T11 | Debug-Modus mit Overlay | T4 |
| T12 | Test auf dem Gerät: alle ACs durchgehen | alles |

## 17. Entscheidungslog

| # | Entscheidung |
|---|---|
| Q1 | Ein Screen. Die rechte Skizze ist das Raster, die linke der gefüllte Zustand. |
| Q2 | Die vertikale Leiste ist eine Wärmeskala, ihre Segmente sind die Bänder der Logik. |
| Q3 | v1 hat nur einen Screen, keine Tabs. |
| Q4 | Die Wetterzeile hat Zusatz-Slots für weitere Informationen. |
| Q5 | Beim Oberteil wird nur das äußerste Teil gezeigt. |
| Q6 | Kopf und Zubehör sind getrennte Slots. |
| Q7 | iPhone 8, minimal große Web-App ohne Homeserver. |
| Q8 | Wetterdaten von Open-Meteo. |
| Q9 | Die Spec folgt dem SDD-Format. |
| Q10 | Rollierendes 4-h-Fenster: Kleidung nach der kältesten Stunde, Regen und UV nach dem Maximum. |
| Q11 | Die Bänder richten sich nach der gefühlten Temperatur, angezeigt wird die echte. |
| Q12 | Die Wetterzeile zeigt Fakten, der Zubehör-Slot zeigt Dinge zum Mitnehmen. |
| Q13 | Das Zubehör steht als Spalte links, gespiegelt zur Skala rechts. |
| Q14 | GitHub Pages, der Standort kommt per URL in localStorage. |
| Q15 | Neu laden beim Aufwecken und alle 30 min. Offline bleibt der letzte Stand, ab 3 h mit Uhr-Icon. Normale Auto-Sperre. |
| Q16 | Auf dem Hauptscreen steht nur die Temperatur als Zahl, sonst Icons. |
| Q17 | Das Raster ist fix, leere Slots bleiben leer. |
| Q18 | Der Skalenpunkt sitzt stufenlos. |
| Q19 | Kein Build-Schritt, Sprite inline, Logik-Block oben im Script. |
| Q20 | Off-white Hintergrund, echte Schrift, keine sichtbaren Slot-Rahmen. |
| Q21 | Es gibt einen Debug-Modus per URL. |
