# towit.ai — Presentation (Vercel)

Static, single-file deck for deployment. `index.html` is the built self-contained presentation
(copied from `../presentation/index.html`).

## Run locally
```bash
npx serve .
```
Navigate with **← / →** (or scroll / swipe). Press **F** for full-screen.

## Deploy on Vercel
Plain static site, no build step.
1. `git init` here (or at the repo root) and push to your own GitHub repo.
2. vercel.com → **Add New → Project → Import** → Framework preset **Other** → **Deploy**.
3. Vercel gives you a shareable `*.vercel.app` URL; pushes to the default branch auto-deploy.

`vercel.json` sets long-lived cache headers on `/assets/*` and the correct mp4 content-type.

## Update
After editing the deck and rebuilding:
```bash
cp ../presentation/index.html index.html
git add index.html && git commit -m "Update deck" && git push
```
