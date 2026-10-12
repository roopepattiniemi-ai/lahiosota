'use strict';
// Lähiösota: Etelä-Tampere – selainasiakas (Canvas 2D, ei riippuvuuksia)
(() => {
const TS = 32; // ruudun koko pikseleinä (grafiikka 32x32)
const PANEL = 215;
const TEAM = { 1: { nimi: 'Multisilta', vari: 'sininen', varinimi: 'sininen', suunta: 'etelässä', css: '#1f6fe0' }, 2: { nimi: 'Peltolammi', vari: 'punainen', varinimi: 'punainen', suunta: 'pohjoisessa', css: '#d8262b' }, 3: { nimi: 'Olennot', css: '#6a4' }, 0: { nimi: 'Puolueeton', css: '#999' } };
const TERRAIN_FILES = ['00_ruoho', '01_metsa', '02_vesi', '03_tie', '04_moottoritie', '05_rata', '06_rakennus', '07_teollisuus', '08_pelto', '09_suo', '10_kallio', '11_puisto', '12_silta', '13_polku'];
const MINI_COLORS = ['#4d7a35', '#2b4d22', '#2d5a8c', '#777', '#555', '#6b5a48', '#8a8a8a', '#666158', '#9a9a4a', '#4f5f3a', '#7a7066', '#5f9a45', '#8a6a3a', '#9c7e50'];
const EXTRA_BUILDINGS = { 'PIZZATEHDAS': 'pizzatehdas', 'KARKKIKAIVOS': 'karkkikaivos', 'LÄÄKINTÄASEMA': 'laakintaasema', 'TIEDUSTELUKESKUS': 'tiedustelukeskus',
  'KAHVILÄHDE': 'kahvilahde', 'PERUNAPELTO': 'perunapelto', 'HUOLTOVARIKKO': 'huoltovarikko', 'ROMUTARVIKEVARASTO': 'romutarvikevarasto',
  'POLTTOAINEVARASTO': 'polttoainevarasto', 'KAASUVARASTO': 'kaasuvarasto', 'LIHAPULLALINNAKE': 'lihapullalinnake', 'Sauna': 'sauna', 'Pihagrilli': 'pihagrilli', 'Kirpputori': 'kirpputori' };
let TRAIN_KEYS = {}; // täytetään yksikkötyypeistä (nappi-kenttä) omalle puolelle
const WEAPON_SFX = { rk62: 'sfx_laukaus_rk62', jatimatic: 'sfx_laukaus_jatimatic', emma: 'sfx_laukaus_emma', suomikp: 'sfx_laukaus_suomikp', puukko: 'sfx_puukko',
  parveke: 'sfx_parveke_ampuu', trimmeri: 'sfx_trimmeri', grilli: 'sfx_grilli_ampuu', kivi: 'sfx_peikko_kivi_heitto', hiisi: 'sfx_vesihiisi_hyokkays', pallo: 'sfx_pallo_potku', salama: 'sfx_vesihiisi_hyokkays' };
const MOVE_SFX = { mopopoika: 'sfx_mopo', dnepr: 'sfx_dnepr', volvo: 'sfx_volvo', monkija: 'sfx_monkija', lada: 'sfx_lada', mummo: 'sfx_rollaattori' };
const VOICES = {
  tolkkijussi: ['valittu', 'kuittaus_1', 'kuittaus_2', 'kuittaus_3', 'baariin'],
  lahiojermu: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'kanni', 'baariin'],
  mopopoika: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'baariin'],
  parvekeampuja: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'baariin'],
  mummo: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'baariin'],
  isa_trimmeri: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'baariin'],
  grillimestari: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays', 'baariin'],
  volvo: ['valittu', 'kuittaus_1', 'kuittaus_2', 'hyokkays'],
  dnepr: ['valittu', 'kuittaus_1', 'hyokkays'],
  monkija: ['valittu', 'kuittaus_1'], lada: ['valittu', 'kuittaus_1'],
};
// Humalakuplat: [tekstit, äänet]
const KUPLAT = {
  1: [['Kippis!', 'Skool!', 'Nyt maistuu!', 'Hyvä meininki!', 'Tästä se lähtee!'], ['sfx_kippis_kilistys', 'aani_kanni_kippis']],
  2: [['Yks vielä!', 'Hik!', 'Mää oon ihan selvä!', 'Kuka siirsi tietä?', 'Sä oot mun paras kaveri!'], ['aani_kanni_yks_viela', 'sfx_hikka_1', 'sfx_hikka_2']],
  3: [['Mihin tää tie loppuu?', 'Hik! Hik!', 'Kaikki pyörii...'], ['sfx_hikka_3', 'aani_kanni_hik']],
  hik: [['Hik!', '*hik*', 'Hik! ...anteeks.', 'Hiks!'], ['sfx_hikka_1', 'sfx_hikka_2', 'sfx_hikka_3', 'aani_kanni_hik']],
  laatta: [['Nyt lentää laatta!', 'Bläääh!', 'Ei olis pitäny...', 'Se kebabi...'], ['aani_kanni_laatta_1', 'aani_kanni_laatta_2', 'sfx_yokkays_1', 'sfx_yokkays_2']],
  sammui: [['Zzz...', 'Mää vaan lepuutan silmiä...', 'Zzz... äiti...'], ['sfx_sammui']],
  omiin: [['Ups, sori!', 'Ai se oli meikäläinen?', 'Ei ollu tarkotus!'], ['aani_kanni_ups_sori']],
  baariin: [['Baariin!', 'Yhet pikaset!', 'Mää käyn yhellä...'], ['aani_kanni_baariin']],
  kotiin: [['Mää lähen kotiin...', 'Mää meen nukkuun.', 'Huomenna uusiks...'], ['aani_kanni_kotiin']],
  putkaan: [['Mää en oo tehny mitään!', 'Ei putkaan!', 'Konstaapeli hei...'], ['sfx_poliisi_sireeni']],
};
// olentojen huudot
KUPLAT.mun_metsa = [['MUN METSÄ!', 'GRRAAAH!', 'Pois mun puista!'], ['aani_peikko_mun_metsa', 'sfx_peikko_karjunta_1']];
KUPLAT.tolkit = [['TÖLKIT TÄNNE!', 'Mun tölkit!', 'Kilisee... MUN!'], ['aani_peikko_tolkit']];
KUPLAT.pois = [['POIS!', 'HÄIPYKÄÄ!', 'RAAAAH!'], ['aani_peikko_pois', 'sfx_peikko_karjunta_2']];
KUPLAT.nalka = [['Peikolla nälkä...', 'Mmm... jermu...', 'Grrr...'], ['aani_peikko_nalka', 'sfx_peikko_murina_1', 'sfx_peikko_murina_2', 'sfx_peikko_murina_3']];
KUPLAT.hiisi = [['Tulkaa syvyyksiin...', 'Sssssss...', 'Vesi on lämmintä...', 'SSSHHHH!'], ['aani_vesihiisi_tulkaa', 'aani_vesihiisi_syvyyksiin', 'aani_vesihiisi_sss', 'sfx_vesihiisi_sihina_1', 'sfx_vesihiisi_sihina_2', 'sfx_vesihiisi_sihina_3']];
KUPLAT.tekstari = [['Ootsä hereil? <3', 'Mä vieläki rakastan sua', 'Muistaksä meiän kesän?', 'Sori siitä... soita'], ['sfx_tekstiviesti']];
KUPLAT.vana = [['TÄNNE SE PALLO!', 'Maali!', 'Vänä potkii!'], ['sfx_pallo_potku']];
const olentoMerkki = {}; // id -> merkin loppuaika
const PAKKO = { tekstari: 1, hiisi: 1, sammui: 1, kotiin: 1, putkaan: 1, laatta: 1 }; // nämä ohittavat 8 s rajan
const STATE_FI = { board: 'nousee kyytiin', molotovi: 'heittää molotovia', jono: 'Alkon jonossa',  idle: 'odottaa', move: 'liikkuu', attack: 'hyökkää', collect: 'kerää tölkkejä', return: 'vie pantteja', gohome: 'palaa keräämään', tobar: 'lähti baariin!', sammunut: 'SAMMUNUT', talo: 'menee kerrostaloon', tosauna: 'menee saunaan', sauna: 'SAUNASSA (ei puolusta)', kirppu: 'menee kirpputorille', lahjo: 'lahjoo mummoa', syo: 'syö kasveja' };

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
  for (const [k, n] of [['peikko', 1], ['peikko_kavely', 4], ['peikko_hyokkays', 4], ['peikko_karjuu', 2], ['peikko_kaatunut', 1], ['vesihiisi', 1], ['vesihiisi_nousu', 6], ['vesihiisi_hyokkays', 4], ['vesihiisi_sukellus', 6]]) p.push(loadImg('o_' + k, `/grafiikka/olennot/${k}.png`));
  for (const k of ['hemuli', 'hemuli_kavely', 'hemuli_syo', 'hemuli_caesar', 'hemuli_caesar_kavely', 'hemuli_caesar_hyokkays', 'vana', 'vana_kavely', 'vana_potku', 'pullomummo', 'pullomummo_kavely']) p.push(loadImg('o_' + k, `/grafiikka/olennot/${k}.png`));
  for (const k of ['kivi_8', 'kuplat_32', 'loiske_32', 'jalkapallo_8', 'lumi_64', 'poliisipiiritys_64']) p.push(loadImg('fx_' + k, `/grafiikka/efektit/${k}.png`));
  for (const k of ['peikot', 'vesihiisi']) p.push(loadImg('tap_' + k, `/grafiikka/ikonit/tapahtuma_${k}.png`));
  for (const [u, t] of Object.entries(map.unitTypes)) {
    if (t.olento) continue;
    const dir = t.luokka === 'ajoneuvo' ? 'ajoneuvot' : 'yksikot';
    for (const c of ['sininen', 'punainen']) {
      for (const suf of ['', '_kavely', '_ampuu', '_sammunut']) if (!(suf === '_ampuu' && !t.ase) && !(suf === '_sammunut' && t.luokka === 'ajoneuvo')) p.push(loadImg(u + '_' + c + suf, `/grafiikka/${dir}/${u}_${c}${suf}.png`));
      p.push(loadImg('ui_' + u + '_' + c, `/grafiikka/ikonit/ui_${u}${c === 'punainen' ? '_punainen' : ''}.png`));
    }
  }
  p.push(loadImg('poliisiauto_sininen', '/grafiikka/ajoneuvot/poliisiauto.png'));
  p.push(loadImg('poliisiauto_sininen_kavely', '/grafiikka/ajoneuvot/poliisiauto_kavely.png'));
  for (const f of ['suuliekki_8', 'makkara_8', 'molotovi_16', 'zzz_16', 'rajahdys_64', 'tuli_32', 'sade_64', 'kary_32', 'kirppis_tolkkikasa_32', 'sauna_32', 'kesajuhlat_32',
    'laatta_latta_1', 'laatta_latta_2', 'laatta_latta_3', 'laatta_hoyry']) p.push(loadImg('fx_' + f, `/grafiikka/efektit/${f}.png`));
  p.push(loadImg('alko', '/grafiikka/rakennukset/alko.png'));
  for (const f of ['tapahtuma_banneri', 'tapahtuma_karttamerkki', 'puoli_sininen', 'puoli_punainen', 'puoli_molemmat']) p.push(loadImg('ui_' + f, `/grafiikka/ui/${f}.png`));
  p.push(loadImg('kartta_tausta', '/grafiikka/kartta/kartta_tausta.png'));
  p.push(loadImg('minikartta', '/grafiikka/kartta/minikartta_256.png'));
  for (const k of Object.keys(map.tapahtumat)) p.push(loadImg('tap_' + k, `/grafiikka/ikonit/tapahtuma_${k}.png`));
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
  const av = VOICES[type]; if (!av) return;
  let list = av.filter(k => k === key || (key === 'kuittaus' && k.startsWith('kuittaus')));
  if (!list.length && key === 'hyokkays') list = av.filter(k => k.startsWith('kuittaus'));
  if (!list.length) return;
  snd(`aani_${type}_${list[Math.floor(Math.random() * list.length)]}`, 0.9, 700);
}
let loops = {};
function loopSnd(name, on, vol = 0.4) {
  if (on && !muted) { if (!loops[name]) { const a = new Audio(`/aanet/${name}.${audioExt}`); a.loop = true; a.volume = vol; a.play().catch(() => {}); loops[name] = a; } }
  else if (loops[name]) { loops[name].pause(); delete loops[name]; }
}
// Musiikki: soittolista satunnaisessa järjestyksessä, ei samaa kahdesti peräkkäin. Valikossa oma teema.
const PLAYLIST = ['musiikki_taistelu', 'musiikki_piiritys', 'musiikki_kannirynnakko'];
let musicVol = +(localStorage.getItem('lahiosota_musiikki') ?? 0.4), lastTrack = null, menuMusic = null;
function nextTrack() { const opts = PLAYLIST.filter(t => t !== lastTrack); lastTrack = opts[Math.floor(Math.random() * opts.length)]; return lastTrack; }
function startMusic() {
  if (menuMusic) { menuMusic.pause(); menuMusic = null; }
  if (music || muted || !ready) return;
  music = new Audio(`/aanet/${nextTrack()}.${audioExt}`); music.volume = musicVol;
  music.onended = () => { music = null; startMusic(); };
  music.play().catch(() => { music = null; });
}
function startMenuMusic() { if (menuMusic || muted || ready) return; menuMusic = new Audio(`/aanet/musiikki_valikko.${audioExt}`); menuMusic.loop = true; menuMusic.volume = musicVol; menuMusic.play().catch(() => { menuMusic = null; }); }
document.addEventListener('click', () => { if (!ready) startMenuMusic(); }, { once: false });
function setMusicVol(v) { musicVol = v; localStorage.setItem('lahiosota_musiikki', v); if (music) music.volume = v; if (menuMusic) menuMusic.volume = v; }
function toggleMute() { muted = !muted; if (muted) { for (const k of Object.keys(loops)) loopSnd(k, false); if (music) { music.pause(); music = null; } if (menuMusic) { menuMusic.pause(); menuMusic = null; } } else startMusic(); log(muted ? 'Äänet pois.' : 'Äänet päälle.'); const mb = $('mykistys'); if (mb) mb.textContent = muted ? '🔇' : '🔊'; }

