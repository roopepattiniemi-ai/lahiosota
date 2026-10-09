import math, requests, time, os, json
from PIL import Image, ImageDraw, ImageFont
S,W,N,E=61.428,23.725,61.465,23.780; z=15
def xy(lat,lon):
    n=2**z; x=(lon+180)/360*n; y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n; return x,y
x0,y0=xy(N,W); x1,y1=xy(S,E)
h=requests.Session(); h.headers['User-Agent']='PeliKarttaConcept/0.1 (hobby game map prototype; low volume)'
tx=range(int(x0),int(x1)+1); ty=range(int(y0),int(y1)+1)
print(len(tx)*len(ty),'tiles')
big=Image.new('RGB',(256*len(tx),256*len(ty)))
for i,X in enumerate(tx):
  for j,Y in enumerate(ty):
    p=f'tiles/{z}_{X}_{Y}.png'
    if not os.path.exists(p):
        r=h.get(f'https://tile.openstreetmap.org/{z}/{X}/{Y}.png',timeout=60); r.raise_for_status(); open(p,'wb').write(r.content); time.sleep(0.3)
    big.paste(Image.open(p).convert('RGB'),(256*i,256*j))
cx0=int((x0-tx[0])*256); cy0=int((y0-ty[0])*256); cx1=int((x1-tx[0])*256); cy1=int((y1-ty[0])*256)
img=big.crop((cx0,cy0,cx1,cy1))
# overlay neighbourhood boundaries
d=ImageDraw.Draw(img,'RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') else ImageFont.load_default()
sf=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14) if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf') else ImageFont.load_default()
for n,col in [('Multisilta',(0,90,255)),('Peltolammi',(220,30,30))]:
    g=[r for r in json.load(open(f'nom_{n}.json')) if r['type']=='administrative'][0]['geojson']['coordinates'][0]
    pts=[((xy(la,lo)[0]-x0)*256,(xy(la,lo)[1]-y0)*256) for lo,la in g]
    d.line(pts+[pts[0]],fill=col+(230,),width=4)
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    d.text((cx,cy),n,fill=col+(255,),font=font,anchor='mm',stroke_width=3,stroke_fill=(255,255,255))
txt='© OpenStreetMap contributors (openstreetmap.org/copyright) – tiles: tile.openstreetmap.org'
w=d.textlength(txt,font=sf); d.rectangle((img.width-w-12,img.height-24,img.width,img.height),fill=(255,255,255,210))
d.text((img.width-w-6,img.height-20),txt,fill=(0,0,0),font=sf)
img.save('reference_osm.png'); print(img.size)
