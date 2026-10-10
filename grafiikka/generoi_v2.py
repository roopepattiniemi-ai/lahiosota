# Lähiösota: Etelä-Tampere – grafiikka v2 (Grafiikkabotti)
# Uudet yksiköt, ajoneuvot, animaatiot, efektit, tapahtumat ja ikonit.
# Ajo: python3 generoi_v2.py   (ei koske v0.1/v0.2-tiedostoihin, paitsi lukee niitä vertailuun)
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import generoi as G
from generoi import hx, shade, outline, shadow, SHADOW, OUT, TEAMS, SKIN, SKIN_D, PANTS, BOOT, person, bag, building, windows, D

for sub in ('yksikot', 'ajoneuvot', 'efektit', 'rakennukset', 'ikonit'):
    os.makedirs(f'{D}/{sub}', exist_ok=True)

CLEAR = (0, 0, 0, 0)
GLASS = hx('#9fc6e0'); GLASS_L = hx('#d8ecf8')
GUN = hx('#2a2a2a'); GUN_L = hx('#4a4a4a'); WOOD = hx('#6b4a2b')
YEL = hx('#ffe14a'); WHITE = hx('#f4f4f0')

def canvas(w=32, h=32):
    im = Image.new('RGBA', (w, h), CLEAR); return im, ImageDraw.Draw(im)
def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h), CLEAR)
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s
def layer(im, fn):
    """Piirrä puoliläpinäkyvät jutut (savu, hehku) erilliselle tasolle ja komposiittaa (ei ääriviivaa)."""
    l = Image.new('RGBA', im.size, CLEAR); fn(ImageDraw.Draw(l)); im.alpha_composite(l); return im

# ---------- pikselifontti 3x5 ----------
FONT = {
 'A': ['010','101','111','101','101'], 'I': ['111','010','010','010','111'], 'N': ['101','111','111','111','101'],
 'V': ['101','101','101','101','010'], 'Z': ['111','001','010','100','111'], '3': ['111','001','011','001','111'],
 '%': ['101','001','010','100','101'], '-': ['000','000','111','000','000'], '!': ['010','010','010','000','010'],
 '?': ['111','001','011','000','010'], '€': ['011','100','111','100','011'],
}
def text(d, x, y, s, col, sc=1):
    for ch in s:
        g = FONT.get(ch)
        if g:
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '1': d.rectangle([x + i*sc, y + j*sc, x + i*sc + sc - 1, y + j*sc + sc - 1], fill=col)
        x += 4 * sc

def flash(d, x, y, big=False):
    """Suuliekki: keskipiste (x,y), osoittaa oikealle."""
    d.polygon([(x, y-2), (x+3 + big, y), (x, y+2), (x-1, y)], fill=hx('#ff9a1a'))
    d.line([(x, y), (x+2 + big, y)], fill=YEL); d.point((x, y), fill=WHITE)
    d.point([(x+1, y-2), (x+1, y+2)], fill=hx('#ffcf3a'))

def zzz(d, x, y):
    """Kolme kasvavaa Z-kirjainta, vasen alakulma (x,y)."""
    for (dx, dy, s) in ((0, 0, 3), (4, -3, 4), (9, -6, 5)):
        X, Y = x + dx, y + dy - s
        d.line([(X, Y), (X+s-1, Y)], fill=YEL); d.line([(X+s-1, Y), (X, Y+s-1)], fill=YEL); d.line([(X, Y+s-1), (X+s-1, Y+s-1)], fill=YEL)

def wheel(d, cx, cy, r, k, tire=hx('#1c1c1c'), rim=hx('#8a8e92')):
    """Pyörä jossa 2-puolainen vanne; k*45° kierto -> 4 kehyksen saumaton pyöriminen."""
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=tire)
    rr = max(1, r-2); d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=rim)
    a = math.radians(k * 45); dx = round(math.cos(a) * rr); dy = round(math.sin(a) * rr)
    d.line([(cx-dx, cy-dy), (cx+dx, cy+dy)], fill=hx('#3a3c40')); d.point((cx, cy), fill=hx('#d0d0d0'))

def no_shadow(im):
    px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            if px[x, y] == SHADOW: px[x, y] = CLEAR
    return im

WALK = [0, 2, 0, -2]     # jalkojen vaihe
BOB  = [0, 1, 0, 1]      # vartalon notkahdus askeleella

# =====================================================================
# VANHAT YKSIKÖT – samat piirtokutsut kuin generoi.py:ssä + kehysparametri
# (kehys 0 tarkistetaan pikselintarkasti nykyistä staattista vastaan)
# =====================================================================
def tolkkijussi(tc, f=0, mode='kavely'):
    im, d = canvas(); w, b = WALK[f], BOB[f]; sw = [0, 1, 0, -1][f]
    person(d, tc, top=6 + b, hat='pipo', walk=w); bag(d, 6, 18 + b + sw); bag(d, 21, 18 + b - sw)
    d.rectangle([11, 15 + b, 12, 19 + b], fill=SKIN); d.rectangle([20, 15 + b, 21, 19 + b], fill=SKIN)
    return outline(im)

def lahiojermu(tc, f=0, mode='kavely'):
    im, d = canvas()
    if mode == 'kavely':
        w, b = WALK[f], BOB[f]
        person(d, tc, top=6 + b, hat='kypara', walk=w)
        d.line([(8, 20+b), (24, 11+b)], fill=GUN, width=2); d.line([(22, 12+b), (27, 9+b)], fill=hx('#3a3a3a'))
        d.rectangle([7, 19+b, 10, 21+b], fill=WOOD); d.point((15, 17+b), fill=WOOD)
        d.rectangle([17, 14+b, 18, 18+b], fill=hx('#3a3a3a'))
        d.rectangle([11, 15+b, 12, 17+b], fill=SKIN); d.rectangle([19, 13+b, 20, 15+b], fill=SKIN)
        return outline(im)
    # ampuu: kivääri vaakatasossa olalla, f0 suuliekki, f1 rekyyli + hylsy
    r = -1 if f == 1 else 0
    person(d, tc, hat='kypara')
    d.rectangle([12+r, 13, 15+r, 15], fill=WOOD)                       # tukki
    d.rectangle([15+r, 13, 26+r, 14], fill=GUN); d.point((27+r, 13), fill=GUN)
    d.rectangle([19+r, 15, 20+r, 17], fill=hx('#3a3a3a')); d.point((24+r, 12), fill=GUN)
    d.rectangle([17+r, 15, 18+r, 16], fill=SKIN); d.rectangle([22+r, 15, 23+r, 16], fill=SKIN)
    outline(im)
    if f == 0: flash(d, 29, 13)
    else: d.point((20, 10), fill=hx('#d8b030')); layer(im, lambda l: l.point([(28, 12), (29, 11)], fill=(200, 200, 200, 150)))
    return im

def mopopoika(tc, f=0, mode='kavely'):
    im, d = canvas(); td = shade(tc, .65); tl = shade(tc, 1.3)
    b = -BOB[f] if mode == 'kavely' else 0   # runko pomppaa ylös
    shadow(d, 16, 28, 12, 2)
    for x in (7, 24):
        d.ellipse([x-4, 21, x+4, 29], fill=hx('#1c1c1c')); d.ellipse([x-1, 24, x+1, 26], fill=hx('#9a9a9a'))
        if mode == 'kavely' and f > 0:  # kehys 0 = alkuperäinen napa; muissa pinna kiertää
            a = math.radians(f * 45); dx, dy = round(math.cos(a)), round(math.sin(a))
            d.line([(x-dx, 25-dy), (x+dx, 25+dy)], fill=hx('#4a4a4a'))
    y = b
    d.polygon([(9, 22+y), (22, 22+y), (25, 18+y), (20, 17+y), (12, 19+y)], fill=tc); d.line([(9, 22+y), (22, 22+y)], fill=td)
    d.line([(12, 19+y), (20, 17+y)], fill=tl); d.rectangle([5, 18+y, 13, 20+y], fill=hx('#2a2a2a'))
    d.line([(24, 18+y), (25, 12+y)], fill=hx('#555555')); d.line([(23, 12+y), (27, 12+y)], fill=hx('#2a2a2a'))
    d.point((27, 15+y), fill=hx('#ffe680'))
    d.rectangle([10, 11+y, 15, 18+y], fill=hx('#3a3a40'))
    if mode == 'ampuu':  # Jatimatic eteenpäin ohjaustangon yli
        d.line([(15, 12), (21, 10)], fill=hx('#3a3a40'), width=2)
        d.rectangle([21, 9, 26, 10], fill=GUN); d.rectangle([22, 11, 23, 12], fill=GUN); d.point((21, 11), fill=SKIN)
    else:
        d.line([(15, 13+y), (23, 12+y)], fill=hx('#3a3a40'), width=2)
    d.rectangle([13, 18+y, 17, 21+y], fill=PANTS)
    d.ellipse([10, 4+y, 16, 10+y], fill=td); d.line([(11, 5+y), (14, 5+y)], fill=tl); d.rectangle([14, 7+y, 16, 9+y], fill=hx('#9fc6e0'))
    outline(im)
    if mode == 'kavely' and f in (1, 2):
        layer(im, lambda l: l.ellipse([0, 19 - f, 3, 22 - f], fill=(190, 190, 190, 120)))   # pakokaasu
    if mode == 'ampuu':
        if f == 0: flash(d, 28, 9)
        else: d.point((19, 7), fill=hx('#d8b030'))
    return im