// ---------- tila ----------
let reconnects = 0, gameOver = false, centeredOnce = false;
let ws, myTeam = 0, map = null, terrainCanvas = null, started = false, ready = false;
let prev = null, cur = null, curAt = 0, prevAt = 0;
const buildingsById = {};
let selected = new Set(), selBuilding = null, groups = {};
let cam = { x: 0, y: 0, z: 1 };
let mouse = { x: 0, y: 0, down: false, sx: 0, sy: 0, inside: false };
const keys = {};
const effects = []; // laukausviivat ym.
const bubbles = [];  // humalakuplat
const lastBubble = {}, lastBubbleSnd = {}, shootT = {};
let globalBubbleSnd = 0, molotovMode = false, lastTap = null;
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
  ws.onopen = () => { reconnects = 0; };
  ws.onclose = () => {
    if (gameOver) return;
    if (reconnects++ < 8) { if (started) log('Yhteys katkesi, yhdistetään uudelleen…', 'punainen'); setTimeout(connect, 1000 + reconnects * 500); }
    else if (started) show('Yhteys katkesi. Lataa sivu uudelleen jatkaaksesi.');
  };
}
function sendCmd(o) { if (ws && ws.readyState === 1) ws.send(JSON.stringify(o)); }
if (params.get('harjoitus') === '1') window.__lahiosota = { send: (o) => sendCmd(o), tila: () => cur }; // testikoukku vain harjoituksessa

function onInit(m) {
  if (started && myTeam && m.team !== myTeam) { log(`Huom: palvelin vaihtoi puolesi: olet nyt ${TEAM[m.team].nimi}.`, 'punainen'); }
  myTeam = m.team; map = m.map;
  document.body.dataset.team = TEAM[myTeam].vari;
  $('aulaPuoli').innerHTML = teamBadge();
  if (started) { $('joukkue').innerHTML = teamBadge(); centerOnHQ(); }
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
  centerOnHQ();
  showBanner();
  log(`Pelaat: ${TEAM[myTeam].nimi} (${TEAM[myTeam].varinimi}). Tuhoa vihollisen päämaja!`, TEAM[myTeam].vari);
  log('Vinkki: klikkaa Tölkkijussia ja oikealla tölkkikasaa.');
  startMusic();
  requestAnimationFrame(frame);
}

function teamBadge() { const t = TEAM[myTeam]; return `Olet <span class="${t.vari}">${t.nimi.toUpperCase()}</span> <small>(${t.varinimi}, ${t.suunta})</small>`; }
function myHQ() { return map.buildings.find(b => b.tyyppi === 'paamaja' && b.owner === myTeam); }
function centerOnHQ() { const h = myHQ(); if (h) centerOn(h.col + 1, h.row + 1.5); }
function showBanner() {
  const t = TEAM[myTeam]; const el = $('banneri');
  el.innerHTML = `OLET <span class="${t.vari}">${t.nimi.toUpperCase()}</span><br><small>${t.varinimi} – päämajasi on ${t.suunta}</small>`;
  el.className = 'banneri ' + t.vari; el.hidden = false;
  setTimeout(() => { el.hidden = true; }, 5000);
}

