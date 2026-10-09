'use strict';
// Lähiösota: Etelä-Tampere – pelilogiikka (palvelin on auktoriteetti).
// Koordinaatit ruutuina: x = sarake, y = rivi (liukuluku, ruudun keskipiste = c+0.5).

const TICK = 0.1; // s

const UNIT_TYPES = {
  tolkkijussi: { nimi: 'Tölkkijussi', hinta: 50, aika: 3, hp: 60, nopeus: 1.6, kantaa: 8, ase: null, juonti: 0.25 },
  lahiojermu:  { nimi: 'Lähiöjermu', hinta: 80, aika: 4, hp: 100, nopeus: 1.8, kantaa: 0,
                 ase: { nimi: 'Pystykorva (RK-62)', vahinko: 9, kantama: 4, tauko: 1.0, aani: 'rk62' }, juonti: 0.55 },
  mopopoika:   { nimi: 'Mopopoika', hinta: 120, aika: 5, hp: 70, nopeus: 3.4, kantaa: 4,
                 ase: { nimi: 'Jatimatic', vahinko: 4, kantama: 3, tauko: 0.45, aani: 'jatimatic' }, juonti: 0.35 },
};

const CAN_VALUE = 10;       // rahaa / tölkki
const START_MONEY = 250;
const HQ_HP = 2500;
const CAPTURE_TIME = 10;    // s yhdellä yksiköllä, nopeutuu max 3 yksiköllä
const CAPTURE_RADIUS = 2.6;
const VISION = 5;

// Rakennustyypit tiles.jsonin resources-nimen mukaan
const BONUS = {
  'KALJA-VARASTO':     { tyyppi: 'baari',  kuvaus: 'Ilmainen kalja: lähellä olevat omat +15 % vahinkoa, mutta kännimittari nousee nopeasti.' },
  'MAKKARA-VARASTO':   { tyyppi: 'kmarket', kuvaus: 'Pantinpalautus: Tölkkijussit tuovat tölkit tänne (10 rahaa/tölkki).' },
  'PIZZATEHDAS':       { tyyppi: 'muu', kuvaus: 'Kaikki omat yksiköt paranevat hitaasti (+0,5 HP/s).' },
  'KARKKIKAIVOS':      { tyyppi: 'muu', kuvaus: 'Energiajuoma: kaikki omat yksiköt liikkuvat 15 % nopeammin.' },
  'LÄÄKINTÄASEMA':     { tyyppi: 'muu', kuvaus: 'Lähellä olevat omat paranevat ja selvenevät nopeasti.' },
  'KAHVILÄHDE':        { tyyppi: 'muu', kuvaus: 'Sammuneet omat heräävät tuplanopeudella.' },
  'PERUNAPELTO':       { tyyppi: 'muu', kuvaus: 'Tuottaa passiivisesti +1 rahaa/s.' },
  'LIHAPULLALINNAKE':  { tyyppi: 'muu', kuvaus: 'Lähellä olevat omat ottavat puolet vähemmän vahinkoa.' },
  'TIEDUSTELUKESKUS':  { tyyppi: 'muu', kuvaus: '(Raakaversio: ei sumua vielä) +0,5 rahaa/s.' },
  'HUOLTOVARIKKO':     { tyyppi: 'muu', kuvaus: '(Raakaversio: ei ajoneuvoja vielä) +0,5 rahaa/s.' },
  'ROMUTARVIKEVARASTO':{ tyyppi: 'muu', kuvaus: '(Raakaversio: ei ajoneuvoja vielä) +0,5 rahaa/s.' },
  'POLTTOAINEVARASTO': { tyyppi: 'muu', kuvaus: '(Raakaversio: ei molotoveja vielä) +0,5 rahaa/s.' },
  'KAASUVARASTO':      { tyyppi: 'muu', kuvaus: '(Raakaversio: ei molotoveja vielä) +0,5 rahaa/s.' },
};

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

class Heap {
  constructor() { this.a = []; }
  push(n, p) { const a = this.a; a.push([p, n]); let i = a.length - 1; while (i > 0) { const j = (i - 1) >> 1; if (a[j][0] <= a[i][0]) break; [a[i], a[j]] = [a[j], a[i]]; i = j; } }
  pop() { const a = this.a; const top = a[0]; const last = a.pop(); if (a.length) { a[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r; if (m === i) break; [a[i], a[m]] = [a[m], a[i]]; i = m; } } return top[1]; }
  get size() { return this.a.length; }
}

