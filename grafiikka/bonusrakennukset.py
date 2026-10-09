# 11 puolueetonta bonusrakennusta 64x64 (Grafiikkabotti). Ajo: python3 bonusrakennukset.py
from generoi import *
def sign(d,x0,yr,w,bg,fg=None):
    d.rectangle([x0+14,yr+6,x0+w-15,yr+22],fill=bg,outline=shade(bg,.6)); return x0+w//2, yr+14
def pizzatehdas():
    im,d,x0,yr,yw,w,h=building(hx('#e8dcc0'),hx('#6a3a2a'))
    cx,cy=sign(d,x0,yr,w,hx('#7a1f1f'))
    d.ellipse([cx-6,cy-6,cx+6,cy+6],fill=hx('#e8b04a'),outline=hx('#b07a2a')); d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=hx('#d84a2a'))
    for p in [(cx-2,cy-1),(cx+2,cy+1),(cx,cy+3),(cx+1,cy-3)]: d.point(p,fill=hx('#f5e8b0'))
    for i in range(0,w,4): d.rectangle([x0+i,yw+3,x0+i+1,yw+6],fill=hx('#c0302a')); d.rectangle([x0+i+2,yw+3,x0+i+3,yw+6],fill=hx('#f0f0ea'))
    windows(d,x0,yw+6,w,1,4,seed=2,col=hx('#d89a4a'),lit=hx('#f0c060')); d.rectangle([x0+25,yw+10,x0+32,yw+h-1],fill=hx('#3a2c20'))
    d.rectangle([x0+44,yr-6,x0+48,yr+4],fill=hx('#7a7570')); d.point([(x0+46,yr-8),(x0+45,yr-10)],fill=hx('#cfcfcf'))
    return outline(im)
def karkkikaivos():
    im,d,x0,yr,yw,w,h=building(hx('#d8d4cc'),hx('#58595c'),h=18,w=40,depth=22)
    cx,cy=x0+w//2,yr+11; d.rectangle([x0+6,yr+5,x0+w-7,yr+17],fill=hx('#2a6ad0'))
    d.rectangle([cx-3,cy-5,cx+2,cy+5],fill=hx('#40e070')); d.polygon([(cx,cy-3),(cx-2,cy+1),(cx+1,cy+1),(cx-1,cy+4)],fill=hx('#1a1a1a'))
    d.rectangle([x0+3,yw+4,x0+w-4,yw+h-3],fill=hx('#7fb0d0'))
    for i,c in enumerate(['#e04a4a','#f0d040','#4ad04a','#e080d0','#40a0f0']): d.rectangle([x0+5+i*6,yw+10,x0+8+i*6,yw+13],fill=hx(c))
    return outline(im)
def laakintaasema():
    im,d,x0,yr,yw,w,h=building(hx('#eaeae4'),hx('#5e6064'))
    cx,cy=x0+w//2,yr+13; d.rectangle([cx-9,cy-9,cx+9,cy+9],fill=hx('#f4f4f0'),outline=hx('#2a9a4a'))
    d.rectangle([cx-2,cy-6,cx+2,cy+6],fill=hx('#2aaa4a')); d.rectangle([cx-6,cy-2,cx+6,cy+2],fill=hx('#2aaa4a'))
    windows(d,x0,yw,w,2,6,seed=3,col=hx('#9fc6e0'),lit=hx('#e8f4ff')); d.rectangle([x0+24,yw+11,x0+31,yw+h-1],fill=hx('#6fa0c0'))
    return outline(im)
def tiedustelukeskus():
    im,d,x0,yr,yw,w,h=building(hx('#a8604a'),hx('#4a4c50'))
    cx,cy=sign(d,x0,yr,w,hx('#2a3a5a'))
    d.rectangle([cx-7,cy-4,cx-1,cy+4],fill=hx('#f0ead8')); d.rectangle([cx+1,cy-4,cx+7,cy+4],fill=hx('#f0ead8')); d.line([(cx,cy-4),(cx,cy+4)],fill=hx('#7a5a3a'))
    for y in (cy-2,cy,cy+2): d.line([(cx-6,y),(cx-2,y)],fill=hx('#888888')); d.line([(cx+2,y),(cx+6,y)],fill=hx('#888888'))
    windows(d,x0,yw,w,2,7,seed=4,start=3,step_y=7)
    d.line([(x0+47,yr-12),(x0+47,yr+4)],fill=hx('#9a9a9a')); d.ellipse([x0+42,yr-14,x0+52,yr-6],outline=hx('#d0d0d0')); d.point((x0+47,yr-10),fill=hx('#e04040'))
    return outline(im)
