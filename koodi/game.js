'use strict';
// Lähiösota: Etelä-Tampere – pelilogiikka (palvelin on auktoriteetti).
// Koordinaatit ruutuina: x = sarake, y = rivi (liukuluku, ruudun keskipiste = c+0.5).

const TICK = 0.1; // s

// puoli: 0 = molemmat, 1 = vain Multisilta, 2 = vain Peltolammi. luokka: jalka | ajoneuvo
const PUUKKO = { nimi: 'Puukko', vahinko: 12, kantama: 1.0, tauko: 0.8, aani: 'puukko' };
const UNIT_TYPES = {
  tolkkijussi:   { nimi: 'Tölkkijussi', puoli: 0, luokka: 'jalka', nappi: 'z', hinta: 50, aika: 3, hp: 60, nopeus: 1.6, kantaa: 8, ase: null, juonti: 0.25 },
  lahiojermu:    { nimi: 'Lähiöjermu', puoli: 0, luokka: 'jalka', nappi: 'x', hinta: 80, aika: 4, hp: 100, nopeus: 1.8, kantaa: 0, molotovi: true, puukko: true,
                   ase: { nimi: 'Pystykorva (RK-62)', vahinko: 9, kantama: 4, tauko: 1.0, aani: 'rk62' }, juonti: 0.55 },
  mopopoika:     { nimi: 'Mopopoika', puoli: 0, luokka: 'jalka', nappi: 'c', hinta: 120, aika: 5, hp: 70, nopeus: 3.4, kantaa: 4, molotovi: true, puukko: true,
                   ase: { nimi: 'Jatimatic', vahinko: 4, kantama: 3, tauko: 0.45, aani: 'jatimatic' }, juonti: 0.35 },
  grillimestari: { nimi: 'Grillimestari', puoli: 0, luokka: 'jalka', nappi: 'b', hinta: 150, aika: 6, hp: 220, nopeus: 0.7, kantaa: 0,
                   ase: { nimi: 'Pihagrilli (makkara + käry, hidastaa)', vahinko: 5, kantama: 3.5, tauko: 0.8, hidastaa: 2.5, aani: 'grilli' }, juonti: 0.4,
                   kuvaus: 'Puolustuspiste: sylkee makkaraa ja käryä, hidastaa vihollisia. Lähes paikallaan.' },
  parvekeampuja: { nimi: 'Kerrostalon parvekeampuja', puoli: 1, luokka: 'jalka', nappi: 't', hinta: 180, aika: 7, hp: 60, nopeus: 0.8, kantaa: 0,
                   ase: { nimi: 'Parvekekivääri (tykistö)', vahinko: 28, kantama: 9, minimi: 2.5, tauko: 4, roiske: 1.3, paikallaan: true, aani: 'parveke' }, juonti: 0.3,
                   kuvaus: 'Kauas kantava tykistö, ampuu vain paikallaan. Ei osu aivan lähelle.' },
  mummo:         { nimi: 'Mummo rollaattorilla', puoli: 1, luokka: 'jalka', nappi: 'y', hinta: 220, aika: 8, hp: 500, nopeus: 0.9, kantaa: 0, panssari: 0.5,
                   ase: { nimi: 'Rollaattori', vahinko: 10, kantama: 1.1, tauko: 1.2, aani: 'puukko' }, juonti: 0.05,
                   kuvaus: 'Hidas, lähes tuhoutumaton tankki. Ottaa puolet vahingosta, ei juuri juo.' },
  isa_trimmeri:  { nimi: 'Isä trimmerin kanssa', puoli: 2, luokka: 'jalka', nappi: 't', hinta: 130, aika: 5, hp: 150, nopeus: 1.9, kantaa: 0, metsassa: true, molotovi: true,
                   ase: { nimi: 'Trimmeri', vahinko: 14, kantama: 1.1, tauko: 0.6, aani: 'trimmeri' }, juonti: 0.45,
                   kuvaus: 'Lähitaistelija, raivaa pusikot: liikkuu metsässä kuin tiellä.' },
  volvo:         { nimi: 'Tuunattu Volvo', puoli: 2, luokka: 'ajoneuvo', nappi: 'y', hinta: 300, aika: 9, hp: 350, nopeus: 3.0, kantaa: 0, kyyti: 4, jyraa: 30, ase: null, juonti: 0.2,
                   kuvaus: 'Kuljettaa 4 jalkaväkeä ja jyrää vihollisen jalkaväkeä. Bensa on kallista.' },
  dnepr:         { nimi: 'Dnepr-sivuvaunupyörä', puoli: 0, luokka: 'ajoneuvo', nappi: 'f', hinta: 260, aika: 8, hp: 170, nopeus: 3.8, kantaa: 0,
                   ase: { nimi: 'Emma-konekivääri (sivuvaunussa)', vahinko: 6, kantama: 4.5, tauko: 0.25, aani: 'emma' }, juonti: 0.25 },
  monkija:       { nimi: 'Mönkijä', puoli: 0, luokka: 'ajoneuvo', nappi: 'g', hinta: 160, aika: 6, hp: 110, nopeus: 3.6, kantaa: 6, maastossa: true,
                   ase: { nimi: 'Suomi-konepistooli', vahinko: 5, kantama: 3, tauko: 0.35, aani: 'suomikp' }, juonti: 0.25,
                   kuvaus: 'Kevyt ja nopea maastossa. Voi kerätä 6 tölkkiä.' },
  lada:          { nimi: 'Lada', puoli: 0, luokka: 'ajoneuvo', nappi: 'j', hinta: 120, aika: 6, hp: 200, nopeus: 3.0, kantaa: 0, kyyti: 3, ase: null, juonti: 0.25,
                   kuvaus: 'Halpa kuljetus kolmelle jalkaväelle.' },
  // puolueettomat olennot (owner 3), ei koulutettavissa
  peikko:        { nimi: 'Metsäpeikko', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 240, nopeus: 1.2, kantaa: 99, metsassa: true, juonti: 0,
                   ase: { nimi: 'Kivi', vahinko: 14, kantama: 4.5, tauko: 2.2, aani: 'kivi' } },
  vesihiisi:     { nimi: 'Vesihiisi', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 320, nopeus: 0, kantaa: 0, juonti: 0,
                   ase: { nimi: 'Kourat', vahinko: 20, kantama: 3, tauko: 1.3, aani: 'hiisi' } },
  // V4: puolueettomat NPC:t (owner 0 = ei hyökättävissä; Caesar owner 3)
  pullomummo:    { nimi: 'Pullonkerääjämummo', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 50, nopeus: 1.0, kantaa: 999, juonti: 0, ase: null },
  hemuli:        { nimi: 'Hemuli', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 80, nopeus: 0.8, kantaa: 0, metsassa: true, juonti: 0, ase: null },
  hemuli_caesar: { nimi: 'Puolijumala Caesar', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 400, nopeus: 1.3, kantaa: 0, metsassa: true, juonti: 0,
                   ase: { nimi: 'Jumalallinen salama', vahinko: 18, kantama: 3.5, tauko: 1.5, aani: 'salama' } },
  vana:          { nimi: 'Vänä', puoli: 3, olento: true, luokka: 'jalka', hinta: 0, aika: 0, hp: 150, nopeus: 1.2, kantaa: 0, juonti: 0,
                   ase: { nimi: 'Jalkapallopotku', vahinko: 50, kantama: 5, tauko: 4, aani: 'pallo' } },
};
const ESINEET = [['kypärä', 'kypara'], ['lenkkarit', 'lenkkarit'], ['tanssimatto', 0], ['kukkaruukku', 0], ['VHS-kasetti (Uuno Turhapuro)', 0], ['posliinikoira', 0]];
const OLENNOT = {
  peikot:    { nimi: 'Metsäpeikot', koskee: 0, teksti: 'Vihaisia peikkoja metsässä! Ne heittelevät kiviä kaikkia kohti ja varastavat tölkkejä. Kaatunut peikko pudottaa tölkkejä.' },
  vesihiisi: { nimi: 'Vesihiisi', koskee: 0, teksti: 'Vesihiisi nousi! Se iskee kaikkiin alle 3 ruudun päässä rannasta. Ratasilta ja rannat ovat vaarallisia.' },
};
const MAX_PEIKOT = 3;
const MOLOTOVI = { hinta: 15, kantama: 5, sade: 1.4, kesto: 5, vahinko: 9, tauko: 6 };
// koskee: 0 = molemmat, 1 = Multisilta, 2 = Peltolammi
const TAPAHTUMAT = {
  poliisipartio:         { nimi: 'Poliisipartio', kesto: 40, koskee: 0, teksti: 'Humalaiset (kännit yli 60 %) viedään putkaan 40 s ajan!', varoitus: 'Sireenit kuuluvat jo kaukaa...' },
  alkon_alennus:         { nimi: 'Alkon alennusmyynti', kesto: 35, koskee: 0, teksti: 'Kaikille +15 % känniä, ja osa jermuista jonottaa Alkoon 35 s.', varoitus: 'Alkon ikkunaan teipataan ALE-lappuja...' },
  sadekuuro:             { nimi: 'Sadekuuro', kesto: 45, koskee: 0, teksti: 'Kaikki liikkuvat hitaammin ja molotovit eivät syty 45 s ajan.', varoitus: 'Sadepilviä näkyvissä...' },
  panttiautomaatti_rikki:{ nimi: 'Panttiautomaatti rikki', kesto: 45, koskee: 0, teksti: 'Yhden K-Marketin pullonpalautus on rikki 45 s.', varoitus: 'Panttiautomaatti pitää outoa ääntä...' },
  pihakirppis:           { nimi: 'Pihakirppis', kesto: 20, koskee: 0, teksti: 'Kentän keskelle ilmestyi isoja tölkkikasoja – nopeat syövät hitaat!', varoitus: 'Joku kantaa pöytiä pihalle...' },
  saunailta:             { nimi: 'Saunailta', kesto: 25, koskee: 2, teksti: 'Peltolammi: 30 % jalkaväestä löylyissä 25 s, palaavat selvinä ja +30 % vahingolla.', varoitus: 'Peltolammilla lämpiää sauna...' },
  taloyhtion_kokous:     { nimi: 'Taloyhtiön kokous', kesto: 20, koskee: 1, teksti: 'Multisilta: 30 % jalkaväestä jumissa kokouksessa 20 s.', varoitus: 'Multisillan rappukäytävään ilmestyi kokouskutsu...' },
  bussi3_myohassa:       { nimi: 'Bussi 3 myöhässä', kesto: 40, koskee: 0, teksti: 'Koulutus kestää tuplasti 40 s ajan.', varoitus: 'Pysäkillä alkaa olla jonoa...' },
  lumimyrsky:            { nimi: 'Lumimyrsky', kesto: 35, koskee: 0, teksti: 'Kaikki hidastuvat (mönkijä vähemmän), Lada jumittaa lumessa 35 s.', varoitus: 'Taivas muuttuu harmaaksi ja tuuli yltyy...' },
  kesajuhlat:            { nimi: 'Kesäjuhlat', kesto: 30, koskee: 0, teksti: 'Aselepo 30 s: kukaan ei ammu eikä valtaa, ja pantit ovat tuplasti arvokkaampia!', varoitus: 'Joku virittää grilliä ja kaiuttimia...' },
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
    this.fires = [];        // molotovien liekit
    this.puddles = [];      // laattalätät
    this.away = [];         // saunassa / taloyhtiön kokouksessa olevat
    this.npcs = new Map();  // poliisiauto
    this.tap = null;        // käynnissä oleva satunnaistapahtuma
    this.nextTap = opts.firstEvent || 90;
    this.tapOrder = [];
    this.nextPeikko = opts.firstPeikko || 150;
    this.nextHiisi = opts.firstHiisi || 200;
    this.hiisi = null;      // { x, y, phase: 'kuplat'|'ylhaalla', t, id }
    this._placeBuildings();
    this._findWater();
    this._spawnStart();
    this._spawnCans(45);
    this._spawnNpcsV4();
  }

  _findWater() {
    // rantavesiruudut (vesi, jonka vieressä kulkukelpoinen ruutu) – järvet/lammet, ei pieniä ojia
    const seen = new Set(); this.shore = [];
    for (let r = 0; r < this.H; r++) for (let c = 0; c < this.W; c++) {
      if (this.terrain[r][c] !== 2 || seen.has(r * 1000 + c)) continue;
      const comp = [], st = [[c, r]]; seen.add(r * 1000 + c);
      while (st.length) { const [x, y] = st.pop(); comp.push([x, y]);
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const nx = x + dx, ny = y + dy; if (nx < 0 || ny < 0 || nx >= this.W || ny >= this.H || this.terrain[ny][nx] !== 2 || seen.has(ny * 1000 + nx)) continue; seen.add(ny * 1000 + nx); st.push([nx, ny]); } }
      if (comp.length < 8) continue;
      for (const [x, y] of comp) if ([[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => this.passable(x + dx, y + dy))) this.shore.push([x, y]);
    }
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
    // V4: kerrostalot kartan rakennusruuduista (2x2 täysin rakennusta), tapahtumarakennukset kulkukelpoisille ruuduille
    const W2 = this.W / 2, H2 = this.H / 2;
    const fit = (c, r, ok) => { for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) { if (used.has((r + i) * 1000 + c + j) || !ok(c + j, r + i)) return false; } return true; };
    const nearest = (tx, ty, ok) => { let best = null, bd = 1e9; for (let r = 0; r < this.H - 1; r++) for (let c = 0; c < this.W - 1; c++) { const d = (c - tx) ** 2 + (r - ty) ** 2; if (d < bd && fit(c, r, ok)) { bd = d; best = [c, r]; } } if (best) for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) used.add((best[1] + i) * 1000 + best[0] + j); return best; };
    const isB = (c, r) => this.terrain[r][c] === 6, isP = (c, r) => this.passable(c, r);
    for (const [tx, ty] of [[W2 + 6, H2 - 2], [W2 - 4, H2 + 6], [W2 + 4, H2 - 12], [W2 - 6, H2 + 14]]) {
      const p = nearest(tx, ty, isB); if (!p) continue;
      this.buildings.push({ id: this.nextId++, tyyppi: 'kerrostalo', nimi: 'Kerrostalo', osm: 'Lähiökerrostalo', col: p[0], row: p[1], owner: 0, cap: { team: 0, p: 0 }, sisalla: [], bileT: 0, piiritysT: 0,
        kuvaus: 'Vallattava. Omat jalkaväet sisään (max 6): suojassa ja ampuvat ikkunoista. 4–5 sisällä = kotibileet, 6 = poliisipiiritys!' });
    }
    for (const [tyyppi, nimi, tx, ty, noCap, kuvaus] of [
      ['sauna', 'Sauna', W2 - 2, H2 - 6, true, 'Puolueeton. Saunojat selviävät ja paranevat, mutta eivät puolusta. Yli 25 s löylyissä = sammuu.'],
      ['pihagrilli', 'Pihagrilli', W2 + 2, H2 - 2, false, 'Vallattava. Omat 4 ruudun säteellä humaltuvat puolet hitaammin, mutta käry paljastaa sijainnin ~20 s välein.'],
      ['kirppu', 'Kirpputori', W2 - 6, H2 + 2, true, 'Puolueeton. 3 tölkkiä = satunnainen esine (kypärä, lenkkarit... tai krääsää).']]) {
      const p = nearest(tx, ty, isP); if (!p) continue;
      this.buildings.push({ id: this.nextId++, tyyppi, nimi, osm: nimi, col: p[0], row: p[1], owner: 0, cap: { team: 0, p: 0 }, noCap, kuvaus, grilliT: 20 });
    }
    for (const b of this.buildings) { b.x = b.col + 1; b.y = b.row + 1; }
  }
  _spawnNpcsV4() {
    const m = this._spawnUnitNear(0, 'pullomummo', this.W / 2, this.H / 2); m.ai = 'vaella'; m.aiT = 0;
    const h2 = this.hq(2), h1 = this.hq(1);
    if (h2) { const h = this._spawnUnitNear(0, 'hemuli', h2.x + 7, h2.y + 5); h.home = [h.x, h.y]; h.aiT = 1; h.ai = 'vaella'; }
    const bar = h1 && this.buildings.filter(b => b.bonus === 'KALJA-VARASTO').sort((a, b) => Math.hypot(a.x - h1.x, a.y - h1.y) - Math.hypot(b.x - h1.x, b.y - h1.y))[0];
    if (h1) { const v = this._spawnUnitNear(0, 'vana', h1.x - 6, h1.y - 3); v.home = bar ? [bar.x, bar.y + 1.2] : [v.x, v.y]; v.ai = 'baariin'; v.aiT = 0; }
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
      if (this.passable(c, r) && !this.buildings.some(b => c >= b.col && c < b.col + 2 && r >= b.row - 1 && r < b.row + 2)) spots.push([c, r, (c + 0.5 - x) ** 2 + (r + 0.5 - y) ** 2]);
    spots.sort((a, b) => a[2] - b[2]);
    let pick = spots[0] || this.nearestPassable(x, y, 10);
    for (const s of spots) { let occ = 0; for (const u of this.units.values()) if (Math.floor(u.x) === s[0] && Math.floor(u.y) === s[1]) occ++; if (!occ) { pick = s; break; } }
    const t = UNIT_TYPES[type];
    const u = { id: this.nextId++, type, owner: team, x: pick[0] + 0.5, y: pick[1] + 0.5, hp: t.hp, maxhp: t.hp,
      k: 0, carry: 0, state: 'idle', path: null, target: null, cd: 0, stun: 0, omiin: false, repath: 0, collectT: 0, home: null, dir: 1,
      slow: 0, buff: 0, cargo: [], molocd: 0, jonoT: 0, crush: {} };
    this.units.set(u.id, u);
    return u;
  }

  _spawnStart() {
    for (const team of [1, 2]) {
      const h = this.hq(team);
      for (let i = 0; i < 2; i++) this._spawnUnitNear(team, 'tolkkijussi', h.x, h.y + 1.5);
      for (let i = 0; i < 2; i++) this._spawnUnitNear(team, 'lahiojermu', h.x, h.y + 1.5);
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
    if (!this.passable(Math.floor(x), Math.floor(y))) { x = p[0] + 0.5; y = p[1] + 0.5; }
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
    if (msg.t === 'tyhjenna') { const b = this.buildings.find(x => x.id === msg.b && x.tyyppi === 'kerrostalo' && x.owner === team); if (b) this._evict(b); return; }
    const ids = Array.isArray(msg.ids) ? msg.ids : [];
    const units = ids.map(id => this.units.get(id)).filter(u => u && u.owner === team);
    if (!units.length) return;
    if (msg.t === 'stop') { for (const u of units) if (u.stun <= 0 && u.state !== 'tobar') { u.state = 'idle'; u.path = null; u.target = null; } return; }
    if (msg.t === 'unload') { for (const u of units) this._unload(u); return; }
    if (msg.t === 'molotovi') {
      const x = +msg.x, y = +msg.y; if (!isFinite(x) || !isFinite(y)) return;
      for (const u of units) if (UNIT_TYPES[u.type].molotovi && u.stun <= 0 && u.state !== 'tobar') { u.state = 'molotovi'; u.target = { x, y }; u.path = null; u.repath = 0; }
      return;
    }
    if (msg.t !== 'order') return;
    const x = +msg.x, y = +msg.y; if (!isFinite(x) || !isFinite(y)) return;
    // mitä klikkauksen alla?
    let enemy = null, ed = 0.7;
    let ownVeh = null, vd = 0.8, mummo = null;
    for (const u of this.units.values()) {
      const d = Math.hypot(u.x - x, u.y - (y + 0.15));
      if (u.type === 'pullomummo') { if (d < 0.8) mummo = u; }
      else if (u.owner !== team && u.owner !== 0) { if (d < ed) { ed = d; enemy = u; } }
      else if (u.owner === team && UNIT_TYPES[u.type].kyyti && d < vd) { vd = d; ownVeh = u; }
    }
    const bld = this.buildings.find(b => x >= b.col && x < b.col + 2 && y >= b.row && y < b.row + 2);
    let can = null, cd = 0.8;
    for (const c of this.cans.values()) { const d = Math.hypot(c.x - x, c.y - y); if (d < cd) { cd = d; can = c; } }
    const dests = this._spreadTargets(x, y, units.length);
    units.forEach((u, i) => {
      if (u.stun > 0 || u.state === 'tobar') return;
      const ut = UNIT_TYPES[u.type];
      u.target = null; u.path = null; u.repath = 0;
      if (ownVeh && ownVeh !== u && ut.luokka === 'jalka') { u.state = 'board'; u.target = { unit: ownVeh.id }; return; }
      if (mummo && u.carry > 0) { u.state = 'lahjo'; u.target = { unit: mummo.id }; return; }
      if (bld && ut.luokka === 'jalka' && !ut.olento) {
        if (bld.tyyppi === 'kerrostalo' && bld.owner === team) { u.state = 'talo'; u.target = { b: bld.id }; return; }
        if (bld.tyyppi === 'sauna') { u.state = 'tosauna'; u.target = { b: bld.id }; return; }
      }
      if (bld && bld.tyyppi === 'kirppu' && u.carry >= 3) { u.state = 'kirppu'; u.target = { b: bld.id }; return; }
      if (enemy && ut.ase) { u.state = 'attack'; u.target = { unit: enemy.id }; return; }
      if (enemy && ut.jyraa) { u.state = 'attack'; u.target = { unit: enemy.id }; return; }
      if (bld && bld.tyyppi === 'paamaja' && bld.owner !== team && ut.ase) { u.state = 'attack'; u.target = { b: bld.id }; return; }
      if (ut.kantaa > 0 && bld && bld.owner === team && (bld.tyyppi === 'kmarket' || bld.tyyppi === 'paamaja') && u.carry > 0) { u.state = 'return'; u.target = { b: bld.id }; return; }
      if (ut.kantaa > 0 && can && (u.type === 'tolkkijussi' || u.type === 'monkija' || u.carry < ut.kantaa)) { u.state = 'collect'; u.target = { can: can.id }; u.home = [can.x, can.y]; return; }
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
    if (!t || (t.puoli && t.puoli !== team) || p.queue.length >= 5) return;
    const price = this.price(team, type);
    if (p.money < price) return;
    p.money -= price; p.queue.push({ type, left: t.aika, total: t.aika });
  }

  price(team, type) {
    const t = UNIT_TYPES[type];
    if (t.luokka === 'ajoneuvo' && (this.ownedBonus(team, 'HUOLTOVARIKKO') || this.ownedBonus(team, 'ROMUTARVIKEVARASTO'))) return Math.round(t.hinta * 0.75);
    return t.hinta;
  }
  molotovPrice(team) { return (this.ownedBonus(team, 'POLTTOAINEVARASTO') || this.ownedBonus(team, 'KAASUVARASTO')) ? Math.round(MOLOTOVI.hinta / 2) : MOLOTOVI.hinta; }
  get aselepo() { return this.tap && this.tap.key === 'kesajuhlat'; }
  get sade() { return this.tap && this.tap.key === 'sadekuuro'; }
  isEnemy(a, b) { return b.owner !== 0 && a.owner !== 0 && b.owner !== a.owner; }

  // ---------- simulaatio ----------
  ownedBonus(team, name) { return this.buildings.some(b => b.owner === team && b.bonus === name); }
  nearOwned(team, u, name, r = 4) { return this.buildings.some(b => b.owner === team && b.bonus === name && Math.hypot(b.x - u.x, b.y - u.y) <= r); }

  step() {
    if (this.winner) return;
    const dt = TICK; this.time += dt; this.tick++;
    // tuotanto
    for (const team of [1, 2]) {
      const p = this.players[team];
      if (p.queue.length) { const q = p.queue[0]; q.left -= dt * (this.tap && this.tap.key === 'bussi3_myohassa' ? 0.5 : 1); if (q.left <= 0) { p.queue.shift(); const h = this.hq(team); if (h) { const u = this._spawnUnitNear(team, q.type, h.x, h.y + 1.5); this.events.push({ e: 'valmis', owner: team, type: q.type, id: u.id }); } } }
      let income = 0;
      for (const b of this.buildings) if (b.owner === team) {
        if (b.bonus === 'PERUNAPELTO') income += 1;
        else if (['TIEDUSTELUKESKUS', 'HUOLTOVARIKKO', 'ROMUTARVIKEVARASTO', 'POLTTOAINEVARASTO', 'KAASUVARASTO'].includes(b.bonus)) income += 0.5;
      }
      p.money += income * dt;
    }
    // tölkkien uusiutuminen
    if (this.tick % 150 === 0 && this.cans.size < 45) this._spawnCans(2);

    this._stepEvents(dt);
    this._stepOlennot(dt);
    for (const u of [...this.units.values()]) if (this.units.has(u.id)) { if (UNIT_TYPES[u.type].olento) this._stepOlento(u, dt); else this._stepUnit(u, dt); }
    this._stepFires(dt);
    this._stepPuddles(dt);
    this._stepNpcs(dt);
    this._stepV4Buildings(dt);
    this._separate();
    this._stepCapture(dt);
  }

  _speed(u) {
    const ut = UNIT_TYPES[u.type] || {};
    let s = ut.nopeus || 3.5;
    if (u.k >= 60) s *= 0.8;
    if (u.slow > 0) s *= 0.5;
    if (u.inPuddle) s *= 0.6;
    if (this.sade) s *= 0.8;
    if (this.tap && this.tap.key === 'lumimyrsky') s *= u.type === 'lada' ? 0 : u.type === 'monkija' ? 0.9 : 0.6;
    if (u.esine === 'lenkkarit') s *= 1.2;
    if (u.owner && this.ownedBonus(u.owner, 'KARKKIKAIVOS')) s *= 1.15;
    let c = this.costAt(u.x, u.y);
    const tid = this.terrain[Math.floor(u.y)] && this.terrain[Math.floor(u.y)][Math.floor(u.x)];
    const rough = tid === 1 || tid === 9 || tid === 10; // metsä, suo, kallio
    if (rough && ut.metsassa) c = 1;
    else if (rough && ut.maastossa) c = Math.max(1, c * 0.6);
    else if (rough && ut.luokka === 'ajoneuvo') c *= 1.6;
    return s / Math.max(0.4, c);
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
    if (u.slow > 0) u.slow -= dt;
    if (u.buff > 0) u.buff -= dt;
    if (u.molocd > 0) u.molocd -= dt;
    // --- kännimittari ---
    let dk = ut.juonti;
    if (this.buildings.some(b => b.tyyppi === 'pihagrilli' && b.owner === u.owner && Math.hypot(b.x - u.x, b.y - u.y) <= 4)) dk *= 0.5;
    if (this.nearOwned(u.owner, u, 'KALJA-VARASTO')) dk += 4;
    const h = this.hq(u.owner);
    if (h && Math.hypot(h.x - u.x, h.y - u.y) < 4) dk -= 1.5;
    if (this.nearOwned(u.owner, u, 'LÄÄKINTÄASEMA')) { dk -= 5; u.hp = Math.min(u.maxhp, u.hp + 5 * dt); }
    if (this.ownedBonus(u.owner, 'PIZZATEHDAS')) u.hp = Math.min(u.maxhp, u.hp + 0.5 * dt);
    u.k = Math.max(0, Math.min(100, u.k + dk * dt));
    { // humalatilan muutokset -> puhekuplat asiakkaalle
      const tila = u.k >= 85 ? 3 : u.k >= 60 ? 2 : u.k >= 20 ? 1 : 0;
      if (u.ktila === undefined) u.ktila = tila;
      if (tila > u.ktila) {
        const laatta = tila === 3 && UNIT_TYPES[u.type].luokka === 'jalka';
        this.events.push({ e: 'humala', id: u.id, owner: u.owner, tila: laatta ? 'laatta' : tila, x: u.x, y: u.y });
        if (laatta) this._puke(u);
      }
      u.ktila = tila;
      if (tila >= 3 && this.tick % 50 === u.id % 50 && this.rand() < (this.tekstariP || 0.04)) { // kännitekstari exälle
        this.events.push({ e: 'tekstari', id: u.id, owner: u.owner, x: u.x, y: u.y });
        this._paljasta(u.owner, [...this.units.values()].filter(o => o.owner === u.owner), 8, 'kännitekstari');
      }
      if (tila >= 2 && this.tick % 40 === u.id % 40 && this.rand() < 0.12) this.events.push({ e: 'humala', id: u.id, owner: u.owner, tila: 'hik', x: u.x, y: u.y });
    }
    if (u.stun > 0) { u.stun -= dt * (this.ownedBonus(u.owner, 'KAHVILÄHDE') ? 2 : 1); if (u.stun <= 0) { u.state = 'idle'; u.path = null; } return; }
    if (u.k >= 85 && this.tick % 10 === 0 && this.rand() < 0.05) {
      const r = this.rand();
      if (r < 0.15) { this._remove(u); this._dropCans(u.x, u.y, u.carry); this.events.push({ e: 'kotiin', id: u.id, owner: u.owner, type: u.type, x: u.x, y: u.y }); return; }
      else if (r < 0.5) { u.stun = 8; u.k -= 30; u.state = 'sammunut'; u.path = null; this.events.push({ e: 'sammui', id: u.id, owner: u.owner, x: u.x, y: u.y }); return; }
      else if (r < 0.75 && ut.ase) { u.omiin = true; this.events.push({ e: 'omiin', id: u.id, owner: u.owner, x: u.x, y: u.y }); }
      else {
        const bar = this.buildings.filter(b => b.bonus === 'KALJA-VARASTO').sort((a, b) => Math.hypot(a.x - u.x, a.y - u.y) - Math.hypot(b.x - u.x, b.y - u.y))[0];
        if (bar) { u.state = 'tobar'; u.target = { b: bar.id }; u.path = null; u.repath = 0; this.events.push({ e: 'baariin', id: u.id, owner: u.owner, x: u.x, y: u.y }); }
      }
    }
    if (u.cd > 0) u.cd -= dt;

    // friendly fire
    if (u.omiin && ut.ase && u.cd <= 0 && !this.aselepo) {
      const f = this._nearestUnit(u, ut.ase.kantama, x => x.owner === u.owner && x !== u);
      u.omiin = false;
      if (f) { this._shoot(u, f); return; }
    }

    switch (u.state) {
      case 'idle': case 'sammunut': {
        u.state = 'idle';
        if (ut.ase && !this.aselepo) { const e = this._nearestUnit(u, ut.ase.kantama > VISION ? ut.ase.kantama : VISION, x => this.isEnemy(u, x) && (this.passable(Math.floor(x.x), Math.floor(x.y)) || Math.hypot(x.x - u.x, x.y - u.y) <= ut.ase.kantama)); if (e) { u.state = 'attack'; u.target = { unit: e.id, auto: true }; } }
        break;
      }
      case 'move': if (this._moveAlong(u, dt)) { u.state = 'idle'; u.path = null; } if (ut.jyraa) this._crush(u); break;
      case 'board': {
        const v = this.units.get(u.target && u.target.unit);
        if (!v || v.owner !== u.owner) { u.state = 'idle'; u.path = null; break; }
        if (Math.hypot(v.x - u.x, v.y - u.y) < 1.2) {
          if (v.cargo.length >= UNIT_TYPES[v.type].kyyti) { u.state = 'idle'; u.path = null; this.events.push({ e: 'taynna', owner: u.owner, x: v.x, y: v.y }); break; }
          this.units.delete(u.id); u.state = 'idle'; u.path = null; v.cargo.push(u);
          this.events.push({ e: 'kyytiin', id: u.id, v: v.id, owner: u.owner, type: v.type });
        } else this._goTo(u, v.x, v.y, dt) || (u.state = 'idle');
        break;
      }
      case 'molotovi': {
        const { x, y } = u.target;
        if (this.aselepo) { u.state = 'idle'; break; }
        if (Math.hypot(x - u.x, y - u.y) <= MOLOTOVI.kantama) {
          u.path = null;
          if (u.molocd > 0) break;
          const price = this.molotovPrice(u.owner);
          if (this.players[u.owner].money < price) { this.events.push({ e: 'eirahaa', owner: u.owner }); u.state = 'idle'; break; }
          this.players[u.owner].money -= price; u.molocd = MOLOTOVI.tauko; u.k = Math.min(100, u.k + 8);
          let tx = x, ty = y, oma = false;
          if (u.k >= 60 && this.rand() < 0.3) { tx = u.x; ty = u.y; oma = true; }
          if (tx !== u.x) u.dir = tx > u.x ? 1 : -1;
          const syttyi = !this.sade;
          this.events.push({ e: 'molotovi', id: u.id, owner: u.owner, x: u.x, y: u.y, tx, ty, syttyi, oma });
          if (syttyi) this.fires.push({ x: tx, y: ty, r: MOLOTOVI.sade, t: MOLOTOVI.kesto, owner: u.owner, delay: 0.5 });
          u.state = 'idle';
        } else this._goTo(u, x, y, dt) || (u.state = 'idle');
        break;
      }
      case 'jono': { // Alkon jono
        const a = this.tap && this.tap.alko;
        if (!a) { u.state = 'idle'; u.path = null; break; }
        if (Math.hypot(a[0] - u.x, a[1] - u.y) < 1.6) { u.path = null; u.jonoT += dt; if (u.jonoT > 8) { u.k = Math.min(100, u.k + 25); u.state = 'idle'; u.jonoT = 0; } }
        else this._goTo(u, a[0], a[1], dt) || (u.state = 'idle');
        break;
      }
      case 'tobar': {
        const b = this.buildings.find(b => b.id === u.target.b);
        if (Math.hypot(b.x - u.x, b.y + 1 - u.y) < 1.5) { u.state = 'idle'; u.path = null; u.k = Math.min(100, u.k + 10); }
        else this._goTo(u, b.x, b.y + 1.2, dt) || (u.state = 'idle');
        break;
      }
      case 'attack': {
        let tx, ty, tgtU = null, tgtB = null;
        if (this.aselepo) { u.state = 'idle'; u.path = null; break; }
        if (u.target.unit) { tgtU = this.units.get(u.target.unit); if (!tgtU) { u.state = 'idle'; u.path = null; break; } tx = tgtU.x; ty = tgtU.y; }
        else { tgtB = this.buildings.find(b => b.id === u.target.b); if (!tgtB || tgtB.owner === u.owner || tgtB.hp <= 0) { u.state = 'idle'; break; } tx = tgtB.x; ty = tgtB.y; }
        const d = Math.hypot(tx - u.x, ty - u.y);
        if (ut.jyraa && !ut.ase) { // Volvo: aja päälle
          if (!tgtU) { u.state = 'idle'; break; }
          this._goTo(u, tx, ty, dt) || (u.state = 'idle'); this._crush(u); break;
        }
        let w = ut.ase;
        if (ut.puukko && tgtU && d <= PUUKKO.kantama) w = PUUKKO;
        const range = w.kantama + (tgtB ? 1.4 : 0);
        const autoR = Math.max(VISION, w.kantama) + 2;
        if (u.target.auto && d > autoR) { u.state = 'idle'; u.path = null; break; }
        if (w.minimi && d < w.minimi) { if (u.target.auto) { u.state = 'idle'; u.path = null; } break; }
        if (d <= range) { u.path = null; if (tx !== u.x) u.dir = tx > u.x ? 1 : -1; if (u.cd <= 0) this._shoot(u, tgtU, tgtB, w); }
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
          if (u.collectT >= (this.inPuddle(c) ? 0.9 : 0.4)) { u.collectT = 0; c.n--; u.carry++; this.events.push({ e: 'kilina', x: c.x, y: c.y, owner: u.owner }); if (c.n <= 0) this.cans.delete(c.id); }
        } else this._goTo(u, c.x, c.y, dt) || (u.state = 'idle');
        break;
      }
      case 'return': {
        let b = u.target && u.target.b ? this.buildings.find(x => x.id === u.target.b && x.owner === u.owner && !x.suljettu) : null;
        if (!b) {
          const opts = this.buildings.filter(x => x.owner === u.owner && x.tyyppi === 'kmarket' && !x.suljettu);
          if (!opts.length && h) opts.push(h); // hätävara: päämaja ottaa tölkit puoleen hintaan
          b = opts.sort((a, c) => Math.hypot(a.x - u.x, a.y - u.y) - Math.hypot(c.x - u.x, c.y - u.y))[0];
          if (!b) { u.state = 'idle'; break; }
          u.target = { b: b.id }; u.path = null;
        }
        if (Math.hypot(b.x - u.x, b.y - u.y) < 2.6) {
          const val = u.carry * CAN_VALUE * (b.tyyppi === 'kmarket' ? 1 : 0.5) * (this.tap && this.tap.key === 'kesajuhlat' ? 2 : 1);
          this.players[u.owner].money += val;
          this.events.push({ e: 'pantti', owner: u.owner, x: b.x, y: b.y, n: u.carry, raha: val });
          u.carry = 0; u.path = null;
          if (u.home) { u.state = 'collect'; u.target = { can: -1 }; const p = u.home; u.path = this.findPath(u.x, u.y, p[0], p[1]); u.state = 'gohome'; }
          else u.state = 'idle';
        } else this._goTo(u, b.x, b.y + 1.2, dt) || (u.state = 'idle');
        break;
      }
      case 'talo': case 'tosauna': case 'kirppu': {
        const b = this.buildings.find(x => x.id === u.target.b);
        if (!b || (u.state === 'talo' && b.owner !== u.owner)) { u.state = 'idle'; u.path = null; break; }
        if (Math.hypot(b.x - u.x, b.y - u.y) < 2.2) {
          u.path = null;
          if (u.state === 'talo') {
            if (b.sisalla.length >= 6) { u.state = 'idle'; this.events.push({ e: 'taynna', owner: u.owner, x: b.x, y: b.y }); break; }
            this.units.delete(u.id); u.state = 'idle'; u.target = null; u.x = b.x; u.y = b.y; b.sisalla.push(u);
            this.events.push({ e: 'taloon', id: u.id, b: b.id, owner: u.owner, n: b.sisalla.length });
          } else if (u.state === 'tosauna') { u.state = 'sauna'; u.saunaT = 0; this.events.push({ e: 'sauna', id: u.id, owner: u.owner, x: u.x, y: u.y }); }
          else {
            u.state = 'idle';
            if (u.carry >= 3) { u.carry -= 3; const it = ESINEET[Math.floor(this.rand() * ESINEET.length)]; u.esine = it[1] || u.esine || 0; u.esineNimi = it[1] ? it[0] : (u.esineNimi || it[0]);
              this.events.push({ e: 'esine', id: u.id, owner: u.owner, x: u.x, y: u.y, nimi: it[0], hyoty: !!it[1] }); }
          }
        } else this._goTo(u, b.x, b.y + 1.2, dt) || (u.state = 'idle');
        break;
      }
      case 'sauna': {
        u.path = null; u.saunaT += dt; u.k = Math.max(0, u.k - 12 * dt); u.hp = Math.min(u.maxhp, u.hp + 4 * dt);
        if (u.saunaT > 25) { u.stun = 15; u.state = 'sammunut'; this.events.push({ e: 'sammui', id: u.id, owner: u.owner, x: u.x, y: u.y, sauna: true }); }
        break;
      }
      case 'lahjo': {
        const m = this.units.get(u.target && u.target.unit);
        if (!m || !u.carry) { u.state = 'idle'; u.path = null; break; }
        if (Math.hypot(m.x - u.x, m.y - u.y) < 1.2) {
          m.lahjottu = u.owner; m.lahjaT = this.time + 60; m.carry += u.carry;
          this.events.push({ e: 'lahjonta', id: m.id, owner: u.owner, n: u.carry, x: m.x, y: m.y }); u.carry = 0; u.state = 'idle'; u.path = null;
        } else this._goTo(u, m.x, m.y, dt) || (u.state = 'idle');
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

  _dmgMul(u) {
    let m = 1;
    if (u.k >= 20 && u.k < 60) m *= 1.25; else if (u.k >= 60) m *= 1.1;
    if (this.nearOwned(u.owner, u, 'KALJA-VARASTO')) m *= 1.15;
    if (u.buff > 0) m *= 1.3;
    return m;
  }
  _damage(attacker, tgtU, dmg) {
    const tt = UNIT_TYPES[tgtU.type];
    if (tt.panssari) dmg *= tt.panssari;
    if (tgtU.esine === 'kypara') dmg *= 0.7;
    if (this.nearOwned(tgtU.owner, tgtU, 'LIHAPULLALINNAKE')) dmg *= 0.5;
    tgtU.hp -= dmg;
    if (tgtU.hp <= 0) { this._kill(tgtU); return true; }
    if (tt.olento) { if (attacker) tgtU.aggro = attacker.id; return false; }
    if (attacker && attacker.owner && attacker.owner !== tgtU.owner && tgtU.state === 'idle' && UNIT_TYPES[tgtU.type].ase && !this.aselepo) { tgtU.state = 'attack'; tgtU.target = { unit: attacker.id, auto: true }; }
    return false;
  }
  _kill(u) {
    this._remove(u);
    if (u.type === 'vesihiisi') this.hiisi = null;
    this._dropCans(u.x, u.y, (UNIT_TYPES[u.type].olento ? 6 : UNIT_TYPES[u.type].luokka === 'jalka' ? 2 : 4) + u.carry);
    this.events.push({ e: 'kuoli', id: u.id, owner: u.owner, type: u.type, x: u.x, y: u.y, ajoneuvo: UNIT_TYPES[u.type].luokka === 'ajoneuvo' });
  }
  _remove(u) {
    if (u.cargo && u.cargo.length) this._unload(u, 25);
    this.units.delete(u.id);
  }
  _unload(v, dmg = 0) {
    if (!v.cargo || !v.cargo.length) return;
    const spots = this._spreadTargets(v.x, v.y, v.cargo.length);
    v.cargo.forEach((p, i) => {
      p.x = spots[i][0]; p.y = spots[i][1]; p.state = 'idle'; p.path = null; p.target = null;
      this.units.set(p.id, p);
      if (dmg) this._damage(null, p, dmg);
    });
    this.events.push({ e: 'purku', id: v.id, owner: v.owner, n: v.cargo.length, x: v.x, y: v.y });
    v.cargo = [];
  }
  _crush(v) {
    const ut = UNIT_TYPES[v.type];
    for (const o of [...this.units.values()]) {
      if (!this.isEnemy(v, o) || UNIT_TYPES[o.type].luokka !== 'jalka') continue;
      if (Math.hypot(o.x - v.x, o.y - v.y) > 0.6) continue;
      if ((v.crush[o.id] || 0) > this.time) continue;
      v.crush[o.id] = this.time + 1;
      this.events.push({ e: 'jyrays', id: v.id, owner: v.owner, x: o.x, y: o.y });
      this._damage(v, o, ut.jyraa);
    }
  }

  _shoot(u, tgtU, tgtB, w) {
    w = w || UNIT_TYPES[u.type].ase;
    u.cd = w.tauko;
    let dmg = w.vahinko * this._dmgMul(u), acc = 0.85;
    if (u.k >= 20 && u.k < 60) acc += 0.07; else if (u.k >= 60) acc -= 0.15 + (u.k - 60) / 200;
    if (w.roiske) acc -= 0.15; // tykistö on epätarkka
    const tx = tgtU ? tgtU.x : tgtB.x, ty = tgtU ? tgtU.y : tgtB.y;
    const hit = tgtB ? true : this.rand() < acc;
    this.events.push({ e: 'ammus', id: u.id, w: w.aani, x: u.x, y: u.y, tx, ty, hit, owner: u.owner, roiske: !!w.roiske, lahi: w.kantama <= 1.2 });
    if (tgtB) {
      tgtB.hp -= dmg;
      if (tgtB.hp <= 0) { tgtB.hp = 0; this.events.push({ e: 'tuhoutui', b: tgtB.id, x: tgtB.x, y: tgtB.y }); if (tgtB.tyyppi === 'paamaja') { this.winner = u.owner; this.events.push({ e: 'voitto', winner: u.owner }); } }
      return;
    }
    if (w.roiske) {
      // osuu maahan (ohi = vähän sivuun) ja roiskuu kaikkiin vihollisiin lähellä
      const ix = hit ? tx : tx + (this.rand() - 0.5) * 2.5, iy = hit ? ty : ty + (this.rand() - 0.5) * 2.5;
      this.events.push({ e: 'rajahdys', x: ix, y: iy, pieni: true });
      for (const o of [...this.units.values()]) {
        if (!this.isEnemy(u, o)) continue;
        const d = Math.hypot(o.x - ix, o.y - iy); if (d > w.roiske) continue;
        this._damage(u, o, dmg * (1 - d / w.roiske * 0.6));
      }
      return;
    }
    if (!hit) return;
    if (w.hidastaa) tgtU.slow = w.hidastaa;
    this._damage(u, tgtU, dmg);
  }

  _puke(u) {
    if (this.puddles.length >= 30) this.puddles.shift();
    this.puddles.push({ x: u.x, y: u.y + 0.1, r: 1.5, t: 25, max: 25 });
  }
  inPuddle(u) { return this.puddles.some(p => Math.hypot(p.x - u.x, p.y - u.y) <= p.r * Math.max(0.5, p.t / p.max)); }
  _stepPuddles(dt) {
    for (const p of this.puddles) p.t -= dt;
    this.puddles = this.puddles.filter(p => p.t > 0);
    if (!this.puddles.length) return;
    for (const u of [...this.units.values()]) if (u.owner && this.inPuddle(u)) {
      u.inPuddle = true; u.hp -= 1.5 * dt; if (u.hp <= 0) this._kill(u);
    } else u.inPuddle = false;
  }

  _stepFires(dt) {
    for (const f of this.fires) {
      if (f.delay > 0) { f.delay -= dt; continue; }
      f.t -= dt;
      for (const o of [...this.units.values()]) {
        if (o.owner === 0) continue;
        if (Math.hypot(o.x - f.x, o.y - f.y) <= f.r) { const killer = [...this.units.values()].find(x => x.owner === f.owner); this._damage(o.owner !== f.owner ? killer : null, o, MOLOTOVI.vahinko * dt); }
      }
    }
    this.fires = this.fires.filter(f => f.t > 0);
  }

  // ---------- satunnaistapahtumat ----------
  startEvent(key) {
    const def = TAPAHTUMAT[key]; if (!def) return;
    if (this.tap) this._endEvent();
    const tap = { key, left: def.kesto, nimi: def.nimi };
    this.tap = tap;
    const infantry = (team) => [...this.units.values()].filter(u => u.owner === team && UNIT_TYPES[u.type].luokka === 'jalka' && u.stun <= 0);
    const pickSome = (arr, frac) => { const n = arr.length ? Math.max(1, Math.round(arr.length * frac)) : 0; const out = []; const a = arr.slice(); while (out.length < n && a.length) out.push(a.splice(Math.floor(this.rand() * a.length), 1)[0]); return out; };
    switch (key) {
      case 'poliisipartio': {
        const edges = [];
        for (let c = 0; c < this.W; c++) for (const r of [0, this.H - 1]) if (this.passable(c, r) && this.cost[this.terrain[r][c]] <= 0.5) edges.push([c, r]);
        for (let r = 0; r < this.H; r++) for (const c of [0, this.W - 1]) if (this.passable(c, r) && this.cost[this.terrain[r][c]] <= 0.5) edges.push([c, r]);
        const e = edges[Math.floor(this.rand() * edges.length)] || this.nearestPassable(this.W / 2, this.H / 2);
        const id = this.nextId++;
        this.npcs.set(id, { id, type: 'poliisiauto', owner: 0, x: e[0] + 0.5, y: e[1] + 0.5, path: null, repath: 0, dir: 1, k: 0, hp: 1, carry: 0, state: 'move', stun: 0, slow: 0 });
        break;
      }
      case 'alkon_alennus': {
        tap.alko = this.nearestPassable(this.W / 2, this.H / 2 - 4).map(v => v + 0.5);
        for (const u of this.units.values()) if (u.owner) u.k = Math.min(100, u.k + 15);
        for (const team of [1, 2]) for (const u of pickSome([...this.units.values()].filter(u => u.owner === team && u.type === 'lahiojermu' && u.stun <= 0), 0.4)) { u.state = 'jono'; u.path = null; u.jonoT = 0; u.repath = 0; }
        break;
      }
      case 'panttiautomaatti_rikki': {
        const km = this.buildings.filter(b => b.tyyppi === 'kmarket');
        const b = km[Math.floor(this.rand() * km.length)]; if (b) { b.suljettu = true; tap.b = b.id; }
        break;
      }
      case 'pihakirppis': {
        for (let i = 0; i < 8; i++) for (let tries = 0; tries < 60; tries++) {
          const c = Math.floor(8 + this.rand() * (this.W - 16)), r = Math.floor(20 + this.rand() * 20);
          if (this.passable(c, r)) { const id = this.nextId++; this.cans.set(id, { id, x: c + 0.5, y: r + 0.5, n: 10 + Math.floor(this.rand() * 6), kirppis: true }); (tap.paikat = tap.paikat || []).push([c + 0.5, r + 0.5]); break; }
        }
        break;
      }
      case 'saunailta': case 'taloyhtion_kokous': {
        const team = key === 'saunailta' ? 2 : 1;
        for (const u of pickSome(infantry(team), 0.3)) {
          this.units.delete(u.id);
          this.away.push({ u, back: this.time + def.kesto, sauna: key === 'saunailta', team });
        }
        tap.team = team;
        break;
      }
    }
    this.events.push({ e: 'tapahtuma', key, nimi: def.nimi, teksti: def.teksti, kesto: def.kesto, koskee: def.koskee });
  }
  _endEvent() {
    const tap = this.tap; if (!tap) return;
    if (tap.b) { const b = this.buildings.find(x => x.id === tap.b); if (b) b.suljettu = false; }
    for (const n of [...this.npcs.values()]) this.npcs.delete(n.id);
    for (const u of this.units.values()) if (u.state === 'jono') { u.state = 'idle'; u.path = null; }
    this.events.push({ e: 'tapahtuma_loppui', key: tap.key, nimi: tap.nimi, koskee: TAPAHTUMAT[tap.key].koskee });
    this.tap = null;
  }
  _stepEvents(dt) {
    // palaajat
    for (const a of this.away.slice()) if (this.time >= a.back) {
      this.away.splice(this.away.indexOf(a), 1);
      const u = a.u;
      if (a.sauna) { const h = this.hq(a.team); if (h) { const s = this._spreadTargets(h.x, h.y + 1.5, 1)[0]; u.x = s[0]; u.y = s[1]; } u.k = 0; u.hp = u.maxhp; u.buff = 60; }
      u.state = 'idle'; u.path = null; u.target = null;
      this.units.set(u.id, u);
      this.events.push({ e: 'palasi', id: u.id, owner: u.owner, sauna: a.sauna });
    }
    if (this.tap) { this.tap.left -= dt; if (this.tap.left <= 0) this._endEvent(); return; }
    this.nextTap -= dt;
    if (!this.tapOrder.length) { this.tapOrder = Object.keys(TAPAHTUMAT); for (let i = this.tapOrder.length - 1; i > 0; i--) { const j = Math.floor(this.rand() * (i + 1)); [this.tapOrder[i], this.tapOrder[j]] = [this.tapOrder[j], this.tapOrder[i]]; } }
    const next = this.tapOrder[this.tapOrder.length - 1];
    if (this.nextTap <= 5 && this.warned !== next + this.nextTapId) {
      this.warned = next + this.nextTapId;
      const d = TAPAHTUMAT[next];
      this.events.push({ e: 'tapahtuma_varoitus', key: next, nimi: d.nimi, teksti: d.varoitus, koskee: d.koskee, sekunnit: Math.ceil(this.nextTap) });
    }
    if (this.nextTap <= 0) {
      this.nextTapId = (this.nextTapId || 0) + 1;
      this.startEvent(this.tapOrder.pop());
      this.nextTap = 60 + this.rand() * 50;
    }
  }
  _stepNpcs(dt) {
    for (const n of this.npcs.values()) {
      // poliisi ajaa humalaisimman kohti ja vie putkaan
      let best = null, bk = 59;
      for (const u of this.units.values()) if (u.owner && u.k > bk) { bk = u.k; best = u; }
      n.repath -= dt;
      if (best && (n.repath <= 0 || !n.path || !n.path.length)) { n.path = this.findPath(n.x, n.y, best.x, best.y); n.repath = 1.5; }
      else if (!best && (!n.path || !n.path.length)) { const p = this.nearestPassable(this.rand() * this.W, this.rand() * this.H); if (p) n.path = this.findPath(n.x, n.y, p[0] + 0.5, p[1] + 0.5); }
      if (n.path) this._moveAlong(n, dt);
      for (const u of [...this.units.values()]) if (u.owner && u.k >= 60 && Math.hypot(u.x - n.x, u.y - n.y) < 1.3) {
        this._remove(u); this._dropCans(u.x, u.y, u.carry);
        this.events.push({ e: 'putkaan', id: u.id, owner: u.owner, type: u.type, x: u.x, y: u.y });
      }
    }
  }

  // ---------- olennot: metsäpeikot ja vesihiisi ----------
  _forest(c, r) { const t = this.terrain[r] && this.terrain[r][c]; return t === 1 || t === 13; }
  _stepOlennot(dt) {
    if (this.winner) return;
    // peikot: muutama kerrallaan, syntyvät metsään kauas päämajoista
    this.nextPeikko -= dt;
    if (this.nextPeikko <= 0) {
      this.nextPeikko = 70 + this.rand() * 50;
      const n = [...this.units.values()].filter(u => u.type === 'peikko').length;
      const add = Math.min(MAX_PEIKOT - n, 1 + Math.floor(this.rand() * 2));
      let first = null;
      for (let i = 0; i < add; i++) for (let tries = 0; tries < 200; tries++) {
        const c = Math.floor(this.rand() * this.W), r = Math.floor(this.rand() * this.H);
        if (!this._forest(c, r) || [1, 2].some(t => { const h = this.hq(t); return h && Math.hypot(h.x - c, h.y - r) < 12; })) continue;
        const p = this._spawnUnitNear(3, 'peikko', c + 0.5, r + 0.5); p.home = [c + 0.5, r + 0.5]; p.ai = 'vaella'; p.aiT = 2;
        first = first || p; break;
      }
      if (first) this.events.push({ e: 'olento', key: 'peikot', ...OLENNOT.peikot, id: first.id, x: first.x, y: first.y });
    }
    // vesihiisi
    const h = this.hiisi;
    if (!h) {
      this.nextHiisi -= dt;
      if (this.nextHiisi <= 0 && this.shore.length) {
        // valitse rantaruutu, jonka lähellä (≤3) on joukkoja
        const cand = this.shore.filter(([c, r]) => [...this.units.values()].some(u => u.owner === 1 || u.owner === 2 ? Math.hypot(u.x - c - 0.5, u.y - r - 0.5) <= 3 : false));
        if (!cand.length) { this.nextHiisi = 8; return; }
        const [c, r] = cand[Math.floor(this.rand() * cand.length)];
        this.hiisi = { x: c + 0.5, y: r + 0.5, phase: 'kuplat', t: 4 };
        this.events.push({ e: 'hiisi_kuplat', x: c + 0.5, y: r + 0.5, teksti: 'Rannassa kuplii ja sihisee... pysy kaukana vedestä!' });
      }
      return;
    }
    h.t -= dt;
    if (h.phase === 'kuplat' && h.t <= 0) {
      const id = this.nextId++; const ut = UNIT_TYPES.vesihiisi;
      const u = { id, type: 'vesihiisi', owner: 3, x: h.x, y: h.y, hp: ut.hp, maxhp: ut.hp, k: 0, carry: 0, state: 'nousu', dir: 1, cd: 1, stun: 0, slow: 0, buff: 0, path: null, repath: 0, cargo: [], crush: {}, nousuT: 0.8 };
      this.units.set(id, u);
      h.phase = 'ylhaalla'; h.t = 14; h.id = id;
      this.events.push({ e: 'olento', key: 'vesihiisi', ...OLENNOT.vesihiisi, id, x: h.x, y: h.y });
    } else if (h.phase === 'ylhaalla' && h.t <= 0) {
      const u = this.units.get(h.id);
      if (u) { this.units.delete(u.id); this.events.push({ e: 'hiisi_sukelsi', id: u.id, x: u.x, y: u.y }); }
      this.hiisi = null; this.nextHiisi = 45 + this.rand() * 35;
    }
  }
  _huuto(u, kind) {
    if ((u.huutoT || 0) > this.time) return;
    u.huutoT = this.time + 6;
    this.events.push({ e: 'huuto', id: u.id, kind, x: u.x, y: u.y });
  }
  _stepOlento(u, dt) {
    const ut = UNIT_TYPES[u.type];
    if (u.cd > 0) u.cd -= dt;
    if (u.slow > 0) u.slow -= dt;
    u.k = 0;
    const foe = x => x.owner === 1 || x.owner === 2;
    if (u.type === 'pullomummo' || u.type === 'hemuli' || u.type === 'hemuli_caesar' || u.type === 'vana') return this._stepNpcV4(u, dt, ut, foe);
    if (u.type === 'vesihiisi') {
      if (u.nousuT > 0) { u.nousuT -= dt; if (u.nousuT <= 0) { u.state = 'idle'; this._huuto(u, 'hiisi'); } return; }
      const t = this._nearestUnit(u, ut.ase.kantama, foe);
      u.state = t ? 'attack' : 'idle';
      if (t && u.cd <= 0 && !this.aselepo) { u.dir = t.x >= u.x ? 1 : -1; this._shoot(u, t, null); if (this.rand() < 0.3) this._huuto(u, 'hiisi'); }
      return;
    }
    // metsäpeikko: arvaamaton tilakone
    u.aiT -= dt;
    if (u.ai === 'karjuu') { if (u.aiT <= 0) { u.ai = 'vaella'; u.aiT = 1; u.state = 'idle'; } return; }
    const home = u.home || [u.x, u.y];
    const farHome = Math.hypot(u.x - home[0], u.y - home[1]) > 8;
    if (u.aggro && !this.units.has(u.aggro)) u.aggro = null;
    if (u.aiT <= 0 || farHome) {
      u.aiT = 3 + this.rand() * 4; u.path = null;
      const near = this._nearestUnit(u, 6, foe);
      const kantaja = this._nearestUnit(u, 7, x => foe(x) && x.carry > 0);
      const roll = this.rand();
      if (farHome) { u.ai = 'kotiin'; u.aggro = null; }
      else if (u.aggro || (near && roll < 0.4)) { u.ai = 'hyokkaa'; u.tgt = u.aggro || near.id; this._huuto(u, 'mun_metsa'); }
      else if (kantaja && roll < 0.65) { u.ai = 'varasta'; u.tgt = kantaja.id; this._huuto(u, 'tolkit'); }
      else if (near && roll < 0.8) {
        // karjaisu: lähellä olevat pelästyvät pakoon
        u.ai = 'karjuu'; u.aiT = 1.5; u.state = 'karjuu';
        this.events.push({ e: 'karjunta', id: u.id, x: u.x, y: u.y }); this._huuto(u, 'pois');
        for (const o of this.units.values()) if (foe(o) && UNIT_TYPES[o.type].luokka === 'jalka' && o.stun <= 0 && Math.hypot(o.x - u.x, o.y - u.y) <= 3.5) {
          const d = Math.hypot(o.x - u.x, o.y - u.y) || 1;
          const p = this.nearestPassable(o.x + (o.x - u.x) / d * 4, o.y + (o.y - u.y) / d * 4, 3);
          if (p) { o.state = 'move'; o.target = null; o.path = this.findPath(o.x, o.y, p[0] + 0.5, p[1] + 0.5); }
        }
        return;
      } else {
        u.ai = 'vaella'; if (this.rand() < 0.15) this._huuto(u, 'nalka');
        for (let i = 0; i < 20; i++) { const c = Math.floor(home[0] + (this.rand() - 0.5) * 10), r = Math.floor(home[1] + (this.rand() - 0.5) * 10); if (this._forest(c, r)) { u.path = this.findPath(u.x, u.y, c + 0.5, r + 0.5); break; } }
      }
    }
    u.state = 'move';
    if (u.ai === 'kotiin') { if (this._goTo(u, home[0], home[1], dt) === false || Math.hypot(u.x - home[0], u.y - home[1]) < 1.5) { u.ai = 'vaella'; u.aiT = 0.5; } return; }
    if (u.ai === 'hyokkaa') {
      const t = this.units.get(u.tgt);
      if (!t || Math.hypot(t.x - u.x, t.y - u.y) > 9) { u.ai = 'vaella'; u.aiT = 0; u.aggro = null; return; }
      const d = Math.hypot(t.x - u.x, t.y - u.y);
      if (d <= ut.ase.kantama) { u.path = null; u.state = 'attack'; u.dir = t.x >= u.x ? 1 : -1; if (u.cd <= 0 && !this.aselepo) this._shoot(u, t, null); }
      else this._goTo(u, t.x, t.y, dt);
      return;
    }
    if (u.ai === 'varasta') {
      const t = this.units.get(u.tgt);
      if (!t || !t.carry) { u.ai = 'vaella'; u.aiT = 0; return; }
      if (Math.hypot(t.x - u.x, t.y - u.y) < 0.9) {
        u.carry += t.carry; this.events.push({ e: 'varasti', id: u.id, owner: t.owner, n: t.carry, x: t.x, y: t.y }); t.carry = 0;
        u.ai = 'kotiin'; return;
      }
      this._goTo(u, t.x, t.y, dt); return;
    }
    if (!u.path || !u.path.length) { u.state = 'idle'; return; }
    this._moveAlong(u, dt);
  }

  // ---------- V4 ----------
  _paljasta(team, units, aika, syy) {
    if (!units.length) return;
    this.events.push({ e: 'paljastus', team, ids: units.map(u => u.id), aika, syy, x: units[0].x, y: units[0].y });
  }
  _evict(b, k, slow) {
    if (!b.sisalla.length) return;
    const spots = this._spreadTargets(b.x, b.y + 1.5, b.sisalla.length);
    b.sisalla.forEach((u, i) => { u.x = spots[i][0]; u.y = spots[i][1]; u.state = 'idle'; u.path = null; u.target = null; if (k) u.k = k; if (slow) u.slow = slow; this.units.set(u.id, u); });
    this.events.push({ e: 'talosta', b: b.id, owner: b.sisalla[0].owner, n: b.sisalla.length, x: b.x, y: b.y });
    b.sisalla = []; b.bileT = 0; b.piiritysT = 0;
  }
  _stepV4Buildings(dt) {
    for (const b of this.buildings) {
      if (b.tyyppi === 'pihagrilli' && b.owner) {
        b.grilliT -= dt;
        if (b.grilliT <= 0) { b.grilliT = 20; this._paljasta(b.owner, [...this.units.values()].filter(u => u.owner === b.owner && Math.hypot(b.x - u.x, b.y - u.y) <= 4), 5, 'pihagrilli'); }
      }
      if (b.tyyppi !== 'kerrostalo') continue;
      const n = b.sisalla.length;
      if (!n) { b.bileT = 0; b.piiritysT = 0; continue; }
      // ampuminen ikkunoista
      if (!this.aselepo) for (const u of b.sisalla) {
        const w = UNIT_TYPES[u.type].ase; if (u.cd > 0) u.cd -= dt; if (!w || u.cd > 0) continue;
        u.x = b.x; u.y = b.y;
        const e = this._nearestUnit(u, w.kantama + 1.5, x => this.isEnemy(u, x)); if (e) this._shoot(u, e, null, w);
      }
      if (n >= 6) {
        if (!b.piiritysT) { b.piiritysT = 4; b.bileT = 0; this.events.push({ e: 'piiritys', b: b.id, owner: b.owner, x: b.x, y: b.y }); }
        b.piiritysT -= dt;
        if (b.piiritysT <= 0) {
          for (const u of b.sisalla) this.events.push({ e: 'putkaan', id: u.id, owner: u.owner, type: u.type, x: b.x, y: b.y });
          b.sisalla = []; b.piiritysT = 0;
        }
      } else if (n >= 4) {
        b.piiritysT = 0;
        if (!b.bileT) this.events.push({ e: 'bileet', b: b.id, owner: b.owner, x: b.x, y: b.y });
        const t0 = b.bileT; b.bileT += dt;
        if (t0 < 10 && b.bileT >= 10) this.events.push({ e: 'naapurit', b: b.id, owner: b.owner, x: b.x, y: b.y });
        if (b.bileT >= 18) { this.events.push({ e: 'haato', b: b.id, owner: b.owner, x: b.x, y: b.y }); this._evict(b, 95, 20); }
      } else { b.bileT = 0; b.piiritysT = 0; }
    }
  }
  _wander(u, cx, cy, rad, ok) {
    for (let i = 0; i < 20; i++) { const c = Math.floor(cx + (this.rand() - 0.5) * 2 * rad), r = Math.floor(cy + (this.rand() - 0.5) * 2 * rad); if (this.passable(c, r) && (!ok || ok(c, r))) { u.path = this.findPath(u.x, u.y, c + 0.5, r + 0.5); return; } }
  }
  muodonmuutos(u) {
    u.type = 'hemuli_caesar'; u.owner = 3; u.hp = u.maxhp = UNIT_TYPES.hemuli_caesar.hp; u.caesarT = 30; u.ai = 'vaella'; u.aiT = 0; u.path = null;
    this.events.push({ e: 'muodonmuutos', id: u.id, x: u.x, y: u.y, nimi: 'Puolijumala Caesar', teksti: 'Hemuli söi jotain outoa ja muuttui PUOLIJUMALA CAESARIKSI! Hän iskee salamoita kaikkiin lähellä oleviin 30 s.', koskee: 0 });
  }
  _stepNpcV4(u, dt, ut, foe) {
    u.aiT = (u.aiT || 0) - dt;
    if (u.type === 'pullomummo') {
      if (u.lahjottu && this.time > u.lahjaT) u.lahjottu = 0;
      let c = this.cans.get(u.tgt);
      if (!c) { let bd = 15; u.tgt = null; for (const cc of this.cans.values()) { const d = Math.hypot(cc.x - u.x, cc.y - u.y); if (d < bd) { bd = d; u.tgt = cc.id; c = cc; } } u.path = null; u.repath = 0; }
      if (c) {
        u.state = 'move';
        if (Math.hypot(c.x - u.x, c.y - u.y) < 0.6) {
          this.cans.delete(c.id); u.tgt = null; this.events.push({ e: 'kilina', x: c.x, y: c.y, owner: 0 });
          if (u.lahjottu) { const raha = c.n * CAN_VALUE; this.players[u.lahjottu].money += raha; this.events.push({ e: 'mummo_raha', id: u.id, owner: u.lahjottu, n: c.n, raha, x: u.x, y: u.y }); }
          else u.carry += c.n;
        } else if (!this._goTo(u, c.x, c.y, dt)) u.tgt = null;
        return;
      }
      if (!u.path || !u.path.length) { u.state = 'idle'; if (u.aiT <= 0) { u.aiT = 4; this._wander(u, u.x, u.y, 6); } return; }
      u.state = 'move'; this._moveAlong(u, dt); return;
    }
    if (u.type === 'hemuli') {
      const home = u.home || [u.x, u.y];
      if (u.state === 'syo') { if (u.aiT <= 0) { u.state = 'idle'; if (this.rand() < (this.caesarP || 0.2)) this.muodonmuutos(u); } return; }
      if (!u.path || !u.path.length) {
        u.state = 'idle';
        if (u.aiT <= 0) {
          const t = this.terrain[Math.floor(u.y)][Math.floor(u.x)];
          if ((t === 0 || t === 1 || t === 11) && this.rand() < 0.5) { u.state = 'syo'; u.aiT = 3; return; }
          u.aiT = 2 + this.rand() * 3; this._wander(u, home[0], home[1], 6);
        }
        return;
      }
      u.state = 'move'; this._moveAlong(u, dt); return;
    }
    if (u.type === 'hemuli_caesar') {
      u.caesarT -= dt;
      if (u.caesarT <= 0) { u.type = 'hemuli'; u.owner = 0; u.maxhp = UNIT_TYPES.hemuli.hp; u.hp = Math.min(u.hp, u.maxhp); u.state = 'idle'; u.path = null; this.events.push({ e: 'caesar_loppui', id: u.id, x: u.x, y: u.y }); return; }
      const t = this._nearestUnit(u, 7, foe);
      if (t) {
        const d = Math.hypot(t.x - u.x, t.y - u.y);
        if (d <= ut.ase.kantama) { u.path = null; u.state = 'attack'; u.dir = t.x >= u.x ? 1 : -1; if (u.cd <= 0 && !this.aselepo) this._shoot(u, t, null); }
        else { u.state = 'move'; this._goTo(u, t.x, t.y, dt); }
        return;
      }
      if (!u.path || !u.path.length) { u.state = 'idle'; if (u.aiT <= 0) { u.aiT = 3; this._wander(u, u.x, u.y, 6); } return; }
      u.state = 'move'; this._moveAlong(u, dt); return;
    }
    // Vänä: baari -> känni -> potkii palloa lähimpiin -> selviää -> baari
    const home = u.home || [u.x, u.y];
    if (u.ai === 'baariin') {
      if (Math.hypot(home[0] - u.x, home[1] - u.y) < 1.5) { u.ai = 'juo'; u.aiT = 8; u.path = null; u.state = 'idle'; }
      else { u.state = 'move'; if (!this._goTo(u, home[0], home[1], dt)) { u.ai = 'juo'; u.aiT = 8; } }
      return;
    }
    if (u.ai === 'juo') { u.state = 'idle'; if (u.aiT <= 0) { u.ai = 'kanni'; u.aiT = 30; this.events.push({ e: 'huuto', id: u.id, kind: 'vana', x: u.x, y: u.y }); } return; }
    if (u.aiT <= 0) { u.ai = 'baariin'; u.path = null; return; }
    const t = this._nearestUnit(u, ut.ase.kantama, foe);
    if (t) { u.path = null; u.state = 'attack'; u.dir = t.x >= u.x ? 1 : -1; if (u.cd <= 0 && !this.aselepo) this._shoot(u, t, null); return; }
    if (!u.path || !u.path.length) { u.state = 'idle'; if ((u.wT = (u.wT || 0) - dt) <= 0) { u.wT = 3; this._wander(u, home[0], home[1], 9); } return; }
    u.state = 'move'; this._moveAlong(u, dt);
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
      if (b.tyyppi === 'paamaja' || b.noCap || this.aselepo) continue;
      const n = { 1: 0, 2: 0 };
      for (const u of this.units.values()) if (u.owner && u.stun <= 0 && Math.hypot(u.x - b.x, u.y - b.y) <= CAPTURE_RADIUS) n[u.owner]++;
      const present = [1, 2].filter(t => n[t] > 0);
      if (present.length === 1 && present[0] !== b.owner) {
        const t = present[0];
        if (b.cap.team !== t) { b.cap.team = t; b.cap.p = 0; }
        b.cap.p += dt / CAPTURE_TIME * Math.min(3, n[t]);
        if (b.cap.p >= 1) {
          const old = b.owner; b.owner = t; b.cap = { team: 0, p: 0 };
          if (b.sisalla && b.sisalla.length) this._evict(b);
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
      unitTypes: UNIT_TYPES, olennot: OLENNOT, canValue: CAN_VALUE, molotovi: MOLOTOVI, tapahtumat: TAPAHTUMAT,
    };
  }
  snapshot() {
    const r1 = v => Math.round(v * 100) / 100;
    const s = {
      t: 's', tick: this.tick, time: r1(this.time), winner: this.winner,
      u: [...this.units.values(), ...this.npcs.values()].map(u => [u.id, u.type, u.owner, r1(u.x), r1(u.y), Math.ceil(u.hp), Math.round(u.k), u.carry, u.stun > 0 ? 'sammunut' : u.state, u.dir, u.cargo ? u.cargo.length : 0, (u.slow > 0 ? 1 : 0) | (u.buff > 0 ? 2 : 0), u.esineNimi || 0]),
      c: [...this.cans.values()].map(c => [c.id, r1(c.x), r1(c.y), c.n]),
      b: this.buildings.map(b => [b.id, b.owner, b.cap.team, r1(b.cap.p), Math.ceil(b.hp || 0), b.suljettu ? 1 : 0, b.sisalla ? b.sisalla.length : 0, (b.bileT > 0 ? 1 : 0) | (b.piiritysT > 0 ? 2 : 0)]),
      l: this.puddles.map(p => [r1(p.x), r1(p.y), p.r, Math.round(p.t / p.max * 100) / 100]),
      f: this.fires.filter(f => !(f.delay > 0)).map(f => [r1(f.x), r1(f.y), f.r, r1(f.t)]),
      tap: this.tap ? { key: this.tap.key, nimi: this.tap.nimi, left: Math.ceil(this.tap.left), alko: this.tap.alko || null, team: this.tap.team || 0, koskee: TAPAHTUMAT[this.tap.key].koskee,
        paikat: this.tap.alko ? [this.tap.alko] : this.tap.key === 'poliisipartio' ? [...this.npcs.values()].map(n => [r1(n.x), r1(n.y)]) : this.tap.b ? [[this.buildings.find(b => b.id === this.tap.b).x, this.buildings.find(b => b.id === this.tap.b).y]] : (this.tap.paikat || []).filter(p => [...this.cans.values()].some(c => c.x === p[0] && c.y === p[1])) } : null,
      nextTap: this.tap ? null : Math.ceil(this.nextTap),
      hb: this.hiisi && this.hiisi.phase === 'kuplat' ? [this.hiisi.x, this.hiisi.y] : null,
      away: this.away.map(a => [a.team, a.sauna ? 1 : 0]),
      hinnat: { 1: Object.fromEntries(Object.keys(UNIT_TYPES).map(k => [k, this.price(1, k)])), 2: Object.fromEntries(Object.keys(UNIT_TYPES).map(k => [k, this.price(2, k)])) },
      molo: { 1: this.molotovPrice(1), 2: this.molotovPrice(2) },
      p: { 1: { money: Math.floor(this.players[1].money), queue: this.players[1].queue.map(q => [q.type, r1(q.left), q.total]) },
           2: { money: Math.floor(this.players[2].money), queue: this.players[2].queue.map(q => [q.type, r1(q.left), q.total]) } },
      ev: this.events,
    };
    this.events = [];
    return s;
  }
}

module.exports = { Game, UNIT_TYPES, TAPAHTUMAT, OLENNOT, TICK };
