#!/usr/bin/env python3
"""Install the owner's 40 original WebP photos into the site from a local ZIP.
Usage: python scripts/install_bodyadvice_photos.py /path/to/bodyadvice_40_photos.zip
Then review and commit docs/images/editorial and updated HTML.
"""
from pathlib import Path
from zipfile import ZipFile
import re, sys, html
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
DEST=DOCS/'images'/'editorial'
ALT={4:'Woman stretching at home',5:'Fresh balanced salad',6:'Mountain lake hiking landscape',15:'Older couple walking outdoors',23:'Woman practising mindfulness',31:'Woman hiking outdoors',37:'Woman taking a movement break'}
TOPICS=[(('neck','shoulder','trapezius','splenius'),37),(('hip','psoas','gluteus'),4),(('finger','hand','wrist','forearm','supinator'),37),(('foot','toe','tibialis','calf','knee'),31),(('nutrition','food','diet'),5),(('hydration','water'),1),(('sleep','rest'),28)]
def image_for(path):
 name=path.stem.lower()
 return next((i for words,i in TOPICS if any(w in name for w in words)),4)
def add_image(path):
 source=path.read_text(encoding='utf-8')
 if 'data-editorial-photo=' in source or '<h1' not in source.lower():return False
 num=image_for(path)
 rel='../images/editorial' if path.parent.name=='articles' else 'images/editorial'
 alt=html.escape(ALT.get(num,'Everyday wellness lifestyle photograph'),quote=True)
 tag=f'<figure data-editorial-photo="{num:02d}" class="article-photo"><img src="{rel}/bodyadvice_{num:02d}.webp" alt="{alt}" loading="lazy" decoding="async" style="width:100%;max-height:380px;object-fit:cover;border-radius:16px"></figure>'
 source,n=re.subn(r'</h1>',lambda m:m.group()+tag,source,count=1,flags=re.I)
 if n:path.write_text(source,encoding='utf-8')
 return bool(n)
def main():
 if len(sys.argv)!=2:raise SystemExit('Provide the path to the supplied photo ZIP.')
 with ZipFile(sys.argv[1]) as archive:
  DEST.mkdir(parents=True,exist_ok=True)
  for i in range(1,41):
   name=f'bodyadvice_{i:02d}.webp'
   data=archive.read(name)
   if data[:4]!=b'RIFF' or data[8:12]!=b'WEBP':raise ValueError(name+' is not WebP')
   (DEST/name).write_bytes(data)
 count=sum(add_image(p) for p in (DOCS/'articles').glob('*.html'))
 print(f'Installed 40 WebP photos and added illustrative photos to {count} articles.')
if __name__=='__main__':main()
