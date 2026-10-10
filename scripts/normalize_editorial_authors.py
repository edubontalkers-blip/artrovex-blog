#!/usr/bin/env python3
"""Normalize editorial bylines in generated article HTML without inventing people."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1] / "docs" / "articles"
count = 0

def transform_json(node):
    if isinstance(node, dict):
        if node.get("@type") == "Article" and isinstance(node.get("author"), dict):
            node["author"] = {"@type": "Organization", "name": "Body Advice Editorial Team"}
        for val in node.values():
            transform_json(val)
    elif isinstance(node, list):
        for val in node:
            transform_json(val)

def rewrite_schema(match):
    try:
        obj = json.loads(match.group(2))
        transform_json(obj)
        return match.group(1) + json.dumps(obj, ensure_ascii=False) + match.group(3)
    except (ValueError, TypeError):
        return match.group(0)

pattern = re.compile(r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)
for path in root.glob("*.html"):
    before = path.read_text(encoding="utf-8")
    after = pattern.sub(rewrite_schema, before)
    # Match the exact legacy generator byline markup, not unrelated people in article prose.
    after = re.sub(
        r'(Written by\\s*<strong>)(?:Emma|James|Laura|Stefan|Monika|Andreas|Giulia|Marco|Valentina|Carmen|Miguel|Isabel|Sophie|Pierre|Marie)(</strong>)',
        r'\\1Body Advice Editorial Team\\2',
        after, flags=re.I
    )
    if after != before:
        path.write_text(after, encoding="utf-8")
        count += 1
print(f"Editorial author metadata normalized in {count} article files")
