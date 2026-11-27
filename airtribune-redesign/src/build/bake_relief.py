"""Bake a dark shaded-relief map of the Task 3 area for the voice-over studio (docs/task3-voiceover/).

Terrain: AWS Terrain Tiles (terrarium PNG, open data; attribution "Terrain: Mapzen / AWS Terrain Tiles, SRTM").
Output pixels are in the task's local km frame (x east, y north, origin = take-off), so the page can draw tracks
straight on top. Run from airtribune-redesign/:  python3 -I src/build/bake_relief.py <tile-cache-dir>
"""
import io, math, os, sys, urllib.request
import numpy as np
from PIL import Image

TO_LAT, TO_LON = 19.9423, -103.65415
X0, X1, Y0, Y1 = -9.0, 27.0, -13.0, 21.0      # km, local frame
RES_M = 14.0                                  # output metres per pixel
Z = 14
cache = sys.argv[1]; os.makedirs(cache, exist_ok=True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "task3-voiceover", "relief.jpg")

W, H = int((X1 - X0) * 1000 / RES_M), int((Y1 - Y0) * 1000 / RES_M)
xs = X0 + (np.arange(W) + .5) * RES_M / 1000
ys = Y1 - (np.arange(H) + .5) * RES_M / 1000
XX, YY = np.meshgrid(xs, ys)
lat = TO_LAT + YY / 110.574
lon = TO_LON + XX / (111.32 * math.cos(math.radians(TO_LAT)))
n = 2 ** Z
px = (lon + 180) / 360 * n * 256
py = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n * 256
tx0, tx1 = int(px.min() // 256), int(px.max() // 256)
ty0, ty1 = int(py.min() // 256), int(py.max() // 256)
mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        fn = os.path.join(cache, f"{Z}_{tx}_{ty}.png")
        if not os.path.exists(fn):
            url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{tx}/{ty}.png"
            open(fn, "wb").write(urllib.request.urlopen(url, timeout=30).read())
        a = np.asarray(Image.open(fn).convert("RGB"), np.float32)
        mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
# bilinear sample
fx, fy = px - tx0 * 256 - .5, py - ty0 * 256 - .5
ix, iy = np.clip(fx.astype(int), 0, mos.shape[1] - 2), np.clip(fy.astype(int), 0, mos.shape[0] - 2)
ax, ay = fx - ix, fy - iy
E = (mos[iy, ix] * (1 - ax) * (1 - ay) + mos[iy, ix + 1] * ax * (1 - ay) + mos[iy + 1, ix] * (1 - ax) * ay + mos[iy + 1, ix + 1] * ax * ay)
E = np.clip(E, 900, 3500)
# hillshade (sun from NW, 40 deg), slight vertical exaggeration
gy, gx = np.gradient(E, RES_M)
slope = np.arctan(1.6 * np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
az, alt = math.radians(315), math.radians(40)
hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - asp)
hs = np.clip(hs, 0, 1)
# colours: site's dark teal, lifted on high ground, hillshade on top
lo, hi = np.array([92, 120, 118.]), np.array([168, 186, 176.])
t = (np.clip((E - 1300) / 1500, 0, 1) ** 0.8)[..., None]
base = lo * (1 - t) + hi * t
rgb = base * (0.62 + 0.55 * hs[..., None])
# faint 100 m contours, stronger every 500 m
for step, a_ in ((100, -8), (500, -18)):
    c = np.floor(E / step)
    edge = (np.abs(np.diff(c, axis=0, prepend=c[:1])) + np.abs(np.diff(c, axis=1, prepend=c[:, :1]))) > 0
    rgb[edge] += a_
Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT, quality=82, optimize=True, progressive=True)
print("wrote", OUT, W, H, "elev range", int(E.min()), int(E.max()))
