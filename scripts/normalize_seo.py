#!/usr/bin/env python3
"""Normalize canonical URLs and reciprocal hreflang links using existing pages only."""
from pathlib import Path
import re

ROOT = Path("docs")
DOMAIN = "https://bodyadvice.site"
LANGS = ("en", "de", "it", "es", "fr")
def canonical(path):
    rel = path.relative_to(ROOT).as_posix()
    return DOMAIN + ("/" if rel == "index.html" else "/" + rel)

def fix():
    changed = 0
    for path in ROOT.rglob("*.html"):
        old = path.read_text(encoding="utf-8")
        content = old.replace("https://www.bodyadvice.site/", DOMAIN + "/")
        expected = canonical(path)
        content = re.sub(r"<link[^>]+rel=.canonical.[^>]*>", lambda m: '<link rel="canonical" href="' + expected + '">', content, count=1, flags=re.I)
        match = re.search(r"<html[^>]+lang=.([a-z]{2}).", content, flags=re.I)
        lang = match.group(1) if match else None
        suffix = re.search(r'-(en|de|it|es|fr)$', path.stem)
        if suffix and lang == suffix.group(1) and "</head>" in content:
            stem = path.stem[:-3]
            siblings = {code: path.with_name(stem + "-" + code + ".html") for code in LANGS}
            siblings = {code: target for code, target in siblings.items() if target.is_file()}
            if len(siblings) > 1:
                alternate = re.compile(r"<link[^>]+rel=.alternate.[^>]+hreflang=[^>]+>\\s*", re.I)
                content = alternate.sub("", content)
                tags = "".join('<link rel="alternate" hreflang="' + code + '" href="' + canonical(target) + '">\\n' for code,target in sorted(siblings.items()))
                content = re.sub(r'</head\\s*>', lambda m: tags + m.group(0), content, count=1, flags=re.I)
        if content != old:
            path.write_text(content, encoding="utf-8")
            changed += 1
    print("Normalized", changed, "HTML pages")
if __name__ == "__main__":
    fix()
