// Übersichtsseite (?overview): alle Zustände und Icons zum Durchsehen (Spec §13.3).
// Wird nur bei ?overview von index.html nachgeladen. Nutzt die Globals der App (RULES, WX, recommend, viewBoxOf, svgEl, …).
const OVERVIEW_CSS = `
/* ===== Übersicht (?overview): Seite zum Durchsehen aller Zustände und Icons ===== */
html.overview, html.overview body { position: static; overflow: auto; height: auto; display: block; touch-action: auto; -webkit-user-select: text; user-select: text; background: #f3efe7; }
html.overview #app { display: none; }
#overview { --s: 0.6; font: 14px/1.45 -apple-system, system-ui, sans-serif; color: var(--ink); max-width: 1500px; margin: 0 auto; padding: 16px 20px 80px; }
#overview h1 { font-size: 24px; margin: 8px 0 4px; }
#overview h2 { font-size: 19px; margin: 40px 0 6px; padding-top: 12px; border-top: 2px solid var(--ink-soft); }
#overview h3 { font-size: 15px; margin: 22px 0 8px; padding: 4px 10px; border-radius: 6px; display: inline-block; }
#overview p.note { margin: 2px 0 10px; color: #6b635b; max-width: 820px; }
#overview .bar { position: sticky; top: 0; z-index: 5; background: #f3efe7; padding: 8px 0; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; border-bottom: 1px solid var(--ink-soft); }
#overview .bar a { color: var(--ink); }
#overview table { border-collapse: collapse; background: #fff; font-size: 13px; }
#overview th, #overview td { border: 1px solid #ddd5c8; padding: 5px 9px; text-align: left; vertical-align: top; }
#overview th { background: #ebe5d8; }
#overview .cards { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-start; }
#overview .card { background: #fff; border: 1px solid #ddd5c8; border-radius: 8px; padding: 8px; width: calc(375px * var(--s) + 16px); font-size: 12px; }
#overview .card b { font-size: 13px; }
#overview .card .id { font: 11px ui-monospace, monospace; color: #6b635b; }
#overview .card .alt { color: #6b635b; }
#overview .shot { display: block; position: relative; width: calc(375px * var(--s)); height: calc(667px * var(--s)); overflow: hidden; margin: 6px 0; border: 1px solid #ddd5c8; }
#overview .shot iframe { position: absolute; left: 0; top: 0; width: 375px; height: 667px; border: 0; transform: scale(var(--s)); transform-origin: 0 0; pointer-events: none; }
#overview .chip { display: inline-block; background: #ebe5d8; border-radius: 10px; padding: 0 7px; margin: 0 3px 3px 0; }
#overview .icons { display: flex; flex-wrap: wrap; gap: 12px; }
#overview .icon { background: var(--bg); border: 1px solid #ddd5c8; border-radius: 8px; padding: 10px; width: 190px; min-height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; gap: 6px; text-align: center; font-size: 12px; }
#overview .icon .art { display: flex; align-items: flex-end; justify-content: center; flex: 1; }
#overview .icon .unused { color: #b0472f; }
#overview .wxrow { display: flex; gap: 10px; align-items: center; }
`;

