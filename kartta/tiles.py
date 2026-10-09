import numpy as np, json
from PIL import Image, ImageDraw
from shapely.geometry import Point
exec(open('render.py').read().split('# ---- figure')[0])   # reuse layers
N=64; S=10; R=N*S; sc=R/W
def topix(x,y): return ((x-x0)*sc, (y1-y)*sc)
def mask_poly(g):
    im=Image.new('L',(R,R),0); d=ImageDraw.Draw(im)
    for p in polys(g.intersection(BX)):
        d.polygon([topix(*c) for c in p.exterior.coords],fill=255)
        for i in p.interiors: d.polygon([topix(*c) for c in i.coords],fill=0)
    return np.array(im)>0
def mask_lines(pred,wpx):
    im=Image.new('L',(R,R),0); d=ImageDraw.Draw(im)
    for f in F:
        if pred(f['tags']) and f['g'].geom_type=='LineString':
            for l in lines(f['g'].intersection(BX)):
                d.line([topix(*c) for c in l.coords],fill=255,width=wpx)
    return np.array(im)>0
frac=lambda m: m.reshape(N,S,N,S).mean(axis=(1,3))
L={}
L['water']=frac(mask_poly(water)); L['forest']=frac(mask_poly(forest)); L['wet']=frac(mask_poly(wet))
L['field']=frac(mask_poly(field)); L['park']=frac(mask_poly(park)); L['indu']=frac(mask_poly(indu)); L['rock']=frac(mask_poly(rock))
L['bld']=frac(mask_poly(unary_union(bld)))
L['mway']=frac(mask_lines(lambda t:t.get('highway') in ('motorway','trunk') and t.get('bridge')!='yes' and t.get('tunnel')!='yes',5))
L['road']=frac(mask_lines(lambda t:t.get('highway') in ('primary','secondary','tertiary','primary_link','secondary_link','motorway_link'),4))
L['street']=frac(mask_lines(lambda t:t.get('highway') in ('residential','unclassified','living_street'),2))
L['rail']=frac(mask_lines(lambda t:t.get('railway')=='rail' and t.get('tunnel')!='yes',3))
L['bridge']=frac(mask_lines(lambda t:t.get('bridge')=='yes' and (t.get('highway') in ('motorway','trunk','primary','secondary','tertiary','residential','unclassified','cycleway','footway','path')),3))
TYPES=['ruoho','metsa','vesi','tie','moottoritie','rata','rakennus','teollisuus','pelto','suo','kallio','puisto','silta']
DESC={'ruoho':'Ruoho / avoin maa','metsa':'Metsä – hidas, antaa suojaa','vesi':'Vesi – jalkaväelle ja ajoneuvoille mahdoton','tie':'Tie – nopea liike','moottoritie':'Moottoritie – ylitys vain silloilla','rata':'Rautatie – ylitys hidas/vain tasoristeyksissä','rakennus':'Rakennettu kortteli – este, voi vallata','teollisuus':'Teollisuus/varikko – avoin asfaltti','pelto':'Pelto/niitty – avoin, nopea','suo':'Suo – erittäin hidas','kallio':'Kallio – hidas','puisto':'Puisto/kenttä – avoin','silta':'Silta – kulku esteen yli'}
COST={'ruoho':1.0,'metsa':2.0,'vesi':None,'tie':0.5,'moottoritie':None,'rata':3.0,'rakennus':None,'teollisuus':0.8,'pelto':1.0,'suo':3.0,'kallio':2.5,'puisto':0.9,'silta':0.5}
grid=np.zeros((N,N),int)
def setw(mask,name): grid[mask]=TYPES.index(name)
setw(L['park']>0.4,'puisto'); setw(L['field']>0.4,'pelto'); setw(L['indu']>0.4,'teollisuus'); setw(L['rock']>0.4,'kallio')
setw(L['wet']>0.4,'suo'); setw(L['forest']>0.5,'metsa'); setw(L['bld']>0.25,'rakennus')
setw(L['street']>0.12,'tie'); setw(L['road']>0.12,'tie'); setw(L['water']>0.5,'vesi')
setw(L['rail']>0.12,'rata'); setw(L['mway']>0.12,'moottoritie'); setw((L['bridge']>0.08)&((L['water']>0.3)|(L['rail']>0.05)|(L['mway']>0.05)),'silta')
# owner
own=np.zeros((N,N),int)
cs=(np.arange(N)+0.5)*W/N
from shapely import contains_xy
XX,YY=np.meshgrid(x0+cs, y1-cs)
own[contains_xy(TEAM['Multisilta'],XX,YY)]=1; own[contains_xy(TEAM['Peltolammi'],XX,YY)]=2
def tc(X,Y): return dict(col=int(X/W*N), row=int((W-Y)/W*N))
res=json.load(open('_res.json'))
def cent(fid):
    g=byid(fid)['g']; c=g.centroid; return c.x-x0,c.y-y0
