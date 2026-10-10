# Lähiösota: Etelä-Tampere – yhtenäinen maalattu pikselitaidetausta pelikentälle (Grafiikkabotti)
# Ajo: python3 generoi_kartta.py   (seedattu, toistettava; kesto ~1 min)
# Pohja: ../kartta/pelikentta_v1_tiles.json, 64x64 ruutua, 32 px/ruutu -> 2048x2048.
# Karttadata © OpenStreetMap contributors (ODbL).
import os, sys, json, math, random
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from generoi import outline as px_outline
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(HERE, 'kartta'); os.makedirs(OUTD, exist_ok=True)
SEED = 1995
T = 32; N = 64; W = T * N
J = json.load(open(os.path.join(ROOT, 'kartta', 'pelikentta_v1_tiles.json')))
G = np.array(J['terrain'], dtype=np.int16)
RUOHO, METSA, VESI, TIE, MOOTTORI, RATA, RAKENNUS, TEOLLISUUS, PELTO, SUO, KALLIO, PUISTO, SILTA = range(13)
OBST = {VESI, MOOTTORI, RAKENNUS}
R = random.Random(SEED)

def H(h): h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)
def inb(r, c): return 0 <= r < N and 0 <= c < N

# ---------------------------------------------------------------- kohina
def vnoise(cell, seed, interp=Image.BICUBIC):
    n = W // cell + 3
    g = np.random.default_rng(seed).random((n, n)).astype(np.float32)
    im = Image.fromarray(g, 'F').resize((n * cell, n * cell), interp)
    a = np.asarray(im)[cell:cell + W, cell:cell + W]
    return a