// ===== Übersicht (?overview): alle Zustände und Icons zum Durchsehen =====
// Nutzt RULES und recommend() direkt, jede Karte ist die echte App (?debug&bare) im Miniformat.
function runOverview() {
  const style = document.createElement('style');
  style.textContent = OVERVIEW_CSS;
  document.head.appendChild(style);
  document.documentElement.classList.add('overview');
  showScreen(null);

  const h = (tag, attrs, ...kids) => {
    const el = document.createElement(tag);
    Object.keys(attrs || {}).forEach((k) => {
      if (k === 'class') el.className = attrs[k]; else if (k === 'style') el.style.cssText = attrs[k]; else el.setAttribute(k, attrs[k]);
    });
    kids.flat().filter((k) => k !== null && k !== undefined && k !== false).forEach((k) => el.append(k));
    return el;
  };
  const short = (id) => id.replace(/^i-[a-z]+-/, '');
  const iconSvg = (id, px) => {
    const vb = viewBoxOf(id);
    const svg = svgEl('svg', { width: vb[2] * px, height: vb[3] * px });
    svgEl('use', { href: `#${id}` }, svg);
    return svg;
  };
  const root = h('div', { id: 'overview' });
  document.body.appendChild(root);

  // --- Kopf mit Zoom ---
  const startZoom = Math.min(1, Math.max(0.35, Number(new URLSearchParams(location.search).get('s')) || 0.6));
  const slider = h('input', { type: 'range', min: '0.35', max: '1', step: '0.05', value: String(startZoom) });
  root.style.setProperty('--s', startZoom);
  slider.addEventListener('input', () => root.style.setProperty('--s', slider.value));
  root.append(
    h('h1', {}, 'Kleidungs-Kiosk: alle Zustände'),
    h('p', { class: 'note' }, 'Jede Karte ist der echte Bildschirm der App. Die Kennung (z. B. ', h('span', { class: 'id' }, 'kuehl-3'), ') kannst du für Kommentare nutzen. Ein Klick auf das Bild öffnet es in voller Größe.'),
    h('div', { class: 'bar' }, h('b', {}, 'Größe'), slider,
      h('a', { href: '#regeln' }, 'Regeln'), h('a', { href: '#baender' }, 'Wärmebänder'), h('a', { href: '#drinnen' }, 'Drinnen'), h('a', { href: '#farben' }, 'Farbvarianten'), h('a', { href: '#varianten' }, 'Wetter-Varianten'), h('a', { href: '#sonder' }, 'Sonderfälle'),
      h('a', { href: '#katalog' }, 'Icon-Katalog'), h('a', { href: '#wetter' }, 'Wetter-Icons'), h('a', { href: '#system' }, 'Sonderzustände')),
  );

  // Die Karten zeigen die Hauptfarben (v=1), damit die Übersicht stabil bleibt. Farbvarianten: eigener Abschnitt.
  const shot = (query, label) => {
    const q = /(^|&)v=/.test(query) ? query : `${query}&v=1`;
    return h('a', { class: 'shot', href: `?debug&${q}`, target: '_blank', title: label },
      h('iframe', { src: `?debug&bare&${q}`, loading: 'lazy', tabindex: '-1', title: label }));
  };

  // --- Regeln als Tabellen ---
  const bands = RULES.bands;
  const bandRange = (b, i) => (i === 0 ? `ab ${b.min} °C` : (b.min === -Infinity ? `unter ${bands[i - 1].min} °C` : `${b.min} bis unter ${bands[i - 1].min} °C`));
  const names = (list) => (list.length ? list.map(short).join(', ') : '–');
  const rulesTable = h('table', {},
    h('tr', {}, ['Band', 'gefühlte Temperatur', 'Kopf', 'Oberteil', 'Hose', 'Schuhe', 'Zubehör', 'Sonnenschutz ab UV', 'drinnen: Oberteil', 'drinnen: Hose'].map((t) => h('th', {}, t))),
    bands.map((b, i) => h('tr', {}, h('td', {}, h('b', {}, b.id)), h('td', {}, bandRange(b, i)), h('td', {}, b.head || '–'), h('td', {}, b.top),
      h('td', {}, b.bottom), h('td', {}, b.shoes), h('td', {}, names(b.acc)), h('td', {}, String(b.uvMin ?? RULES.sun.uvMin)), h('td', {}, [].concat(b.in.top).join(' oder ')), h('td', {}, b.in.bottom))));
  const R = RULES;
  const overrideTable = h('table', {},
    h('tr', {}, ['Regel', 'Auslöser', 'Wirkung', 'gilt in Bändern']. map((t) => h('th', {}, t))),
    h('tr', {}, h('td', {}, 'Sonne'), h('td', {}, `UV-Index ≥ ${R.sun.uvMin}, in ${bands.filter((b) => b.uvMin).map((b) => `${b.id} erst ≥ ${b.uvMin}`).join(', ')}`), h('td', {}, `Sonnencreme; Kopf = ${R.sun.head}, falls das Band keinen Kopf setzt (Mütze gewinnt)`), h('td', {}, 'alle')),
    h('tr', {}, h('td', {}, 'Sonnenbrille'), h('td', {}, `UV-Index ≥ ${R.sun.uvGlasses}`), h('td', {}, 'zusätzlich Sonnenbrille'), h('td', {}, 'alle')),
    h('tr', {}, h('td', {}, 'Wind'), h('td', {}, `Böen ≥ ${R.wind.gustMin} km/h`), h('td', {}, `Oberteil = ${R.wind.top}; Wind-Hinweis immer. Regen und Schnee schlagen die Windjacke.`), h('td', {}, R.wind.topInBands.join(', ') + ' (Hinweis in allen)')),
    h('tr', {}, h('td', {}, 'Regen'), h('td', {}, `Regenwahrsch. ≥ ${R.rain.probMin} % UND ≥ ${R.rain.sumMin} mm in 4 h`), h('td', {}, `Oberteil = ${R.rain.top}, Hose = ${R.rain.bottom}, Schuhe = ${R.rain.shoes}`),
      h('td', {}, `Jacke: ${R.rain.topInBands.join(', ')}; Hose: ${R.rain.bottomInBands.join(', ')}; Schuhe: ${R.rain.shoesInBands.join(', ')}`)),
    h('tr', {}, h('td', {}, 'Schnee'), h('td', {}, `Neuschnee ≥ ${R.snow.sumMin} cm in 4 h ODER liegend ≥ ${R.snow.depthMin} cm`), h('td', {}, `Oberteil = ${R.snow.top}, Hose = ${R.snow.bottom}, Schuhe = ${R.snow.shoes} (schlägt Regen und Wind)`), h('td', {}, `Jacke und Hose: ${R.snow.topInBands.join(', ')}; Schuhe: ${R.snow.shoesInBands.join(', ')}; wärmer wird Schnee ignoriert`)),
    h('tr', {}, h('td', {}, 'Drinnen'), h('td', {}, 'Umschalter links im Bild (Haus / Baum)'), h('td', {}, 'Grundkleidung des Bandes (Spalten „drinnen“), ohne Kopf, Schuhe, Zubehör und ohne Wetter-Overrides. Springt nach 60 s und beim Aufwecken zurück auf draußen.'), h('td', {}, 'alle')),
    h('tr', {}, h('td', {}, 'Farbvarianten'), h('td', {}, 'jeder Tag neu'), h('td', {}, 'Jedes Teil hat eine Hauptfarbe und weitere Farben (-v2, -v3). Je Teil und Tag wählt die App eine, gleicher Tag = gleiches Bild.'), h('td', {}, 'alle')),
    h('tr', {}, h('td', {}, 'Glätte-Hinweis'), h('td', {}, `niedrigste Lufttemp. (nächste 4 h) ≤ ${R.ice.tempMax} °C UND nass (≥ ${R.ice.wetMin} mm Niederschlag in den nächsten 4 h oder in den letzten ~6 h), oder gefrierender Regen/Niesel (Wettercode 56, 57, 66, 67) bei jeder Temperatur`), h('td', {}, 'Hinweis-Symbol, keine Kleidungsänderung'), h('td', {}, 'alle')),
    h('tr', {}, h('td', {}, 'Grenzen'), h('td', {}, `max. ${R.maxAccessories} Zubehör, max. ${R.maxHints} Hinweise`), h('td', {}, `Zubehör-Reihenfolge (was zuerst bleibt): ${R.accessoryOrder.join(' › ')}. Folge: In eisig und frost fällt bei UV ≥ ${R.sun.uvGlasses} die Sonnenbrille weg.`), h('td', {}, '–')));
  root.append(
    h('h2', { id: 'regeln' }, 'Regeln'),
    h('p', { class: 'note' }, 'Direkt aus RULES in der App erzeugt. Bandgrenzen gelten für die gefühlte Temperatur (niedrigster Wert der nächsten 4 Stunden), untere Grenze inklusive.'),
    rulesTable, h('p', {}), overrideTable);

  // --- Wärmebänder ---
  const bandRep = (i) => {
    const b = bands[i];
    if (i === 0) return b.min + 2;
    const upper = bands[i - 1].min;
    return b.min === -Infinity ? upper - 3 : Math.floor((b.min + upper) / 2);
  };
  root.append(h('h2', { id: 'baender' }, 'Wärmebänder (trocken, kein UV, kein Wind)'),
    h('p', { class: 'note' }, 'Das Grundbild je Band. Die Temperatur im Thermometer ist ein Beispielwert aus der Mitte des Bandes.'));
  const bandCards = h('div', { class: 'cards' });
  bands.forEach((b, i) => {
    const t = bandRep(i);
    bandCards.append(h('div', { class: 'card' }, h('b', {}, b.id), ' ', h('span', { class: 'id' }, bandRange(b, i)), shot(`felt=${t}`, b.id)));
  });
  root.append(bandCards);

  // --- Drinnen: Grundkleidung je Band ---
  root.append(h('h2', { id: 'drinnen' }, 'Drinnen (Umschalter „Haus“)'),
    h('p', { class: 'note' }, 'Was das Kind im Haus anhat: Grundkleidung des Bandes, ohne Jacke, Mütze, Schuhe, Zubehör. Wetter ändert daran nichts.'));
  const inCards = h('div', { class: 'cards' });
  bands.forEach((b, i) => {
    inCards.append(h('div', { class: 'card' }, h('b', {}, `${b.id} drinnen`), ' ', h('span', { class: 'id' }, `${[].concat(b.in.top).join(' / ')} + ${b.in.bottom}`), shot(`felt=${bandRep(i)}&view=in`, `${b.id} drinnen`)));
  });
  root.append(inCards);

  // --- Farbvarianten ---
  const variantRows = [...new Set([...document.querySelectorAll('symbol')].map((sy) => sy.id.match(/-v(\d+)$/)).filter(Boolean).map((m) => Number(m[1])))].sort();
  root.append(h('h2', { id: 'farben' }, 'Farbvarianten'),
    h('p', { class: 'note' }, 'Die Bänder oben zeigen die Hauptfarben (v1). Hier dieselben Bänder mit Variante 2, 3 … überall, wo ein Teil so viele hat (sonst bleibt die Hauptfarbe). Im Alltag wählt die App je Teil und Tag zufällig eine Farbe, und zwei Nachbarn (z. B. Jacke und Hose) bekommen nie dieselbe Farbfamilie. Hier ist die Variante erzwungen, deshalb können auch Paare vorkommen, die im Alltag ausgeschlossen sind (Marine auf Marine). Alle Varianten einzeln: Icon-Katalog.'));
  variantRows.forEach((n) => {
    const row = h('div', { class: 'cards' });
    bands.forEach((b, i) => row.append(h('div', { class: 'card' }, h('b', {}, `${b.id} · Variante ${n}`), shot(`felt=${bandRep(i)}&v=${n}`, `${b.id} Variante ${n}`))));
    root.append(h('h3', { style: 'background:#ebe5d8' }, `Variante ${n}`), row);
  });

  // --- Varianten: alle Kombinationen, doppelte Ergebnisse zusammengefasst ---
  const SNOW_MAX_FELT = 14;   // Schnee nur dort durchspielen, wo er physikalisch vorkommt
  const groups = bands.map(() => new Map());
  bands.forEach((b, bi) => {
    const lowest = b.min === -Infinity ? bandRep(bi) : b.min;
    const iceOk = lowest <= R.ice.tempMax;
    const uvLevels = [0, b.uvMin ?? R.sun.uvMin, R.sun.uvGlasses];   // niedrig / Sonnenschutz des Bandes / Brille
    const combos = [];
    for (let rain = 0; rain < 2; rain++) for (let snow = 0; snow < 2; snow++) for (let gust = 0; gust < 2; gust++) for (let uv = 0; uv < 3; uv++) for (let wet = 0; wet < 2; wet++) {
      if (snow && bandRep(bi) > SNOW_MAX_FELT) continue;
      if (wet && !iceOk) continue;
      combos.push({ rain, snow, gust, uv, wet });
    }
    combos.sort((a, c) => (a.rain + a.snow + a.gust + a.uv + a.wet) - (c.rain + c.snow + c.gust + c.uv + c.wet));
    combos.forEach((k) => {
      const felt = k.wet ? lowest : bandRep(bi);
      const cond = {
        tempDisplay: felt, feltMin: felt, tempMin: felt,
        rainProbMax: k.rain ? 80 : 0, rainSum: k.rain ? 2 : 0, wetBefore: k.wet ? 0.5 : 0,
        snowSum: k.snow ? 1 : 0, snowDepth: 0, uvMax: uvLevels[k.uv],
        gustMax: k.gust ? R.wind.gustMin + 10 : 0, code: k.snow ? 73 : (k.rain ? 61 : 0), isDay: true,
      };
      const o = recommend(cond, RULES, WX);
      const key = [o.head, o.top, o.bottom, o.shoes, o.accessories.join(), o.hints.join(), o.weatherIcon].join('|');
      const parts = [k.wet && 'nasser Boden', k.rain && 'Regen', k.snow && 'Schnee', k.gust && `Wind ≥ ${R.wind.gustMin}`,
        k.uv === 1 && `UV ≥ ${uvLevels[1]}`, k.uv === 2 && `UV ≥ ${uvLevels[2]}`].filter(Boolean);
      const label = parts.length ? parts.join(' + ') : 'trocken, ruhig';
      const query = new URLSearchParams({ felt, tmin: felt, rain: cond.rainProbMax, rainsum: cond.rainSum, wet: cond.wetBefore, snow: cond.snowSum, uv: cond.uvMax, gust: cond.gustMax, code: cond.code }).toString();
      if (groups[bi].has(key)) groups[bi].get(key).alt.push(label);
      else groups[bi].set(key, { label, o, query, alt: [] });
    });
  });
  let total = 0;
  root.append(h('h2', { id: 'varianten' }, 'Wetter-Varianten je Band'),
    h('p', { class: 'note' }, `Alle Kombinationen aus Regen, Schnee, Wind, UV (niedrig / Sonnenschutz des Bandes / ab ${R.sun.uvGlasses}) und Glätte, durch die echte Logik gerechnet. Kombinationen mit gleichem Ergebnis sind zu einer Karte zusammengefasst („gleich bei …“). Schnee wird nur in Bändern bis ${SNOW_MAX_FELT} °C durchgespielt (wärmer wird er ignoriert, A-23), nasser Boden nur dort, wo Frost möglich ist.`));
  bands.forEach((b, bi) => {
    const look = bandLook(bi);
    const cards = h('div', { class: 'cards' });
    let n = 0;
    groups[bi].forEach((g) => {
      n++; total++;
      const o = g.o;
      cards.append(h('div', { class: 'card' },
        h('b', {}, g.label), ' ', h('span', { class: 'id' }, `${b.id}-${n}`),
        shot(g.query, `${b.id}-${n}`),
        h('div', {}, [o.head, o.top, o.bottom, o.shoes, ...o.accessories, ...o.hints].filter(Boolean).map((id) => h('span', { class: 'chip' }, short(id)))),
        g.alt.length ? h('div', { class: 'alt', title: g.alt.join('\n') }, `gleich bei: ${g.alt.slice(0, 3).join('; ')}${g.alt.length > 3 ? ` (+${g.alt.length - 3} weitere)` : ''}`) : null));
    });
    root.append(h('h3', { style: `background:${look.tint};border:1px solid ${look.liquid}` }, `${b.id} · ${bandRange(b, bi)} · ${n} Varianten`), cards);
  });

  // --- Sonderfälle, die die Kombinationen oben nicht erreichen ---
  const specials = h('div', { class: 'cards' });
  [['felt=12&tmin=12&rain=80&rainsum=2&code=66', 'Gefrierender Regen bei 12 °C: Glätte-Hinweis trotz Plusgrad'],
    ['felt=7&tmin=0&wet=0.5&code=0', 'Kalter Morgen: gefühlt 7 °C, Luft 0 °C, Boden nass → Glätte'],
    ['felt=12&tmin=12&depth=3', 'Tauwetter in kühl: 3 cm Schnee liegen → Winterstiefel, Jacke bleibt'],
    ['felt=7&tmin=6&depth=3', 'Tauwetter in kalt: 3 cm Schnee liegen → Winterstiefel, Jacke bleibt'],
    ['felt=17&tmin=16&depth=5', 'Schnee „liegt“ bei 17 °C (Datenfehler): ohne Wirkung'],
    ['felt=3&tmin=2&rain=80&rainsum=2', 'Regen in eisig: Winterjacke, Matschhose, Winterstiefel'],
    ['felt=22&code=45', 'Nebel (Wettercode 45)'], ['felt=22&code=95', 'Gewitter (Wettercode 95)'],
    ['felt=22&code=51', 'Nieselregen (Wettercode 51, zu wenig für Regenjacke)'], ['felt=22&night=1', 'Nacht (klar)']]
    .forEach(([q, label]) => specials.append(h('div', { class: 'card' }, h('b', {}, label), shot(q, label))));
  root.append(h('h2', { id: 'sonder' }, 'Sonderfälle'),
    h('p', { class: 'note' }, 'Zustände, die in den Kombinationen oben nicht vorkommen: Luft- und gefühlte Temperatur weichen voneinander ab, gefrierender Regen, weitere Wettercodes, Nacht.'), specials);

  // --- Icon-Katalog ---
  const usage = new Map();
  const add = (id, tag) => { if (!id) return; if (!usage.has(id)) usage.set(id, []); const l = usage.get(id); if (!l.includes(tag)) l.push(tag); };
  bands.forEach((b) => {
    if (b.head) add(`i-head-${b.head}`, b.id);
    add(`i-top-${b.top}`, b.id); add(`i-bottom-${b.bottom}`, b.id); add(`i-shoes-${b.shoes}`, b.id);
    b.acc.forEach((a) => add(`i-acc-${a}`, b.id));
  });
  add(`i-head-${R.sun.head}`, 'UV'); add('i-acc-sonnencreme', 'UV'); add('i-acc-sonnenbrille', 'UV hoch');
  add(`i-top-${R.wind.top}`, 'Wind'); add('i-hint-wind', 'Wind');
  add(`i-top-${R.rain.top}`, 'Regen'); add(`i-bottom-${R.rain.bottom}`, 'Regen'); add(`i-shoes-${R.rain.shoes}`, 'Regen');
  add(`i-top-${R.snow.top}`, 'Schnee'); add(`i-bottom-${R.snow.bottom}`, 'Schnee'); add(`i-shoes-${R.snow.shoes}`, 'Schnee');
  bands.forEach((b) => { [].concat(b.in.top).forEach((t) => add(`i-top-${t}`, `${b.id} drinnen`)); add(`i-bottom-${b.in.bottom}`, `${b.id} drinnen`); });
  add('i-ui-innen', 'Umschalter'); add('i-ui-aussen', 'Umschalter');
  add('i-hint-glaette', 'Glätte');
  WX.codeGroups.forEach((g) => { add(`i-wx-${g.icon}`, 'Wetter'); add(`i-wx-${g.iconNight}`, 'Wetter'); });
  add('i-sys-uhr', 'Daten alt'); add('i-sys-fehler', 'Fehler'); add('i-ui-flocke', 'Thermometer');

  const kinds = [['head', 'Kopf'], ['top', 'Oberteile'], ['bottom', 'Hosen'], ['shoes', 'Schuhe'], ['acc', 'Zubehör'], ['hint', 'Hinweise'], ['wx', 'Wetter'], ['sys', 'System'], ['ui', 'Sonstiges']];
  root.append(h('h2', { id: 'katalog' }, 'Icon-Katalog'),
    h('p', { class: 'note' }, 'Alle Symbole der App in Anzeigegröße. Rot markiert: Das Symbol existiert, wird von keiner Regel verwendet.'));
  const allIds = [...document.querySelectorAll('symbol')].map((s) => s.id);
  kinds.forEach(([kind, title]) => {
    const ids = allIds.filter((id) => id.startsWith(`i-${kind}-`));
    if (!ids.length) return;
    const row = h('div', { class: 'icons' });
    ids.forEach((id) => {
      const px = kind === 'wx' || kind === 'hint' || kind === 'sys' ? 3 : (kind === 'acc' ? PX_EXTRAS : PX_CLOTHES);
      const isVariant = /-v\d+$/.test(id);
      const baseId = isVariant ? id.replace(/-v\d+$/, '') : id;
      const used = usage.get(baseId);
      const weights = VARIANT_WEIGHTS[baseId] || [];
      const reserve = isVariant && weights[Number(id.match(/-v(\d+)$/)[1]) - 1] === 0;
      row.append(h('div', { class: 'icon' }, h('div', { class: 'art' }, iconSvg(id, kind === 'ui' ? 3 : px)), h('b', {}, short(id)),
        h('div', { class: used ? '' : 'unused' }, reserve ? 'Reserve: wird nicht gezeigt' : (used ? `${isVariant ? 'Farbvariante: ' : ''}${used.join(', ')}` : 'von keiner Regel verwendet'))));
    });
    root.append(h('h3', { style: 'background:#ebe5d8' }, title), row);
  });

  // --- Wetter-Icons ---
  const wxNames = { klar: 'klar', teilweise: 'teils bewölkt', bedeckt: 'bedeckt', nebel: 'Nebel', niesel: 'Nieselregen', regen: 'Regen / Schauer', schnee: 'Schnee', gewitter: 'Gewitter' };
  const wxTable = h('table', {}, h('tr', {}, ['Wetter', 'Tag', 'Nacht', 'Wettercodes (Open-Meteo)'].map((t) => h('th', {}, t))),
    WX.codeGroups.map((g) => h('tr', {}, h('td', {}, wxNames[g.icon] || g.icon),
      h('td', {}, iconSvg(`i-wx-${g.icon}`, 3)), h('td', {}, iconSvg(`i-wx-${g.iconNight}`, 3)), h('td', {}, g.codes.join(', ')))));
  root.append(h('h2', { id: 'wetter' }, 'Wetter-Icons'),
    h('p', { class: 'note' }, 'Bei mehreren Codes im 4-Stunden-Fenster gewinnt der schwerere (Reihenfolge wie in der Tabelle, unten = schwerer). Unbekannte Codes zeigen „bedeckt“.'), wxTable);

  // --- Sonderzustände ---
  const sys = h('div', { class: 'cards' });
  [['state=loading', 'Lädt (erster Abruf)'], ['state=error', 'Fehler (keine Daten)'], ['felt=15&age=200', 'Daten veraltet (≥ 180 min, Uhr neben dem Wetter)'], ['state=setup', 'Kein Standort']]
    .forEach(([q, label]) => sys.append(h('div', { class: 'card' }, h('b', {}, label), shot(q, label))));
  root.append(h('h2', { id: 'system' }, 'Sonderzustände'), sys,
    h('p', { class: 'note' }, `${total} Wetter-Varianten insgesamt.`));
}
