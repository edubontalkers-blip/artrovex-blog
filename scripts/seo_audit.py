#!/usr/bin/env python3
"""Read-only site audit. Never modifies production or source files."""
import collections
import html.parser
import json
import pathlib
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path("docs")
DOMAIN = "https://bodyadvice.site"
issues = collections.Counter()
examples = collections.defaultdict(list)

def report(kind, source, detail):
    issues[kind] += 1
    if len(examples[kind]) < 12:
        examples[kind].append(f"{source}: {detail}")

class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.alts, self.canonicals, self.langlinks = [], [], [], [], []
        self.html_lang = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.html_lang = a.get("lang", "")
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img":
            self.images.append(a.get("src", ""))
            if not a.get("alt", "").strip(): self.alts.append(a.get("src", ""))
        if tag == "link":
            if a.get("rel") == "canonical": self.canonicals.append(a.get("href", ""))
            if a.get("rel") == "alternate" and a.get("hreflang"):
                self.langlinks.append((a["hreflang"], a.get("href", "")))

def local_path(href):
    from urllib.parse import urlsplit, unquote
    if href.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "//")): return None
    if href.startswith(("http:", "https:")):
        u = urlsplit(href)
        if u.netloc.lower() not in ("bodyadvice.site", "www.bodyadvice.site"): return None
        path = unquote(u.path)
    else:
        path = unquote(urlsplit(href).path)
    return path

def exists_link(path, source):
    if not path: return True
    if path.startswith("/"): target = ROOT / path.lstrip("/")
    else: target = source.parent / path
    if target.is_dir(): target = target / "index.html"
    if target.suffix == "" and not target.exists(): target = target / "index.html"
    try:
        target.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    return target.is_file()

def canonical_url_for_file(path):
    rel = path.relative_to(ROOT).as_posix()
    return DOMAIN + ("/" if rel == "index.html" else "/" + rel)

pages = list(ROOT.rglob("*.html"))
page_alternates = {}
page_languages = {}
page_canonicals = {}
print(f"HTML pages: {len(pages)}")
for source in pages:
    try: content = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report("encoding", source, "invalid UTF-8"); continue
    p = PageParser()
    try: p.feed(content)
    except Exception as e: report("html_parse", source, str(e))
    if not p.html_lang: report("missing_html_lang", source, "missing lang")
    page_alternates[canonical_url_for_file(source)] = dict(p.langlinks)
    page_languages[canonical_url_for_file(source)] = p.html_lang
    page_canonicals[canonical_url_for_file(source)] = p.canonicals
    for href in p.links:
        path = local_path(href)
        if path is not None and not exists_link(path, source):
            report("broken_internal_link", source, href)
    for src in p.images:
        path = local_path(src)
        if path is not None and not exists_link(path, source):
            report("missing_local_image", source, src)
    for src in p.alts: report("missing_image_alt", source, src)
    expected = DOMAIN + "/" + (str(source.relative_to(ROOT)) if source.name != "index.html" else str(source.parent.relative_to(ROOT)).replace(".", ""))
    if not p.canonicals: report("missing_canonical", source, expected)
    elif len(p.canonicals) != 1: report("duplicate_canonical", source, p.canonicals)
    elif p.canonicals[0] != expected: report("canonical_mismatch", source, f"{p.canonicals[0]} expected {expected}")
    if p.langlinks and p.html_lang and not any(lang == p.html_lang and url == expected for lang, url in p.langlinks):
        report("hreflang_missing_self", source, expected)
    for blob in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.S | re.I):
        try: json.loads(blob)
        except Exception as e: report("invalid_jsonld", source, str(e))

# Verify reciprocal hreflang clusters and real local targets, not just self references.
for source_url, alternates in page_alternates.items():
    for lang, target in alternates.items():
        if lang == "x-default":
            continue
        if target not in page_alternates:
            report("hreflang_missing_target", source_url, f"{lang}: {target}")
            continue
        if page_languages[target] != lang:
            report("hreflang_wrong_language", source_url, f"{lang}: {target} is {page_languages[target]}")
        if page_alternates[target].get(page_languages[source_url]) != source_url:
            report("hreflang_not_reciprocal", source_url, f"{lang}: {target}")
        if page_canonicals[target] != [target]:
            report("hreflang_target_not_canonical", source_url, target)

tree = ET.parse(ROOT / "sitemap.xml")
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [x.text for x in tree.findall("s:url/s:loc", ns)]
print(f"Sitemap URLs: {len(urls)}")
for url in urls:
    path = local_path(url)
    if path is None or not exists_link(path, ROOT / "index.html"):
        report("missing_sitemap_target", "sitemap.xml", url)
if len(urls) != len(set(urls)): report("duplicate_sitemap_urls", "sitemap.xml", str(len(urls)-len(set(urls))))
for path in ("sitemap.xml", "robots.txt"):
    for ua in ("Mozilla/5.0", "Googlebot"):
        url = DOMAIN + "/" + path
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()
                print(f"REMOTE {url} UA={ua} HTTP={response.status} CT={response.headers.get('Content-Type')} bytes={len(data)} final={response.url}")
                if response.status != 200 or not data: report("remote_bad_response", url, str(response.status))
        except Exception as e:
            report("remote_fetch_failed", url, f"{ua}: {type(e).__name__} {e}")
print("AUDIT COUNTS:", json.dumps(issues, sort_keys=True))
for kind, items in examples.items():
    print(f"\\n[{kind}]")
    for item in items: print("  " + item)
if any(issues[k] for k in ("missing_sitemap_target", "duplicate_sitemap_urls", "invalid_jsonld", "hreflang_missing_target", "hreflang_wrong_language", "hreflang_not_reciprocal", "hreflang_target_not_canonical")):
    raise SystemExit("Critical audit errors")
