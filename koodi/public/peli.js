'use strict';
// Lähiösota: Etelä-Tampere – selainasiakas (Canvas 2D, ei riippuvuuksia)
(() => {
const TS = 32; // ruudun koko pikseleinä (grafiikka 32x32)
const PANEL = 215;
const TEAM = { 1: { nimi: 'Multisilta', vari: 'sininen', css: '#1f6fe0' }, 2: { nimi: 'Peltolammi', vari: 'punainen', css: '#d8262b' }, 0: { nimi: 'Puolueeton', css: '#999' } };
const TERRAIN_FILES = ['00_ruoho', '01_metsa', '02_vesi', '03_tie', '04_moottoritie', '05_rata', '06_rakennus', '07_teollisuus', '08_pelto', '09_suo', '10_kallio', '11_puisto', '12_silta'];
const MINI_COLORS = ['#4d7a35', '#2b4d22', '#2d5a8c', '#777', '#555', '#6b5a48', '#8a8a8a', '#666158', '#9a9a4a', '#4f5f3a', '#7a7066', '#5f9a45', '#8a6a3a'];
const EXTRA_BUILDINGS = { 'PIZZATEHDAS': 'pizzatehdas', 'KARKKIKAIVOS': 'karkkikaivos', 'LÄÄKINTÄASEMA': 'laakintaasema', 'TIEDUSTELUKESKUS': 'tiedustelukeskus',
  'KAHVILÄHDE': 'kahvilahde', 'PERUNAPELTO': 'perunapelto', 'HUOLTOVARIKKO': 'huoltovarikko', 'ROMUTARVIKEVARASTO': 'romutarvikevarasto',
  'POLTTOAINEVARASTO': 'polttoainevarasto', 'KAASUVARASTO': 'kaasuvarasto', 'LIHAPULLALINNAKE': 'lihapullalinnake' };
const TRAIN_KEYS = { z: 'tolkkijussi', x: 'lahiojermu', c: 'mopopoika' };
const STATE_FI = { idle: 'odottaa', move: 'liikkuu', attack: 'hyökkää', collect: 'kerää tölkkejä', return: 'vie pantteja', gohome: 'palaa keräämään', tobar: 'lähti baariin!', sammunut: 'SAMMUNUT' };

const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);

// ---------- aula ----------
function randCode() { return Math.random().toString(36).slice(2, 8); }
function token() { let t = localStorage.getItem('lahiosota_token'); if (!t) { t = randCode() + randCode(); localStorage.setItem('lahiosota_token', t); } return t; }
$('luo').onclick = () => { location.search = '?huone=' + randCode(); };
$('harjoitus').onclick = () => { location.search = '?huone=h' + randCode() + '&harjoitus=1'; };
$('kopioi').onclick = () => { $('linkkiKentta').select(); navigator.clipboard && navigator.clipboard.writeText($('linkkiKentta').value); };

// ---------- assetit ----------
const IMG = {};
function loadImg(key, src) { return new Promise(res => { const i = new Image(); i.onload = () => { IMG[key] = i; res(); }; i.onerror = () => res(); i.src = src; }); }
function loadAssets() {
  const p = [];
  TERRAIN_FILES.forEach((f, i) => p.push(loadImg('t' + i, '/grafiikka/maasto/' + f + '.png')));
  for (const u of ['tolkkijussi', 'lahiojermu', 'mopopoika']) for (const c of ['sininen', 'punainen']) p.push(loadImg(u + '_' + c, `/grafiikka/yksikot/${u}_${c}.png`));
  p.push(loadImg('paamaja_sininen', '/grafiikka/rakennukset/paamaja_sininen.png'));
  p.push(loadImg('paamaja_punainen', '/grafiikka/rakennukset/paamaja_punainen.png'));
  p.push(loadImg('kmarket', '/grafiikka/rakennukset/kmarket.png'));
  p.push(loadImg('baari', '/grafiikka/rakennukset/baari.png'));
  p.push(loadImg('tolkki', '/grafiikka/ikonit/tolkki_16.png'));
  for (const f of Object.values(EXTRA_BUILDINGS)) p.push(loadImg('b_' + f, `/grafiikka/rakennukset/${f}.png`));
  return Promise.all(p);
}

// ---------- äänet ----------
const audioExt = new Audio().canPlayType('audio/ogg') ? 'ogg' : 'mp3';
const SND = {};
let muted = false, music = null, lastPlay = {};
function snd(name, vol = 0.6, minGap = 60) {
  if (muted) return;
  const now = performance.now(); if (lastPlay[name] && now - lastPlay[name] < minGap) return; lastPlay[name] = now;
  if (!SND[name]) SND[name] = new Audio(`/aanet/${name}.${audioExt}`);
  const a = SND[name].cloneNode(); a.volume = vol; a.play().catch(() => {});
}
function voice(type, key) {
  const opts = { tolkkijussi: { valittu: ['valittu'], kuittaus: ['kuittaus_1', 'kuittaus_2', 'kuittaus_3'], hyokkays: ['kuittaus_1'], baariin: ['baariin'] },
    lahiojermu: { valittu: ['valittu'], kuittaus: ['kuittaus_1', 'kuittaus_2'], hyokkays: ['hyokkays'], kanni: ['kanni'], baariin: ['baariin'] },
    mopopoika: { valittu: ['valittu'], kuittaus: ['kuittaus_1', 'kuittaus_2'], hyokkays: ['hyokkays'], baariin: ['baariin'] } }[type];
  const list = opts && opts[key]; if (!list) return;
  snd(`aani_${type}_${list[Math.floor(Math.random() * list.length)]}`, 0.9, 700);
}
function startMusic() { if (music || muted) return; music = new Audio(`/aanet/musiikki_taistelu.${audioExt}`); music.loop = true; music.volume = 0.4; music.play().catch(() => { music = null; }); }
function toggleMute() { muted = !muted; if (muted && music) { music.pause(); music = null; } else startMusic(); log(muted ? 'Äänet pois.' : 'Äänet päälle.'); }

// ---------- tila ----------
let ws, myTeam = 0, map = null, terrainCanvas = null, started = false, ready = false;
let prev = null, cur = null, curAt = 0, prevAt = 0;
const buildingsById = {};
let selected = new Set(), selBuilding = null, groups = {};
let cam = { x: 0, y: 0, z: 1 };
let mouse = { x: 0, y: 0, down: false, sx: 0, sy: 0, inside: false };
const keys = {};
const effects = []; // laukausviivat ym.
const floaters = [];

const canvas = $('kentta'), ctx = canvas.getContext('2d');
const mini = $('minikartta'), mctx = mini.getContext('2d');

function log(t, cls) { const d = document.createElement('div'); d.textContent = t; if (cls) d.className = cls; const l = $('loki'); l.prepend(d); while (l.children.length > 14) l.lastChild.remove(); }

// ---------- yhteys ----------
const huone = params.get('huone');
if (huone) connect();

function connect() {
  $('aulaNapit').hidden = true;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws?huone=${encodeURIComponent(huone)}&token=${token()}${params.get('harjoitus') === '1' ? '&harjoitus=1' : ''}`);
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.t === 'init') onInit(m);
    else if (m.t === 'lobby') onLobby(m);
    else if (m.t === 'start') onStart();
    else if (m.t === 's') onSnap(m);
    else if (m.t === 'virhe') { alert(m.viesti); }
    else if (m.t === 'chat') log(`${TEAM[m.team].nimi}: ${m.teksti}`);
  };
  ws.onclose = () => { if (started) show('Yhteys katkesi. Lataa sivu uudelleen jatkaaksesi.'); };
}
function sendCmd(o) { if (ws && ws.readyState === 1) ws.send(JSON.stringify(o)); }

function onInit(m) {
  myTeam = m.team; map = m.map;
  for (const b of map.buildings) buildingsById[b.id] = b;
  if (!m.solo) {
    $('linkki').hidden = false;
    $('linkkiKentta').value = `${location.origin}/?huone=${m.huone}`;
  }
}
function onLobby(m) {
  if (!started) $('odotus').textContent = m.present[1] && m.present[2] ? 'Molemmat paikalla – peli alkaa!' : 'Odotetaan vastustajaa…';
  else if (!(m.present[1] && m.present[2]) && !params.get('harjoitus')) log('Vastustaja ei ole yhteydessä (voi palata samalla linkillä).');
}
async function onStart() {
  if (started) return; started = true;
  await loadAssets();
  ready = true;
  $('aula').hidden = true; $('peli').hidden = false;
  buildTerrain(); buildPanel(); resize();
  const h = map.buildings.find(b => b.tyyppi === 'paamaja' && b.owner === myTeam);
  centerOn(h.col + 1, h.row + 1);
  log(`Pelaat: ${TEAM[myTeam].nimi}. Tuhoa vihollisen päämaja!`, TEAM[myTeam].vari);
  log('Vinkki: klikkaa Tölkkijussia ja oikealla tölkkikasaa.');
  requestAnimationFrame(frame);
}

function onSnap(s) {
  prev = cur; prevAt = curAt; cur = s; curAt = performance.now();
  cur.um = new Map(s.u.map(u => [u[0], u]));
  for (const id of [...selected]) if (!cur.um.has(id)) selected.delete(id);
  for (const e of s.ev) handleEvent(e);
  if (ready) updatePanel();
}

function handleEvent(e) {
  const mine = e.owner === myTeam;
  const vis = e.x != null && onScreen(e.x, e.y);
  switch (e.e) {
    case 'ammus': effects.push({ x: e.x, y: e.y, tx: e.tx, ty: e.ty, hit: e.hit, t: 0.12, c: e.owner === 1 ? '#9cf' : '#f99' }); if (vis) snd('sfx_laukaus_' + e.w, 0.25, 90); break;
    case 'kilina': if (mine && vis) snd('sfx_tolkki_kilina', 0.35, 250); break;
    case 'pantti': if (mine) { snd('sfx_tolkki_kilina', 0.6); floaters.push({ x: e.x, y: e.y - 1, t: 1.5, txt: `+${Math.round(e.raha)} €`, c: '#e8c33a' }); } break;
    case 'valtaus': {
      const b = buildingsById[e.b];
      if (e.owner === myTeam) { snd('sfx_valtaus_valmis', 0.8); log(`Vallattu: ${b.nimi} (${b.osm})`, TEAM[myTeam].vari); }
      else if (e.old === myTeam) { snd('sfx_valtaus_menetetty', 0.8); log(`Menetettiin: ${b.nimi}!`, 'punainen'); }
      else log(`${TEAM[e.owner].nimi} valtasi: ${b.nimi}`);
      break;
    }
    case 'kuoli': if (vis) snd('sfx_kuolema', 0.5, 150); if (vis) floaters.push({ x: e.x, y: e.y, t: 1, txt: '✝', c: '#fff' }); if (mine) log(`${map.unitTypes[e.type].nimi} kaatui.`); break;
    case 'kotiin': if (mine) { voice('lahiojermu', 'kanni'); log(`${map.unitTypes[e.type].nimi}: "Mää lähen kotiin..." (liian kännissä)`, 'punainen'); } if (vis) floaters.push({ x: e.x, y: e.y, t: 2, txt: 'lähti kotiin', c: '#ff0' }); break;
    case 'sammui': if (vis || mine) snd('sfx_sammui', 0.7, 500); if (mine) log('Yksikkö sammui! (kännimittari täynnä)'); if (vis) floaters.push({ x: e.x, y: e.y, t: 2, txt: 'Zzz', c: '#ff0' }); break;
    case 'omiin': if (mine) log('Kännissä ampui omiaan!', 'punainen'); break;
    case 'baariin': if (mine) { const bu = cur && cur.um.get(e.id); voice(bu ? bu[1] : 'lahiojermu', 'baariin'); } if (mine) log('Yksikkö lähti baariin!'); if (vis) floaters.push({ x: e.x, y: e.y, t: 2, txt: 'baariin!', c: '#fc6' }); break;
    case 'valmis': if (mine) { snd('sfx_koulutus_valmis', 0.6); voice(e.type, 'valittu'); log(`${map.unitTypes[e.type].nimi} valmis.`); } break;
    case 'tuhoutui': snd('sfx_rakennus_tuhoutui', 0.9); break;
    case 'voitto': show(e.winner === myTeam ? 'VOITTO!<br><small>Vihollisen päämaja on tuhottu.</small>' : 'TAPPIO<br><small>Päämajasi tuhottiin.</small>'); break;
  }
}
function show(html) { const i = $('ilmoitus'); i.innerHTML = html + '<br><button onclick="location.href=\'/\'">Uusi peli</button>'; i.hidden = false; }

// ---------- maasto ----------
function buildTerrain() {
  terrainCanvas = document.createElement('canvas');
  terrainCanvas.width = map.cols * TS; terrainCanvas.height = map.rows * TS;
  const t = terrainCanvas.getContext('2d');
  for (let r = 0; r < map.rows; r++) for (let c = 0; c < map.cols; c++) {
    const id = map.terrain[r][c]; const im = IMG['t' + id];
    if (im) t.drawImage(im, c * TS, r * TS, TS, TS); else { t.fillStyle = MINI_COLORS[id]; t.fillRect(c * TS, r * TS, TS, TS); }
  }
}

// ---------- paneeli ----------
function buildPanel() {
  $('joukkue').innerHTML = `<span class="${TEAM[myTeam].vari}">${TEAM[myTeam].nimi}</span>`;
  const k = $('koulutus'); k.innerHTML = '';
  for (const [key, type] of Object.entries(TRAIN_KEYS)) {
    const t = map.unitTypes[type];
    const b = document.createElement('button'); b.id = 'kouluta_' + type;
    b.textContent = `[${key.toUpperCase()}] ${t.nimi} – ${t.hinta} €`;
    b.title = t.ase ? `${t.ase.nimi}, HP ${t.hp}` : `Kerää tölkkejä (kantaa ${t.kantaa}), HP ${t.hp}`;
    b.onclick = () => { sendCmd({ t: 'train', type }); snd('sfx_ui_klikkaus', 0.5); };
    k.appendChild(b);
  }
}
let lastPanel = 0;
function updatePanel() {
  const now = performance.now(); if (now - lastPanel < 150) return; lastPanel = now;
  const p = cur.p[myTeam];
  $('raha').textContent = `Pantit: ${p.money} €`;
  for (const type of Object.values(TRAIN_KEYS)) $('kouluta_' + type).disabled = p.money < map.unitTypes[type].hinta || p.queue.length >= 5;
  $('jono').textContent = p.queue.length ? 'Koulutus: ' + p.queue.map((q, i) => i === 0 ? `${map.unitTypes[q[0]].nimi} ${Math.ceil(q[1])}s` : map.unitTypes[q[0]].nimi).join(', ') : '';
  const v = $('valinta');
  if (selected.size) {
    const us = [...selected].map(id => cur.um.get(id)).filter(Boolean);
    if (us.length === 1) {
      const u = us[0], t = map.unitTypes[u[1]];
      v.innerHTML = `<b>${t.nimi}</b> <small>(${STATE_FI[u[8]] || u[8]})</small><br>HP ${u[5]}/${t.hp}<div class="mittari"><div style="width:${u[5] / t.hp * 100}%;background:#4c4"></div></div>` +
        `Kännimittari ${u[6]} %<div class="mittari"><div style="width:${u[6]}%;background:${kColor(u[6])}"></div></div>` +
        `<small>${kText(u[6])}</small>` + (t.kantaa ? `<br>Tölkkejä: ${u[7]}/${t.kantaa}` : '') + (t.ase ? `<br><small>Ase: ${t.ase.nimi}</small>` : '');
    } else {
      const cnt = {}; us.forEach(u => cnt[u[1]] = (cnt[u[1]] || 0) + 1);
      const avgK = Math.round(us.reduce((a, u) => a + u[6], 0) / us.length);
      v.innerHTML = `<b>${us.length} yksikköä</b><br>` + Object.entries(cnt).map(([k, n]) => `${n}× ${map.unitTypes[k].nimi}`).join('<br>') +
        `<br>Kännit keskim. ${avgK} %<div class="mittari"><div style="width:${avgK}%;background:${kColor(avgK)}"></div></div>`;
    }
  } else if (selBuilding) {
    const b = buildingsById[selBuilding], s = cur.b.find(x => x[0] === b.id);
    v.innerHTML = `<b>${b.nimi}</b><br><small>${b.osm}</small><br>Omistaja: <span class="${TEAM[s[1]].vari || ''}">${TEAM[s[1]].nimi}</span>` +
      (b.maxhp ? `<br>HP ${s[4]}/${b.maxhp}` : '') + (s[3] > 0 ? `<br>Valtaus (${TEAM[s[2]].nimi}): ${Math.round(s[3] * 100)} %` : '') + `<br><small>${b.kuvaus}</small>`;
  } else v.innerHTML = '<small>Valitse yksiköitä hiirellä. Oikea klikkaus antaa käskyn.</small>';
}
function kColor(k) { return k < 20 ? '#8c8' : k < 60 ? '#ec3' : k < 85 ? '#f80' : '#f22'; }
function kText(k) { return k < 20 ? 'Selvä.' : k < 60 ? 'Pieni hiprakka: +25 % vahinko, tarkempi.' : k < 85 ? 'Humalassa: hitaampi, epätarkka.' : 'TÄYSI KÄNNI: voi sammua, lähteä kotiin, baariin tai ampua omia! Vie päämajan lähelle selviämään.'; }

// ---------- kamera ja koordinaatit ----------
function viewW() { return canvas.width; } function viewH() { return canvas.height; }
function resize() { canvas.width = window.innerWidth - PANEL; canvas.height = window.innerHeight; ctx.imageSmoothingEnabled = false; clampCam(); }
window.addEventListener('resize', () => started && resize());
function clampCam() { if (!map) return; const ww = map.cols * TS * cam.z, wh = map.rows * TS * cam.z; cam.x = Math.max(0, Math.min(cam.x, ww - viewW())); cam.y = Math.max(0, Math.min(cam.y, wh - viewH())); }
function centerOn(tx, ty) { cam.x = tx * TS * cam.z - viewW() / 2; cam.y = ty * TS * cam.z - viewH() / 2; clampCam(); }
function toWorld(sx, sy) { return [(sx + cam.x) / (TS * cam.z), (sy + cam.y) / (TS * cam.z)]; }
function toScreen(tx, ty) { return [tx * TS * cam.z - cam.x, ty * TS * cam.z - cam.y]; }
function onScreen(tx, ty) { const [x, y] = toScreen(tx, ty); return x > -40 && y > -40 && x < viewW() + 40 && y < viewH() + 40; }

// ---------- syöte ----------
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('mousemove', e => { mouse.x = e.offsetX; mouse.y = e.offsetY; mouse.inside = true; });
canvas.addEventListener('mouseleave', () => { mouse.inside = false; });
canvas.addEventListener('mousedown', e => {
  startMusic();
  if (e.button === 0) { mouse.down = true; mouse.sx = e.offsetX; mouse.sy = e.offsetY; }
  if (e.button === 2) rightClick(e.offsetX, e.offsetY);
});
window.addEventListener('mouseup', e => {
  if (e.button !== 0 || !mouse.down) return; mouse.down = false;
  if (!cur) return;
  const [ax, ay] = toWorld(Math.min(mouse.sx, mouse.x), Math.min(mouse.sy, mouse.y));
  const [bx, by] = toWorld(Math.max(mouse.sx, mouse.x), Math.max(mouse.sy, mouse.y));
  const add = e.shiftKey;
  if (!add) selected.clear();
  selBuilding = null;
  const isBox = Math.abs(mouse.x - mouse.sx) > 5 || Math.abs(mouse.y - mouse.sy) > 5;
  if (isBox) {
    for (const u of cur.u) if (u[2] === myTeam) { const [x, y] = lerpPos(u); if (x >= ax && x <= bx && y >= ay - 0.4 && y <= by + 0.2) selected.add(u[0]); }
  } else {
    const u = unitAt(ax, ay, true);
    if (u) selected.add(u[0]);
    else { const b = buildingAt(ax, ay); if (b) selBuilding = b.id; }
  }
  if (selected.size) { const u = cur.um.get([...selected][0]); voice(u[1], 'valittu'); }
  updatePanel(lastPanel = 0);
});
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const [wx, wy] = toWorld(e.offsetX, e.offsetY);
  const zs = [1, 1.5, 2]; let i = zs.indexOf(cam.z); i = Math.max(0, Math.min(zs.length - 1, i + (e.deltaY < 0 ? 1 : -1))); cam.z = zs[i];
  cam.x = wx * TS * cam.z - e.offsetX; cam.y = wy * TS * cam.z - e.offsetY; clampCam(); ctx.imageSmoothingEnabled = false;
}, { passive: false });
mini.addEventListener('mousedown', e => { const f = map.cols / mini.width; centerOn(e.offsetX * f, e.offsetY * f); });
mini.addEventListener('contextmenu', e => { e.preventDefault(); const f = map.cols / mini.width; order(e.offsetX * f, e.offsetY * f); });

window.addEventListener('keydown', e => {
  if (!ready) return;
  const k = e.key.toLowerCase(); keys[k] = true;
  if (TRAIN_KEYS[k]) { sendCmd({ t: 'train', type: TRAIN_KEYS[k] }); snd('sfx_ui_klikkaus', 0.5); }
  if (k === 'h') sendCmd({ t: 'stop', ids: [...selected] });
  if (k === 'm') toggleMute();
  if (k === ' ') { e.preventDefault(); const h = map.buildings.find(b => b.tyyppi === 'paamaja' && b.owner === myTeam); if (h) centerOn(h.col + 1, h.row + 1); }
  if (/^[1-9]$/.test(k)) {
    if (e.ctrlKey) { e.preventDefault(); groups[k] = new Set(selected); log(`Ryhmä ${k} tallennettu.`); }
    else if (groups[k]) { selected = new Set([...groups[k]].filter(id => cur.um.has(id))); selBuilding = null; }
  }
  if (k.startsWith('arrow')) e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

function unitAt(x, y, ownOnly) {
  let best = null, bd = 0.6;
  for (const u of cur.u) { if (ownOnly && u[2] !== myTeam) continue; const [ux, uy] = lerpPos(u); const d = Math.hypot(ux - x, uy - 0.25 - y); if (d < bd) { bd = d; best = u; } }
  return best;
}
function buildingAt(x, y) { return map.buildings.find(b => x >= b.col && x < b.col + 2 && y >= b.row - 0.5 && y < b.row + 2); }

function rightClick(sx, sy) { const [x, y] = toWorld(sx, sy); order(x, y); }
function order(x, y) {
  if (!selected.size || !cur) return;
  const ids = [...selected];
  // äänikuittaus: hyökkäys jos vihollinen alla
  const enemy = unitAt(x, y, false); const b = buildingAt(x, y);
  const attack = (enemy && enemy[2] !== myTeam) || (b && b.tyyppi === 'paamaja' && cur.b.find(s => s[0] === b.id)[1] !== myTeam);
  const first = cur.um.get(ids[0]);
  if (first) { voice(first[1], attack ? 'hyokkays' : 'kuittaus'); if (first[1] === 'mopopoika') snd('sfx_mopo', 0.4, 1500); }
  sendCmd({ t: 'order', ids, x, y: enemy && enemy[2] !== myTeam ? lerpPos(enemy)[1] : y });
  effects.push({ mark: true, x, y, t: 0.5, c: attack ? '#f44' : '#4f4' });
}

// ---------- piirto ----------
function lerpPos(u) {
  if (!prev || !prev.um) return [u[3], u[4]];
  const p = prev.um.get(u[0]); if (!p) return [u[3], u[4]];
  const a = Math.min(1, (performance.now() - curAt) / Math.max(1, curAt - prevAt));
  return [p[3] + (u[3] - p[3]) * a, p[4] + (u[4] - p[4]) * a];
}

let lastFrame = performance.now();
function frame(now) {
  const dt = Math.min(0.1, (now - lastFrame) / 1000); lastFrame = now;
  // kameran liike
  const sp = 700 * dt;
  if (keys['arrowleft'] || keys['a'] || (mouse.inside && mouse.x < 12)) cam.x -= sp;
  if (keys['arrowright'] || keys['d'] || (mouse.inside && mouse.x > viewW() - 12)) cam.x += sp;
  if (keys['arrowup'] || keys['w'] || (mouse.inside && mouse.y < 12)) cam.y -= sp;
  if (keys['arrowdown'] || keys['s'] || (mouse.inside && mouse.y > viewH() - 12)) cam.y += sp;
  clampCam();
  draw(dt);
  requestAnimationFrame(frame);
}

function draw(dt) {
  const z = cam.z, S = TS * z;
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, viewW(), viewH());
  ctx.drawImage(terrainCanvas, cam.x / z, cam.y / z, viewW() / z, viewH() / z, 0, 0, viewW(), viewH());
  if (!cur) return;

  // tölkit
  for (const c of cur.c) {
    if (!onScreen(c[1], c[2])) continue;
    const [x, y] = toScreen(c[1], c[2]);
    const n = Math.min(3, Math.ceil(c[3] / 3));
    for (let i = 0; i < n; i++) { if (IMG.tolkki) ctx.drawImage(IMG.tolkki, x - 8 * z + (i - 1) * 5 * z, y - 8 * z - (i % 2) * 3 * z, 16 * z, 16 * z); else { ctx.fillStyle = '#ccc'; ctx.fillRect(x - 3, y - 3, 6, 6); } }
    ctx.fillStyle = '#fff'; ctx.font = `${10 * z}px monospace`; ctx.fillText(c[3], x + 8 * z, y + 8 * z);
  }

  // rakennukset + yksiköt syvyysjärjestyksessä
  const items = [];
  for (const b of map.buildings) items.push({ y: b.row + 2, b });
  for (const u of cur.u) { const [x, y] = lerpPos(u); items.push({ y, u, x }); }
  items.sort((a, b) => a.y - b.y);
  for (const it of items) it.b ? drawBuilding(it.b) : drawUnit(it.u, it.x, it.y);

  // efektit
  for (let i = effects.length - 1; i >= 0; i--) {
    const e = effects[i]; e.t -= dt; if (e.t <= 0) { effects.splice(i, 1); continue; }
    if (e.mark) { const [x, y] = toScreen(e.x, e.y); ctx.strokeStyle = e.c; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, (1 - e.t * 2) * 10 * z + 3, 0, 7); ctx.stroke(); continue; }
    const [x1, y1] = toScreen(e.x, e.y - 0.35), [x2, y2] = toScreen(e.tx + (e.hit ? 0 : 0.4), e.ty - 0.3 + (e.hit ? 0 : 0.3));
    ctx.strokeStyle = e.c; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }
  ctx.font = `bold ${12 * z}px monospace`; ctx.textAlign = 'center';
  for (let i = floaters.length - 1; i >= 0; i--) {
    const f = floaters[i]; f.t -= dt; if (f.t <= 0) { floaters.splice(i, 1); continue; }
    const [x, y] = toScreen(f.x, f.y - (2 - f.t) * 0.5); ctx.fillStyle = '#000'; ctx.fillText(f.txt, x + 1, y + 1); ctx.fillStyle = f.c; ctx.fillText(f.txt, x, y);
  }
  ctx.textAlign = 'left';

  // valintalaatikko
  if (mouse.down) { ctx.strokeStyle = '#4f4'; ctx.lineWidth = 1; ctx.strokeRect(mouse.sx + 0.5, mouse.sy + 0.5, mouse.x - mouse.sx, mouse.y - mouse.sy); }
  drawMini();
}

function drawBuilding(b) {
  if (!onScreen(b.col + 1, b.row + 1)) return;
  const z = cam.z, S = TS * z;
  const s = cur.b.find(x => x[0] === b.id); const owner = s[1];
  const [x, y] = toScreen(b.col, b.row);
  // omistajan merkki maassa
  ctx.fillStyle = TEAM[owner].css + '55'; ctx.fillRect(x - 2, y - 2, 2 * S + 4, 2 * S + 4);
  ctx.strokeStyle = TEAM[owner].css; ctx.lineWidth = 2; ctx.strokeRect(x - 2, y - 2, 2 * S + 4, 2 * S + 4);
  let im = null;
  if (b.tyyppi === 'paamaja') im = IMG['paamaja_' + (owner === 2 ? 'punainen' : 'sininen')];
  else if (b.tyyppi === 'kmarket') im = IMG.kmarket; else if (b.tyyppi === 'baari') im = IMG.baari; else im = IMG['b_' + EXTRA_BUILDINGS[b.nimi]];
  if (im) ctx.drawImage(im, x, y, 2 * S, 2 * S);
  else { // placeholder
    ctx.fillStyle = '#5a5248'; ctx.fillRect(x + 4 * z, y + 10 * z, 2 * S - 8 * z, 2 * S - 12 * z);
    ctx.fillStyle = '#3a342e'; ctx.fillRect(x + 2 * z, y + 6 * z, 2 * S - 4 * z, 6 * z);
    ctx.fillStyle = '#ffd'; ctx.font = `bold ${7 * z}px monospace`; ctx.textAlign = 'center';
    ctx.fillText(b.nimi.split(/[- ]/)[0].slice(0, 10), x + S, y + S + 4 * z); ctx.textAlign = 'left';
  }
  if (selBuilding === b.id) { ctx.strokeStyle = '#fff'; ctx.strokeRect(x - 3, y - 3, 2 * S + 6, 2 * S + 6); }
  // nimi pienellä
  if (z >= 1) { ctx.font = `${9 * z}px monospace`; ctx.fillStyle = '#000'; ctx.fillText(b.nimi, x + 1, y - 4 + 1); ctx.fillStyle = '#fff'; ctx.fillText(b.nimi, x, y - 4); }
  // HP / valtaus
  if (b.maxhp) bar(x, y + 2 * S + 3, 2 * S, s[4] / b.maxhp, '#4c4');
  if (s[3] > 0) bar(x, y + 2 * S + 8, 2 * S, s[3], TEAM[s[2]].css);
}
function bar(x, y, w, f, c) { ctx.fillStyle = '#000'; ctx.fillRect(x, y, w, 4); ctx.fillStyle = c; ctx.fillRect(x, y, w * Math.max(0, f), 4); }

function drawUnit(u, ux, uy) {
  if (!onScreen(ux, uy)) return;
  const z = cam.z, S = TS * z;
  const [x, y] = toScreen(ux, uy);
  const sel = selected.has(u[0]);
  if (sel) { ctx.strokeStyle = '#4f4'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(x, y, 9 * z, 4 * z, 0, 0, 7); ctx.stroke(); }
  const im = IMG[u[1] + '_' + (u[2] === 2 ? 'punainen' : 'sininen')];
  ctx.save();
  // ankkuri (0.5, 0.875)
  const dx = x, dy = y;
  ctx.translate(dx, dy);
  if (u[8] === 'sammunut') ctx.rotate(Math.PI / 2);
  if (u[9] < 0) ctx.scale(-1, 1);
  if (im) ctx.drawImage(im, -S / 2, -S * 0.875, S, S);
  else { ctx.fillStyle = TEAM[u[2]].css; ctx.fillRect(-6 * z, -20 * z, 12 * z, 18 * z); }
  ctx.restore();
  const t = map.unitTypes[u[1]];
  const by = y - S * 0.95;
  if (sel || u[5] < t.hp) bar(x - 10 * z, by, 20 * z, u[5] / t.hp, u[2] === myTeam ? '#4c4' : '#e44');
  // kännimittari omille
  if (u[2] === myTeam) { ctx.fillStyle = '#000'; ctx.fillRect(x - 10 * z, by + 4, 20 * z, 3); ctx.fillStyle = kColor(u[6]); ctx.fillRect(x - 10 * z, by + 4, 20 * z * u[6] / 100, 3); }
  if (u[7] > 0 && IMG.tolkki) { ctx.drawImage(IMG.tolkki, x + 5 * z, y - 14 * z, 10 * z, 10 * z); }
  if (u[8] === 'sammunut') { ctx.fillStyle = '#ff0'; ctx.font = `${10 * z}px monospace`; ctx.fillText('Zzz', x + 6 * z, y - 18 * z); }
}

let miniBase = null;
function drawMini() {
  const W = mini.width, f = W / map.cols;
  if (!miniBase) {
    miniBase = document.createElement('canvas'); miniBase.width = W; miniBase.height = W; const m = miniBase.getContext('2d');
    for (let r = 0; r < map.rows; r++) for (let c = 0; c < map.cols; c++) { m.fillStyle = MINI_COLORS[map.terrain[r][c]]; m.fillRect(c * f, r * f, Math.ceil(f), Math.ceil(f)); }
  }
  mctx.drawImage(miniBase, 0, 0);
  for (const b of map.buildings) { const s = cur.b.find(x => x[0] === b.id); mctx.fillStyle = TEAM[s[1]].css; mctx.fillRect(b.col * f, b.row * f, 2 * f, 2 * f); mctx.strokeStyle = '#fff'; mctx.lineWidth = 1; mctx.strokeRect(b.col * f, b.row * f, 2 * f, 2 * f); }
  mctx.fillStyle = '#ddd'; for (const c of cur.c) mctx.fillRect(c[1] * f - 1, c[2] * f - 1, 2, 2);
  for (const u of cur.u) { mctx.fillStyle = u[2] === 1 ? '#6af' : '#f66'; mctx.fillRect(u[3] * f - 1.5, u[4] * f - 1.5, 3, 3); }
  mctx.strokeStyle = '#fff'; mctx.lineWidth = 1;
  mctx.strokeRect(cam.x / (TS * cam.z) * f, cam.y / (TS * cam.z) * f, viewW() / (TS * cam.z) * f, viewH() / (TS * cam.z) * f);
}
})();