def fbm(seed, cells=(256, 96, 32, 12), weights=(.45, .3, .17, .08)):
    a = sum(w * vnoise(c, seed + i * 101) for i, (c, w) in enumerate(zip(cells, weights)))
    return (a - a.min()) / (a.max() - a.min() + 1e-6)
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - .47
BAY = np.tile(BAYER4, (W // 4, W // 4))
YY, XX = np.mgrid[0:W, 0:W]
CHECK = ((XX + YY) & 1).astype(bool)

def ramp(v, cols, dither=.09):
    """Kvantisoi arvo 0..1 väriportaisiin järjestetyllä (Bayer) ditheröinnillä."""
    k = len(cols); idx = np.clip(((v + BAY * dither) * k).astype(np.int32), 0, k - 1)
    return np.stack(cols)[idx]

# ---------------------------------------------------------------- pohjamaasto per ruutu
def base_grid():
    """Tie/rata/silta-ruuduille valitaan alla näkyvä maasto naapureista (tiet piirretään vektoreina päälle)."""
    B = G.copy(); natural_pass = {RUOHO, METSA, TEOLLISUUS, PELTO, SUO, KALLIO, PUISTO}
    for r in range(N):
        for c in range(N):
            t = G[r, c]
            if t not in (TIE, RATA, SILTA): continue
            pool = natural_pass if t != SILTA else (natural_pass | {VESI, MOOTTORI})
            best = None
            for rad in (1, 2, 3, 5):
                cnt = {}
                for dr in range(-rad, rad + 1):
                    for dc in range(-rad, rad + 1):
                        if inb(r + dr, c + dc) and G[r + dr, c + dc] in pool:
                            v = G[r + dr, c + dc]; cnt[v] = cnt.get(v, 0) + (3 if v in (VESI, MOOTTORI) and t == SILTA else 1)
                if cnt: best = max(cnt, key=cnt.get); break
            B[r, c] = best if best is not None else RUOHO
    return B

def gauss_blur(a, sigma):
    rad = int(sigma * 3) + 1; x = np.arange(-rad, rad + 1); k = np.exp(-x ** 2 / (2 * sigma ** 2)); k /= k.sum()
    p = np.pad(a, rad, mode='edge')
    p = np.apply_along_axis(lambda m: np.convolve(m, k, 'valid'), 0, p)
    p = np.apply_along_axis(lambda m: np.convolve(m, k, 'valid'), 1, p)
    return p
def soft_mask(tile_mask, sigma_px):
    S = 8; up = np.kron(tile_mask.astype(np.float32), np.ones((S, S), np.float32))        # 512x512
    b = gauss_blur(up, sigma_px / (T / S)).astype(np.float32)
    return np.asarray(Image.fromarray(b, 'F').resize((W, W), Image.BILINEAR))

def classify(B):
    sig = {VESI: 13}; amp = {VESI: .3, MOOTTORI: .1, RAKENNUS: .15}
    best = np.full((W, W), -9, np.float32); second = np.full((W, W), -9, np.float32)
    cb = np.zeros((W, W), np.uint8); cs = np.zeros((W, W), np.uint8)
    for c in sorted(set(B.flatten().tolist())):
        s = soft_mask(B == c, sig.get(c, 6)) + amp.get(c, .32) * (fbm(SEED + 7 * c, (64, 24, 8), (.5, .32, .18)) - .5)
        hi = s > best; mid = (~hi) & (s > second)
        second = np.where(hi, best, np.where(mid, s, second)); cs = np.where(hi, cb, np.where(mid, c, cs)).astype(np.uint8)
        best = np.where(hi, s, best); cb = np.where(hi, c, cb).astype(np.uint8)
    # ditheröity siirtymävyö (ei estemaastoissa, jotta esteiden reuna pysyy selvänä)
    gap = best - second
    obst = np.isin(cb, list(OBST)) | np.isin(cs, list(OBST))
    swap = (gap < .05) & CHECK & ~obst
    cls = np.where(swap, cs, cb).astype(np.uint8)
    return cls

# ---------------------------------------------------------------- tekstuurit
def textures(cls):
    img = np.zeros((W, W, 3), np.uint8)
    n1 = fbm(SEED + 1); n2 = fbm(SEED + 2, (48, 16, 6), (.5, .3, .2)); fine = np.random.default_rng(SEED + 3).random((W, W)).astype(np.float32)
    def put(c, arr):
        m = cls == c; img[m] = arr[m]
    put(RUOHO, ramp(.55 * n1 + .45 * n2, [H('#3d6424'), H('#4a7530'), H('#558234'), H('#62903c'), H('#6f9a44')]))
    put(METSA, ramp(.5 * n1 + .5 * n2, [H('#1f3a1a'), H('#284822'), H('#30522a'), H('#3a5c2c')]))
    put(MOOTTORI, ramp(.4 * n1 + .6 * n2, [H('#3a5428'), H('#45602e'), H('#506a34')]))
    put(PUISTO, ramp(.35 * n2 + .65 * (((XX + YY // 3) // 10) % 2) * .5 + .2 * n1, [H('#5a8a34'), H('#64963a'), H('#70a242'), H('#7aac4a')]))
    put(TEOLLISUUS, ramp(.6 * n2 + .4 * fine, [H('#4c4e51'), H('#55575a'), H('#5e6063'), H('#686a6c')], .05))
    put(RAKENNUS, ramp(.6 * n2 + .4 * fine, [H('#5a5c5a'), H('#646660'), H('#6e6e68')], .05))
    yard = (fbm(SEED + 60, (40, 14), (.6, .4)) > .5) & (cls == RAKENNUS)                         # nurmipihoja
    img[yard] = ramp(n2, [H('#456a2a'), H('#4f7830'), H('#5a8434')])[yard]
    put(KALLIO, ramp(.5 * n2 + .3 * fine + .2 * n1, [H('#5c5a56'), H('#6c6a66'), H('#7d7b77'), H('#8e8c88'), H('#a09e98')], .12))
    sm = (fbm(SEED + 30, (40, 14, 5), (.5, .3, .2)) > .62) & (cls == KALLIO)                       # sammal kalliolla
    img[sm] = ramp(n2, [H('#4f6a30'), H('#5a7a34')])[sm]
    # suo: oliivi, mättäät, lammikot
    put(SUO, ramp(.5 * n2 + .5 * fine, [H('#4a5530'), H('#55603a'), H('#636a40'), H('#747448')], .15))
    pools = (fbm(SEED + 40, (36, 12, 5), (.55, .3, .15)) > .64) & (cls == SUO)
    img[pools] = ramp(n2, [H('#2b4550'), H('#33505a')])[pools]
    # pelto: lohkoittain vaihtuva sarkasuunta ja väri
    lab = components(G == PELTO)
    pal = [[H('#8e8a3a'), H('#a39a48'), H('#b0a650')], [H('#6b8a34'), H('#7a9a3e'), H('#88a646')], [H('#6a4a2a'), H('#7a5a34'), H('#8a6a40')]]
    lab_px = np.kron(lab, np.ones((T, T), np.int32))
    out = np.zeros((W, W, 3), np.uint8)
    for k in range(1, lab.max() + 1):
        rr = random.Random(SEED + k); ang = rr.choice([0, 90, 30, 120]); p = rr.choice(pal)
        a = math.radians(ang); u = XX * math.cos(a) + YY * math.sin(a)
        stripe = ((u // 3) % 2).astype(np.float32)
        sel = lab_px == k
        out[sel] = ramp(.6 * stripe + .25 * n2 + .15 * fine, p, .05)[sel]
    m = (cls == PELTO) & (lab_px > 0); img[m] = out[m]
    m = (cls == PELTO) & (lab_px == 0); img[m] = ramp(n2, pal[1])[m]
    # vesi: syvyys pehmennetystä maskista
    wdeep = soft_mask(G == VESI, 40)
    v = np.clip((wdeep - .45) / .55, 0, 1) * .75 + .25 * n2
    put(VESI, ramp(1 - v, [H('#1d4672'), H('#24527e'), H('#2d5f8c'), H('#386c98'), H('#4a7ea6')], .12))
    return img

def components(mask):
    lab = np.zeros(mask.shape, np.int32); k = 0
    for r in range(N):
        for c in range(N):
            if mask[r, c] and not lab[r, c]:
                k += 1; st = [(r, c)]; lab[r, c] = k
                while st:
                    a, b = st.pop()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if inb(a + dr, b + dc) and mask[a + dr, b + dc] and not lab[a + dr, b + dc]:
                            lab[a + dr, b + dc] = k; st.append((a + dr, b + dc))
    return lab

def dilate(m, n):
    m = m.copy()
    for _ in range(n):
        o = m.copy(); o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]; m = o
    return m

def shores(img, cls):
    water = cls == VESI; land = ~water
    near_land = dilate(land, 2) & water; edge = dilate(land, 1) & water
    img[near_land] = H('#4f86ae'); img[edge] = H('#8fb8d8')
    near_w = dilate(water, 4) & land & np.isin(cls, [RUOHO, PUISTO, METSA, SUO, PELTO])
    sandy = near_w & (fbm(SEED + 50, (48, 16), (.6, .4)) > .45)
    img[near_w & ~sandy] = ramp(fbm(SEED + 51, (12, 4), (.6, .4)), [H('#4a6a2a'), H('#5a7a30'), H('#7a8a40')])[near_w & ~sandy]
    img[sandy] = ramp(fbm(SEED + 52, (10, 4), (.6, .4)), [H('#a8986a'), H('#bba878'), H('#c9b888')])[sandy]
    # kaislikkoa ja välkettä
    rr = np.random.default_rng(SEED + 53)
    ys, xs = np.nonzero(dilate(land, 5) & water & ~edge)
    for i in rr.choice(len(ys), size=min(len(ys), 900), replace=False):
        y, x = ys[i], xs[i]
        if y > 3: img[y - 3:y + 1, x] = H('#5a7a34'); img[y - 3, x] = H('#7a6a3a')
    ys, xs = np.nonzero(water & ~dilate(land, 8))
    for i in rr.choice(len(ys), size=min(len(ys), 500), replace=False):
        y, x = ys[i], min(xs[i], W - 3); img[y, x:x + 3] = H('#6a9ac0'); img[y, x + 1] = H('#cfe6f5')

# ---------------------------------------------------------------- vektorit
def tc(r, c): return ((c + .5) * T, (r + .5) * T)
def chaikin(p, it=2):
    for _ in range(it):
        if len(p) < 3: return p
        q = [p[0]]
        for a, b in zip(p, p[1:]):
            q += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        q.append(p[-1]); p = q
    return p
def walk(pts, step):
    """Pisteet tasavälein polylinjalla + yksikkötangentti."""
    out = []; carry = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0: continue
        tx, ty = (x1 - x0) / L, (y1 - y0) / L; s = carry
        while s < L: out.append((x0 + tx * s, y0 + ty * s, tx, ty)); s += step
        carry = s - L
    return out
def offset(pts, d):
    res = []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, ty) or 1
        res.append((x - ty / L * d, y + tx / L * d))
    return res
def smooth_line(xs, ys, win):
    xs = np.array(xs, float); k = np.ones(win) / win; p = np.pad(xs, win // 2, mode='edge')
    return list(zip(np.convolve(p, k, 'valid'), ys))

def bridge_axis(r, c):
    def is_route(rr, cc): return inb(rr, cc) and G[rr, cc] in (TIE, RATA, SILTA)
    def is_ob(rr, cc): return inb(rr, cc) and G[rr, cc] in OBST
    v = (is_route(r - 1, c) + is_route(r + 1, c)) + 2 * (is_ob(r, c - 1) + is_ob(r, c + 1))
    h = (is_route(r, c - 1) + is_route(r, c + 1)) + 2 * (is_ob(r - 1, c) + is_ob(r + 1, c))
    return 'v' if v >= h else 'h'

def road_graph():
    nodes = {(r, c) for r in range(N) for c in range(N) if G[r, c] == TIE}
    adj = {n: set() for n in nodes}
    for (r, c) in nodes:
        for dr, dc in ((0, 1), (1, 0)):
            if (r + dr, c + dc) in nodes: adj[(r, c)].add((r + dr, c + dc)); adj[(r + dr, c + dc)].add((r, c))
        for dc in (1, -1):
            o = (r + 1, c + dc)
            if o in nodes and (r + 1, c) not in nodes and (r, c + dc) not in nodes \
               and G[r + 1, c] not in OBST and G[r, c + dc] not in OBST:
                adj[(r, c)].add(o); adj[o].add((r, c))
    # tasoristeykset: tie - rata - tie
    extra = []
    for r in range(N):
        for c in range(N):
            if G[r, c] == RATA:
                for (a, b) in (((r, c - 1), (r, c + 1)), ((r - 1, c), (r + 1, c))):
                    if a in nodes and b in nodes: extra.append((a, b))
    return nodes, adj, extra

def chains(nodes, adj):
    seen = set(); out = []
    def key(a, b): return (a, b) if a < b else (b, a)
    for n in sorted(nodes):
        if len(adj[n]) == 2: continue
        for m in sorted(adj[n]):
            if key(n, m) in seen: continue
            ch = [n, m]; seen.add(key(n, m)); prev, cur = n, m
            while len(adj[cur]) == 2:
                nx = [x for x in adj[cur] if x != prev][0]
                if key(cur, nx) in seen: break
                seen.add(key(cur, nx)); ch.append(nx); prev, cur = cur, nx
            out.append(ch)
    for n in sorted(nodes):   # pelkkiä 2-asteen silmukoita
        for m in sorted(adj[n]):
            if key(n, m) not in seen:
                ch = [n, m]; seen.add(key(n, m)); prev, cur = n, m
                while True:
                    nx = [x for x in adj[cur] if x != prev and key(cur, x) not in seen]
                    if not nx: break
                    seen.add(key(cur, nx[0])); ch.append(nx[0]); prev, cur = cur, nx[0]
                out.append(ch)
    return out

def motorway_lines():
    xs, ys = [], []
    for r in range(1, N):
        cs = [c for c in range(N) if G[r, c] in (MOOTTORI, SILTA) and c > 33]
        xs.append((np.mean(cs) + .5) * T); ys.append((r + .5) * T)
    xs = [xs[0] + (xs[0] - xs[3]) / 3 * 1.6] + xs + [xs[-1] + (xs[-1] - xs[-4]) / 3 * 1.2]
    ys = [-24] + ys + [W + 24]
    main = smooth_line(xs, ys, 7)
    top = [(21.3 * T, -30), (22.2 * T, 2), (23.2 * T, 12), (32.8 * T, 12), (33.8 * T, 2), (34.7 * T, -30)]
    return [main, chaikin(top, 3)]

def rail_line():
    xs, ys = [], []
    for r in range(1, N):
        cs = [c for c in range(N) if G[r, c] == RATA or (G[r, c] == SILTA and r > 50)]
        if cs: xs.append((np.mean(cs) + .5) * T); ys.append((r + .5) * T)
    xs = [xs[0] + (xs[0] - xs[2]) / 2 * 1.5] + xs + [xs[-1] + (xs[-1] - xs[-3]) / 2 * 1.5]
    ys = [-24] + ys + [W + 24]
    return smooth_line(xs, ys, 5)

def C(h, a=255): v = H(h); return (int(v[0]), int(v[1]), int(v[2]), a)

def draw_motorway(d, lines):
    for i, pts in enumerate(lines):
        w = 46 if i == 0 else 38
        d.line(pts, fill=C('#2e3032'), width=w + 6, joint='curve')
        d.line(pts, fill=C('#9a9c9e'), width=w + 2, joint='curve')          # kaiteet
        d.line(pts, fill=C('#3d3f42'), width=w, joint='curve')
        d.line(offset(pts, w / 2 - 3), fill=C('#d8d8d0'), width=1); d.line(offset(pts, -(w / 2 - 3)), fill=C('#d8d8d0'), width=1)
        if i == 0:
            d.line(pts, fill=C('#4a6630'), width=4); d.line(offset(pts, 2.5), fill=C('#b0b2b4'), width=1); d.line(offset(pts, -2.5), fill=C('#b0b2b4'), width=1)
            lanes = (11, -11)
        else:
            d.line(pts, fill=C('#c9b23a'), width=1); lanes = (9, -9)
        for lo in lanes:
            for j, (x, y, tx, ty) in enumerate(walk(offset(pts, lo), 4)):
                if j % 4 < 2: d.point((x, y), fill=C('#d8d8d0')); d.point((x + tx, y + ty), fill=C('#d8d8d0'))

def draw_roads(d, nodes, adj, extra, bridges):
    chs = chains(nodes, adj)
    polys = []
    for ch in chs:
        pts = [tc(*n) for n in ch]
        polys.append(chaikin(pts, 2))
    for (a, b) in extra: polys.append([tc(*a), tc(*b)])
    stubs = []
    for (r, c) in nodes:
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            rr, cc = r + dr, c + dc
            if (rr, cc) in bridges: stubs.append([tc(r, c), ((c + .5 + dc * .9) * T, (r + .5 + dr * .9) * T)])
            if not inb(rr, cc): stubs.append([tc(r, c), ((c + .5 + dc) * T, (r + .5 + dr) * T)])
        if len(adj[(r, c)]) == 0 and not any((r + dr, c + dc) in bridges for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0))):
            stubs.append([((c + .2) * T, (r + .5) * T), ((c + .8) * T, (r + .5) * T)])
    blocks = [(r, c) for (r, c) in nodes if {(r, c + 1), (r + 1, c), (r + 1, c + 1)} <= nodes]
    allp = polys + stubs
    WR, WC = 15, 19
    for p in allp:   # reunakivet / piennar
        d.line(p, fill=C('#8a8a84'), width=WC, joint='curve')
        for q in (p[0], p[-1]): d.ellipse([q[0] - WC / 2, q[1] - WC / 2, q[0] + WC / 2, q[1] + WC / 2], fill=C('#8a8a84'))
    for (r, c) in blocks: d.rectangle([(c + .5) * T - WC / 2, (r + .5) * T - WC / 2, (c + 1.5) * T + WC / 2, (r + 1.5) * T + WC / 2], fill=C('#8a8a84'))
    for p in allp:
        d.line(p, fill=C('#4a4c50'), width=WR, joint='curve')
        for q in (p[0], p[-1]): d.ellipse([q[0] - WR / 2, q[1] - WR / 2, q[0] + WR / 2, q[1] + WR / 2], fill=C('#4a4c50'))
    for (r, c) in blocks: d.rectangle([(c + .5) * T - WR / 2, (r + .5) * T - WR / 2, (c + 1.5) * T + WR / 2, (r + 1.5) * T + WR / 2], fill=C('#4a4c50'))
    # keskiviiva katkoviivana pidemmille osuuksille (ei risteyksissä)
    for ch, p in zip(chs, polys):
        if len(ch) < 3: continue
        pts = walk(p, 1); n = len(pts)
        for j, (x, y, tx, ty) in enumerate(pts):
            if 12 < j < n - 12 and (j // 4) % 2 == 0: d.point((x, y), fill=C('#d8d4c0'))

def draw_bridges(d, bridges):
    for (r, c) in sorted(bridges):
        ax = bridge_axis(r, c); x0, y0 = c * T, r * T
        if ax == 'h':
            d.rectangle([x0 - 2, y0 + 7, x0 + T + 1, y0 + 27], fill=(0, 0, 0, 90))                       # varjo alle
            d.rectangle([x0 - 2, y0 + 4, x0 + T + 1, y0 + 25], fill=C('#2a2a2c'))
            d.rectangle([x0 - 2, y0 + 5, x0 + T + 1, y0 + 24], fill=C('#8d8f92'))
            d.rectangle([x0 - 2, y0 + 8, x0 + T + 1, y0 + 21], fill=C('#55575a'))
            for x in range(x0, x0 + T, 4): d.point((x, y0 + 6), fill=C('#cfd2d6')); d.point((x, y0 + 23), fill=C('#cfd2d6'))
            d.line([(x0 - 2, y0 + 5), (x0 + T + 1, y0 + 5)], fill=C('#c8ccd0'))
        else:
            d.rectangle([x0 + 7, y0 - 2, x0 + 27, y0 + T + 1], fill=(0, 0, 0, 90))
            d.rectangle([x0 + 4, y0 - 2, x0 + 25, y0 + T + 1], fill=C('#2a2a2c'))
            d.rectangle([x0 + 5, y0 - 2, x0 + 24, y0 + T + 1], fill=C('#8d8f92'))
            d.rectangle([x0 + 8, y0 - 2, x0 + 21, y0 + T + 1], fill=C('#55575a'))
            for y in range(y0, y0 + T, 4): d.point((x0 + 6, y), fill=C('#cfd2d6')); d.point((x0 + 23, y), fill=C('#cfd2d6'))
            d.line([(x0 + 5, y0 - 2), (x0 + 5, y0 + T + 1)], fill=C('#c8ccd0'))

def draw_rail(d, pts):
    d.line(pts, fill=C('#5a554c'), width=20, joint='curve')
    d.line(pts, fill=C('#7d7466'), width=17, joint='curve')
    for j, (x, y, tx, ty) in enumerate(walk(pts, 1)):
        if (j * 7) % 5 == 0: d.point((x - ty * ((j * 13) % 15 - 7), y + tx * ((j * 13) % 15 - 7)), fill=C('#958a78'))
    for (x, y, tx, ty) in walk(pts, 4):
        d.line([(x - ty * 7, y + tx * 7), (x + ty * 7, y - tx * 7)], fill=C('#4a3523'), width=2)
    for o in (-4, 4):
        d.line(offset(pts, o + .8), fill=C('#3a3a3a'), width=1)
        d.line(offset(pts, o), fill=C('#b5b8bc'), width=1)

# ---------------------------------------------------------------- rakennukset (koriste esteruuduilla)
def block(d, x0, y0, x1, y1, rr, wallh=8):
    roof = rr.choice(['#4e5054', '#5a5c60', '#55504c', '#606264', '#4a4846'])
    wall = rr.choice(['#b8b4aa', '#c4bfb4', '#a89c8c', '#9a8a7a', '#c8c4bc'])
    d.rectangle([x0 + 3, y0 + 3, x1 + 4, y1 + 3], fill=(0, 0, 0, 100))                                   # varjo
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=C('#1e1e1e'))
    yw = y1 - wallh
    d.rectangle([x0, y0, x1, yw - 1], fill=C(roof)); d.line([(x0, y0), (x1, y0)], fill=C('#8b8e93'))
    d.line([(x0, y0), (x0, yw - 1)], fill=C('#7a7c80')); d.rectangle([x0 + 1, yw - 1, x1, yw - 1], fill=C('#3a3c40'))
    d.rectangle([x0, yw, x1, y1], fill=C(wall))
    bal = rr.random() < .6; bcol = rr.choice(['#8a3a24', '#9a4e2a', '#6a5040'])
    for y in range(yw + 1, y1 - 1, 3):
        for x in range(x0 + 2, x1 - 1, 3):
            d.point((x, y), fill=C('#2b3a4a') if rr.random() > .12 else C('#e8d27a'))
            if bal and (x - x0) % 9 == 2: d.line([(x - 1, y + 1), (x + 1, y + 1)], fill=C(bcol))
    # katon detaljit: ilmanvaihtohormit, porraskuilut, antennit
    for x in range(x0 + 5, x1 - 4, rr.choice([9, 11, 13])):
        yy = y0 + 3 + rr.randint(0, max(0, (yw - y0) - 8))
        d.rectangle([x, yy, x + 3, yy + 2], fill=C('#9a9da1')); d.line([(x, yy + 3), (x + 3, yy + 3)], fill=C('#2c2d30'))
    if rr.random() < .5:
        ax = rr.randint(x0 + 3, max(x0 + 3, x1 - 4)); d.line([(ax, y0 + 3), (ax, y0 + 8)], fill=C('#2c2d30')); d.line([(ax - 2, y0 + 4), (ax + 2, y0 + 4)], fill=C('#2c2d30'))

def draw_buildings(d, skip):
    rr = random.Random(SEED + 77)
    Bm = (G == RAKENNUS); used = np.zeros_like(Bm)
    for (r, c) in skip: used[r, c] = True
    # vaakalamellit (2-3 ruutua), sitten pystylamellit, sitten pistetalot
    for r in range(N):
        c = 0
        while c < N:
            if Bm[r, c] and not used[r, c]:
                e = c
                while e + 1 < N and Bm[r, e + 1] and not used[r, e + 1] and e - c < 2: e += 1
                if e > c:
                    if e - c == 1 and c + 2 < N and Bm[r, c + 2] and not used[r, c + 2] and rr.random() < .5: e += 1
                    for k in range(c, e + 1): used[r, k] = True
                    block(d, c * T + 3, r * T + 3, (e + 1) * T - 4, (r + 1) * T - 4, rr)
                c = e + 1
            else: c += 1
    for c in range(N):
        for r in range(N - 1):
            if Bm[r, c] and Bm[r + 1, c] and not used[r, c] and not used[r + 1, c]:
                used[r, c] = used[r + 1, c] = True
                block(d, c * T + 5, r * T + 3, (c + 1) * T - 6, (r + 2) * T - 4, rr, wallh=9)
    for r in range(N):
        for c in range(N):
            if Bm[r, c] and not used[r, c]:
                used[r, c] = True; block(d, c * T + 5, r * T + 4, (c + 1) * T - 6, (r + 1) * T - 4, rr, wallh=8)

# ---------------------------------------------------------------- puut ja pikkudetaljit
def tree_sprites():
    sp = []
    for v in range(4):   # kuuset
        h = 14 + v * 2; w = 9 + v; im = Image.new('RGBA', (w + 2, h + 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = (w + 2) // 2
        for i, f in enumerate((1.0, .75, .5)):
            top = int(i * h * .28); d.polygon([(cx, top), (cx - int(w / 2 * f + 1), top + int(h * .5)), (cx + int(w / 2 * f + 1), top + int(h * .5))], fill=C('#1d3b1a'))
            d.polygon([(cx, top + 1), (cx - int(w / 2 * f), top + int(h * .5) - 1), (cx, top + int(h * .5) - 1)], fill=C('#2c5426'))
        d.line([(cx, h - 3), (cx, h)], fill=C('#4a3220'))
        sp.append(('kuusi', px_outline(im, C('#10200e'))))
    for v in range(3):   # koivut
        w = 10 + v * 2; h = 14 + v * 2; im = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = (w + 2) // 2
        d.rectangle([cx - 1, h - 6, cx, h], fill=C('#e8e8e0')); d.point((cx, h - 3), fill=C('#2a2a2a'))
        d.ellipse([1, 1, w, h - 5], fill=C('#41692a')); d.ellipse([2, 1, w - 2, h - 8], fill=C('#557f32')); d.ellipse([3, 2, w - 4, h - 11 + v], fill=C('#6e9a40'))
        sp.append(('koivu', px_outline(im, C('#1a2e12'))))
    return sp

def bush():
    im = Image.new('RGBA', (8, 7), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 7, 6], fill=C('#2f5a24')); d.ellipse([1, 0, 5, 3], fill=C('#4a7a30')); return px_outline(im, C('#18301a'))
def car_sprite(col, vertical=True):
    im = Image.new('RGBA', (5, 9) if vertical else (9, 5), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if vertical:
        d.rectangle([0, 0, 4, 8], fill=C(col)); d.rectangle([1, 2, 3, 3], fill=C('#2b3a4a')); d.rectangle([1, 4, 3, 5], fill=C(col)); d.rectangle([1, 6, 3, 6], fill=C('#2b3a4a'))
    else:
        d.rectangle([0, 0, 8, 4], fill=C(col)); d.rectangle([2, 1, 3, 3], fill=C('#2b3a4a')); d.rectangle([6, 1, 6, 3], fill=C('#2b3a4a'))
    return im

def details(canvas, cls, blocked, sprites):
    """Puut metsiin + harvakseltaan pensaita, kiviä, tölkkejä ja parkkipaikkoja kuljettaville alueille."""
    rr = random.Random(SEED + 99); d = ImageDraw.Draw(canvas)
    items = []
    # metsä: tiheä tärisytetty hila
    step = 8
    for gy in range(0, W, step):
        for gx in range(0, W, step):
            x = gx + rr.randint(0, step - 1); y = gy + rr.randint(0, step - 1)
            if cls[y, x] != METSA or blocked[y, x] or rr.random() < .12: continue
            kind = 'koivu' if rr.random() < .28 else 'kuusi'
            cand = [s for s in sprites if s[0] == kind]; items.append((y, x, rr.choice(cand)[1]))
    # puistot ja nurmet: yksittäisiä koivuja ja pensaita
    for _ in range(9000):
        x, y = rr.randrange(8, W - 8), rr.randrange(8, W - 8); c = cls[y, x]
        if blocked[y, x]: continue
        if c in (PUISTO, RUOHO) and rr.random() < (.06 if c == RUOHO else .1):
            items.append((y, x, rr.choice([s for s in sprites if s[0] == 'koivu'])[1]))
        elif c in (PUISTO, RUOHO, SUO) and rr.random() < .35: items.append((y, x, BUSH))
    def fits(y, x, im):   # koko sprite (latvus mukaan lukien) pysyy pois esteiltä ja teiltä
        w, h = im.size; x0, x1, y0 = max(0, x - w // 2), min(W - 1, x + w // 2), max(0, y - h + 2)
        return not (blocked[y0, x] or blocked[y0, x0] or blocked[y0, x1] or blocked[y, x0] or blocked[y, x1] or blocked[(y + y0) // 2, x0] or blocked[(y + y0) // 2, x1])
    for (y, x, im) in sorted(items, key=lambda t: t[0]):
        if not fits(y, x, im): continue
        w, h = im.size
        d.ellipse([x - w // 2 + 1, y - 2, x + w // 2 + 3, y + 2], fill=(0, 0, 0, 70))
        canvas.alpha_composite(im, (x - w // 2, y - h + 1))
    # kivet, tölkit (vain kuljettavilla, ei teillä)
    for _ in range(6000):
        x, y = rr.randrange(4, W - 4), rr.randrange(4, W - 4); c = cls[y, x]
        if blocked[y, x] or c in (VESI, MOOTTORI, RAKENNUS, METSA): continue
        p = rr.random()
        if p < .35 and c in (RUOHO, KALLIO, PUISTO, PELTO):
            g = rr.choice(['#8a8884', '#9a9894', '#77746f'])
            d.rectangle([x, y, x + 2, y + 1], fill=C(g)); d.point((x, y), fill=C('#b8b6b0')); d.line([(x, y + 2), (x + 2, y + 2)], fill=C('#3a3a38'))
        elif p < (.42 if c == TEOLLISUUS else .5):
            col = rr.choice(['#c8ced6', '#2f6fb0', '#d8b030', '#c03030'])
            d.rectangle([x, y, x + 1, y + 2], fill=C(col)); d.point((x, y), fill=C('#eef2f6'))
    # parkkipaikat teollisuusruuduilla
    cols = ['#c03030', '#2f6fb0', '#e8e8e4', '#3a3a3c', '#d8b030', '#5a7a4a', '#8a8e92']
    for r in range(N):
        for c in range(N):
            if G[r, c] != TEOLLISUUS or rr.random() > .35: continue
            x0, y0 = c * T, r * T
            if blocked[y0 + 16, x0 + 16] or cls[y0 + 16, x0 + 16] != TEOLLISUUS: continue
            for row in (0, 1):
                yy = y0 + 4 + row * 13
                for k in range(5):
                    x = x0 + 3 + k * 6
                    if blocked[yy + 4, x + 3] or cls[yy + 4, x + 3] != TEOLLISUUS: continue
                    d.line([(x, yy), (x, yy + 9)], fill=C('#c8c8c0'))
                    if rr.random() < .35: canvas.alpha_composite(car_sprite(rr.choice(cols)), (x + 1, yy + 1))
                d.line([(x0 + 3 + 5 * 6, yy), (x0 + 3 + 5 * 6, yy + 9)], fill=C('#c8c8c0')) if x0 + 33 < W else None
    # öljytahroja ja halkeamia asfaltilla
    for _ in range(1500):
        x, y = rr.randrange(4, W - 6), rr.randrange(4, W - 6)
        if cls[y, x] == TEOLLISUUS and not blocked[y, x]:
            if rr.random() < .5: d.ellipse([x, y, x + 3, y + 2], fill=C('#3e4043'))
            else: d.line([(x, y), (x + rr.randint(-4, 4), y + rr.randint(2, 6))], fill=C('#3a3c3e'))

def plaza(d, col, row):
    x0, y0, x1, y1 = col * T - 4, row * T - 4, (col + 2) * T + 3, (row + 2) * T + 3
    d.rounded_rectangle([x0, y0, x1, y1], 6, fill=C('#8a8680'))
    d.rounded_rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], 5, fill=C('#a29d94'))
    for x in range(x0 + 6, x1 - 2, 6): d.line([(x, y0 + 3), (x, y1 - 3)], fill=C('#958f86'))
    for y in range(y0 + 6, y1 - 2, 6): d.line([(x0 + 3, y), (x1 - 3, y)], fill=C('#958f86'))

# ---------------------------------------------------------------- pääohjelma
def main():
    global BUSH
    BUSH = bush()
    B = base_grid()
    cls = classify(B)
    img = textures(cls); shores(img, cls)
    canvas = Image.fromarray(img, 'RGB').convert('RGBA')
    # tiet yms. maskiin, jotta detaljit eivät mene niiden päälle
    nodes, adj, extra = road_graph()
    bridges = {(r, c) for r in range(N) for c in range(N) if G[r, c] == SILTA}
    mlines = motorway_lines(); rail = rail_line()
    sites = {(b['col'], b['row']) for b in J['bases']} | {(b['col'], b['row']) for b in J['resources']}
    vm = Image.new('L', (W, W), 0); vd = ImageDraw.Draw(vm)
    for p in mlines: vd.line(p, fill=255, width=60, joint='curve')
    vd.line(rail, fill=255, width=26, joint='curve')
    for ch in chains(nodes, adj): vd.line(chaikin([tc(*n) for n in ch], 2), fill=255, width=26, joint='curve')
    for (r, c) in nodes: vd.ellipse([(c + .5) * T - 13, (r + .5) * T - 13, (c + .5) * T + 13, (r + .5) * T + 13], fill=255)
    for (r, c) in bridges: vd.rectangle([c * T - 4, r * T - 4, (c + 1) * T + 4, (r + 1) * T + 4], fill=255)
    for (c, r) in sites: vd.rectangle([c * T - 8, r * T - 8, (c + 2) * T + 8, (r + 2) * T + 8], fill=255)
    for r in range(N):
        for c in range(N):
            if G[r, c] in OBST: vd.rectangle([c * T - 2, r * T - 2, (c + 1) * T + 1, (r + 1) * T + 1], fill=255)
    blocked = np.asarray(vm) > 0
    details(canvas, cls, blocked, tree_sprites())
    ov = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for (c, r) in sorted(sites): plaza(d, c, r)
    draw_motorway(d, mlines)
    draw_roads(d, nodes, adj, extra, bridges)
    draw_bridges(d, bridges)
    draw_rail(d, rail)
    canvas.alpha_composite(ov)
    ov = Image.new('RGBA', (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    skip = {(r + dr, c + dc) for (c, r) in sites for dr in (0, 1) for dc in (0, 1)}
    draw_buildings(d, skip)
    canvas.alpha_composite(ov)
    # rajattu paletti, ei ditheröintiä kvantisoinnissa (oma Bayer-dither tekstuureissa)
    q = canvas.convert('RGB').quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(f'{OUTD}/kartta_tausta.png', optimize=True)
    for i in range(4):
        for j in range(4):
            q.crop((j * 512, i * 512, (j + 1) * 512, (i + 1) * 512)).save(f'{OUTD}/kartta_tausta_{i}_{j}.png', optimize=True)
    rgb = q.convert('RGB')
    mini = rgb.resize((256, 256), Image.BOX).quantize(palette=q, dither=Image.Dither.NONE)
    mini.save(f'{OUTD}/minikartta_256.png', optimize=True)
    # debug: ruudukko + esteet punaisella
    dbg = rgb.convert('RGBA'); o = Image.new('RGBA', (W, W), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
    for r in range(N):
        for c in range(N):
            if G[r, c] in OBST: od.rectangle([c * T, r * T, (c + 1) * T - 1, (r + 1) * T - 1], fill=(255, 0, 0, 80))
            elif G[r, c] == SILTA: od.rectangle([c * T, r * T, (c + 1) * T - 1, (r + 1) * T - 1], fill=(0, 255, 0, 70))
    for k in range(N + 1):
        od.line([(k * T, 0), (k * T, W)], fill=(255, 255, 255, 60)); od.line([(0, k * T), (W, k * T)], fill=(255, 255, 255, 60))
    dbg.alpha_composite(o); dbg.convert('RGB').save(f'{OUTD}/debug_ruudukko.png', optimize=True)
    # esikatselut
    rgb.resize((1024, 1024), Image.BOX).save(f'{OUTD}/esikatselu_kartta.png')
    cx, cy = 28 * T + 16, 33 * T + 16
    rgb.crop((cx - 256, cy - 160, cx + 256, cy + 160)).resize((1024, 640), Image.NEAREST).save(f'{OUTD}/esikatselu_kartta_lahikuva.png')
    print('valmis, värejä', len(q.getcolors()))

if __name__ == '__main__':
    main()
