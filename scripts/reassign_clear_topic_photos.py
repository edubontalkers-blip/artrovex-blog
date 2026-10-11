#!/usr/bin/env python3
"""Conservative batch photo reassignment for unambiguous article subjects.

Only update a photograph when the filename names an explicit activity.
Never change noindex review pages or image licenses; preserve existing alt text.
"""
from collections import Counter
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]/"docs/articles"
# Specific subject matches with a visually documented matching subject in manifest.
RULES=(
    (re.compile(r"(?:hiking|hike|trekking|mountain-walk)",re.I), (12,16,31)),
    (re.compile(r"(?:running|jogging|runner)",re.I), (8,)),
    (re.compile(r"(?:cycling|bicycle|biking|cyclist)",re.I), (26,)),
    (re.compile(r"(?:yoga|yogic)",re.I), (15,19)),
    (re.compile(r"(?:pilates)",re.I), (24,)),
    (re.compile(r"(?:weight-lifting|weightlifting)",re.I), (14,)),
)
PHOTO=re.compile(r'(?P<prefix>/images/editorial/bodyadvice_)(?P<number>\d{2})(?P<suffix>\.webp)')
usage=Counter()
changed=[]
for page in sorted(ROOT.glob("*.html")):
    raw=page.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*noindex',raw,re.I):
        continue
    matches=[(name,choices) for name,choices in RULES if name.search(page.stem)]
    if len(matches)!=1:
        continue
    m=PHOTO.search(raw)
    if not m:
        continue
    choices=matches[0][1]
    old=int(m.group("number"))
    if old in choices:
        usage[old]+=1
        continue
    # Distribute within the SAME subject, not across unrelated images.
    selected=min(choices,key=lambda number:(usage[number],number))
    candidate=f"bodyadvice_{selected:02d}.webp"
    if not (ROOT.parent/"images/editorial"/candidate).is_file():
        raise RuntimeError("Missing image "+candidate)
    updated=raw[:m.start("number")]+f"{selected:02d}"+raw[m.end("number"):]
    if updated!=raw:
        page.write_text(updated,encoding="utf-8")
        changed.append((page.name,old,selected))
        usage[selected]+=1
print("TOPICALLY MATCHED PHOTO UPDATES:",len(changed))
print("MATCHED PHOTO USAGE:",dict(usage))
for item in changed[:40]:
    print("PHOTO UPDATE",*item)
