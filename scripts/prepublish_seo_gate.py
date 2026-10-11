#!/usr/bin/env python3
"""Prepublication content and SEO gate for BodyAdvice articles (read-only)."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys

ROOT=Path("docs")
ARTICLES=ROOT/"articles"
LANGS={"de","it","en","es","fr"}
CLAIM_PATTERNS = [
    re.compile("\\b(?:cures?|treats?|prevents?|heals?)\\s+(?:arthritis|disease|inflammation|chronic pain)\\b", re.I),
    re.compile("\\b(?:guaranteed|permanent)\\s+(?:pain relief|recovery|cure)\\b", re.I),
    re.compile("\\b(?:cura|trata|previene|elimina)\\s+(?:la\\s+)?(?:artritis|inflamaci[oó]n|dolor cr[oó]nico)\\b", re.I),
    re.compile("\\b(?:guarisce|cura|previene|elimina)\\s+(?:l[’']?)?(?:artrite|infiammazione|dolore cronico)\\b", re.I),
    re.compile("\\b(?:heilt|behandelt|verhindert|beseitigt)\\s+(?:arthritis|entz[uü]ndungen|chronische schmerzen)\\b", re.I),
    re.compile("\\b(?:gu[eé]rit|traite|pr[eé]vient|[eé]limine)\\s+(?:l[’']?)?(?:arthrite|inflammation|douleur chronique)\\b", re.I),
]

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.title="";self.h1=[];self.h2=[];self.meta=[];self.canon=[];self.lang="";self.img=[];self.links=[];self.noindex=False;self._capture=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html":self.lang=a.get("lang","")
        if tag=="title":self._capture="title"
        if tag in ("h1","h2"):self._capture=tag;getattr(self,tag).append("")
        if tag=="meta" and a.get("name","").lower()=="description":self.meta.append(a.get("content",""))
        if tag=="meta" and a.get("name","").lower()=="robots" and "noindex" in a.get("content","").lower():self.noindex=True
        if tag=="link" and a.get("rel")=="canonical":self.canon.append(a.get("href",""))
        if tag=="img":self.img.append(a)
        if tag=="a" and a.get("href"):self.links.append(a["href"])
    def handle_endtag(self,tag):
        if tag==self._capture:self._capture=None
    def handle_data(self,data):
        if self._capture=="title":self.title+=data
        elif self._capture in ("h1","h2"):
            arr=getattr(self,self._capture)
            if arr:arr[-1]+=data

def audit(path):
    p=Page();p.feed(path.read_text(encoding="utf-8"))
    errors=[];warnings=[]
    if p.lang not in LANGS:errors.append("unsupported/missing HTML language")
    if not p.title.strip():errors.append("missing title")
    elif not 25<=len(p.title.strip())<=75:warnings.append("title length outside editorial guideline")
    if len(p.h1)!=1 or not p.h1[0].strip():errors.append("requires exactly one meaningful H1")
    if not p.noindex and (len(p.meta)!=1 or not p.meta[0].strip()):errors.append("requires unique meta description")
    elif not p.noindex and not 70<=len(p.meta[0])<=180:warnings.append("meta description length outside guideline")
    if not p.noindex and not p.h2:warnings.append("no H2 section headings")
    expected="https://bodyadvice.site/"+path.relative_to(ROOT).as_posix()
    if p.canon!=[expected]:errors.append("canonical must equal own published URL")
    if not p.img:errors.append("missing article illustration")
    for i in p.img:
        if not i.get("alt","").strip():errors.append("image without alt text")
        src=i.get("src","").split("?",1)[0]
        if src.startswith("/") and not (ROOT/src.lstrip("/")).is_file():errors.append("missing local image")
    if not p.noindex and not any("articles/" in href or href.endswith(".html") for href in p.links):warnings.append("no editorial internal links")
    raw = path.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", raw)
    searchable = " ".join([text, p.title, *p.meta, *[i.get("alt", "") for i in p.img]])
    for pattern in CLAIM_PATTERNS:
        for match in pattern.finditer(searchable):
            start = max(0, match.start() - 240)
            end = min(len(searchable), match.end() + 180)
            context = searchable[start:end].lower()
            # Quotes describing fraudulent sellers are not endorsements.
            # Still surface them for human review, but do not block automatically.
            counterfeit = any(word in context for word in (
                "fälschung", "fälschungen", "falsific", "contraffatt",
                "counterfeit", "fake seller", "contrefaçon", "contrefaçons",
                "claims we never made", "niemals gemacht", "nunca hemos",
                "mai fatto", "jamais fait"
            ))
            rejected = any(word in context for word in ("niemals", "nunca", "mai ", "jamais", "never", "not true", "falsch", "false", "falso", "fausse"))
            if counterfeit and rejected:
                warnings.append("quoted third-party medical claim; review context: " + match.group(0))
            else:
                errors.append("potential medical claim: " + match.group(0))
    if not p.noindex and len(text.split())<250:warnings.append("short article; review depth and search intent")
    return errors,warnings,p

def main():
    files=sorted(ARTICLES.glob("*.html"))
    failures=[];warnings=[];titles=Counter();descriptions=Counter()
    for f in files:
        err,warn,p=audit(f)
        if not p.noindex:
            titles[(p.lang,p.title.strip().casefold())]+=1
            descriptions[(p.lang,p.meta[0].strip().casefold() if p.meta else "")]+=1
        failures.extend((f.name,e) for e in err)
        warnings.extend((f.name,w) for w in warn)
    for f in files:
        _,_,p=audit(f)
        if not p.noindex and p.title and titles[(p.lang,p.title.strip().casefold())]>1:failures.append((f.name,"duplicate title within language"))
        if not p.noindex and p.meta and descriptions[(p.lang,p.meta[0].strip().casefold())]>1:failures.append((f.name,"duplicate description within language"))
    print(f"Articles: {len(files)}; blocking issues: {len(failures)}; editorial warnings: {len(warnings)}")
    for f,e in failures[:60]:print("BLOCK",f,e)
    for f,e in warnings[:30]:print("REVIEW",f,e)
    print("Human editorial approval remains mandatory: pattern matching does not guarantee claim-free content.")
    if failures:sys.exit(1)

if __name__=="__main__":main()
