#!/usr/bin/env python3
"""Read-only editorial photo integration audit."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "docs" / "articles"
IMAGES = ROOT / "docs" / "images" / "editorial"

class Photos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.figures = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "figure" and "data-editorial-photo" in a:
            self.figures.append(a["data-editorial-photo"])
        if tag == "img":
            self.images.append(a)

def main():
    files = sorted(ARTICLES.glob("*.html"))
    actual = {p.name for p in IMAGES.glob("bodyadvice_*.webp")}
    expected = {f"bodyadvice_{i:02d}.webp" for i in range(1, 41)}
    errors = []
    if actual != expected:
        errors.append(f"Inventory mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for name in sorted(actual):
        data = (IMAGES / name).read_bytes()
        if not (data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
            errors.append(f"Invalid WebP header: {name}")
        if len(data) < 1024:
            errors.append(f"Suspiciously small: {name}")
    usage = Counter()
    for page in files:
        p = Photos()
        p.feed(page.read_text(encoding="utf-8"))
        if len(p.figures) != 1:
            errors.append(f"{page.name}: expected one editorial figure, got {len(p.figures)}")
        for figure in p.figures:
            try: usage[int(figure)] += 1
            except ValueError: errors.append(f"{page.name}: invalid figure number {figure}")
        for img in p.images:
            src = img.get("src", "")
            if "images/editorial/bodyadvice_" not in src: continue
            target = (page.parent / src.split("?", 1)[0]).resolve()
            if not target.is_file():
                errors.append(f"{page.name}: missing image {src}")
            if not img.get("alt", "").strip():
                errors.append(f"{page.name}: missing alt text {src}")
        for number in p.figures:
            matching = [i for i in p.images if i.get("src", "").endswith(f"bodyadvice_{number}.webp")]
            if not matching:
                errors.append(f"{page.name}: figure {number} does not match an img")
    print(f"Articles audited: {len(files)}")
    print(f"Editorial WebP assets: {len(actual)}")
    print(f"Photo usage: {dict(sorted(usage.items()))}")
    print(f"Unused photos: {[i for i in range(1,41) if not usage[i]]}")
    print(f"Errors: {len(errors)}")
    for e in errors[:80]: print("ERROR:", e)
    if errors: sys.exit(1)

if __name__ == "__main__":
    main()
