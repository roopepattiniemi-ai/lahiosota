import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MPoly, Circle, RegularPolygon, FancyBboxPatch, PathPatch
from matplotlib.path import Path
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point
from shapely.ops import unary_union
from scipy.ndimage import gaussian_filter
from common import *
rng=np.random.default_rng(7)
x0,y0,x1,y1=BX.bounds
def T(x,y): return x-x0, y-y0   # local metres
W=x1-x0
def polys(g):
    if g.is_empty: return []
    if g.geom_type=='Polygon': return [g]
    if hasattr(g,'geoms'): return [p for gg in g.geoms for p in polys(gg)]
    return []
def lines(g):
    if g.is_empty: return []
    if g.geom_type=='LineString': return [g]
    if hasattr(g,'geoms'): return [l for gg in g.geoms for l in lines(gg)]
    return []
def ppath(p):
    verts=[];codes=[]
    for ring in [p.exterior]+list(p.interiors):
        c=[T(*xy) for xy in ring.coords]; verts+=c; codes+=[Path.MOVETO]+[Path.LINETO]*(len(c)-2)+[Path.CLOSEPOLY]
    return Path(verts,codes)
def fill(ax,g,z,**kw):
    for p in polys(g.intersection(BX)):
        ax.add_patch(PathPatch(ppath(p),zorder=z,**kw))
def draw_lines(ax,g,z,**kw):
    for l in lines(g.intersection(BX)):
        xs,ys=zip(*[T(*c) for c in l.coords]); ax.plot(xs,ys,zorder=z,solid_capstyle='round',solid_joinstyle='round',**kw)
def U(pred,buf=0):
    gs=[f['g'] for f in F if pred(f['tags']) and f['g'].geom_type in ('Polygon','MultiPolygon')]
    return unary_union([g.buffer(buf) if buf else g for g in gs]).buffer(0) if gs else Polygon()
t=lambda k,vals: (lambda tg: tg.get(k) in vals)
water=U(lambda tg: tg.get('natural')=='water' or tg.get('water') or tg.get('natural')=='bay')
forest=U(lambda tg: tg.get('natural')=='wood' or tg.get('landuse')=='forest').difference(water)
wet=U(t('natural',['wetland']))
field=U(lambda tg: tg.get('landuse') in ('meadow','farmland','allotments','brownfield','landfill') or tg.get('natural') in ('grassland','heath','scrub'))
park=U(lambda tg: tg.get('leisure') in ('park','pitch','playground','sports_centre') or tg.get('landuse') in ('grass','recreation_ground','cemetery'))
indu=U(lambda tg: tg.get('landuse') in ('industrial','commercial','retail','railway','construction','military'))
resi=U(t('landuse',['residential']))
rock=U(t('natural',['bare_rock']))
# simplified buildings: oriented rectangles
bld=[f['g'] for f in F if 'building' in f['tags'] and f['g'].geom_type=='Polygon' and f['g'].area>25]
def simp(b):
    r=b.minimum_rotated_rectangle
    return r if r.area<b.area*1.35 else b.simplify(3)