# =====================================================================
# UUDET YKSIKÖT
# =====================================================================
def parvekeampuja(tc, f=0, mode='kavely'):
    """Kantaa omaa parvekkeenkaidetta kilpenä, pitkä kiikarikivääri kaiteen päällä."""
    im, d = canvas(); td = shade(tc, .65); tl = shade(tc, 1.3)
    w = WALK[f] if mode == 'kavely' else 0; b = BOB[f] if mode == 'kavely' else 0
    r = -1 if (mode == 'ampuu' and f == 1) else 0
    shadow(d, 15, 28, 11, 2)
    cx = 13
    d.rectangle([cx-3, 22, cx-1, 26-w], fill=PANTS); d.rectangle([cx+1, 22, cx+3, 26+w], fill=PANTS)
    d.rectangle([cx-3, 26-w, cx-1, 27-w], fill=BOOT); d.rectangle([cx+1, 26+w, cx+3, 27+w], fill=BOOT)
    y = b
    # huppari (huppu päässä)
    d.rectangle([cx-4, 10+y, cx+4, 20+y], fill=tc); d.line([(cx-4, 10+y), (cx-4, 20+y)], fill=tl)
    d.rectangle([cx-3, 4+y, cx+3, 10+y], fill=td); d.rectangle([cx-1, 6+y, cx+3, 10+y], fill=SKIN)
    d.point([(cx+1, 7+y)], fill=OUT); d.line([(cx-1, 10+y), (cx+3, 10+y)], fill=SKIN_D); d.line([(cx-3, 4+y), (cx+2, 4+y)], fill=tl)
    # kiikarikivääri kaiteen yläpuolella (piirretään kaiteen jälkeen)
    # kaide: ruskea profiilipelti, metallinen yläjohde, tiimivärinen pyyhe roikkuu
    d.rectangle([3, 15+y, 25, 23+y], fill=hx('#9a4e2a'))
    for x in range(4, 25, 2): d.line([(x, 16+y), (x, 23+y)], fill=hx('#7a3a1e'))
    d.line([(3, 23+y), (25, 23+y)], fill=hx('#5a2a14'))
    d.line([(2, 14+y), (26, 14+y)], fill=hx('#c8ccd0')); d.line([(2, 15+y), (26, 15+y)], fill=hx('#8a8e92'))
    d.rectangle([5, 14+y, 9, 20+y], fill=tl); d.line([(5, 18+y), (9, 18+y)], fill=WHITE); d.line([(9, 15+y), (9, 20+y)], fill=td)
    d.rectangle([cx-2+r, 10+y, cx+3+r, 12+y], fill=WOOD)
    d.rectangle([cx+3+r, 10+y, 27+r, 11+y], fill=GUN); d.point((28+r, 10+y), fill=GUN)
    d.rectangle([cx+6+r, 8+y, cx+11+r, 8+y], fill=hx('#1c1c1c')); d.point((cx+11+r, 8+y), fill=hx('#7fd0ff')); d.point((cx+8+r, 9+y), fill=hx('#1c1c1c'))
    d.line([(24+r, 12+y), (23+r, 13+y)], fill=GUN); d.line([(25+r, 12+y), (26+r, 13+y)], fill=GUN)   # kaksijalka kaiteella
    d.rectangle([cx+3, 12+y, cx+4, 13+y], fill=SKIN)
    outline(im)
    if mode == 'ampuu':
        if f == 0: flash(d, 30, 10 + y)
        else: layer(im, lambda l: l.ellipse([27, 6, 31, 10], fill=(210, 210, 210, 140)))
    return im

def mummo(tc, f=0, mode='kavely'):
    """Hunttu-mummo rollaattorin kanssa: valkoinen kampaus, silmälasit, pitkä tiimivärinen takki, käsilaukku."""
    im, d = canvas(); td = shade(tc, .65); tl = shade(tc, 1.3)
    mv = mode == 'kavely'; w = (1 if f == 1 else -1 if f == 3 else 0) if mv else 0; b = BOB[f] if mv else 0
    shadow(d, 17, 28, 12, 2)
    cx = 11; y = b
    # jalat (sukkahousut) ja kengät
    d.rectangle([cx-2, 23, cx-1, 26-w], fill=hx('#b89a80')); d.rectangle([cx+1, 23, cx+2, 26+w], fill=hx('#b89a80'))
    d.rectangle([cx-3, 26-w, cx-1, 27-w], fill=BOOT); d.rectangle([cx+1, 26+w, cx+3, 27+w], fill=BOOT)
    # takki (leveä helma, kumara)
    d.polygon([(cx-4, 11+y), (cx+4, 11+y), (cx+5, 23), (cx-5, 23)], fill=tc)
    d.line([(cx-4, 11+y), (cx-5, 23)], fill=tl); d.line([(cx+4, 11+y), (cx+5, 23)], fill=td)
    d.line([(cx-5, 22), (cx+5, 22)], fill=td)
    # pää eteenpäin kumarassa + valkoinen kampaus
    hx0 = cx + 1
    d.rectangle([hx0-1, 7+y, hx0+3, 11+y], fill=SKIN); d.line([(hx0-1, 11+y), (hx0+3, 11+y)], fill=SKIN_D)
    d.rectangle([hx0-3, 5+y, hx0+2, 8+y], fill=hx('#e8e8ec')); d.rectangle([hx0-4, 3+y, hx0-1, 6+y], fill=hx('#d4d4da'))
    d.point((hx0-3, 4+y), fill=WHITE)
    d.line([(hx0+1, 9+y), (hx0+3, 9+y)], fill=hx('#7a7a80')); d.point((hx0+2, 9+y), fill=OUT)   # lasit
    # käsilaukku kyynärtaipeessa
    if mode == 'ampuu':
        if f == 0:   # laukku ylhäällä
            d.line([(cx+2, 12), (cx+5, 5)], fill=tc, width=2); d.rectangle([cx+4, 1, cx+9, 5], fill=hx('#7a1f3a'))
            d.line([(cx+5, 0), (cx+8, 0)], fill=hx('#4a1020'))
        else:        # laukku iskee eteen
            d.line([(cx+2, 12), (cx+8, 11)], fill=tc, width=2); d.rectangle([cx+9, 9, cx+14, 13], fill=hx('#7a1f3a'))
            d.line([(cx+9, 8), (cx+12, 8)], fill=hx('#4a1020'))
    else:
        d.rectangle([cx-6, 14+y, cx-3, 18+y], fill=hx('#7a1f3a')); d.line([(cx-5, 13+y), (cx-4, 13+y)], fill=hx('#4a1020'))
    # rollaattori
    ry = y if mv else 0
    d.line([(cx+4, 13+y), (19, 13+ry)], fill=tc)                       # käsivarsi
    d.point((19, 13+ry), fill=SKIN)
    M = hx('#b8bcc0'); M2 = hx('#7a7e82')
    d.line([(20, 12+ry), (21, 26)], fill=M); d.line([(27, 15+ry), (28, 26)], fill=M)
    d.line([(20, 12+ry), (27, 15+ry)], fill=M2); d.rectangle([19, 11+ry, 21, 12+ry], fill=hx('#2a2a2a'))
    d.rectangle([21, 18+ry, 27, 21+ry], fill=hx('#5a5e62')); d.line([(21, 18+ry), (27, 18+ry)], fill=M)   # kori
    d.point([(23, 17+ry), (25, 17+ry)], fill=hx('#e8b44a'))                                                # pullat korissa
    for x in (21, 28):
        d.rectangle([x-1, 25, x+1, 27], fill=hx('#1c1c1c'))
        d.point((x + (0 if f % 2 == 0 or not mv else (1 if f == 1 else -1)), 26), fill=hx('#8a8e92'))
    outline(im)
    if mode == 'ampuu' and f == 1:
        d.point([(26, 8), (27, 10), (26, 13), (25, 11)], fill=YEL); d.point((26, 11), fill=WHITE)
    return im

def isa_trimmeri(tc, f=0, mode='kavely'):
    """Isä: lippis, oranssit kuulosuojaimet, viikset; siimatrimmeri alaviistoon eteen."""
    im, d = canvas(); td = shade(tc, .65)
    mv = mode == 'kavely'; w = WALK[f] if mv else 0; b = BOB[f] if mv else 0
    cx = 12; top = 6 + b
    person(d, tc, cx=cx, top=top, hat='lippis', walk=w)
    OR = hx('#f07a10'); ORD = hx('#b0500a')
    d.line([(cx-3, top-1), (cx+2, top-1)], fill=ORD)                         # sanka
    d.rectangle([cx-4, top+2, cx-3, top+4], fill=OR); d.rectangle([cx+3, top+2, cx+4, top+4], fill=OR)
    d.line([(cx-1, top+5), (cx+1, top+5)], fill=hx('#5a3a20'))               # viikset
    d.line([(cx-1, top+9), (cx+1, top+9)], fill=shade(tc, 1.3))              # paidan kaulus
    # trimmeri: moottori takana ylhäällä, varsi alaviistoon, terä edessä
    sh = 1 if (mode == 'ampuu' and f == 1) else 0
    d.line([(5, 15+b), (27+sh, 24)], fill=hx('#b8bcc0'))
    d.rectangle([1, 14+b, 5, 17+b], fill=OR); d.line([(1, 17+b), (5, 17+b)], fill=ORD); d.point((2, 15+b), fill=hx('#2a2a2a'))
    d.line([(16, 15+b), (17, 19+b)], fill=hx('#2a2a2a'))                     # kahva
    d.rectangle([cx+3, 15+b, cx+4, 16+b], fill=SKIN); d.rectangle([16, 17+b, 17, 18+b], fill=SKIN)
    hxp = 27 + sh
    d.rectangle([hxp-2, 22, hxp+2, 24], fill=OR); d.line([(hxp-3, 25), (hxp+3, 25)], fill=hx('#2a2a2a'))
    outline(im)
    # siima pyörii
    s = (f % 2) if mv else f
    sp = [(hxp-4, 26), (hxp+4, 26)] if s == 0 else [(hxp-3, 27), (hxp+3, 25)]
    d.line(sp, fill=hx('#e0e0e0'))
    if mode == 'ampuu':   # ruohonsilppua ja pölyä lentää
        r = random.Random(40 + f)
        for _ in range(7): d.point((hxp + r.randint(-4, 5), r.randint(16, 23)), fill=r.choice([hx('#4aa03a'), hx('#6ac04a'), hx('#8a6a40')]))
    return im

