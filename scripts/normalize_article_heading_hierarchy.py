#!/usr/bin/env python3
"""Promote existing article section headings from H3 to H2 when H2 is absent.

No text is generated or removed; heading hierarchy only. All five languages.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]/"docs/articles"
changed=[]
for path in sorted(ROOT.glob("*.html")):
    html=path.read_text(encoding="utf-8")
    if re.search(r"<h2\b",html,re.I):
        continue
    # Only promote existing authored section headings inside article sections.
    pattern=re.compile(r'(<div\s+class="art-sec"[^>]*>\s*)<h3>(.*?)</h3>',re.S|re.I)
    n=len(pattern.findall(html))
    if n<2:
        continue
    revised=pattern.sub(lambda m:m.group(1)+"<h2>"+m.group(2)+"</h2>",html)
    revised=revised.replace(".art-sec h3{",".art-sec h2{")
    if revised!=html:
        path.write_text(revised,encoding="utf-8")
        changed.append((path.name,n))
print("SECTION HIERARCHY PAGES UPDATED:",len(changed))
print("SECTION HIERARCHY HEADINGS PROMOTED:",sum(n for _,n in changed))
for name,n in changed[:30]:
    print("H2 UPDATE",name,n)
