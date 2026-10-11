#!/usr/bin/env python3
"""Normalize canonical and reciprocal hreflang links across static HTML."""
from pathlib import Path
import re

ROOT = Path("docs")
DOMAIN = "https://bodyadvice.site"
LANGS = ("en", "de", "it", "es", "fr")
CANONICAL = re.compile(r'<link\b(?=[^>]*\brel=["\x27]canonical["\x27])[^>]*>\s*', re.I)
ALTERNATE = re.compile(r'<link\b(?=[^>]*\brel=["\x27]alternate["\x27])(?=[^>]*\bhreflang=)[^>]*>\s*', re.I)

def canonical(path):
    rel = path.relative_to(ROOT).as_posix()
    return DOMAIN + ("/" if rel == "index.html" else "/" + rel)

def fix():
    changed = 0
    for path in ROOT.rglob("*.html"):
        old = path.read_text(encoding="utf-8")
        content = old.replace("https://www.bodyadvice.site/", DOMAIN + "/")
        expected = canonical(path)
        # Replace all stale canonical tags and insert exactly one.
        content = CANONICAL.sub("", content)
        content = ALTERNATE.sub("", content)
        tags = ['<link rel="canonical" href="' + expected + '">']
        lang_match = re.search(r'<html\b[^>]*\blang=["\x27]([a-z]{2})["\x27]', content, re.I)
        language = lang_match.group(1) if lang_match else None
        suffix = re.search(r'-(en|de|it|es|fr)$', path.stem)
        if suffix and language == suffix.group(1):
            base = path.stem[:-3]
            siblings = {lang: path.with_name(base + "-" + lang + ".html") for lang in LANGS}
            siblings = {lang: target for lang, target in siblings.items() if target.is_file()}
            # Only reciprocal language clusters backed by real HTML files.
            if len(siblings) > 1:
                for lang, target in sorted(siblings.items()):
                    tags.append('<link rel="alternate" hreflang="' + lang + '" href="' + canonical(target) + '">')
        content, count = re.subn(r'</head\s*>', lambda m: "\n".join(tags) + "\n" + m.group(0), content, count=1, flags=re.I)
        if not count:
            print("WARNING: No head tag:", path)
        if content != old:
            path.write_text(content, encoding="utf-8")
            changed += 1
    print("Normalized", changed, "HTML pages")

if __name__ == "__main__":
    fix()