def grillimestari(tc, f=0, mode='kavely'):
    """Kokkihattu, tiimivärinen takki, pyörillä kulkeva pallogrilli jonka kannella Emma (pannulipas)."""
    im, d = canvas(); td = shade(tc, .65)
    mv = mode == 'kavely'; w = WALK[f] if mv else 0; b = BOB[f] if mv else 0
    cx = 8; top = 7 + b
    person(d, tc, cx=cx, top=top, hat=None, walk=w)
    d.rectangle([cx-3, top-4, cx+3, top+1], fill=WHITE); d.rectangle([cx-4, top-5, cx+4, top-3], fill=WHITE)
    d.line([(cx-3, top+1), (cx+3, top+1)], fill=hx('#c8c8c4')); d.point((cx-2, top-4), fill=hx('#d8d8d4'))
    d.line([(cx-2, top+8), (cx+2, top+8)], fill=WHITE)                          # kokin kaulahuivi
    # grilli (pallo) + jalat + pyörät
    gx = 22
    d.line([(gx-4, 22), (gx-5, 27)], fill=hx('#3a3a3a')); d.line([(gx+4, 22), (gx+5, 27)], fill=hx('#3a3a3a'))
    d.line([(gx, 23), (gx, 26)], fill=hx('#3a3a3a'))
    d.ellipse([gx-6, 14, gx+6, 24], fill=hx('#2a2a2c')); d.line([(gx-4, 22), (gx+4, 22)], fill=hx('#1a1a1a'))
    d.line([(gx-5, 18), (gx-4, 17)], fill=hx('#5a5a5e'))                          # kiilto
    d.ellipse([gx-5, 14, gx+5, 17], fill=hx('#ff8a1a')); d.line([(gx-3, 15), (gx+3, 15)], fill=hx('#ffc23a'))
    for x in (gx-3, gx+1): d.line([(x, 15), (x+1, 15)], fill=hx('#8a2a1a'))   # makkarat
    for x in (gx-5, gx+5):
        d.rectangle([x-1, 26, x+1, 28], fill=hx('#1c1c1c'))
        d.point((x + (0 if (not mv or f % 2 == 0) else 1), 27), fill=hx('#8a8e92'))
    # Emma grillin päällä
    rc = -1 if (mode == 'ampuu' and f == 0) else 0
    d.rectangle([cx+2+rc, 9+b, cx+6+rc, 10+b], fill=WOOD)
    d.rectangle([cx+6+rc, 9+b, 29+rc, 10+b], fill=GUN)
    for x in range(cx+14, 28, 2): d.point((x+rc, 9+b), fill=GUN_L)
    d.line([(26+rc, 11+b), (25+rc, 13+b)], fill=GUN); d.line([(27+rc, 11+b), (28+rc, 13+b)], fill=GUN)
    d.ellipse([cx+7+rc, 6+b, cx+13+rc, 8+b], fill=hx('#4a5030')); d.point((cx+10+rc, 6+b), fill=hx('#7a8050'))
    d.rectangle([cx+3, 11+b, cx+4, 12+b], fill=SKIN)
    outline(im)
    def smoke(l):
        o = (f % 2) if mv else 0
        l.ellipse([gx-4+o, 3-o, gx+o, 7-o], fill=(200, 200, 200, 100)); l.ellipse([gx-o, 0, gx+3-o, 3], fill=(210, 210, 210, 70))
    if mode == 'ampuu':
        if f == 0: flash(d, 31, 9 + b)
        else:
            d.rectangle([27, 2, 30, 3], fill=hx('#a03a20')); d.line([(27, 2), (30, 2)], fill=hx('#c85a3a'))   # lentävä makkara
            layer(im, lambda l: l.ellipse([gx-5, 1, gx+2, 7], fill=(190, 185, 175, 150)))
    else: layer(im, smoke)
    return im

# ---------- sammunut (makaa maassa, zzz) ----------
def sammunut(tc, kind):
    im, d = canvas(); td = shade(tc, .65); tl = shade(tc, 1.3)
    d.ellipse([3, 23, 29, 29], fill=SHADOW)
    # esine maassa takana
    if kind == 'tolkkijussi': bag(d, 4, 15); bag(d, 25, 17)
    elif kind == 'lahiojermu': d.line([(5, 18), (21, 16)], fill=GUN, width=2); d.rectangle([3, 18, 6, 19], fill=WOOD)
    elif kind == 'parvekeampuja':
        d.rectangle([4, 13, 22, 18], fill=hx('#9a4e2a')); d.line([(4, 13), (22, 13)], fill=hx('#c8ccd0'))
        for x in range(5, 22, 2): d.line([(x, 14), (x, 18)], fill=hx('#7a3a1e'))
    elif kind == 'mopopoika':
        d.rectangle([6, 13, 22, 17], fill=tc); d.line([(6, 13), (22, 13)], fill=tl)
        for x in (4, 24): d.ellipse([x-2, 10, x+2, 19], fill=hx('#1c1c1c')); d.point((x, 14), fill=hx('#9a9a9a'))
    elif kind == 'mummo':
        M = hx('#b8bcc0'); d.rectangle([4, 14, 12, 15], fill=M); d.line([(4, 14), (4, 19)], fill=M); d.line([(12, 14), (12, 19)], fill=M)
        d.rectangle([5, 16, 11, 17], fill=hx('#5a5e62')); d.rectangle([3, 19, 5, 20], fill=hx('#1c1c1c')); d.rectangle([11, 19, 13, 20], fill=hx('#1c1c1c'))
        d.rectangle([24, 14, 28, 17], fill=hx('#7a1f3a'))
    elif kind == 'isa_trimmeri':
        d.line([(4, 15), (26, 18)], fill=hx('#b8bcc0')); d.rectangle([2, 13, 6, 16], fill=hx('#f07a10')); d.rectangle([25, 16, 29, 18], fill=hx('#f07a10'))
    elif kind == 'grillimestari':
        d.rectangle([24, 14, 29, 17], fill=WHITE); d.rectangle([23, 17, 30, 18], fill=WHITE)    # pudonnut kokkihattu
        d.line([(4, 17), (10, 15)], fill=hx('#9a9a9a'))                                       # grillipihdit
        d.rectangle([12, 15, 15, 16], fill=hx('#a03a20'))                                     # makkara
    # makaava hahmo, pää oikealla
    legs = hx('#b89a80') if kind == 'mummo' else PANTS
    d.rectangle([5, 21, 11, 22], fill=legs); d.rectangle([6, 23, 11, 24], fill=legs)
    d.rectangle([3, 21, 4, 22], fill=BOOT); d.rectangle([4, 23, 5, 24], fill=BOOT)
    body = tc
    d.rectangle([11, 19, 20, 25], fill=body); d.line([(11, 19), (20, 19)], fill=tl); d.line([(11, 25), (20, 25)], fill=td)
    if kind == 'mummo': d.rectangle([6, 19, 11, 25], fill=tc)
    d.rectangle([21, 19, 25, 23], fill=SKIN); d.line([(22, 21), (23, 21)], fill=OUT); d.line([(21, 23), (25, 23)], fill=SKIN_D)
    d.rectangle([18, 25, 21, 26], fill=SKIN)                                                    # käsi retkottaa
    if kind == 'tolkkijussi': d.rectangle([26, 19, 27, 23], fill=td)
    elif kind == 'lahiojermu': d.rectangle([26, 18, 27, 24], fill=td); d.line([(27, 18), (27, 24)], fill=tl)
    elif kind == 'parvekeampuja': d.rectangle([24, 18, 27, 24], fill=td); d.rectangle([21, 20, 24, 22], fill=SKIN)
    elif kind == 'mopopoika': d.ellipse([21, 18, 28, 24], fill=td); d.rectangle([21, 20, 23, 22], fill=GLASS)
    elif kind == 'mummo': d.rectangle([25, 18, 28, 23], fill=hx('#e8e8ec')); d.point((22, 21), fill=hx('#7a7a80'))
    elif kind == 'isa_trimmeri':
        d.rectangle([26, 19, 27, 23], fill=hx('#2a2a2a')); d.rectangle([22, 18, 24, 18], fill=hx('#f07a10')); d.rectangle([22, 24, 24, 24], fill=hx('#f07a10'))
    elif kind == 'grillimestari': d.rectangle([26, 19, 26, 23], fill=hx('#5a3a20'))
    zzz(d, 18, 12)
    return outline(im)

# =====================================================================
# AJONEUVOT 48x32
# =====================================================================
VB = [0, -1, 0, -1]   # rungon pomppu

def arch(d, cx, cy, r): d.ellipse([cx-r-1, cy-r-1, cx+r+1, cy+r+1], fill=hx('#141414'))

