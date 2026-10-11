#!/usr/bin/env python3
"""Add deterministic, accessible editorial photography to existing and new pages."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1] / "docs"
IMAGES = "/images/editorial/"
MARKER = "data-editorial-photo=\"v1\""
STYLE = """
<style id="editorial-photo-style">
.editorial-photo{margin:22px 0 32px;overflow:hidden;border-radius:14px;background:#e6ede6;max-width:320px;box-shadow:0 4px 12px rgba(17,57,43,.08)}
.editorial-photo img{display:block;width:100%;height:auto;aspect-ratio:192/174;object-fit:cover;object-position:center}
.editorial-photo figcaption{font:13px/1.5 system-ui,sans-serif;color:#52695b;padding:9px 14px;background:#f5f8f3}
@media(max-width:600px){.editorial-photo{margin:16px 0 24px;border-radius:12px}.editorial-photo img{height:auto}}
</style>
"""
CATEGORY = {
    "body-health": 37,
    "healthy-living": 6,
    "exercises": 4,
    "nutrition": 5,
    "mind-balance": 23,
    "travel-activity": 31,
}
ALT = {
    "en": "Lifestyle and wellbeing editorial photograph",
    "de": "Redaktionelles Foto zu Alltag und Wohlbefinden",
    "it": "Fotografia editoriale sul benessere quotidiano",
    "es": "Fotografía editorial sobre bienestar cotidiano",
    "fr": "Photo éditoriale sur le bien-être au quotidien",
}

def choose(path):
    stem = path.stem.lower()
    for name, num in CATEGORY.items():
        if name in stem:
            return num
    if any(t in stem for t in ("foot", "toe", "walk", "hiking", "travel", "cycling")):
        pool = [6, 15, 31, 34]
    elif any(t in stem for t in ("food", "nutrition", "diet", "hydration")):
        pool = [5, 10, 17]
    elif any(t in stem for t in ("neck", "shoulder", "back", "muscle", "stretch", "exercise")):
        pool = [4, 23, 37, 29]
    else:
        pool = [4, 5, 6, 15, 23, 31, 37]
    index = int(hashlib.sha256(stem.encode()).hexdigest()[:8], 16) % len(pool)
    return pool[index]

def process(path):
    html = path.read_text(encoding="utf-8")
    if MARKER in html or "editorial-photo-style" in html:
        revised = re.sub(r'<style id="editorial-photo-style">.*?</style>', STYLE.strip(), html, count=1, flags=re.S)
        if revised != html:
            path.write_text(revised, encoding="utf-8")
            return True
        return False
    if not re.search(r"<h1\b[^>]*>", html, re.I):
        return False
    language = re.search(r'<html\b[^>]*\blang=["\']([a-z]{2})', html, re.I)
    lang = language.group(1) if language else "en"
    num = choose(path)
    img = ROOT / "images" / "editorial" / f"bodyadvice_{num:02d}.webp"
    if not img.exists():
        print("Missing photo:", img)
        return False
    alt = ALT.get(lang, ALT["en"])
    figure = (f'<figure class="editorial-photo" {MARKER}>'
              f'<img src="{IMAGES}bodyadvice_{num:02d}.webp" alt="{alt}" '
              f'loading="lazy" decoding="async" width="192" height="174"></figure>')
    # Insert immediately after the first page title; avoid modifying title text.
    html, count = re.subn(r"(</h1\s*>)", lambda m: m.group(1) + "\n" + figure, html, count=1, flags=re.I)
    if not count:
        return False
    html = re.sub(r"</head\s*>", STYLE + "\n</head>", html, count=1, flags=re.I)
    path.write_text(html, encoding="utf-8")
    return True

def main():
    files = list((ROOT / "articles").glob("*.html")) + list((ROOT / "topics").glob("*.html"))
    files += list((ROOT / "guides").rglob("*.html")) + list((ROOT / "info").rglob("*.html"))
    files += [p for p in ROOT.glob("articles-*.html")]
    changed = sum(process(p) for p in files)
    print(f"Editorial photography added to {changed} pages; examined {len(files)}.")

if __name__ == "__main__":
    main()
