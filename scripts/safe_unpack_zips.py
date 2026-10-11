#!/usr/bin/env python3
"""Safely unpack ZIPs uploaded to incoming-zips/ into imported-zips/<archive-name>/."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile
import os, re, stat, sys

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "incoming-zips"
OUT = ROOT / "imported-zips"
MAX_ARCHIVE = 50 * 1024 * 1024
MAX_UNPACKED = 150 * 1024 * 1024
MAX_FILES = 500
MAX_FILE = 30 * 1024 * 1024

def main():
    archives = sorted(INBOX.glob("*.zip")) if INBOX.exists() else []
    if not archives:
        print("No ZIPs to unpack.")
        return
    for archive in archives:
        if archive.stat().st_size > MAX_ARCHIVE:
            raise ValueError(f"ZIP too large: {archive.name}")
        dest = OUT / archive.stem
        if dest.exists():
            raise ValueError(f"Destination already exists: {dest}; refusing overwrite")
        with ZipFile(archive) as z:
            members = [m for m in z.infolist() if not m.is_dir()]
            if not members or len(members) > MAX_FILES:
                raise ValueError("Archive empty or contains too many files")
            if sum(m.file_size for m in members) > MAX_UNPACKED:
                raise ValueError("Archive exceeds expanded size limit")
            paths = []
            for m in members:
                name = m.filename.replace("\\", "/")
                p = PurePosixPath(name)
                mode = m.external_attr >> 16
                if (p.is_absolute() or ".." in p.parts or "\x00" in name
                    or ":" in name or not p.parts or name.startswith(".")
                    or any(part.startswith(".") for part in p.parts)
                    or (mode and stat.S_ISLNK(mode))
                    or m.file_size > MAX_FILE):
                    raise ValueError(f"Unsafe ZIP entry: {name!r}")
                paths.append((m, p))
            if len({str(p).casefold() for _, p in paths}) != len(paths):
                raise ValueError("Duplicate file paths in archive")
            for m, p in paths:
                target = dest.joinpath(*p.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(m) as src, target.open("xb") as dst:
                    while chunk := src.read(1024 * 1024):
                        dst.write(chunk)
        archive.unlink()
        print(f"Unpacked {len(paths)} files from {archive.name} into {dest.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
