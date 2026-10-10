# Tapahtumailmoituksen UI-grafiikat (Grafiikkabotti). Ajo: python3 ilmoitus.py
from generoi import *
def banneri(w=480,h=96):
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,w-1,h-1],fill=(20,22,26,225)); d.rectangle([0,0,w-1,h-1],outline=hx('#c9a227'))
    d.rectangle([2,2,w-3,h-3],outline=hx('#5a4a1a'))
    for x in range(0,w,12):  # varoitusraidat ylä- ja alareunaan
        d.polygon([(x,4),(x+6,4),(x+2,9),(x-4,9)],fill=hx('#c9a227')); d.polygon([(x,h-10),(x+6,h-10),(x+2,h-5),(x-4,h-5)],fill=hx('#c9a227'))
    d.rectangle([14,18,77,77],fill=(0,0,0,120),outline=hx('#c9a227'))  # 64x64 ikonipaikka (ikoni 32x32 2x)
    return im
def merkki(size=16):
    sheet=Image.new('RGBA',(size*4,size),(0,0,0,0))
    for f,a in enumerate((255,200,140,200)):
        im=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(im)
        d.polygon([(8,15),(2,6),(4,2),(12,2),(14,6)],fill=hx('#f0c020')[:3]+(a,),outline=OUT)
        d.rectangle([7,4,8,8],fill=OUT); d.point((7,10),fill=OUT); d.point((8,10),fill=OUT)
        sheet.alpha_composite(im,(f*size,0))
    return sheet
def puolimerkki():
    out={}
    for n,c in (('sininen',TEAMS['sininen']),('punainen',TEAMS['punainen']),('molemmat',hx('#c9a227'))):
        im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
        if n=='molemmat':
            d.rectangle([1,3,7,12],fill=TEAMS['sininen']); d.rectangle([8,3,14,12],fill=TEAMS['punainen'])
        else: d.rectangle([1,3,14,12],fill=c)
        d.rectangle([1,3,14,12],outline=OUT); d.line([(1,2),(1,15)],fill=hx('#cccccc'))
        out[n]=im
    return out
if __name__=='__main__':
    import os; os.makedirs(f'{D}/ui',exist_ok=True)
    banneri().save(f'{D}/ui/tapahtuma_banneri.png'); merkki().save(f'{D}/ui/tapahtuma_karttamerkki.png')
    for n,im in puolimerkki().items(): im.save(f'{D}/ui/puoli_{n}.png')
    print('ok')
