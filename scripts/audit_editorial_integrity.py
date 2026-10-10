#!/usr/bin/env python3
"""Non-destructive audit for Body Advice editorial integrity."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
generator = (root / "generate.py").read_text(encoding="utf-8")
issues = []
if 'author_name = authors.get(lang, authors["en"])' in generator:
    issues.append("Generator rotates fictional personal bylines.")
if '"@type": "Person"' in generator and '"jobTitle": "Wellness Blogger"' in generator:
    issues.append("Generator presents unverified authors as Person in Article schema.")
if 'meta name="keywords"' in generator[generator.find("def update_index("):generator.find("def generate_sitemap(")]:
    issues.append("Homepage generator still includes meta keyword stuffing.")
for lang in ("de", "it", "en", "es", "fr"):
    path = root / "docs" / "guides" / f"hydration-nutrition-{lang}.html"
    if not path.exists():
        issues.append(f"Missing editorial guide: {lang}")
print("Body Advice editorial audit")
for issue in issues:
    print("WARNING:", issue)
print(f"{len(issues)} issue(s) detected.")
sys.exit(1 if issues else 0)
