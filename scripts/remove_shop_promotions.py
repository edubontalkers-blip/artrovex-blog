#!/usr/bin/env python3
"""Remove public shop promotions and provide a neutral collaboration route."""
from pathlib import Path
import re

ROOT = Path("docs")
for path in ROOT.rglob("*.html"):
    if path.name in {"collaboration.html", "thank-you.html"}:
        continue
    html = path.read_text(encoding="utf-8")
    old = html
    # Delete external shop anchor elements rather than leaving dead links.
    html = re.sub(r'<a\b[^>]*href=["\']https?://(?:www\.)?artrovex\.shop[^"\']*["\'][^>]*>.*?</a>', "", html, flags=re.I | re.S)
    # Remove plain-text domain mentions.
    html = re.sub(r'(?:https?://)?(?:www\.)?artrovex\.shop(?:/[\w/-]+)?', "", html, flags=re.I)
    # Remove stranded shop-only navigation.
    html = re.sub(r'<a\b[^>]*>\s*(?:🛍\s*)?(?:Shop|Official store|Offizieller Shop|Tienda oficial|Boutique officielle)\s*</a>', "", html, flags=re.I)
    # Collaboration contact on the main page and About, avoiding duplicate links.
    if path.name in {"index.html", "about.html"} and 'href="/collaboration.html"' not in html:
        html = html.replace("</nav>", '<a href="/collaboration.html">Collaboration</a></nav>', 1)
    if html != old:
        path.write_text(html, encoding="utf-8")