bld=[simp(b) for b in bld]
# ---- figure
HEAD=170
fig=plt.figure(figsize=(16,16+HEAD/100),dpi=100)
ax=fig.add_axes([0,0,1,16/(16+HEAD/100)]); ax.set_xlim(0,W); ax.set_ylim(0,W); ax.axis('off')
# base grass with noise
n=gaussian_filter(rng.random((400,400)),4); n=(n-n.min())/(n.max()-n.min())
base=np.array([0.66,0.75,0.42]); img=base[None,None,:]*(0.9+0.2*n[...,None])
ax.imshow(np.clip(img,0,1),extent=(0,W,0,W),zorder=0,interpolation='bicubic')
fill(ax,field,1,fc='#d9cf7e',ec='#b8ab5a',lw=0.8,hatch='///',alpha=1)
fill(ax,park,1.2,fc='#9fcf62',ec='#7fae45',lw=0.8)
fill(ax,resi,1.1,fc='#c9c9a0',ec='none',alpha=0.55)
fill(ax,indu,1.3,fc='#b3ada2',ec='#8c857a',lw=1)
fill(ax,wet,1.5,fc='#7d9a62',ec='#5c7a48',lw=0.8,hatch='...')
fill(ax,rock,1.6,fc='#a8a29a',ec='#77716a',lw=0.8)
fill(ax,forest,2,fc='#3f6d2c',ec='#2b4f1d',lw=1.5)
# trees
fp=forest.intersection(BX); minx,miny,maxx,maxy=fp.bounds
from shapely import contains_xy
pts=rng.uniform([minx,miny],[maxx,maxy],(26000,2)); m=contains_xy(fp,pts[:,0],pts[:,1]); pts=pts[m]
pts=pts[(contains_xy(water.buffer(5),pts[:,0],pts[:,1])==False)]
ax.scatter(pts[:,0]-x0+3,pts[:,1]-y0-3,s=55,c='#22401a',zorder=2.1,linewidths=0,alpha=.6)
ax.scatter(pts[:,0]-x0,pts[:,1]-y0,s=45,c=rng.choice(['#4d8236','#56913b','#467a31'],len(pts)),zorder=2.2,linewidths=0)
ax.scatter(pts[:,0]-x0-2,pts[:,1]-y0+2,s=8,c='#7fb455',zorder=2.3,linewidths=0,alpha=.7)
# water
fill(ax,water.buffer(10),3,fc='#d8d2a4',ec='none')  # beach rim
fill(ax,water,3.1,fc='#3a7cc2',ec='#1d4f86',lw=2)
fill(ax,water.buffer(-15),3.2,fc='#3f88d0',ec='#6fb0ea',lw=1.2,alpha=.8)
wp=water.intersection(BX)
if not wp.is_empty:
    minx,miny,maxx,maxy=wp.bounds; q=rng.uniform([minx,miny],[maxx,maxy],(1500,2)); q=q[contains_xy(wp.buffer(-25),q[:,0],q[:,1])]
    for a,b in q[:160]: ax.plot([a-x0-9,a-x0,a-x0+9],[b-y0,b-y0+4,b-y0],color='#a9d4f5',lw=1.2,zorder=3.3,alpha=.8)
for f in F:
    if f['tags'].get('waterway') in ('stream','river') and f['g'].geom_type=='LineString':
        draw_lines(ax,f['g'],3.05,color='#3a7cc2',lw=1.8)
# team territories
COL={'Multisilta':'#1f6fe0','Peltolammi':'#d8262b'}
for nme,g in TEAM.items():
    fill(ax,g,4,fc=COL[nme],ec='none',alpha=0.13)
# buildings coloured by owner
for b in bld:
    c=b.centroid
    own='#8d8a84'; top='#b9b5ac'
    if TEAM['Multisilta'].contains(c): own,top='#24508f','#5d8fd6'
    elif TEAM['Peltolammi'].contains(c): own,top='#8f2427','#de6a5f'
    sh=Polygon([(x+5,y-5) for x,y in b.exterior.coords])
    fill(ax,sh,5,fc='black',ec='none',alpha=.35)
    fill(ax,b,5.1,fc=top,ec=own,lw=1.1)
# roads
ROAD={'motorway':(15,'#5b3b12','#f0a53a'),'motorway_link':(8,'#5b3b12','#f0a53a'),'trunk':(12,'#5b3b12','#f0a53a'),
      'primary':(10,'#6b5420','#f5d667'),'primary_link':(6,'#6b5420','#f5d667'),'secondary':(9,'#6b5420','#f7e08a'),
      'tertiary':(7,'#6b5a3a','#f3ead0'),'residential':(5,'#6e6450','#efe8d6'),'unclassified':(5,'#6e6450','#efe8d6'),'living_street':(4.5,'#6e6450','#efe8d6'),'service':(3,'#6e6450','#e6dfcc')}
