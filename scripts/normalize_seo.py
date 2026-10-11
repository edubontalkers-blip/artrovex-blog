#!/usr/bin/env python3
"""Normalize internal canonical/hreflang URLs across generated HTML pages."""
from pathlib import Path
from html.parser import HTMLParser
import re

ROOT = Path("docs")
DOMAIN = "https://bodyadvice.site"
LANGS = ("en", "de", "it", "es", "fr")

def canonical(path):
    relative = path.relative_to(ROOT).as_posix()
    return DOMAIN + ("/" if relative == "index.html" else "/" + relative)

def fix():
    modified = 0
    for path in ROOT.rglob("*.html"):
        original = path.read_text(encoding="utf-8")
        expected = canonical(path)
        content = original
        # Normalize only internal URL hosts, never unrelated external domains.
        content = re.sub(r'https://www\.bodyadvice\.site(?=[/"\'?#]|$)', DOMAIN, content)
        content = re.sub(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']+(["\'])', lambda m: m[1] + expected + m[2], content, count=1)
        # Self-reference is mandatory if the document advertises a hreflang cluster.
        match = re.search(r'<html\b[^>]*\blang=["\']([a-z]{2})["\']', content)
        language = match.group(1) if match else None
        if language in LANGS and 'hreflang=' in content:
            self_tag = re.compile(r'<link\b(?=[^>]*\brel=["\']alternate["\'])(?=[^>]*\bhreflang=["\']' + language + r'["\'])[^>]*>', re.I)
            if self_tag.search(content):
                content = self_tag.sub(lambda m: re.sub(r'href=["\'][^"\']+["\']', 'href="' + expected + '"', m.group(0)), content, count=1)
            else:
                head = re.search(r'</head\s*>', content, re.I)
                if head:
                    content = content[:head.start()] + f'<link rel="alternate" hreflang="{language}" href="{expected}">\n' + content[head.start():]

        # Rebuild reciprocal language links only from actual sibling translations.
        # Do not advertise missing translations or redirect to unrelated pages.
        stem = path.stem
        suffix = re.search(r'-(en|de|it|es|fr)
            path.write_text(content, encoding="utf-8")
            modified += 1
    print(f"Normalized canonical and hreflang in {modified} HTML files")

if __name__ == "__main__":
    fix()
, stem)
        if suffix and language == suffix.group(1):
            base = stem[:-3]
            siblings = {lang: path.with_name(base + "-" + lang + ".html")
                        for lang in LANGS}
            siblings = {lang: sibling for lang, sibling in siblings.items()
                        if sibling.is_file()}
            if len(siblings) > 1:
                alternate_tag = re.compile(r'<link\\b(?=[^>]*\\brel=[\\"\\']alternate[\\"\\'])(?=[^>]*\\bhreflang=[\\"\\'])[^>]*>\\s*', re.I)
                content = alternate_tag.sub("", content)
                tags = "".join(f'<link rel="alternate" hreflang="{lang}" href="{canonical(sibling)}">\\n'
                               for lang, sibling in sorted(siblings.items()))
                content = re.sub(r'</head\\s*>', lambda m: tags + m.group(0), content, count=1, flags=re.I)
        if content != original:
            path.write_text(content, encoding="utf-8")
            modified += 1
    print(f"Normalized canonical and hreflang in {modified} HTML files")

if __name__ == "__main__":
    fix()
