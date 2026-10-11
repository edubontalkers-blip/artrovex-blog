#!/usr/bin/env python3
"""Normalize canonical and reciprocal hreflang for existing translated pages only."""
from pathlib import Path
from html.parser import HTMLParser
import re

ROOT = Path("docs")
DOMAIN = "https://bodyadvice.site"
LANGS = ("en", "de", "it", "es", "fr")
CANON = re.compile(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>\s*', re.I)
ALT = re.compile(r'<link\b(?=[^>]*\brel=["\']alternate["\'])(?=[^>]*\bhreflang=["\'])[^>]*>\s*', re.I)
HEAD = re.compile(r'</head\s*>', re.I)
SUFFIX = re.compile(r'-(en|de|it|es|fr)$')

def canonical(path):
    rel = path.relative_to(ROOT).as_posix()
    return DOMAIN + ("/" if rel == "index.html" else "/" + rel)

def main():
    paths = sorted(ROOT.rglob("*.html"))
    groups = {}
    for path in paths:
        match = SUFFIX.search(path.stem)
        if match:
            key = (path.parent, path.stem[:-3])
            groups.setdefault(key, {})[match.group(1)] = path
    changed = 0
    for path in paths:
        source = path.read_text(encoding="utf-8")
        if not HEAD.search(source):
            continue
        content = CANON.sub("", source)
        content = ALT.sub("", content)
        match = SUFFIX.search(path.stem)
        tags = [f'<link rel="canonical" href="{canonical(path)}">']
        if match:
            siblings = groups.get((path.parent, path.stem[:-3]), {})
            if len(siblings) > 1:
                tags.extend(f'<link rel="alternate" hreflang="{lang}" href="{canonical(sibling)}">'
                            for lang, sibling in sorted(siblings.items()))
        content = HEAD.sub(lambda m: "\n".join(tags) + "\n" + m.group(0), content, count=1)
        if content != source:
            path.write_text(content, encoding="utf-8")
            changed += 1
    print(f"Normalized SEO in {changed} / {len(paths)} HTML pages")

if __name__ == "__main__":
    main()
