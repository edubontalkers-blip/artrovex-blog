#!/usr/bin/env python3
"""Promote existing article section headings from H3 to H2 when H2 is absent.

No text is generated or removed; heading hierarchy only. All five languages.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]/"docs/articles"
TITLE_SUFFIX=" | Body Advice Wellness Blog"
title_fixes=0
changed=[]
for path in sorted(ROOT.glob("*.html")):
    html=path.read_text(encoding="utf-8")
    original=html
    if 'content="noindex' not in html:
        m=re.search(r"<title>([^<]+)</title>",html)
        if m and len(m.group(1))>75 and m.group(1).endswith(TITLE_SUFFIX):
            short=m.group(1)[:-len(TITLE_SUFFIX)]
            if 25<=len(short)<=75:
                html=html[:m.start(1)]+short+html[m.end(1):]
                title_fixes+=1
    if re.search(r"<h2\b",html,re.I):
        continue
    # Only promote existing authored section headings inside article sections.
    pattern=re.compile(r'(<div\s+class="art-sec"[^>]*>\s*)<h3>(.*?)</h3>',re.S|re.I)
    n=len(pattern.findall(html))
    if n<2:
        if html!=original:path.write_text(html,encoding="utf-8")
        continue
    revised=pattern.sub(lambda m:m.group(1)+"<h2>"+m.group(2)+"</h2>",html)
    revised=revised.replace(".art-sec h3{",".art-sec h2{")
    if revised!=html:
        path.write_text(revised,encoding="utf-8")
        changed.append((path.name,n))
print("TITLE SUFFIX FIXES:",title_fixes)
print("SECTION HIERARCHY PAGES UPDATED:",len(changed))
print("SECTION HIERARCHY HEADINGS PROMOTED:",sum(n for _,n in changed))
for name,n in changed[:30]:
    print("H2 UPDATE",name,n)
