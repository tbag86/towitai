#!/usr/bin/env python3
"""gen_client_media.py <slug>  —  generate the per-dealer assets for one client:

  1. logo   — downloaded from config "logo_url" if the file is missing (skip if no url)
  2. showroom image  — Nano Banana Pro, from "showroom_prompt"
  3. showroom video  — Veo image-to-video, animating that real image (keeps it accurate)

Needs GEMINI_API_KEY (env or build/.env). The towit fleet photos/video are shared and
are NOT regenerated here — only the dealership-specific imagery is."""
import sys, os, json, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

def ap(rel):  # config paths are relative to build/
    return rel if os.path.isabs(rel) else os.path.join(HERE, rel)

def main(slug):
    cfg = json.load(open(os.path.join(HERE, "clients", f"{slug}.json")))
    # 1) logo
    logo = ap(cfg["logo"])
    if not os.path.exists(logo) and cfg.get("logo_url", "").startswith("http"):
        os.makedirs(os.path.dirname(logo), exist_ok=True)
        print(f"  downloading logo → {os.path.relpath(logo, HERE)}")
        urllib.request.urlretrieve(cfg["logo_url"], logo)
    elif not os.path.exists(logo):
        print(f"  ! logo missing and no logo_url — drop a file at {cfg['logo']}")

    import gen_media as gm  # imported here so render-only flows don't need the API key
    # 2) showroom still
    img = ap(cfg["showroom_image"])
    print(f"  generating showroom image → {os.path.relpath(img, HERE)}")
    gm.gen_image(img, cfg["showroom_prompt"], ar="16:9")
    # 3) showroom video (image-to-video from the still we just made)
    vid = ap(cfg["showroom_video"])
    motion = cfg.get("showroom_motion_prompt", "Continue this exact scene in motion; very slow cinematic push-in, keep everything identical. NO TEXT, NO LOGOS.")
    print(f"  generating showroom video → {os.path.relpath(vid, HERE)}")
    gm.gen_veo(vid, motion, ar="16:9", image=img)
    print(f"  client media ready for {slug}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: gen_client_media.py <slug>")
    main(sys.argv[1])
