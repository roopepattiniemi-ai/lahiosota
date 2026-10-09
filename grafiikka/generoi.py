# Lähiösota: Etelä-Tampere – proseduraalinen pikselitaide (Grafiikkabotti)
# Ajo: python3 generoi.py  -> kirjoittaa PNG:t tämän kansion alikansioihin
import random, os
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__))
T = 32
def hx(h, a=255):
    h = h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a)
def shade(c, f):
    return tuple(max(0,min(255,int(v*f))) for v in c[:3]) + (c[3],)
OUT = hx('#1a1a1a')
TEAMS = {'sininen': hx('#1f6fe0'), 'punainen': hx('#d8262b')}

def outline(im, col=OUT):
    px = im.load(); w,h = im.size; add=[]
    for y in range(h):
        for x in range(w):
            if px[x,y][3]==0:
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx,ny=x+dx,y+dy
                    if 0<=nx<w and 0<=ny<h and px[nx,ny][3]>0 and px[nx,ny]!=SHADOW:
                        add.append((x,y)); break
    for p in add: px[p]=col
    return im
SHADOW = (0,0,0,90)
def shadow(d, cx, cy, rx, ry):
    d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=SHADOW)

def noise_tile(base, var, seed, dots=None):
    r = random.Random(seed); im = Image.new('RGBA',(T,T),base); px=im.load()
    for y in range(T):
        for x in range(T):
            f = 1 + r.uniform(-var,var); px[x,y]=shade(base,f)
    if dots:
        for col,n in dots:
            for _ in range(n): px[r.randrange(T),r.randrange(T)] = col
    return im

