"""Shared bake steps for any task box: wind (Open-Meteo), KK7 skyways/thermals, shaded relief.

Same sources and recolouring as the one-off scripts in src/build/ (bake_wind.py, bake_kk7.py, bake_relief.py),
with the date, box, level and time zone as arguments.
"""
import io, json, math, os, time, urllib.error, urllib.request
import numpy as np
from PIL import Image

UA = "airtribune-redesign task pipeline"
KK7_SRC = "paraglidingatlas-maker.github.io"     # KK7 rule: ?src=<our hostname> + matching Referer, < 10 req/s


def _cache(cache, sub):
    d = os.path.join(cache or os.environ.get("TASK_CACHE", "/tmp/task-cache"), sub)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- wind
def fetch_wind(box, to, date, utc_offset_s, gate_s, log=print):
    """Hourly model wind at the racing level: a 5 x 5 grid on the model's own 0.25 deg points over the box
    (for the animation) plus the take-off point (for the caption). One Open-Meteo request."""
    level, lvl = ("600hPa", "4,200 m (600 hPa)") if (to.get("elev_m") or 0) > 2600 else ("700hPa", "3,200 m (700 hPa)")
    span = max(box["n"] - box["s"], (box["e"] - box["w"]) * math.cos(math.radians(to["lat"])))
    step = 0.25 * max(1, math.ceil(span / 4 / 0.25 - 0.15))
    clat = round((box["n"] + box["s"]) / 2 / 0.25) * 0.25
    clon = round((box["e"] + box["w"]) / 2 / 0.25) * 0.25
    lats = [round(clat + k * step, 2) for k in range(-2, 3)]
    lons = [round(clon + k * step, 2) for k in range(-2, 3)]
    pts = [(la, lo) for la in lats for lo in lons] + [(to["lat"], to["lon"])]
    gh = gate_s // 3600
    h0, h1 = gh - 2, gh + 5
    # ask in GMT for the local day +- 1 so any offset fits, then shift by the task's UTC offset
    import datetime as dt
    d = dt.date.fromisoformat(date)
    url = ("https://historical-forecast-api.open-meteo.com/v1/forecast?"
           f"latitude={','.join(str(p[0]) for p in pts)}&longitude={','.join(str(p[1]) for p in pts)}"
           f"&start_date={d - dt.timedelta(days=1)}&end_date={d + dt.timedelta(days=1)}"
           f"&hourly=wind_speed_{level},wind_direction_{level}&models=ecmwf_ifs025&timezone=GMT")
    res = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90))
    if isinstance(res, dict):
        res = [res]
    assert len(res) == len(pts), len(res)

    def uv(r, hr):
        utc = dt.datetime.combine(d, dt.time()) + dt.timedelta(hours=hr) - dt.timedelta(seconds=utc_offset_s)
        n = r["hourly"]["time"].index(utc.strftime("%Y-%m-%dT%H:00"))
        s, f = r["hourly"][f"wind_speed_{level}"][n], r["hourly"][f"wind_direction_{level}"][n]
        return s, f

    grid = []
    for hr in range(h0, h1 + 1):
        g = [[None] * 5 for _ in range(5)]
        for k in range(25):
            j, i = divmod(k, 5)
            s, f = uv(res[k], hr)
            a = math.radians(f)
            g[j][i] = [round(-s * math.sin(a), 1), round(-s * math.cos(a), 1)]
        grid.append(g)
    aloft = [[hr, round(uv(res[25], hr)[0], 1), round(uv(res[25], hr)[1])] for hr in range(gh - 1, gh + 4)]
    log(f"  wind: ECMWF IFS {level}, grid {lats[0]}..{lats[-1]} N x {lons[0]}..{lons[-1]} E, hours {h0}-{h1} local")
    return dict(aloft=dict(src="ECMWF IFS", lvl=lvl.split(" (")[0], h=aloft),
                grid=dict(src="ECMWF IFS 0.25°", lvl=lvl, lat=lats, lon=lons, h0=h0, h=grid),
                query=url, credit="Wind: Open-Meteo historical forecast API, ECMWF IFS 0.25°")


