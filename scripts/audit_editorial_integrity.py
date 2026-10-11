#!/usr/bin/env python3
"""Non-destructive audit for Body Advice editorial integrity."""
from pathlib import Path
import re
import sys
import json
from collections import Counter

root = Path(__file__).resolve().parents[1]
generator = (root / "generate.py").read_text(encoding="utf-8")
issues = []
if 'author_name = authors.get(lang, authors["en"])' in generator or "authors_by_lang = {" in generator:
    issues.append("Generator still assigns unverified personal bylines.")
if '"jobTitle": "Wellness Blogger"' in generator:
    issues.append("Generator presents unverified authors as Person in Article schema.")
if 'meta name="keywords"' in generator[generator.find("def update_index("):generator.find("def generate_sitemap(")]:
    issues.append("Homepage generator still includes meta keyword stuffing.")
for lang in ("de", "it", "en", "es", "fr"):
    path = root / "docs" / "guides" / f"hydration-nutrition-{lang}.html"
    if not path.exists():
        issues.append(f"Missing editorial guide: {lang}")
# Audit every catalogued article, not just generator templates.
catalog = json.loads((root / "docs" / "articles_meta.json").read_text(encoding="utf-8"))
seen = set()
flags = []
missing = []
sensitive = ("cricoid", "carotid", "jugular", "throat", "swallowing", "lymph node")
first_person = re.compile(
    r"\b(?:my|i've|i learned|what i do|my clients|my patients|"
    r"mein(?:e|em|en)?|ich|meine kunden|"
    r"ma routine|mon expérience|mes clients|j'ai|je fais|"
    r"mi rutina|mis clientes|aprendí|me dolía|"
    r"la mia|ho imparato|quello che faccio|i miei clienti)\b",
    re.IGNORECASE
)
for item in catalog:
    rel = item.get("file", "")
    if rel in seen:
        issues.append("Duplicate catalog entry: " + rel)
    seen.add(rel)
    path = root / "docs" / rel
    if not path.is_file():
        missing.append(rel)
        continue
    html = path.read_text(encoding="utf-8")
    title = item.get("title", "")
    if first_person.search(title):
        flags.append({"file": rel, "reason": "first-person headline requires editorial verification", "title": title})
    if any(term in (item.get("topic", "") + " " + rel).lower() for term in sensitive):
        flags.append({"file": rel, "reason": "sensitive anatomy requires clinical review"})
    if html.count("<div") != html.count("</div>"):
        flags.append({"file": rel, "reason": "possible unmatched div elements"})
    if "<h1" not in html:
        flags.append({"file": rel, "reason": "missing h1"})
    if 'name="robots" content="noindex' in html:
        flags.append({"file": rel, "reason": "noindex page still in catalog"})
# Do not treat flagged material as reviewed or approved.
if flags:
    print("EDITORIAL REVIEW REQUIRED:", len(flags), "flags; review report generated (not approved).")
if missing:
    issues.append(str(len(missing)) + " catalogued HTML files missing")
report = {"catalogued": len(catalog), "languages": dict(Counter(m.get("lang") for m in catalog)),
          "missing": missing, "editorial_review_count": len(flags), "editorial_review": flags}
report_path = root / "editorial-audit.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + chr(10), encoding="utf-8")
print("Editorial review flags:", len(flags), "| Missing HTML:", len(missing))
print("Report:", report_path)
print("Body Advice editorial audit")
for issue in issues:
    print("WARNING:", issue)
print(f"{len(issues)} issue(s) detected.")
sys.exit(1 if issues else 0)