def volvo(tc, f=0, mode='kavely'):
    """Tuunattu 240-farmari: pitkä laatikko, takaspoileri, liekkiteipit, mustat vanteet, madallettu."""
    im, d = canvas(48, 32); tl = shade(tc, 1.3); td = shade(tc, .65); y = VB[f]
    shadow(d, 24, 28, 23, 3)
    d.rectangle([1, 16+y, 46, 25+y], fill=tc); d.line([(1, 16+y), (46, 16+y)], fill=tl); d.line([(1, 25+y), (46, 25+y)], fill=td)
    d.polygon([(3, 9+y), (30, 9+y), (36, 16+y), (3, 16+y)], fill=tc)
    d.rectangle([3, 7+y, 30, 9+y], fill=tl)                                         # katto
    d.rectangle([0, 6+y, 6, 7+y], fill=hx('#1c1c1c'))                               # spoileri
    d.polygon([(5, 10+y), (13, 10+y), (13, 15+y), (5, 15+y)], fill=GLASS)
    d.rectangle([15, 10+y, 22, 15+y], fill=GLASS); d.polygon([(24, 10+y), (30, 10+y), (34, 15+y), (24, 15+y)], fill=GLASS)
    d.line([(16, 10+y), (19, 10+y)], fill=GLASS_L); d.line([(25, 10+y), (28, 10+y)], fill=GLASS_L)
    d.line([(36, 16+y), (46, 17+y)], fill=tl)                                        # konepelti
    d.line([(23, 17+y), (23, 23+y)], fill=td); d.line([(13, 17+y), (13, 23+y)], fill=td)   # ovisaumat
    d.rectangle([45, 18+y, 47, 21+y], fill=hx('#f0f0d0')); d.rectangle([45, 22+y, 47, 23+y], fill=hx('#2a2a2a'))
    d.rectangle([0, 18+y, 1, 21+y], fill=hx('#c02020'))
    d.line([(0, 24+y), (47, 24+y)], fill=hx('#2a2a2a'))                               # helmalista
    # liekkiteippi
    for i, x in enumerate(range(28, 44, 3)):
        d.polygon([(x, 22+y), (x+4, 19+y-(i % 2)), (x+3, 22+y)], fill=hx('#ffb020'))
    d.line([(28, 22+y), (43, 22+y)], fill=hx('#e0601a'))
    for cx in (10, 37): arch(d, cx, 25, 4); wheel(d, cx, 25, 4, f, rim=hx('#3a3c40'))
    d.line([(0, 26), (3, 26)], fill=hx('#b0b0b0'))                                    # pakoputki
    outline(im)
    if f in (1, 2): layer(im, lambda l: l.ellipse([0, 22 - f, 3, 25 - f], fill=(180, 180, 180, 110)))
    return im

def lada(tc, f=0, mode='kavely'):
    """Laatikkomainen sedan: kromipuskurit, pyöreät valot, ruostetta, kattotelineellä kaljakori."""
    im, d = canvas(48, 32); body = shade(tc, .9); tl = shade(tc, 1.2); td = shade(tc, .6); y = VB[f]
    shadow(d, 24, 28, 20, 3)
    d.rectangle([5, 16+y, 43, 25+y], fill=body); d.line([(5, 16+y), (43, 16+y)], fill=tl); d.line([(5, 25+y), (43, 25+y)], fill=td)
    d.polygon([(12, 16+y), (15, 9+y), (30, 9+y), (34, 16+y)], fill=body)
    d.line([(15, 9+y), (30, 9+y)], fill=tl)
    d.polygon([(14, 15+y), (16, 11+y), (21, 11+y), (21, 15+y)], fill=GLASS); d.polygon([(23, 11+y), (29, 11+y), (32, 15+y), (23, 15+y)], fill=GLASS)
    d.line([(24, 11+y), (27, 11+y)], fill=GLASS_L)
    d.line([(22, 17+y), (22, 23+y)], fill=td)
    # kattoteline + keltainen kaljakori
    d.line([(15, 8+y), (30, 8+y)], fill=hx('#5a5a5a')); d.point([(16, 8+y), (29, 8+y)], fill=hx('#3a3a3a'))
    d.rectangle([17, 3+y, 26, 7+y], fill=hx('#e8c020')); d.line([(17, 3+y), (26, 3+y)], fill=hx('#fff08a'))
    for x in range(18, 26, 2): d.point((x, 4+y), fill=hx('#c8ced6'))
    # ruostetta, valot, puskurit
    d.point([(8, 22+y), (9, 23+y), (8, 23+y), (38, 23+y)], fill=hx('#8a4a1a'))
    d.ellipse([41, 17+y, 43, 19+y], fill=hx('#f0f0d0')); d.point((40, 20+y), fill=hx('#f0a020'))
    d.rectangle([4, 18+y, 5, 20+y], fill=hx('#c02020'))
    d.line([(3, 23+y), (6, 23+y)], fill=hx('#d8dce0')); d.line([(42, 23+y), (45, 23+y)], fill=hx('#d8dce0'))
    for cx in (13, 36): arch(d, cx, 25, 4); wheel(d, cx, 25, 4, f, rim=hx('#a8acb0'))
    outline(im)
    if f in (1, 2): layer(im, lambda l: l.ellipse([0, 23 - f, 4, 27 - f], fill=(120, 120, 120, 130)))   # Lada savuttaa
    return im

def monkija(tc, f=0, mode='kavely'):
    """Mönkijä: isot nappularenkaat, tiimiväriset lokasuojat, telineet, kuski kypärässä."""
    im, d = canvas(48, 32); tl = shade(tc, 1.3); td = shade(tc, .65); y = VB[f] if mode == 'kavely' else 0
    shadow(d, 24, 28, 19, 3)
    for cx in (12, 35):
        kk = f if mode == 'kavely' else 0
        wheel(d, cx, 23, 5, kk, rim=hx('#c8b020'))
        for a in range(0, 360, 45):     # nappulat
            aa = math.radians(a + kk * 22); d.point((cx + round(math.cos(aa) * 5.5), 23 + round(math.sin(aa) * 5.5)), fill=hx('#1c1c1c'))
    d.rectangle([15, 17+y, 32, 22+y], fill=hx('#3a3c40'))                                   # runko/moottori
    d.rectangle([18, 19+y, 24, 22+y], fill=hx('#6a6c70'))
    d.polygon([(4, 18+y), (7, 14+y), (19, 14+y), (20, 18+y)], fill=tc); d.line([(7, 14+y), (19, 14+y)], fill=tl)
    d.polygon([(28, 18+y), (29, 14+y), (41, 14+y), (44, 18+y)], fill=tc); d.line([(29, 14+y), (41, 14+y)], fill=tl)
    d.line([(4, 18+y), (20, 18+y)], fill=td); d.line([(28, 18+y), (44, 18+y)], fill=td)
    d.line([(4, 12+y), (14, 12+y)], fill=hx('#6a6c70')); d.line([(33, 12+y), (42, 12+y)], fill=hx('#6a6c70'))   # telineet
    d.rectangle([6, 9+y, 11, 11+y], fill=hx('#6a4a2a'))                                      # laatikko takatelineellä
    d.rectangle([15, 12+y, 25, 14+y], fill=hx('#1c1c1c'))                                    # penkki
    d.line([(29, 13+y), (31, 9+y)], fill=hx('#555555')); d.line([(30, 9+y), (33, 9+y)], fill=hx('#1c1c1c'))
    d.point((43, 16+y), fill=hx('#ffe680'))
    # kuski
    d.rectangle([17, 6+y, 23, 12+y], fill=tc); d.line([(17, 6+y), (17, 12+y)], fill=tl)
    d.line([(23, 8+y), (30, 9+y)], fill=tc, width=2); d.point((30, 9+y), fill=SKIN)
    d.rectangle([21, 12+y, 26, 15+y], fill=PANTS); d.rectangle([25, 15+y, 27, 18+y], fill=BOOT)
    d.ellipse([17, 0+y, 23, 6+y], fill=td); d.line([(18, 1+y), (21, 1+y)], fill=tl); d.rectangle([21, 3+y, 23, 4+y], fill=GLASS)
    if mode == 'ampuu':   # Suomi-konepistooli (rumpulipas) ohjaustangon yli
        rc = -1 if f == 1 else 0
        d.line([(23, 7), (27, 6)], fill=tc, width=2)
        d.rectangle([25+rc, 5, 27+rc, 6], fill=WOOD); d.rectangle([27+rc, 5, 35+rc, 6], fill=GUN); d.line([(30+rc, 5), (35+rc, 5)], fill=GUN_L)
        d.ellipse([28+rc, 7, 31+rc, 10], fill=hx('#3a3c40'))
    outline(im)
    if mode == 'ampuu':
        if f == 0: flash(d, 37, 5)
        else: d.point((29, 2), fill=hx('#d8b030')); layer(im, lambda l: l.ellipse([35, 3, 39, 7], fill=(210, 210, 210, 140)))
    elif f in (1, 3) and mode == 'kavely': layer(im, lambda l: [l.point((x, 27), fill=(140, 110, 70, 160)) for x in (3, 5, 26, 28)])   # multaa
    return im

