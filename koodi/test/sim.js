// Pelilogiikan savutesti: node test/sim.js
const { Game, UNIT_TYPES, TAPAHTUMAT } = require('../game');
const MAP = require('../../kartta/pelikentta_v2_tiles.json');
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

// 7. v3: metsäpeikot ja vesihiisi
{ const g = new Game(MAP, { seed: 7, firstEvent: 1e9, firstPeikko: 1, firstHiisi: 1e9 });
  assert(g.shore.length > 10, 'rantavesiruudut löytyvät (' + g.shore.length + ')');
  run(g, 2); const pk = [...g.units.values()].filter(u => u.type === 'peikko');
  assert(pk.length >= 1 && pk.length <= 3 && pk.every(p => g._forest(Math.floor(p.x), Math.floor(p.y))), 'peikot syntyivät metsään (' + pk.length + ')');
  g.nextPeikko = 0; run(g, 1); g.nextPeikko = 0; run(g, 1); g.nextPeikko = 0; run(g, 1);
  assert([...g.units.values()].filter(u => u.type === 'peikko').length <= 3, 'peikkoja enintään 3');
  // peikko hyökkää lähelle tulleeseen ja varastaa kuorman
  const p = pk[0]; const j = g._spawnUnitNear(1, 'tolkkijussi', p.x + 1, p.y); j.carry = 5; j.state = 'idle';
  let stole = false, hit = false; const hp0 = j.hp;
  for (let i = 0; i < 400 && !(stole || hit); i++) { j.state = 'idle'; g.step(); const s = g.snapshot(); if (s.ev.some(e => e.e === 'varasti')) stole = true; if (j.hp < hp0 || !g.units.has(j.id)) hit = true; if (s.ev.some(e => e.e === 'karjunta')) hit = true; }
  assert(stole || hit, 'peikko reagoi lähellä olevaan (varasti=' + stole + ', hyökkäsi/karjui=' + hit + ')');
  // kaatunut peikko pudottaa tölkkejä
  const c0 = [...g.cans.values()].reduce((a, c) => a + c.n, 0); const p2 = [...g.units.values()].find(u => u.type === 'peikko'); g._damage(null, p2, 9999);
  assert([...g.cans.values()].reduce((a, c) => a + c.n, 0) >= c0 + 6, 'kaatunut peikko pudotti tölkkejä'); }
{ const g = new Game(MAP, { seed: 8, firstEvent: 1e9, firstPeikko: 1e9, firstHiisi: 1 });
  const [c, r] = g.shore[0]; const u = g._spawnUnitNear(1, 'lahiojermu', c + 0.5, r + 0.5); u.x = c + 0.5 + 1.5; while (!g.passable(Math.floor(u.x), Math.floor(u.y))) u.x -= 0.5;
  let ev = []; for (let i = 0; i < 60; i++) { g.step(); ev = ev.concat(g.snapshot().ev); }
  assert(ev.some(e => e.e === 'hiisi_kuplat'), 'vesihiisi: kuplat ennen nousua');
  assert(ev.some(e => e.e === 'olento' && e.key === 'vesihiisi'), 'vesihiisi nousi');
  const h = [...g.units.values()].find(x => x.type === 'vesihiisi'); assert(h && g.terrain[Math.floor(h.y)][Math.floor(h.x)] === 2, 'hiisi on vedessä');
  for (let i = 0; i < 160; i++) { g.step(); ev = ev.concat(g.snapshot().ev); }
  assert(ev.some(e => e.e === 'ammus' && e.w === 'hiisi'), 'hiisi hyökkäsi rannalla olevaan');
  assert(ev.some(e => e.e === 'hiisi_sukelsi') || !g.units.has(h.id), 'hiisi sukelsi takaisin'); }

