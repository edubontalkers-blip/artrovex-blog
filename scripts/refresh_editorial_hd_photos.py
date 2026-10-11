#!/usr/bin/env python3
"""Replace BodyAdvice miniatures using high-resolution CC0 Commons photographs."""
import io,json,re,time,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageOps
root=Path(__file__).resolve().parents[1]/"docs"
queries=["stretching exercise","healthy salad","yoga outdoors","fitness exercise","vegetables food","walking nature","healthy lifestyle","running outdoors","healthy breakfast","cycling nature","meditation","mountain hiking","healthy cooking","strength training","stretching","walking trail","vegetable salad","water drinking","yoga","fresh fruit","outdoor fitness","forest trail","mindfulness","exercise yoga","healthy food","bicycle riding","morning sunshine","wellness lifestyle","physical exercise","mountain landscape","hiking backpack","fresh vegetables","movement exercise","nature walk","walking park","office stretching","healthy posture","physiotherapy exercise","balanced meal","outdoor activity"]
def request(url):
 req=urllib.request.Request(url,headers={"User-Agent":"BodyAdvicePhotoEditor/1.0 (https://bodyadvice.site)"})
 with urllib.request.urlopen(req,timeout=40) as f:return f.read(15000000)
def candidates(q):
 args={"action":"query","generator":"search","gsrsearch":"filetype:bitmap "+q,"gsrnamespace":6,"gsrlimit":40,"prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":1600,"format":"json"}
 data=json.loads(request("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(args)))
 for p in sorted(data.get("query",{}).get("pages",{}).values(),key=lambda v:v.get("index",999)):
  i=(p.get("imageinfo") or [{}])[0]
  lic=re.sub("<[^>]*>","",i.get("extmetadata",{}).get("LicenseShortName",{}).get("value",""))
  if lic != "CC0" or i.get("width",0)<1200 or i.get("height",0)<700:continue
  meta=i.get("extmetadata",{})
  usage=re.sub("<[^>]*>","",meta.get("UsageTerms",{}).get("value","")).strip().lower()
  if usage and "cc0" not in usage and "public domain" not in usage and "no rights reserved" not in usage:continue
  url=i.get("thumburl") or i.get("url")
  if url and re.search(r"\.(jpe?g|png|webp)(\?|$)",url,re.I):yield p["title"],url,i.get("descriptionurl",""),lic
used=set();credits=[];count=0
for n,q in enumerate(queries,1):
 for title,url,source,license_name in candidates(q):
  if title in used:continue
  try:
   im=ImageOps.exif_transpose(Image.open(io.BytesIO(request(url)))).convert("RGB")
   if im.width<1200 or im.height<700:continue
   im.thumbnail((1600,1200),Image.Resampling.LANCZOS)
   if im.width<1100:continue
   out=root/"images"/"editorial"/f"bodyadvice_{n:02d}.webp"
   im.save(out,"WEBP",quality=86,method=6)
   used.add(title);count+=1
   credits.append(f"| {n:02d} | [{title}]({source}) | {license_name} |")
   print(n,title,im.size,flush=True)
   break
  except Exception as e:print("Skipping:",str(e)[:130],flush=True)
 else:print("No suitable verified CC0 image:",n,q,flush=True)
 time.sleep(.2)
(root/"image-credits.md").write_text("# BodyAdvice editorial photo sources\n\nPhotos identified as CC0 or public domain in Wikimedia Commons metadata at download time.\n\n| Image | Source | License |\n|---|---|---|\n"+"\n".join(credits)+"\n")
print("Successfully replaced",count,"of 40 photos")
if count!=40:raise SystemExit("Require all 40 individually verified CC0 images; do not publish partial batch")
