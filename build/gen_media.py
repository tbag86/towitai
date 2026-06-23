#!/usr/bin/env python3
"""
gen_media.py — Generate stills (Nano Banana Pro / Imagen 4) and video (Veo 3.1)
via the Google Generative Language API.

API key resolution order:
  1. env var GEMINI_API_KEY (or GOOGLE_API_KEY)
  2. a local `.env` next to this script, containing:  GEMINI_API_KEY=...

Usage:
  gen_media.py image  assets/gen/foo.png  "prompt"  [--model nbpro|imagen]  [--ar 16:9]
  gen_media.py veo    assets/video/foo.mp4 "prompt"  [--ar 16:9] [--fast]
  gen_media.py batch  image_batch.json                # [{type,out,prompt,ar,model}, ...]

Designed to be run in the background; prints progress lines.
Save stills as the filenames deck.html references in assets/gen, then run
build_inline.py to fold them into the single-file presentation/index.html.
"""
import sys, os, json, base64, time, urllib.request, urllib.error

# ---- API key ----
HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, ".env")
def load_key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if k: return k
    if os.path.exists(ENV):
        for line in open(ENV):
            line = line.strip()
            if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("No GEMINI_API_KEY found (set the env var or create build/.env)")
KEY = load_key()
BASE = "https://generativelanguage.googleapis.com/v1beta"

IMAGE_MODEL = "gemini-3-pro-image"          # Nano Banana Pro
IMAGEN_MODEL = "imagen-4.0-ultra-generate-001"
VEO_MODEL = "veo-3.1-generate-preview"
VEO_FAST = "veo-3.1-fast-generate-preview"

def post(url, payload, timeout=300):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def get(url, timeout=120):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

# ---------- IMAGES ----------
def gen_image_nbpro(out, prompt, ar="16:9"):
    url = f"{BASE}/models/{IMAGE_MODEL}:generateContent?key={KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": ar}},
    }
    res = post(url, payload)
    for part in res["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            open(out, "wb").write(base64.b64decode(part["inlineData"]["data"]))
            return out
    raise RuntimeError("no image in response: " + json.dumps(res)[:300])

def gen_image_imagen(out, prompt, ar="16:9"):
    url = f"{BASE}/models/{IMAGEN_MODEL}:predict?key={KEY}"
    payload = {"instances": [{"prompt": prompt}],
               "parameters": {"sampleCount": 1, "aspectRatio": ar}}
    res = post(url, payload)
    b64 = res["predictions"][0]["bytesBase64Encoded"]
    open(out, "wb").write(base64.b64decode(b64))
    return out

def gen_image(out, prompt, model="nbpro", ar="16:9"):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fn = gen_image_imagen if model == "imagen" else gen_image_nbpro
    try:
        fn(out, prompt, ar)
    except Exception as e:
        alt = "nbpro" if model == "imagen" else "imagen"
        print(f"  [{os.path.basename(out)}] {model} failed ({str(e)[:80]}); trying {alt}")
        (gen_image_nbpro if alt == "nbpro" else gen_image_imagen)(out, prompt, ar)
    kb = os.path.getsize(out) // 1024
    print(f"  IMAGE ok: {out} ({kb} KB)")
    return out

# ---------- VIDEO (Veo) ----------
def gen_veo(out, prompt, ar="16:9", fast=False, image=None):
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    model = VEO_FAST if fast else VEO_MODEL
    url = f"{BASE}/models/{model}:predictLongRunning?key={KEY}"
    instance = {"prompt": prompt}
    if image:  # image-to-video: animate a real photo as the first frame (keeps the actual subject)
        img_bytes = open(image, "rb").read()
        mt = "image/png" if image.lower().endswith(".png") else "image/jpeg"
        instance["image"] = {"bytesBase64Encoded": base64.b64encode(img_bytes).decode(), "mimeType": mt}
        print(f"  VEO using first-frame image: {os.path.basename(image)}")
    payload = {"instances": [instance],
               "parameters": {"aspectRatio": ar}}
    op = post(url, payload)
    name = op["name"]
    print(f"  VEO started: {os.path.basename(out)} op={name.split('/')[-1]}")
    poll_url = f"{BASE}/{name}?key={KEY}"
    for i in range(60):  # up to ~10 min
        time.sleep(10)
        st = json.loads(get(poll_url))
        if st.get("done"):
            if "error" in st:
                raise RuntimeError(f"Veo error: {st['error']}")
            resp = st["response"]
            samples = (resp.get("generateVideoResponse", {}).get("generatedSamples")
                       or resp.get("generatedSamples")
                       or resp.get("videos") or [])
            if not samples:
                raise RuntimeError("no samples: " + json.dumps(resp)[:300])
            v = samples[0].get("video", samples[0])
            if "uri" in v:
                uri = v["uri"]
                sep = '&' if '?' in uri else '?'
                data = get(f"{uri}{sep}key={KEY}", timeout=300)
                open(out, "wb").write(data)
            elif "bytesBase64Encoded" in v:
                open(out, "wb").write(base64.b64decode(v["bytesBase64Encoded"]))
            else:
                raise RuntimeError("no video data: " + json.dumps(v)[:200])
            mb = os.path.getsize(out) / 1e6
            print(f"  VEO ok: {out} ({mb:.1f} MB)")
            return out
        print(f"  VEO polling {os.path.basename(out)} … {(i+1)*10}s")
    raise RuntimeError("Veo timed out")

# ---------- CLI ----------
def main():
    a = sys.argv
    if len(a) < 2:
        print(__doc__); return
    cmd = a[1]
    def opt(name, default=None):
        return a[a.index(name)+1] if name in a else default
    if cmd == "image":
        gen_image(a[2], a[3], model=opt("--model", "nbpro"), ar=opt("--ar", "16:9"))
    elif cmd == "veo":
        gen_veo(a[2], a[3], ar=opt("--ar", "16:9"), fast=("--fast" in a), image=opt("--image"))
    elif cmd == "batch":
        spec = json.load(open(a[2]))
        ok, fail = 0, 0
        for item in spec:
            try:
                if item["type"] == "image":
                    gen_image(item["out"], item["prompt"], item.get("model", "nbpro"), item.get("ar", "16:9"))
                elif item["type"] == "veo":
                    gen_veo(item["out"], item["prompt"], item.get("ar", "16:9"), item.get("fast", False), item.get("image"))
                ok += 1
            except Exception as e:
                fail += 1
                print(f"  FAIL {item.get('out')}: {str(e)[:160]}")
        print(f"\nBatch done: {ok} ok, {fail} failed")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
