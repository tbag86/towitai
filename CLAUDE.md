# towit.ai — Presentation system

This repo builds **cinematic, editorial, single-file pitch decks** for towit.ai. It is a clone of a
deck that worked extremely well, stripped to a neutral starting point. This file tells you (the CLI)
exactly how the system is put together and the quality bar to hold. **Read it before editing.**

The goal every time: a deck that looks like it came from a top design studio — *confident, specific,
cinematic* — and the **opposite of a generic AI/Gamma/template deck**. Every slide is a *designed*
slide. There are no bare image dumps and no clip-art.

> **Multi-dealership system (read `CLIENTS.md`).** This repo is now templated: one shared layout
> (`build/template.deck.html`) + one JSON per dealership (`build/clients/<slug>.json`) → a deck per
> dealer at `/<slug>`. The towit kit (Ford Ranger MS-RT + Brian James trailers, towit logo, service
> copy) is baked into the template and stays stable; only the dealer name, logo and showroom
> image/video change. Make a new one with **"create a version for <dealer>"**, or
> `python3 build/new_client.py <slug>` → `python3 build/build_client.py <slug> --gen`. The
> single-file `build/deck.html` workflow below is superseded by this — the design-system notes still
> apply to `template.deck.html`.

---

## 1. How the system is structured

```
towit-ai/
├── build/
│   ├── deck.html            ← THE SOURCE you edit (external assets, easy to read)
│   ├── build_inline.py      ← base64-inlines every asset → ../presentation/index.html
│   ├── gen_media.py         ← generates stills (Nano Banana Pro) + video (Veo 3.1)
│   ├── image_batch.json     ← batch image prompts (the prompt RECIPE lives here)
│   ├── veo_batch.json       ← batch video prompts
│   ├── shoot.js             ← Playwright QA: screenshots every slide at 1920×1080
│   └── assets/
│       ├── gen/             ← generated stills + the SVG placeholders shipped here now
│       ├── logos/           ← brand + partner logos (SVG/PNG); placeholders shipped now
│       └── video/           ← Veo .mp4 clips (empty until you generate them)
├── presentation/
│   └── index.html           ← BUILT single-file deck (self-contained, ~tens of MB) — what you present
├── site/
│   ├── index.html           ← deploy copy (same file) for Vercel
│   ├── vercel.json          ← static-site config + asset cache headers
│   └── .gitignore
├── NARRATIVE.md             ← fill this in FIRST: brief, audience, figures, slide order
└── CLAUDE.md                ← this file
```

**The golden workflow:**
1. Edit content/layout in **`build/deck.html`** (references `assets/...`, fast to iterate).
2. (Optional) generate real imagery with **`gen_media.py`** into `build/assets/gen` & `build/assets/video`.
3. Run **`python3 build/build_inline.py`** → writes the self-contained **`presentation/index.html`**.
4. Copy that to the deploy folder: `cp presentation/index.html site/index.html`.
5. Deploy `site/` to Vercel (see §6).

> **Always edit `deck.html`, never the built `presentation/index.html` directly** — it's a generated
> artifact with megabytes of base64. Re-running `build_inline.py` overwrites it.

---

## 2. Why a single file? (don't break this)

`build_inline.py` turns every `src`/`poster`/`data-fallback="assets/..."` into a base64 data URI, so
the presentation is **one HTML file with zero external dependencies**. It always renders — emailed,
AirDropped, on a USB stick, or synced through iCloud — and is immune to the "images won't show"
class of bugs. The trade-off is file size (tens of MB once real photos/video are inlined); that opens
locally in a second or two. Keep this property.

---

## 3. The design system (the "presets")

It is **one `<style>` block** at the top of `deck.html`. Don't reach for a framework or new fonts.

