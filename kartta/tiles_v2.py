# pelikentta_v2_tiles.json: v1-ruudukko + OSM-tiet (3), polut (13 'polku') ja sillat (12) suoraan OSM-viivageometriasta.
# Ajo: python3 tiles_v2.py   (lukee pelikentta_v1_tiles.json + raw/*.osm, ei muuta v1:tä)
# Karttadata © OpenStreetMap contributors (ODbL 1.0).
import json, os, math, copy
from collections import Counter, deque
import numpy as np
import osm_vektorit as OV
HERE = os.path.dirname(os.path.abspath(__file__))
T = 32; N = 64
RUOHO, METSA, VESI, TIE, MOOTTORI, RATA, RAKENNUS, TEOLLISUUS, PELTO, SUO, KALLIO, PUISTO, SILTA, POLKU = range(14)
OBST = {VESI, MOOTTORI, RAKENNUS}
ROAD_GRID = {'ramppi', 'paatie', 'katu', 'huoltotie'}
SKIP_SERVICE = {'parking_aisle', 'driveway', 'drive-through'}
PATH_GRID = {'polku'}
PATH_ON = {METSA, SUO, KALLIO, PUISTO}

def traverse(pts):
    """Ruudut joiden läpi polylinja kulkee, järjestyksessä, 4-yhtenäisenä (viistoaskeleet täydennetään)."""
    seq = []
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        L = math.hypot(xb - xa, yb - ya); n = max(1, int(L / 0.25))
        for i in range(n + 1):
            x = xa + (xb - xa) * i / n; y = ya + (yb - ya) * i / n
            c, r = int(math.floor(x / T)), int(math.floor(y / T))
            if not seq or seq[-1][:2] != (r, c): seq.append((r, c, x, y))
    out = []
    for k, (r, c, x, y) in enumerate(seq):
        if out:
            pr, pc = out[-1][:2]
            if abs(pr - r) == 1 and abs(pc - c) == 1:
                # viistoaskel: valitse se välisruutu, jota viiva on lähempänä
                cand = [(pr, c), (r, pc)]
                def dist(t):
                    cx, cy = (t[1] + .5) * T, (t[0] + .5) * T; return math.hypot(cx - x, cy - y)
                m = min(cand, key=dist); out.append((m[0], m[1], None, None))
        out.append((r, c, x, y))
    return [(r, c) for (r, c, _, _) in out if 0 <= r < N and 0 <= c < N]