def kahvilahde():
    im,d,x0,yr,yw,w,h=building(hx('#f0dcd0'),hx('#7a5a4a'),w=48)
    cx,cy=sign(d,x0,yr,w,hx('#f4c0d0'))
    d.rectangle([cx-5,cy-3,cx+3,cy+5],fill=hx('#f8f8f4'),outline=hx('#7a4a2a')); d.rectangle([cx+4,cy-1,cx+5,cy+3],outline=hx('#7a4a2a'))
    d.rectangle([cx-4,cy-2,cx+2,cy-1],fill=hx('#5a3018')); d.point([(cx-2,cy-5),(cx,cy-6)],fill=hx('#cfcfcf'))
    d.line([(cx-9,cy-6),(cx-9,cy-3)],fill=hx('#f8f8f4')); d.line([(cx-7,cy-6),(cx-7,cy-3)],fill=hx('#f8f8f4'))  # pupun korvat
    for x in (x0+4,x0+32): d.rectangle([x,yw+7,x+11,yw+15],fill=hx('#e8c890'))
    d.rectangle([x0+20,yw+9,x0+27,yw+h-1],fill=hx('#6a3a2a'))
    return outline(im)
def perunapelto():
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([2,10,61,61],fill=hx('#6a4a2a'))
    r=random.Random(5)
    for y in range(14,60,6):
        d.line([(4,y),(59,y)],fill=hx('#4e3520'))
        for x in range(6,58,5): d.point((x+r.randint(0,1),y-2),fill=hx('#4aa03a')); d.point((x+1,y-3),fill=hx('#6ac04a'))
    for x in range(2,62,6): d.line([(x,8),(x,11)],fill=hx('#8a6a40'))
    d.line([(2,9),(61,9)],fill=hx('#a08050'))
    d.rectangle([46,0,58,10],fill=hx('#b04030')); d.polygon([(45,1),(52,-4),(59,1)],fill=hx('#5a4a40')); d.rectangle([50,5,53,10],fill=hx('#3a2a1a'))
    d.line([(10,0),(10,8)],fill=hx('#6a4a2a')); d.line([(7,3),(13,3)],fill=hx('#6a4a2a')); d.point((10,0),fill=hx('#e8d27a'))
    return outline(im)
def huoltovarikko():
    im,d,x0,yr,yw,w,h=building(hx('#8a9098'),hx('#5a6068'),h=24)
    for i in range(3):
        x=x0+4+i*18; d.rectangle([x,yw+5,x+13,yw+h-1],fill=hx('#b0b4b8'))
        for y in range(yw+6,yw+h,2): d.line([(x,y),(x+13,y)],fill=hx('#8a8e92'))
    for i in range(0,w,6): d.rectangle([x0+i,yr+2,x0+i+2,yr+4],fill=hx('#e0c020'))
    d.rectangle([x0+20,yr+10,x0+35,yr+20],fill=hx('#e0c020'),outline=hx('#8a7010'))
    d.polygon([(x0+24,yr+18),(x0+31,yr+12),(x0+33,yr+14),(x0+26,yr+19)],fill=hx('#2a2a2a'))
    return outline(im)
def romutarvikevarasto():
    im,d,x0,yr,yw,w,h=building(hx('#3a5aa0'),hx('#4a4c50'),h=22)
    d.rectangle([x0+10,yw+3,x0+w-11,yw+8],fill=hx('#f0d020')); d.rectangle([x0+14,yw+4,x0+w-15,yw+7],fill=hx('#e03030'))
    d.rectangle([x0+22,yw+11,x0+33,yw+h-1],fill=hx('#2a2a30'))
    for i,c in enumerate(['#8a8a8a','#a05030','#606a70']): d.rectangle([x0+3+i*5,yr+6+i*3,x0+9+i*5,yr+10+i*3],fill=hx(c))
    d.ellipse([x0+40,yr+8,x0+48,yr+16],fill=hx('#1c1c1c')); d.ellipse([x0+43,yr+11,x0+45,yr+13],fill=hx('#9a9a9a'))
    return outline(im)