# ---------------- MAASTO ----------------
def maasto():
    t = {}
    g = hx('#4f7a2e')
    t['ruoho'] = noise_tile(g,.08,1,[(hx('#3d6123'),40),(hx('#6b9640'),30),(hx('#c9c27a'),3)])
    m = noise_tile(hx('#3d5f24'),.08,2,[(hx('#2f4a1c'),40)]); d=ImageDraw.Draw(m)
    for (x,y) in [(8,10),(22,8),(14,22),(27,24),(4,27)]:
        d.polygon([(x,y-7),(x-5,y+3),(x+5,y+3)],fill=hx('#1d3b1a')); d.polygon([(x,y-5),(x-3,y+1),(x+3,y+1)],fill=hx('#2c5426'))
        d.point((x,y+4),fill=hx('#4a3220'))
    t['metsa']=m
    v = noise_tile(hx('#2d5a86'),.05,3); d=ImageDraw.Draw(v); r=random.Random(3)
    for _ in range(6):
        x,y=r.randrange(2,26),r.randrange(2,30); d.line([(x,y),(x+4,y)],fill=hx('#5f8fbf'))
    t['vesi']=v
    a = noise_tile(hx('#55575a'),.06,4,[(hx('#6a6c6f'),30),(hx('#45474a'),30)]); t['tie']=a
    mt = noise_tile(hx('#3f4144'),.05,5); d=ImageDraw.Draw(mt)
    for x in range(0,T,8): d.line([(x,15),(x+3,15)],fill=hx('#d9d9d0'))
    d.line([(0,1),(T,1)],fill=hx('#c9b23a')); d.line([(0,30),(T,30)],fill=hx('#c9b23a'))
    d.line([(0,0),(T,0)],fill=hx('#8a8c8f')); d.line([(0,31),(T,31)],fill=hx('#8a8c8f')); t['moottoritie']=mt
    rt = noise_tile(hx('#6b5d4b'),.1,6,[(hx('#8a8a8a'),60)]); d=ImageDraw.Draw(rt)
    for y in range(1,T,5): d.line([(6,y),(25,y)],fill=hx('#4a3523')); d.line([(6,y+1),(25,y+1)],fill=hx('#3a2a1c'))
    d.line([(10,0),(10,T)],fill=hx('#b5b8bc')); d.line([(21,0),(21,T)],fill=hx('#b5b8bc')); t['rata']=rt
    # rakennus: kerrostalon katto ylhäältä
    rk = Image.new('RGBA',(T,T),hx('#4f7a2e')); d=ImageDraw.Draw(rk)
    d.rectangle([1,1,30,30],fill=hx('#5a5c60')); d.rectangle([1,1,30,30],outline=hx('#8b8e93'))
    d.rectangle([2,2,29,29],outline=hx('#3c3e41'))
    r=random.Random(7)
    for (x,y) in [(6,6),(20,9),(12,20)]: d.rectangle([x,y,x+3,y+2],fill=hx('#9a9da1')); d.line([(x,y+3),(x+3,y+3)],fill=hx('#2c2d30'))
    d.line([(24,18),(24,25)],fill=hx('#2c2d30')); d.line([(22,20),(26,20)],fill=hx('#2c2d30'))
    t['rakennus']=rk
    te = noise_tile(hx('#6e6b66'),.06,8,[(hx('#5a5752'),40),(hx('#7f7c76'),20)]); d=ImageDraw.Draw(te)
    d.line([(0,10),(12,10)],fill=hx('#c9c27a')); d.line([(18,24),(31,24)],fill=hx('#c9c27a')); t['teollisuus']=te
    p = noise_tile(hx('#8e9a45'),.06,9); d=ImageDraw.Draw(p)
    for y in range(2,T,4): d.line([(0,y),(T,y)],fill=hx('#76803a'))
    t['pelto']=p
    s = noise_tile(hx('#56603a'),.1,10,[(hx('#3f5a4f'),60),(hx('#8a7d4a'),20)]); d=ImageDraw.Draw(s)
    for (x,y) in [(6,8),(20,18),(10,25)]: d.ellipse([x,y,x+6,y+3],fill=hx('#2f4d5a'))
    t['suo']=s
    k = noise_tile(hx('#7d7b77'),.1,11,[(hx('#5c5a56'),50),(hx('#a3a19c'),30),(hx('#4f7a2e'),25)]); t['kallio']=k
    pu = noise_tile(hx('#5d8c36'),.06,12,[(hx('#79a84a'),40)]); d=ImageDraw.Draw(pu)
    d.line([(0,22),(31,14)],fill=hx('#b8a982')); d.line([(0,23),(31,15)],fill=hx('#a39572'))
    d.point([(5,5),(25,6),(14,27)],fill=hx('#e8e05a')); t['puisto']=pu
    si = Image.new('RGBA',(T,T),hx('#2d5a86')); d=ImageDraw.Draw(si)
    d.rectangle([0,4,31,27],fill=hx('#8d8f92')); d.rectangle([0,7,31,24],fill=hx('#55575a'))
    for x in range(0,T,4): d.point((x,4),fill=hx('#3c3e41')); d.point((x,27),fill=hx('#3c3e41'))
    d.line([(0,28),(31,28)],fill=hx('#1f3e5c')); t['silta']=si
    order=['ruoho','metsa','vesi','tie','moottoritie','rata','rakennus','teollisuus','pelto','suo','kallio','puisto','silta']
    for i,k in enumerate(order): t[k].save(f'{D}/maasto/{i:02d}_{k}.png')
    sheet=Image.new('RGBA',(T*len(order),T))
    for i,k in enumerate(order): sheet.paste(t[k],(i*T,0))
    sheet.save(f'{D}/maasto/maasto_tileset.png')
    return order

