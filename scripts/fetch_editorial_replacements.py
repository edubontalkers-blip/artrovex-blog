#!/usr/bin/env python3
"""Download four distinct editorial replacements from Wikimedia Commons, verifying CC0."""
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images" / "editorial"
SOURCES = {
    33: "File:Maintaining a healthy lifestyle.jpg",
    36: "File:Walking in Park.jpg",
    37: "File:Yoga and fitness work out.jpg",
    38: "File:Wikimedia Nigeria Imo State Network Fitness Walk and Exercise 3.jpg",
}
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "BodyAdviceEditorial/1.0 (editorial license verification)"}

def fetch(url):
    with urlopen(Request(url, headers=HEADERS), timeout=40) as response:
        return response.read()

def main():
    pending = {}
    hashes = set()
    for number, title in SOURCES.items():
        from urllib.parse import urlencode
        url = API + "?" + urlencode({
            "action": "query", "format": "json", "titles": title,
            "prop": "imageinfo", "iiprop": "url|extmetadata",
        })
        payload = json.loads(fetch(url))
        page = next(iter(payload["query"]["pages"].values()))
        info = page["imageinfo"][0]
        meta = info["extmetadata"]
        license_code = meta.get("LicenseShortName", {}).get("value", "").strip().upper()
        if license_code != "CC0":
            raise ValueError(f"{title}: license is {license_code!r}, not CC0")
        data = fetch(info["url"])
        with Image.open(io.BytesIO(data)) as opened:
            im = ImageOps.exif_transpose(opened)
            im.load()
            if im.width < 500 or im.height < 300:
                raise ValueError(f"{title}: source too small: {im.size}")
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")
            buffer = io.BytesIO()
            im.save(buffer, format="WEBP", quality=88, method=6)
            encoded = buffer.getvalue()
        digest = hashlib.sha256(encoded).hexdigest()
        if digest in hashes:
            raise ValueError(f"Duplicate image: {title}")
        hashes.add(digest)
        pending[number] = encoded
        print(f"{number}: {title}: CC0; original {im.width}x{im.height}; WebP {len(encoded)} bytes")
    OUT.mkdir(parents=True, exist_ok=True)
    for number, data in pending.items():
        (OUT / f"bodyadvice_{number:02d}.webp").write_bytes(data)
    print("Four CC0 WebP files saved; no upscaling applied.")

if __name__ == "__main__":
    main()