def dnepr(tc, f=0, mode='kavely'):
    """Dnepr-sivuvaunupyörä: oliivinvihreä pyörä, tiimivärinen sivuvaunu, sivuvaunussa Emma-ampuja."""
    im, d = canvas(48, 32); tl = shade(tc, 1.3); td = shade(tc, .65)
    mv = mode == 'kavely'; y = VB[f] if mv else 0; k = f if mv else 0
    OL = hx('#5a6332'); OLL = hx('#7a8448'); OLD = hx('#3e4422')
    shadow(d, 24, 28, 23, 3)
    for cx in (8, 40): wheel(d, cx, 22, 5, k)
    d.arc([2, 16, 14, 28], 180, 300, fill=OL)                                              # takalokasuoja
    d.rectangle([15, 15+y, 27, 19+y], fill=hx('#6a6c70'))                                    # moottori
    d.polygon([(16, 12+y), (28, 12+y), (29, 15+y), (17, 16+y)], fill=OL); d.line([(17, 12+y), (28, 12+y)], fill=OLL)  # tankki
    d.rectangle([9, 12+y, 16, 13+y], fill=hx('#2a2a2a'))                                     # satula
    d.line([(32, 10+y), (40, 22)], fill=hx('#7a7e82')); d.line([(30, 9+y), (33, 9+y)], fill=hx('#2a2a2a'))
    d.rectangle([34, 11+y, 36, 13+y], fill=OL); d.point((36, 12+y), fill=hx('#ffe680'))
    # kuski
    d.rectangle([9, 7+y, 15, 12+y], fill=OLD); d.line([(9, 7+y), (9, 12+y)], fill=OL)
    d.line([(15, 8+y), (30, 9+y)], fill=OLD, width=2); d.point((30, 9+y), fill=SKIN)
    d.ellipse([9, 1+y, 15, 7+y], fill=td); d.line([(10, 2+y), (13, 2+y)], fill=tl); d.rectangle([13, 4+y, 15, 5+y], fill=hx('#c8a040'))
    # sivuvaunu (lähempänä katsojaa)
    wheel(d, 27, 26, 3, k)
    d.polygon([(13, 18+y), (35, 18+y), (41, 21+y), (37, 26+y), (15, 26+y), (12, 22+y)], fill=tc)
    d.line([(13, 18+y), (35, 18+y)], fill=tl); d.line([(15, 26+y), (37, 26+y)], fill=td)
    d.line([(14, 22+y), (39, 22+y)], fill=td)
    # ampuja + Emma
    rc = -1 if (mode == 'ampuu' and f == 1) else 0
    d.rectangle([21, 14+y, 27, 18+y], fill=OLD); d.ellipse([21, 8+y, 27, 14+y], fill=td); d.line([(22, 9+y), (25, 9+y)], fill=tl)
    d.rectangle([25, 11+y, 27, 13+y], fill=SKIN)
    d.rectangle([25+rc, 15+y, 29+rc, 16+y], fill=WOOD)
    d.rectangle([29+rc, 15+y, 44+rc, 16+y], fill=hx('#3a3c40')); d.line([(29+rc, 15+y), (44+rc, 15+y)], fill=hx('#6a6c70'))
    for x in range(34, 43, 2): d.point((x+rc, 16+y), fill=GUN)
    d.ellipse([29+rc, 12+y, 35+rc, 14+y], fill=hx('#4a5030')); d.point((32+rc, 12+y), fill=hx('#8a9058'))
    d.line([(41+rc, 17+y), (40+rc, 19+y)], fill=GUN); d.line([(42+rc, 17+y), (43+rc, 19+y)], fill=GUN)   # jalusta
    outline(im)
    if mode == 'ampuu':
        if f == 0: flash(d, 45, 15 + y)
        else: d.point((31, 10), fill=hx('#d8b030')); layer(im, lambda l: l.ellipse([43, 12, 47, 16], fill=(210, 210, 210, 140)))
    elif f in (1, 2): layer(im, lambda l: l.ellipse([0, 17 - f, 3, 20 - f], fill=(190, 190, 190, 110)))
    return im

def poliisiauto(f=0):
    """Neutraali partioauto: valkoinen, sininen sivuraita, katolla sini-punainen valopalkki (ei tunnuksia)."""
    im, d = canvas(48, 32); y = VB[f]
    W = hx('#e8ecf0'); WL = hx('#ffffff'); WD = hx('#a8b0b8'); BL = hx('#1a3a9a')
    shadow(d, 24, 28, 22, 3)
    d.rectangle([2, 16+y, 46, 25+y], fill=W); d.line([(2, 16+y), (46, 16+y)], fill=WL); d.line([(2, 25+y), (46, 25+y)], fill=WD)
    d.polygon([(8, 16+y), (13, 9+y), (30, 9+y), (36, 16+y)], fill=W); d.line([(13, 9+y), (30, 9+y)], fill=WL)
    d.polygon([(11, 15+y), (14, 11+y), (21, 11+y), (21, 15+y)], fill=GLASS); d.polygon([(23, 11+y), (29, 11+y), (33, 15+y), (23, 15+y)], fill=GLASS)
    d.rectangle([2, 19+y, 46, 21+y], fill=BL)
    for x in range(4, 46, 4): d.point((x, 20+y), fill=hx('#f0d020'))                     # heijastinruudutus
    d.line([(22, 16+y), (22, 23+y)], fill=WD)
    d.rectangle([45, 17+y, 47, 18+y], fill=hx('#f0f0d0')); d.rectangle([1, 17+y, 2, 18+y], fill=hx('#c02020'))
    d.line([(1, 23+y), (47, 23+y)], fill=hx('#3a3c40'))
    # valopalkki
    on_b = f % 2 == 0
    d.rectangle([16, 6+y, 21, 8+y], fill=hx('#3aa0ff') if on_b else hx('#1a3a7a'))
    d.rectangle([22, 6+y, 27, 8+y], fill=hx('#ff3a3a') if not on_b else hx('#7a1a1a'))
    d.line([(16, 6+y), (27, 6+y)], fill=WL)
    for cx in (11, 37): arch(d, cx, 25, 4); wheel(d, cx, 25, 4, f)
    outline(im)
    def glow(l):
        c = (90, 170, 255, 90) if on_b else (255, 80, 80, 90)
        x0 = 16 if on_b else 22; l.ellipse([x0-2, 4+y, x0+7, 10+y], fill=c)
    gl = Image.new('RGBA', im.size, CLEAR); glow(ImageDraw.Draw(gl))
    im = Image.alpha_composite(gl, im)   # hehku rungon taakse
    return im

# =====================================================================
# EFEKTIT
# =====================================================================
def suuliekki():
    im, d = canvas(8, 8)
    d.polygon([(1, 1), (7, 4), (1, 6)], fill=hx('#ff8a1a')); d.polygon([(1, 2), (6, 4), (1, 5)], fill=hx('#ffc23a'))
    d.line([(0, 3), (4, 3)], fill=YEL); d.line([(0, 4), (4, 4)], fill=YEL); d.point([(1, 3), (1, 4)], fill=WHITE)
    d.point([(3, 0), (3, 7)], fill=hx('#ff8a1a'))
    return im

def rajahdys():
    frames = []; R = random.Random(64)
    blobs = [(R.uniform(0, 6.283), R.uniform(0, 1), R.uniform(.6, 1.1)) for _ in range(14)]
    debris = [(R.uniform(0, 6.283), R.uniform(.7, 1.2)) for _ in range(12)]
    pal = [hx('#fff8d0'), hx('#ffe14a'), hx('#ff9a1a'), hx('#e0401a'), hx('#7a2a1a'), hx('#5a5456'), hx('#8a8486')]
    for k in range(6):
        im, d = canvas(64, 64); c = 32
        if k == 0:
            d.ellipse([c-9, c-9, c+9, c+9], fill=pal[1]); d.ellipse([c-6, c-6, c+6, c+6], fill=pal[0])
            for a in range(0, 360, 45):
                aa = math.radians(a); d.line([(c, c), (c + math.cos(aa) * 14, c + math.sin(aa) * 14)], fill=pal[1])
            frames.append(im); continue
        rad = [0, 20, 25, 27, 28, 29][k]
        layers = {1: [2, 1, 0], 2: [3, 2, 1], 3: [5, 3, 2], 4: [6, 5, 4], 5: [6, 5, 5]}[k]
        sc = [1.0, .72, .45]
        for li, ci in enumerate(layers):
            col = pal[ci]
            if k >= 4: col = col[:3] + ((200 if k == 4 else 120) - li * 10,)
            for (a, dist, s) in blobs:
                br = rad * .58 * s * sc[li]; dx = math.cos(a) * dist * rad * .55 * sc[li]; dy = math.sin(a) * dist * rad * .55 * sc[li] - (k - 1) * 1.5 * li
                d.ellipse([c+dx-br, c+dy-br - (k * 2 if k >= 3 else 0), c+dx+br, c+dy+br - (k * 2 if k >= 3 else 0)], fill=col)
        if 2 <= k <= 4:
            for (a, s) in debris:
                r = rad * s * (1 + k * .15); x, y = c + math.cos(a) * r, c + math.sin(a) * r + (k - 2) * 2
                d.point((x, y), fill=pal[2] if k < 4 else pal[4]); d.point((x + 1, y), fill=pal[3])
        if k == 5:   # hiipuvat hiillokset
            for (a, s) in debris[:6]: d.point((c + math.cos(a) * 14 * s, c + 10 + math.sin(a) * 4), fill=hx('#ff9a1a'))
        frames.append(im)
    return strip(frames)

def molotovi():
    im, d = canvas(16, 16)
    d.rectangle([5, 8, 10, 14], fill=hx('#3a8a3a')); d.rectangle([6, 6, 9, 7], fill=hx('#3a8a3a')); d.rectangle([7, 4, 8, 5], fill=hx('#3a8a3a'))
    d.line([(6, 9), (6, 13)], fill=hx('#7ac07a')); d.rectangle([6, 11, 9, 13], fill=hx('#c8a040'))   # kalja/bensa sisällä
    d.rectangle([7, 2, 8, 3], fill=hx('#e8e0c8'))                                                 # rätti
    d.polygon([(8, 0), (11, 0), (10, 3), (8, 3)], fill=hx('#ff8a1a')); d.point([(9, 1), (10, 1)], fill=YEL)
    outline(im)
    d.point((12, 0), fill=hx('#ffc23a'))
    return im

def tuli():
    frames = []
    for k in range(4):
        im, d = canvas(32, 32); R = random.Random(300 + k)
        d.ellipse([4, 26, 28, 30], fill=SHADOW)
        d.line([(7, 28), (24, 25)], fill=hx('#4a3220'), width=2); d.line([(8, 25), (25, 28)], fill=hx('#5a3a24'), width=2)
        for col, wmul, hmul in ((hx('#c0301a'), 1.0, 1.0), (hx('#ff8a1a'), .7, .75), (hx('#ffe14a'), .4, .45)):
            for i, x in enumerate(range(8, 25, 4)):
                hgt = (14 + 6 * math.sin(i * 1.7 + k * 1.57) + R.uniform(-2, 2)) * hmul; ww = 4 * wmul
                tip = x + R.choice([-1, 0, 1])
                d.polygon([(x - ww, 27), (x + ww, 27), (tip, 27 - hgt)], fill=col)
        for _ in range(4): d.point((R.randint(8, 24), R.randint(2, 10)), fill=hx('#ffc23a'))
        frames.append(im)
    return strip(frames)