# ---------------- YKSIKÖT ----------------
SKIN=hx('#e0b08a'); SKIN_D=hx('#b88663'); PANTS=hx('#2b2f3a'); BOOT=hx('#1c1c1c')
def person(d, team, cx=16, top=6, hat='pipo', walk=0):
    tc=team; tl=shade(tc,1.3); td=shade(tc,.65)
    shadow(d, cx, 28, 7, 2)
    # jalat
    d.rectangle([cx-3,20,cx-1,26+(-walk)],fill=PANTS); d.rectangle([cx+1,20,cx+3,26+walk],fill=PANTS)
    d.rectangle([cx-3,26-walk,cx-1,27-walk],fill=BOOT); d.rectangle([cx+1,26+walk,cx+3,27+walk],fill=BOOT)
    # takki
    d.rectangle([cx-4,top+7,cx+4,20],fill=tc); d.line([(cx-4,top+7),(cx-4,20)],fill=tl); d.line([(cx+4,top+7),(cx+4,20)],fill=td)
    d.line([(cx,top+8),(cx,20)],fill=td)
    # pää
    d.rectangle([cx-2,top+2,cx+2,top+6],fill=SKIN); d.point([(cx-1,top+4),(cx+1,top+4)],fill=OUT)
    d.line([(cx-2,top+6),(cx+2,top+6)],fill=SKIN_D)
    if hat=='pipo': d.rectangle([cx-3,top,cx+3,top+2],fill=td); d.point((cx,top-1),fill=tl)
    elif hat=='lippis': d.rectangle([cx-3,top,cx+2,top+2],fill=hx('#2a2a2a')); d.line([(cx+2,top+2),(cx+4,top+2)],fill=hx('#2a2a2a'))
    elif hat=='kypara': d.rectangle([cx-3,top-1,cx+3,top+2],fill=td); d.line([(cx-3,top-1),(cx+3,top-1)],fill=tl)

def bag(d,x,y):
    d.rectangle([x,y,x+4,y+5],fill=hx('#dfe3ea')); d.line([(x+1,y-1),(x+3,y-1)],fill=hx('#dfe3ea'))
    d.point([(x+1,y+2),(x+3,y+3)],fill=hx('#c4a43a')); d.point((x+2,y+1),fill=hx('#9aa3b0'))

def tolkkijussi(team):
    im=Image.new('RGBA',(T,T),(0,0,0,0)); d=ImageDraw.Draw(im)
    person(d,team,hat='pipo'); bag(d,6,18); bag(d,21,18)
    d.rectangle([11,15,12,19],fill=SKIN); d.rectangle([20,15,21,19],fill=SKIN)
    return outline(im)
def lahiojermu(team):
    im=Image.new('RGBA',(T,T),(0,0,0,0)); d=ImageDraw.Draw(im)
    person(d,team,hat='kypara')
    # RK-62 vinottain
    d.line([(8,20),(24,11)],fill=hx('#2a2a2a'),width=2); d.line([(22,12),(27,9)],fill=hx('#3a3a3a'))
    d.rectangle([7,19,10,21],fill=hx('#6b4a2b')); d.point((15,17),fill=hx('#6b4a2b'))
    d.rectangle([17,14,18,18],fill=hx('#3a3a3a'))
    d.rectangle([11,15,12,17],fill=SKIN); d.rectangle([19,13,20,15],fill=SKIN)
    return outline(im)
def mopopoika(team):
    im=Image.new('RGBA',(T,T),(0,0,0,0)); d=ImageDraw.Draw(im)
    tc=team; td=shade(tc,.65); tl=shade(tc,1.3)
    shadow(d,16,28,12,2)
    # renkaat
    for x in (7,24): d.ellipse([x-4,21,x+4,29],fill=hx('#1c1c1c')); d.ellipse([x-1,24,x+1,26],fill=hx('#9a9a9a'))
    # runko
    d.polygon([(9,22),(22,22),(25,18),(20,17),(12,19)],fill=tc); d.line([(9,22),(22,22)],fill=td)
    d.line([(12,19),(20,17)],fill=tl); d.rectangle([5,18,13,20],fill=hx('#2a2a2a'))  # penkki
    d.line([(24,18),(25,12)],fill=hx('#555555')); d.line([(23,12),(27,12)],fill=hx('#2a2a2a'))
    d.point((27,15),fill=hx('#ffe680'))
    # kuski
    d.rectangle([10,11,15,18],fill=hx('#3a3a40')); d.line([(15,13),(23,12)],fill=hx('#3a3a40'),width=2)
    d.rectangle([13,18,17,21],fill=PANTS)
    d.ellipse([10,4,16,10],fill=td); d.line([(11,5),(14,5)],fill=tl); d.rectangle([14,7,16,9],fill=hx('#9fc6e0'))
    return outline(im)