class Game {
  constructor(map, opts = {}) {
    this.map = map;
    this.W = map.size.cols; this.H = map.size.rows;
    this.terrain = map.terrain;
    this.cost = {};
    for (const t of map.terrain_types) this.cost[t.id] = t.move_cost;
    this.rand = mulberry32(opts.seed || 12345);
    this.time = 0; this.tick = 0;
    this.nextId = 1;
    this.units = new Map();
    this.cans = new Map();
    this.events = [];
    this.winner = 0;
    this.players = {
      1: { money: START_MONEY, queue: [], nimi: 'Multisilta' },
      2: { money: START_MONEY, queue: [], nimi: 'Peltolammi' },
    };
    this.buildings = [];
    this._placeBuildings();
    this._spawnStart();
    this._spawnCans(45);
  }

  passable(c, r) {
    if (c < 0 || r < 0 || c >= this.W || r >= this.H) return false;
    return this.cost[this.terrain[r][c]] != null;
  }
  costAt(x, y) { const c = Math.floor(x), r = Math.floor(y); if (!this.passable(c, r)) return 1; return this.cost[this.terrain[r][c]]; }

  _placeBuildings() {
    const used = new Set();
    const free = (c, r) => { for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) { if (used.has((r + i) * 1000 + c + j)) return false; if (c + j >= this.W || r + i >= this.H) return false; } return true; };
    const place = (c, r) => {
      for (let rad = 0; rad < 6; rad++) for (let dr = -rad; dr <= rad; dr++) for (let dc = -rad; dc <= rad; dc++) {
        if (Math.max(Math.abs(dr), Math.abs(dc)) !== rad) continue;
        if (free(c + dc, r + dr) && c + dc >= 0 && r + dr >= 0) { for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) used.add((r + dr + i) * 1000 + c + dc + j); return [c + dc, r + dr]; }
      }
      return [c, r];
    };
    for (const b of this.map.bases) {
      const [c, r] = place(b.col, b.row);
      this.buildings.push({ id: this.nextId++, tyyppi: 'paamaja', nimi: b.nimi, osm: b.osm_name, col: c, row: r, owner: b.faction,
        hp: HQ_HP, maxhp: HQ_HP, cap: { team: 0, p: 0 }, kuvaus: 'Kouluttaa yksiköt. Tuhoa vihollisen päämaja voittaaksesi. Lähellä selvitään.' });
    }
    for (const res of this.map.resources) {
      const bon = BONUS[res.nimi] || { tyyppi: 'muu', kuvaus: '' };
      const [c, r] = place(res.col, res.row);
      const owner = res.puoli === 'Multisilta' ? 1 : res.puoli === 'Peltolammi' ? 2 : 0;
      this.buildings.push({ id: this.nextId++, tyyppi: bon.tyyppi, bonus: res.nimi, nimi: res.nimi, osm: res.osm_name, col: c, row: r, owner,
        cap: { team: 0, p: 0 }, kuvaus: bon.kuvaus });
    }
    for (const b of this.buildings) { b.x = b.col + 1; b.y = b.row + 1; }
  }

  hq(team) { return this.buildings.find(b => b.tyyppi === 'paamaja' && b.owner === team); }

  nearestPassable(x, y, maxR = 8) {
    const c0 = Math.floor(x), r0 = Math.floor(y);
    let best = null, bd = Infinity;
    for (let r = r0 - maxR; r <= r0 + maxR; r++) for (let c = c0 - maxR; c <= c0 + maxR; c++) {
      if (!this.passable(c, r)) continue;
      const d = (c + 0.5 - x) ** 2 + (r + 0.5 - y) ** 2;
      if (d < bd) { bd = d; best = [c, r]; }
    }
    return best;
  }

  _spawnUnitNear(team, type, x, y) {
    // etsi vapaa ruutu rakennuksen ympäriltä
    const spots = [];
    for (let r = Math.floor(y) - 3; r <= Math.floor(y) + 3; r++) for (let c = Math.floor(x) - 3; c <= Math.floor(x) + 3; c++)
      if (this.passable(c, r)) spots.push([c, r, (c + 0.5 - x) ** 2 + (r + 0.5 - y) ** 2]);
    spots.sort((a, b) => a[2] - b[2]);
    let pick = spots[0] || this.nearestPassable(x, y, 10);
    for (const s of spots) { let occ = 0; for (const u of this.units.values()) if (Math.floor(u.x) === s[0] && Math.floor(u.y) === s[1]) occ++; if (!occ) { pick = s; break; } }
    const t = UNIT_TYPES[type];
    const u = { id: this.nextId++, type, owner: team, x: pick[0] + 0.5, y: pick[1] + 0.5, hp: t.hp, maxhp: t.hp,
      k: 0, carry: 0, state: 'idle', path: null, target: null, cd: 0, stun: 0, omiin: false, repath: 0, collectT: 0, home: null, dir: 1 };
    this.units.set(u.id, u);
    return u;
  }

  _spawnStart() {
    for (const team of [1, 2]) {
      const h = this.hq(team);
      for (let i = 0; i < 2; i++) this._spawnUnitNear(team, 'tolkkijussi', h.x, h.y);
      for (let i = 0; i < 2; i++) this._spawnUnitNear(team, 'lahiojermu', h.x, h.y);
      // aloitustölkit päämajan lähelle
      for (let i = 0; i < 4; i++) this._spawnCanNear(h.x, h.y, 4, 7, 5 + Math.floor(this.rand() * 4));
    }
  }

  _spawnCanNear(x, y, rmin, rmax, n) {
    for (let tries = 0; tries < 50; tries++) {
      const a = this.rand() * Math.PI * 2, d = rmin + this.rand() * (rmax - rmin);
      const c = Math.floor(x + Math.cos(a) * d), r = Math.floor(y + Math.sin(a) * d);
      if (this.passable(c, r)) { const id = this.nextId++; this.cans.set(id, { id, x: c + 0.5, y: r + 0.5, n }); return; }
    }
  }
  _spawnCans(count) {
    for (let i = 0; i < count; i++) {
      for (let tries = 0; tries < 50; tries++) {
        const c = Math.floor(this.rand() * this.W), r = Math.floor(this.rand() * this.H);
        if (this.passable(c, r)) { const id = this.nextId++; this.cans.set(id, { id, x: c + 0.5, y: r + 0.5, n: 3 + Math.floor(this.rand() * 6) }); break; }
      }
    }
  }
  _dropCans(x, y, n) {
    if (n <= 0) return;
    const p = this.passable(Math.floor(x), Math.floor(y)) ? [Math.floor(x), Math.floor(y)] : this.nearestPassable(x, y);
    if (!p) return;
    const id = this.nextId++; this.cans.set(id, { id, x: x, y: y, n });
  }

  // ---------- reitinhaku (A*, 8 suuntaa, ei kulmanoikaisua) ----------
  findPath(sx, sy, tx, ty) {
    let sc = Math.floor(sx), sr = Math.floor(sy);
    let tc = Math.floor(tx), tr = Math.floor(ty);
    if (!this.passable(tc, tr)) { const p = this.nearestPassable(tx, ty); if (!p) return null; [tc, tr] = p; }
    if (!this.passable(sc, sr)) { const p = this.nearestPassable(sx, sy, 3); if (p) [sc, sr] = p; }
    const W = this.W, start = sr * W + sc, goal = tr * W + tc;
    if (start === goal) return [[tc + 0.5, tr + 0.5]];
    const g = new Float32Array(W * this.H).fill(Infinity), from = new Int32Array(W * this.H).fill(-1), closed = new Uint8Array(W * this.H);
    const h = (i) => { const dc = Math.abs(i % W - tc), dr = Math.abs(((i / W) | 0) - tr); return 0.5 * (Math.max(dc, dr) + 0.414 * Math.min(dc, dr)); };
    const heap = new Heap(); g[start] = 0; heap.push(start, h(start));
    let found = false, expanded = 0;
    while (heap.size) {
      const cur = heap.pop(); if (closed[cur]) continue; closed[cur] = 1;
      if (cur === goal) { found = true; break; }
      if (++expanded > 6000) break;
      const cc = cur % W, cr = (cur / W) | 0;
      for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
        if (!dr && !dc) continue;
        const nc = cc + dc, nr = cr + dr;
        if (!this.passable(nc, nr)) continue;
        if (dr && dc && (!this.passable(cc + dc, cr) || !this.passable(cc, cr + dr))) continue;
        const ni = nr * W + nc; if (closed[ni]) continue;
        const step = (dr && dc ? 1.414 : 1) * (this.cost[this.terrain[cr][cc]] + this.cost[this.terrain[nr][nc]]) / 2;
        const ng = g[cur] + step;
        if (ng < g[ni]) { g[ni] = ng; from[ni] = cur; heap.push(ni, ng + h(ni)); }
      }
    }
    if (!found) return null;
    const path = []; let i = goal;
    while (i !== start && i !== -1) { path.push([i % W + 0.5, ((i / W) | 0) + 0.5]); i = from[i]; }
    path.reverse();
    if (path.length) { path[path.length - 1] = this.passable(Math.floor(tx), Math.floor(ty)) ? [tx, ty] : path[path.length - 1]; }
    return path;
  }

  // ---------- komennot ----------
  command(team, msg) {
    if (this.winner) return;
    if (msg.t === 'train') return this._train(team, msg.type);
    const ids = Array.isArray(msg.ids) ? msg.ids : [];
    const units = ids.map(id => this.units.get(id)).filter(u => u && u.owner === team);
    if (!units.length) return;
    if (msg.t === 'stop') { for (const u of units) if (u.stun <= 0 && u.state !== 'tobar') { u.state = 'idle'; u.path = null; u.target = null; } return; }
    if (msg.t !== 'order') return;
    const x = +msg.x, y = +msg.y; if (!isFinite(x) || !isFinite(y)) return;
    // mitä klikkauksen alla?
    let enemy = null, ed = 0.7;
    for (const u of this.units.values()) if (u.owner !== team) { const d = Math.hypot(u.x - x, u.y - (y + 0.15)); if (d < ed) { ed = d; enemy = u; } }
    const bld = this.buildings.find(b => x >= b.col && x < b.col + 2 && y >= b.row && y < b.row + 2);
    let can = null, cd = 0.8;
    for (const c of this.cans.values()) { const d = Math.hypot(c.x - x, c.y - y); if (d < cd) { cd = d; can = c; } }
    const dests = this._spreadTargets(x, y, units.length);
    units.forEach((u, i) => {
      if (u.stun > 0 || u.state === 'tobar') return;
      const ut = UNIT_TYPES[u.type];
      u.target = null; u.path = null; u.repath = 0;
      if (enemy && ut.ase) { u.state = 'attack'; u.target = { unit: enemy.id }; return; }
      if (bld && bld.tyyppi === 'paamaja' && bld.owner !== team && ut.ase) { u.state = 'attack'; u.target = { b: bld.id }; return; }
      if (u.type === 'tolkkijussi' && bld && bld.owner === team && (bld.tyyppi === 'kmarket' || bld.tyyppi === 'paamaja') && u.carry > 0) { u.state = 'return'; u.target = { b: bld.id }; return; }
      if (ut.kantaa > 0 && can && (u.type === 'tolkkijussi' || u.carry < ut.kantaa)) { u.state = 'collect'; u.target = { can: can.id }; u.home = [can.x, can.y]; return; }
      const d = bld ? this._spreadTargets(bld.x, bld.y + 1.2, units.length)[i] : dests[i];
      u.state = 'move'; u.path = this.findPath(u.x, u.y, d[0], d[1]);
      if (!u.path) u.state = 'idle';
    });
  }

  _spreadTargets(x, y, n) {
    const out = []; const c0 = Math.floor(x), r0 = Math.floor(y);
    for (let rad = 0; rad < 8 && out.length < n; rad++)
      for (let dr = -rad; dr <= rad && out.length < n; dr++) for (let dc = -rad; dc <= rad && out.length < n; dc++) {
        if (Math.max(Math.abs(dr), Math.abs(dc)) !== rad) continue;
        if (this.passable(c0 + dc, r0 + dr)) out.push(rad === 0 && this.passable(c0, r0) ? [x, y] : [c0 + dc + 0.5, r0 + dr + 0.5]);
      }
    while (out.length < n) out.push([x, y]);
    return out;
  }

  _train(team, type) {
    const t = UNIT_TYPES[type]; const p = this.players[team];
    if (!t || p.money < t.hinta || p.queue.length >= 5) return;
    p.money -= t.hinta; p.queue.push({ type, left: t.aika, total: t.aika });
  }

  // ---------- simulaatio ----------
  ownedBonus(team, name) { return this.buildings.some(b => b.owner === team && b.bonus === name); }
  nearOwned(team, u, name, r = 4) { return this.buildings.some(b => b.owner === team && b.bonus === name && Math.hypot(b.x - u.x, b.y - u.y) <= r); }

  step() {
    if (this.winner) return;
    const dt = TICK; this.time += dt; this.tick++;
    // tuotanto
    for (const team of [1, 2]) {
      const p = this.players[team];
      if (p.queue.length) { const q = p.queue[0]; q.left -= dt; if (q.left <= 0) { p.queue.shift(); const h = this.hq(team); if (h) { const u = this._spawnUnitNear(team, q.type, h.x, h.y + 1.5); this.events.push({ e: 'valmis', owner: team, type: q.type, id: u.id }); } } }
      let income = 0;
      for (const b of this.buildings) if (b.owner === team) {
        if (b.bonus === 'PERUNAPELTO') income += 1;
        else if (['TIEDUSTELUKESKUS', 'HUOLTOVARIKKO', 'ROMUTARVIKEVARASTO', 'POLTTOAINEVARASTO', 'KAASUVARASTO'].includes(b.bonus)) income += 0.5;
      }
      p.money += income * dt;
    }
    // tölkkien uusiutuminen
    if (this.tick % 150 === 0 && this.cans.size < 45) this._spawnCans(2);

    for (const u of [...this.units.values()]) this._stepUnit(u, dt);
    this._separate();
    this._stepCapture(dt);
  }

  _speed(u) {
    let s = UNIT_TYPES[u.type].nopeus;
    if (u.k >= 60) s *= 0.8;
    if (this.ownedBonus(u.owner, 'KARKKIKAIVOS')) s *= 1.15;
    return s / Math.max(0.4, this.costAt(u.x, u.y));
  }

  _moveAlong(u, dt) {
    if (!u.path || !u.path.length) return true;
    let dist = this._speed(u) * dt;
    while (dist > 0 && u.path.length) {
      const [px, py] = u.path[0];
      const dx = px - u.x, dy = py - u.y, d = Math.hypot(dx, dy);
      if (dx) u.dir = dx > 0 ? 1 : -1;
      if (d <= dist) { u.x = px; u.y = py; u.path.shift(); dist -= d; }
      else { u.x += dx / d * dist; u.y += dy / d * dist; dist = 0; }
    }
    return !u.path.length;
  }

  _goTo(u, x, y, dt) {
    u.repath -= dt;
    if (!u.path || u.repath <= 0) { u.path = this.findPath(u.x, u.y, x, y); u.repath = 1.5; }
    if (!u.path) return false;
    this._moveAlong(u, dt);
    return true;
  }

  _stepUnit(u, dt) {
    const ut = UNIT_TYPES[u.type];
    // --- kännimittari ---
    let dk = ut.juonti;
    if (this.nearOwned(u.owner, u, 'KALJA-VARASTO')) dk += 4;
    const h = this.hq(u.owner);
    if (h && Math.hypot(h.x - u.x, h.y - u.y) < 4) dk -= 1.5;
    if (this.nearOwned(u.owner, u, 'LÄÄKINTÄASEMA')) { dk -= 5; u.hp = Math.min(u.maxhp, u.hp + 5 * dt); }
    if (this.ownedBonus(u.owner, 'PIZZATEHDAS')) u.hp = Math.min(u.maxhp, u.hp + 0.5 * dt);
    u.k = Math.max(0, Math.min(100, u.k + dk * dt));
    if (u.stun > 0) { u.stun -= dt * (this.ownedBonus(u.owner, 'KAHVILÄHDE') ? 2 : 1); if (u.stun <= 0) { u.state = 'idle'; u.path = null; } return; }
    if (u.k >= 85 && this.tick % 10 === 0 && this.rand() < 0.05) {
      const r = this.rand();
      if (r < 0.15) { this.units.delete(u.id); this._dropCans(u.x, u.y, u.carry); this.events.push({ e: 'kotiin', id: u.id, owner: u.owner, type: u.type, x: u.x, y: u.y }); return; }
      else if (r < 0.5) { u.stun = 8; u.k -= 30; u.state = 'sammunut'; u.path = null; this.events.push({ e: 'sammui', id: u.id, owner: u.owner, x: u.x, y: u.y }); return; }
      else if (r < 0.75 && ut.ase) { u.omiin = true; this.events.push({ e: 'omiin', id: u.id, owner: u.owner, x: u.x, y: u.y }); }
      else {
        const bar = this.buildings.filter(b => b.bonus === 'KALJA-VARASTO').sort((a, b) => Math.hypot(a.x - u.x, a.y - u.y) - Math.hypot(b.x - u.x, b.y - u.y))[0];
        if (bar) { u.state = 'tobar'; u.target = { b: bar.id }; u.path = null; u.repath = 0; this.events.push({ e: 'baariin', id: u.id, owner: u.owner, x: u.x, y: u.y }); }
      }
    }
    if (u.cd > 0) u.cd -= dt;

    // friendly fire
    if (u.omiin && ut.ase && u.cd <= 0) {
      const f = this._nearestUnit(u, ut.ase.kantama, x => x.owner === u.owner && x !== u);
      u.omiin = false;
      if (f) { this._shoot(u, f); return; }
    }

    switch (u.state) {
      case 'idle': case 'sammunut': {
        u.state = 'idle';
        if (ut.ase) { const e = this._nearestUnit(u, VISION, x => x.owner !== u.owner); if (e) { u.state = 'attack'; u.target = { unit: e.id, auto: true }; } }
        break;
      }
      case 'move': if (this._moveAlong(u, dt)) { u.state = 'idle'; u.path = null; } break;
      case 'tobar': {
        const b = this.buildings.find(b => b.id === u.target.b);
        if (Math.hypot(b.x - u.x, b.y + 1 - u.y) < 1.5) { u.state = 'idle'; u.path = null; u.k = Math.min(100, u.k + 10); }
        else this._goTo(u, b.x, b.y + 1.2, dt) || (u.state = 'idle');
        break;
      }
      case 'attack': {
        let tx, ty, tgtU = null, tgtB = null;
        if (u.target.unit) { tgtU = this.units.get(u.target.unit); if (!tgtU) { u.state = 'idle'; u.path = null; break; } tx = tgtU.x; ty = tgtU.y; }
        else { tgtB = this.buildings.find(b => b.id === u.target.b); if (!tgtB || tgtB.owner === u.owner || tgtB.hp <= 0) { u.state = 'idle'; break; } tx = tgtB.x; ty = tgtB.y; }
        const range = ut.ase.kantama + (tgtB ? 1.4 : 0);
        const d = Math.hypot(tx - u.x, ty - u.y);
        if (u.target.auto && d > VISION + 2) { u.state = 'idle'; u.path = null; break; }
        if (d <= range) { u.path = null; if (tx !== u.x) u.dir = tx > u.x ? 1 : -1; if (u.cd <= 0) this._shoot(u, tgtU, tgtB); }
        else if (!this._goTo(u, tx, ty, dt)) u.state = 'idle';
        break;
      }
      case 'collect': {
        if (u.carry >= ut.kantaa) { u.state = 'return'; u.target = null; u.path = null; break; }
        let c = this.cans.get(u.target && u.target.can);
        if (!c) {
          // seuraava kasa läheltä
          let best = null, bd = 8;
          for (const cc of this.cans.values()) { const d = Math.hypot(cc.x - u.x, cc.y - u.y); if (d < bd) { bd = d; best = cc; } }
          if (best) { u.target = { can: best.id }; u.path = null; c = best; }
          else { u.state = u.carry > 0 ? 'return' : 'idle'; u.path = null; break; }
        }
        if (Math.hypot(c.x - u.x, c.y - u.y) < 0.6) {
          u.path = null; u.collectT += dt;
          if (u.collectT >= 0.4) { u.collectT = 0; c.n--; u.carry++; this.events.push({ e: 'kilina', x: c.x, y: c.y, owner: u.owner }); if (c.n <= 0) this.cans.delete(c.id); }
        } else this._goTo(u, c.x, c.y, dt) || (u.state = 'idle');
        break;
      }
      case 'return': {
        let b = u.target && u.target.b ? this.buildings.find(x => x.id === u.target.b && x.owner === u.owner) : null;
        if (!b) {
          const opts = this.buildings.filter(x => x.owner === u.owner && x.tyyppi === 'kmarket');
          if (!opts.length && h) opts.push(h); // hätävara: päämaja ottaa tölkit puoleen hintaan
          b = opts.sort((a, c) => Math.hypot(a.x - u.x, a.y - u.y) - Math.hypot(c.x - u.x, c.y - u.y))[0];
          if (!b) { u.state = 'idle'; break; }
          u.target = { b: b.id }; u.path = null;
        }
        if (Math.hypot(b.x - u.x, b.y - u.y) < 2.6) {
          const val = u.carry * CAN_VALUE * (b.tyyppi === 'kmarket' ? 1 : 0.5);
          this.players[u.owner].money += val;
          this.events.push({ e: 'pantti', owner: u.owner, x: b.x, y: b.y, n: u.carry, raha: val });
          u.carry = 0; u.path = null;
          if (u.home) { u.state = 'collect'; u.target = { can: -1 }; const p = u.home; u.path = this.findPath(u.x, u.y, p[0], p[1]); u.state = 'gohome'; }
          else u.state = 'idle';
        } else this._goTo(u, b.x, b.y + 1.2, dt) || (u.state = 'idle');
        break;
      }
      case 'gohome': { // takaisin keräyspaikalle
        if (this._moveAlong(u, dt) || Math.hypot(u.home[0] - u.x, u.home[1] - u.y) < 2) { u.state = 'collect'; u.target = { can: -1 }; u.path = null; }
        break;
      }
    }
  }

  _nearestUnit(u, r, pred) {
    let best = null, bd = r;
    for (const o of this.units.values()) { if (!pred(o)) continue; const d = Math.hypot(o.x - u.x, o.y - u.y); if (d <= bd) { bd = d; best = o; } }
    return best;
  }

  _shoot(u, tgtU, tgtB) {
    const w = UNIT_TYPES[u.type].ase;
    u.cd = w.tauko;
    let dmg = w.vahinko, acc = 0.85;
    if (u.k >= 20 && u.k < 60) { dmg *= 1.25; acc += 0.07; }
    else if (u.k >= 60) { dmg *= 1.1; acc -= 0.15 + (u.k - 60) / 200; }
    if (this.nearOwned(u.owner, u, 'KALJA-VARASTO')) dmg *= 1.15;
    const tx = tgtU ? tgtU.x : tgtB.x, ty = tgtU ? tgtU.y : tgtB.y;
    const hit = tgtB ? true : this.rand() < acc;
    this.events.push({ e: 'ammus', w: w.aani, x: u.x, y: u.y, tx, ty, hit, owner: u.owner });
    if (!hit) return;
    if (tgtB) {
      tgtB.hp -= dmg;
      if (tgtB.hp <= 0) { tgtB.hp = 0; this.events.push({ e: 'tuhoutui', b: tgtB.id, x: tgtB.x, y: tgtB.y }); if (tgtB.tyyppi === 'paamaja') { this.winner = u.owner; this.events.push({ e: 'voitto', winner: u.owner }); } }
      return;
    }
    if (this.nearOwned(tgtU.owner, tgtU, 'LIHAPULLALINNAKE')) dmg *= 0.5;
    tgtU.hp -= dmg;
    if (tgtU.hp <= 0) {
      this.units.delete(tgtU.id);
      this._dropCans(tgtU.x, tgtU.y, 2 + tgtU.carry);
      this.events.push({ e: 'kuoli', id: tgtU.id, owner: tgtU.owner, type: tgtU.type, x: tgtU.x, y: tgtU.y });
      // mopopoika varastaa tölkkikuorman
      if (u.type === 'mopopoika' && tgtU.carry > 0) { /* tölkit putoavat maahan, mopo voi kerätä */ }
    } else if (tgtU.state === 'idle' && UNIT_TYPES[tgtU.type].ase) { tgtU.state = 'attack'; tgtU.target = { unit: u.id, auto: true }; }
  }

  _separate() {
    const arr = [...this.units.values()];
    for (let i = 0; i < arr.length; i++) for (let j = i + 1; j < arr.length; j++) {
      const a = arr[i], b = arr[j]; const dx = b.x - a.x, dy = b.y - a.y; const d = Math.hypot(dx, dy);
      if (d < 0.4) {
        const push = (0.4 - d) / 2 + 0.001; const nx = d ? dx / d : (a.id % 2 ? 1 : -1), ny = d ? dy / d : 0;
        const ax = a.x - nx * push, ay = a.y - ny * push, bx = b.x + nx * push, by = b.y + ny * push;
        if (this.passable(Math.floor(ax), Math.floor(ay))) { a.x = ax; a.y = ay; }
        if (this.passable(Math.floor(bx), Math.floor(by))) { b.x = bx; b.y = by; }
      }
    }
  }

  _stepCapture(dt) {
    for (const b of this.buildings) {
      if (b.tyyppi === 'paamaja') continue;
      const n = { 1: 0, 2: 0 };
      for (const u of this.units.values()) if (u.stun <= 0 && Math.hypot(u.x - b.x, u.y - b.y) <= CAPTURE_RADIUS) n[u.owner]++;
      const present = [1, 2].filter(t => n[t] > 0);
      if (present.length === 1 && present[0] !== b.owner) {
        const t = present[0];
        if (b.cap.team !== t) { b.cap.team = t; b.cap.p = 0; }
        b.cap.p += dt / CAPTURE_TIME * Math.min(3, n[t]);
        if (b.cap.p >= 1) {
          const old = b.owner; b.owner = t; b.cap = { team: 0, p: 0 };
          this.events.push({ e: 'valtaus', b: b.id, owner: t, old, x: b.x, y: b.y });
        }
      } else if (b.cap.p > 0 && present.length !== 1) { b.cap.p = Math.max(0, b.cap.p - dt / CAPTURE_TIME / 2); if (!b.cap.p) b.cap.team = 0; }
      else if (present.length === 1 && present[0] === b.owner) { b.cap = { team: 0, p: 0 }; }
    }
  }

  // ---------- verkko ----------
  initData() {
    return {
      cols: this.W, rows: this.H, terrain: this.terrain, terrainTypes: this.map.terrain_types, attribution: this.map.attribution,
      buildings: this.buildings.map(b => ({ id: b.id, tyyppi: b.tyyppi, nimi: b.nimi, osm: b.osm, col: b.col, row: b.row, kuvaus: b.kuvaus, maxhp: b.maxhp || 0, owner: b.owner })),
      unitTypes: UNIT_TYPES, canValue: CAN_VALUE,
    };
  }
  snapshot() {
    const r1 = v => Math.round(v * 100) / 100;
    const s = {
      t: 's', tick: this.tick, time: r1(this.time), winner: this.winner,
      u: [...this.units.values()].map(u => [u.id, u.type, u.owner, r1(u.x), r1(u.y), Math.ceil(u.hp), Math.round(u.k), u.carry, u.stun > 0 ? 'sammunut' : u.state, u.dir]),
      c: [...this.cans.values()].map(c => [c.id, r1(c.x), r1(c.y), c.n]),
      b: this.buildings.map(b => [b.id, b.owner, b.cap.team, r1(b.cap.p), Math.ceil(b.hp || 0)]),
      p: { 1: { money: Math.floor(this.players[1].money), queue: this.players[1].queue.map(q => [q.type, r1(q.left), q.total]) },
           2: { money: Math.floor(this.players[2].money), queue: this.players[2].queue.map(q => [q.type, r1(q.left), q.total]) } },
      ev: this.events,
    };
    this.events = [];
    return s;
  }
}

module.exports = { Game, UNIT_TYPES, TICK };
