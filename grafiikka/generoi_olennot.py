# Lähiösota: Etelä-Tampere – olennot (metsäpeikko, vesihiisi) + efektit + ikonit (Grafiikkabotti)
# Ajo: python3 generoi_olennot.py   (kirjoittaa vain olennot/, efektit/kivi_8|kuplat_32|loiske_32, ikonit/tapahtuma_{peikot,vesihiisi}, ikonit/ui_{peikko,vesihiisi}, esikatselu_olennot.png)
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from generoi import hx, shade, outline, shadow, SHADOW, OUT, TEAMS, D

os.makedirs(f'{D}/olennot', exist_ok=True)
CLEAR = (0, 0, 0, 0); F = 48
def canvas(w=F, h=F):
    im = Image.new('RGBA', (w, h), CLEAR); return im, ImageDraw.Draw(im)
def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h), CLEAR)
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s
def layer(im, fn):
    l = Image.new('RGBA', im.size, CLEAR); fn(ImageDraw.Draw(l)); im.alpha_composite(l); return im

# ---------------- paletti ----------------
SK = hx('#76826a'); SK_L = hx('#98a486'); SK_D = hx('#525c48'); SK_DD = hx('#33392c'); BELLY = hx('#8e9070')
MOSS = hx('#7aa632'); MOSS_L = hx('#b4d24e'); MOSS_D = hx('#4c7428'); LICHEN = hx('#d6dcb0'); LICHEN2 = hx('#a9c4bc')
EYE = hx('#ff2a1a'); EYE_L = hx('#ffd27a'); TOOTH = hx('#ece4c4'); TWIG = hx('#5a4430')
ROCK = hx('#8c8882'); ROCK_L = hx('#b8b4ac'); ROCK_D = hx('#5c5852')
MOUTH = hx('#5a1418'); YEL = hx('#ffe14a')