order=['service','living_street','unclassified','residential','tertiary','secondary_link','secondary','primary_link','primary','trunk','motorway_link','motorway']
for f in F:
    hw=f['tags'].get('highway')
    if hw in ('footway','cycleway','path','track') and f['g'].geom_type=='LineString':
        draw_lines(ax,f['g'],6,color='#f3ecd0',lw=1.2,alpha=.55,dashes=(2,2))
for i,k in enumerate(order):
    if k not in ROAD: continue
    w,cas,col=ROAD[k]
    gs=[f['g'] for f in F if f['tags'].get('highway')==k and f['g'].geom_type=='LineString' and f['tags'].get('tunnel')!='yes']
    if not gs: continue
    g=unary_union(gs).simplify(4)
    draw_lines(ax,g,7+i*0.1,color=cas,lw=w+2.5)
    draw_lines(ax,g,7.05+i*0.1,color=col,lw=w)
    if k=='motorway': draw_lines(ax,g,7.07+i*0.1,color='#fff6dd',lw=1,dashes=(6,6))
# rail
rail=unary_union([f['g'] for f in F if f['tags'].get('railway')=='rail' and f['g'].geom_type=='LineString']).simplify(3)
draw_lines(ax,rail,8.5,color='#2b2b2b',lw=6)
draw_lines(ax,rail,8.6,color='#eeeeee',lw=2.5,dashes=(5,5))
# team borders
for nme,g in TEAM.items():
    for p in polys(g.intersection(BX)):
        xs,ys=zip(*[T(*c) for c in p.exterior.coords])
        ax.plot(xs,ys,color=COL[nme],lw=9,alpha=.25,zorder=9)
        ax.plot(xs,ys,color=COL[nme],lw=3.2,zorder=9.1,dashes=(8,4))
TXT=dict(fontfamily='DejaVu Sans',fontweight='bold')
def halo(w=4,c='white'): return [pe.withStroke(linewidth=w,foreground=c)]
# HQs
def hq(feat_id,nme,label):
    c=byid(feat_id)['g'].centroid; X,Y=T(c.x,c.y)
    ax.add_patch(Circle((X,Y),260,fc=COL[nme],ec=COL[nme],alpha=.18,lw=0,zorder=10))
    ax.add_patch(Circle((X,Y),260,fc='none',ec=COL[nme],lw=3,ls=(0,(6,4)),zorder=10.1))
    ax.add_patch(RegularPolygon((X,Y),6,radius=70,fc=COL[nme],ec='white',lw=3,zorder=10.3))
    ax.add_patch(RegularPolygon((X,Y),6,radius=45,fc='white',ec=COL[nme],lw=2,zorder=10.4))
    ax.text(X,Y,'★',fontsize=22,color=COL[nme],ha='center',va='center',zorder=10.5)
    ax.text(X-70 if nme=='Multisilta' else X,Y-100,label,fontsize=13,color='white',ha='center',va='top',zorder=10.6,path_effects=halo(4,'#111'),**TXT)
    return X,Y
