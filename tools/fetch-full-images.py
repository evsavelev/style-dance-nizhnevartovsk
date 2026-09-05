from pathlib import Path
from bs4 import BeautifulSoup
import json,urllib.request,concurrent.futures
from PIL import Image
root=Path(__file__).resolve().parents[1]
original=root/'stitch-original'
cache=root/'.tools/source-images';cache.mkdir(exist_ok=True,parents=True)
s=BeautifulSoup((original/'desktop/f5ee03817e2940f0ae21469e0799ad15/index.html').read_text(encoding='utf-8'),'html.parser')
manifest=json.loads((original/'download-manifest.json').read_text(encoding='utf-8'))
lookup={r['url']:r['file'] for r in manifest if r['status']=='ok'}
def fetch(url):
 target=cache/Path(lookup[url]).name
 with urllib.request.urlopen(url+'=s0',timeout=30) as response:target.write_bytes(response.read())
 with Image.open(target) as im:return (target.name,im.size)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for row in pool.map(fetch,sorted({img['src'] for img in s.select('img')})):print(row)