function onSnap(s) {
  prev = cur; prevAt = curAt; cur = s; curAt = performance.now();
  cur.um = new Map(s.u.map(u => [u[0], u]));
  for (const id of [...selected]) if (!cur.um.has(id)) selected.delete(id);
  for (const e of s.ev) handleEvent(e);
  if (ready && !centeredOnce) { centeredOnce = true; centerOnHQ(); }
  if (ready) updatePanel();
}

function handleEvent(e) {
  const mine = e.owner === myTeam;
  const vis = e.x != null && onScreen(e.x, e.y);
  switch (e.e) {
    case 'ammus':
      shootT[e.id] = performance.now();
      if (e.roiske) effects.push({ arc: true, x: e.x, y: e.y, tx: e.tx, ty: e.ty, t: 0.8, t0: 0.8, img: 'fx_makkara_8' });
      else if (e.w === 'kivi') effects.push({ arc: true, x: e.x, y: e.y - 0.6, tx: e.tx, ty: e.ty, t: 0.5, t0: 0.5, img: 'fx_kivi_8', spin: true, osuu: e.hit && vis ? 'sfx_peikko_kivi_osuma' : null });
      else if (e.w === 'pallo') effects.push({ arc: true, x: e.x, y: e.y - 0.2, tx: e.tx, ty: e.ty, t: 0.5, t0: 0.5, img: 'fx_jalkapallo_8', spin: true, osuu: e.hit && vis ? 'sfx_pallo_osuma' : null });
      else if (e.w === 'hiisi') effects.push({ splash: true, x: e.tx, y: e.ty, t: 0.4, t0: 0.4 });
      else if (e.w === 'grilli') effects.push({ arc: true, x: e.x, y: e.y, tx: e.tx, ty: e.ty, t: 0.35, t0: 0.35, img: 'fx_makkara_8', kary: true });
      else if (!e.lahi) effects.push({ x: e.x, y: e.y, tx: e.tx, ty: e.ty, hit: e.hit, t: 0.12, c: e.owner === 1 ? '#9cf' : '#f99', flash: true });
      if (vis) snd(WEAPON_SFX[e.w] || 'sfx_laukaus_rk62', e.w === 'parveke' ? 0.5 : 0.25, 90); break;
    case 'rajahdys': effects.push({ boom: true, x: e.x, y: e.y, t: 0.6, t0: 0.6, small: e.pieni }); break;
    case 'molotovi':
      effects.push({ arc: true, x: e.x, y: e.y, tx: e.tx, ty: e.ty, t: 0.5, t0: 0.5, img: 'fx_molotovi_16', spin: true });
      if (vis || mine) setTimeout(() => snd(e.syttyi ? 'sfx_molotovi' : 'sfx_molotovi_sammuu', 0.7, 100), 350);
      if (mine && !e.syttyi) log('Molotovi ei syttynyt sateessa!');
      if (e.oma) { bubble(e.id, 'omiin', e.x, e.y, true); if (mine) log('Kännissä pudotti molotovin omiin jalkoihin!', 'punainen'); }
      break;
    case 'eirahaa': if (mine) log('Ei rahaa molotoviin (kalja maksaa)!'); break;
    case 'jyrays': if (vis) snd('sfx_ajoneuvo_tormays', 0.6, 300); break;
    case 'kyytiin': if (mine) log(`${map.unitTypes[e.type] ? map.unitTypes[e.type].nimi : 'Ajoneuvo'}: yksikkö nousi kyytiin.`); break;
    case 'taynna': if (mine) log('Kyyti on täynnä!'); break;
    case 'purku': if (mine) log(`${e.n} yksikköä nousi kyydistä.`); break;
    case 'putkaan': bubble(e.id, 'putkaan', e.x, e.y, mine || vis); if (mine) log(`Poliisi vei ${map.unitTypes[e.type].nimi.toLowerCase()}n putkaan!`, 'punainen'); break;
    case 'humala': bubble(e.id, String(e.tila), e.x, e.y, mine || vis);
      if (e.tila === 'laatta' && (mine || vis)) setTimeout(() => snd('sfx_laatta_latsahdys', 0.6, 200), 700); break;
    case 'palasi': if (mine) log(e.sauna ? 'Saunojat palasivat terästettyinä (+30 % vahinko)!' : 'Kokous loppui, joukot palasivat.'); break;
    case 'tapahtuma': onTapahtuma(e); break;
    case 'taloon': if (mine) log(`Yksikkö meni kerrostaloon (${e.n}/6).`); break;
    case 'talosta': if (mine) log(`${e.n} yksikköä tuli ulos kerrostalosta.`); break;
    case 'bileet': if (mine) log('Kerrostalossa alkoi kotibileet! (4–5 sisällä)', 'tapahtuma'); break;
    case 'naapurit': snd('sfx_naapurit_valittaa', 0.8, 100); if (mine) log('Naapurit valittaa! Häätö tulossa...', 'punainen'); break;
    case 'haato': snd('sfx_haato', 0.8, 100); if (mine) log('HÄÄTÖ! Bilettäjät heitettiin ulos sikakännissä.', 'punainen'); break;
    case 'piiritys': snd('sfx_poliisi_sireeni', 0.8, 100); if (mine) log('POLIISIPIIRITYS! 6 hengen bileet kerrostalossa – kaikki putkaan!', 'punainen'); break;
    case 'sauna': if (mine && vis) snd('sfx_sauna_loyly', 0.6, 400); break;
    case 'esine': bubbleTxt(e.id, `Löysin: ${e.nimi}!`, e.x, e.y); if (mine) log(`Kirpputori: ${e.nimi}${e.hyoty ? ' (hyödyllinen!)' : ' (turha krääsä)'}`); break;
    case 'lahjonta': bubbleTxt(e.id, 'Kiitos kultaseni!', e.x, e.y); if (mine) log(`Mummo lahjottu ${e.n} tölkillä: 60 s hänen keräämänsä tölkit ovat teidän rahaa!`); break;
    case 'mummo_raha': if (mine) floaters.push({ x: e.x, y: e.y - 1, t: 1.5, txt: `+${e.raha} € (mummo)`, c: '#e8c33a' }); break;
    case 'tekstari': bubble(e.id, 'tekstari', e.x, e.y, mine || vis); if (mine) log('Kännitekstari exälle! Koko joukkueen sijainti paljastui 8 s.', 'punainen'); break;
    case 'paljastus': if (e.team !== myTeam) { for (const id of e.ids) olentoMerkki[id] = performance.now() + e.aika * 1000; log(`Vihollisen sijainti paljastui (${e.syy})!`, 'tapahtuma'); } else if (e.syy === 'pihagrilli') { snd('sfx_grilli_kary', 0.5, 2000); log('Grillin käry paljasti sijaintinne!', 'punainen'); } break;
    case 'muodonmuutos': snd('sfx_hemuli_muodonmuutos', 0.9, 100); olentoMerkki[e.id] = performance.now() + 8000; onTapahtuma({ key: 'caesar', nimi: e.nimi, teksti: e.teksti, koskee: 0 }); break;
    case 'caesar_loppui': log('Caesar muuttui takaisin Hemuliksi.', 'tapahtuma'); break;
    case 'olento': olentoMerkki[e.id] = performance.now() + 10000; onTapahtuma(e);
      if (e.key === 'vesihiisi') { effects.push({ splash: true, x: e.x, y: e.y, t: 0.5, t0: 0.5 }); snd('sfx_vesihiisi_nousu', 0.8, 100); } break;
    case 'hiisi_kuplat': onVaroitus({ teksti: e.teksti, koskee: 0, sekunnit: 4 }); snd('sfx_vesihiisi_ennakko', vis ? 0.8 : 0.4, 100); break;
    case 'hiisi_sukelsi': effects.push({ dive: true, x: e.x, y: e.y, t: 0.75, t0: 0.75 }); if (vis) snd('sfx_vesihiisi_sukellus', 0.7, 100); log('Vesihiisi painui pinnan alle.', 'tapahtuma'); break;
    case 'huuto': bubble(e.id, e.kind, e.x, e.y, true); break;
    case 'karjunta': if (vis) snd('sfx_peikko_karjunta_' + (1 + Math.floor(Math.random() * 2)), 0.8, 300); break;
    case 'varasti': if (mine) log(`Peikko varasti ${e.n} tölkkiä!`, 'punainen'); break;
    case 'tapahtuma_loppui': snd('sfx_tapahtuma_loppui', 0.6, 100); log(`Tapahtuma päättyi: ${e.nimi}.`, 'tapahtuma'); break;
    case 'tapahtuma_varoitus': onVaroitus(e); break;
    case 'kilina': if (mine && vis) snd('sfx_tolkki_kilina', 0.35, 250); break;
    case 'pantti': if (mine) { snd('sfx_tolkki_kilina', 0.6); floaters.push({ x: e.x, y: e.y - 1, t: 1.5, txt: `+${Math.round(e.raha)} €`, c: '#e8c33a' }); } break;
    case 'valtaus': {
      const b = buildingsById[e.b];
      if (e.owner === myTeam) { snd('sfx_valtaus_valmis', 0.8); log(`Vallattu: ${b.nimi} (${b.osm})`, TEAM[myTeam].vari); }
      else if (e.old === myTeam) { snd('sfx_valtaus_menetetty', 0.8); log(`Menetettiin: ${b.nimi}!`, 'punainen'); }
      else log(`${TEAM[e.owner].nimi} valtasi: ${b.nimi}`);
      break;
    }
    case 'kuoli': if (e.owner === 3) { if (e.type === 'peikko') { effects.push({ corpse: true, x: e.x, y: e.y, t: 4, t0: 4 }); if (vis) snd('sfx_peikko_kaatuu', 0.8, 100); } else effects.push({ dive: true, x: e.x, y: e.y, t: 0.75, t0: 0.75 }); log(`${map.unitTypes[e.type].nimi} kaatui ja pudotti tölkkejä!`, 'tapahtuma'); break; }
      if (e.ajoneuvo) { effects.push({ boom: true, x: e.x, y: e.y, t: 0.6, t0: 0.6 }); if (vis) snd('sfx_rakennus_tuhoutui', 0.6, 200); } if (vis) snd('sfx_kuolema', 0.5, 150); if (vis) floaters.push({ x: e.x, y: e.y, t: 1, txt: '✝', c: '#fff' }); if (mine) log(`${map.unitTypes[e.type].nimi} kaatui.`); break;
    case 'kotiin': bubble(e.id, 'kotiin', e.x, e.y, false); if (mine) { voice('lahiojermu', 'kanni'); log(`${map.unitTypes[e.type].nimi}: "Mää lähen kotiin..." (liian kännissä)`, 'punainen'); } break;
    case 'sammui': bubble(e.id, 'sammui', e.x, e.y, mine || vis); if (mine) log('Yksikkö sammui! (kännimittari täynnä)'); break;
    case 'omiin': bubble(e.id, 'omiin', e.x, e.y, mine || vis); if (mine) log('Kännissä ampui omiaan!', 'punainen'); break;
    case 'baariin': bubble(e.id, 'baariin', e.x, e.y, mine || vis); if (mine) log('Yksikkö lähti baariin!'); break;
    case 'valmis': if (mine) { snd('sfx_koulutus_valmis', 0.6); voice(e.type, 'valittu'); log(`${map.unitTypes[e.type].nimi} valmis.`); } break;
    case 'tuhoutui': snd('sfx_rakennus_tuhoutui', 0.9); break;
    case 'voitto': gameOver = true; show(e.winner === myTeam ? 'VOITTO!<br><small>Vihollisen päämaja on tuhottu.</small>' : 'TAPPIO<br><small>Päämajasi tuhottiin.</small>'); break;
  }
}
function bubbleTxt(id, txt, x, y) { if (bubbles.length >= 6) bubbles.shift(); bubbles.push({ id, x, y, txt, t: 3, t0: 3 }); }
function bubble(id, tila, x, y, withSound) {
  const def = KUPLAT[tila]; if (!def) return;
  const now = performance.now();
  if (!PAKKO[tila] && lastBubble[id] && now - lastBubble[id] < 8000) return;
  if (!onScreen(x, y) && !PAKKO[tila]) return;
  if (bubbles.length >= 6) { if (!PAKKO[tila]) return; bubbles.shift(); }
  for (let i = bubbles.length - 1; i >= 0; i--) if (bubbles[i].id === id) bubbles.splice(i, 1);
  lastBubble[id] = now;
  const txt = def[0][Math.floor(Math.random() * def[0].length)];
  bubbles.push({ id, x, y, txt, t: 2.6, t0: 2.6 });
  if (withSound && onScreen(x, y) && (!lastBubbleSnd[id] || now - lastBubbleSnd[id] > 8000) && now - globalBubbleSnd > 1200) {
    lastBubbleSnd[id] = now; globalBubbleSnd = now;
    snd(def[1][Math.floor(Math.random() * def[1].length)], 0.7, 300);
  }
}
function koskeeTxt(k) {
  if (!k) return 'Koskee molempia puolia';
  const t = TEAM[k]; return `Koskee: ${t.nimi} (${t.varinimi})` + (k === myTeam ? ' – SINUA' : ' – vastustajaa');
}
function lippu(k) { const im = IMG['ui_puoli_' + (k === 1 ? 'sininen' : k === 2 ? 'punainen' : 'molemmat')]; return im ? `<img class="lippu" src="${im.src}">` : ''; }
function onTapahtuma(e) {
  snd('sfx_tapahtuma_jingle', 0.8, 100);
  setTimeout(() => snd('aani_tapahtuma_' + e.key, 0.95, 100), 1500);
  if (e.key === 'poliisipartio') setTimeout(() => snd('sfx_poliisi_sireeni', 0.6, 100), 3500);
  log(`TAPAHTUMA: ${e.nimi}. ${e.teksti} (${koskeeTxt(e.koskee)})`, 'tapahtuma');
  const el = $('tapahtumaBanneri');
  const ic = IMG['tap_' + e.key], bg = IMG.ui_tapahtuma_banneri;
  el.className = bg ? 'kuvalla' : '';
  el.style.backgroundImage = bg ? `url(${bg.src})` : '';
  el.innerHTML = (ic ? `<img class="ikoni" src="${ic.src}">` : '') + `<div class="teksti"><b>${e.nimi.toUpperCase()}!</b> ${e.kesto ? `<small>${e.kesto} s</small>` : ''}<br>${e.teksti}<br><small>${lippu(e.koskee)} ${koskeeTxt(e.koskee)}</small></div>`;
  el.hidden = false; clearTimeout(el._t); el._t = setTimeout(() => { el.hidden = true; }, 6000);
}
function onVaroitus(e) {
  snd('sfx_tapahtuma_varoitus', 0.7, 100);
  log(`Varoitus (${e.sekunnit} s): ${e.teksti}`, 'tapahtuma');
  const el = $('varoitus'); el.innerHTML = `${lippu(e.koskee)} ${e.teksti} <small>(${e.sekunnit} s)</small>`; el.hidden = false;
  clearTimeout(el._t); el._t = setTimeout(() => { el.hidden = true; }, 4500);
}

