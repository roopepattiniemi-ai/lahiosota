# Laattalättä-efekti (Grafiikkabotti). Ajo: python3 laatta.py
import random, math
from generoi import *
COLS=[hx('#9aa83a'),hx('#b8b848'),hx('#7d8a2a'),hx('#c9a84a'),hx('#5f6a1e')]
def blob(size, phase, seed=1):
    # phase 1 = tuore, 2 = puoliksi haihtunut, 3 = melkein kuivunut
    r=random.Random(seed); im=Image.new('RGBA',(size,size),(0,0,0,0)); px=im.load()
    c=size/2; base=size*0.34*(1,0.8,0.6)[phase-1]; alpha=(230,185,130)[phase-1]
    lobes=[(r.uniform(0,6.28),r.uniform(.05,.14),r.randint(2,5)) for _ in range(4)]
    for y in range(size):
        for x in range(size):
            dx,dy=x-c+.5,(y-c+.5)*1.35; dist=math.hypot(dx,dy); a=math.atan2(dy,dx)
            rad=base*(1+sum(m*math.sin(k*a+p) for p,m,k in lobes))
            if dist<rad:
                edge=dist>rad-2
                col=COLS[4] if edge else COLS[r.choice([0,0,0,1,2,3])]
                if phase==3 and r.random()<.35: continue
                px[x,y]=col[:3]+(alpha,)
    d=ImageDraw.Draw(im)
    # paloja ja kuplia
    for _ in range((10,6,3)[phase-1]):
        x,y=r.randint(int(c-base*.6),int(c+base*.6)),r.randint(int(c-base*.45),int(c+base*.45))
        if px[x,y][3]>0: d.rectangle([x,y,x+1,y+1],fill=hx('#e8d27a')[:3]+(alpha,))
    for _ in range((5,3,0)[phase-1]):
        x,y=r.randint(int(c-base*.5),int(c+base*.5)),r.randint(int(c-base*.4),int(c+base*.4))
        if px[x,y][3]>0: d.point((x,y),fill=(240,250,200,alpha)); d.point((x+1,y-1),fill=(255,255,255,alpha))
    return im
def tile(phase, seed=7):
    r=random.Random(seed); T=32; alpha=(200,150,100)[phase-1]
    im=Image.new('RGBA',(T,T),(0,0,0,0)); px=im.load()
    dens=(.85,.6,.35)[phase-1]
    # saumaton kohina: periodinen sin-summa
    ph=[r.uniform(0,6.28) for _ in range(6)]
    for y in range(T):
        for x in range(T):
            v=(math.sin(2*math.pi*x/T*1+ph[0])+math.sin(2*math.pi*y/T*1+ph[1])+.6*math.sin(2*math.pi*(x+y)/T*2+ph[2])+.5*math.sin(2*math.pi*(x-y)/T*3+ph[3]))
            if v>(1-dens*2.4):
                px[x,y]=r.choice(COLS[:4])[:3]+(alpha,)
    return im
def hoyry(seed=3):
    # 4 kehystä: nouseva vihreä höyry + 3 kärpästä
    r=random.Random(seed); sheet=Image.new('RGBA',(128,32),(0,0,0,0))
    flies=[(r.uniform(0,6.28),r.uniform(6,10),r.uniform(3,6)) for _ in range(3)]
    for f in range(4):
        im=Image.new('RGBA',(32,32),(0,0,0,0)); d=ImageDraw.Draw(im)
        for i,x0 in enumerate((10,16,22)):
            y=26-((f*5+i*7)%20); a=max(70,210-(26-y)*7); x=x0+int(2*math.sin((f+i)*1.6))
            d.ellipse([x-2,y-2,x+2,y+2],fill=(150,190,60,a)); d.point((x,y-1),fill=(220,235,170,a))
        for (p,rx,ry) in flies:
            t=p+f*1.57; x=16+int(rx*math.cos(t)); y=12+int(ry*math.sin(2*t))
            d.point((x,y),fill=(20,20,20,255)); d.point((x+1,y),fill=(20,20,20,255))
            d.point((x,y-1),fill=(200,220,240,200)) if f%2==0 else d.point((x+1,y-1),fill=(200,220,240,200))
        sheet.alpha_composite(im,(f*32,0))
    return sheet
if __name__=='__main__':
    for p in (1,2,3):
        blob(96,p).save(f'{D}/efektit/laatta_latta_{p}.png')
        blob(64,p,seed=2).save(f'{D}/efektit/laatta_latta_pieni_{p}.png')
        tile(p).save(f'{D}/efektit/laatta_tiili_{p}.png')
    hoyry().save(f'{D}/efektit/laatta_hoyry.png')
    # esikatselu ruohon päällä
    g=Image.open(f'{D}/maasto/00_ruoho.png'); S=3
    pv=Image.new('RGBA',(3*100+3*36+8+130,110),hx('#22252a'))
    for p in (1,2,3):
        bg=Image.new('RGBA',(96,96));
        for yy in range(0,96,32):
            for xx in range(0,96,32): bg.paste(g,(xx,yy))
        bg.alpha_composite(Image.open(f'{D}/efektit/laatta_latta_{p}.png')); pv.alpha_composite(bg,(4+(p-1)*100,6))
        t=g.copy(); t.alpha_composite(Image.open(f'{D}/efektit/laatta_tiili_{p}.png')); pv.alpha_composite(t,(304+(p-1)*36,6))
    h=Image.open(f'{D}/efektit/laatta_hoyry.png'); hb=Image.new('RGBA',(128,32));
    for xx in range(0,128,32): hb.paste(g,(xx,0))
    hb.alpha_composite(h); pv.alpha_composite(hb,(412,50))
    pv.resize((pv.width*S,pv.height*S),Image.NEAREST).save(f'{D}/esikatselu_laatta.png'); print('ok')