def sade():
    im = Image.new('RGBA', (64, 64), CLEAR); px = im.load(); R = random.Random(64)
    for _ in range(46):
        x, y = R.randrange(64), R.randrange(64); L = R.choice([3, 4, 5])
        for i in range(L):
            a = 90 + 15 * i
            px[(x - i // 2) % 64, (y + i) % 64] = (180, 205, 240, min(200, a))
    for _ in range(6):   # pieniä roiskeita
        x, y = R.randrange(64), R.randrange(64)
        for dx in (-1, 1): px[(x + dx) % 64, y] = (200, 220, 245, 120)
    return im

def makkara():
    im, d = canvas(8, 8)
    d.rectangle([1, 3, 6, 5], fill=hx('#a83a20')); d.line([(2, 3), (5, 3)], fill=hx('#d86a40'))
    d.point([(3, 4), (5, 5)], fill=hx('#5a1a0a')); d.point([(0, 4), (7, 4)], fill=hx('#7a2a14'))
    return outline(im)

def kary():
    im = Image.new('RGBA', (32, 32), CLEAR)
    for (cx, cy, r, a, col) in [(16, 18, 11, 70, (150, 145, 135)), (11, 17, 7, 120, (170, 165, 155)), (20, 14, 8, 120, (175, 170, 160)),
                                (15, 21, 8, 130, (140, 135, 128)), (14, 12, 5, 130, (195, 190, 182)), (21, 21, 6, 120, (160, 155, 148)),
                                (12, 13, 3, 140, (215, 212, 205)), (19, 11, 3, 140, (215, 212, 205))]:
        l = Image.new('RGBA', (32, 32), CLEAR); ImageDraw.Draw(l).ellipse([cx-r, cy-r, cx+r, cy+r], fill=col + (a,)); im.alpha_composite(l)
    return im

def zzz16():
    im, d = canvas(16, 16); zzz(d, 1, 13); return outline(im)

def kirppis():
    im, d = canvas(32, 32)
    shadow(d, 16, 27, 14, 3)
    W = hx('#8a5a30'); WL = hx('#b07a44')
    d.rectangle([3, 13, 20, 16], fill=WL); d.line([(3, 16), (20, 16)], fill=W)
    d.line([(4, 17), (4, 25)], fill=W); d.line([(19, 17), (19, 25)], fill=W)
    d.rectangle([4, 10, 19, 13], fill=hx('#e8e0c8'))                     # pöytäliina
    for i, x in enumerate((5, 9, 13)): d.rectangle([x, 8, x+2, 11], fill=[hx('#c8ced6'), hx('#2f6fb0'), hx('#d8b030')][i])
    d.rectangle([16, 6, 19, 9], fill=hx('#f0d020'))   # hintalappu
    d.point((17, 7), fill=OUT); d.point((18, 8), fill=OUT)
    # tölkkikasa maassa
    cans = [(18, 24), (21, 24), (24, 24), (27, 24), (19, 21), (22, 21), (25, 21), (21, 18), (24, 18), (8, 25), (11, 25)]
    cols = [hx('#c8ced6'), hx('#2f6fb0'), hx('#d8b030'), hx('#c03030')]
    for i, (x, y) in enumerate(cans):
        c = cols[i % 4]; d.rectangle([x, y, x+2, y+3], fill=c); d.point((x, y), fill=shade(c, 1.3)); d.point((x+2, y+3), fill=shade(c, .6))
    return outline(im)

def sauna():
    im, d = canvas(32, 32)
    shadow(d, 14, 28, 11, 2)
    d.rectangle([5, 15, 22, 27], fill=hx('#3a3a3c')); d.line([(5, 15), (22, 15)], fill=hx('#5a5a5e'))     # kiuas
    d.rectangle([8, 22, 13, 25], fill=hx('#1a1a1a')); d.rectangle([9, 23, 12, 24], fill=hx('#ff8a1a'))    # luukku+hehku
    for (x, y) in [(6, 12), (9, 11), (12, 12), (15, 11), (18, 12), (8, 13), (14, 13), (19, 14), (11, 14)]:
        d.ellipse([x, y, x+3, y+2], fill=hx('#8a8580')); d.point((x+1, y), fill=hx('#b8b4ae'))
    # kiulu + kauha
    d.rectangle([23, 21, 29, 27], fill=hx('#b07a44')); d.line([(23, 23), (29, 23)], fill=hx('#7a5030')); d.line([(23, 26), (29, 26)], fill=hx('#7a5030'))
    d.line([(26, 16), (26, 22)], fill=hx('#8a5a30')); d.ellipse([24, 14, 28, 17], fill=hx('#8a5a30'))
    outline(im)
    def steam(l):
        for (cx, cy, r, a) in [(10, 7, 4, 120), (16, 5, 5, 110), (13, 2, 3, 90), (20, 8, 3, 100)]:
            l.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(235, 238, 242, a))
    return layer(im, steam)

def kesajuhlat():
    im, d = canvas(32, 32)
    shadow(d, 16, 28, 14, 2)
    P = hx('#8a5a30')
    d.line([(2, 4), (2, 27)], fill=P); d.line([(29, 4), (29, 27)], fill=P)
    pts = [(2 + i, 5 + round(5 * math.sin(math.pi * i / 27))) for i in range(28)]
    d.line(pts, fill=hx('#d8d8d8'))
    flagc = [hx('#d8262b'), hx('#f0d020'), hx('#1f6fe0'), hx('#3aa03a'), hx('#e070c0'), hx('#ff8a1a')]
    for j, i in enumerate(range(3, 26, 4)):
        x, y = pts[i]; d.polygon([(x, y+1), (x+3, y+1), (x+1, y+5)], fill=flagc[j % 6])
    # pieni grilli ja lippusalko-tunnelma
    d.ellipse([10, 17, 20, 23], fill=hx('#2a2a2c')); d.ellipse([11, 16, 19, 19], fill=hx('#ff8a1a'))
    d.line([(12, 16), (14, 16)], fill=hx('#8a2a1a')); d.line([(16, 17), (18, 17)], fill=hx('#8a2a1a'))
    d.line([(12, 22), (11, 27)], fill=hx('#3a3a3a')); d.line([(18, 22), (19, 27)], fill=hx('#3a3a3a'))
    d.rectangle([22, 22, 26, 26], fill=hx('#e8c020')); d.line([(22, 22), (26, 22)], fill=hx('#fff08a'))   # kaljakori
    return outline(im)

# =====================================================================
# TAPAHTUMARAKENNUKSET
# =====================================================================
def alko():
    im, d, x0, yr, yw, w, h = building(hx('#d8d0c0'), hx('#55575c'), h=22)
    WR = hx('#5a1424')
    d.rectangle([x0+12, yr+7, x0+w-13, yr+21], fill=WR, outline=hx('#3a0c18'))
    text(d, x0+19, yr+12, 'VIINA', hx('#f0c850'))
    for bx in (x0+14, x0+w-17):
        d.rectangle([bx, yr+12, bx+2, yr+18], fill=hx('#3a8a3a')); d.point((bx+1, yr+11), fill=hx('#3a8a3a')); d.point((bx+1, yr+10), fill=hx('#c8a040'))
    # näyteikkunat, joissa pullohyllyt
    for i in (0, 1):
        x = x0+3 + i*31
        d.rectangle([x, yw+6, x+18, yw+h-3], fill=hx('#6f9fbf'))
        for row, yy in enumerate((yw+8, yw+13)):
            d.line([(x, yy+4), (x+18, yy+4)], fill=hx('#8a6a40'))
            for j in range(0, 18, 2):
                c = [hx('#3a8a3a'), hx('#7a1f3a'), hx('#c8a040'), hx('#e8e8e4')][(j // 2 + row + i) % 4]
                d.rectangle([x+j+1, yy+1, x+j+1, yy+3], fill=c)
    d.rectangle([x0+23, yw+8, x0+31, yw+h-1], fill=hx('#2a3a4a')); d.line([(x0+27, yw+8), (x0+27, yw+h-1)], fill=hx('#6f9fbf'))
    d.rectangle([x0+21, yw+3, x0+33, yw+5], fill=WR)
    d.rectangle([x0+w-6, yw+h-4, x0+w-2, yw+h], fill=hx('#e8e0c8')); d.point((x0+w-4, yw+h-5), fill=hx('#3a8a3a'))   # paperikassi
    return outline(im)

def bussi3(f=0):
    im, d = canvas(64, 32); y = VB[f]
    W = hx('#e8ecee'); WD = hx('#a8b0b4'); T = hx('#1a8a8a'); TD = hx('#0f5a5a')
    shadow(d, 32, 28, 31, 3)
    d.rectangle([1, 6+y, 61, 25+y], fill=W); d.rectangle([1, 4+y, 59, 6+y], fill=hx('#f8fafa'))
    d.line([(1, 25+y), (61, 25+y)], fill=WD); d.rectangle([1, 21+y, 61, 24+y], fill=hx('#4a4c50'))
    d.rectangle([1, 18+y, 61, 19+y], fill=T); d.line([(1, 20+y), (61, 20+y)], fill=TD)
    for x in range(3, 44, 7): d.rectangle([x, 9+y, x+5, 15+y], fill=hx('#2a3a4a')); d.point((x+1, 9+y), fill=GLASS)
    d.rectangle([46, 9+y, 51, 20+y], fill=hx('#5a7a8a')); d.line([(48, 9+y), (48, 20+y)], fill=hx('#2a3a4a'))   # etuovi
    d.rectangle([20, 9+y, 25, 20+y], fill=hx('#5a7a8a')); d.line([(22, 9+y), (22, 20+y)], fill=hx('#2a3a4a'))  # keskiovi
    d.polygon([(53, 9+y), (60, 9+y), (62, 16+y), (53, 16+y)], fill=hx('#6f9fbf')); d.line([(54, 10+y), (58, 10+y)], fill=GLASS_L)
    # linjakilpi '3'
    d.rectangle([52, 2+y, 60, 8+y], fill=hx('#141414')); text(d, 55, 3+y, '3', hx('#ffb020'))
    d.rectangle([61, 17+y, 62, 18+y], fill=hx('#f0f0d0')); d.rectangle([0, 17+y, 1, 18+y], fill=hx('#c02020'))
    for cx in (12, 43): arch(d, cx, 25, 4); wheel(d, cx, 25, 4, f)
    return outline(im)

# =====================================================================
# TAPAHTUMAIKONIT 32x32
# =====================================================================
def ik_poliisipartio():
    im, d = canvas()
    d.rectangle([7, 22, 24, 27], fill=hx('#3a3c40')); d.line([(7, 22), (24, 22)], fill=hx('#6a6c70'))
    d.pieslice([8, 7, 23, 30], 180, 360, fill=hx('#3aa0ff')); d.pieslice([11, 10, 20, 26], 180, 270, fill=hx('#b8e0ff'))
    d.rectangle([8, 18, 23, 21], fill=hx('#2a80e0'))
    outline(im)
    for (a, b) in [((3, 10), (6, 13)), ((28, 10), (25, 13)), ((15, 1), (15, 4)), ((1, 18), (4, 18)), ((30, 18), (27, 18))]:
        d.line([a, b], fill=hx('#ff3a3a') if a[0] > 16 else hx('#3aa0ff'))
    return im
def ik_alkon_ale():
    im, d = canvas()
    d.rectangle([8, 13, 16, 28], fill=hx('#3a8a3a')); d.polygon([(8, 13), (10, 9), (14, 9), (16, 13)], fill=hx('#3a8a3a'))
    d.rectangle([10, 3, 13, 9], fill=hx('#3a8a3a')); d.rectangle([10, 2, 13, 3], fill=hx('#c8a040'))
    d.line([(9, 14), (9, 26)], fill=hx('#7ac07a')); d.rectangle([9, 17, 15, 23], fill=hx('#e8e0c8')); d.line([(10, 19), (14, 19)], fill=hx('#7a1f3a'))
    d.polygon([(17, 12), (27, 12), (30, 17), (27, 22), (17, 22)], fill=hx('#e02a2a')); d.point((28, 17), fill=CLEAR)
    d.rectangle([19, 14, 20, 15], fill=WHITE); d.rectangle([24, 19, 25, 20], fill=WHITE)      # iso %-merkki
    d.line([(25, 14), (19, 20)], fill=WHITE)
    return outline(im)
def ik_sadekuuro():
    im, d = canvas()
    for (cx, cy, r) in [(10, 13, 6), (17, 10, 8), (24, 14, 6)]: d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=hx('#8a96a8'))
    d.rectangle([5, 14, 28, 19], fill=hx('#8a96a8')); d.ellipse([12, 4, 20, 10], fill=hx('#b0bccc'))
    d.line([(6, 19), (27, 19)], fill=hx('#6a7688'))
    for i, x in enumerate(range(7, 27, 4)):
        yy = 22 + (i % 2) * 3; d.line([(x+1, yy), (x, yy+3)], fill=hx('#4a90e0'))
    return outline(im)
def ik_automaatti_rikki():
    im, d = canvas()
    d.rectangle([7, 3, 22, 28], fill=hx('#c8ccd0')); d.line([(7, 3), (22, 3)], fill=hx('#e8ecf0'))
    d.rectangle([9, 6, 20, 11], fill=hx('#1a2a1a')); text(d, 11, 6, '?', hx('#ff4040'))
    d.rectangle([11, 15, 18, 17], fill=hx('#1a1a1a')); d.rectangle([9, 21, 20, 25], fill=hx('#7a7e82'))
    d.line([(15, 3), (13, 9), (17, 14), (14, 22)], fill=hx('#4a4a4a'))                 # halkeama
    d.rectangle([23, 20, 26, 27], fill=hx('#c8ced6')); d.rectangle([23, 22, 26, 25], fill=hx('#2f6fb0'))   # tölkki
    outline(im)
    d.line([(20, 1), (30, 11)], fill=hx('#ff2a2a'), width=2); d.line([(30, 1), (20, 11)], fill=hx('#ff2a2a'), width=2)
    return im
def ik_pihakirppis():
    im = kirppis(); d = ImageDraw.Draw(im); return im
def ik_saunailta():
    im, d = canvas()
    d.rectangle([7, 16, 21, 27], fill=hx('#b07a44')); d.line([(7, 19), (21, 19)], fill=hx('#7a5030')); d.line([(7, 25), (21, 25)], fill=hx('#7a5030'))
    d.ellipse([7, 14, 21, 18], fill=hx('#5a8ab0')); d.line([(18, 4), (24, 15)], fill=hx('#8a5a30'), width=2); d.ellipse([22, 13, 28, 18], fill=hx('#8a5a30'))
    outline(im)
    return layer(im, lambda l: [l.ellipse([x-r, y-r, x+r, y+r], fill=(240, 242, 246, 150)) for (x, y, r) in ((10, 8, 4), (14, 4, 3), (5, 5, 2))])
def ik_taloyhtion_kokous():
    im, d = canvas()
    d.rectangle([3, 10, 20, 28], fill=hx('#b8b4aa')); d.rectangle([3, 8, 20, 10], fill=hx('#5a5c60'))
    for yy in (12, 17, 22):
        for x in (5, 10, 15): d.rectangle([x, yy, x+2, yy+2], fill=hx('#2b3a4a'))
    d.rectangle([10, 22, 12, 28], fill=hx('#3a2c20')); d.point((15, 12), fill=hx('#e8d27a'))
    d.rectangle([16, 1, 30, 10], fill=WHITE); d.polygon([(19, 10), (22, 10), (18, 14)], fill=WHITE)
    for x in (19, 23, 27): d.rectangle([x, 5, x+1, 6], fill=OUT)
    return outline(im)
def ik_bussi_myohassa():
    im, d = canvas()
    d.rectangle([2, 10, 24, 25], fill=hx('#e8ecee')); d.rectangle([2, 19, 24, 20], fill=hx('#1a8a8a'))
    for x in (4, 10): d.rectangle([x, 12, x+4, 16], fill=hx('#2a3a4a'))
    d.polygon([(17, 12), (22, 12), (24, 17), (17, 17)], fill=hx('#6f9fbf'))
    d.rectangle([17, 7, 23, 11], fill=hx('#141414')); text(d, 19, 7, '3', hx('#ffb020'))
    for cx in (7, 19): d.ellipse([cx-3, 23, cx+3, 29], fill=hx('#1c1c1c')); d.point((cx, 26), fill=hx('#8a8e92'))
    d.ellipse([18, 0, 31, 13], fill=WHITE, outline=hx('#e02a2a')); d.line([(24, 2), (24, 6)], fill=OUT); d.line([(24, 6), (28, 8)], fill=OUT)
    return outline(im)
def ik_kesajuhlat():
    im, d = canvas()
    d.ellipse([18, 1, 29, 12], fill=hx('#ffd23a')); d.ellipse([20, 3, 25, 8], fill=hx('#fff08a'))
    pts = [(1 + i, 13 + round(5 * math.sin(math.pi * i / 29))) for i in range(30)]
    d.line(pts, fill=hx('#d8d8d8'))
    flagc = [hx('#d8262b'), hx('#f0d020'), hx('#1f6fe0'), hx('#3aa03a'), hx('#e070c0'), hx('#ff8a1a'), hx('#d8262b')]
    for j, i in enumerate(range(2, 29, 4)):
        x, y = pts[i]; d.polygon([(x, y+1), (x+3, y+1), (x+1, y+6)], fill=flagc[j])
    d.rectangle([8, 23, 12, 28], fill=hx('#c8ced6')); d.rectangle([8, 25, 12, 26], fill=hx('#d8262b'))
    d.rectangle([18, 23, 22, 28], fill=hx('#c8ced6')); d.rectangle([18, 25, 22, 26], fill=hx('#1f6fe0'))
    text(d, 13, 23, '!', hx('#ffd23a'))
    return outline(im)

# =====================================================================
# UI-IKONIT 24x24 (rajattu natiivispritestä, ajoneuvot pienennetty 2:1 "moodi"-otannalla)
# =====================================================================
def downscale2(im):
    w, h = im.size; src = im.load(); out = Image.new('RGBA', (w // 2, h // 2), CLEAR); px = out.load()
    for y in range(h // 2):
        for x in range(w // 2):
            cs = [src[2*x+i, 2*y+j] for j in (0, 1) for i in (0, 1)]
            op = [c for c in cs if c[3] == 255 and c != OUT]
            if len([c for c in cs if c[3] == 255]) >= 2 and op:
                px[x, y] = max(set(op), key=op.count) if len(set(op)) < 4 else op[1 if len(op) > 1 else 0]
    return outline(out)
def ui_icon(sprite, vehicle=False):
    im = no_shadow(sprite.copy())
    if vehicle:
        # leikkaa savut ym. puoliläpinäkyvät pois ennen pienennystä
        px = im.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                if px[x, y][3] < 255: px[x, y] = CLEAR
        im = downscale2(im)
    bb = im.getbbox(); im = im.crop(bb); w, h = im.size
    if w > 24: im = im.crop(((w - 24) // 2, 0, (w - 24) // 2 + 24, h)); w = 24
    if h > 23: im = im.crop((0, 0, w, 23)); h = 23
    out = Image.new('RGBA', (24, 24), CLEAR); out.alpha_composite(im, ((24 - w) // 2, (24 - h) // 2 if h < 22 else 1))
    return out

# =====================================================================
UNITS = {'tolkkijussi': tolkkijussi, 'lahiojermu': lahiojermu, 'mopopoika': mopopoika,
         'parvekeampuja': parvekeampuja, 'mummo': mummo, 'isa_trimmeri': isa_trimmeri, 'grillimestari': grillimestari}
NEW_UNITS = ['parvekeampuja', 'mummo', 'isa_trimmeri', 'grillimestari']
ATTACK_UNITS = ['lahiojermu', 'mopopoika', 'parvekeampuja', 'mummo', 'isa_trimmeri', 'grillimestari']
VEHICLES = {'dnepr': dnepr, 'monkija': monkija, 'lada': lada, 'volvo': volvo}
ATTACK_VEHICLES = ['dnepr', 'monkija']
ALIAKSET = {'alkon_alennus': 'alkon_ale', 'panttiautomaatti_rikki': 'automaatti_rikki', 'bussi3_myohassa': 'bussi_myohassa'}

def main():
    made = []
    def save(im, rel): im.save(f'{D}/{rel}'); made.append(rel)
    # --- yksiköt ---
    for n, fn in UNITS.items():
        for tn, tc in TEAMS.items():
            frames = [fn(tc, f, 'kavely') for f in range(4)]
            if n in NEW_UNITS: save(frames[0], f'yksikot/{n}_{tn}.png')
            else:   # vanhat: kehys 0 == nykyinen staattinen kuva (pikselintarkka)
                ref = Image.open(f'{D}/yksikot/{n}_{tn}.png').convert('RGBA')
                assert ref.tobytes() == frames[0].tobytes(), f'{n}_{tn}: kehys 0 poikkeaa staattisesta'
            save(strip(frames), f'yksikot/{n}_{tn}_kavely.png')
            if n in ATTACK_UNITS: save(strip([fn(tc, f, 'ampuu') for f in range(2)]), f'yksikot/{n}_{tn}_ampuu.png')
            save(sammunut(tc, n), f'yksikot/{n}_{tn}_sammunut.png')
            save(ui_icon(frames[0]), f'ikonit/ui_{n}.png' if tn == 'sininen' else f'ikonit/ui_{n}_punainen.png')
    # --- ajoneuvot ---
    for n, fn in VEHICLES.items():
        for tn, tc in TEAMS.items():
            frames = [fn(tc, f, 'kavely') for f in range(4)]
            save(frames[0], f'ajoneuvot/{n}_{tn}.png'); save(strip(frames), f'ajoneuvot/{n}_{tn}_kavely.png')
            if n in ATTACK_VEHICLES: save(strip([fn(tc, f, 'ampuu') for f in range(2)]), f'ajoneuvot/{n}_{tn}_ampuu.png')
            save(ui_icon(frames[0], vehicle=True), f'ikonit/ui_{n}.png' if tn == 'sininen' else f'ikonit/ui_{n}_punainen.png')
    pf = [poliisiauto(f) for f in range(4)]
    save(pf[0], 'ajoneuvot/poliisiauto.png'); save(strip(pf), 'ajoneuvot/poliisiauto_kavely.png')
    # --- efektit ---
    save(suuliekki(), 'efektit/suuliekki_8.png'); save(rajahdys(), 'efektit/rajahdys_64.png')
    save(molotovi(), 'efektit/molotovi_16.png'); save(tuli(), 'efektit/tuli_32.png'); save(sade(), 'efektit/sade_64.png')
    save(makkara(), 'efektit/makkara_8.png'); save(kary(), 'efektit/kary_32.png'); save(zzz16(), 'efektit/zzz_16.png')
    save(kirppis(), 'efektit/kirppis_tolkkikasa_32.png'); save(sauna(), 'efektit/sauna_32.png'); save(kesajuhlat(), 'efektit/kesajuhlat_32.png')
    # --- tapahtumat ---
    save(alko(), 'rakennukset/alko.png'); save(bussi3(), 'rakennukset/bussi3.png')
    for n, fn in [('poliisipartio', ik_poliisipartio), ('alkon_ale', ik_alkon_ale), ('sadekuuro', ik_sadekuuro),
                  ('automaatti_rikki', ik_automaatti_rikki), ('pihakirppis', ik_pihakirppis), ('saunailta', ik_saunailta),
                  ('taloyhtion_kokous', ik_taloyhtion_kokous), ('bussi_myohassa', ik_bussi_myohassa), ('kesajuhlat', ik_kesajuhlat)]:
        save(fn(), f'ikonit/tapahtuma_{n}.png')
    # aliakset koodi/game.js:n TAPAHTUMAT-avaimille (sama kuva, eri nimi), jotta koodi voi käyttää `tapahtuma_${avain}`
    for alias, src in ALIAKSET.items():
        save(Image.open(f'{D}/ikonit/tapahtuma_{src}.png'), f'ikonit/tapahtuma_{alias}.png')
    preview()
    print(len(made), 'tiedostoa'); return made

# ---------------- esikatselut (3x NEAREST) ----------------
S = 3; BG = hx('#22252a'); CELL = hx('#2e3238'); FNT = ImageFont.load_default()
def big(im): return im.resize((im.size[0] * S, im.size[1] * S), Image.NEAREST)
def put(pv, d, im, x, y, fw=None):
    """Liitä 3x; piirrä kehysten rajat (fw = kehyksen leveys natiivina)."""
    b = big(im); fw = fw or im.size[0]
    for i in range(im.size[0] // fw): d.rectangle([x + i*fw*S, y, x + (i+1)*fw*S - 1, y + b.size[1] - 1], fill=CELL, outline=hx('#3c4048'))
    pv.alpha_composite(b, (x, y)); return x + b.size[0] + 10

def preview():
    # yksiköt
    rows = []
    for n in UNITS:
        for tn in TEAMS:
            r = [(f'yksikot/{n}_{tn}.png', 32), (f'yksikot/{n}_{tn}_kavely.png', 32)]
            if n in ATTACK_UNITS: r.append((f'yksikot/{n}_{tn}_ampuu.png', 32))
            r.append((f'yksikot/{n}_{tn}_sammunut.png', 32)); r.append((f'ikonit/ui_{n}{"" if tn == "sininen" else "_punainen"}.png', 24))
            rows.append((f'{n}_{tn}', r, 32))
    for n in VEHICLES:
        for tn in TEAMS:
            r = [(f'ajoneuvot/{n}_{tn}.png', 48), (f'ajoneuvot/{n}_{tn}_kavely.png', 48)]
            if n in ATTACK_VEHICLES: r.append((f'ajoneuvot/{n}_{tn}_ampuu.png', 48))
            r.append((f'ikonit/ui_{n}{"" if tn == "sininen" else "_punainen"}.png', 24))
            rows.append((f'{n}_{tn}', r, 32))
    rows.append(('poliisiauto', [('ajoneuvot/poliisiauto.png', 48), ('ajoneuvot/poliisiauto_kavely.png', 48)], 32))
    rows.append(('bussi3', [('rakennukset/bussi3.png', 64)], 32))
    W = 0
    for _, r, _ in rows: W = max(W, 150 + sum(Image.open(f'{D}/{p}').size[0] * S + 10 for p, _ in r))
    H = 10 + len(rows) * (32 * S + 8)
    pv = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(pv); y = 10
    for name, r, _ in rows:
        d.text((8, y + 40), name, fill=(220, 220, 220, 255), font=FNT); x = 150
        for p, fw in r: x = put(pv, d, Image.open(f'{D}/{p}').convert('RGBA'), x, y, fw)
        y += 32 * S + 8
    pv.save(f'{D}/esikatselu_v2_yksikot.png')
    # efektit, tapahtumat, ikonit
    groups = [
        ('efektit', [('efektit/suuliekki_8.png', 8), ('efektit/makkara_8.png', 8), ('efektit/molotovi_16.png', 16), ('efektit/zzz_16.png', 16),
                     ('efektit/kary_32.png', 32), ('efektit/kirppis_tolkkikasa_32.png', 32), ('efektit/sauna_32.png', 32), ('efektit/kesajuhlat_32.png', 32)]),
        ('tuli / sade', [('efektit/tuli_32.png', 32), ('efektit/sade_64.png', 64), ('SADE2x2', 128)]),
        ('rajahdys', [('efektit/rajahdys_64.png', 64)]),
        ('rakennukset', [('rakennukset/alko.png', 64), ('rakennukset/bussi3.png', 64), ('ajoneuvot/poliisiauto_kavely.png', 48)]),
        ('tapahtumaikonit', [(f'ikonit/tapahtuma_{n}.png', 32) for n in ['poliisipartio', 'alkon_ale', 'sadekuuro', 'automaatti_rikki', 'pihakirppis', 'saunailta', 'taloyhtion_kokous', 'bussi_myohassa', 'kesajuhlat']]),
        ('ui sininen', [(f'ikonit/ui_{n}.png', 24) for n in list(UNITS) + list(VEHICLES)]),
        ('ui punainen', [(f'ikonit/ui_{n}_punainen.png', 24) for n in list(UNITS) + list(VEHICLES)]),
    ]
    def load(p):
        if p == 'SADE2x2':   # tiilityksen tarkistus 2x2 ruohon päällä
            g = Image.open(f'{D}/maasto/00_ruoho.png').convert('RGBA'); t = Image.new('RGBA', (128, 128))
            for i in range(4): t.paste(g, ((i % 4) * 32, 0))
            for yy in range(0, 128, 32):
                for xx in range(0, 128, 32): t.paste(g, (xx, yy))
            s = Image.open(f'{D}/efektit/sade_64.png')
            for yy in (0, 64):
                for xx in (0, 64): t.alpha_composite(s, (xx, yy))
            return t
        return Image.open(f'{D}/{p}').convert('RGBA')
    W = max(150 + sum(load(p).size[0] * S + 10 for p, _ in r) for _, r in groups)
    H = 10 + sum(max(load(p).size[1] for p, _ in r) * S + 12 for _, r in groups)
    pv = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(pv); y = 10
    for name, r in groups:
        hh = max(load(p).size[1] for p, _ in r) * S
        d.text((8, y + hh // 2 - 5), name, fill=(220, 220, 220, 255), font=FNT); x = 150
        for p, fw in r: x = put(pv, d, load(p), x, y, fw)
        y += hh + 12
    pv.save(f'{D}/esikatselu_v2_efektit.png')

if __name__ == '__main__':
    main()
