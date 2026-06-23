# towit.ai — Presentation

A cinematic, editorial, **single-file** pitch-deck system. Clone of a deck design that worked very
well, reset to a neutral starting point for towit.ai.

- **Present:** open `presentation/index.html` (one self-contained file). ← / → to navigate, **F** for full-screen.
- **Edit:** change `build/deck.html`, then run `python3 build/build_inline.py` to rebuild the single file.
- **Deploy:** push `site/` to Vercel (static, no build step).

👉 **`CLAUDE.md` is the full guide** — design tokens, component library, the media pipeline, and the
quality bar. Start a new deck by filling in **`NARRATIVE.md`** first.

```bash
python3 build/build_inline.py            # build → presentation/index.html
cp presentation/index.html site/index.html
node build/shoot.js                      # optional QA screenshots
```

The shipped `deck.html` contains 17 placeholder slides — one per layout pattern — as a reference
library. Imagery is lightweight SVG placeholders; generate real stills/video with `build/gen_media.py`.
