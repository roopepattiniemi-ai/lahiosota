'use strict';
// Lähiösota-palvelin: staattiset tiedostot + WebSocket-huoneet (1v1 linkillä).
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { WebSocketServer } = require('ws');
const { Game, TICK, UNIT_TYPES } = require('./game');

const PORT = +process.env.PORT || 3000;
const ROOT = path.resolve(__dirname, '..');
const MAP_FILE = process.env.MAP_FILE || path.join(ROOT, 'kartta', 'pelikentta_v2_tiles.json');
const MAP = JSON.parse(fs.readFileSync(MAP_FILE, 'utf8'));

const STATIC = { '/grafiikka/': path.join(ROOT, 'grafiikka'), '/aanet/': path.join(ROOT, 'aanet'), '/': path.join(__dirname, 'public') };
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png',
  '.json': 'application/json', '.ogg': 'audio/ogg', '.mp3': 'audio/mpeg', '.md': 'text/plain; charset=utf-8' };

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  for (const [prefix, dir] of Object.entries(STATIC)) {
    if (!url.startsWith(prefix)) continue;
    let rel = url.slice(prefix.length) || 'index.html';
    const file = path.resolve(dir, rel);
    if (!file.startsWith(dir + path.sep) && file !== dir) break;
    fs.readFile(file, (err, data) => {
      if (err) { res.writeHead(404); res.end('Ei löydy'); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
      res.end(data);
    });
    return;
  }
  res.writeHead(404); res.end('Ei löydy');
});

const rooms = new Map(); // koodi -> { game, slots: {1: ws|null, 2: ws|null}, started, solo, timer, empty }

function getRoom(code, solo) {
  let r = rooms.get(code);
  if (!r) {
    r = { code, game: new Game(MAP, { seed: crypto.randomInt(1, 2 ** 31) }), slots: { 1: null, 2: null }, tokens: {}, started: false, solo, timer: null, emptySince: 0 };
    rooms.set(code, r);
  }
  return r;
}

function send(ws, obj) { if (ws && ws.readyState === 1) ws.send(JSON.stringify(obj)); }
function broadcast(r, obj) { const s = JSON.stringify(obj); for (const t of [1, 2]) if (r.slots[t] && r.slots[t].readyState === 1) r.slots[t].send(s); }
function lobbyInfo(r) { broadcast(r, { t: 'lobby', present: { 1: !!r.slots[1], 2: !!r.slots[2] }, started: r.started }); }

function start(r) {
  if (r.started) return;
  r.started = true;
  broadcast(r, { t: 'start' });
  r.timer = setInterval(() => {
    r.game.step();
    const snap = r.game.snapshot();
    broadcast(r, snap);
    if (r.game.winner && !r.endedAt) r.endedAt = Date.now();
  }, TICK * 1000);
}