hq('w119563251','Multisilta','MULTISILLAN PÄÄMAJA\n(Multisillan kenttä)')
hq('w89892330','Peltolammi','PELTOLAMMIN PÄÄMAJA\n(Peltolammin kenttä)')
# faction names
def ll(lat,lon): p=P(lat,lon); return T(p.x,p.y)
X,Y=ll(61.4370,23.7530); ax.text(X,Y,'MULTISILTA',fontsize=36,color=COL['Multisilta'],ha='center',zorder=11,path_effects=halo(7),**TXT)
X,Y=ll(61.4588,23.7475); ax.text(X,Y,'PELTOLAMMI',fontsize=34,color=COL['Peltolammi'],ha='center',zorder=11,path_effects=halo(7),**TXT)
# resources
RES=[('n937725439','KALJA-VARASTO','Multisilta',(330,30)),
     ('n937725594','MAKKARA-VARASTO','Multisilta',(300,-150)),
     ('n937725504','PIZZATEHDAS','Multisilta',(-420,-300)),
     ('w202620231','HUOLTOVARIKKO','neutral',(330,-60)),
     ('n2185869502','KALJA-VARASTO','Peltolammi',(-260,330)),
     ('n13586884077','KARKKIKAIVOS','Peltolammi',(150,300)),
     ('n494186930','MAKKARA-VARASTO','Peltolammi',(330,120)),
     ('n494186925','LÄÄKINTÄASEMA','Peltolammi',(160,-170)),
     ('n11751407705','TIEDUSTELUKESKUS','Peltolammi',(-330,-150)),
     ('n8680016825','KAHVILÄHDE','neutral',(-330,-150)),
     ('w165732490','PERUNAPELTO','neutral',(-280,230)),
     ('w1208147637','POLTTOAINEVARASTO','neutral',(-20,140)),
     ('n9881870373','KAASUVARASTO','neutral',(120,-170)),
     ('w81912057','LIHAPULLALINNAKE','neutral',(-60,240)),
     ('w40685657','ROMUTARVIKEVARASTO','neutral',(0,-250)),
    ]
CN={'Multisilta':COL['Multisilta'],'Peltolammi':COL['Peltolammi'],'neutral':'#6b5b00'}
used=[]
for fid,lab,side,(dx,dy) in RES:
    f=byid(fid); c=f['g'].centroid if f['g'].geom_type!='Point' else f['g']; X,Y=T(c.x,c.y)
    name=f['tags'].get('name')
    used.append(dict(id=fid,osm_name=name,game_label=lab,side=side,x=X,y=Y))
    ax.plot([X,X+dx],[Y,Y+dy],color='#222',lw=1.4,zorder=12)
    ax.add_patch(RegularPolygon((X,Y),4,radius=34,fc='#ffd21f',ec='#222',lw=2,zorder=12.5))
    ax.text(X,Y,'$',fontsize=11,ha='center',va='center',zorder=12.6,color='#222',**TXT)
    ax.text(X+dx,Y+dy,f'{lab}\n{name}',fontsize=9.5,ha='center',va='center',zorder=12.7,color='#222',linespacing=1.15,
            bbox=dict(boxstyle='round,pad=0.35',fc='#fff6c9',ec=CN[side],lw=2),**TXT)
# chokepoints
for nme,la,lo,desc in CHOKE:
    X,Y=ll(la,lo)
    ax.add_patch(RegularPolygon((X,Y),3,radius=60,fc='#ff8c00',ec='#1a1a1a',lw=2.5,zorder=13))
    ax.text(X,Y-10,'⚔',fontsize=17,ha='center',va='center',zorder=13.1,color='#1a1a1a')
    ax.text(X,Y+75,f'PULLONKAULA\n{nme}',fontsize=10,ha='center',va='bottom',zorder=13.2,color='#ffe9c2',path_effects=halo(3.5,'#3a1a00'),**TXT)
# terrain labels
for txt,la,lo,fs,rot in [('Peltolammi (järvi)',61.4462,23.7425,13,0),('Peltolammin–Pärrinkosken\nsuojelualue: hidas maasto',61.4515,23.7330,10,0),
                         ('Valtatie 3 – ylitys vain silloilla',None,None,11,71),('Päärata',61.4555,23.7380,10,-75),('Särkijärvi',61.4400,23.7720,14,0),('PUOLUEETON\nKAUPPA-ALUE',61.4588,23.7728,13,0)]:
    X,Y=ll(la,lo) if la else (1812,725); ax.text(X,Y,txt,fontsize=fs,rotation=rot,ha='center',va='center',zorder=11.5,color='white',path_effects=halo(3.5,'#173a5e'),**TXT)
