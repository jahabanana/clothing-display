// Testmodus (?test): läuft in der Seite selbst, ohne Framework (Spec §13.2).
// Wird nur bei ?test von index.html nachgeladen. Nutzt die Globals der App (RULES, WX, recommend, aggregate, els, …).
function runTests() {
  showScreen(null);
  setHidden(els.testOutput, false);

  const lines = [];
  let passCount = 0; let failCount = 0; let warnCount = 0;
  function assertEq(actual, expected, msg) {
    if (actual !== expected) {
      throw new Error(`${msg || ''} erwartet ${JSON.stringify(expected)}, war ${JSON.stringify(actual)}`);
    }
  }
  function assertTrue(v, msg) { if (!v) throw new Error(msg || 'erwartet true'); }
  function test(name, fn) {
    try { fn(); passCount++; lines.push(`PASS ${name}`); } catch (e) { failCount++; lines.push(`FAIL ${name} - ${e.message}`); }
  }
  function cond(overrides) {
    return Object.assign({
      tempDisplay: 15, feltMin: 15, tempMin: 15,
      rainProbMax: 0, rainSum: 0, wetBefore: 0,
      snowSum: 0, snowDepth: 0,
      uvMax: 0, gustMax: 0,
      code: 0, isDay: true,
    }, overrides);
  }

  RULES.bands.forEach((band) => {
    test(`Band ${band.id} liefert Basis-Outfit`, () => {
      const felt = band.min === -Infinity ? -50 : band.min;
      const o = recommend(cond({ feltMin: felt }), RULES, WX);
      assertEq(o.band, band.id);
      assertEq(o.top, `i-top-${band.top}`);
      assertEq(o.bottom, `i-bottom-${band.bottom}`);
      assertEq(o.shoes, `i-shoes-${band.shoes}`);
      assertEq(o.head, band.head ? `i-head-${band.head}` : null);
    });
  });

  test('Bandgrenze 24.9 -> warm', () => assertEq(recommend(cond({ feltMin: 24.9 }), RULES, WX).band, 'warm'));
  test('Bandgrenze 25.0 -> heiss', () => assertEq(recommend(cond({ feltMin: 25.0 }), RULES, WX).band, 'heiss'));
  test('Bandgrenze 19.9 -> mild', () => assertEq(recommend(cond({ feltMin: 19.9 }), RULES, WX).band, 'mild'));
  test('Bandgrenze -0.1 -> frost', () => assertEq(recommend(cond({ feltMin: -0.1 }), RULES, WX).band, 'frost'));
  test('Bandgrenze 0.0 -> eisig', () => assertEq(recommend(cond({ feltMin: 0.0 }), RULES, WX).band, 'eisig'));

  test('AC-6 felt=22 uv=3', () => {
    const o = recommend(cond({ feltMin: 22, uvMax: 3 }), RULES, WX);
    assertTrue(o.accessories.includes('i-acc-sonnencreme'));
    assertEq(o.head, 'i-head-sonnenhut');
    assertTrue(!o.accessories.includes('i-acc-sonnenbrille'));
  });
  test('AC-6 felt=22 uv=8', () => {
    const o = recommend(cond({ feltMin: 22, uvMax: 8 }), RULES, WX);
    assertTrue(o.accessories.includes('i-acc-sonnenbrille'));
  });
  test('AC-6 felt=3 uv=5', () => {
    const o = recommend(cond({ feltMin: 3, uvMax: 5 }), RULES, WX);
    assertEq(o.head, 'i-head-muetze');
    assertTrue(o.accessories.includes('i-acc-sonnencreme'));
  });
  test('A-22 felt=3 uv=4: unter 5 in eisig keine Creme', () => {
    const o = recommend(cond({ feltMin: 3, uvMax: 4 }), RULES, WX);
    assertTrue(!o.accessories.includes('i-acc-sonnencreme'));
    assertEq(o.overrides.includes('sun'), false);
  });
  test('A-22 felt=-3 uv=4: frost keine Creme, uv=5 Creme', () => {
    assertTrue(!recommend(cond({ feltMin: -3, uvMax: 4 }), RULES, WX).accessories.includes('i-acc-sonnencreme'));
    assertTrue(recommend(cond({ feltMin: -3, uvMax: 5 }), RULES, WX).accessories.includes('i-acc-sonnencreme'));
  });
  test('A-22 felt=7 uv=4: kalt keine Creme, uv=5 Creme', () => {
    assertTrue(!recommend(cond({ feltMin: 7, uvMax: 4 }), RULES, WX).accessories.includes('i-acc-sonnencreme'));
    assertTrue(recommend(cond({ feltMin: 7, uvMax: 5 }), RULES, WX).accessories.includes('i-acc-sonnencreme'));
  });
  test('A-22 felt=12 uv=3: kuehl Creme und Hut ab 3', () => {
    const o = recommend(cond({ feltMin: 12, uvMax: 3 }), RULES, WX);
    assertTrue(o.accessories.includes('i-acc-sonnencreme'));
    assertEq(o.head, 'i-head-sonnenhut');
  });

  test('AC-7 Regen', () => {
    const o = recommend(cond({ feltMin: 12, rainProbMax: 80, rainSum: 2 }), RULES, WX);
    assertEq(o.top, 'i-top-regenjacke');
    assertEq(o.shoes, 'i-shoes-gummistiefel');
  });
  test('AC-7 Regen+Schnee in kuehl: Regenjacke, Matschhose, Winterstiefel', () => {
    const o = recommend(cond({ feltMin: 12, rainProbMax: 80, rainSum: 2, snowSum: 1 }), RULES, WX);
    assertEq(o.top, 'i-top-regenjacke');
    assertEq(o.bottom, 'i-bottom-matschhose');
    assertEq(o.shoes, 'i-shoes-winterstiefel');
  });
  test('AC-7 Regen bei Kaelte: Winterjacke bleibt, Matschhose', () => {
    const o = recommend(cond({ feltMin: 3, rainProbMax: 80, rainSum: 2 }), RULES, WX);
    assertEq(o.top, 'i-top-winterjacke');
    assertEq(o.bottom, 'i-bottom-matschhose');
    assertEq(o.shoes, 'i-shoes-winterstiefel');
  });
  test('A-24 Matschhose nur kuehl bis eisig', () => {
    const rain = (felt) => recommend(cond({ feltMin: felt, rainProbMax: 80, rainSum: 2 }), RULES, WX).bottom;
    assertEq(rain(27), 'i-bottom-hose-kurz');
    assertEq(rain(22), 'i-bottom-hose-kurz');
    assertEq(rain(17), 'i-bottom-hose-lang');
    assertEq(rain(12), 'i-bottom-matschhose');
    assertEq(rain(7), 'i-bottom-matschhose');
    assertEq(rain(3), 'i-bottom-matschhose');
    assertEq(rain(-3), 'i-bottom-schneehose');
  });
  test('A-24 Regen in kalt: Matschhose, Gummistiefel', () => {
    const o = recommend(cond({ feltMin: 7, rainProbMax: 80, rainSum: 2 }), RULES, WX);
    assertEq(o.bottom, 'i-bottom-matschhose');
    assertEq(o.shoes, 'i-shoes-gummistiefel');
  });
  test('A-24 Regen+Schnee in kalt: Winterstiefel schlagen Gummistiefel', () => {
    const o = recommend(cond({ feltMin: 7, rainProbMax: 80, rainSum: 2, snowSum: 1 }), RULES, WX);
    assertEq(o.shoes, 'i-shoes-winterstiefel');
    assertEq(o.top, 'i-top-winterjacke');
  });
  test('Regen nur bei UND-Bedingung', () => {
    const o = recommend(cond({ feltMin: 12, rainProbMax: 80, rainSum: 0.1 }), RULES, WX);
    assertEq(o.top, 'i-top-teddyjacke');
  });

  test('AC-16 felt=17 gust=55', () => {
    const o = recommend(cond({ feltMin: 17, gustMax: 55 }), RULES, WX);
    assertEq(o.top, 'i-top-regenjacke');
    assertTrue(o.hints.includes('i-hint-wind'));
  });
  test('AC-16 felt=27 gust=55', () => {
    const o = recommend(cond({ feltMin: 27, gustMax: 55 }), RULES, WX);
    assertEq(o.top, 'i-top-tshirt');
    assertTrue(o.hints.includes('i-hint-wind'));
  });

  test('AC-17 felt=-1 tmin=0 wet=0.5', () => {
    const o = recommend(cond({ feltMin: -1, tempMin: 0, wetBefore: 0.5 }), RULES, WX);
    assertTrue(o.hints.includes('i-hint-glaette'));
  });
  test('AC-17 code=66', () => {
    const o = recommend(cond({ code: 66 }), RULES, WX);
    assertTrue(o.hints.includes('i-hint-glaette'));
  });

  test('A-23 Schnee in eisig: Schneejacke, Schneehose, Winterstiefel', () => {
    const o = recommend(cond({ feltMin: 3, snowSum: 1 }), RULES, WX);
    assertEq(o.top, 'i-top-schneejacke');
    assertEq(o.bottom, 'i-bottom-schneehose');
    assertEq(o.shoes, 'i-shoes-winterstiefel');
  });
  test('A-23 frost trocken: Schneejacke und Schneehose', () => {
    const o = recommend(cond({ feltMin: -8 }), RULES, WX);
    assertEq(o.top, 'i-top-schneejacke');
    assertEq(o.bottom, 'i-bottom-schneehose');
  });
  test('A-23 Schnee in kuehl und kalt: nur Winterstiefel (Tauwetter)', () => {
    const k = recommend(cond({ feltMin: 12, snowDepth: 3 }), RULES, WX);
    assertEq(k.top, 'i-top-teddyjacke'); assertEq(k.bottom, 'i-bottom-hose-lang'); assertEq(k.shoes, 'i-shoes-winterstiefel');
    const c = recommend(cond({ feltMin: 7, snowDepth: 3 }), RULES, WX);
    assertEq(c.top, 'i-top-winterjacke'); assertEq(c.shoes, 'i-shoes-winterstiefel');
  });
  test('A-23 Schnee in warm, mild, heiss wird ignoriert', () => {
    [27, 22, 17].forEach((felt) => {
      const base = recommend(cond({ feltMin: felt }), RULES, WX);
      const snow = recommend(cond({ feltMin: felt, snowSum: 1, snowDepth: 5 }), RULES, WX);
      assertEq(snow.top, base.top); assertEq(snow.bottom, base.bottom); assertEq(snow.shoes, base.shoes);
    });
  });
  test('Regen schlaegt Wind', () => {
    const o = recommend(cond({ feltMin: 17, gustMax: 60, rainProbMax: 80, rainSum: 2 }), RULES, WX);
    assertEq(o.top, 'i-top-regenjacke');
  });

  test('A-26 drinnen: nur Grundkleidung, ohne Kopf, Schuhe, Zubehoer', () => {
    RULES.bands.forEach((band) => {
      const felt = band.min === -Infinity ? -50 : band.min;
      const o = recommend(cond({ feltMin: felt, uvMax: 9, rainProbMax: 80, rainSum: 2, snowSum: 1 }), RULES, WX);
      assertEq(o.inside.head, null);
      assertEq(o.inside.shoes, null);
      assertEq(o.inside.accessories.length, 0);
      assertEq(o.inside.topChoices.map((id) => id.replace('i-top-', '')).join(), [].concat(band.in.top).join());
      assertEq(o.inside.bottom, `i-bottom-${band.in.bottom}`);
    });
  });
  test('A-26 drinnen kuehl bis frost: Pullover oder Kapuzenpullover, lange Hose, keine Schneehose', () => {
    [12, 7, 3, -8].forEach((felt) => {
      const o = recommend(cond({ feltMin: felt }), RULES, WX);
      assertEq(o.inside.topChoices.join(), 'i-top-pullover,i-top-kapuzenpullover');
      assertEq(o.inside.bottom, 'i-bottom-hose-lang');
    });
  });
  test('A-26 drinnen: beide Oberteile kommen vor, pro Tag bleibt die Wahl gleich', () => {
    const o = recommend(cond({ feltMin: 3 }), RULES, WX);
    const seen = new Set();
    for (let d = 0; d < 60; d++) {
      const a = pickOutfitVariants(o.inside, `2026-${d}`);
      assertEq(a.top, pickOutfitVariants(o.inside, `2026-${d}`).top);
      seen.add(a.top.replace(/-v\d+$/, ''));
    }
    assertEq([...seen].sort().join(), 'i-top-kapuzenpullover,i-top-pullover');
  });
  test('A-28 Halstuch in kuehl, Schal in eisig und frost, sonst keins von beiden', () => {
    const acc = (felt) => recommend(cond({ feltMin: felt }), RULES, WX).accessories;
    assertEq(acc(12).join(), 'i-acc-halstuch');
    assertEq(acc(7).join(), 'i-acc-handschuhe');
    assertEq(acc(3).join(), 'i-acc-handschuhe,i-acc-schal');
    assertEq(acc(-3).join(), 'i-acc-handschuhe,i-acc-schal');
    assertEq(acc(17).length + acc(22).length + acc(27).length, 0);
  });
  test('A-28 kuehl mit UV 9: Creme, Halstuch, Brille (max. 3)', () => {
    const o = recommend(cond({ feltMin: 12, uvMax: 9 }), RULES, WX);
    assertEq(o.accessories.join(), 'i-acc-sonnencreme,i-acc-halstuch,i-acc-sonnenbrille');
  });
  test('A-29 Schneejacke: nur die erste Farbe wird gewaehlt, Reserve bleibt im Sprite', () => {
    assertTrue(variantIds('i-top-schneejacke').length >= 2, 'Reserve-Farben fehlen im Sprite');
    for (let d = 0; d < 200; d++) assertEq(pickVariant('i-top-schneejacke', `2026-${d}`), 'i-top-schneejacke');
    forcedVariant = 2;
    assertEq(pickVariant('i-top-schneejacke', 'x'), 'i-top-schneejacke');
    forcedVariant = 0;
  });
  test('A-30 Sneaker und Sandalen (Crocs) haben keine Farbvarianten', () => {
    assertEq(variantIds('i-shoes-sneaker').length, 1);
    assertEq(variantIds('i-shoes-sandalen').length, 1);
  });

  test('A-26 Umschalter: inaktives Symbol ist zu 40 % sichtbar, aktives voll (nicht doppelt abgedunkelt)', () => {
    setView('out', false);
    const op = (btn) => Number(getComputedStyle(btn).opacity) * Number(getComputedStyle(btn.querySelector('svg')).opacity);
    assertEq(op(els.viewOut), 1);
    assertTrue(Math.abs(op(els.viewIn) - 0.4) < 0.01, `inaktiv ${op(els.viewIn)}`);
  });
  test('A-26 Umschalter: Tipp auf Haus blendet Schuhe und Zubehoer aus, Tipp auf Baum bringt sie zurueck', () => {
    const o = recommend(cond({ feltMin: 3, uvMax: 9 }), RULES, WX);
    setView('out', false);
    renderOutfit(o, cond({ feltMin: 3 }));
    assertEq(els.clothIcons[3].hasAttribute('hidden'), false);
    assertEq(els.accIcons[0].hasAttribute('hidden'), false);
    els.viewIn.click();
    assertEq(viewMode, 'in');
    assertEq(els.viewIn.getAttribute('aria-pressed'), 'true');
    assertEq(els.clothIcons[3].hasAttribute('hidden'), true);
    assertEq(els.clothIcons[0].hasAttribute('hidden'), true);
    assertEq(els.accIcons[0].hasAttribute('hidden'), true);
    els.viewOut.click();
    assertEq(viewMode, 'out');
    assertEq(els.clothIcons[3].hasAttribute('hidden'), false);
    clearTimeout(viewResetTimer);
    lastRender = null;
  });

  test('AC-8 max 3 Zubehoer, max 2 Hinweise', () => {
    const o = recommend(cond({ feltMin: 3, uvMax: 8, gustMax: 60, code: 66, tempMin: -1 }), RULES, WX);
    assertTrue(o.accessories.length <= 3);
    assertTrue(o.hints.length <= 2);
  });

  test('AC-10 felt=30 -> 0', () => assertEq(recommend(cond({ feltMin: 30 }), RULES, WX).scalePos, 0));
  test('AC-10 felt=-5 -> 1', () => assertEq(recommend(cond({ feltMin: -5 }), RULES, WX).scalePos, 1));
  test('AC-10 felt=40 geklemmt -> 0', () => assertEq(recommend(cond({ feltMin: 40 }), RULES, WX).scalePos, 0));
  test('AC-10 felt=-20 geklemmt -> 1', () => assertEq(recommend(cond({ feltMin: -20 }), RULES, WX).scalePos, 1));

  function buildSample(startS, n) {
    const time = []; const temp = []; const felt = []; const prob = []; const precip = [];
    const snowfall = []; const snowDepth = []; const uv = []; const gust = []; const code = []; const isDay = [];
    for (let i = 0; i < n; i++) {
      time.push(startS + i * 3600); temp.push(10 + i); felt.push(8 + i);
      prob.push(i % 5 === 0 ? 60 : 10); precip.push(i % 5 === 0 ? 1 : 0);
      snowfall.push(0); snowDepth.push(0);
      uv.push(i % 24 < 12 ? 4 : 0); gust.push(10 + i);
      code.push(i % 7 === 0 ? 61 : 1); isDay.push(i % 24 < 12 ? 1 : 0);
    }
    return {
      current: { time: startS, temperature_2m: temp[0] },
      hourly: {
        time, temperature_2m: temp, apparent_temperature: felt, precipitation_probability: prob,
        precipitation: precip, snowfall, snow_depth: snowDepth, uv_index: uv,
        wind_gusts_10m: gust, weather_code: code, is_day: isDay,
      },
    };
  }

  test('aggregate() Index-Versatz', () => {
    const startS = 1000000000;
    const forecast = buildSample(startS, 30);
    const c = aggregate(forecast, (startS + 10 * 3600 + 100) * 1000);
    assertTrue(c !== null);
    assertEq(c.feltMin, 18);
    assertEq(c.tempMin, 20);
    assertEq(c.gustMax, 24);
  });
  test('aggregate() null bei Fenster ausserhalb der Daten', () => {
    const startS = 1000000000;
    const forecast = buildSample(startS, 10);
    const c = aggregate(forecast, (startS + 9 * 3600 + 100) * 1000);
    assertEq(c, null);
  });
  test('aggregate() null wenn im Fenster keine gefuehlte Temperatur steht', () => {
    const startS = 1000000000;
    const forecast = buildSample(startS, 30);
    for (let i = 10; i <= 14; i++) forecast.hourly.apparent_temperature[i] = null;
    assertEq(aggregate(forecast, (startS + 10 * 3600 + 100) * 1000), null);
  });
  test('aggregate() null-Werte werden uebersprungen', () => {
    const startS = 1000000000;
    const forecast = buildSample(startS, 30);
    forecast.hourly.apparent_temperature[10] = null;
    const c = aggregate(forecast, (startS + 10 * 3600 + 100) * 1000);
    assertEq(c.feltMin, 19);
  });
  test('aggregate() alle Werte eines Summenfeldes null -> 0', () => {
    const startS = 1000000000;
    const forecast = buildSample(startS, 30);
    for (let i = 11; i <= 14; i++) forecast.hourly.precipitation[i] = null;
    const c = aggregate(forecast, (startS + 10 * 3600 + 100) * 1000);
    assertEq(c.rainSum, 0);
  });

  const usedIds = new Set();
  RULES.bands.forEach((b) => {
    if (b.head) usedIds.add(`i-head-${b.head}`);
    usedIds.add(`i-top-${b.top}`); usedIds.add(`i-bottom-${b.bottom}`); usedIds.add(`i-shoes-${b.shoes}`);
    [].concat(b.in.top).forEach((x) => usedIds.add(`i-top-${x}`)); usedIds.add(`i-bottom-${b.in.bottom}`);
    b.acc.forEach((a) => usedIds.add(`i-acc-${a}`));
  });
  usedIds.add(`i-head-${RULES.sun.head}`);
  usedIds.add('i-acc-sonnencreme'); usedIds.add('i-acc-sonnenbrille');
  usedIds.add(`i-top-${RULES.wind.top}`); usedIds.add('i-hint-wind');
  usedIds.add(`i-top-${RULES.rain.top}`); usedIds.add(`i-bottom-${RULES.rain.bottom}`); usedIds.add(`i-shoes-${RULES.rain.shoes}`);
  usedIds.add(`i-top-${RULES.snow.top}`); usedIds.add(`i-bottom-${RULES.snow.bottom}`); usedIds.add(`i-shoes-${RULES.snow.shoes}`);
  usedIds.add('i-ui-innen'); usedIds.add('i-ui-aussen');
  usedIds.add('i-hint-glaette');
  WX.codeGroups.forEach((g) => { usedIds.add(`i-wx-${g.icon}`); usedIds.add(`i-wx-${g.iconNight}`); });
  usedIds.add('i-sys-uhr'); usedIds.add('i-sys-fehler');

  usedIds.forEach((id) => {
    test(`Icon vorhanden: ${id}`, () => {
      const symbol = document.getElementById(id);
      assertTrue(symbol && symbol.tagName.toLowerCase() === 'symbol', `Symbol #${id} fehlt`);
    });
    const symbol = document.getElementById(id);
    if (symbol && symbol.hasAttribute('data-placeholder')) {
      warnCount++;
      lines.push(`WARN Platzhalter aktiv: ${id}`);
    }
  });

  // Farbvarianten (A-25): jede Variante passt in das Fenster ihres Teils, die Auswahl ist stabil und kommt rum
  const SLOT_MAX = { head: [40, 15], top: [30, 24], bottom: [30, 27], shoes: [30, 17], acc: [26, 20] };   // Breite, Höhe in Kunstpixeln
  const baseIds = [...document.querySelectorAll('symbol')].map((sy) => sy.id)
    .filter((id) => /^i-(head|top|bottom|shoes|acc)-/.test(id) && !/-v\d+$/.test(id));
  baseIds.forEach((id) => {
    const kind = id.split('-')[1];
    test(`Größe passt ins Fenster (alle Varianten): ${id}`, () => {
      variantIds(id).forEach((vid) => {
        const vb = viewBoxOf(vid);
        assertTrue(vb[2] <= SLOT_MAX[kind][0] && vb[3] <= SLOT_MAX[kind][1], `${vid} ist ${vb[2]}x${vb[3]}, erlaubt ${SLOT_MAX[kind].join('x')}`);
      });
    });
  });
  test('Variante: gleicher Tag, gleiche Auswahl, gültiges Symbol', () => {
    ['2026-1-1', '2026-1-2', '2026-1-3'].forEach((seed) => {
      const id = pickVariant('i-top-tshirt', seed);
      assertEq(id, pickVariant('i-top-tshirt', seed));
      assertTrue(variantIds('i-top-tshirt').includes(id), id);
    });
  });
  test('Variante: über viele Tage kommen alle T-Shirt-Farben vor', () => {
    const seen = new Set();
    for (let d = 1; d <= 300; d++) seen.add(pickVariant('i-top-tshirt', `2026-5-${d}`));
    assertEq(seen.size, variantIds('i-top-tshirt').length);
  });
  test('Variante: Teil ohne Varianten bleibt, ?v erzwingt', () => {
    assertEq(pickVariant('i-acc-sonnencreme', 'x'), 'i-acc-sonnencreme');
    forcedVariant = 2;
    assertEq(pickVariant('i-top-tshirt', 'x'), 'i-top-tshirt-v2');
    forcedVariant = 0;
  });
  baseIds.filter((id) => !id.startsWith('i-acc-')).forEach((id) => {
    test(`Variante: Farb-Tags vorhanden (${id})`, () => {
      variantIds(id).forEach((vid) => assertTrue(Array.isArray(VARIANT_TAGS[vid]), `${vid} fehlt in VARIANT_TAGS`));
    });
  });
  test('Variante: Nachbarn teilen nie ein Farb-Tag (alle Bänder, Wetter, 200 Tage)', () => {
    const wetter = [{}, { rainProbMax: 80, rainSum: 2 }, { snowSum: 1 }, { gustMax: 60 }, { uvMax: 9 }];
    let checked = 0;
    RULES.bands.forEach((band) => {
      const felt = band.min === -Infinity ? -10 : band.min;
      wetter.forEach((w) => {
        const o = recommend(cond(Object.assign({ feltMin: felt }, w)), RULES, WX);
        [o, o.inside].forEach((look) => {
          for (let d = 0; d < 200; d++) {
            const c = pickOutfitVariants(look, `2026-${d}`);
            [['head', 'top'], ['top', 'bottom'], ['bottom', 'shoes']].forEach(([a, b]) => {
              if (!c[a] || !c[b]) return;
              const shared = (VARIANT_TAGS[c[a]] || []).filter((t) => (VARIANT_TAGS[c[b]] || []).includes(t));
              assertEq(shared.length, 0, `${band.id} Tag ${d}: ${c[a]} + ${c[b]} teilen ${shared}`);
              checked++;
            });
          }
        });
      });
    });
    assertTrue(checked > 1000, 'zu wenige Paare geprüft');
  });
  Object.keys(VARIANT_WEIGHTS).forEach((id) => {
    test(`Variante: Gewichte passen zur Anzahl (${id})`, () => assertEq(VARIANT_WEIGHTS[id].length, variantIds(id).length));
  });

  lines.push('');
  lines.push(`${passCount} PASS, ${failCount} FAIL, ${warnCount} WARN`);
  els.testOutput.textContent = lines.join('\n');
}
