#!/usr/bin/env python3
"""Read-only review of editorial photo subject relevance and overuse."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ARTICLES=ROOT/"docs/articles"
IMAGES=ROOT/"docs/images/editorial"
manifest=json.loads((IMAGES/"photo-license-manifest.json").read_text(encoding="utf-8"))
titles={int(re.search(r"_(\d+)\.webp",x["file"]).group(1)):x["title"].lower() for x in manifest}
topics={
 "exercise":("exercise","fitness","gym","sport","yoga","pilates","weight","walking","hiking","running","cycling"),
 "food":("food","salad","vegetable","breakfast","cooking","fruit","apple","market"),
 "outdoors":("forest","trail","hiking","walking","beach","nature"),
 "relaxation":("meditation","yoga","mindfulness","relax"),
}
article_topics={
 "exercise":("exercise","muscle","massage","stretch","mobility","activation","release","workout","yoga","pilates"),
 "food":("food","diet","nutrition","meal","vegetable","breakfast","salad"),
 "outdoors":("walking","hiking","cycling","running","trail","outdoor"),
 "relaxation":("relax","sleep","stress","mindful","meditation"),
}
usage=Counter(); mismatches=[]; samples=defaultdict(list)
for path in sorted(ARTICLES.glob("*.html")):
    html=path.read_text(encoding="utf-8")
    m=re.search(r"/images/editorial/bodyadvice_(\d{2})\.webp",html)
    if not m:continue
    num=int(m.group(1));usage[num]+=1
    slug=path.stem.lower()
    categories={k for k,words in article_topics.items() if any(w in slug for w in words)}
    image_categories={k for k,words in topics.items() if any(w in titles.get(num,"") for w in words)}
    if categories and image_categories and not (categories & image_categories):
        mismatches.append((path.name,num))
        if len(samples[num])<5:samples[num].append(path.name)
print("PHOTOS AVAILABLE:",len(manifest),"PHOTOS USED:",len(usage))
print("PHOTO USAGE:",dict(sorted(usage.items())))
print("POTENTIAL SUBJECT MISMATCHES:",len(mismatches))
for num in sorted(samples):
    print("REVIEW",num,titles.get(num,""),samples[num])
print("NOTE: Keyword matching is triage only; visually review images before reassignment.")