# scale bar + compass
ax.add_patch(FancyBboxPatch((40,40),700,200,boxstyle='round,pad=10',fc='#2a2418',ec='#c9a75a',lw=3,alpha=.92,zorder=14))
LEG=[('#3f6d2c','Metsä (hidas, suoja)'),('#d9cf7e','Pelto/niitty (avoin)'),('#3a7cc2','Vesi (ei kulkua)'),('#b3ada2','Teollisuus/varikko'),('#f5d667','Päätie (nopea)'),('#7d9a62','Suo (erittäin hidas)')]
for i,(c,l) in enumerate(LEG):
    r,cc=divmod(i,2); xx=70+cc*340; yy=200-r*45
    ax.add_patch(FancyBboxPatch((xx,yy-12),40,24,boxstyle='round,pad=2',fc=c,ec='#ddd',lw=1,zorder=14.1))
    ax.text(xx+52,yy,l,fontsize=10,color='#f3e7c4',va='center',zorder=14.2,**TXT)
ax.plot([W-560,W-60],[70,70],color='black',lw=8,zorder=14,solid_capstyle='butt'); ax.plot([W-560,W-310],[70,70],color='white',lw=5,zorder=14.1,solid_capstyle='butt')
ax.text(W-310,95,'500 m',fontsize=12,ha='center',zorder=14.2,path_effects=halo(3),**TXT)
ax.annotate('',xy=(W-110,W-90),xytext=(W-110,W-260),arrowprops=dict(arrowstyle='simple,head_width=1.6,head_length=1.4,tail_width=0.6',fc='#c9a75a',ec='#2a2418',lw=2),zorder=14)
ax.text(W-110,W-300,'P',fontsize=20,ha='center',zorder=14,color='#2a2418',path_effects=halo(4,'#c9a75a'),**TXT)
ax.text(W-12,12,'Karttadata © OpenStreetMap-tekijät (ODbL) – openstreetmap.org/copyright',fontsize=9,ha='right',va='bottom',zorder=15,color='#111',
        bbox=dict(boxstyle='square,pad=0.3',fc='white',ec='none',alpha=.75))
# frame
for s in [(0,0,W,W)]:
    ax.add_patch(plt.Rectangle((0,0),W,W,fc='none',ec='#2a2418',lw=14,zorder=20))
# header
hx=fig.add_axes([0,16/(16+HEAD/100),1,(HEAD/100)/(16+HEAD/100)]); hx.axis('off'); hx.set_xlim(0,1); hx.set_ylim(0,1)
g=np.linspace(0,1,256)[None,:]; hx.imshow(np.dstack([0.12+0*g,0.10+0*g,0.07+0*g]),extent=(0,1,0,1),aspect='auto')
hx.add_patch(plt.Rectangle((0,0),.5,.06,color=COL['Multisilta'])); hx.add_patch(plt.Rectangle((.5,0),.5,.06,color=COL['Peltolammi']))
hx.text(.5,.66,'LÄHIÖSOTA: ETELÄ-TAMPERE',fontsize=40,ha='center',va='center',color='#f2c84b',path_effects=halo(6,'#000'),**TXT)
hx.text(.5,.27,'Taistelukenttä v1 · Multisilta vastaan Peltolammi',fontsize=19,ha='center',va='center',color='#f3e7c4',**TXT)
hx.text(.02,.27,'◆ SININEN: MULTISILTA',fontsize=14,color='#6fa5ff',va='center',**TXT)
hx.text(.98,.27,'PUNAINEN: PELTOLAMMI ◆',fontsize=14,color='#ff7a72',va='center',ha='right',**TXT)
fig.savefig('pelikentta_v1.png',dpi=100)
import json; json.dump(used,open('_res.json','w'),ensure_ascii=False,indent=1)
print('done')