# ---------------------------------------------------------------- KK7
_sent = []


def _kk7_tile(cache, layer, z, x, y):
    fn = os.path.join(cache, f"{layer}_{z}_{x}_{y}.png")
    if not os.path.exists(fn):
        now = time.time()
        while len(_sent) >= 8 and now - _sent[-8] < 1.0:
            time.sleep(.05); now = time.time()
        _sent.append(now)
        url = f"https://thermal.kk7.ch/tiles/{layer}_all_all/{z}/{x}/{2**z - 1 - y}.png?src={KK7_SRC}"
        req = urllib.request.Request(url, headers={"Referer": f"https://{KK7_SRC}/", "User-Agent": UA})
        try:
            data = urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            data = b""
        open(fn, "wb").write(data)
    data = open(fn, "rb").read()
    if len(data) < 80:
        return np.zeros((256, 256, 4), np.uint8)
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"))


def _lift(a):          # skyways: faint blue lines lifted to a light sky blue
    a = a.astype(np.float32); r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    t = np.clip(b - np.maximum(r, g), 0, None) / 255
    out = np.stack([r + 120 * t, g + 170 * t, b, al * 1.5], -1)
    out[al == 0] = 0
    return np.clip(out, 0, 255).astype(np.uint8)


def _heat(a):          # thermals: KK7 blue->red hue redrawn pale amber -> orange -> red
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


_wx = lambda lon, n: (lon + 180) / 360 * n * 256
_wy = lambda lat, n: (1 - np.arcsinh(np.tan(np.radians(lat))) / math.pi) / 2 * n * 256


