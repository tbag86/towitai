#!/usr/bin/env python3
"""build_client.py — build a dealership pitch from clients/<slug>.json and wire its URL.

  python3 build/build_client.py williams           # render + inline → site/williams/index.html
  python3 build/build_client.py williams --gen      # also (re)generate the dealer's showroom img+video
  python3 build/build_client.py --all               # rebuild every client
  python3 build/build_client.py --routes            # just regenerate the Vercel routes

Each client is served at /<slug>; the 'home' client in clients/_config.json is also served at /.
Run a build, then commit & push — Vercel redeploys automatically."""
import sys, os, json, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SITE = os.path.join(ROOT, "site")
import render

def all_slugs():
    return sorted(os.path.splitext(os.path.basename(p))[0]
                  for p in glob.glob(os.path.join(HERE, "clients", "*.json"))
                  if not os.path.basename(p).startswith("_"))

def built_slugs():
    return sorted(d for d in os.listdir(SITE)
                  if os.path.exists(os.path.join(SITE, d, "index.html"))) if os.path.isdir(SITE) else []

def write_routes():
    home = "williams"
    cfgp = os.path.join(HERE, "clients", "_config.json")
    if os.path.exists(cfgp):
        home = json.load(open(cfgp)).get("home", home)
    slugs = built_slugs()
    rewrites = []
    if home in slugs:
        rewrites.append({"source": "/", "destination": f"/site/{home}/index.html"})
    for s in slugs:
        rewrites.append({"source": f"/{s}", "destination": f"/site/{s}/index.html"})
        rewrites.append({"source": f"/{s}/", "destination": f"/site/{s}/index.html"})
    open(os.path.join(ROOT, "vercel.json"), "w").write(json.dumps({"rewrites": rewrites}, indent=2) + "\n")
    print(f"  routes: / → {home}   |   " + "  ".join(f"/{s}" for s in slugs))

def build(slug, gen=False):
    if gen:
        print(f"[{slug}] generating dealer media …")
        subprocess.run([sys.executable, os.path.join(HERE, "gen_client_media.py"), slug], check=True, cwd=HERE)
    print(f"[{slug}] render + inline …")
    deck = render.render(slug)
    out = os.path.join(SITE, slug, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, "build_inline.py"), deck, out], check=True)
    print(f"[{slug}] → {os.path.relpath(out, ROOT)}")

def main(argv):
    gen = "--gen" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--routes" in argv and not args:
        write_routes(); return
    if "--all" in argv:
        targets = all_slugs()
    elif args:
        targets = args
    else:
        raise SystemExit(__doc__)
    for slug in targets:
        build(slug, gen=gen)
    write_routes()
    print("\nDone. Commit & push to deploy:  git add -A && git commit -m \"deck: " + ",".join(targets) + "\" && git push")

if __name__ == "__main__":
    main(sys.argv[1:])
