#!/usr/bin/env python3
"""Remove leaked draft-generation text from quarantined article headings only."""
from pathlib import Path
import re

ROOT = Path("docs/articles")
HEADINGS = {
    "de": "Artikel in redaktioneller Prüfung",
    "it": "Articolo in revisione editoriale",
    "en": "Article under editorial review",
    "es": "Artículo en revisión editorial",
    "fr": "Article en cours de révision éditoriale",
}
changed = []
for path in sorted(ROOT.glob("*.html")):
    html = path.read_text(encoding="utf-8")
    if not re.search(r'<meta[^>]+name="robots"[^>]+content="noindex', html):
        continue
    lang = re.search(r'<html lang="(de|it|en|es|fr)"', html)
    if not lang:
        continue
    title = re.search(r'<title>(.*?)</title>', html, re.S)
    h1 = re.search(r'<h1(?:\\s[^>]*)?>(.*?)</h1>', html, re.S)
    if not title or not h1:
        continue
    leaked = ("Wait, that", "Hmm, let me think", "\\n\\n")
    if not any(marker in title.group(1) for marker in leaked) and not any(marker in h1.group(1) for marker in leaked):
        continue
    safe = HEADINGS[lang.group(1)]
    html = html[:title.start(1)] + safe + html[title.end(1):]
    h1 = re.search(r'<h1(?:\\s[^>]*)?>(.*?)</h1>', html, re.S)
    html = html[:h1.start(1)] + safe + html[h1.end(1):]
    path.write_text(html, encoding="utf-8")
    changed.append(str(path))
print("Cleaned quarantined article headings:", len(changed))
for name in changed:
    print(name)
