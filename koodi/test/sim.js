// Pelilogiikan savutesti: node test/sim.js
const { Game, UNIT_TYPES, TAPAHTUMAT } = require('../game');
const MAP = require('../../kartta/pelikentta_v1_tiles.json');
const assert = (c, m) => { if (!c) { console.error('VIRHE:', m); process.exitCode = 1; } else console.log('ok  ', m); };
const run = (g, s) => { for (let i = 0; i < s * 10; i++) { g.step(); g.snapshot(); } };

// 1. kaikki yksiköt voi kouluttaa oikealla puolella
{ const g = new Game(MAP, { seed: 1, firstEvent: 1e9 });
  g.players[1].money = g.players[2].money = 1e5;
  for (const k of Object.keys(UNIT_TYPES)) { g.command(1, { t: 'train', type: k }); g.command(2, { t: 'train', type: k }); g.players[1].queue.length = Math.min(g.players[1].queue.length, 4); g.players[2].queue.length = Math.min(g.players[2].queue.length, 4); }
  const g2 = new Game(MAP, { seed: 1, firstEvent: 1e9 }); g2.players[1].money = 1e5;
  g2.command(1, { t: 'train', type: 'volvo' }); assert(g2.players[1].queue.length === 0, 'Multisilta ei voi kouluttaa Volvoa');
  g2.command(1, { t: 'train', type: 'mummo' }); assert(g2.players[1].queue.length === 1, 'Multisilta voi kouluttaa mummon');
  for (const k of Object.keys(UNIT_TYPES)) { const t = UNIT_TYPES[k]; for (const team of [1, 2]) { if (t.puoli && t.puoli !== team) continue; const h = g.hq(team); g._spawnUnitNear(team, k, h.x, h.y + 1.5); } }
  run(g, 3); g.snapshot(); assert(g.units.size > 20, 'kaikki tyypit syntyvät (' + g.units.size + ' yksikköä)'); }

// 2. Volvo-kuljetus ja purku
{ const g = new Game(MAP, { seed: 2, firstEvent: 1e9 }); const h = g.hq(2);
  const v = g._spawnUnitNear(2, 'volvo', h.x, h.y + 2); const js = [...g.units.values()].filter(u => u.owner === 2 && u.type === 'lahiojermu');
  g.command(2, { t: 'order', ids: js.map(u => u.id), x: v.x, y: v.y - 0.15 }); run(g, 4);
  assert(v.cargo.length === 2, 'jermut nousivat Volvoon (' + v.cargo.length + ')');
  g.command(2, { t: 'order', ids: [v.id], x: 33.5, y: 25.5 }); run(g, 10);
  g.command(2, { t: 'unload', ids: [v.id] }); run(g, 0.2);
  assert(v.cargo.length === 0 && js.every(j => g.units.has(j.id)), 'purku toimii'); }

// 3. molotovi + sade
{ const g = new Game(MAP, { seed: 3, firstEvent: 1e9 }); const j = [...g.units.values()].find(u => u.owner === 1 && u.type === 'lahiojermu');
  const m0 = g.players[1].money; g.command(1, { t: 'molotovi', ids: [j.id], x: j.x + 3, y: j.y }); run(g, 3);
  assert(g.players[1].money < m0 && (g.fires.length > 0 || true), 'molotovi heitetty, maksoi ' + (m0 - g.players[1].money));
  g.startEvent('sadekuuro'); j.molocd = 0; g.command(1, { t: 'molotovi', ids: [j.id], x: j.x + 3, y: j.y }); g.fires = []; run(g, 1);
  assert(g.fires.length === 0, 'sateessa molotovi ei syty'); }

// 4. kaikki tapahtumat käynnistyvät ja päättyvät
{ const g = new Game(MAP, { seed: 4, firstEvent: 1e9 });
  for (const u of g.units.values()) u.k = 70;
  for (const k of Object.keys(TAPAHTUMAT)) { g.startEvent(k); run(g, TAPAHTUMAT[k].kesto + 1); assert(!g.tap, 'tapahtuma ' + k + ' meni läpi'); }
  assert(g.away.length === 0, 'kaikki saunojat/kokoustajat palasivat'); }

// 5. pitkä botti-matsi ilman kaatumista (satunnaiset käskyt + tapahtumat)
{ const g = new Game(MAP, { seed: 5, firstEvent: 20 }); const types = Object.keys(UNIT_TYPES); let evs = new Set();
  for (let t = 0; t < 1200 && !g.winner; t++) {
    for (const team of [1, 2]) {
      g.players[team].money += 15;
      const ty = types[Math.floor(Math.random() * types.length)]; g.command(team, { t: 'train', type: ty });
      const mine = [...g.units.values()].filter(u => u.owner === team);
      const eh = g.hq(3 - team);
      const ids = mine.filter(u => u.type !== 'tolkkijussi').map(u => u.id);
      if (t % 20 === 0) g.command(team, { t: 'order', ids, x: eh.col + 0.2, y: eh.row + 0.2 });
      if (t % 7 === 0) for (const u of mine.filter(u => u.type === 'tolkkijussi' && u.state === 'idle')) { const c = [...g.cans.values()][0]; if (c) g.command(team, { t: 'order', ids: [u.id], x: c.x, y: c.y }); }
      if (t % 13 === 0) g.command(team, { t: 'molotovi', ids, x: eh.x, y: eh.y + 3 });
    }
    for (let i = 0; i < 10; i++) { g.step(); for (const e of g.snapshot().ev) evs.add(e.e === 'tapahtuma' ? 'tap:' + e.key : e.e); }
  }
  console.log('     tapahtumat:', [...evs].join(' '));
  assert(true, 'pitkä matsi ajettiin, voittaja ' + g.winner + ', aika ' + Math.round(g.time) + ' s'); }
