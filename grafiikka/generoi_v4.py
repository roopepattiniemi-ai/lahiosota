# Lähiösota: Etelä-Tampere – grafiikka V4 (Grafiikkabotti): hemuli, vänä, pullomummo, rakennukset, lumi, poliisipiiritys
# Ajo: python3 generoi_v4.py  (kirjoittaa vain V4-tiedostot + esikatselu_v4.png)
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from generoi import hx, shade, outline, shadow, SHADOW, OUT, D, building
from generoi_v2 import canvas, strip, layer, text, YEL, WHITE

for s in ('olennot', 'efektit', 'rakennukset', 'ikonit'): os.makedirs(f'{D}/{s}', exist_ok=True)
CLEAR = (0, 0, 0, 0)
WALK = [0, 2, 0, -2]; BOB = [0, 1, 0, 1]
SMOKE = (210, 210, 215, 150)
CAN = hx('#c8ced6'); CAN_B = hx('#2f6fb0'); CAN_R = hx('#c03a2a')

def smoke(im, pts):
    return layer(im, lambda l: [l.ellipse([x - r, y - r, x + r, y + r], fill=SMOKE) for (x, y, r) in pts])

# ---------------- HEMULI 32x32 ----------------
HS = hx('#d9cfc6'); HS_D = hx('#a89a90'); DRESS = hx('#7a9a4a'); DRESS_D = hx('#56702f'); DRESS_P = hx('#e8d27a')
HAT = hx('#d8b860'); HAT_D = hx('#a88a3a'); FLOWER = hx('#e0405a')
def hemuli(f=0, mode='kavely'):
    im, d = canvas(); w = WALK[f] if mode == 'kavely' else 0; b = BOB[f] if mode == 'kavely' else 0
    shadow(d, 15, 28, 8, 2)
    d.rectangle([12, 24, 13, 27 - w // 2], fill=HS_D); d.rectangle([17, 24, 18, 27 + w // 2], fill=HS_D)
    d.rectangle([11, 27 - w // 2, 14, 28 - w // 2], fill=HS_D); d.rectangle([16, 27 + w // 2, 19, 28 + w // 2], fill=HS_D)
    eat = mode == 'syo'
    d.polygon([(10, 25), (21, 25), (18, 13 + b), (13, 13 + b)], fill=DRESS); d.line([(10, 25), (21, 25)], fill=DRESS_D)
    for (x, y) in ((13, 22), (17, 20), (15, 17), (19, 23)): d.point((x, y + b), fill=DRESS_P)
    if eat:   # kumartuu, kuono maahan, kasvi
        k = f; d.line([(27, 28), (27, 24 + k * 2)], fill=hx('#3a8a2a')); d.point([(26, 25 + k * 2), (28, 26 + k * 2)], fill=hx('#5ab83a'))
        if k == 0: d.point((27, 23), fill=hx('#f0e040'))
        d.ellipse([16, 12, 23, 19], fill=HS); d.polygon([(21, 14), (27, 22), (25, 24), (20, 18)], fill=HS)
        d.point((20, 14), fill=OUT); d.rectangle([14, 9, 23, 12], fill=HAT); d.line([(14, 12), (23, 12)], fill=HAT_D); d.point((18, 9), fill=FLOWER)
        d.line([(17, 16), (21, 19)], fill=HS)
        return outline(im)
    d.line([(14, 16 + b), (11, 21 + b)], fill=HS); d.line([(18, 16 + b), (21, 20 + b)], fill=HS)
    d.ellipse([12, 6 + b, 19, 14 + b], fill=HS); d.polygon([(17, 8 + b), (25, 9 + b), (25, 12 + b), (17, 13 + b)], fill=HS)
    d.ellipse([23, 8 + b, 26, 12 + b], fill=HS_D); d.point((18, 9 + b), fill=OUT); d.line([(19, 12 + b), (23, 12 + b)], fill=HS_D)
    d.rectangle([10, 5 + b, 21, 6 + b], fill=HAT_D); d.rectangle([12, 2 + b, 19, 5 + b], fill=HAT); d.line([(12, 5 + b), (19, 5 + b)], fill=hx('#7a4ab0'))
    d.point([(14, 3 + b), (15, 2 + b), (16, 3 + b)], fill=FLOWER); d.point((15, 3 + b), fill=YEL)
    d.line([(24, 12 + b), (27, 13 + b)], fill=WHITE); d.point((28, 13 + b), fill=hx('#ff7a1a'))   # tupakka
    outline(im)
    return smoke(im, [(29, 10 + b - f % 2, 1), (28 + f % 2, 6 + b, 1), (30, 3 + b - f % 2, 1)])

# ---------------- CAESAR 48x48 ----------------
TOGA = hx('#f0ece0'); TOGA_D = hx('#c8c0aa'); PURP = hx('#7a2a6a'); LAUR = hx('#7ab83a'); GOLD = hx('#ffd23a')
def caesar(f=0, mode='kavely'):
    im, d = canvas(48, 48); w = WALK[f] if mode == 'kavely' else 0; b = BOB[f] if mode == 'kavely' else 0
    d.ellipse([10, 40, 36, 45], fill=SHADOW)
    d.rectangle([17, 36, 19, 42 - w], fill=HS_D); d.rectangle([24, 36, 26, 42 + w], fill=HS_D)
    d.rectangle([16, 41 - w, 20, 42 - w], fill=hx('#8a5a2a')); d.rectangle([23, 41 + w, 27, 42 + w], fill=hx('#8a5a2a'))
    d.polygon([(13, 37), (31, 37), (28, 18 + b), (16, 18 + b)], fill=TOGA); d.line([(13, 37), (31, 37)], fill=TOGA_D)
    d.line([(16, 19 + b), (29, 36)], fill=PURP, width=2); d.line([(18, 24 + b), (17, 35)], fill=TOGA_D)
    # käsi: hyökkäyksessä nousee
    arm = {0: (31, 26), 1: (33, 14), 2: (38, 20), 3: (33, 28)}[f] if mode == 'hyokkays' else (30, 30)
    d.line([(26, 21 + b), (arm[0], arm[1] + b)], fill=HS, width=3)
    d.ellipse([16, 7 + b, 27, 19 + b], fill=HS); d.polygon([(24, 10 + b), (37, 12 + b), (37, 16 + b), (24, 18 + b)], fill=HS)
    d.ellipse([34, 11 + b, 39, 16 + b], fill=HS_D); d.point([(25, 12 + b), (26, 12 + b)], fill=OUT); d.line([(27, 17 + b), (34, 16 + b)], fill=HS_D)
    for i, x in enumerate(range(15, 29, 2)): d.ellipse([x, 6 + b + (i % 2), x + 2, 8 + b + (i % 2)], fill=LAUR)   # seppele
    d.point([(16, 7 + b), (22, 6 + b), (27, 7 + b)], fill=GOLD)
    d.line([(37, 16 + b), (41, 17 + b)], fill=WHITE); d.point((42, 17 + b), fill=hx('#ff7a1a'))
    outline(im)
    g = Image.new('RGBA', im.size, CLEAR); gd = ImageDraw.Draw(g)       # hehku figuurin taakse (ei ääriviivaa)
    gd.ellipse([9, 3, 39, 41], fill=(255, 220, 90, 45)); gd.ellipse([13, 6, 35, 38], fill=(255, 235, 130, 60))
    g.alpha_composite(im); im = g
    if mode == 'hyokkays':
        def zap(l):
            if f == 1: l.ellipse([30, 9, 37, 16], fill=(255, 240, 140, 200))
            if f == 2:
                l.line([(39, 19), (43, 16), (41, 21), (47, 18)], fill=(255, 235, 90, 255), width=2); l.ellipse([36, 16, 42, 23], fill=(255, 250, 200, 220))
            if f == 3: l.line([(40, 24), (47, 22)], fill=(255, 230, 120, 120))
        layer(im, zap)
    return smoke(im, [(44, 13 + b - f % 2, 1), (43 + f % 2, 9 + b, 2), (45, 4 + b, 1)])

# ---------------- VÄNÄ 32x32 ----------------
VERK = hx('#3a3a48'); VERK_L = hx('#f0f0f0'); PIPO = hx('#c86a1a'); SKIN = hx('#e0b08a'); SKIN_D = hx('#b88663')
def vana(f=0, mode='kavely'):
    im, d = canvas(); sway = [0, 2, 0, -1][f] if mode == 'kavely' else 0; w = WALK[f] if mode == 'kavely' else 0
    shadow(d, 16, 28, 7, 2)
    kick = mode == 'potku'
    if kick:   # takajalka tukena, etujalka potkaisee
        d.rectangle([13, 20, 15, 27], fill=VERK); d.rectangle([13, 27, 15, 28], fill=hx('#e8e8e8'))
        leg = {0: (11, 26), 1: (14, 27), 2: (23, 22), 3: (21, 25)}[f]
        d.line([(17, 20), leg], fill=VERK, width=3); d.rectangle([leg[0] - 1, leg[1], leg[0] + 2, leg[1] + 1], fill=hx('#e8e8e8'))
        if f in (0, 1): d.ellipse([20, 24, 24, 28], fill=WHITE); d.point([(22, 26)], fill=OUT)
    else:
        d.rectangle([13, 20, 15, 27 - w], fill=VERK); d.rectangle([17, 20, 19, 27 + w], fill=VERK)
        d.line([(13, 21), (13, 26 - w)], fill=VERK_L); d.line([(17, 21), (17, 26 + w)], fill=VERK_L)
        d.rectangle([13, 27 - w, 15, 28 - w], fill=hx('#e8e8e8')); d.rectangle([17, 27 + w, 20, 28 + w], fill=hx('#e8e8e8'))
    x = 12 + sway // 2
    d.rectangle([x, 12, x + 8, 20], fill=VERK); d.line([(x, 12), (x, 20)], fill=VERK_L); d.line([(x + 8, 12), (x + 8, 20)], fill=VERK_L)
    d.rectangle([x + 9, 14, x + 10, 17], fill=SKIN); d.rectangle([x + 10, 13, x + 12, 16], fill=CAN); d.line([(x + 10, 14), (x + 12, 14)], fill=hx('#3a8a3a'))
    hx_ = x + sway // 2 + 1
    d.rectangle([hx_ + 1, 6, hx_ + 6, 11], fill=SKIN); d.point((hx_ + 5, 8), fill=OUT); d.point((hx_ + 6, 10), fill=hx('#d86a6a'))
    d.line([(hx_ + 1, 11), (hx_ + 6, 11)], fill=SKIN_D); d.point((hx_ + 6, 9), fill=hx('#e07a6a'))  # punainen nenä
    d.rectangle([hx_, 3, hx_ + 6, 6], fill=PIPO); d.point((hx_ + 2, 2), fill=WHITE); d.line([(hx_, 6), (hx_ + 6, 6)], fill=shade(PIPO, .7))
    outline(im)
    if mode == 'kavely' and f in (1, 3): ImageDraw.Draw(im).point([(hx_ + 9, 4), (hx_ + 10, 3)], fill=(255, 240, 160, 200))   # hik
    return im
def jalkapallo():
    im, d = canvas(8, 8); d.ellipse([1, 1, 6, 6], fill=WHITE); d.point([(3, 3), (4, 4), (2, 5), (5, 2)], fill=hx('#2a2a2a')); return outline(im)

# ---------------- PULLOMUMMO 32x32 ----------------
HUIVI = hx('#a04a3a'); COAT = hx('#6a5a3a'); COAT_D = hx('#4a3e28')
def pullomummo(f=0):
    im, d = canvas(); w = WALK[f]; b = BOB[f]
    shadow(d, 17, 28, 11, 2)
    d.rectangle([9, 21, 10, 27 - w], fill=hx('#4a4a50')); d.rectangle([12, 21, 13, 27 + w], fill=hx('#4a4a50'))
    d.rectangle([8, 27 - w, 10, 28 - w], fill=hx('#2a2a2a')); d.rectangle([12, 27 + w, 14, 28 + w], fill=hx('#2a2a2a'))
    d.polygon([(7, 22), (15, 22), (14, 12 + b), (8, 12 + b)], fill=COAT); d.line([(8, 12 + b), (8, 22)], fill=COAT_D)
    d.ellipse([8, 6 + b, 14, 12 + b], fill=SKIN); d.point((13, 8 + b), fill=OUT)
    d.chord([7, 4 + b, 15, 11 + b], 180, 360, fill=HUIVI); d.polygon([(7, 8 + b), (9, 8 + b), (8, 13 + b)], fill=HUIVI); d.point((10, 5 + b), fill=hx('#e8c040'))
    # kärry
    cx = 17
    for wx in (cx + 2, cx + 10): d.ellipse([wx - 1, 26, wx + 1, 28], fill=hx('#1c1c1c'))
    d.rectangle([cx, 15, cx + 13, 25], fill=hx('#8a8e92')); d.rectangle([cx + 1, 16, cx + 12, 24], fill=hx('#5a5e62'))
    for i in range(4): d.line([(cx + 3 + i * 3, 16), (cx + 3 + i * 3, 24)], fill=hx('#8a8e92'))
    r = random.Random(4)
    for (x, y) in ((1, 10), (4, 9), (7, 11), (10, 9), (2, 13), (6, 13), (9, 12)):
        c = r.choice([CAN_B, CAN_R, hx('#3a8a3a')]); d.rectangle([cx + x, y + b // 2, cx + x + 2, y + 4 + b // 2], fill=CAN); d.point((cx + x + 1, y + 2 + b // 2), fill=c)
    d.line([(14, 16 + b), (cx, 15)], fill=SKIN); d.line([(cx - 1, 14), (cx, 15)], fill=hx('#2a2a2a'))
    return outline(im)

# ---------------- RAKENNUKSET 64x64 ----------------
def sauna():
    im, d, x0, yr, yw, w, h = building(hx('#8a5a30'), hx('#3e3a36'), h=20, w=46, depth=22)
    for y in range(yw + 2, yw + h, 3): d.line([(x0, y), (x0 + w - 1, y)], fill=hx('#6a4220'))
    d.rectangle([x0 + 8, yw + 7, x0 + 15, yw + h - 1], fill=hx('#3a2414')); d.point((x0 + 14, yw + 13), fill=hx('#d8b04a'))
    d.rectangle([x0 + 24, yw + 6, x0 + 31, yw + 11], fill=hx('#e8b44a')); d.line([(x0 + 27, yw + 6), (x0 + 27, yw + 11)], fill=hx('#5a3520'))
    d.rectangle([x0 + 34, yr + 2, x0 + 39, yr + 12], fill=hx('#7a7672')); d.rectangle([x0 + 33, yr + 1, x0 + 40, yr + 2], fill=hx('#4a4642'))
    for i in range(4): d.rectangle([x0 + w - 8 + i * 2, yw + h - 3, x0 + w - 7 + i * 2, yw + h], fill=hx('#b07a44'))   # puupino
    outline(im)
    return smoke(im, [(x0 + 37, yr - 2, 3), (x0 + 40, yr - 7, 3), (x0 + 36, yr - 12, 2), (x0 + 41, 2, 2)])
def pihagrilli():
    im, d = canvas(64, 64)
    d.rectangle([6, 52, 60, 58], fill=SHADOW)
    d.rectangle([4, 14, 59, 26], fill=hx('#5a3a2a')); d.rectangle([4, 14, 59, 26], outline=hx('#7a5a3a'))
    for x in range(6, 58, 4): d.line([(x, 15), (x, 25)], fill=hx('#4a2e20'))
    for x in (6, 56): d.rectangle([x, 27, x + 2, 54], fill=hx('#6b4a2b'))
    for (y, x1) in ((44, 8), (50, 34)):   # penkit + pöytä
        d.rectangle([x1, y, x1 + 20, y + 2], fill=hx('#b07a44')); d.rectangle([x1, y + 3, x1 + 20, y + 3], fill=hx('#7a5030'))
        d.point([(x1 + 1, y + 5), (x1 + 19, y + 5)], fill=hx('#5a3a20'))
    d.rectangle([24, 34, 38, 42], fill=hx('#2a2a2a')); d.ellipse([24, 32, 38, 37], fill=hx('#4a4a4a'))
    d.line([(26, 34), (36, 34)], fill=hx('#ff7a1a')); d.rectangle([29, 33, 32, 34], fill=hx('#a03a20')); d.line([(27, 42), (25, 47)], fill=hx('#2a2a2a')); d.line([(35, 42), (37, 47)], fill=hx('#2a2a2a'))
    d.rectangle([12, 40, 15, 43], fill=CAN); d.rectangle([12, 41, 15, 42], fill=CAN_B)
    outline(im)
    return smoke(im, [(31, 29, 3), (34, 22, 3), (30, 15, 2), (35, 8, 2)])
def kirpputori():
    im, d = canvas(64, 64)
    d.rectangle([6, 54, 60, 59], fill=SHADOW)
    d.polygon([(4, 8), (60, 8), (58, 22), (6, 22)], fill=hx('#2a7ac0'))
    for x in range(6, 58, 8): d.polygon([(x, 8), (x + 4, 8), (x + 4, 22), (x, 22)], fill=hx('#e8ecee'))
    for x in (7, 56): d.rectangle([x, 23, x + 1, 55], fill=hx('#8a8e92'))
    r = random.Random(11)
    for (tx, ty) in ((6, 34), (34, 34), (18, 48)):
        d.rectangle([tx, ty, tx + 22, ty + 5], fill=hx('#d8c8a8')); d.line([(tx, ty + 5), (tx + 22, ty + 5)], fill=hx('#a89878'))
        d.line([(tx + 1, ty + 6), (tx + 1, ty + 9)], fill=hx('#6a6a6a')); d.line([(tx + 21, ty + 6), (tx + 21, ty + 9)], fill=hx('#6a6a6a'))
        for i in range(5):
            x = tx + 1 + i * 4; c = r.choice([hx('#d8262b'), hx('#f0d020'), hx('#3aa03a'), hx('#8a5ac0'), hx('#e8e8e8'), hx('#6a4a2b')])
            d.rectangle([x, ty - r.randrange(2, 6), x + 2, ty], fill=c)
    d.rectangle([44, 44, 52, 52], fill=hx('#b08a5a')); d.line([(44, 46), (52, 46)], fill=hx('#7a5a30'))      # pahvilaatikko
    d.rectangle([47, 41, 49, 44], fill=CAN); d.rectangle([20, 26, 30, 31], fill=WHITE); text(d, 21, 26, '€', hx('#d8262b'))
    return outline(im)

# ---------------- LUMI + POLIISIPIIRITYS ----------------
def lumi():
    im, d = canvas(64, 64); r = random.Random(64)
    for _ in range(70):
        x, y = r.randrange(64), r.randrange(64); big = r.random() < .3
        for k in range(3 if big else 2):
            d.point(((x + k) % 64, (y + k) % 64), fill=(250, 252, 255, 230))
        if r.random() < .4: d.point(((x - 1) % 64, (y - 1) % 64), fill=(220, 230, 245, 120))
    return im
def ik_lumimyrsky():
    im, d = canvas()
    for (cx, cy, r_) in [(10, 11, 6), (18, 8, 8), (25, 12, 5)]: d.ellipse([cx - r_, cy - r_, cx + r_, cy + r_], fill=hx('#9aa6b8'))
    d.rectangle([5, 12, 29, 17], fill=hx('#9aa6b8')); d.line([(6, 17), (28, 17)], fill=hx('#6a7688'))
    for (x, y) in ((8, 22), (16, 25), (24, 21), (12, 28), (22, 28)):
        d.point([(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=WHITE)
    outline(im); d = ImageDraw.Draw(im)
    for (y, x0, x1) in ((20, 1, 6), (25, 26, 31), (29, 1, 8)): d.line([(x0, y), (x1, y)], fill=hx('#cfe0f0'))
    return im
def minicar(d, x, y, f, flip=False):
    d.rectangle([x, y, x + 17, y + 8], fill=hx('#f0f0f0')); d.rectangle([x, y + 5, x + 17, y + 6], fill=hx('#1f4fb0'))
    d.rectangle([x + 4, y + 1, x + 13, y + 4], fill=hx('#2a3a4a'))
    for wx in (x + 3, x + 14): d.rectangle([wx - 1, y + 8, wx + 1, y + 9], fill=hx('#1c1c1c'))
    a, b = (hx('#3a80ff'), hx('#ff3a3a')) if f % 2 == 0 else (hx('#ff3a3a'), hx('#3a80ff'))
    d.rectangle([x + 6, y - 1, x + 8, y], fill=a); d.rectangle([x + 9, y - 1, x + 11, y], fill=b)
def piiritys(f):
    im, d = canvas(64, 64)
    for (x, y) in ((2, 52), (44, 4)): minicar(d, x, y, f)
    outline(im); d = ImageDraw.Draw(im)
    for i in range(0, 60, 4):   # eristysnauha alareunassa ja sivuilla
        c = hx('#f0d020') if (i // 4) % 2 == 0 else hx('#1a1a1a')
        d.line([(22 + i // 2, 60), (24 + i // 2, 60)], fill=c); d.line([(62, 18 + i // 1.5), (62, 20 + i // 1.5)], fill=c)
        d.line([(1, 8 + i * 0.7), (1, 10 + i * 0.7)], fill=c)
    def glow(l):
        for (x, y) in ((10, 51), (52, 3)):
            col = (60, 120, 255, 90) if f % 2 == 0 else (255, 60, 60, 90); r_ = 6 + (f // 2) * 3
            l.ellipse([x - r_, y - r_, x + r_, y + r_], fill=col)
    return layer(im, glow)

# =====================================================================
def main():
    made = []
    def save(im, rel): im.save(f'{D}/{rel}'); made.append(rel)
    hw = [hemuli(f) for f in range(4)]; save(hw[0], 'olennot/hemuli.png'); save(strip(hw), 'olennot/hemuli_kavely.png')
    save(strip([hemuli(f, 'syo') for f in range(2)]), 'olennot/hemuli_syo.png')
    cw = [caesar(f) for f in range(4)]; save(cw[0], 'olennot/hemuli_caesar.png'); save(strip(cw), 'olennot/hemuli_caesar_kavely.png')
    save(strip([caesar(f, 'hyokkays') for f in range(4)]), 'olennot/hemuli_caesar_hyokkays.png')
    vw = [vana(f) for f in range(4)]; save(vw[0], 'olennot/vana.png'); save(strip(vw), 'olennot/vana_kavely.png')
    save(strip([vana(f, 'potku') for f in range(4)]), 'olennot/vana_potku.png'); save(jalkapallo(), 'efektit/jalkapallo_8.png')
    pw = [pullomummo(f) for f in range(4)]; save(pw[0], 'olennot/pullomummo.png'); save(strip(pw), 'olennot/pullomummo_kavely.png')
    save(sauna(), 'rakennukset/sauna.png'); save(pihagrilli(), 'rakennukset/pihagrilli.png'); save(kirpputori(), 'rakennukset/kirpputori.png')
    save(lumi(), 'efektit/lumi_64.png'); save(ik_lumimyrsky(), 'ikonit/tapahtuma_lumimyrsky.png')
    save(strip([piiritys(f) for f in range(4)]), 'efektit/poliisipiiritys_64.png')
    preview(made); print(len(made), 'tiedostoa')

def preview(files):
    S = 3; BG = hx('#22252a'); CELL = hx('#2e3238')
    rows = [files[0:3], files[3:6], files[6:10], files[10:12], files[12:15], files[15:18]]
    def load(p):
        im = Image.open(f'{D}/{p}').convert('RGBA')
        if p == 'efektit/lumi_64.png':   # tiilitys 2x2 ruohon päällä
            g = Image.open(f'{D}/maasto/00_ruoho.png').convert('RGBA'); t = Image.new('RGBA', (128, 128))
            for y in range(0, 128, 32):
                for x in range(0, 128, 32): t.paste(g, (x, y))
            for y in (0, 64):
                for x in (0, 64): t.alpha_composite(im, (x, y))
            return t
        if p == 'efektit/poliisipiiritys_64.png':
            t = Image.new('RGBA', im.size)
            for i in range(4): t.alpha_composite(Image.open(f'{D}/rakennukset/paamaja_sininen.png').convert('RGBA'), (i * 64, 0))
            t.alpha_composite(im); return t
        return im
    imgs = [[load(p) for p in r] for r in rows]
    W = max(sum(i.size[0] * S + 10 for i in r) for r in imgs) + 20; H = sum(max(i.size[1] for i in r) * S + 10 for r in imgs) + 10
    pv = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(pv); y = 10
    for r in imgs:
        x = 10
        for im in r:
            b = im.resize((im.size[0] * S, im.size[1] * S), Image.NEAREST); d.rectangle([x, y, x + b.size[0] - 1, y + b.size[1] - 1], fill=CELL)
            pv.alpha_composite(b, (x, y)); x += b.size[0] + 10
        y += max(i.size[1] for i in r) * S + 10
    pv.save(f'{D}/esikatselu_v4.png')

if __name__ == '__main__':
    main()