### Brand tokens — `:root`
```
--ink:#15252B  --ink2:#0F1E23                      text / dark slide bg
--teal:#0C6E6C --teal-d:#0A4F4E --teal-l:#1A8C89   primary accent
--coral:#DC5538  --green:#2C8C5B  --gold:#C9933A    secondary accents
--paper:#F3EFE6  --paper2:#E9E3D5  --card:#FBF9F4    light backgrounds / cards
--muted:#5B6B70  --muted2:#8A979B                  secondary text
--hair:#CFC7B6   --hair-d:rgba(255,255,255,.16)    hairline borders (light / dark)
#6FD0CC = the light-teal used for accents ON dark/teal slides
```
To re-brand: change these tokens (and the `#6FD0CC` accents) — the whole deck reflows. The palette is
deliberately muted and editorial; keep that energy even if you change hues.

### Type — Lato only
Loaded from Google Fonts (300/400/700/900 + italic). The hierarchy *is* the design:
- `h1` 900, `clamp(38px,6vw,94px)`, line-height .98, tight negative tracking — hero only.
- `h2` 900, `clamp(28px,4vw,60px)` — slide titles.
- `h3` 900, `clamp(16px,1.4vw,21px)` — card/step headings.
- `.kick` 700, uppercase, `.26em` letter-spacing, teal, with a trailing rule — the section label above every title.
- `p.lead` 400, `clamp(14px,1.2vw,19px)`, `max-width:44ch` — intro paragraphs.
- Body text is light (400) and never full-width; **bold (700/900) carries emphasis**, not colour-spam.

