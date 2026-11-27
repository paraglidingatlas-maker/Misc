"""Import the KK7 skyways / thermals once, so the pages never ask KK7 at runtime.

Source: KK7 Thermal & Skyways (thermal.kk7.ch, CC BY-NC-SA 4.0, built from public tracklogs). TMS, 256 px tiles.
KK7 rules: send ?src=<our hostname> with a matching Referer (else 403), stay under 10 requests a second.

Recolouring is the same as the old in-browser code:
  skyways  - faint blue lines lifted to a light sky blue, faint alpha firmed up;
  thermals - strength read from KK7's blue->red hue, redrawn pale amber -> orange -> red.

Outputs (WebP with alpha):
  events/img/sky/tapalpa-<layer>.webp      Tapalpa Task 3 area at z12, resampled to a plain lat/lon grid
                                           (the live tracker's map frame is equirectangular, so one <image> fits);
  events/img/sky/<slug>-<layer>.webp       each event venue at z11, a 1536 x 640 px Web Mercator crop centred
                                           on the venue (the Flying site map draws it at the venue's world pixel).
  events/img/sky/sky.json                  bounds of every image.

Run from airtribune-redesign/:  python3 -I src/build/bake_kk7.py <tile-cache-dir>
"""
import io, json, math, os, sys, time, urllib.request
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "events", "img", "sky")
cache = sys.argv[1]; os.makedirs(cache, exist_ok=True); os.makedirs(OUT, exist_ok=True)
SRC = "paraglidingatlas-maker.github.io"
LAYERS = ("skyways", "thermals")

# Tapalpa task area (lat/lon box) and venues (lat, lon); venue slugs = Airtribune slugs used by the page builders
TAPALPA = dict(s=19.50, n=20.40, w=-103.90, e=-103.05, z=12)
VENUES = {"srs-2027-1": [45.95, 13.73], "srs-2027-2": [44.40, 6.33], "srs-2027-wsf": [46.28, 13.14],
          "srs-2027-3": [41.37, 21.25], "srs-2027-4": [43.97, 6.51], "bwo2027": [17.92, 73.82]}
VZ, VW, VH = 11, 1536, 640

_sent = []
def tile(layer, z, x, y):
    """XYZ tile (y from the top) as an RGBA array; None-safe (transparent) for 404/empty."""
    fn = os.path.join(cache, f"{layer}_{z}_{x}_{y}.png")
    if not os.path.exists(fn):
        now = time.time()
        while len(_sent) >= 8 and now - _sent[-8] < 1.0:
            time.sleep(.05); now = time.time()
        _sent.append(now)
        url = f"https://thermal.kk7.ch/tiles/{layer}_all_all/{z}/{x}/{2**z - 1 - y}.png?src={SRC}"
        req = urllib.request.Request(url, headers={"Referer": f"https://{SRC}/", "User-Agent": "airtribune-redesign-bake/1.0"})
        try:
            data = urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 404: raise
            data = b""
        open(fn, "wb").write(data)
    data = open(fn, "rb").read()
    if len(data) < 80:
        return np.zeros((256, 256, 4), np.uint8)
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"))