# ---------------- RAKENNUKSET (64x64, viisto ylänäkymä) ----------------
B=64
def building(wall, roof, h=22, w=56, depth=26):
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im)
    x0=(B-w)//2; y_roof=B-6-h-depth; y_wall=y_roof+depth
    d.rectangle([x0+3,y_wall+h-1,x0+w+2,y_wall+h+3],fill=SHADOW)
    d.rectangle([x0,y_roof,x0+w-1,y_wall-1],fill=roof)
    d.rectangle([x0,y_roof,x0+w-1,y_wall-1],outline=shade(roof,1.25))
    d.rectangle([x0,y_wall,x0+w-1,y_wall+h-1],fill=wall)
    d.line([(x0,y_wall),(x0+w-1,y_wall)],fill=shade(wall,.6))
    return im,d,x0,y_roof,y_wall,w,h
def windows(d,x0,y,w,rows,cols,col=hx('#2b3a4a'),lit=hx('#e8d27a'),seed=0,start=4,step_y=6):
    r=random.Random(seed); gap=(w-8)//cols
    for j in range(rows):
        for i in range(cols):
            x=x0+start+i*gap; yy=y+3+j*step_y
            d.rectangle([x,yy,x+2,yy+2],fill=lit if r.random()<.2 else col)
def paamaja(team):
    im,d,x0,yr,yw,w,h=building(hx('#9a948a'),hx('#4e5054'))
    tc=team; td=shade(tc,.65)
    windows(d,x0,yw,w,2,8,seed=1)
    d.rectangle([x0+23,yw+11,x0+32,yw+h-1],fill=hx('#3a2c20')); d.rectangle([x0+22,yw+9,x0+33,yw+10],fill=tc)
    # hiekkasäkit
    for i in range(6): d.ellipse([x0+2+i*5,yw+h-2,x0+7+i*5,yw+h+2],fill=hx('#b8a06a'),outline=hx('#7a6640'))
    # lippu katolla
    d.line([(x0+8,yr-10),(x0+8,yr+8)],fill=hx('#cccccc')); d.rectangle([x0+9,yr-10,x0+18,yr-4],fill=tc)
    d.line([(x0+9,yr-4),(x0+18,yr-4)],fill=td)
    # katolla tutka-antenni ja raita
    d.rectangle([x0+30,yr+6,x0+44,yr+18],fill=td); d.rectangle([x0+31,yr+7,x0+43,yr+17],fill=tc)
    d.ellipse([x0+34,yr+9,x0+40,yr+15],fill=hx('#e6e6e6')); d.point((x0+37,yr+12),fill=OUT)
    return outline(im)
def kmarket():
    im,d,x0,yr,yw,w,h=building(hx('#c9c4b8'),hx('#5e6064'),h=20)
    gr=hx('#1f8a3a'); wh=hx('#f0f0ea')
    # isot ikkunat
    for i in range(4): d.rectangle([x0+4+i*13,yw+9,x0+13+i*13,yw+h-2],fill=hx('#6f9fbf')); d.line([(x0+5+i*13,yw+10),(x0+8+i*13,yw+10)],fill=hx('#d8ecf8'))
    # raidallinen markiisi
    for i in range(0,w,4): d.rectangle([x0+i,yw+3,x0+i+1,yw+7],fill=gr); d.rectangle([x0+i+2,yw+3,x0+i+3,yw+7],fill=wh)
    d.line([(x0,yw+8),(x0+w-1,yw+8)],fill=shade(gr,.6))
    # kyltti katon reunalla: tölkki + nuoli (ei brändilogoa)
    d.rectangle([x0+16,yr+14,x0+39,yr+24],fill=gr,outline=shade(gr,.6))
    d.rectangle([x0+19,yr+16,x0+22,yr+22],fill=hx('#d9dde3')); d.line([(x0+19,yr+16),(x0+22,yr+16)],fill=hx('#9aa3b0'))
    d.line([(x0+25,yr+19),(x0+35,yr+19)],fill=wh); d.polygon([(x0+35,yr+16),(x0+37,yr+19),(x0+35,yr+22)],fill=wh)
    # ostoskärryt
    d.rectangle([x0+w-8,yw+h,x0+w-3,yw+h+3],outline=hx('#b0b0b0'))
    return outline(im)
