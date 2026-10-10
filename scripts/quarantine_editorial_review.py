#!/usr/bin/env python3
"""Temporarily noindex unverified personal-experience articles pending human review."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
hold = ROOT / "audits" / "title-triage-2026-10-11.json"
data = json.loads(hold.read_text(encoding="utf-8"))
count = 0
for item in data["flagged_articles"]:
    path = ROOT / "docs" / item["file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    html = path.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name=["\']robots["\']', html, flags=re.I):
        html = re.sub(r'<meta\s+name=["\']robots["\'][^>]*>', '<meta name="robots" content="noindex,follow">', html, count=1, flags=re.I)
    elif "</head>" in html:
        html = html.replace("</head>", '<meta name="robots" content="noindex,follow">\n</head>', 1)
    else:
        raise ValueError("Missing head in " + str(path))
    path.write_text(html, encoding="utf-8")
    count += 1
print("Applied noindex to", count, "pending-review articles")