### Motion
- Each slide's children with class `.r` fade/rise in; add `.d1 … .d6` for staggered delays.
- Photos get an 18–20s Ken Burns zoom (`@keyframes ken`).
- Stats animate by count-up — give the element `data-count="48"` and inner text `0`.
- Progress bar, dot-nav, and per-slide section number are wired in the `<script>` (don't touch unless needed).

### Texture
A faint SVG film **grain** (`--grain`) sits over photos and light slides, plus colour **grade**
gradients on imagery. This is what moves photos away from the raw-AI look — keep `.grade` + `.grain`
on every `.photo`/`.bg`.

---

## 4. Component vocabulary (copy these patterns)

All defined in the `<style>` block; here's when to use each. Slide variants: default = light paper;
add `dark` (ink) or `teal` (gradient) to `<section class="slide ...">` for rhythm.

| Pattern | Class | Use for |
|---|---|---|
| Section label | `.kick` | the small uppercase line above every title |
| Two-column | `.split` / `.split.img-r` | text + photo (the workhorse) |
| Grid | `.cols.c2 … .c5` | cards, stats, partners |
| Editorial card | `.card` (`.num` for 01/02…) | grouped points |
| Big number | `.stat` (`.coral`), `.statlbl`, `.statrule` | headline metrics (+ `data-count`) |
| Logo row | `.lockup` + `.chip` (`.chip.sm`) | partner / credibility logos |
| Table | `.tbl` (`.who` = bold first cell) | roles, alignment, sources |
| Process | `.steps` + `.step .n` | numbered left-to-right flow (5 wide) |
| Lists | `ul.tick` / `ul.tick.cross` | ticked benefits / crossed pain-points |
| Contrast | `.two` + `.box.no` / `.box.yes` | without-vs-with |
| Q&A grid | `.obj` + `.o .q .a` | objection handling |
| Call-to-action | `.asks` + `.ask .n` | the ask / next steps |
| Art-directed photo | `.photo` + `.grade` + `.grain` + `.cap` | inline imagery, always captioned |
| Full-bleed | `.bg` + `.scrim.l`/`.scrim.b` + `.fcap` | cinematic background slide |
| Misc | `.pill`, `.tag`, `small.note` | chips, kickers, footnotes |

`deck.html` currently ships **17 slides, one per pattern** — a working reference library. Build your
real deck by copying these blocks and deleting what you don't need.

---

## 5. Generating imagery & video (the look that sells it)

`gen_media.py` calls the Google Generative Language API:
- **Stills:** Nano Banana Pro (`gemini-3-pro-image`), falls back to Imagen 4.
- **Video:** Veo 3.1 (`veo-3.1-generate-preview`, or `--fast` for the cheaper preview).

**Key:** set `GEMINI_API_KEY` in your environment, or create `build/.env` with `GEMINI_API_KEY=...`.

```bash
# one image
python3 build/gen_media.py image assets/gen/ph_cover.png "…prompt…" --ar 16:9
# one video
python3 build/gen_media.py veo   assets/video/veo_cover.mp4 "…prompt…" --ar 16:9
# batch (edit the prompts first)
python3 build/gen_media.py batch build/image_batch.json
python3 build/gen_media.py batch build/veo_batch.json
```

### The prompt recipe (this is the secret)
Every prompt ends with the same DNA: **photoreal / cinematic, atmospheric, muted brand-aligned
palette, cinematic depth, NO TEXT, NO LOGOS, NO CAPTIONS.** Describe subject + setting + light
(blue-hour / golden-hour / soft overcast) + mood. For abstract/tech slides: "glowing teal and
warm-amber nodes, dark navy field, soft bokeh, elegant, minimal."

Then the deck does the rest: the `.grade` gradient tints each image to the palette, `.grain` adds
film grain, and **every image is captioned** (`.cap` / `.fcap` "indicative visualisation"). This
combination is what stops it reading as AI clip-art. **Never** drop an ungraded, uncaptioned raw
generation onto a slide.

### Using video on the cover
The cover currently uses a still (`.bg > img`). To use a Veo clip, swap the `<img>` for the video
markup — the JS already plays the active slide's video and falls back to the poster image on error:
```html
<div class="bg">
  <video autoplay muted loop playsinline preload="auto"
         poster="assets/gen/ph_cover.png" data-fallback="assets/gen/ph_cover.png">
    <source src="assets/video/veo_cover.mp4" type="video/mp4"></video>
  <div class="grade"></div><div class="grain"></div>
</div>
```
Keep a `poster` + `data-fallback` still so the slide always shows something. Compress clips before
inlining (a multi-MB mp4 becomes ~1.33× as base64).

---

## 6. Build, QA & deploy

```bash
# build the single file
python3 build/build_inline.py            # → presentation/index.html

# QA: screenshot every slide (needs Playwright/Chromium)
node build/shoot.js                      # → build/assets/shots/slide-XX.png

# stage for deploy
cp presentation/index.html site/index.html
```

**Vercel:** `site/` is a plain static site (no build step). `git init` in `site/` (or the repo root),
push to your own GitHub, then on vercel.com → Add New → Project → Import → Framework preset **Other**
→ Deploy. `vercel.json` already sets long cache headers on `/assets/*` and the mp4 content-type.
(There is intentionally **no** git history shipped here — connect your own repo.)

Present locally by opening `presentation/index.html`: **← / →**, ↑/↓, space, scroll or swipe to
navigate; click footer dots to jump; **F** for full-screen.

---

## 7. Quality bar — do / don't

**Do**
- Start from **`NARRATIVE.md`**: nail audience, goal, tone, the figures, and the slide order before designing.
- Open every section with a `.kick`, then a 900-weight `h2`.
- Be specific and quantified — real numbers in `.stat`s; back them on a final sources/assumptions slide.
- Vary slide backgrounds (paper / `dark` / `teal`) for rhythm; keep imagery graded + grained + captioned.
- Keep copy tight: leads ≤ ~44ch, card bodies one or two lines.

**Don't**
- Don't add new fonts, frameworks, or libraries — Lato + the existing `<style>` only.
- Don't edit `presentation/index.html` by hand — edit `deck.html` and rebuild.
- Don't use raw, uncaptioned AI imagery, stocky clip-art, drop shadows everywhere, or rainbow text.
- Don't claim figures you can't source. Caption visuals honestly as indicative.
- Don't reintroduce any third-party brand without their assets/permission — use placeholder chips until you have them.