def build(verbose=True):
    J = json.load(open(os.path.join(HERE, 'pelikentta_v1_tiles.json')))
    G1 = np.array(J['terrain']); G = G1.copy()
    V = OV.load()
    sites = {(b['row'] + dr, b['col'] + dc) for b in J['bases'] + J['resources'] for dr in (0, 1) for dc in (0, 1)}
    # moottoritiesiltojen ruudut (alikulut)
    mw_bridge = set()
    for v in V:
        if v['luokka'] in ('moottoritie', 'ramppi') and v['bridge']: mw_bridge |= set(traverse(v['pts']))
    # rata-ruutu muuttuu tieksi vain tasoristeyksessä: tien segmentti leikkaa radan segmentin samassa ruudussa
    rail_segs = {}
    for v in V:
        if v['luokka'] == 'rata' and not v['tunnel']:
            for a, b in zip(v['pts'], v['pts'][1:]):
                for t in set(traverse([a, b])): rail_segs.setdefault(t, []).append((a, b))
    def crosses_rail(pts, tile):
        def ccw(A, B, C): return (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
        def inter(p1, p2, p3, p4): return (ccw(p1, p2, p3) * ccw(p1, p2, p4) < 0) and (ccw(p3, p4, p1) * ccw(p3, p4, p2) < 0)
        for a, b in zip(pts, pts[1:]):
            if tile not in traverse([a, b]): continue
            for (c, d) in rail_segs.get(tile, []):
                if inter(a, b, c, d):
                    return True
        return False
    why = Counter()
    road_tiles, path_tiles, bridge_tiles = set(), set(), set()
    for v in V:
        if v['tunnel']: continue
        isroad = v['luokka'] in ROAD_GRID and not (v['luokka'] == 'huoltotie' and v['service'] in SKIP_SERVICE)
        ispath = v['luokka'] in PATH_GRID
        if not (isroad or ispath): continue
        for (r, c) in traverse(v['pts']):
            t = G1[r, c]
            if t == SILTA: continue
            if t in (VESI, MOOTTORI):
                if v['bridge']: bridge_tiles.add((r, c)); why['silta: tie/polku sillalla esteen yli'] += 1
                elif t == MOOTTORI and (r, c) in mw_bridge: bridge_tiles.add((r, c)); why['silta: alikulku moottoritiesillan alta'] += 1
                continue
            if t == RAKENNUS:
                # vain oikeat kadut halkaisevat korttelin; huoltotiet/polut eivät
                if isroad and v['luokka'] != 'huoltotie': road_tiles.add((r, c))
                continue
            if t == RATA:
                if isroad and crosses_rail(v['pts'], (r, c)): road_tiles.add((r, c)); why['tasoristeys rata->tie'] += 1
                continue
            if isroad: road_tiles.add((r, c))
            elif t in PATH_ON: path_tiles.add((r, c))
    for (r, c) in path_tiles: G[r, c] = POLKU
    for (r, c) in road_tiles: G[r, c] = TIE
    for (r, c) in bridge_tiles: G[r, c] = SILTA
    J2 = copy.deepcopy(J)
    J2['name'] = 'Lähiösota: Etelä-Tampere – taistelukenttä v2'; J2['version'] = 2
    J2['terrain_types'] = J['terrain_types'] + [dict(id=13, key='polku', kuvaus='Metsäpolku – nopeampi kuin metsä', move_cost=0.8)]
    J2['terrain'] = G.tolist()
    J2['muutokset_v1'] = 'Tiet (3), sillat (12) ja metsäpolut (13) päivitetty OSM-viivageometriasta (kartta/tiles_v2.py).'
    # tarkistukset
    cost = {t['id']: t['move_cost'] for t in J2['terrain_types']}
    for (r, c) in sites: assert cost[int(G[r, c])] is not None or cost[int(G1[r, c])] is None, f'rakennuspaikka {r},{c} muuttui esteeksi'
    site_changes = [(r, c, int(G1[r, c]), int(G[r, c])) for (r, c) in sorted(sites) if G1[r, c] != G[r, c]]
    def bfs(grid, s, g):
        seen = {s}; q = deque([(s, 0)])
        while q:
            (r, c), d = q.popleft()
            if (r, c) == g: return d
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < N and 0 <= cc < N and (rr, cc) not in seen and cost[int(grid[rr, cc])] is not None:
                    seen.add((rr, cc)); q.append(((rr, cc), d + 1))
        return None
    b1, b2 = [(b['row'], b['col']) for b in J['bases']]
    reach = (bfs(G1, b1, b2), bfs(G, b1, b2))
    # tieverkon yhtenäisyys ruudukossa (4-naapuruus, tie+silta)
    def comps(grid, vals):
        seen = np.zeros(grid.shape, bool); sizes = []
        for r in range(N):
            for c in range(N):
                if grid[r, c] in vals and not seen[r, c]:
                    q = [(r, c)]; seen[r, c] = True; n = 0
                    while q:
                        a, b = q.pop(); n += 1
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            rr, cc = a + dr, b + dc
                            if 0 <= rr < N and 0 <= cc < N and not seen[rr, cc] and grid[rr, cc] in vals: seen[rr, cc] = True; q.append((rr, cc))
                    sizes.append(n)
        return sorted(sizes, reverse=True)
    stats = dict(
        muutokset=Counter(f"{J2['terrain_types'][a]['key']}->{J2['terrain_types'][b]['key']}" for a, b in zip(G1.flatten(), G.flatten()) if a != b),
        maarat_v1={t['key']: int((G1 == t['id']).sum()) for t in J2['terrain_types']},
        maarat_v2={t['key']: int((G == t['id']).sum()) for t in J2['terrain_types']},
        bfs_askeleet_v1_v2=reach, rakennuspaikkojen_muutokset=site_changes, siltasyyt=why,
        tieverkon_komponentit_v1=comps(G1, {TIE, SILTA})[:8], tieverkon_komponentit_v2=comps(G, {TIE, SILTA})[:8])
    json.dump(J2, open(os.path.join(HERE, 'pelikentta_v2_tiles.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    if verbose:
        for k, v in stats.items(): print(k, dict(v) if isinstance(v, Counter) else v)
    return J2, stats

if __name__ == '__main__':
    build()