function show(html) { const i = $('ilmoitus'); i.innerHTML = html + '<br><button onclick="location.href=\'/\'">Uusi peli</button>'; i.hidden = false; }

// ---------- maasto ----------
function buildTerrain() {
  terrainCanvas = document.createElement('canvas');
  terrainCanvas.width = map.cols * TS; terrainCanvas.height = map.rows * TS;
  const t = terrainCanvas.getContext('2d');
  // yhtenäinen maalattu taustakuva (32 px / ruutu); ruudukko jää vain liikkumisdataksi
  if (IMG.kartta_tausta) { t.imageSmoothingEnabled = false; t.drawImage(IMG.kartta_tausta, 0, 0, map.cols * TS, map.rows * TS); return; }
  for (let r = 0; r < map.rows; r++) for (let c = 0; c < map.cols; c++) {
    const id = map.terrain[r][c]; const im = IMG['t' + id];
    if (im) t.drawImage(im, c * TS, r * TS, TS, TS); else { t.fillStyle = MINI_COLORS[id]; t.fillRect(c * TS, r * TS, TS, TS); }
  }
}

// ---------- paneeli ----------
function buildPanel() {
  $('joukkue').innerHTML = teamBadge();
  TRAIN_KEYS = {};
  const k = $('koulutus'); k.innerHTML = '';
  for (const [type, t] of Object.entries(map.unitTypes)) {
    if (t.puoli && t.puoli !== myTeam) continue;
    TRAIN_KEYS[t.nappi] = type;
    const b = document.createElement('button'); b.id = 'kouluta_' + type; b.className = 'koulutusnappi';
    const ic = IMG['ui_' + type + '_' + TEAM[myTeam].vari];
    b.innerHTML = (ic ? `<img src="${ic.src}">` : '') + `<span>[${t.nappi.toUpperCase()}] ${t.nimi}</span><span class="hinta" id="hinta_${type}">${t.hinta} €</span>`;
    b.title = (t.kuvaus ? t.kuvaus + ' ' : '') + (t.ase ? `Ase: ${t.ase.nimi}. ` : '') + `HP ${t.hp}` + (t.kantaa ? `, kantaa ${t.kantaa} tölkkiä` : '') + (t.kyyti ? `, kyytiin ${t.kyyti}` : '');
    b.onclick = () => { sendCmd({ t: 'train', type }); snd('sfx_ui_klikkaus', 0.5); };
    k.appendChild(b);
  }
  const vs = $('voimakkuus'); vs.value = Math.round(musicVol * 100); vs.oninput = () => setMusicVol(vs.value / 100);
  $('mykistys').onclick = () => toggleMute();
  const ab = $('kyvyt'); ab.innerHTML = '';
  const mb = document.createElement('button'); mb.id = 'molotoviNappi'; mb.textContent = '[V] Molotovi'; mb.title = 'Valitse jermuja, mopoja tai isiä, paina V ja klikkaa kohdetta. Maksaa kaljaa (rahaa). Sateessa ei syty.';
  mb.onclick = () => startMolotov(); ab.appendChild(mb);
  const ub = document.createElement('button'); ub.id = 'purkuNappi'; ub.textContent = '[U] Pura kyyti'; ub.title = 'Volvo / Lada: kyytiläiset ulos. Kyytiin pääsee oikealla klikkauksella omaan ajoneuvoon.';
  ub.onclick = () => sendCmd({ t: 'unload', ids: [...selected] }); ab.appendChild(ub);
}
function startMolotov() {
  const ok = [...selected].some(id => { const u = cur.um.get(id); return u && map.unitTypes[u[1]].molotovi; });
  if (!ok) { log('Valitse ensin Lähiöjermu, Mopopoika tai Isä.'); return; }
  molotovMode = true; canvas.style.cursor = 'cell'; log('Molotovi: klikkaa kohdetta (Esc peruu).');
}
let lastPanel = 0;
function updatePanel() {
  const now = performance.now(); if (now - lastPanel < 150) return; lastPanel = now;
  const p = cur.p[myTeam];
  $('raha').textContent = `Pantit: ${p.money} €`;
  const hinnat = cur.hinnat ? cur.hinnat[myTeam] : {};
  for (const type of Object.values(TRAIN_KEYS)) { const h = hinnat[type] || map.unitTypes[type].hinta; $('kouluta_' + type).disabled = p.money < h || p.queue.length >= 5; $('hinta_' + type).textContent = h + ' €'; }
  const selU = [...selected].map(id => cur.um.get(id)).filter(Boolean);
  $('molotoviNappi').hidden = !selU.some(u => map.unitTypes[u[1]].molotovi);
  $('molotoviNappi').textContent = `[V] Molotovi (${cur.molo ? cur.molo[myTeam] : 15} €)`;
  $('purkuNappi').hidden = !selU.some(u => u[10] > 0);
  const tp = $('tapahtumaTila');
  if (cur.tap) { const ic = IMG['tap_' + cur.tap.key];
    tp.innerHTML = `<div class="aktiivinen">${ic ? `<img src="${ic.src}">` : ''}<div><b>${cur.tap.nimi}</b> ${lippu(cur.tap.koskee)}<br><span class="laskuri">${cur.tap.left} s</span></div></div>`; }
  else tp.innerHTML = cur.nextTap != null && cur.nextTap <= 5 ? '<small>Jotain on tulossa...</small>' : '';
  $('jono').textContent = p.queue.length ? 'Koulutus: ' + p.queue.map((q, i) => i === 0 ? `${map.unitTypes[q[0]].nimi} ${Math.ceil(q[1])}s` : map.unitTypes[q[0]].nimi).join(', ') : '';
  const v = $('valinta');
  if (selected.size) {
    const us = [...selected].map(id => cur.um.get(id)).filter(Boolean);
    if (us.length === 1) {
      const u = us[0], t = map.unitTypes[u[1]];
      v.innerHTML = `<b>${t.nimi}</b> <small>(${STATE_FI[u[8]] || u[8]})</small><br>HP ${u[5]}/${t.hp}<div class="mittari"><div style="width:${u[5] / t.hp * 100}%;background:#4c4"></div></div>` +
        `Kännimittari ${u[6]} %<div class="mittari"><div style="width:${u[6]}%;background:${kColor(u[6])}"></div></div>` +
        `<small>${kText(u[6])}</small>` + (t.kantaa ? `<br>Tölkkejä: ${u[7]}/${t.kantaa}` : '') + (t.kyyti ? `<br>Kyydissä: ${u[10]}/${t.kyyti}` : '') + (t.ase ? `<br><small>Ase: ${t.ase.nimi}</small>` : '') + (u[11] & 2 ? '<br><small>Terästetty (+30 %)</small>' : '') + (u[11] & 1 ? '<br><small>Hidastettu</small>' : '') + (u[12] ? `<br><small>Esine: ${u[12]}</small>` : '');
    } else {
      const cnt = {}; us.forEach(u => cnt[u[1]] = (cnt[u[1]] || 0) + 1);
      const avgK = Math.round(us.reduce((a, u) => a + u[6], 0) / us.length);
      v.innerHTML = `<b>${us.length} yksikköä</b><br>` + Object.entries(cnt).map(([k, n]) => `${n}× ${map.unitTypes[k].nimi}`).join('<br>') +
        `<br>Kännit keskim. ${avgK} %<div class="mittari"><div style="width:${avgK}%;background:${kColor(avgK)}"></div></div>`;
    }
  } else if (selBuilding) {
    const b = buildingsById[selBuilding], s = cur.b.find(x => x[0] === b.id);
    v.innerHTML = `<b>${b.nimi}</b><br><small>${b.osm}</small><br>Omistaja: <span class="${TEAM[s[1]].vari || ''}">${TEAM[s[1]].nimi}</span>` +
      (b.maxhp ? `<br>HP ${s[4]}/${b.maxhp}` : '') + (s[3] > 0 ? `<br>Valtaus (${TEAM[s[2]].nimi}): ${Math.round(s[3] * 100)} %` : '') + `<br><small>${b.kuvaus}</small>` +
      (b.tyyppi === 'kerrostalo' ? `<br>Sisällä: ${s[6]}/6` + (s[1] === myTeam && s[6] ? `<br><button data-tyhjenna="${b.id}">Tyhjennä talo</button>` : '') : '');
    if (!v._v4) { v._v4 = true; v.addEventListener('mousedown', ev => { const id = ev.target && ev.target.dataset && ev.target.dataset.tyhjenna; if (id) sendCmd({ t: 'tyhjenna', b: +id }); }); }
  } else v.innerHTML = '<small>Valitse yksiköitä hiirellä. Oikea klikkaus antaa käskyn.</small>';
}
function kColor(k) { return k < 20 ? '#8c8' : k < 60 ? '#ec3' : k < 85 ? '#f80' : '#f22'; }
function kText(k) { return k < 20 ? 'Selvä.' : k < 60 ? 'Pieni hiprakka: +25 % vahinko, tarkempi.' : k < 85 ? 'Humalassa: hitaampi, epätarkka.' : 'TÄYSI KÄNNI: voi sammua, lähteä kotiin, baariin tai ampua omia! Vie päämajan lähelle selviämään.'; }