def baari():
    im,d,x0,yr,yw,w,h=building(hx('#7a4a2e'),hx('#3e3530'),h=22,w=50)
    # puupaneeli
    for y in range(yw+2,yw+h,3): d.line([(x0,y),(x0+w-1,y)],fill=hx('#6a3f26'))
    d.rectangle([x0+19,yw+9,x0+28,yw+h-1],fill=hx('#2a1a10')); d.point((x0+27,yw+15),fill=hx('#d8b04a'))
    for x in (x0+4,x0+34): d.rectangle([x,yw+8,x+10,yw+15],fill=hx('#e8b44a')); d.line([(x+5,yw+8),(x+5,yw+15)],fill=hx('#5a3520'))
    # kyltti: kaljatuoppi
    d.rectangle([x0+14,yr+8,x0+35,yr+22],fill=hx('#2a1a10'),outline=hx('#d8b04a'))
    d.rectangle([x0+21,yr+11,x0+27,yr+19],fill=hx('#e8a830')); d.rectangle([x0+21,yr+10,x0+27,yr+12],fill=hx('#fff4d8'))
    d.rectangle([x0+28,yr+13,x0+29,yr+17],outline=hx('#e8a830'))
    # tölkkejä ja kalja­kori
    d.rectangle([x0+w-6,yw+h-4,x0+w+1,yw+h+1],fill=hx('#d8b030'),outline=hx('#8a6a10'))
    return outline(im)

# ---------------- IKONIT ----------------
def tolkki(size):
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([5,2,10,13],fill=hx('#c8ced6')); d.line([(5,2),(5,13)],fill=hx('#eef2f6')); d.line([(10,2),(10,13)],fill=hx('#8a929c'))
    d.rectangle([5,6,10,10],fill=hx('#2f6fb0')); d.line([(6,7),(8,7)],fill=hx('#e8d27a'))
    d.line([(6,1),(9,1)],fill=hx('#9aa3b0')); d.point((7,1),fill=hx('#5a626c'))
    outline(im)
    return im if size==16 else im.resize((size,size),Image.NEAREST)

if __name__=='__main__':
    order=maasto()
    units={'tolkkijussi':tolkkijussi,'lahiojermu':lahiojermu,'mopopoika':mopopoika}
    for n,f in units.items():
        for tn,tc in TEAMS.items(): f(tc).save(f'{D}/yksikot/{n}_{tn}.png')
    for tn,tc in TEAMS.items(): paamaja(tc).save(f'{D}/rakennukset/paamaja_{tn}.png')
    kmarket().save(f'{D}/rakennukset/kmarket.png'); baari().save(f'{D}/rakennukset/baari.png')
    tolkki(16).save(f'{D}/ikonit/tolkki_16.png'); tolkki(32).save(f'{D}/ikonit/tolkki_32.png')
    # esikatselu 4x suurennoksella
    S=4; pv=Image.new('RGBA',(13*T*S//2+90, 420),hx('#22252a'))
    for i,k in enumerate(order):
        im=Image.open(f'{D}/maasto/{i:02d}_{k}.png').resize((T*S//2,T*S//2),Image.NEAREST); pv.paste(im,(10+i*T*S//2,10))
    x=10
    for n in units:
        for tn in TEAMS:
            im=Image.open(f'{D}/yksikot/{n}_{tn}.png').resize((T*3,T*3),Image.NEAREST); pv.alpha_composite(im,(x,90)); x+=T*3+8
    x=10
    for f in ['paamaja_sininen','paamaja_punainen','kmarket','baari']:
        im=Image.open(f'{D}/rakennukset/{f}.png').resize((B*3,B*3),Image.NEAREST); pv.alpha_composite(im,(x,200)); x+=B*3+8
    pv.alpha_composite(Image.open(f'{D}/ikonit/tolkki_32.png').resize((64,64),Image.NEAREST),(x,260))
    pv.save(f'{D}/esikatselu.png'); print('ok', pv.size)
