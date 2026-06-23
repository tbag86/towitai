# Dealership decks — how to make a new one

Each dealership gets its own pitch at its own URL (e.g. `towitai.vercel.app/williams`,
`/mercedes`). The **towit.ai content stays identical** for every dealer — the blue Ford Ranger
MS-RT, the Brian James Race Transporter 7 / T Transporter photos + cover video, the towit logo,
and all the service copy. Only the **dealership-specific bits** change: name, logo, and the
showroom image + video.

## The one prompt
Just ask Claude:

> **"Create a version for Mercedes"**

…and it will scaffold the config, fetch/generate the dealer logo + showroom imagery, build, and
wire up the `/mercedes` URL. The rest of this file is what that automation does, so a human can do
it too.

## Do it by hand (3 steps)

```bash
# 1. Scaffold a new dealer (creates clients/mercedes.json + assets/clients/mercedes/)
python3 build/new_client.py mercedes "Mercedes-Benz of Manchester"

# 2. Edit build/clients/mercedes.json:
#    - "logo_url": a direct link to their logo (svg/png)  — OR drop a file at assets/clients/mercedes/logo.svg
#    - "logo_chip": "" for a dark logo (cream chip), "ink" for a white/light logo (dark chip)
#    - "showroom_prompt": tweak for the brand (keep "NO LOGOS, NO BADGES")

# 3. Build it (generates the showroom image + video, inlines, wires the URL)
python3 build/build_client.py mercedes --gen
```

Then preview and ship:

```bash
node build/shoot.js ../site/mercedes/index.html      # QA screenshots → build/assets/shots/
git add -A && git commit -m "deck: mercedes" && git push   # Vercel auto-deploys → /mercedes
```

## What lives where

| Path | What |
|---|---|
| `build/template.deck.html` | The shared 4-slide layout. Edit this to change **every** deck. towit assets are baked in. |
| `build/clients/<slug>.json` | One dealership's data (name, logo, showroom prompts). |
| `build/assets/clients/<slug>/` | That dealer's `logo`, `showroom.png`, `showroom.mp4`. |
| `build/assets/gen/ph_*.jpg`, `build/assets/video/veo_cover.mp4` | **Shared towit fleet** — Ranger MS-RT + Brian James trailers. Don't make these per-client. |
| `build/assets/logos/logo_towit.png` | The towit logo (shared). |
| `site/<slug>/index.html` | The built, self-contained deck that gets deployed. |
| `vercel.json` | Auto-generated routes (`/` → home client, `/<slug>` per dealer). Don't hand-edit. |

## Scripts

| Command | Does |
|---|---|
| `new_client.py <slug> ["Name"]` | Scaffold a new dealer config + asset folder. |
| `gen_client_media.py <slug>` | Download the logo (if `logo_url` set) + generate the showroom image & video. Needs `GEMINI_API_KEY` in `build/.env`. |
| `build_client.py <slug> [--gen]` | Render + inline → `site/<slug>/index.html` and rewrite the routes. `--gen` also runs media generation. |
| `build_client.py --all` | Rebuild every dealer (e.g. after editing the template). |
| `build_client.py --routes` | Just regenerate `vercel.json`. |

The site root (`/`) serves the `home` client set in `build/clients/_config.json`.

## Accuracy rule
The towit kit (Ranger MS-RT + Brian James trailers) is always **real fleet photography** — never
AI-generated, so the vehicle and trailers are exactly right. AI is only used for the dealer's
showroom scene, which is captioned "indicative visualisation". If a dealer gives you a real photo
of their showroom, drop it in as `assets/clients/<slug>/showroom.png` and re-run with `--gen` to
animate it (or skip `--gen` to use a still).
