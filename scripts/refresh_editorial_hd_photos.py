#!/usr/bin/env python3
"""Replace BodyAdvice miniatures using high-resolution CC0 Commons photographs."""
import io,json,re,time,hashlib,urllib.parse,urllib.request
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
# Improve only repeated photographs. Keep every existing verified photo unless a distinct CC0 replacement is found.
manifest_path=root/"images"/"editorial"/"photo-license-manifest.json"
manifest=json.loads(manifest_path.read_text())
assert len(manifest)==40
used={e["title"] for e in manifest}
seen=set()
duplicates=[]
for n,e in enumerate(manifest,1):
 if e["title"] in seen: duplicates.append(n)
 seen.add(e["title"])
print("Repeated images to replace:",duplicates,flush=True)
extra={
 "yoga outdoors":["yoga woman outdoor exercise","yoga fitness park","yoga practice"],
 "healthy lifestyle":["healthy fitness walking","healthy food preparation","outdoor physical activity"],
 "cycling nature":["bicycle cycling park","cyclist bicycle","bike riding outdoors"],
 "strength training":["weight lifting gym","fitness workout dumbbells","bodyweight exercise"],
 "stretching":["stretching gym exercise","flexibility exercise","stretching legs"],
 "walking trail":["walking hiking path","forest footpath","pedestrian nature trail"],
 "fresh fruit":["fruit market apples","fresh berries fruits","fruit basket"],
 "exercise yoga":["yoga exercise pose","pilates exercise","outdoor yoga"],
 "morning sunshine":["sunrise landscape","morning walking","sunshine park"],
 "wellness lifestyle":["wellness spa nature","healthy living outdoors","relaxing nature"],
 "hiking backpack":["backpacker mountain hiking","hiking rucksack","mountain trail"],
 "movement exercise":["physical activity running","exercise outdoors","fitness park"],
 "nature walk":["walking in forest","nature footpath","hiking trail"],
 "office stretching":["office exercise desk","stretching at desk","workplace exercise"],
 "healthy posture":["ergonomic sitting","posture exercise","back stretching"],
 "physiotherapy exercise":["physical therapy exercise","rehabilitation exercise","exercise mat"],
 "balanced meal":["vegetable healthy lunch","healthy plate food","salad bowl"]
}
changed=0
for n in duplicates:
 q=queries[n-1]
 search_terms=extra.get(q,[])+[q+" photograph",q.split()[0]+" exercise",q]
 found=False
 for term in search_terms:
  for title,url,source,lic in candidates(term):
   if title in used:continue
   try:
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(request(url)))).convert("RGB")
    if im.width<1200 or im.height<700:continue
    im.thumbnail((1600,1200),Image.Resampling.LANCZOS)
    if im.width<1100:continue
    out=root/"images"/"editorial"/f"bodyadvice_{n:02d}.webp"
    im.save(out,"WEBP",quality=86,method=6)
    manifest[n-1]={"file":out.name,"title":title,"source":source,"license":lic,"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}
    used.add(title);changed+=1;found=True
    print("Unique replacement",n,title,flush=True)
    break
   except Exception as exc:print("Skipped",str(exc)[:100],flush=True)
  if found:break
 if not found:print("No distinct CC0 replacement found for",n,q,flush=True)
 time.sleep(.2)
if changed:
 manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 credits=["| Image | Source | License |","|---|---|---|"]
 for n,e in enumerate(manifest,1):credits.append(f"| {n:02d} | [{e['title']}]({e['source']}) | {e['license']} |")
 (root/"image-credits.md").write_text("# BodyAdvice editorial photo sources\n\nWikimedia Commons CC0 photographs, with original source links.\n\n"+"\n".join(credits)+"\n")
print("New distinct photos:",changed,"Remaining repeated:",40-len({e["title"] for e in manifest}),flush=True)
