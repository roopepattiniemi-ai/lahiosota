# OSM-raakadatasta (raw/*.osm) tie-, rata- ja polkuviivat pelikentän pikselikoordinaatteihin (Grafiikkabotti).
# 32 px/ruutu, 64x64 ruutua -> 2048x2048 px, origo vasen yläkulma (pohjoinen ylhäällä).
# Projektio WGS84 -> EPSG:3067 (ETRS-TM35FIN) toteutettu itse (Krüger-sarja), ei ulkoisia kirjastoja.
# Karttadata © OpenStreetMap contributors (ODbL 1.0).
import os, glob, json, math
import xml.etree.ElementTree as ET
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TILES_V1 = os.path.join(HERE, 'pelikentta_v1_tiles.json')
PX = 2048

def tm35(lon, lat):
    a = 6378137.0; f = 1 / 298.257222101; n = f / (2 - f); A = a / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64); k0 = 0.9996
    al = [n / 2 - 2 / 3 * n ** 2 + 5 / 16 * n ** 3, 13 / 48 * n ** 2 - 3 / 5 * n ** 3, 61 / 240 * n ** 3]
    phi = np.radians(lat); lam = np.radians(np.asarray(lon) - 27.0); c = 2 * math.sqrt(n) / (1 + n)
    t = np.sinh(np.arctanh(np.sin(phi)) - c * np.arctanh(c * np.sin(phi)))
    xi = np.arctan(t / np.cos(lam)); eta = np.arctanh(np.sin(lam) / np.sqrt(1 + t ** 2))
    E = 500000 + k0 * A * (eta + sum(al[j] * np.cos(2 * (j + 1) * xi) * np.sinh(2 * (j + 1) * eta) for j in range(3)))
    N = k0 * A * (xi + sum(al[j] * np.sin(2 * (j + 1) * xi) * np.cosh(2 * (j + 1) * eta) for j in range(3)))
    return E, N

ROAD_CLASS = {
    'motorway': 'moottoritie', 'trunk': 'moottoritie',
    'motorway_link': 'ramppi', 'trunk_link': 'ramppi',
    'primary': 'paatie', 'secondary': 'paatie', 'tertiary': 'paatie', 'primary_link': 'paatie', 'secondary_link': 'paatie', 'tertiary_link': 'paatie',
    'residential': 'katu', 'unclassified': 'katu', 'living_street': 'katu', 'road': 'katu',
    'service': 'huoltotie',
    'footway': 'polku', 'cycleway': 'polku', 'path': 'polku', 'track': 'polku', 'bridleway': 'polku', 'steps': 'polku', 'pedestrian': 'polku',
}

def load(cache=True):
    """Palauttaa listan dict(id, luokka, hw, bridge, tunnel, layer, sidewalk, pts=[(x,y),...]) pikseleinä."""
    cf = os.path.join(HERE, 'osm_vektorit_cache.json')
    if cache and os.path.exists(cf) and os.path.getmtime(cf) > max(os.path.getmtime(f) for f in glob.glob(os.path.join(HERE, 'raw', '*.osm'))):
        return json.load(open(cf))
    J = json.load(open(TILES_V1)); x0, y0, x1, y1 = J['bounds_3067']; sc = PX / (x1 - x0)
    nodes = {}; ways = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'raw', '*.osm'))):
        for el in ET.parse(f).getroot():
            if el.tag == 'node': nodes[int(el.get('id'))] = (float(el.get('lon')), float(el.get('lat')))
            elif el.tag == 'way':
                tags = {t.get('k'): t.get('v') for t in el.findall('tag')}
                if 'highway' in tags or tags.get('railway') == 'rail':
                    ways[int(el.get('id'))] = ([int(n.get('ref')) for n in el.findall('nd')], tags)
    out = []
    for wid, (nds, tags) in sorted(ways.items()):
        ll = [nodes[n] for n in nds if n in nodes]
        if len(ll) < 2: continue
        lon = np.array([p[0] for p in ll]); lat = np.array([p[1] for p in ll])
        E, N = tm35(lon, lat)
        pts = [(round(float((e - x0) * sc), 2), round(float((y1 - nn) * sc), 2)) for e, nn in zip(E, N)]
        if tags.get('railway') == 'rail': cls = 'rata'
        else:
            cls = ROAD_CLASS.get(tags.get('highway'))
            if cls is None: continue
            if tags.get('area') == 'yes': continue
        if cls == 'polku' and tags.get('footway') in ('sidewalk', 'crossing'): cls = 'jalkakaytava'
        if cls == 'polku' and tags.get('cycleway') in ('crossing',): cls = 'jalkakaytava'
        out.append(dict(id=wid, luokka=cls, hw=tags.get('highway', 'rail'), service=tags.get('service', ''),
                        bridge=tags.get('bridge', 'no') not in ('no', ''), tunnel=tags.get('tunnel', 'no') not in ('no', '') or tags.get('covered') == 'yes',
                        layer=int(tags.get('layer', '0')) if tags.get('layer', '0').lstrip('-').isdigit() else 0,
                        nodes=[n for n in nds if n in nodes], name=tags.get('name', ''), pts=pts))
    if cache: json.dump(out, open(cf, 'w'), ensure_ascii=False)
    return out

if __name__ == '__main__':
    V = load(cache=False); from collections import Counter
    inside = [v for v in V if any(0 <= x < PX and 0 <= y < PX for x, y in v['pts'])]
    print(len(V), len(inside)); print(Counter(v['luokka'] for v in inside)); print(Counter((v['luokka'], v['bridge']) for v in inside if v['bridge'] or v['tunnel']))