// ---------- kamera ja koordinaatit ----------
function viewW() { return canvas.width; } function viewH() { return canvas.height; }
function resize() { canvas.width = window.innerWidth - PANEL; canvas.height = window.innerHeight; ctx.imageSmoothingEnabled = false; clampCam(); }
window.addEventListener('resize', () => started && resize());
function minZoom() { return map ? Math.max(1, viewW() / (map.cols * TS), viewH() / (map.rows * TS)) : 1; }
function clampCam() { if (!map) return; if (cam.z < minZoom()) cam.z = minZoom(); const ww = map.cols * TS * cam.z, wh = map.rows * TS * cam.z; cam.x = Math.max(0, Math.min(cam.x, ww - viewW())); cam.y = Math.max(0, Math.min(cam.y, wh - viewH())); }
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
  if (molotovMode) {
    const [x, y] = toWorld(e.offsetX, e.offsetY);
    if (e.button === 0 || e.button === 2) { sendCmd({ t: 'molotovi', ids: [...selected], x, y }); effects.push({ mark: true, x, y, t: 0.5, c: '#fa0' });
      const f = cur.um.get([...selected][0]); if (f) voice(f[1], 'hyokkays'); }
    molotovMode = false; canvas.style.cursor = 'crosshair'; return;
  }
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
  const zs = [1, 1.5, 2, 3].filter(z => z >= minZoom()); if (!zs.length || zs[0] > minZoom()) zs.unshift(minZoom()); let i = zs.findIndex(z => z >= cam.z - 1e-6); if (i < 0) i = 0; i = Math.max(0, Math.min(zs.length - 1, i + (e.deltaY < 0 ? 1 : -1))); cam.z = zs[i];
  cam.x = wx * TS * cam.z - e.offsetX; cam.y = wy * TS * cam.z - e.offsetY; clampCam(); ctx.imageSmoothingEnabled = false;
}, { passive: false });
mini.addEventListener('mousedown', e => { const f = map.cols / mini.width; centerOn(e.offsetX * f, e.offsetY * f); });
mini.addEventListener('contextmenu', e => { e.preventDefault(); const f = map.cols / mini.width; order(e.offsetX * f, e.offsetY * f); });