def mosaic(layer, z, tx0, tx1, ty0, ty1):
    m = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 4), np.uint8)
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            m[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = tile(layer, z, tx, ty)
    return m

def lift(a):          # skyways
    a = a.astype(np.float32); r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    t = np.clip(b - np.maximum(r, g), 0, None) / 255
    out = np.stack([r + 120 * t, g + 170 * t, b, al * 1.5], -1)
    out[al == 0] = 0
    return np.clip(out, 0, 255).astype(np.uint8)

def heat(a):          # thermals
    f = a.astype(np.float32) / 255; r, g, b, al = f[..., 0], f[..., 1], f[..., 2], a[..., 3].astype(np.float32)
    mx, mn = f[..., :3].max(-1), f[..., :3].min(-1); c = mx - mn; cs = np.where(c > 0, c, 1)
    h = np.where(mx == r, 60 * (((g - b) / cs + 6) % 6), np.where(mx == g, 60 * ((b - r) / cs + 2), 60 * ((r - g) / cs + 4)))
    h = np.where(c > .04, h, 240.0); h = np.where(h > 300, 0, h)
    v = np.clip((240 - h) / 240, 0, 1); lo = v < .5; k = np.where(lo, v * 2, (v - .5) * 2)[..., None]
    A = np.where(lo[..., None], [255, 205, 130], [255, 125, 35]); B = np.where(lo[..., None], [255, 125, 35], [215, 25, 25])
    rgb = A + (B - A) * k
    out = np.concatenate([rgb, np.minimum(255, al * (1.2 + .6 * v))[..., None]], -1)
    out[a[..., 3] == 0] = 0
    return np.clip(out, 0, 255).astype(np.uint8)

wx = lambda lon, n: (lon + 180) / 360 * n * 256
wy = lambda lat, n: (1 - np.arcsinh(np.tan(np.radians(lat))) / math.pi) / 2 * n * 256

def save(arr, name):
    fn = os.path.join(OUT, name)
    Image.fromarray(arr, "RGBA").save(fn, "WEBP", quality=60, method=6, alpha_quality=50)
    print(f"  {name}: {arr.shape[1]}x{arr.shape[0]}, {os.path.getsize(fn) // 1024} KB")

meta = {"credit": "Skyways & thermals: thermal.kk7.ch, CC BY-NC-SA 4.0", "baked": time.strftime("%Y-%m-%d")}

# --- Tapalpa: Mercator mosaic resampled onto a linear lat/lon grid (bilinear) ---
T = TAPALPA; n = 2 ** T["z"]
px0, px1, py0, py1 = wx(T["w"], n), wx(T["e"], n), wy(T["n"], n), wy(T["s"], n)
tx0, tx1, ty0, ty1 = int(px0 // 256), int(px1 // 256), int(py0 // 256), int(py1 // 256)
W, H = int(round(px1 - px0)), int(round(py1 - py0))
lon = T["w"] + (np.arange(W) + .5) / W * (T["e"] - T["w"])
lat = T["n"] - (np.arange(H) + .5) / H * (T["n"] - T["s"])
fx = wx(lon, n) - tx0 * 256 - .5; fy = wy(lat, n) - ty0 * 256 - .5
print(f"Tapalpa z{T['z']}: tiles {tx1 - tx0 + 1}x{ty1 - ty0 + 1}, image {W}x{H}")
for layer in LAYERS:
    m = (lift if layer == "skyways" else heat)(mosaic(layer, T["z"], tx0, tx1, ty0, ty1)).astype(np.float32)
    ix = np.clip(fx.astype(int), 0, m.shape[1] - 2); iy = np.clip(fy.astype(int), 0, m.shape[0] - 2)
    ux = np.clip(fx - ix, 0, 1)[None, :, None]; uy = np.clip(fy - iy, 0, 1)[:, None, None]
    I, J = np.meshgrid(ix, iy)
    p = m[J, I] * (1 - ux) * (1 - uy) + m[J, I + 1] * ux * (1 - uy) + m[J + 1, I] * (1 - ux) * uy + m[J + 1, I + 1] * ux * uy
    save(np.clip(p, 0, 255).astype(np.uint8), f"tapalpa-{layer}.webp")
meta["tapalpa"] = {k: T[k] for k in ("s", "n", "w", "e", "z")}

# --- venues: Web Mercator crops centred on the venue ---
n = 2 ** VZ; meta["venues"] = {}
for slug, (la, lo) in VENUES.items():
    cx, cy = round(float(wx(lo, n))), round(float(wy(la, n)))
    x0, y0 = cx - VW // 2, cy - VH // 2
    tx0, tx1, ty0, ty1 = x0 // 256, (x0 + VW - 1) // 256, y0 // 256, (y0 + VH - 1) // 256
    print(f"{slug} z{VZ}: tiles {tx1 - tx0 + 1}x{ty1 - ty0 + 1}")
    for layer in LAYERS:
        m = mosaic(layer, VZ, tx0, tx1, ty0, ty1)
        crop = m[y0 - ty0 * 256: y0 - ty0 * 256 + VH, x0 - tx0 * 256: x0 - tx0 * 256 + VW]
        save((lift if layer == "skyways" else heat)(crop), f"{slug}-{layer}.webp")
    meta["venues"][slug] = {"ll": [la, lo], "z": VZ, "x0": x0, "y0": y0, "w": VW, "h": VH}
json.dump(meta, open(os.path.join(OUT, "sky.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, "sky.json"))
