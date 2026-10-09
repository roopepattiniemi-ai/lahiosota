import xml.etree.ElementTree as ET, glob, pickle
from shapely.geometry import LineString, Polygon, Point, MultiPolygon
from shapely.ops import linemerge, polygonize, unary_union
nodes={}; ways={}; rels={}
for f in glob.glob('raw/*.osm'):
    for el in ET.parse(f).getroot():
        tags={t.get('k'):t.get('v') for t in el.findall('tag')}
        i=int(el.get('id')) if el.get('id') else None
        if el.tag=='node': nodes[i]=(float(el.get('lon')),float(el.get('lat')),tags)
        elif el.tag=='way': ways[i]=([int(n.get('ref')) for n in el.findall('nd')],tags)
        elif el.tag=='relation': rels[i]=([(m.get('type'),int(m.get('ref')),m.get('role')) for m in el.findall('member')],tags)
print(len(nodes),len(ways),len(rels))
AREA_KEYS={'building','landuse','natural','leisure','amenity','water','place','parking','shop'}
feats=[]
def wcoords(w): 
    return [nodes[n][:2] for n in ways[w][0] if n in nodes]
for wid,(nds,tags) in ways.items():
    c=wcoords(wid)
    if len(c)<2: continue
    closed=nds[0]==nds[-1] and len(c)>=4
    isarea = closed and (tags.get('area')=='yes' or (any(k in tags for k in AREA_KEYS) and 'highway' not in tags and 'barrier' not in tags) )
    if 'natural' in tags and tags['natural'] in ('coastline','tree_row','cliff'): isarea=False
    g=Polygon(c) if isarea else LineString(c)
    if not g.is_valid: g=g.buffer(0)
    feats.append(dict(geom=g,tags=tags,id=f'w{wid}'))
for rid,(mem,tags) in rels.items():
    if tags.get('type')!='multipolygon': continue
    outer=[LineString(wcoords(r)) for t,r,ro in mem if t=='way' and r in ways and ro!='inner' and len(wcoords(r))>1]
    inner=[LineString(wcoords(r)) for t,r,ro in mem if t=='way' and r in ways and ro=='inner' and len(wcoords(r))>1]
    if not outer: continue
    op=list(polygonize(unary_union(outer)))
    if not op: continue
    g=unary_union(op)
    ip=list(polygonize(unary_union(inner))) if inner else []
    if ip: g=g.difference(unary_union(ip))
    feats.append(dict(geom=g,tags=tags,id=f'r{rid}'))
for nid,(lo,la,tags) in nodes.items():
    if tags and any(k in tags for k in ('shop','amenity','tourism','historic','leisure','natural','railway','public_transport','sport','place')):
        feats.append(dict(geom=Point(lo,la),tags=tags,id=f'n{nid}'))
print(len(feats))
pickle.dump(feats,open('feats.pkl','wb'))