const wss = new WebSocketServer({ server, path: '/ws' });
wss.on('connection', (ws, req) => {
  const q = new URL(req.url, 'http://x').searchParams;
  const code = (q.get('huone') || '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 24);
  if (!code) { send(ws, { t: 'virhe', viesti: 'Huonekoodi puuttuu.' }); ws.close(); return; }
  const solo = q.get('harjoitus') === '1';
  const token = (q.get('token') || '').slice(0, 64);
  const r = getRoom(code, solo);
  // paikan valinta: sama token saa saman puolen takaisin
  let team = 0;
  for (const t of [1, 2]) if (r.tokens[t] && r.tokens[t] === token && !r.slots[t]) team = t;
  if (!team) for (const t of [1, 2]) if (!r.slots[t] && !r.tokens[t]) { team = t; break; }
  if (!team) for (const t of [1, 2]) if (!r.slots[t]) { team = t; break; }
  if (!team) { send(ws, { t: 'virhe', viesti: 'Huone on täynnä (2 pelaajaa).' }); ws.close(); return; }
  r.slots[team] = ws; r.tokens[team] = token; r.emptySince = 0;
  ws.team = team; ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
  send(ws, { t: 'init', team, huone: code, solo: r.solo, map: r.game.initData() });
  lobbyInfo(r);
  if (r.started) send(ws, { t: 'start' });
  else if (r.solo || (r.slots[1] && r.slots[2])) start(r);

  ws.on('message', (data) => {
    let msg; try { msg = JSON.parse(data); } catch { return; }
    if (!msg || typeof msg !== 'object') return;
    if (msg.t === 'chat') { broadcast(r, { t: 'chat', team, teksti: String(msg.teksti || '').slice(0, 200) }); return; }
    if (!r.started) return;
    // testikomennot vain yksinpelin harjoitushuoneissa (ei vaikuta 1v1-peleihin)
    if (msg.t === 'debug' && r.solo) {
      const g = r.game;
      if (msg.tap) g.startEvent(String(msg.tap));
      if (msg.olento === 'peikot') g.nextPeikko = 0;
      if (msg.olento === 'vesihiisi') { g.nextHiisi = 0; const [c, r] = g.shore[0] || [0, 0]; const h = g.hq(team); if (h) g._spawnUnitNear(team, 'lahiojermu', c + 2, r); }
      if (msg.raha) g.players[team].money += Math.min(100000, +msg.raha || 0);
      if (msg.kanni) for (const u of g.units.values()) if (u.owner === team) u.k = Math.min(100, +msg.kanni);
      if (msg.v4) { // V4-testaus: caesar | vana | mummo | tekstari | grilli | bileet | piiritys
        const v = String(msg.v4), mine = [...g.units.values()].filter(u => u.owner === team);
        const npc = (t) => [...g.units.values()].find(u => u.type === t);
        if (v === 'caesar' && npc('hemuli')) g.muodonmuutos(npc('hemuli'));
        if (v === 'vana' && npc('vana')) { const n = npc('vana'); n.ai = 'kanni'; n.aiT = 30; const h = g.hq(team); if (h) { n.x = h.x + 3; n.y = h.y + 3; n.path = null; } }
        if (v === 'mummo' && npc('pullomummo')) { const n = npc('pullomummo'); const h = g.hq(team); if (h) { n.x = h.x + 2; n.y = h.y + 3; n.path = null; } for (const u of mine) u.carry = Math.max(u.carry, 3); }
        if (v === 'tekstari' && mine[0]) { mine[0].k = 100; g.tekstariP = 1; setTimeout(() => { g.tekstariP = 0; }, 6000); }
        if (v === 'grilli' || v === 'bileet' || v === 'piiritys') {
          const b = g.buildings.find(x => x.tyyppi === (v === 'grilli' ? 'pihagrilli' : 'kerrostalo')); if (b) { b.owner = team; b.grilliT = 1; }
          if (b && v !== 'grilli') for (let i = 0; i < (v === 'bileet' ? 4 : 6); i++) { const u = g._spawnUnitNear(team, 'lahiojermu', b.x, b.y + 2); u.state = 'talo'; u.target = { b: b.id }; u.path = null; }
        }
        return;
      }
      if (msg.spawn) { const h = g.hq(team); g._spawnUnitNear(team, String(msg.spawn), h.x, h.y + 1.5); }
      return;
    }
    r.game.command(team, msg);
  });
  ws.on('close', () => {
    if (r.slots[team] === ws) r.slots[team] = null;
    lobbyInfo(r);
    if (!r.slots[1] && !r.slots[2]) r.emptySince = Date.now();
  });
});

// heartbeat: pitää yhteyden auki välityspalvelimien (esim. Render) läpi ja siivoaa kuolleet yhteydet
setInterval(() => {
  for (const ws of wss.clients) {
    if (ws.isAlive === false) { ws.terminate(); continue; }
    ws.isAlive = false; try { ws.ping(); } catch {}
  }
}, 25000);

// tyhjien huoneiden siivous
setInterval(() => {
  for (const [code, r] of rooms) {
    if ((r.emptySince && Date.now() - r.emptySince > 5 * 60 * 1000) || (r.endedAt && Date.now() - r.endedAt > 30 * 60 * 1000)) {
      clearInterval(r.timer); rooms.delete(code);
    }
  }
}, 30000);

server.listen(PORT, () => console.log(`Lähiösota käynnissä: http://localhost:${PORT}`));