def llp(la,lo): p=P(la,lo); return p.x-x0,p.y-y0
la0,lo0,la1,lo1=bbox_ll()
out=dict(
  name='Lähiösota: Etelä-Tampere – taistelukenttä v1', version=1,
  size=dict(cols=N,rows=N,tile_m=round(W/N,2)), origin='row 0 = pohjoinen (north), col 0 = länsi (west)',
  crs='EPSG:3067 (ETRS-TM35FIN)', bounds_3067=[round(v,1) for v in BX.bounds],
  bbox_wgs84=dict(south=round(la0,5),west=round(lo0,5),north=round(la1,5),east=round(lo1,5)),
  attribution='Karttadata © OpenStreetMap-tekijät, ODbL 1.0 – https://www.openstreetmap.org/copyright',
  terrain_types=[dict(id=i,key=k,kuvaus=DESC[k],move_cost=COST[k]) for i,k in enumerate(TYPES)],
  factions=[dict(id=0,nimi='Puolueeton'),dict(id=1,nimi='Multisilta',vari='#1f6fe0'),dict(id=2,nimi='Peltolammi',vari='#d8262b')],
  bases=[dict(faction=1,nimi='Multisillan päämaja',osm_name='Multisillan kenttä',**tc(*cent('w119563251'))),
         dict(faction=2,nimi='Peltolammin päämaja',osm_name='Peltolammin kenttä',**tc(*cent('w89892330')))],
  resources=[dict(nimi=r['game_label'],osm_name=r['osm_name'],osm_id=r['id'],puoli=r['side'],**tc(r['x'],r['y'])) for r in res],
  chokepoints=[dict(nimi=f'Pullonkaula: {n}',kuvaus=d,**tc(*llp(la,lo))) for n,la,lo,d in CHOKE],
  terrain=grid.tolist(), owner=own.tolist())
json.dump(out,open('pelikentta_v1_tiles.json','w'),ensure_ascii=False,separators=(',',':'))
# preview
pal={'ruoho':(150,190,100),'metsa':(50,100,40),'vesi':(50,120,200),'tie':(240,225,160),'moottoritie':(240,160,50),'rata':(40,40,40),'rakennus':(160,150,140),'teollisuus':(185,180,170),'pelto':(220,205,120),'suo':(110,140,90),'kallio':(130,130,130),'puisto':(160,210,100),'silta':(255,255,255)}
im=np.array([[pal[TYPES[v]] for v in r] for r in grid],np.uint8)
oc={1:np.array([31,111,224]),2:np.array([216,38,43])}
for k,c in oc.items(): m=own==k; im[m]=(im[m]*0.7+c*0.3).astype(np.uint8)
Image.fromarray(im).resize((640,640),Image.NEAREST).save('pelikentta_v1_tiles_preview.png')
print({k:int((grid==i).sum()) for i,k in enumerate(TYPES)}, out['bases'], out['chokepoints'])
