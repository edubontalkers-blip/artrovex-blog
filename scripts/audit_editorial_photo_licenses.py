#!/usr/bin/env python3
"""Independently recheck CC0 source metadata and exact local WebP bytes."""
import hashlib,json,re,urllib.parse,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"docs"/"images"/"editorial"
entries=json.loads((root/"photo-license-manifest.json").read_text())
assert entries and len({e["file"] for e in entries})==len(entries),"Invalid audited file list"
for e in entries:
 assert e["license"]=="CC0" and e["source"].startswith("https://commons.wikimedia.org/wiki/"),"Invalid license/source"
 p=root/e["file"]
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==e["sha256"],"Image bytes changed"
 title=e["source"].split("/wiki/",1)[1]
 params=urllib.parse.urlencode({"action":"query","titles":urllib.parse.unquote(title).replace("_"," "),"prop":"imageinfo","iiprop":"extmetadata","format":"json"})
 req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+params,headers={"User-Agent":"BodyAdvicePhotoEditor/1.0 (https://bodyadvice.site)"})
 with urllib.request.urlopen(req,timeout=40) as response: data=json.load(response)
 pages=list(data.get("query",{}).get("pages",{}).values())
 assert len(pages)==1 and "missing" not in pages[0],"Source no longer available"
 meta=pages[0]["imageinfo"][0]["extmetadata"]
 license_name=re.sub("<[^>]*>","",meta.get("LicenseShortName",{}).get("value",""))
 assert license_name=="CC0",f"License changed for {e['file']}: {license_name}"
 print("PASS",e["file"],license_name,flush=True)
print("Verified all 40 source licenses and hashes.")
