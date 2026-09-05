from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parents[1]
out=root/'qa';out.mkdir(exist_ok=True)
original=root/'stitch-original'
hashes={str(p.relative_to(original)):hashlib.sha256(p.read_bytes()).hexdigest() for p in original.rglob('*') if p.is_file()}
(out/'original-sha256.json').write_text(json.dumps(hashes,indent=2))
for p in original.glob('desktop/*/index.html'):
 s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 print('\nSCREEN',p.parent.name,'SHA',hashlib.sha256(p.read_bytes()).hexdigest())
 for sec in s.select('body > section'):
  print('SECTION',sec.get('id'),sec.get('class'),sec.get_text(' ',strip=True)[:700])
 print('IMAGES',[(i.get('alt'),i.get('class')) for i in s.select('img')])
 print('BUTTONS',[(b.get_text(' ',strip=True),b.get('onclick')) for b in s.select('button')])
for name in ['f5ee03817e2940f0ae21469e0799ad15','dd83ae81ebd343d18a2c4f6ac5fc4c39']:
 im=Image.open(original/'desktop'/name/'screenshot-full.png')
 im.crop((0,0,2560,1800)).resize((1280,900)).save(out/(name+'-hero.png'))