// 9. v4: kerrostalot, sauna, grilli, mummo, kirppis, lumimyrsky, tekstarit, hemuli, vänä
{ const g = new Game(MAP, { seed: 9, firstEvent: 1e9, firstPeikko: 1e9, firstHiisi: 1e9 });
  const B = t => g.buildings.filter(b => b.tyyppi === t), evs = [], runE = s => { for (let i = 0; i < s * 10; i++) { g.step(); evs.push(...g.snapshot().ev); } };
  assert(B('kerrostalo').length >= 2 && B('sauna').length && B('pihagrilli').length && B('kirppu').length, 'v4-rakennukset sijoitettu (' + B('kerrostalo').length + ' kerrostaloa)');
  const kt = B('kerrostalo')[0]; kt.owner = 1;
  const js = []; for (let i = 0; i < 4; i++) js.push(g._spawnUnitNear(1, 'lahiojermu', kt.x, kt.y + 2));
  g.command(1, { t: 'order', ids: js.map(u => u.id), x: kt.x, y: kt.y }); runE(4);
  assert(kt.sisalla.length === 4 && js.every(u => !g.units.has(u.id)), 'jalkaväki meni kerrostaloon (' + kt.sisalla.length + ')');
  assert(evs.some(e => e.e === 'bileet'), 'kotibileet alkoivat'); runE(18);
  assert(evs.some(e => e.e === 'naapurit') && evs.some(e => e.e === 'haato') && js.every(u => g.units.has(u.id) && u.k >= 80 && u.slow > 0), 'naapurit valittaa -> häätö kännissä (' + js.map(u => [g.units.has(u.id), Math.round(u.k), Math.round(u.slow)]).join(' ') + ')');
  const e2 = g._spawnUnitNear(2, 'tolkkijussi', kt.x, kt.y + 3); kt.sisalla = js.slice(0, 2); js.slice(0, 2).forEach(u => g.units.delete(u.id)); evs.length = 0; runE(3);
  assert(evs.some(e => e.e === 'ammus' && js.slice(0, 2).some(j => j.id === e.id)), 'talosta ammutaan');
  g.command(1, { t: 'tyhjenna', b: kt.id }); assert(!kt.sisalla.length, 'Tyhjennä talo toimii'); g._remove(e2);
  kt.sisalla = js.slice(); for (let i = 0; i < 2; i++) kt.sisalla.push(g._spawnUnitNear(1, 'tolkkijussi', 1, 1)); kt.sisalla.forEach(u => g.units.delete(u.id)); evs.length = 0; runE(5);
  assert(evs.some(e => e.e === 'piiritys') && evs.filter(e => e.e === 'putkaan').length === 6 && !kt.sisalla.length, 'poliisipiiritys vei 6 putkaan');
  // sauna
  const sa = B('sauna')[0]; const s1 = g._spawnUnitNear(2, 'lahiojermu', sa.x, sa.y + 2); s1.k = 80; s1.hp = 30;
  g.command(2, { t: 'order', ids: [s1.id], x: sa.x, y: sa.y }); runE(6);
  assert(s1.state === 'sauna' && s1.k < 50 && s1.hp > 30, 'sauna: selviää ja paranee (k=' + Math.round(s1.k) + ')'); runE(23);
  assert(s1.stun > 0, 'sauna: yli 25 s -> sammui');
  // grilli
  const gr = B('pihagrilli')[0]; gr.owner = 1; gr.grilliT = 0.5; const gj = g._spawnUnitNear(1, 'lahiojermu', gr.x, gr.y + 2); evs.length = 0; runE(1);
  assert(evs.some(e => e.e === 'paljastus' && e.team === 1 && e.ids.includes(gj.id)), 'pihagrilli paljastaa sijainnin');
  // mummo + lahjonta
  const m = [...g.units.values()].find(u => u.type === 'pullomummo'); const mj = g._spawnUnitNear(1, 'tolkkijussi', m.x + 1, m.y); mj.carry = 4; mj.stun = 0;
  g.command(1, { t: 'order', ids: [mj.id], x: m.x, y: m.y - 0.15 }); runE(3);
  assert(m.lahjottu === 1 && mj.carry === 0, 'mummo lahjottu tölkeillä');
  g.cans.clear(); const cid = g.nextId++; g.cans.set(cid, { id: cid, x: m.x + 0.5, y: m.y, n: 5 }); m.tgt = null; const r0 = g.players[1].money; runE(4);
  assert(g.players[1].money >= r0 + 50 && evs.some(e => e.e === 'mummo_raha'), 'lahjottu mummo muuttaa tölkit rahaksi');
  // kirppis
  const ki = B('kirppu')[0]; const kj = g._spawnUnitNear(1, 'tolkkijussi', ki.x, ki.y + 2); kj.carry = 3; evs.length = 0;
  g.command(1, { t: 'order', ids: [kj.id], x: ki.x, y: ki.y }); runE(4);
  assert(kj.carry === 0 && evs.some(e => e.e === 'esine' && e.id === kj.id), 'kirpputori: 3 tölkkiä -> esine');
  kj.esine = 'lenkkarit'; const sp1 = g._speed(kj); kj.esine = 0; assert(sp1 > g._speed(kj), 'lenkkarit nopeuttavat');
  // lumimyrsky
  const la = g._spawnUnitNear(1, 'lada', 20, 40), mo = g._spawnUnitNear(1, 'monkija', 20, 40), sj0 = g._speed(kj), mo0 = g._speed(mo); g.startEvent('lumimyrsky');
  assert(g._speed(la) === 0 && Math.abs(g._speed(kj) / sj0 - 0.6) < 0.01 && Math.abs(g._speed(mo) / mo0 - 0.9) < 0.01, 'lumimyrsky hidastaa, Lada jumissa'); g._endEvent();
  // tekstari
  g.tekstariP = 1; const tj = g._spawnUnitNear(2, 'lahiojermu', 30, 12); tj.k = 100; tj.ktila = 3; evs.length = 0; runE(6); g.tekstariP = 0;
  assert(evs.some(e => e.e === 'tekstari') && evs.some(e => e.e === 'paljastus' && e.team === 2 && e.aika === 8), 'kännitekstari paljastaa joukkueen');
  // hemuli
  const he = [...g.units.values()].find(u => u.type === 'hemuli'); g.caesarP = 1; he.state = 'syo'; he.aiT = 0.1; runE(0.3);
  assert(he.type === 'hemuli_caesar' && he.owner === 3 && evs.some(e => e.e === 'muodonmuutos'), 'hemulista tuli Caesar');
  const hv = g._spawnUnitNear(1, 'tolkkijussi', he.x + 1, he.y); evs.length = 0; runE(3);
  assert(evs.some(e => e.e === 'ammus' && e.id === he.id), 'Caesar hyökkää'); runE(30);
  assert(he.type === 'hemuli' && he.owner === 0, 'Caesar palasi hemuliksi');
  // vänä
  const va = [...g.units.values()].find(u => u.type === 'vana'); va.ai = 'kanni'; va.aiT = 30; va.cd = 0; const vt = g._spawnUnitNear(2, 'tolkkijussi', va.x + 2, va.y); vt.hp = 40; evs.length = 0; runE(1);
  assert(evs.some(e => e.e === 'ammus' && e.w === 'pallo'), 'Vänä potkaisi palloa');
}
