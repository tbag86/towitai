#!/usr/bin/env python3
"""new_client.py <slug> ["Display Name"]  —  scaffold a new dealership.

Creates build/clients/<slug>.json (from _template.json) and build/assets/clients/<slug>/.
Then: set the logo_url (or drop a logo file), tweak the showroom prompt, and run
  python3 build/build_client.py <slug> --gen
"""
import sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))

def main(slug, name=None):
    name = name or slug.replace("-", " ").title()
    cfg_path = os.path.join(HERE, "clients", f"{slug}.json")
    if os.path.exists(cfg_path):
        raise SystemExit(f"clients/{slug}.json already exists")
    tpl = json.load(open(os.path.join(HERE, "clients", "_template.json")))
    cfg = {
        "slug": slug,
        "name": name,
        "date": tpl["date"],
        "logo": f"assets/clients/{slug}/logo.svg",
        "logo_url": "",
        "logo_chip": "",
        "showroom_image": f"assets/clients/{slug}/showroom.png",
        "showroom_video": f"assets/clients/{slug}/showroom.mp4",
        "showroom_prompt": tpl["showroom_prompt"],
        "showroom_motion_prompt": tpl["showroom_motion_prompt"],
    }
    os.makedirs(os.path.join(HERE, "assets", "clients", slug), exist_ok=True)
    open(cfg_path, "w").write(json.dumps(cfg, indent=2) + "\n")
    print(f"Created build/clients/{slug}.json and build/assets/clients/{slug}/")
    print("Next:")
    print(f"  1. Set \"logo_url\" in clients/{slug}.json (or drop the logo at {cfg['logo']});")
    print(f"     if the logo is white/light, set \"logo_chip\":\"ink\".")
    print(f"  2. Tweak \"showroom_prompt\" for the brand.")
    print(f"  3. python3 build/build_client.py {slug} --gen")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: new_client.py <slug> [\"Display Name\"]")
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