def tank(color, top, label_col):
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im)
    shadow(d,32,56,28,4)
    return im,d
def polttoainevarasto():
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im); shadow(d,32,57,29,4)
    d.rectangle([2,6,61,12],fill=hx('#e8e8e4')); d.rectangle([2,12,61,14],fill=hx('#d8a020'))
    for x in (8,54): d.rectangle([x,14,x+2,52],fill=hx('#c8c8c4'))
    for x in (18,34):
        d.rectangle([x,28,x+8,52],fill=hx('#d0d0cc'),outline=hx('#7a7a78')); d.rectangle([x+2,32,x+6,38],fill=hx('#1a1a1a')); d.point((x+4,35),fill=hx('#40e040'))
        d.line([(x+8,40),(x+11,44)],fill=hx('#2a2a2a'))
    d.rectangle([22,16,40,24],fill=hx('#d8a020')); d.polygon([(31,17),(28,21),(31,23),(34,21)],fill=hx('#c03020'))
    return outline(im)
def kaasuvarasto():
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im); shadow(d,32,57,29,4)
    for cx in (18,46):
        d.rectangle([cx-12,22,cx+12,52],fill=hx('#e8eef0')); d.ellipse([cx-12,16,cx+12,28],fill=hx('#f8fafa'),outline=hx('#9aa8b0'))
        d.line([(cx+10,24),(cx+10,52)],fill=hx('#b0bcc4')); d.rectangle([cx-12,38,cx+12,41],fill=hx('#2a8ac0'))
        d.line([(cx-8,52),(cx-8,56)],fill=hx('#7a7a78')); d.line([(cx+8,52),(cx+8,56)],fill=hx('#7a7a78'))
    d.polygon([(32,4),(28,12),(32,14),(36,12)],fill=hx('#40a0f0')); d.polygon([(32,8),(30,12),(34,12)],fill=hx('#e0f4ff'))
    d.line([(30,40),(34,40)],fill=hx('#7a7a78'))
    return outline(im)
def lihapullalinnake():
    im=Image.new('RGBA',(B,B),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([3,60,62,63],fill=SHADOW)
    d.rectangle([1,6,62,30],fill=hx('#4a4c50'),outline=hx('#6a6c70'))
    d.rectangle([1,30,62,60],fill=hx('#1f4fa0')); d.line([(1,30),(62,30)],fill=hx('#143a7a'))
    d.rectangle([1,40,62,46],fill=hx('#f0c820'))
    # piikkilanka/hiekkasäkit
    for i in range(0,62,5): d.ellipse([i,57,i+5,61],fill=hx('#b8a06a'),outline=hx('#7a6640'))
    for i in range(3,62,4): d.point((i,5),fill=hx('#9a9a9a')); d.point((i+1,4),fill=hx('#9a9a9a'))
    d.rectangle([26,48,37,57],fill=hx('#2a2a30'))
    # lihapulla-kyltti katolla
    d.ellipse([22,10,40,26],fill=hx('#8a4a24'),outline=hx('#5a2a10')); d.point([(27,14),(33,16),(29,21)],fill=hx('#b06a3a'))
    d.point([(36,13),(25,18)],fill=hx('#5a2a10'))
    for x in (6,52): d.rectangle([x,14,x+5,22],fill=hx('#5a5c60'),outline=hx('#3a3c40'))
    return outline(im)
items={'pizzatehdas':pizzatehdas,'karkkikaivos':karkkikaivos,'laakintaasema':laakintaasema,'tiedustelukeskus':tiedustelukeskus,
 'kahvilahde':kahvilahde,'perunapelto':perunapelto,'huoltovarikko':huoltovarikko,'romutarvikevarasto':romutarvikevarasto,
 'polttoainevarasto':polttoainevarasto,'kaasuvarasto':kaasuvarasto,'lihapullalinnake':lihapullalinnake}
if __name__=='__main__':
    pv=Image.new('RGBA',(6*(B*2+8)+8,2*(B*2+8)+8),hx('#22252a'))
    for i,(n,f) in enumerate(items.items()):
        im=f(); im.save(f'{D}/rakennukset/{n}.png')
        pv.alpha_composite(im.resize((B*2,B*2),Image.NEAREST),(8+(i%6)*(B*2+8),8+(i//6)*(B*2+8)))
    pv.save(f'{D}/esikatselu_bonus.png'); print('ok')
