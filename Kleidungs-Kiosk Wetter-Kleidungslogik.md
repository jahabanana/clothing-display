# Kleidungs-Kiosk: Wetter-Kleidungslogik

2026-09-17 · @Someone

## Ziel & Kontext

Ein altes iPhone wird zu einem jailbroken Single-Purpose-Kiosk umgebaut: kein Homescreen, maximal 1–3 Screens. Nach dem Aufwecken zeigt das Gerät automatisch:

- die aktuelle Temperatur (klein, ggf. als Thermometer-Icon)
- das Wetter (Sonne, Wolken, Regen etc.)
- eine Kleidungsempfehlung

Zielgruppe: ein Kind (kein Baby), das sich damit selbstständig wettergerecht anziehen kann.

## Temperatur-Tabelle

| Temperatur | Oberteil | Hose | Jacke | Kopf & Hände | Schuhe |
| --- | --- | --- | --- | --- | --- |
| ab 25°C | T-Shirt | kurze Hose | – | – | Sandalen |
| 20–24°C | T-Shirt | kurze/lange Hose | – | – | Sneaker |
| 15–19°C | Longsleeve oder T-Shirt mit Strickjacke | lange Hose | – | – | Sneaker |
| 10–14°C | Pullover | lange Hose | normale Jacke | – | Sneaker |
| 5–9°C | Pullover | lange Hose | Winterjacke | Mütze, Handschuhe | Sneaker |
| 0–4°C | Pullover | lange Hose | Winterjacke | Mütze, Schal, Handschuhe | Winterstiefel |
| unter 0°C | Pullover | lange Hose (Thermo) | Schneeanzug | Mütze, Schal, dicke Handschuhe | Winterstiefel |

Schuhwerk ist bewusst auf die vier vorhandenen Paare beschränkt: Sandalen, Sneaker, Gummistiefel, Winterstiefel.

## UV-Index: Sonnenschutz

Sonnenschutz ist unabhängig von Temperatur und Sonnenschein – ausschließlich an den UV-Index gekoppelt.

| UV-Index | Maßnahme |
| --- | --- |
| 0–2 (niedrig) | kein Schutz nötig |
| 3–5 (moderat) | Sonnencreme LSF 30+, Sonnenhut |
| 6–7 (hoch) | Sonnencreme LSF 50, Sonnenhut, Mittagssonne (11–15 Uhr) meiden |
| 8+ (sehr hoch/extrem) | Sonnencreme LSF 50+, Sonnenhut, Sonnenbrille, möglichst Schatten/drinnen |

## Wetter-Overrides

Überschreiben Jacke und/oder Schuhe aus der Temperatur-Tabelle:

| Wetter | Override |
| --- | --- |
| Regen | Regenjacke statt normaler Jacke, Gummistiefel statt Basis-Schuh |
| Schnee | Schneeanzug statt normaler Jacke, Winterstiefel (erzwungen) |
| starker Wind | zusätzlich Kapuze/Windjacke, unabhängig von Temperatur |

## Nächste Schritte

1. Web-App-Logik bauen: Temperatur → Basis-Set, UV-Index → Sonnenschutz-Flag, Regen/Schnee → Override von Jacke + Schuhen, Wind → additiver Hinweis
2. Wetterdaten-Anbindung (z. B. Open-Meteo, kein API-Key nötig)
3. Jailbreak-Setup auf dem iPhone (palera1n oder Dopamine, je nach Modell/iOS-Version)
4. Kiosk-Verhalten einrichten: Homescreen ausblenden, Auto-Boot in die App, Auto-Lock aus
