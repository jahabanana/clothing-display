# Kleidungs-Kiosk — Spec v1.0

> Status: **Final, bereit zur Umsetzung. Keine offenen Punkte.** Stand 2026-09-21. Alle `OFFEN`-Punkte aus v0.1 sind entschieden. Wo die Logik-Datei oder die Assets keine Antwort hergaben, gilt eine Entscheidung `A-xx`. Jana hat alle bestätigt (Liste in [§14](#14-entscheidungen-und-erledigte-punkte)). Jede lässt sich später über `RULES` oder ein Asset ändern, ohne die Spec anzufassen. Fehlende Grafiken starten als Platzhalter (§12.4). Die Unterschiede zwischen v0.1, der Logik-Datei und den Dateien im Ordner stehen im Prüfbericht in [§18](#18-prüfbericht-v01--v10). v0.1 liegt als `kleidungs-kiosk-spec.v0.1.md` daneben.
>
> Quellen: `Kleidungs-Kiosk Wetter-Kleidungslogik.md` (2026-09-17), `clothes/` (19 SVGs), `icons/` (12 SVGs). Ein Styleguide liegt nicht vor.

---

## 1. Ziel

Ein altes iPhone 8 hängt als Single-Purpose-Kiosk im Flur. Beim Aufwecken zeigt es dem Kind **auf einen Blick**, was es heute anziehen soll: Kopf, Oberteil, Hose, Schuhe und Zubehör, abgeleitet aus dem Wetter der nächsten Stunden. Das Kind soll sich damit **selbstständig und wettergerecht** anziehen können, ohne lesen zu müssen.

## 2. Scope

**In Scope (v1)**
- Genau ein Screen mit einer Outfit-Empfehlung für die nächsten ~4 Stunden
- Wetterzeile: Zustand, Temperatur, bis zu 2 Hinweis-Icons
- Wärmeskala mit Positionspunkt
- Offline-Fähigkeit (letzter Stand bleibt sichtbar)
- Debug-Modus und Test-Modus per URL

**Out of Scope (v1)**
- Mehrere Screens oder Tabs (Nachmittag, Morgen). Das Layout soll die Erweiterung aber nicht verbauen.
- Schichten-Darstellung. Beim Oberteil wird nur das äußerste Teil gezeigt.
- Mehrere Kinder oder Profile
- Interaktion auf dem Hauptscreen außer Aufwecken (keine Taps, nichts zum Verschieben). Der Setup-Screen für Eltern hat einen Button.
- Server, Accounts, Build-Pipeline
- Aus der Logik-Datei nicht darstellbar und daher weggelassen: Lichtschutzfaktor-Stufen, „Mittagssonne meiden“ (UV 6–7), „dicke“ Handschuhe, Thermohose. Es gibt je ein Icon für Sonnencreme, Handschuhe und lange Hose.

## 3. Zielgerät & Plattform

| | |
|---|---|
| Gerät | iPhone 8 (A11), 375 × 667 pt, 2× Dichte (750 × 1334 px), kein Notch |
| OS | iOS 16 (bestätigt, höchste Version fürs iPhone 8). Jailbreak mit palera1n vorhanden, **v1 braucht ihn nicht** (§3.1) |
| Laufzeit | Safari-Web-App vom Homescreen, `display: standalone` |
| Orientierung | Hochformat, gesperrt über die **Ausrichtungssperre im Kontrollzentrum**. iOS ignoriert `orientation` im Manifest |
| Bildschirm | normale Auto-Sperre, **2 Minuten** (`A-13`), kein Wach-halten-Tweak |
| Hosting | GitHub Pages (statisch, öffentliches Repo, HTTPS, Projektpfad `/<repo>/`) |

### 3.1 Geräte-Einrichtung

- **Kein Gerätecode.** palera1n verlangt auf A11-Geräten unter iOS 16 ohnehin einen deaktivierten Code.
- **Aufwecken** heißt auf dem iPhone 8: Home drücken zeigt den Sperrbildschirm, ein zweiter Druck auf Home öffnet die zuletzt aktive App, also den Kiosk. Das Kind muss zweimal drücken. Den Sperrbildschirm zu überspringen ginge nur per Jailbreak-Tweak und ist nicht Teil von v1.
- **Auto-Sperre 2 min**, Stromsparmodus aus (er erzwingt 30 s). 30 s reichen zum Anziehen nicht.
- **Geführter Zugriff** (Bedienungshilfen) ist empfohlen, damit ein Druck auf Home in der App nicht zum Homescreen führt. In T2 prüfen, ob er mit der Homescreen-Web-App zusammenarbeitet.
- Dauerhaft am Strom, „Optimiertes Laden“ an.
- Kein Feature von v1 hängt vom Jailbreak ab. Ein Neustart ohne erneuten Jailbreak (palera1n ist semi-tethered) ist daher unkritisch.

## 4. Architektur

### 4.1 Dateien

```
/index.html            – Markup, CSS, JS, SVG-Sprite (<symbol>), Logik-Konfig, Debug- und Test-Modus
/sw.js                 – Service Worker (muss eigene Datei sein)
/manifest.json         – Web-App-Manifest
/icon-180.png          – Apple Touch Icon (A-12)
/assets/clothes/*.svg  – Quell-SVGs, zur Laufzeit nicht benutzt
/assets/icons/*.svg    – Quell-SVGs, zur Laufzeit nicht benutzt
/tools/svg2symbol.*    – einmalige Asset-Konvertierung (§12.1), zur Laufzeit nicht benutzt
```

- **Kein Build-Schritt.** Vanilla HTML/CSS/JS (ES2020), keine Abhängigkeiten. Die SVG-Konvertierung ist ein Handgriff beim Hinzufügen eines Icons. Ihr Ergebnis wird in `index.html` eingefügt und eingecheckt.
- **Alle Pfade relativ** (`sw.js`, `manifest.json`, `icon-180.png`), weil die Seite unter `/<repo>/` liegt.
- Alle Icons liegen als `<symbol>` in einem Sprite in `index.html` und werden über `<use href="#…">` eingebunden.
- Der Konfig-Block (`RULES`, `WX`) steht **ganz oben** im Script (§7.1, §8.1).
- Logik und Aggregation sind reine Funktionen: `aggregate(forecast, nowMs) → Conditions | null` und `recommend(conditions, RULES, WX) → Outfit`.

**Head-Pflichtangaben**

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#FAF7F0">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-180.png">
```

Dazu Kiosk-CSS: `overflow: hidden` und fixiertes `body` (kein Gummiband-Scrollen), `user-select: none`, `-webkit-touch-callout: none`, `touch-action: none` auf dem Hauptscreen.

**manifest.json**

```json
{
  "name": "Kleidungs-Kiosk",
  "short_name": "Anziehen",
  "display": "standalone",
  "background_color": "#FAF7F0",
  "theme_color": "#FAF7F0",
  "icons": [{ "src": "icon-180.png", "sizes": "180x180", "type": "image/png" }]
}
```

Bewusst **ohne `start_url`**: Ohne sie startet die Homescreen-App mit der URL, unter der sie hinzugefügt wurde, also samt `?lat&lon` (§4.3). Ebenfalls ohne `orientation`, weil iOS das nicht unterstützt.

### 4.2 Service Worker

- **App-Shell** (`./`, `index.html`, `manifest.json`, `icon-180.png`): cache-first. Der Cache-Name enthält eine `CACHE_VERSION`-Konstante.
- **Navigationen mit `caches.match(request, { ignoreSearch: true })`** beantworten, weil die Start-URL Query-Parameter tragen kann.
- **Jede Änderung an `index.html` erfordert eine neue `CACHE_VERSION` in `sw.js`.** Nur ein geändertes `sw.js` löst ein Update aus.
- Requests an andere Origins (Open-Meteo) fängt der SW nicht ab (kein `respondWith`). Die letzte erfolgreiche Antwort liegt roh mit Zeitstempel in `localStorage` (`kiosk.lastForecast` = `{ fetchedAt, data }`).
- **Update-Ablauf:**
  1. Beim Aufwecken ruft die Seite `registration.update()` auf, weil beim Fortsetzen der Web-App keine Navigation stattfindet.
  2. Der neue SW cacht vor, ruft `skipWaiting()` auf und übernimmt in `activate` per `clients.claim()`. Alte Caches werden gelöscht.
  3. Die Seite lädt bei `controllerchange` einmal neu, aber nur, wenn vorher schon ein Controller aktiv war (kein Reload bei der Erstinstallation).

### 4.3 Konfiguration (Standort)

- Der Standort gehört **nicht** ins Repo.
- Gespeichert wird er in `localStorage` (`kiosk.location` = `{ lat, lon }`), **gerundet auf 2 Nachkommastellen** (≈ 1 km, reicht fürs Wetter).
- **Weg A, URL:** `index.html?lat=<lat>&lon=<lon>` in Safari öffnen, dann „Zum Home-Bildschirm“. Die App übernimmt gültige Parameter bei **jedem** Start (idempotent) und entfernt sie per `history.replaceState` aus der Adressleiste. Gültig heißt: Zahl, `lat` in −90…90, `lon` in −180…180.
- **Weg B, Button:** Der Setup-Screen (§9) hat den Button „Standort ermitteln“ (`navigator.geolocation`, einmalig). Das funktioniert direkt im Homescreen-Kontext und umgeht das Problem getrennter Speicher.
- Hintergrund: Unter iOS hat die Homescreen-App einen eigenen Speicher, getrennt von Safari. Weg A funktioniert nur, weil die Start-URL die Parameter mitbringt (kein `start_url`, §4.1). T2 verifiziert beide Wege auf dem Gerät.

## 5. Datenquelle

**Open-Meteo Forecast API** (kein Key, CORS ok).

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}&longitude={lon}
  &current=temperature_2m
  &hourly=temperature_2m,apparent_temperature,precipitation_probability,
          precipitation,snowfall,snow_depth,weather_code,uv_index,
          wind_gusts_10m,is_day
  &timezone=auto
  &timeformat=unixtime
  &past_hours=6
  &forecast_days=2
```

| Feld | Einheit | Gültigkeit laut API |
|---|---|---|
| `temperature_2m`, `apparent_temperature` | °C | Momentanwert zur vollen Stunde |
| `weather_code`, `is_day`, `uv_index`, `snow_depth` | WMO / 0‑1 / Index / **m** | Momentanwert |
| `precipitation` | mm | **Summe der vorangehenden Stunde** |
| `snowfall` | cm | **Summe der vorangehenden Stunde** |
| `precipitation_probability` | % | **Wahrscheinlichkeit für > 0,1 mm in der vorangehenden Stunde** |
| `wind_gusts_10m` | km/h (Default) | **Maximum der vorangehenden Stunde** |

- `timeformat=unixtime` macht die Stundensuche robust (Zahlenvergleich statt Zeitzonen-Strings).
- `past_hours=6` liefert die Stunden vor dem Fenster für die Glätte-Regel.
- `forecast_days=2` hält das Fenster auch spät abends vollständig. Mit gecachten Daten reicht es bis zum Ende des Folgetags (§9).
- Fetch mit **Timeout 10 s** (`AbortController`).

## 6. Aggregation: Wetterfenster

**Fenster:** die aktuelle Stunde plus die 3 folgenden, also 4 Stunden, rollierend und unabhängig von der Tageszeit.

`i` ist der Index mit `hourly.time[i] ≤ jetzt < hourly.time[i] + 3600`.

- **Momentanwerte** (Temperaturen, Code, UV, Schneedecke, `is_day`): Indizes `i … i+3`
- **Werte der vorangehenden Stunde** (Niederschlag, Wahrscheinlichkeit, Schneefall, Böen): Indizes `i+1 … i+4`. Sie decken dieselben 4 Stunden ab.
- Fehlt `i` oder `i+4` in den Daten, liefert `aggregate()` `null` (§9).
- `null` in einzelnen API-Werten wird bei min, max und Summe übersprungen. Sind alle Werte eines Felds `null`, gilt 0 bzw. bei Temperaturen „keine Daten“ → `null`.

| Feld | Berechnung | Wofür |
|---|---|---|
| `tempDisplay` | `current.temperature_2m`, falls `current.time` < 60 min alt, sonst `temperature_2m[i]` | Zahl in der Wetterzeile |
| `feltMin` | min(`apparent_temperature`) | Band, Kleidung, Skala |
| `tempMin` | min(`temperature_2m`) | Glätte-Hinweis |
| `rainProbMax` | max(`precipitation_probability`) | Regen-Override |
| `rainSum` | Summe(`precipitation`) | Regen-Override, Glätte |
| `wetBefore` | Summe(`precipitation`) über die bis zu 6 Stunden vor dem Fenster (`i−5 … i`) | Glätte |
| `snowSum` | Summe(`snowfall`) | Schnee-Override |
| `snowDepth` | max(`snow_depth`) × 100 (m → cm) | Schnee-Override |
| `uvMax` | max(`uv_index`) | Sonnenschutz |
| `gustMax` | max(`wind_gusts_10m`) | Wind |
| `code` | „schwerster“ `weather_code` im Fenster (Rangfolge §8.1) | Wetter-Icon |
| `isDay` | `is_day[i] === 1` | Tag- oder Nacht-Icon |

**Leitregel:** Die Kleidung richtet sich nach der **kältesten gefühlten** Stunde, Regen und UV nach dem **Maximum** im Fenster. Die Bandgrenzen gelten für den ungerundeten Wert.

```ts
type Conditions = {
  tempDisplay: number; feltMin: number; tempMin: number;
  rainProbMax: number; rainSum: number; wetBefore: number;
  snowSum: number; snowDepth: number;   // cm
  uvMax: number; gustMax: number;       // km/h
  code: number; isDay: boolean;
};
```

## 7. Entscheidungslogik

### 7.1 Konfig-Block

Werte sind Icon-Namen ohne Präfix. Gerendert wird `i-<slot>-<name>` (§12).

```js
// ===== KLEIDUNGSLOGIK — hier anpassen =====
const RULES = {
  // Wärmebänder von warm nach kalt. min = untere Schwelle für feltMin in °C,
  // inklusiv, ungerundet. Quelle: Temperatur-Tabelle der Logik-Datei.
  bands: [
    { id: 'heiss', min:  25, head: null,     top: 'tshirt',      bottom: 'hose-kurz', shoes: 'sandalen',      acc: [] },
    { id: 'warm',  min:  20, head: null,     top: 'tshirt',      bottom: 'hose-kurz', shoes: 'sneaker',       acc: [] },                    // A-01
    { id: 'mild',  min:  15, head: null,     top: 'longsleeve',  bottom: 'hose-lang', shoes: 'sneaker',       acc: [] },                    // A-02
    { id: 'kuehl', min:  10, head: null,     top: 'teddyjacke',  bottom: 'hose-lang', shoes: 'sneaker',       acc: [] },                    // A-03
    { id: 'kalt',  min:   5, head: 'muetze', top: 'winterjacke', bottom: 'hose-lang', shoes: 'sneaker',       acc: ['handschuhe'] },
    { id: 'eisig', min:   0, head: 'muetze', top: 'winterjacke', bottom: 'hose-lang', shoes: 'winterstiefel', acc: ['handschuhe', 'schal'] },
    { id: 'frost', min: -Infinity, head: 'muetze', top: 'schneeanzug', bottom: 'hose-lang', shoes: 'winterstiefel', acc: ['handschuhe', 'schal'] }, // A-15
  ],
  scale: { max: 30, min: -5 },   // Enden der Wärmeskala in °C → 7 Segmente à 5 °C (A-09)

  sun: {                          // nur UV-Index, unabhängig von Temperatur und Bewölkung
    uvMin: 3,                     // ab hier Sonnencreme + Sonnenhut
    uvGlasses: 8,                 // ab hier zusätzlich Sonnenbrille
    head: 'sonnenhut',            // nur, wenn das Band keinen Kopf setzt (Mütze gewinnt)
  },
  wind: {                         // Wind = gustMax ≥ gustMin                                   A-04
    gustMin: 50,                  // km/h Böen, niedrigste DWD-Warnstufe (Bft 7)
    top: 'kapuzenjacke',          // „Kapuze/Windjacke“ laut Logik-Datei
    topInBands: ['warm', 'mild', 'kuehl'],   // nicht bei Hitze; ab 'kalt' hat die Winterjacke eine Kapuze
  },
  rain: {                         // Regen = rainProbMax ≥ probMin UND rainSum ≥ sumMin        A-05
    probMin: 50,                  // %
    sumMin: 0.5,                  // mm in 4 h
    top: 'regenjacke',
    topInBands: ['heiss', 'warm', 'mild', 'kuehl'],            // Winterjacke und Schneeanzug bleiben
    shoes: 'gummistiefel',
    shoesInBands: ['heiss', 'warm', 'mild', 'kuehl', 'kalt'],  // Winterstiefel bleiben
  },
  snow: {                         // Schnee = snowSum ≥ sumMin ODER snowDepth ≥ depthMin       A-06
    sumMin: 0.2,                  // cm Neuschnee in 4 h
    depthMin: 2,                  // cm liegender Schnee
    top: 'schneeanzug',           // in allen Bändern
    shoes: 'winterstiefel',       // in allen Bändern, schlägt Gummistiefel, auch über 0 °C
  },
  ice: {                          // Glätte-Hinweis                                             A-07
    tempMax: 1,                   // °C: tempMin ≤ tempMax …
    wetMin: 0.1,                  // … UND (rainSum ≥ wetMin ODER wetBefore ≥ wetMin)
    freezingCodes: [56, 57, 66, 67],   // gefrierender Niesel/Regen im Fenster: immer Glätte
  },
  maxAccessories: 3,
  accessoryOrder: ['sonnencreme', 'handschuhe', 'schal', 'sonnenbrille'],   // A-08
  maxHints: 2,
};
```

### 7.2 Auswertungsreihenfolge

Spätere Schritte überschreiben frühere. Für das Oberteil gilt damit Schnee > Regen > Wind > Band, für die Schuhe Schnee > Regen > Band.

1. **Band:** das erste Band mit `feltMin >= band.min`.
2. **Basis-Outfit** aus dem Band übernehmen.
3. **Sonne:** Bei `uvMax >= sun.uvMin` kommt `sonnencreme` ins Zubehör, und der Kopf wird `sun.head`, falls er leer ist. Bei `uvMax >= sun.uvGlasses` kommt zusätzlich `sonnenbrille` ins Zubehör.
4. **Wind:** Bei `gustMax >= wind.gustMin` wird das Oberteil `wind.top`, wenn das Band in `wind.topInBands` steht.
5. **Regen:** Bei Regen (Definition in `rain`) wird das Oberteil `rain.top` (Band in `topInBands`) und werden die Schuhe `rain.shoes` (Band in `shoesInBands`).
6. **Schnee:** Bei Schnee werden Oberteil und Schuhe `snow.top` bzw. `snow.shoes`. Das gilt auch bei Schneematsch über 0 °C.
7. **Zubehör:** deduplizieren, nach `accessoryOrder` sortieren (Unbekanntes ans Ende), auf `maxAccessories` kürzen.
8. **Hinweise** (§8.2), gekürzt auf `maxHints`.
9. **Wetter-Icon** aus `code` und `isDay` (§8.1).
10. **Skala:** `scalePos = (scale.max − clamp(feltMin, scale.min, scale.max)) / (scale.max − scale.min)`.

### 7.3 Datenmodell

```ts
type Outfit = {
  band: string;                  // Band-ID
  head: IconId | null;           // volle Symbol-IDs, z. B. 'i-head-muetze'
  top: IconId;                   // nur äußerstes Teil
  bottom: IconId;
  shoes: IconId;
  accessories: IconId[];         // 0–3, sortiert
  weatherIcon: IconId;
  hints: IconId[];               // 0–2, Glätte vor Wind
  scalePos: number;              // 0 (oben, warm) … 1 (unten, kalt)
  overrides: ('sun' | 'glasses' | 'wind' | 'rain' | 'snow')[];   // fürs Debug-Overlay
};
```

## 8. Wetterzeile

### 8.1 Wetter-Icon (WMO-Code → Icon)

Die Konfiguration steht als `WX` neben `RULES`. Der Rang entspricht der Reihenfolge, höher heißt schwerer.

| Rang | Gruppe | WMO-Codes | Icon Tag | Icon Nacht (`isDay = false`) |
|---|---|---|---|---|
| 0 | klar | 0, 1 | `i-wx-klar` | `i-wx-klar-nacht` (A-14) |
| 1 | teilweise bewölkt | 2 | `i-wx-teilweise` | `i-wx-bedeckt` (A-14) |
| 2 | bedeckt | 3 | `i-wx-bedeckt` | = Tag |
| 3 | Nebel | 45, 48 | `i-wx-nebel` | = Tag |
| 4 | Niesel | 51, 53, 55, 56, 57 | `i-wx-niesel` | = Tag |
| 5 | Regen | 61, 63, 65, 66, 67, 80, 81, 82 | `i-wx-regen` | = Tag |
| 6 | Schnee | 71, 73, 75, 77, 85, 86 | `i-wx-schnee` | = Tag |
| 7 | Gewitter | 95, 96, 99 | `i-wx-gewitter` | = Tag |

Unbekannte Codes werden wie „bedeckt“ behandelt.

### 8.2 Hinweis-Icons (max. 2)

Priorität absteigend:
1. **Glätte** (`i-hint-glaette`): ein Code aus `ice.freezingCodes` im Fenster ODER (`tempMin ≤ ice.tempMax` UND (`rainSum ≥ ice.wetMin` ODER `wetBefore ≥ ice.wetMin`))
2. **Wind** (`i-hint-wind`): `gustMax ≥ wind.gustMin`

Gewitter ist **kein** Hinweis mehr: `code` ist der schwerste Code im Fenster, das Wetter-Icon zeigt Gewitter also immer schon. Mit zwei möglichen Hinweisen greift das Limit von 2 nie, es bleibt aber als Schutz.

Zusätzlich gibt es den Systemzustand **„Daten alt“** (`i-sys-uhr`, §9). Er belegt keinen Hinweis-Platz, sondern hat einen eigenen Platz am rechten Rand.

Sonnencreme und Regenjacke sind **keine** Hinweise, sie gehören zur Kleidung. Jedes Icon hat genau einen Ort. Die Windjacke (Kleidung) und das Wind-Icon (Wetter-Fakt) sind zwei verschiedene Icons.

## 9. Zustände

`kiosk.lastForecast` speichert die **rohe** API-Antwort. Das Fenster wird bei jedem Rendern neu relativ zur aktuellen Uhrzeit berechnet, auch aus dem Cache. So zeigt der Kiosk nach 5 h ohne Netz die Prognose für die jetzigen Stunden und nicht für längst vergangene.

| Zustand | Bedingung | Anzeige |
|---|---|---|
| Setup | kein gültiger Standort gespeichert | Eltern-Screen: kurzer Text, Beispiel-URL, Button „Standort ermitteln“ (Text ok) |
| Erstes Laden | Standort vorhanden, `aggregate()` aus dem Cache ergibt `null`, Request läuft | leere Slots, Temperatur leer, am Platz des Wetter-Icons ein pulsierender Punkt (`--ink-soft`) |
| Normal | `aggregate()` ≠ `null`, `fetchedAt` < 180 min alt | vollständige Empfehlung |
| Veraltet | `aggregate()` ≠ `null`, `fetchedAt` ≥ 180 min alt | Empfehlung plus `i-sys-uhr` |
| Fehler | `aggregate()` ergibt `null` (kein Cache, oder das Fenster liegt außerhalb der Daten, also nach ~40 h offline) und der Request ist fehlgeschlagen oder abgelaufen | leere Slots, Temperatur leer, `i-sys-fehler` am Platz des Wetter-Icons |

## 10. Aktualisierung

- **Sofort aus dem Cache rendern**, dann im Hintergrund abrufen und bei Erfolg neu rendern.
- Auslöser: Laden, `visibilitychange` → `visible`, `pageshow` (Aufwecken) sowie alle **30 min** per `setInterval`, solange die Seite sichtbar ist.
- **Entprellen:** kein neuer Abruf, wenn der letzte Versuch weniger als 60 s zurückliegt. `visibilitychange` und `pageshow` feuern beim Aufwecken oft beide.
- Beim Aufwecken zusätzlich `registration.update()` (§4.2).

## 11. Layout & Visuelles

### 11.1 Raster (iPhone 8, 375 × 667 pt, Viewport inkl. Statusleiste)

```
┌───────────────────────────────────────────┐  Statusleiste 20 pt (safe-area-inset-top)
│ [Wetter]  23°C           [H1] [H2] [⏱]    │  Wetterzeile 72 pt
├──────┬─────────────────────────────┬──────┤  Abstand 8 pt
│ [Z1] │          [ KOPF ]           │ ┌──┐ │
│ [Z2] │                             │ │  │ │
│ [Z3] │         [ OBERTEIL ]        │ │ ●│ │  Wärmeskala
│      │                             │ │  │ │
│      │           [ HOSE ]          │ │  │ │  4 × 136 pt
│      │                             │ │  │ │
│      │          [ SCHUHE ]         │ └──┘ │
└──────┴─────────────────────────────┴──────┘  Rand unten 23 pt
 16 | 56 pt |        247 pt         | 40 pt | 16
```

**Feste Maße in pt.** Alle Positionen und Größen sind Vielfache von 0,5 pt, also ganze Gerätepixel. Im Kleidungsraster gibt es keine `fr`-, `%`- oder `vh`-Größen, weil z. B. 559 / 4 = 139,75 pt Pixel-Art unscharf macht.

| Element | x | y | Größe |
|---|---|---|---|
| Wetter-Icon | 16 | 32 | 48 × 48 (Line-Icon 24er Raster × 2) |
| Temperatur | 76 | vertikal zentriert in 20–92 | Schrift §11.3 |
| Hinweis H1, H2 | 235, 279 | 38 | 36 × 36 (× 1,5) |
| Uhr ⏱ | 323 | 38 | 36 × 36 |
| Kleidungs-Slot k (0…3) | 72 | 100 + 136·k | 247 × 136 |
| Kleidungs-Icon in Slot k | 131,5 | 104 + 136·k | 128 × 128 (32er Raster × 4 pt) |
| Zubehör-Icon k (0…2) | 20 | 104 + 56·k | 48 × 48 (32er Raster × 1,5 pt) |
| Wärmeskala (Balken) | 327 | 100 | 24 × 544 |

- Das Raster ist **fix**. Leere Slots bleiben leer, nichts rückt nach. Das gilt auch für H1, H2 und ⏱.
- **Keine sichtbaren Slot-Rahmen.** Nur die Wärmeskala hat eine Kontur.
- **Pixel-Art** (Kleidung, Zubehör): `shape-rendering="crispEdges"`, ganzzahlige Skalierung (4 pt = 8 px bzw. 1,5 pt = 3 px pro Kunstpixel).
- **Line-Icons** (Wetter, Hinweise, System): normales Antialiasing, **kein** `crispEdges` (es würde runde Striche zerreißen). Farbe über `stroke="currentColor"`.

### 11.2 Wärmeskala

- Vertikal, **oben warm, unten kalt**, abgerundeter Balken mit 2 pt Kontur in `--ink`, Radius 12 pt.
- Anzahl der Segmente = Anzahl der Bänder (7). Trennlinien (1 pt, `--ink`) liegen an den Bandgrenzen, **proportional zur Temperatur**: `y = 100 + (scale.max − band.min) / (scale.max − scale.min) × 544`, gerundet auf 0,5 pt. Mit 30…−5 °C sind die Segmente gleich hoch (≈ 77,5 pt).
- **Nur Linien, kein Farbverlauf** (A-09). Die Farbe kommt von den Kleidungs-Icons.
- **Punkt stufenlos:** Kreis 16 pt, gefüllt in `--ink`, Mittelpunkt `x = 339`, `y = 108 + scalePos × 528`.
- Reine Anzeige ohne Interaktion.

### 11.3 Farbe & Typografie

Ein Styleguide liegt nicht vor. Die Werte sind aus der Palette der Icons abgeleitet (A-10):

| Token | Wert | Verwendung |
|---|---|---|
| `--bg` | `#FAF7F0` | Hintergrund, fest, kein Dark Mode |
| `--ink` | `#3B3632` | Temperatur, Line-Icons, Skala, Punkt |
| `--ink-soft` | `rgba(59, 54, 50, 0.35)` | Ladeindikator, Platzhalter-Icons |

- Temperatur in **echter Schrift**: `font-family: ui-rounded, -apple-system, system-ui, sans-serif`, 40 pt, Gewicht 600, `font-variant-numeric: tabular-nums`. Die Systemschrift wird nicht nachgeladen (A-11).
- Format: `Math.round()`, dann `23°C`. Minusgrade mit echtem Minuszeichen (`−3°C`, U+2212), nie `−0°C`.
- Außer der Temperatur gibt es keinen Text auf dem Hauptscreen.
- **Homescreen-Icon** `icon-180.png`: das T-Shirt-Pixel-Art × 5 (160 px) mittig auf `#FAF7F0`, 180 × 180, ohne Transparenz (A-12).

## 12. Icon-Inventar

Symbol-IDs: `i-<slot>-<name>` mit den Slots `top`, `bottom`, `shoes`, `head`, `acc`, `wx`, `hint`, `sys`. **Alle vorhandenen Icons kommen ins Sprite**, auch unbenutzte, damit ein Tausch nur `RULES` betrifft (≈ 1,5 KB pro Icon).

### 12.1 Konvertierung (T7)

Die Quell-SVGs sind so nicht einbettbar: 477 KB für 19 Kleidungs-Icons (§18, P-05). `tools/svg2symbol` macht pro Datei:
1. `<metadata>` (C2PA-Manifest, 7,7 KB pro Datei) entfernen
2. 640er Koordinaten durch 20 teilen → `viewBox="0 0 32 32"`
3. Pixel pro Farbe zu einem `<path>` zusammenfassen (horizontale Läufe)
4. Als `<symbol id="…" viewBox="0 0 32 32">` ausgeben, Farben kleingeschrieben

Gemessen ergibt das ≈ 28 KB für alle 19 Kleidungs-Icons. Line-Icons werden nur umbenannt, `stroke="black"` wird zu `currentColor`.

### 12.2 Kleidung & Zubehör (Pixel-Art, 32 × 32)

| Symbol-ID | Quelldatei (`clothes/`) | verwendet in | Status |
|---|---|---|---|
| `i-top-tshirt` | `t-shirt_blau_32x32 2.svg` | heiss, warm | ✅ |
| `i-top-longsleeve` | `longsleeve_oliv-gestreift_32x32.svg` | mild | ✅ |
| `i-top-strickjacke` | `strickjacke_mauve_32x32.svg` | – (Alternative mild, A-02) | ✅ |
| `i-top-pullover` | `pullover_gelb_32x32.svg` | – (nie äußerstes Teil, P-08) | ✅ |
| `i-top-kapuzenpullover` | `kapuzenpullover_gelb_32x32.svg` | – (Alternative Wind, A-04) | ✅ |
| `i-top-teddyjacke` | `teddyjacke_creme_32x32.svg` | kuehl | ✅ |
| `i-top-kapuzenjacke` | `kapuzenjacke_pink_32x32 1.svg` | Wind-Override | ⚠️ Stilbruch, neu zeichnen (P-04) |
| `i-top-winterjacke` | `winterjacke_rot_32x32.svg` | kalt, eisig | ✅ |
| `i-top-schneeanzug` | `schneeanzug_blauviolett_32x32.svg` | frost, Schnee-Override | ✅ |
| `i-top-regenjacke` | – | Regen-Override | ⏳ Platzhalter: Kapuzenjacke |
| `i-bottom-hose-kurz` | `hose-kurz_khaki_32x32.svg` | heiss, warm | ✅ |
| `i-bottom-hose-lang` | `hose-lang_denim_32x32.svg` | mild … frost | ✅ |
| `i-shoes-sandalen` | `sandalen_orange_32x32.svg` | heiss | ✅ |
| `i-shoes-sneaker` | `sneaker_weiss_32x32.svg` | warm … kalt | ✅ |
| `i-shoes-gummistiefel` | `gummistiefel_gelb_32x32.svg` | Regen-Override | ✅ |
| `i-shoes-winterstiefel` | `winterstiefel_braun_32x32.svg` | eisig, frost, Schnee | ✅ |
| `i-head-muetze` | `muetze_rot_32x32.svg` | kalt, eisig, frost | ✅ |
| `i-head-sonnenhut` | `sonnenhut_stroh_32x32.svg` | UV ≥ 3 | ✅ |
| `i-acc-schal` | `schal_petrol_32x32.svg` | eisig, frost | ✅ |
| `i-acc-sonnenbrille` | `sonnenbrille_koralle_32x32.svg` | UV ≥ 8 | ✅ |
| `i-acc-handschuhe` | – | kalt, eisig, frost | ⏳ Platzhalter: gestricheltes Quadrat |
| `i-acc-sonnencreme` | – | UV ≥ 3 | ⏳ Platzhalter: gestricheltes Quadrat |

Falls die pinke Kapuzenjacke in Wirklichkeit die Regenjacke ist, wird sie zu `i-top-regenjacke` umbenannt, und der Wind-Override nimmt den Kapuzenpullover.

### 12.3 Wetter, Hinweise, System (Line-Icons, 24 × 24, 2er Strich, runde Enden)

| Symbol-ID | Quelldatei (`icons/`) | Status |
|---|---|---|
| `i-wx-klar` | `weather-icons-7.svg` (Sonne) | ✅ |
| `i-wx-klar-nacht` | `weather-icons-4.svg` (Mond) | ✅ |
| `i-wx-teilweise` | `weather-icons-3.svg` (Sonne hinter Wolke) | ✅ |
| `i-wx-bedeckt` | `weather-icons.svg` (Wolke) | ✅ |
| `i-wx-nebel` | – | ⏳ Platzhalter: Wolke |
| `i-wx-niesel` | `weather-icons-2.svg` (Wolke mit Punkten) | ✅ |
| `i-wx-regen` | `weather-icons-1.svg` (Wolke mit Strichen) | ✅ |
| `i-wx-schnee` | `weather-icons-5.svg` (Schneeflocke) | ✅ |
| `i-wx-gewitter` | – | ⏳ Platzhalter: Regenwolke |
| `i-hint-wind` | `weather-icons-11.svg` (Wind) | ✅ |
| `i-hint-glaette` | – | ⏳ Platzhalter: Thermometer (`weather-icons-9.svg`) |
| `i-sys-uhr` | – | ⏳ Platzhalter: einfache Uhr (§12.4) |
| `i-sys-fehler` | – | ⏳ Platzhalter: Warnkreis (§12.4) |
| (unbenutzt) | `weather-icons-6.svg` (Funkeln), `-8` (Sonnenauf-/untergang), `-10` (Schirm) | – |

Fehlende Line-Icons möglichst aus **demselben Icon-Set** nehmen (Wolke mit Blitz, Wolke mit Nebel, Uhr, Wolke durchgestrichen oder Warnkreis), damit Strichstärke und Stil passen.

### 12.4 Platzhalter

v1 startet mit Platzhaltern (Q34). Jede ⏳-ID existiert von Anfang an als `<symbol>` mit dem Attribut `data-placeholder`. So prüft AC-12 die IDs sofort, und eine nachgelieferte Grafik ersetzt nur den Inhalt des Symbols. Wo es ein inhaltlich passendes Icon gibt, verweist der Platzhalter darauf, damit das Kind etwas Sinnvolles sieht:

| ID | Platzhalter | Umsetzung |
|---|---|---|
| `i-top-regenjacke` | Kapuzenjacke | `<symbol id="i-top-regenjacke" viewBox="0 0 32 32" data-placeholder><use href="#i-top-kapuzenjacke"/></symbol>` |
| `i-wx-nebel` | Wolke | `<use href="#i-wx-bedeckt"/>` |
| `i-wx-gewitter` | Regenwolke | `<use href="#i-wx-regen"/>` |
| `i-hint-glaette` | Thermometer | Pfade aus `weather-icons-9.svg` kopiert |
| `i-sys-uhr` | Uhr | `<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>` im Strichstil des Sets (2er Strich, runde Enden, `currentColor`) |
| `i-sys-fehler` | Warnkreis | `<circle cx="12" cy="12" r="10"/><path d="M12 7v6M12 17h.01"/>` im selben Strichstil |
| `i-acc-handschuhe`, `i-acc-sonnencreme` | gestricheltes, abgerundetes Quadrat in `--ink-soft` | kein passendes Ersatz-Icon vorhanden |

- Solange die Regenjacke fehlt, zeigen Wind und Regen dieselbe Jacke. Der Regen ist trotzdem an den Gummistiefeln erkennbar.
- Handschuhe und Sonnencreme sind als Erstes nachzuliefern, weil das Kind bei ihnen nur ein leeres Kästchen sieht.
- `?test` listet verbleibende Platzhalter als **Warnung**, nicht als Fehler.

## 13. Debug- & Test-Modus

### 13.1 Debug (`?debug`)

- `?debug` **ohne** weitere Parameter: Live-Daten plus Overlay.
- `?debug` **mit** mindestens einem Parameter: ein vollständig synthetisches Szenario. Alle nicht gesetzten Felder nehmen die Defaults unten an. Es gibt keinen Netzabruf, und der Setup-Screen wird übersprungen, damit Tests deterministisch und offline laufen.

| Parameter | überschreibt | Default |
|---|---|---|
| `temp` | `tempDisplay` | `felt`, sonst 15 |
| `felt` | `feltMin` | `temp`, sonst 15 |
| `tmin` | `tempMin` | `temp`, sonst 15 |
| `rain` | `rainProbMax` (%) | 0 |
| `rainsum` | `rainSum` (mm) | 0 |
| `wet` | `wetBefore` (mm) | 0 |
| `snow` | `snowSum` (cm) | 0 |
| `depth` | `snowDepth` (cm) | 0 |
| `uv` | `uvMax` | 0 |
| `gust` | `gustMax` (km/h) | 0 |
| `code` | `code` (WMO) | 0 |
| `night` | `isDay = false` (Flag) | Tag |
| `age` | Datenalter in Minuten | 0 |

Das Overlay ist halbtransparent, liegt unten und zeigt Band, `feltMin`, aktive `overrides`, Hinweise und das Datenalter.

### 13.2 Test (`?test`)

Die Logik liegt in `index.html`, und es gibt keinen Build. Deshalb laufen die Tests in der Seite selbst und geben eine PASS/FAIL-Liste als Text aus:
- tabellengetriebene Fälle für `recommend()`: jedes Band, jede Bandgrenze (z. B. 24,9 / 25,0), Sonne, Wind, Regen, Schnee, Kombinationen, Limits
- `aggregate()` mit einer eingebetteten Beispiel-Antwort: Index-Versatz, `null`-Werte, Fenster außerhalb der Daten
- Icon-Existenz: jede ID aus `RULES`, `WX`, Hinweisen und System ist ein `<symbol>` (AC-12)
- Warnung, solange Platzhalter existieren

## 14. Entscheidungen und erledigte Punkte

### 14.1 Entscheidungen (von Jana am 2026-09-21 bestätigt)

Die IDs heißen weiter `A-xx`, weil die Spec an vielen Stellen darauf verweist. Jede ist eine Zeile in `RULES` oder ein Asset und lässt sich nach dem Alltagstest (T12) anpassen.

| ID | Entscheidung | Begründung |
|---|---|---|
| A-01 | 20–24 °C: kurze Hose | Logik sagt „kurz/lang“. Die gefühlte Minimaltemperatur ist schon konservativ |
| A-02 | 15–19 °C: Longsleeve | Logik: „Longsleeve oder T-Shirt mit Strickjacke“. Tausch auf `strickjacke` ist eine Zeile |
| A-03 | „normale Jacke“ (10–14 °C) = Teddyjacke | einzige Übergangsjacke ohne andere Rolle. Trägt das Kind eine andere, wird in `RULES` das Band `kuehl` geändert |
| A-04 | Wind: Kapuzenjacke in warm/mild/kühl, ab Böen 50 km/h, dazu das Wind-Icon | Logik: „zusätzlich Kapuze/Windjacke, unabhängig von Temperatur“. Bei ≥ 25 °C keine Jacke, ab 'kalt' Winterjacke mit Kapuze |
| A-05 | Regen: ≥ 50 % UND ≥ 0,5 mm in 4 h. Regenjacke nur in Bändern ohne Winterjacke, Gummistiefel nur statt Sandalen/Sneaker | UND vermeidet Gummistiefel bei „vielleicht ein Tropfen“. Winterstiefel sind wärmer und dicht |
| A-06 | Schnee: ≥ 0,2 cm Neuschnee ODER ≥ 2 cm Schneedecke. Schnee gewinnt immer, auch über 0 °C | Schneematsch → Winterstiefel. Liegender Schnee am Morgen danach zählt auch |
| A-07 | Glätte: gefrierender Regen ODER (≤ 1 °C UND nass im Fenster oder 6 h davor) | typischer Fall ist Nässe vom Vorabend, die morgens friert |
| A-08 | Zubehör-Reihenfolge: Sonnencreme, Handschuhe, Schal, Sonnenbrille | greift nur bei 4 Teilen gleichzeitig (UV ≥ 8 bei ≤ 4 °C), praktisch nie |
| A-09 | Skala 30 … −5 °C, nur Linien | ergibt 7 gleich hohe Segmente, wie in der Skizze |
| A-10 | Farben `#FAF7F0` / `#3B3632` | kein Styleguide vorhanden |
| A-11 | Schrift `ui-rounded` 600, 40 pt | passt zu den runden Line-Icons |
| A-12 | Homescreen-Icon = T-Shirt | eindeutigstes Motiv |
| A-13 | Auto-Sperre 2 min | 30 s reichen zum Anziehen nicht |
| A-14 | Nachts: Mond statt Sonne, Wolke statt Sonne-mit-Wolke | Mond-Icon vorhanden, im Winter ist es morgens dunkel |
| A-15 | Unter 0 °C: Schneeanzug im Oberteil-Slot, im Hose-Slot weiter die lange Hose | Q5 gilt nur fürs Oberteil. Das Kind sieht, dass drunter eine Hose gehört |

### 14.2 Von Jana geklärt

| ID | Punkt | Ergebnis |
|---|---|---|
| O-1 | iOS-Version | iOS 16 |
| O-2 | Lizenz des Line-Icon-Sets | für den persönlichen Gebrauch frei, das reicht (Q33) |
| O-3 | Fehlende Grafiken: Regenjacke, Handschuhe, Sonnencreme (Pixel-Art); Nebel, Gewitter, Glätte, Uhr, Fehler (Line); Kapuzenjacke ohne Kontur neu | Start mit Platzhaltern (§12.4). Grafiken kommen später (T7a), sie blockieren nichts |

### 14.3 Verbleib der v0.1-Punkte

| v0.1 | Entscheidung |
|---|---|
| OFFEN-01 | iOS 16 (O-1) |
| OFFEN-02 | T-Shirt (A-12) |
| OFFEN-03 | aktuelle Temperatur (§6), Fallback Stundenwert |
| OFFEN-10 | 7 Bänder aus der Logik-Tabelle (§7.1, A-01…03, A-15) |
| OFFEN-11 | 30 … −5 °C (A-09) |
| OFFEN-12/13 | UV ≥ 3 Creme und Hut, UV ≥ 8 Brille (Logik-Datei). Mütze schlägt Sonnenhut |
| OFFEN-14 | UND, 50 % / 0,5 mm (A-05) |
| OFFEN-15 | Regenjacke ja (Logik-Datei), vorerst Platzhalter Kapuzenjacke. Matschhose nicht in der Logik → nein |
| OFFEN-16 | kein Schirm (nicht in der Logik) |
| OFFEN-17/18/22 | 0,2 cm oder 2 cm Decke; Schneeanzug; Schnee gewinnt auch über 0 °C (A-06) |
| OFFEN-19/20 | Böen 50 km/h (A-04); Glätte-Regel A-07 |
| OFFEN-21 | A-08 |
| OFFEN-30/31 | Zuordnung §12.3; Nacht nur für klar und teilweise (A-14) |
| OFFEN-32/45 | Platzhalter-Uhr und -Warnkreis (§12.4), Grafik später (O-3) |
| OFFEN-33/34 | Zubehör 32er Pixel-Art × 1,5; Wetter 24er Line × 2; Hinweise × 1,5 (§11.1) |
| OFFEN-35 | nur Linien (A-09) |
| OFFEN-36/37 | A-10, A-11 |
| OFFEN-40–44 | Inventar §12 |
| AC-15 „OFFEN“ | < 150 KB, nur mit Konvertierung erreichbar (§12.1) |

## 15. Akzeptanzkriterien

- **AC-1** Vom Homescreen geöffnet läuft die App im Vollbild ohne Safari-UI. Das Hochformat hält die Ausrichtungssperre.
- **AC-2** Mit `?lat&lon` oder über „Standort ermitteln“ wird der Standort gerundet gespeichert, die Parameter verschwinden aus der URL, und beim nächsten Start wird er ohne Parameter geladen.
- **AC-3** Ohne gespeicherten Standort erscheint der Setup-Screen.
- **AC-4** Die Empfehlung basiert auf der aktuellen plus den 3 folgenden Stunden: Momentanwerte `i…i+3`, Werte der vorangehenden Stunde `i+1…i+4`. Die Kleidung folgt `min(apparent_temperature)` im Fenster (Test mit Beispiel-Antwort).
- **AC-5** Für jedes Band in `RULES` zeigt `?debug&felt=<Wert im Band>` genau das Basis-Outfit dieses Bands.
- **AC-6** `?debug&felt=22&uv=3` zeigt Sonnencreme und Sonnenhut, mit `uv=8` zusätzlich die Sonnenbrille. `?debug&felt=3&uv=5` zeigt die Mütze (kein Sonnenhut) und die Sonnencreme.
- **AC-7** `?debug&felt=12&rain=80&rainsum=2` zeigt Regenjacke und Gummistiefel, mit zusätzlich `snow=1` Schneeanzug und Winterstiefel. `?debug&felt=3&rain=80&rainsum=2` behält Winterjacke und Winterstiefel.
- **AC-8** Es werden nie mehr als 3 Zubehör-Icons und nie mehr als 2 Hinweis-Icons angezeigt.
- **AC-9** Leere Slots verändern die Position der übrigen Slots nicht.
- **AC-10** Der Skalenpunkt liegt bei `felt=30` ganz oben und bei `felt=-5` ganz unten, dazwischen linear. Werte außerhalb werden begrenzt.
- **AC-11** Im Flugmodus zeigt die App nach vorherigem Laden den letzten Stand, mit dem Fenster neu relativ zur aktuellen Uhrzeit berechnet. Mit `?debug&age=180` erscheint das Uhr-Icon.
- **AC-12** `?test` prüft, dass jede in `RULES`, `WX`, Hinweisen und System referenzierte Icon-ID als `<symbol>` existiert.
- **AC-13** Pixel-Art-Icons erscheinen auf dem iPhone 8 ohne weiche Kanten, Line-Icons ohne ausgefranste Striche (Sichtprüfung).
- **AC-14** Nach dem Aufwecken werden die Daten neu geladen, ohne Nutzeraktion. Es gibt höchstens einen Abruf pro Aufwecken.
- **AC-15** `index.html` + `sw.js` + `manifest.json` sind zusammen < 150 KB (unkomprimiert).
- **AC-16** `?debug&felt=17&gust=55` zeigt die Kapuzenjacke und das Wind-Icon. `?debug&felt=27&gust=55` behält das T-Shirt und zeigt das Wind-Icon.
- **AC-17** `?debug&felt=-1&tmin=0&wet=0.5` zeigt das Glätte-Icon, ebenso `?debug&code=66`.
- **AC-18** Nach einem Deploy mit neuer `CACHE_VERSION` läuft spätestens nach dem zweiten Aufwecken die neue Version.
- **AC-19** `?test` meldet keine Fehler. Warnungen für Platzhalter sind erlaubt.

## 16. Tasks

| # | Task | Abhängig von |
|---|---|---|
| T1 | Repo anlegen, GitHub Pages aktivieren, Grundgerüst `index.html` (Head §4.1) / `manifest.json` / `sw.js`, Quell-SVGs nach `assets/` (Dateinamen ohne Leer- und Kopie-Suffix) | – |
| T2 | Geräte-Einrichtung §3.1. Standort Weg A und B im Homescreen-Kontext verifizieren, Geführten Zugriff testen | T1 |
| T3 | Open-Meteo-Abruf (Timeout), `aggregate()` → `Conditions` inkl. Index-Versatz und `null` | T1 |
| T4 | `RULES`, `WX` und reine Funktion `recommend()` | – |
| T5 | `?test`-Modus: Fälle für `recommend()`, `aggregate()` mit Beispiel-Antwort, Icon-Existenz | T3, T4, T7 |
| T6 | Layout-Raster mit festen Maßen, Slots, Wärmeskala mit Punkt | – |
| T7 | `tools/svg2symbol`, Sprite zusammenstellen, IDs nach §12, Platzhalter nach §12.4 | T1 |
| T7a | Später, blockiert nichts: fehlende Grafiken und die Kapuzenjacke ohne Kontur nachliefern, zuerst Handschuhe und Sonnencreme. Nur den Inhalt des Symbols tauschen, `data-placeholder` entfernen, `CACHE_VERSION` erhöhen | – |
| T8 | Wetterzeile: Icon-Mapping inkl. Nacht, Hinweise, Uhr | T3, T7 |
| T9 | Zustände (Setup inkl. Geolocation-Button, Laden, Veraltet, Fehler) und Caching | T3 |
| T10 | Aktualisierung (Aufwecken, 30 min, Entprellen) und SW-Update-Ablauf | T3 |
| T11 | Debug-Modus mit Overlay | T4 |
| T12 | Test auf dem Gerät: alle ACs. Danach eine Woche Alltagstest, Schwellen in `RULES` nachjustieren (P-17) | alles |

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
| Q22 | Bänder und Outfits kommen aus der Temperatur-Tabelle der Logik-Datei. Mehrdeutige Zellen sind als A-01…03 und A-15 entschieden. |
| Q23 | Sonnenschutz nach den UV-Stufen der Logik-Datei: ab 3 Creme und Hut, ab 8 Brille. Kein Schirm. |
| Q24 | Wind wirkt auf Kleidung (Kapuzenjacke, Logik-Datei) und als Hinweis-Icon. |
| Q25 | Gewitter ist kein Hinweis, das Wetter-Icon zeigt es bereits. |
| Q26 | Schnee gewinnt bei Oberteil und Schuhen, auch über 0 °C. Liegender Schnee zählt. |
| Q27 | Gecacht wird die Rohantwort. Das Fenster wird immer relativ zur aktuellen Uhrzeit neu berechnet, „veraltet“ heißt Abruf ≥ 3 h her (präzisiert Q15). |
| Q28 | Kleidung und Zubehör sind Pixel-Art (crisp), Wetter, Hinweise und System sind Line-Icons (weich). |
| Q29 | Setup zusätzlich per Geolocation-Button, Koordinaten auf 2 Nachkommastellen gerundet. |
| Q30 | Tests laufen im Browser per `?test`, ohne Test-Framework. |
| Q31 | Die Logik-Datei ist für Kleidungsregeln maßgeblich, die Spec für Gerät und Verhalten. Deren „Nächste Schritte“ (Auto-Lock aus, kein Homescreen) sind überholt. |
| Q32 | Zielsystem ist iOS 16. |
| Q33 | Das Line-Icon-Set ist für den persönlichen Gebrauch frei. Das reicht, auch im öffentlichen Repo. |
| Q34 | v1 startet mit Platzhaltern. Wo möglich verweisen sie auf ein passendes vorhandenes Icon (§12.4). |
| Q35 | Alle Entscheidungen A-01…A-15 sind bestätigt. |

## 18. Prüfbericht v0.1 → v1.0

Geprüft wurde v0.1 gegen die Logik-Datei, die 31 SVGs und die Open-Meteo-Dokumentation.

### 18.1 Assets

| # | Befund | Folge in v1.0 |
|---|---|---|
| P-01 | Das Inventar war veraltet: 19 Kleidungs-SVGs liegen vor, v0.1 kannte nur 5 Oberteile als fertig | §12 mit Datei → ID |
| P-02 | Es fehlen Regenjacke, Handschuhe, Sonnencreme sowie die Line-Icons für Nebel, Gewitter, Glätte, Uhr und Fehler | O-3, Platzhalter §12.4 |
| P-03 | Die Wetter-Icons sind 24er **Line-Icons** (schwarzer Strich, runde Enden), keine Pixel-Art. `crispEdges` und die Regel „ganzzahlige Pixel“ passen nicht | Regel geteilt (§11.1, Q28) |
| P-04 | `kapuzenjacke_pink` hat als einziges Icon eine dunkle Kontur (`#50232D`) und stammt aus einem anderen Export (Figma) | neu zeichnen (O-3) |
| P-05 | 477 KB roh: jede der 17 Dateien trägt 7,7 KB C2PA-Metadaten, dazu ein `<rect>` pro Pixel. AC-15 wäre ohne Konvertierung verfehlt | §12.1, gemessen ≈ 28 KB |
| P-06 | Zwei Exportformate (Rect-Gruppen mit `crispEdges` vs. Figma-Pfade ohne), Koordinaten im 640er Raster (20 Einheiten pro Kunstpixel) | Konvertierung normalisiert auf 32 × 32 |
| P-07 | Dateinamen mit Kopie-Suffix und Leerzeichen (`… 1.svg`, `… 2.svg`) | beim Umzug nach `assets/` bereinigen (T1) |
| P-08 | Pullover, Kapuzenpullover und Strickjacke sind in keinem Band das äußerste Teil und werden nie angezeigt, eine Folge von Q5. Pullover und Kapuzenpullover haben dieselbe Palette und unterscheiden sich nur durch die Kapuze | bewusst so. Icons bleiben als Alternativen im Sprite |
| P-09 | Unbenutzte Line-Icons: Schirm, Sonnenauf-/untergang, Thermometer, Funkeln | dokumentiert, nicht im Sprite nötig |
| P-10 | v0.1 verweist mehrfach auf einen Styleguide, der nicht im Ordner liegt | Werte abgeleitet (A-10, A-11) |

### 18.2 Abgleich mit der Logik-Datei

| # | Befund | Folge in v1.0 |
|---|---|---|
| P-11 | v0.1 gab die Sonnenbrille ab UV 3. Laut Logik gibt es sie erst ab UV 8 | korrigiert (§7.1) |
| P-12 | Der Schirm (OFFEN-16) steht nicht in der Logik-Datei | gestrichen |
| P-13 | Wind ist in der Logik eine Kleidungsregel („Kapuze/Windjacke“), in v0.1 nur ein Hinweis | beides (Q24) |
| P-14 | Die Regenjacke ersetzt laut Logik nur die „normale Jacke“. Offen war, was ohne Jacke gilt und was mit Winterjacke | `topInBands`, `shoesInBands` (A-05) |
| P-15 | Mehrdeutige Tabellenzellen: „kurze/lange Hose“, „Longsleeve oder T-Shirt mit Strickjacke“, „normale Jacke“, „Thermohose“, „dicke Handschuhe“ | A-01…03. Thermohose und dicke Handschuhe haben keine eigenen Icons |
| P-16 | Die Logik-Datei will Auto-Lock aus, keinen Homescreen und 1–3 Screens, die Spec normale Auto-Sperre, eine Homescreen-Web-App und 1 Screen | die Spec gilt (Q31) |
| P-17 | Die Logik-Tabelle sagt nur „Temperatur“. Die Spec nimmt die **gefühlte Minimaltemperatur** (Q10, Q11) und ist damit doppelt konservativ. Beispiel: Luft 3 °C bei Wind ergibt gefühlt −1 °C und damit schon den Schneeanzug | bewusst beibehalten. Nachjustieren in T12 |
| P-18 | Lichtschutzfaktor-Stufen und „Mittagssonne meiden“ lassen sich ohne Text nicht darstellen | Out of Scope (§2) |

### 18.3 Technik und Spec-intern

| # | Befund | Folge in v1.0 |
|---|---|---|
| P-19 | Niederschlag, Wahrscheinlichkeit, Schneefall und Böen gelten bei Open-Meteo für die **vorangehende** Stunde. v0.1 hätte bei ihnen die falschen 4 Stunden aggregiert | Index-Versatz (§6) |
| P-20 | `current.apparent_temperature` und `current.weather_code` wurden abgefragt, aber nie benutzt. Die Stundensuche per Zeit-String ist fehleranfällig | entfernt. `timeformat=unixtime` |
| P-21 | Gewitter erschien doppelt (Wetter-Icon und Hinweis), gegen die eigene Regel „jedes Icon hat genau einen Ort“ | Q25 |
| P-22 | Die Veraltet-Regel trug nicht: Die Daten reichen bis Ende morgen, und eine eingefrorene Empfehlung zeigt vergangene Stunden | Q27 |
| P-23 | Ein SW-Update wird beim Aufwecken nicht aktiv (keine Navigation). Cache-Treffer scheitern an Query-Parametern | `registration.update()`, Reload, `ignoreSearch` (§4.2) |
| P-24 | Eine `start_url` im Manifest würde die Setup-Parameter verwerfen. iOS kennt keine Ausrichtungssperre per Manifest | §4.1, §3 |
| P-25 | `~`-Maße und flexible Zeilen ergeben halbe Gerätepixel (559 / 4 = 139,75 pt), das macht Pixel-Art unscharf. Das Verhalten der Statusleiste war unklar | feste Maße (§11.1) |
| P-26 | AC-7 war mit Regen als UND-Regel nicht eindeutig. Unklare Debug-Defaults ließen Live-Werte in Tests einfließen. Es fehlten Parameter für `tempMin`, Schneedecke und Nacht | §13.1, AC-7 |
| P-27 | T5 hatte keinen Ort: Die Logik liegt in `index.html`, und es gibt keinen Build | `?test` (§13.2) |
| P-28 | Doppelte Abrufe beim Aufwecken, kein Timeout, `null`-Werte der API unbehandelt | §5, §6, §10 |
| P-29 | Aufwecken führt auf dem iPhone 8 zum Sperrbildschirm (zweiter Druck nötig). Home in der App führt zum Homescreen, und 30 s Auto-Sperre sind zu kurz | §3.1 |
| P-30 | Keine Funktion von v1 braucht den Jailbreak | §3 |
