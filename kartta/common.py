import json,pickle
from shapely.geometry import shape, box, Point
from shapely.ops import transform, unary_union
from pyproj import Transformer
TR=Transformer.from_crs(4326,3067,always_xy=True); TRI=Transformer.from_crs(3067,4326,always_xy=True)
def proj(g): return transform(TR.transform,g)
CLAT,CLON,HALF=61.4475,23.7525,1450
cx,cy=TR.transform(CLON,CLAT)
BX=box(cx-HALF,cy-HALF,cx+HALF,cy+HALF)
def bbox_ll():
    lo0,la0=TRI.transform(cx-HALF,cy-HALF); lo1,la1=TRI.transform(cx+HALF,cy+HALF); return la0,lo0,la1,lo1
F=pickle.load(open('feats.pkl','rb'))
for f in F: f['g']=proj(f['geom'])
F=[f for f in F if f['g'].intersects(BX)]
TEAM={n:proj(shape([r for r in json.load(open(f'nom_{n}.json')) if r['type']=='administrative'][0]['geojson'])) for n in ['Multisilta','Peltolammi']}
def byid(i): return next(f for f in F if f['id']==i)
def P(lat,lon): return Point(*TR.transform(lon,lat))
# chokepoints from boundary-crossing analysis
CHOKE=[("Lempääläntie",61.44687,23.74983,"Päätie rajan yli"),
       ("Ratasilta (Päärata)",61.44449,23.73745,"Rata Peltolammin salmen yli"),
       ("Pyörätiesola",61.44515,23.75700,"Kapea kevyen liikenteen väylä")]