window.addEventListener('keydown', e => {
  if (!ready) return;
  const k = e.key.toLowerCase(); keys[k] = true;
  if (TRAIN_KEYS[k]) { sendCmd({ t: 'train', type: TRAIN_KEYS[k] }); snd('sfx_ui_klikkaus', 0.5); }
  if (k === 'h') sendCmd({ t: 'stop', ids: [...selected] });
  if (k === 'v') startMolotov();
  if (k === 'u') sendCmd({ t: 'unload', ids: [...selected] });
  if (k === 'escape') { molotovMode = false; canvas.style.cursor = 'crosshair'; }
  if (k === 'm') toggleMute();
  if (k === ' ') { e.preventDefault(); centerOnHQ(); }
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
  if (first) { voice(first[1], attack ? 'hyokkays' : 'kuittaus'); if (MOVE_SFX[first[1]]) snd(MOVE_SFX[first[1]], 0.4, 1500); }
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

  const nowMs = performance.now();
  // laattalätät
  for (const l of cur.l || []) {
    if (!onScreen(l[0], l[1])) continue;
    const [x, y] = toScreen(l[0], l[1]);
    const ph = l[3] > 0.66 ? 1 : l[3] > 0.33 ? 2 : 3; const im = IMG['fx_laatta_latta_' + ph];
    const sz = l[2] * 2 * TS * z * Math.max(0.5, l[3]);
    ctx.globalAlpha = Math.min(1, 0.4 + l[3]);
    if (im) ctx.drawImage(im, x - sz / 2, y - sz / 2, sz, sz); else { ctx.fillStyle = '#9a3'; ctx.beginPath(); ctx.ellipse(x, y, sz / 2, sz / 3, 0, 0, 7); ctx.fill(); }
    ctx.globalAlpha = 1;
    const st = IMG.fx_laatta_hoyry; if (st) { const fw = st.height, fr = Math.floor(nowMs / 200) % Math.max(1, Math.floor(st.width / fw)); ctx.drawImage(st, fr * fw, 0, fw, fw, x - fw * z / 2, y - fw * z, fw * z, fw * z); }
  }
  loopSnd('sfx_laatta_karpaset_loop', (cur.l || []).some(l => onScreen(l[0], l[1])), 0.2);
  // tuli (molotovit)
  for (const f of cur.f || []) {
    if (!onScreen(f[0], f[1])) continue;
    const im = IMG.fx_tuli_32;
    for (let i = 0; i < 5; i++) {
      const a = i * 1.3, rr = i ? f[2] * 0.6 : 0; const [x, y] = toScreen(f[0] + Math.cos(a) * rr, f[1] + Math.sin(a) * rr * 0.7);
      if (im) { const fr = (Math.floor(nowMs / 120) + i) % 4; ctx.drawImage(im, fr * 32, 0, 32, 32, x - 16 * z, y - 28 * z, 32 * z, 32 * z); }
      else { ctx.fillStyle = '#f60'; ctx.fillRect(x - 5, y - 10, 10, 10); }
    }
  }
  // tapahtumaobjektit: Alko, sauna, kesäjuhlat
  if (cur.tap && cur.tap.alko && IMG.alko) { const [x, y] = toScreen(cur.tap.alko[0] - 1, cur.tap.alko[1] - 2.2); ctx.drawImage(IMG.alko, x, y, 2 * S, 2 * S); }
  if (cur.away && cur.away.length) for (const team of [1, 2]) {
    const n = cur.away.filter(a => a[0] === team).length; if (!n) continue;
    const h = map.buildings.find(b => b.tyyppi === 'paamaja' && b.owner === team); const im = cur.away.find(a => a[0] === team)[1] ? IMG.fx_sauna_32 : null;
    const [x, y] = toScreen(h.col + 2.2, h.row + 0.5);
    if (im) ctx.drawImage(im, x, y, 32 * z, 32 * z);
    ctx.fillStyle = '#fff'; ctx.font = `bold ${10 * z}px monospace`; ctx.fillText((im ? 'saunassa ' : 'kokouksessa ') + n, x, y);
  }
  if (cur.tap && cur.tap.key === 'kesajuhlat' && IMG.fx_kesajuhlat_32) for (const b of map.buildings.filter(b => b.tyyppi === 'paamaja')) { const [x, y] = toScreen(b.col - 1, b.row + 1); ctx.drawImage(IMG.fx_kesajuhlat_32, x, y, 32 * z, 32 * z); }

  // tapahtumapaikkojen merkit
  if (cur.tap && cur.tap.paikat) for (const pk of cur.tap.paikat) {
    if (!onScreen(pk[0], pk[1])) continue; const [x, y] = toScreen(pk[0], pk[1]); const im = IMG.ui_tapahtuma_karttamerkki;
    const yy = y - (cur.tap.key === 'poliisipartio' ? 28 : 20) * z;
    if (im) { const fr = Math.floor(nowMs / 150) % 4; ctx.drawImage(im, fr * 16, 0, 16, 16, x - 8 * z, yy - 16 * z, 16 * z, 16 * z); }
    else { ctx.fillStyle = '#fc0'; ctx.fillText('!', x, yy); }
  }

  // tölkit
  for (const c of cur.c) {
    if (!onScreen(c[1], c[2])) continue;
    const [x, y] = toScreen(c[1], c[2]);
    if (c[3] >= 10 && IMG.fx_kirppis_tolkkikasa_32) { ctx.drawImage(IMG.fx_kirppis_tolkkikasa_32, x - 16 * z, y - 24 * z, 32 * z, 32 * z); ctx.fillStyle = '#fff'; ctx.font = `${10 * z}px monospace`; ctx.fillText(c[3], x + 10 * z, y + 8 * z); continue; }
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

  // vesihiiden kuplat (ennakkovaroitus) + olentojen karttamerkit
  if (cur.hb) { const [x, y] = toScreen(cur.hb[0], cur.hb[1]); const im = IMG.fx_kuplat_32; const fr = Math.floor(nowMs / 166) % 4;
    if (im) ctx.drawImage(im, fr * 32, 0, 32, 32, x - 16 * z, y - 16 * z, 32 * z, 32 * z); else { ctx.fillStyle = '#cef'; for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.arc(x + Math.sin(nowMs / 200 + k * 2) * 8 * z, y + Math.cos(nowMs / 300 + k) * 5 * z, 2 * z, 0, 7); ctx.fill(); } } }
  loopSnd('sfx_vesihiisi_kuplat_loop', !!(cur.hb && onScreen(cur.hb[0], cur.hb[1])), 0.4);
  { const mk = IMG.ui_tapahtuma_karttamerkki; const pts = cur.hb ? [cur.hb] : [];
    for (const [id, until] of Object.entries(olentoMerkki)) { if (nowMs > until) { delete olentoMerkki[id]; continue; } const u = cur.um.get(+id); if (u) pts.push(lerpPos(u)); }
    for (const p of pts) { const [x, y] = toScreen(p[0], p[1]); const yy = y - 44 * z; if (mk) { const fw = mk.height, fr = Math.floor(nowMs / 150) % Math.max(1, Math.floor(mk.width / fw)); ctx.drawImage(mk, fr * fw, 0, fw, fw, x - fw * z / 2, yy - fw * z, fw * z, fw * z); } else { ctx.fillStyle = '#fc0'; ctx.fillRect(x - 3, yy - 8, 6, 8); } } }
  // efektit
  for (let i = effects.length - 1; i >= 0; i--) {
    const e = effects[i]; e.t -= dt; if (e.t <= 0) { if (e.osuu) snd(e.osuu, 0.5, 150); effects.splice(i, 1); continue; }
    if (e.boom) { const im = IMG.fx_rajahdys_64; const fr = Math.min(5, Math.floor((1 - e.t / e.t0) * 6)); const [x, y] = toScreen(e.x, e.y); const sz = (e.small ? 40 : 64) * z;
      if (im) ctx.drawImage(im, fr * 64, 0, 64, 64, x - sz / 2, y - sz * 0.7, sz, sz); else { ctx.fillStyle = '#fa0'; ctx.beginPath(); ctx.arc(x, y, sz / 3, 0, 7); ctx.fill(); } continue; }
    if (e.arc) { const a = 1 - e.t / e.t0; const px = e.x + (e.tx - e.x) * a, py = e.y + (e.ty - e.y) * a - Math.sin(a * Math.PI) * 1.5; const [x, y] = toScreen(px, py); const im = IMG[e.img];
      if (im) { ctx.save(); ctx.translate(x, y); if (e.spin) ctx.rotate(a * 12); ctx.drawImage(im, -im.width * z / 2, -im.height * z / 2, im.width * z, im.height * z); ctx.restore(); } else { ctx.fillStyle = '#c84'; ctx.fillRect(x - 3, y - 3, 6, 6); }
      if (e.kary && IMG.fx_kary_32 && a > 0.8) { const [kx, ky] = toScreen(e.tx, e.ty); ctx.globalAlpha = 0.6; ctx.drawImage(IMG.fx_kary_32, kx - 16 * z, ky - 24 * z, 32 * z, 32 * z); ctx.globalAlpha = 1; }
      continue; }
    if (e.splash || e.dive || e.corpse) { const [x, y] = toScreen(e.x, e.y); const a = 1 - e.t / e.t0;
      if (e.corpse) { const im = IMG.o_peikko_kaatunut; ctx.globalAlpha = Math.min(1, e.t); if (im) ctx.drawImage(im, x - 24 * z, y - 43 * z, 48 * z, 48 * z); ctx.globalAlpha = 1; continue; }
      if (e.dive && IMG.o_vesihiisi_sukellus) { const fr = Math.min(5, Math.floor(a * 6)); ctx.drawImage(IMG.o_vesihiisi_sukellus, fr * 48, 0, 48, 48, x - 24 * z, y - 43 * z, 48 * z, 48 * z); continue; }
      const im = IMG.fx_loiske_32; if (im) { const fr = Math.min(3, Math.floor(a * 4)); ctx.drawImage(im, fr * 32, 0, 32, 32, x - 16 * z, y - 24 * z, 32 * z, 32 * z); } else { ctx.strokeStyle = '#9cf'; ctx.beginPath(); ctx.arc(x, y, a * 12 * z, 0, 7); ctx.stroke(); } continue; }
    if (e.mark) { const [x, y] = toScreen(e.x, e.y); ctx.strokeStyle = e.c; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, (1 - e.t * 2) * 10 * z + 3, 0, 7); ctx.stroke(); continue; }
    const [x1, y1] = toScreen(e.x, e.y - 0.35), [x2, y2] = toScreen(e.tx + (e.hit ? 0 : 0.4), e.ty - 0.3 + (e.hit ? 0 : 0.3));
    ctx.strokeStyle = e.c; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    if (e.flash && IMG.fx_suuliekki_8) { ctx.save(); ctx.translate(x1, y1); ctx.rotate(Math.atan2(y2 - y1, x2 - x1)); ctx.drawImage(IMG.fx_suuliekki_8, 0, -4 * z, 8 * z, 8 * z); ctx.restore(); }
  }
  ctx.font = `bold ${12 * z}px monospace`; ctx.textAlign = 'center';
  for (let i = floaters.length - 1; i >= 0; i--) {
    const f = floaters[i]; f.t -= dt; if (f.t <= 0) { floaters.splice(i, 1); continue; }
    const [x, y] = toScreen(f.x, f.y - (2 - f.t) * 0.5); ctx.fillStyle = '#000'; ctx.fillText(f.txt, x + 1, y + 1); ctx.fillStyle = f.c; ctx.fillText(f.txt, x, y);
  }
  ctx.textAlign = 'left';

  // sade
  const rainOn = cur.tap && cur.tap.key === 'sadekuuro';
  loopSnd('sfx_sade_loop', rainOn, 0.35);
  if (rainOn) {
    const im = IMG.fx_sade_64, off = (nowMs / 4) % 64;
    ctx.fillStyle = 'rgba(20,30,60,.25)'; ctx.fillRect(0, 0, viewW(), viewH());
    if (im) for (let yy = -64 + off; yy < viewH(); yy += 64) for (let xx = -64 + off / 3; xx < viewW(); xx += 64) ctx.drawImage(im, xx, yy);
  }
  const snowOn = cur.tap && cur.tap.key === 'lumimyrsky';
  loopSnd('sfx_lumimyrsky_loop', snowOn, 0.35);
  if (snowOn) { const im = IMG.fx_lumi_64, off = (nowMs / 6) % 64; ctx.fillStyle = 'rgba(230,240,255,.18)'; ctx.fillRect(0, 0, viewW(), viewH());
    if (im) for (let yy = -64 + off; yy < viewH(); yy += 64) for (let xx = -64 + off; xx < viewW(); xx += 64) ctx.drawImage(im, xx, yy); }
  loopSnd('sfx_bileet_loop', cur.b.some(x => x[7] & 1), 0.3);
  // humalakuplat
  ctx.font = `bold ${Math.round(11 * Math.min(z, 1.5))}px "Courier New", monospace`;
  for (let i = bubbles.length - 1; i >= 0; i--) {
    const b = bubbles[i]; b.t -= dt; if (b.t <= 0) { bubbles.splice(i, 1); continue; }
    const u = cur.um.get(b.id); if (u) { const p = lerpPos(u); b.x = p[0]; b.y = p[1]; }
    const [x, y0] = toScreen(b.x, b.y); const y = y0 - 34 * z - (1 - b.t / b.t0) * 6;
    const w = ctx.measureText(b.txt).width + 10, hgt = 16;
    ctx.globalAlpha = Math.min(1, b.t * 2);
    ctx.fillStyle = '#fff'; ctx.strokeStyle = '#000'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.rect(Math.round(x - w / 2), Math.round(y - hgt), Math.round(w), hgt); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - 4, y); ctx.lineTo(x, y + 6); ctx.lineTo(x + 4, y); ctx.fill();
    ctx.fillStyle = '#000'; ctx.textAlign = 'center'; ctx.fillText(b.txt, x, y - 4); ctx.textAlign = 'left';
    ctx.globalAlpha = 1;
  }
  // pysyvä joukkuetarra
  { const t = TEAM[myTeam]; const txt = `${t.nimi.toUpperCase()} (${t.varinimi})`; ctx.font = 'bold 14px monospace'; const w = ctx.measureText(txt).width + 16;
    ctx.fillStyle = 'rgba(0,0,0,.65)'; ctx.fillRect(8, 8, w, 24); ctx.fillStyle = t.css; ctx.fillRect(8, 8, 5, 24); ctx.fillStyle = '#fff'; ctx.fillText(txt, 18, 25); }
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
  ctx.fillStyle = (owner ? TEAM[owner].css : '#999999') + '55'; ctx.fillRect(x - 2, y - 2, 2 * S + 4, 2 * S + 4);
  ctx.strokeStyle = TEAM[owner].css; ctx.lineWidth = 2; ctx.strokeRect(x - 2, y - 2, 2 * S + 4, 2 * S + 4);
  let im = null;
  if (b.tyyppi === 'paamaja') im = IMG['paamaja_' + (owner === 2 ? 'punainen' : 'sininen')];
  else if (b.tyyppi === 'kmarket') im = IMG.kmarket; else if (b.tyyppi === 'baari') im = IMG.baari; else im = IMG['b_' + EXTRA_BUILDINGS[b.nimi]];
  if (b.tyyppi === 'kerrostalo') {
    if (s[6]) { ctx.fillStyle = 'rgba(0,0,0,.7)'; ctx.fillRect(x + S - 12 * z, y + S - 8 * z, 24 * z, 14 * z); ctx.fillStyle = '#ff0'; ctx.font = `bold ${10 * z}px monospace`; ctx.textAlign = 'center'; ctx.fillText(s[6] + '/6', x + S, y + S + 3 * z); ctx.textAlign = 'left'; }
    if (s[7] & 1 && Math.floor(performance.now() / 250) % 2) { ctx.fillStyle = 'rgba(255,0,200,.25)'; ctx.fillRect(x, y, 2 * S, 2 * S); }
    if (s[7] & 2 && IMG.fx_poliisipiiritys_64) ctx.drawImage(IMG.fx_poliisipiiritys_64, (Math.floor(performance.now() / 250) % 4) * 64, 0, 64, 64, x, y, 2 * S, 2 * S);
  } else if (im) ctx.drawImage(im, x, y, 2 * S, 2 * S);
  else { // placeholder
    ctx.fillStyle = '#5a5248'; ctx.fillRect(x + 4 * z, y + 10 * z, 2 * S - 8 * z, 2 * S - 12 * z);
    ctx.fillStyle = '#3a342e'; ctx.fillRect(x + 2 * z, y + 6 * z, 2 * S - 4 * z, 6 * z);
    ctx.fillStyle = '#ffd'; ctx.font = `bold ${7 * z}px monospace`; ctx.textAlign = 'center';
    ctx.fillText(b.nimi.split(/[- ]/)[0].slice(0, 10), x + S, y + S + 4 * z); ctx.textAlign = 'left';
  }
  if (s[5]) { ctx.fillStyle = 'rgba(0,0,0,.7)'; ctx.fillRect(x, y + S - 8 * z, 2 * S, 14 * z); ctx.fillStyle = '#f44'; ctx.font = `bold ${9 * z}px monospace`; ctx.fillText('RIKKI', x + 4 * z, y + S + 3 * z); }
  if (selBuilding === b.id) { ctx.strokeStyle = '#fff'; ctx.strokeRect(x - 3, y - 3, 2 * S + 6, 2 * S + 6); }
  // nimi pienellä
  if (z >= 1) { ctx.font = `${9 * z}px monospace`; ctx.fillStyle = '#000'; ctx.fillText(b.nimi, x + 1, y - 4 + 1); ctx.fillStyle = '#fff'; ctx.fillText(b.nimi, x, y - 4); }
  // HP / valtaus
  if (b.maxhp) bar(x, y + 2 * S + 3, 2 * S, s[4] / b.maxhp, '#4c4');
  if (s[3] > 0) bar(x, y + 2 * S + 8, 2 * S, s[3], TEAM[s[2]].css);
}
function bar(x, y, w, f, c) { ctx.fillStyle = '#000'; ctx.fillRect(x, y, w, 4); ctx.fillStyle = c; ctx.fillRect(x, y, w * Math.max(0, f), 4); }

