import json, sys
from PIL import Image, ImageDraw
d='media/swarm4/sprites/'; m=json.load(open(d+'sprites.json'))
names=sorted(m); H=420; cols=6
tiles=[]
for n in names:
    im=Image.open(d+m[n]['file']); s=H/ max(im.height,1); im=im.resize((max(1,int(im.width*s)),H)); tiles.append((n,im))
W=max(t[1].width for t in tiles)+20; rows=(len(tiles)+cols-1)//cols
sh=Image.new('RGB',(W*cols,(H+30)*rows),(28,34,48)); dr=ImageDraw.Draw(sh)
for i,(n,im) in enumerate(tiles):
    x=(i%cols)*W+10; y=(i//cols)*(H+30)
    sh.paste(im,(x,y+25),im); dr.text((x,y+5),n,fill=(255,255,255))
sh.save('media/swarm4/sprites/contact.jpg',quality=90)