def bake_kk7(box, out_dir, cache=None, log=print, max_px=2800):
    """KK7 skyways + thermals over the box, resampled to a plain lat/lon grid (the live tracker's frame)."""
    cache = _cache(cache, "kk7")
    z = 12
    while z > 8 and _wx(box["e"], 2 ** z) - _wx(box["w"], 2 ** z) > max_px:
        z -= 1
    n = 2 ** z
    px0, px1, py0, py1 = _wx(box["w"], n), _wx(box["e"], n), _wy(box["n"], n), _wy(box["s"], n)
    tx0, tx1, ty0, ty1 = int(px0 // 256), int(px1 // 256), int(py0 // 256), int(py1 // 256)
    W, H = int(round(px1 - px0)), int(round(py1 - py0))
    lon = box["w"] + (np.arange(W) + .5) / W * (box["e"] - box["w"])
    lat = box["n"] - (np.arange(H) + .5) / H * (box["n"] - box["s"])
    fx = _wx(lon, n) - tx0 * 256 - .5; fy = _wy(lat, n) - ty0 * 256 - .5
    out = dict(box=box, z=z, credit="Skyways & thermals: thermal.kk7.ch, CC BY-NC-SA 4.0")
    for layer in ("skyways", "thermals"):
        m = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 4), np.uint8)
        for tx in range(tx0, tx1 + 1):
            for ty in range(ty0, ty1 + 1):
                m[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = _kk7_tile(cache, layer, z, tx, ty)
        m = (_lift if layer == "skyways" else _heat)(m).astype(np.float32)
        ix = np.clip(fx.astype(int), 0, m.shape[1] - 2); iy = np.clip(fy.astype(int), 0, m.shape[0] - 2)
        ux = np.clip(fx - ix, 0, 1)[None, :, None]; uy = np.clip(fy - iy, 0, 1)[:, None, None]
        I, J = np.meshgrid(ix, iy)
        p = m[J, I] * (1 - ux) * (1 - uy) + m[J, I + 1] * ux * (1 - uy) + m[J + 1, I] * (1 - ux) * uy + m[J + 1, I + 1] * ux * uy
        name = f"sky-{layer}.webp"
        Image.fromarray(np.clip(p, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(out_dir, name), "WEBP",
                                                                         quality=60, method=6, alpha_quality=50)
        out[layer] = name
    log(f"  KK7: z{z}, {W}x{H} px, tiles {tx1 - tx0 + 1}x{ty1 - ty0 + 1}")
    return out


# ---------------------------------------------------------------- relief
def bake_relief(box, frame, out_dir, cache=None, log=print, max_px=2000):
    """Dark shaded relief (AWS Terrain Tiles, terrarium) in the task's local km frame (x east, y north)."""
    cache = _cache(cache, "terrain")
    x0, y0 = frame.km(box["s"], box["w"]); x1, y1 = frame.km(box["n"], box["e"])
    res_m = max(14.0, (x1 - x0) * 1000 / max_px)
    Z = 14 if res_m < 20 else 13 if res_m < 40 else 12
    W, H = int((x1 - x0) * 1000 / res_m), int((y1 - y0) * 1000 / res_m)
    xs = x0 + (np.arange(W) + .5) * res_m / 1000
    ys = y1 - (np.arange(H) + .5) * res_m / 1000
    XX, YY = np.meshgrid(xs, ys)
    lat = frame.lat0 + YY / frame.ky
    lon = frame.lon0 + XX / frame.kx
    n = 2 ** Z
    px, py = _wx(lon, n), _wy(lat, n)
    tx0, tx1, ty0, ty1 = int(px.min() // 256), int(px.max() // 256), int(py.min() // 256), int(py.max() // 256)
    mos = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            fn = os.path.join(cache, f"{Z}_{tx}_{ty}.png")
            if not os.path.exists(fn):
                url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{tx}/{ty}.png"
                open(fn, "wb").write(urllib.request.urlopen(url, timeout=30).read())
            a = np.asarray(Image.open(fn).convert("RGB"), np.float32)
            mos[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    fx, fy = px - tx0 * 256 - .5, py - ty0 * 256 - .5
    ix, iy = np.clip(fx.astype(int), 0, mos.shape[1] - 2), np.clip(fy.astype(int), 0, mos.shape[0] - 2)
    ax, ay = fx - ix, fy - iy
    E = mos[iy, ix] * (1 - ax) * (1 - ay) + mos[iy, ix + 1] * ax * (1 - ay) + mos[iy + 1, ix] * (1 - ax) * ay + mos[iy + 1, ix + 1] * ax * ay
    lo_e, hi_e = np.percentile(E, 2), np.percentile(E, 99.5)
    E = np.clip(E, lo_e - 200, hi_e + 200)
    gy, gx = np.gradient(E, res_m)
    slope = np.arctan(1.6 * np.hypot(gx, gy)); asp = np.arctan2(-gx, gy)
    az, alt = math.radians(315), math.radians(40)
    hs = np.clip(np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - asp), 0, 1)
    lo, hi = np.array([92, 120, 118.]), np.array([168, 186, 176.])
    t = (np.clip((E - lo_e) / max(1, hi_e - lo_e), 0, 1) ** 0.8)[..., None]
    rgb = (lo * (1 - t) + hi * t) * (0.62 + 0.55 * hs[..., None])
    for st, a_ in ((100, -8), (500, -18)):
        c = np.floor(E / st)
        edge = (np.abs(np.diff(c, axis=0, prepend=c[:1])) + np.abs(np.diff(c, axis=1, prepend=c[:, :1]))) > 0
        rgb[edge] += a_
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(os.path.join(out_dir, "relief.jpg"), quality=76, optimize=True, progressive=True)
    log(f"  relief: {W}x{H} px at {res_m:.0f} m, z{Z}")
    return dict(file="relief.jpg", x0=round(x0, 3), x1=round(x1, 3), y0=round(y0, 3), y1=round(y1, 3), res_m=round(res_m, 1),
                credit="Terrain: Mapzen / AWS Terrain Tiles, SRTM")