const prevPos = {};
function drawUnit(u, ux, uy) {
  if (!onScreen(ux, uy)) return;
  const z = cam.z, S = TS * z;
  const [x, y] = toScreen(ux, uy);
  const sel = selected.has(u[0]);
  const t = map.unitTypes[u[1]] || { hp: 1, luokka: 'ajoneuvo' };
  const veh = t.luokka === 'ajoneuvo';
  if (sel) { ctx.strokeStyle = '#4f4'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(x, y, (veh ? 14 : 9) * z, 4 * z, 0, 0, 7); ctx.stroke(); }
  if (t.olento) { drawOlento(u, x, y, z, sel, t, ux, uy); return; }
  const col = u[2] === 2 ? 'punainen' : 'sininen';
  const key = u[1] + '_' + col;
  const now = performance.now();
  const pp = prevPos[u[0]]; const moving = pp && Math.hypot(pp[0] - ux, pp[1] - uy) > 0.002; prevPos[u[0]] = [ux, uy];
  const shooting = shootT[u[0]] && now - shootT[u[0]] < 250;
  let im = IMG[key], fr = 0, nfr = 1;
  if (u[8] === 'sammunut' && IMG[key + '_sammunut']) im = IMG[key + '_sammunut'];
  else if (shooting && IMG[key + '_ampuu']) { im = IMG[key + '_ampuu']; nfr = 2; fr = Math.floor((now - shootT[u[0]]) / 125) % 2; }
  else if (moving && IMG[key + '_kavely']) { im = IMG[key + '_kavely']; nfr = 4; fr = Math.floor(now / 150) % 4; }
  const fw = im ? im.width / nfr : 32, fh = im ? im.height : 32;
  ctx.save(); ctx.translate(x, y);
  if (u[8] === 'sammunut' && !IMG[key + '_sammunut']) ctx.rotate(Math.PI / 2);
  if (u[9] < 0) ctx.scale(-1, 1);
  if (im) ctx.drawImage(im, fr * fw, 0, fw, fh, -fw * z / 2, -fh * z * 0.875, fw * z, fh * z);
  else { ctx.fillStyle = TEAM[u[2]].css; ctx.fillRect(-6 * z, -20 * z, 12 * z, 18 * z); ctx.fillStyle = '#fff'; ctx.font = `${8 * z}px monospace`; ctx.fillText(u[1][0].toUpperCase(), -3 * z, -8 * z); }
  ctx.restore();
  if (u[2] === 0) return; // poliisi
  const by = y - S * 0.95;
  if (sel || u[5] < t.hp) bar(x - 10 * z, by, 20 * z, u[5] / t.hp, u[2] === myTeam ? '#4c4' : '#e44');
  if (u[2] === myTeam) { ctx.fillStyle = '#000'; ctx.fillRect(x - 10 * z, by + 4, 20 * z, 3); ctx.fillStyle = kColor(u[6]); ctx.fillRect(x - 10 * z, by + 4, 20 * z * u[6] / 100, 3); }
  if (u[7] > 0 && IMG.tolkki) { ctx.drawImage(IMG.tolkki, x + 5 * z, y - 14 * z, 10 * z, 10 * z); }
  if (u[10] > 0) { ctx.fillStyle = '#000'; ctx.fillRect(x + 8 * z, y - 24 * z, 12 * z, 10 * z); ctx.fillStyle = '#ff0'; ctx.font = `bold ${9 * z}px monospace`; ctx.fillText(u[10], x + 10 * z, y - 16 * z); }
  if (u[11] & 1 && IMG.fx_kary_32) { ctx.globalAlpha = 0.45; ctx.drawImage(IMG.fx_kary_32, x - 10 * z, y - 26 * z, 20 * z, 20 * z); ctx.globalAlpha = 1; }
  if (u[8] === 'sammunut' && !IMG[key + '_sammunut']) { ctx.fillStyle = '#ff0'; ctx.font = `${10 * z}px monospace`; ctx.fillText('Zzz', x + 6 * z, y - 18 * z); }
}

