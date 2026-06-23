#!/usr/bin/env python3
"""render.py <slug>  —  fill template.deck.html with clients/<slug>.json → clients/<slug>/deck.html

Placeholders in the template: {{NAME}} {{DATE}} {{LOGO}} {{LOGO_CHIP}}
{{SHOWROOM_IMG}} {{SHOWROOM_VIDEO}}.  Everything else (towit fleet photos/video,
towit logo, service copy) is baked into the template and stays stable for every client."""
import sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.deck.html")

def load_client(slug):
    p = os.path.join(HERE, "clients", f"{slug}.json")
    if not os.path.exists(p):
        raise SystemExit(f"No config: build/clients/{slug}.json (copy clients/_template.json)")
    return json.load(open(p))

def render(slug):
    c = load_client(slug)
    html = open(TEMPLATE, encoding="utf-8").read()
    mapping = {
        "{{NAME}}":            c["name"],
        "{{DATE}}":            c.get("date", ""),
        "{{LOGO}}":            c["logo"],
        "{{LOGO_CHIP}}":       c.get("logo_chip", ""),
        "{{SHOWROOM_IMG}}":    c["showroom_image"],
        "{{SHOWROOM_VIDEO}}":  c["showroom_video"],
    }
    for k, v in mapping.items():
        html = html.replace(k, v)
    leftover = [k for k in mapping if k in html]  # none expected
    out_dir = os.path.join(HERE, "clients", slug)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "deck.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"  rendered {os.path.relpath(out, HERE)}  ({c['name']})")
    return out

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: render.py <slug>")
    render(sys.argv[1])
