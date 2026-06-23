#!/usr/bin/env python3
"""Inline every asset (image/logo/video) into deck.html as base64 data URIs,
producing a single self-contained presentation/index.html that works anywhere
— no external files, immune to iCloud sync/eviction and the .png-that-is-jpeg bug."""
import os, re, base64, sys

BUILD = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BUILD, "deck.html")
OUT = os.path.abspath(os.path.join(BUILD, "..", "presentation", "index.html"))

def mime(path, data):
    if data[:4] == b"\x89PNG": return "image/png"
    if data[:3] == b"\xff\xd8\xff": return "image/jpeg"
    if path.endswith(".svg"): return "image/svg+xml"
    if path.endswith(".mp4") or data[4:8] == b"ftyp": return "video/mp4"
    if path.endswith((".jpg", ".jpeg")): return "image/jpeg"
    return "application/octet-stream"

html = open(SRC, encoding="utf-8").read()
cache = {}
def datauri(rel):
    if rel in cache: return cache[rel]
    p = os.path.join(BUILD, rel)
    if not os.path.exists(p):
        print(f"  ! missing {rel}"); return rel
    data = open(p, "rb").read()
    uri = f"data:{mime(p, data)};base64,{base64.b64encode(data).decode()}"
    cache[rel] = uri
    print(f"  inlined {rel}  ({len(data)//1024} KB -> {len(uri)//1024} KB b64)")
    return uri

# replace src="assets/..." , poster="assets/..." , and <source src="assets/...">
def repl(m):
    attr, q, path = m.group(1), m.group(2), m.group(3)
    return f'{attr}={q}{datauri(path)}{q}'
pattern = re.compile(r'(src|poster|data-fallback)=(["\'])(assets/[^"\']+)\2')
html2 = pattern.sub(repl, html)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html2)
mb = os.path.getsize(OUT)/1e6
print(f"\nWrote {OUT}  ({mb:.1f} MB self-contained)")
print(f"assets inlined: {len(cache)}")