def rock(d, x, y, s=7):
    """Kivi, vasen yläkulma (x,y), leveys s."""
    h = s - 1
    d.ellipse([x, y, x + s, y + h], fill=ROCK_D); d.ellipse([x, y, x + s - 1, y + h - 1], fill=ROCK)
    d.ellipse([x + 1, y + 1, x + s // 2 + 1, y + h // 2], fill=ROCK_L); d.point((x + s - 2, y + h - 2), fill=ROCK_D)

def fist(d, x, y, col, nails=True):
    d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=col); d.line([(x - 2, y - 3), (x + 2, y - 3)], fill=shade(col, 1.2))
    d.line([(x - 3, y + 2), (x + 3, y + 2)], fill=shade(col, .75))
    if nails: d.point([(x + 4, y - 1), (x + 4, y + 1), (x + 3, y + 3)], fill=TOOTH)

# =====================================================================
# METSÄPEIKKO 48x48, ankkuri (0.5, 0.9) = jalat y≈43
# =====================================================================
def peikko(b=0, lx=0, fl=(0, 0), bl=(0, 0), fa=(34, 33), ba=(11, 34), rk=(35, 32), mouth=0, hy=0, seed=5):
    im, d = canvas(); r = random.Random(seed)
    d.ellipse([9, 40, 39, 45], fill=SHADOW)
    # jalat (taempi tummempi)
    x = 17 + bl[0]; d.rectangle([x, 33 + b, x + 4, 41 - bl[1]], fill=SK_D); d.ellipse([x - 2, 39 - bl[1], x + 5, 43 - bl[1]], fill=SK_DD)
    x = 25 + fl[0]; d.rectangle([x, 33 + b, x + 5, 41 - fl[1]], fill=SK); d.line([(x, 33 + b), (x, 40 - fl[1])], fill=SK_D)
    d.ellipse([x - 1, 39 - fl[1], x + 8, 43 - fl[1]], fill=SK_D); d.point([(x + 8, 41 - fl[1]), (x + 6, 43 - fl[1])], fill=TOOTH)
    # taempi käsi
    d.line([(15 + lx, 21 + b), ba], fill=SK_DD, width=5); fist(d, ba[0], ba[1], SK_D, nails=False)
    # vartalo
    d.ellipse([10 + lx, 15 + b, 36 + lx, 38 + b], fill=SK_D); d.ellipse([12 + lx, 15 + b, 36 + lx, 36 + b], fill=SK)
    d.ellipse([21 + lx, 24 + b, 35 + lx, 36 + b], fill=BELLY); d.line([(24 + lx, 28 + b), (31 + lx, 28 + b)], fill=SK_L)
    # sammalkyttyrä hartioilla + jäkälä + roikkuvat sammaleet
    d.ellipse([8 + lx, 10 + b, 31 + lx, 25 + b], fill=MOSS_D); d.ellipse([9 + lx, 10 + b, 30 + lx, 22 + b], fill=MOSS)
    for xx in range(10, 30, 3): d.line([(xx + lx, 21 + b), (xx + lx, 23 + b + r.randrange(0, 4))], fill=MOSS_D)
    for _ in range(14): d.point((r.randrange(11, 28) + lx, r.randrange(11, 19) + b), fill=MOSS_L)
    for _ in range(7):
        px_, py_ = r.randrange(11, 27) + lx, r.randrange(12, 20) + b
        d.point([(px_, py_), (px_ + 1, py_)], fill=LICHEN if r.random() < .6 else LICHEN2)
    # pää (eteen, kumarassa)
    hx_, hy_ = lx, b + hy
    d.polygon([(28 + hx_, 15 + hy_), (23 + hx_, 10 + hy_), (29 + hx_, 18 + hy_)], fill=SK_D)                    # korva
    d.ellipse([27 + hx_, 11 + hy_, 39 + hx_, 23 + hy_], fill=SK); d.ellipse([28 + hx_, 17 + hy_, 39 + hx_, 25 + hy_], fill=SK_D)
    d.ellipse([28 + hx_, 16 + hy_, 38 + hx_, 23 + hy_], fill=SK)
    for (a, c) in [((29, 11), (28, 8)), ((32, 10), (33, 7)), ((35, 11), (37, 8))]:                         # risuhiukset
        d.line([(a[0] + hx_, a[1] + hy_), (c[0] + hx_, c[1] + hy_)], fill=TWIG)
    d.point((29 + hx_, 12 + hy_), fill=MOSS_L)
    d.line([(32 + hx_, 13 + hy_), (38 + hx_, 15 + hy_)], fill=SK_DD); d.line([(32 + hx_, 14 + hy_), (37 + hx_, 16 + hy_)], fill=SK_DD)  # vihainen otsa
    d.rectangle([35 + hx_, 16 + hy_, 36 + hx_, 17 + hy_], fill=EYE); d.point((36 + hx_, 16 + hy_), fill=EYE_L)
    d.point((32 + hx_, 17 + hy_), fill=EYE)
    d.polygon([(37 + hx_, 15 + hy_), (44 + hx_, 19 + hy_), (43 + hx_, 21 + hy_), (37 + hx_, 20 + hy_)], fill=SK_L)  # nenä
    d.line([(38 + hx_, 20 + hy_), (43 + hx_, 21 + hy_)], fill=SK_D); d.point((43 + hx_, 18 + hy_), fill=hx('#c48a7a'))
    if mouth:
        d.polygon([(33 + hx_, 21 + hy_), (40 + hx_, 21 + hy_), (39 + hx_, 22 + hy_ + mouth), (34 + hx_, 22 + hy_ + mouth)], fill=MOUTH)
        d.point([(35 + hx_, 22 + hy_), (38 + hx_, 22 + hy_), (36 + hx_, 21 + hy_ + mouth), (37 + hx_, 21 + hy_ + mouth)], fill=TOOTH)
    else:
        d.line([(33 + hx_, 22 + hy_), (39 + hx_, 22 + hy_)], fill=SK_DD); d.point([(38 + hx_, 21 + hy_), (34 + hx_, 21 + hy_)], fill=TOOTH)
    # etukäsi (+ kivi)
    sh = (27 + lx, 22 + b)
    if rk and rk[1] > fa[1]: rock(d, *rk)
    d.line([sh, fa], fill=SK, width=6); d.line([(sh[0] + 1, sh[1] - 2), (fa[0], fa[1] - 3)], fill=SK_L)
    if rk and rk[1] <= fa[1]: rock(d, *rk)
    fist(d, fa[0], fa[1], SK)
    return outline(im)

WALK = [dict(b=0, lx=1, fl=(3, 0), bl=(-2, 0), fa=(33, 33), ba=(13, 34), rk=(34, 32)),
        dict(b=2, lx=0, fl=(0, 0), bl=(0, 2), fa=(35, 34), ba=(11, 35), rk=(36, 33)),
        dict(b=0, lx=-1, fl=(-2, 0), bl=(3, 0), fa=(36, 33), ba=(10, 34), rk=(37, 32)),
        dict(b=2, lx=0, fl=(0, 2), bl=(0, 0), fa=(34, 34), ba=(12, 35), rk=(35, 33))]
ATTACK = [dict(b=2, lx=1, fa=(37, 37), ba=(21, 37), rk=(37, 36), mouth=1),                  # nosto maasta
          dict(b=0, lx=-2, fa=(22, 7), ba=(33, 29), rk=(17, 1), mouth=2, hy=-1),            # kivi pään yllä
          dict(b=1, lx=2, fa=(41, 18), ba=(10, 31), rk=(40, 10), mouth=3, hy=1),            # heitto (irtoaa)
          dict(b=2, lx=1, fa=(38, 33), ba=(11, 33), rk=None, mouth=2, hy=1)]                # jälkiliike
def peikko_hyokkays(i):
    im = peikko(**ATTACK[i])
    if i == 2:   # heilahdusviiru
        layer(im, lambda l: l.arc([16, 2, 46, 34], 200, 300, fill=(255, 255, 255, 150), width=1))
    return im

def peikko_karjuu(i):
    j = i % 2
    im = peikko(b=0, lx=-1 + j, fa=(36, 8 - j), ba=(13, 9 + j), rk=None, mouth=4, hy=-2 + j)
    def lines(l):
        for k, (a, c) in enumerate([((44, 14), (47, 12)), ((45, 19), (47, 19)), ((44, 24), (47, 26))]):
            if (k + j) % 2 == 0 or j: l.line([a, c], fill=(255, 240, 200, 220))
    return layer(im, lines)

def peikko_kaatunut():
    im, d = canvas()
    d.ellipse([4, 36, 44, 45], fill=SHADOW)
    rock(d, 2, 36, 7)
    d.rectangle([40, 35, 43, 41], fill=hx('#c8ced6')); d.rectangle([40, 37, 43, 39], fill=hx('#2f6fb0'))       # tölkki
    # jalat vasemmalla, makaa selällään, pää oikealla
    d.ellipse([7, 30, 15, 36], fill=SK_D); d.ellipse([9, 36, 17, 42], fill=SK)
    d.ellipse([12, 27, 36, 43], fill=SK_D); d.ellipse([13, 27, 36, 41], fill=SK); d.ellipse([16, 28, 32, 36], fill=BELLY)
    d.ellipse([12, 38, 30, 44], fill=MOSS_D); d.line([(14, 40), (28, 40)], fill=MOSS)
    d.point([(17, 41), (22, 42), (26, 41)], fill=LICHEN)
    d.line([(20, 33), (17, 24)], fill=SK, width=5); fist(d, 17, 23, SK)                                  # käsi pystyssä
    d.ellipse([31, 28, 43, 39], fill=SK); d.polygon([(38, 29), (42, 22), (44, 24), (41, 30)], fill=SK_L)  # nenä ylös
    for (x, y) in ((34, 31), (38, 31)):
        d.line([(x - 1, y - 1), (x + 1, y + 1)], fill=SK_DD); d.line([(x - 1, y + 1), (x + 1, y - 1)], fill=SK_DD)
    d.line([(34, 35), (39, 35)], fill=SK_DD); d.rectangle([37, 36, 38, 37], fill=hx('#d86a7a'))
    outline(im)
    d = ImageDraw.Draw(im)
    for (x, y) in ((30, 20), (37, 16), (44, 21)):     # tähdet
        d.point([(x, y - 1), (x - 1, y), (x, y), (x + 1, y), (x, y + 1)], fill=YEL); d.point([(x - 1, y - 1), (x + 1, y + 1)], fill=hx('#ffa020'))
    return im

def kivi8():
    im, d = canvas(8, 8); rock(d, 1, 1, 6); return outline(im)

# =====================================================================
# VESIHIISI 48x48, ankkuri (0.5, 0.9); vedenpinta y=38, rengas keskellä (24,39)
# =====================================================================
YW = 38
B = hx('#2f6a4e'); B_L = hx('#5fa078'); B_D = hx('#1c4232'); FIN = hx('#3fa0a0'); FIN_L = hx('#9fe0d8')
HAIR = hx('#4f8a24'); HAIR_L = hx('#9ac83a'); HAIR_D = hx('#2f5a1c'); CLAW = hx('#e6f0d0')
EYE_Y = hx('#ffe23a'); FOAM = hx('#eaf6ff'); FOAM_B = hx('#9fd0f0'); SUB = (10, 34, 48)

def claws(d, x, y, dirx=1, dy=0):
    for k in (-2, 0, 2): d.line([(x, y + k), (x + 4 * dirx, y + k + dy + (k // 2))], fill=CLAW)

def hiisi_layer(ox=0, oy=0, fa=(38, 28), ba=(9, 31), mouth=0, seed=9):
    im, d = canvas(); r = random.Random(seed)
    def P(x, y): return (x + ox, y + oy)
    # taaemmat levähiukset
    for k in range(6):
        x0 = 17 + k * 2; d.line([P(x0, 9), P(x0 - 4, 22 + r.randrange(0, 8)), P(x0 - 6 + r.randrange(0, 3), 34)], fill=HAIR_D, width=2)
    # taempi käsi + evä
    d.line([P(16, 25), (ba[0] + ox, ba[1] + oy)], fill=B_D, width=4)
    d.polygon([P(13, 27), P(8, 22), P(12, 30)], fill=shade(FIN, .7)); claws(d, ba[0] + ox - 1, ba[1] + oy, -1)
    # vartalo
    d.ellipse([*P(13, 19), *P(33, 50)], fill=B_D); d.ellipse([*P(14, 19), *P(33, 48)], fill=B)
    d.ellipse([*P(22, 25), *P(32, 46)], fill=B_L)
    for yy in (29, 32, 35): d.line([P(24, yy), P(30, yy)], fill=B)              # vatsasuomut
    # pää
    d.ellipse([*P(17, 6), *P(33, 21)], fill=B); d.ellipse([*P(24, 10), *P(34, 21)], fill=B_L)
    d.polygon([P(18, 9), P(14, 3), P(22, 7)], fill=FIN); d.line([P(15, 4), P(19, 8)], fill=FIN_L)     # evä-korva
    d.line([P(25, 10), P(28, 12)], fill=B_D); d.line([P(29, 12), P(32, 10)], fill=B_D)                   # kulmat
    d.rectangle([*P(26, 12), *P(27, 13)], fill=EYE_Y); d.rectangle([*P(30, 12), *P(31, 13)], fill=EYE_Y)
    d.point([P(27, 13), P(31, 13)], fill=OUT)
    if mouth:
        d.polygon([P(24, 16), P(33, 16), P(32, 17 + mouth), P(25, 17 + mouth)], fill=MOUTH)
        d.point([P(26, 16), P(28, 16), P(30, 16), P(32, 16)], fill=CLAW)
    else:
        d.line([P(24, 17), P(33, 16)], fill=B_D); d.point([P(26, 18), P(29, 18), P(32, 17)], fill=CLAW)
    d.line([P(20, 17), P(20, 19)], fill=B_D); d.line([P(22, 18), P(22, 20)], fill=B_D)                    # kidukset
    # levähiukset päälaella + etusuortuvat
    d.chord([*P(16, 5), *P(30, 15)], 180, 360, fill=HAIR)
    for k in range(5):
        x0 = 18 + k * 3; d.line([P(x0, 7), P(x0 - 2, 14 + (k % 2) * 3)], fill=HAIR_L if k % 2 else HAIR)
    d.line([P(17, 9), P(16, 26), P(18, 30)], fill=HAIR, width=2)
    # etukäsi: evä kyynärvarressa + kynnet
    d.line([P(28, 23), (fa[0] + ox, fa[1] + oy)], fill=B, width=4)
    mx, my = (28 + fa[0]) // 2 + ox, (23 + fa[1]) // 2 + oy
    d.polygon([(mx - 3, my + 1), (mx - 7, my + 6), (mx + 2, my + 2)], fill=FIN); d.line([(mx - 7, my + 6), (mx - 2, my + 2)], fill=FIN_L)
    d.ellipse([fa[0] + ox - 2, fa[1] + oy - 3, fa[0] + ox + 2, fa[1] + oy + 3], fill=B_L)
    claws(d, fa[0] + ox + 2, fa[1] + oy)
    return im

def ring(rx, ry=4, cx=24, cy=YW + 1, splash=0, f=0):
    """Palauttaa (taka, etu) -tasot: vesirengas jonka takakaari creaturen takana ja etukaari edessä."""
    back, db = canvas(); front, df = canvas()
    if rx <= 0: return back, front
    db.ellipse([cx - rx - 3, cy - ry - 1, cx + rx + 3, cy + ry + 1], outline=(200, 230, 255, 90))         # ulompi väre
    db.ellipse([cx - rx + 1, cy - ry + 1, cx + rx - 1, cy + ry - 1], fill=(8, 28, 44, 90))                # tumma kuoppa
    db.arc([cx - rx, cy - ry, cx + rx, cy + ry], 180, 360, fill=FOAM_B)
    df.arc([cx - rx, cy - ry, cx + rx, cy + ry], 0, 180, fill=FOAM); df.arc([cx - rx, cy - ry + 1, cx + rx, cy + ry + 1], 20, 160, fill=FOAM_B)
    rr = random.Random(f * 7 + rx)
    for _ in range(3 + splash * 3):
        a = rr.uniform(math.pi * 1.05, math.pi * 1.95); dist = rx + rr.randrange(0, 3)
        x = cx + int(math.cos(a) * dist); y = cy + int(math.sin(a) * ry) - rr.randrange(1, 2 + splash * 4)
        df.point((x, y), fill=FOAM); 
        if splash: df.point((x, y + 1), fill=FOAM_B)
    return back, front

def swirl(d, cx, cy, rx, ry, f):
    for k in range(3):
        a0 = f * 60 + k * 120
        d.arc([cx - rx + k * 2, cy - ry + k, cx + rx - k * 2, cy + ry - k], a0, a0 + 150, fill=(14, 40, 66, 200) if k < 2 else (160, 210, 240, 200))

def hiisi(oy=0, ox=0, rx=17, splash=0, f=0, vortex=False, **kw):
    full = hiisi_layer(ox, oy, **kw) if oy < 40 else canvas()[0]
    above = full.copy(); sub = canvas()[0]; pa, ps, pf = above.load(), sub.load(), full.load()
    for y in range(YW, F):
        for x in range(F):
            if pf[x, y][3]:
                pa[x, y] = CLEAR; a = 150 - (y - YW) * 28
                if a > 0: ps[x, y] = SUB + (a,)
    outline(above)
    out = canvas()[0]; back, front = ring(rx, splash=splash, f=f)
    out.alpha_composite(back)
    if vortex: swirl(ImageDraw.Draw(out), 24, YW + 1, max(4, rx - 2), 3, f)
    out.alpha_composite(sub); out.alpha_composite(above)
    if oy < 30:   # silmien hehku
        def glow(l):
            for ex in (26, 30): l.ellipse([ex + ox - 2, 11 + oy, ex + ox + 3, 15 + oy], fill=(255, 226, 58, 60))
        layer(out, glow)
    out.alpha_composite(front)
    return out

RISE = [dict(oy=48, rx=8, vortex=True), dict(oy=26, rx=11, vortex=True), dict(oy=17, rx=14, vortex=True),
        dict(oy=10, rx=16), dict(oy=4, rx=17), dict(oy=0, rx=17)]
def hiisi_nousu(i): return hiisi(f=i, **RISE[i])
def hiisi_sukellus(i):
    p = dict(RISE[5 - i]); p['splash'] = 1 if i < 5 else 2; p['vortex'] = i >= 3
    if i == 5: p['rx'] = 14
    return hiisi(f=i + 10, **p)
HATT = [dict(ox=-2, oy=1, fa=(33, 12), ba=(12, 14), mouth=2),
        dict(ox=1, oy=0, fa=(40, 24), ba=(14, 18), mouth=3),
        dict(ox=2, oy=0, fa=(42, 27), ba=(34, 31), mouth=3, splash=2),
        dict(ox=1, oy=1, fa=(38, 30), ba=(10, 31), mouth=1, splash=1)]
def hiisi_hyokkays(i):
    p = dict(HATT[i]); im = hiisi(f=i + 20, **p)
    if i == 2:
        layer(im, lambda l: [l.arc([28, 10 + k * 4, 50, 34 + k * 4], 290, 350, fill=(255, 255, 255, 190)) for k in range(3)])
    return im

# ---------------- vesiefektit 32x32 ----------------
def bubble(d, x, y, r):
    if r <= 1: d.point((x, y), fill=FOAM); d.point((x + 1, y), fill=FOAM_B); return
    d.ellipse([x - r, y - r, x + r, y + r], outline=FOAM_B); d.point((x - 1, y - 1), fill=FOAM)
def kuplat(i):
    im, d = canvas(32, 32)
    layer(im, lambda l: l.ellipse([5, 11, 27, 25], fill=(8, 26, 44, 110)))
    swirl(d, 16, 18, 10, 5, i)
    for (x, y0, r, sp) in ((12, 20, 2, 4), (19, 17, 1, 3), (16, 22, 1, 5), (22, 21, 2, 3), (9, 18, 1, 4)):
        y = y0 - (i * sp) % 14; bubble(d, x + (i % 2), y, r)
    return im
def loiske(i):
    im, d = canvas(32, 32); cx, cy = 16, 24
    rx = [6, 9, 12, 14][i]
    d.arc([cx - rx, cy - 3, cx + rx, cy + 3], 0, 360, fill=FOAM if i < 3 else FOAM_B)
    if i == 0: d.polygon([(12, 24), (14, 17), (16, 21), (18, 16), (20, 24)], fill=FOAM_B); d.line([(14, 18), (16, 22)], fill=FOAM)
    if i == 1:
        d.polygon([(13, 24), (15, 8), (17, 6), (19, 24)], fill=FOAM_B); d.line([(16, 7), (16, 22)], fill=FOAM)
        for (x, y) in ((10, 12), (22, 10), (8, 18), (24, 16)): d.point([(x, y), (x, y + 1)], fill=FOAM)
    if i == 2:
        d.polygon([(14, 24), (16, 15), (18, 24)], fill=FOAM_B)
        for (x, y) in ((7, 16), (25, 14), (5, 21), (27, 20), (12, 9), (21, 8)): d.point([(x, y), (x, y + 1)], fill=FOAM)
    if i == 3:
        for (x, y) in ((4, 23), (28, 22), (10, 21), (23, 21)): d.point((x, y), fill=FOAM)
    return im

# ---------------- ikonit ----------------
def ik_peikot():
    im, d = canvas(32, 32)
    for (x, y) in ((3, 8), (26, 5)): d.polygon([(x, y), (x - 4, y + 12), (x + 4, y + 12)], fill=hx('#1d3b1a'))   # kuuset
    back = peikko(**WALK[0]).crop((14, 6, 46, 38)); px = back.load()
    for y in range(32):
        for x in range(32):
            if px[x, y][3] == 255 and px[x, y][:3] != OUT[:3]: px[x, y] = shade(px[x, y], .55)
    im.alpha_composite(back, (-8, -3))
    im.alpha_composite(peikko(**WALK[0]).crop((14, 6, 46, 38)), (2, 2))
    return im
def ik_vesihiisi():
    im = hiisi(oy=8, rx=15).crop((8, 10, 40, 42)); return im
def ui_crop(src, box):
    c = src.crop(box); out = Image.new('RGBA', (24, 24), CLEAR); out.alpha_composite(c, (0, 0)); return out

# =====================================================================
def main():
    made = []
    def save(im, rel): im.save(f'{D}/{rel}'); made.append(rel)
    walk = [peikko(**p) for p in WALK]
    save(walk[0], 'olennot/peikko.png'); save(strip(walk), 'olennot/peikko_kavely.png')
    save(strip([peikko_hyokkays(i) for i in range(4)]), 'olennot/peikko_hyokkays.png')
    save(peikko_kaatunut(), 'olennot/peikko_kaatunut.png')
    save(strip([peikko_karjuu(i) for i in range(2)]), 'olennot/peikko_karjuu.png')
    save(kivi8(), 'efektit/kivi_8.png')
    nousu = [hiisi_nousu(i) for i in range(6)]
    save(nousu[5], 'olennot/vesihiisi.png'); save(strip(nousu), 'olennot/vesihiisi_nousu.png')
    save(strip([hiisi_hyokkays(i) for i in range(4)]), 'olennot/vesihiisi_hyokkays.png')
    save(strip([hiisi_sukellus(i) for i in range(6)]), 'olennot/vesihiisi_sukellus.png')
    save(strip([kuplat(i) for i in range(4)]), 'efektit/kuplat_32.png')
    save(strip([loiske(i) for i in range(4)]), 'efektit/loiske_32.png')
    save(ik_peikot(), 'ikonit/tapahtuma_peikot.png'); save(ik_vesihiisi(), 'ikonit/tapahtuma_vesihiisi.png')
    save(ui_crop(walk[0], (22, 6, 46, 30)), 'ikonit/ui_peikko.png')
    save(ui_crop(hiisi(oy=6, rx=0), (14, 4, 38, 28)), 'ikonit/ui_vesihiisi.png')
    preview(); print(len(made), 'tiedostoa'); return made

# ---------------- esikatselu 3x NEAREST ----------------
S = 3
def tiled(tile, w, h):
    t = Image.open(f'{D}/maasto/{tile}').convert('RGBA'); out = Image.new('RGBA', (w, h))
    for y in range(0, h, 32):
        for x in range(0, w, 32): out.paste(t, (x, y))
    return out
def preview():
    from PIL import ImageFont
    fnt = ImageFont.load_default(); BG = hx('#22252a')
    jermu = Image.open(f'{D}/yksikot/lahiojermu_sininen.png').convert('RGBA')
    rows = [('metsa', ['olennot/peikko.png', 'olennot/peikko_kavely.png', 'JERMU']),
            ('metsa', ['olennot/peikko_hyokkays.png', 'efektit/kivi_8.png']),
            ('metsa', ['olennot/peikko_karjuu.png', 'olennot/peikko_kaatunut.png']),
            ('vesi', ['olennot/vesihiisi.png', 'olennot/vesihiisi_nousu.png', 'JERMU']),
            ('vesi', ['olennot/vesihiisi_hyokkays.png']),
            ('vesi', ['olennot/vesihiisi_sukellus.png']),
            ('vesi', ['efektit/kuplat_32.png', 'efektit/loiske_32.png']),
            (None, ['ikonit/tapahtuma_peikot.png', 'ikonit/tapahtuma_vesihiisi.png', 'ikonit/ui_peikko.png', 'ikonit/ui_vesihiisi.png'])]
    def img(p): return jermu if p == 'JERMU' else Image.open(f'{D}/{p}').convert('RGBA')
    W = max(sum(img(p).size[0] + 4 for p in r) for _, r in rows) * S + 20
    H = sum(48 * S + 10 for _ in rows) + 10
    pv = Image.new('RGBA', (W, H), BG); y = 10
    for bg, r in rows:
        x = 10
        for p in r:
            im = img(p); w, h = im.size; hh = 48 if h < 48 and bg else h
            base = tiled('01_metsa.png' if bg == 'metsa' else '02_vesi.png', w, hh) if bg else Image.new('RGBA', (w, h), hx('#2e3238'))
            base.alpha_composite(im, (0, hh - h - (5 if h < 48 and bg and h > 8 else 0)) if bg else (0, 0))
            pv.alpha_composite(base.resize((w * S, base.size[1] * S), Image.NEAREST), (x, y)); x += (w + 4) * S
        y += 48 * S + 10
    pv.save(f'{D}/esikatselu_olennot.png')

if __name__ == '__main__':
    main()