function drawOlento(u, x, y, z, sel, t, ux, uy) {
  const now = performance.now();
  const shooting = shootT[u[0]] && now - shootT[u[0]] < 500;
  const P = 'o_' + u[1];
  let im = IMG[P], nfr = 1, fr = 0;
  const st = (n, ms, loop = true) => { const k = IMG[P + n]; if (!k) return; im = k; nfr = Math.round(k.width / k.height); fr = loop ? Math.floor(now / ms) % nfr : Math.min(nfr - 1, Math.floor((now - (shootT[u[0]] || now)) / ms)); };
  if (u[8] === 'nousu') { im = IMG.o_vesihiisi_nousu || im; nfr = 6; fr = Math.min(5, Math.floor((now - (spawnT[u[0]] || (spawnT[u[0]] = now))) / 125)); }
  else if (shooting) st('_hyokkays', 125, false);
  else if (u[8] === 'karjuu') st('_karjuu', 250);
  else if (shooting && u[1] === 'vana') st('_potku', 125, false);
  else if (u[8] === 'syo') st('_syo', 333);
  else if (u[8] === 'move' && u[1] !== 'vesihiisi') st('_kavely', 180);
  const fs = im ? im.height : 48;
  ctx.save(); ctx.translate(x, y); if (u[9] < 0) ctx.scale(-1, 1);
  if (im) ctx.drawImage(im, fr * fs, 0, fs, fs, -fs / 2 * z, -fs * 0.9 * z, fs * z, fs * z);
  else { ctx.fillStyle = u[1] === 'peikko' ? '#4a6a2a' : '#2a6a7a'; ctx.fillRect(-10 * z, -30 * z, 20 * z, 28 * z); }
  ctx.restore();
  if (u[2] && (sel || u[5] < t.hp)) bar(x - 14 * z, y - 46 * z, 28 * z, u[5] / t.hp, '#c6f');
}
const spawnT = {};

let miniBase = null;
function drawMini() {
  const W = mini.width, f = W / map.cols;
  if (!miniBase) {
    miniBase = document.createElement('canvas'); miniBase.width = W; miniBase.height = W; const m = miniBase.getContext('2d');
    if (IMG.minikartta) m.drawImage(IMG.minikartta, 0, 0, W, W); else
    for (let r = 0; r < map.rows; r++) for (let c = 0; c < map.cols; c++) { m.fillStyle = MINI_COLORS[map.terrain[r][c]]; m.fillRect(c * f, r * f, Math.ceil(f), Math.ceil(f)); }
  }
  mctx.drawImage(miniBase, 0, 0);
  for (const b of map.buildings) { const s = cur.b.find(x => x[0] === b.id); mctx.fillStyle = TEAM[s[1]].css; mctx.fillRect(b.col * f, b.row * f, 2 * f, 2 * f); mctx.strokeStyle = '#fff'; mctx.lineWidth = 1; mctx.strokeRect(b.col * f, b.row * f, 2 * f, 2 * f); }
  mctx.fillStyle = '#ddd'; for (const c of cur.c) mctx.fillRect(c[1] * f - 1, c[2] * f - 1, 2, 2);
  for (const u of cur.u) { mctx.fillStyle = u[2] === 1 ? '#6af' : u[2] === 2 ? '#f66' : u[2] === 3 ? '#c6f' : '#fff'; mctx.fillRect(u[3] * f - 1.5, u[4] * f - 1.5, 3, 3); }
  if (Math.floor(performance.now() / 300) % 2) { mctx.fillStyle = '#ff0'; for (const id of Object.keys(olentoMerkki)) { const u = cur.um.get(+id); if (u) mctx.fillRect(u[3] * f - 3, u[4] * f - 3, 6, 6); } }
  if (cur.hb && Math.floor(performance.now() / 300) % 2) { mctx.fillStyle = '#c6f'; mctx.fillRect(cur.hb[0] * f - 3, cur.hb[1] * f - 3, 6, 6); }
  if (cur.tap && cur.tap.paikat && Math.floor(performance.now() / 300) % 2) { mctx.fillStyle = '#fc0'; for (const pk of cur.tap.paikat) mctx.fillRect(pk[0] * f - 3, pk[1] * f - 3, 6, 6); }
  mctx.strokeStyle = '#fff'; mctx.lineWidth = 1;
  mctx.strokeRect(cam.x / (TS * cam.z) * f, cam.y / (TS * cam.z) * f, viewW() / (TS * cam.z) * f, viewH() / (TS * cam.z) * f);
}
})();
