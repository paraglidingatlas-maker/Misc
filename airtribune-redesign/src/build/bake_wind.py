"""Bake the wind field for the wind animation (live tracker + fly-through), once.

Source: Open-Meteo historical forecast API (historical-forecast-api.open-meteo.com), model ECMWF IFS 0.25°,
hourly wind at 700 hPa (about 3,200 m, the top of the climbs), local time (America/Mexico_City, UTC-6).
Grid: 5 x 5 points on the model's own 0.25° grid, covering the Tapalpa Task 3 area
(19.50-20.50 N, 104.00-103.00 W), so every point is a real model value, not an interpolation by the API.
One request for all 25 points (Open-Meteo takes comma-separated coordinates).

Output: the line after the /*WINDGRID*/ marker in src/live-tracker.html and concepts/flythrough.html is replaced by
  const WINDGRID = {src, lvl, lat:[s..n], lon:[w..e], h0, h:[[[u, v] per lon] per lat] per hour};
u, v = km/h toward east / north. Also saved to src/data/wind/tapalpa-t3-700hPa.json.
Then run src/build/build_pages.py to refresh events/live.html.

Run from airtribune-redesign/:  python3 -I src/build/bake_wind.py
"""
import json, math, os, re, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
DATE, TZ, MODEL, LEVEL = "2026-11-10", "America/Mexico_City", "ecmwf_ifs025", "700hPa"
LATS = [19.50, 19.75, 20.00, 20.25, 20.50]
LONS = [-104.00, -103.75, -103.50, -103.25, -103.00]
H0, H1 = 10, 17   # local hours kept (race window 12:15 to about 16:00, with margin)

pts = [(la, lo) for la in LATS for lo in LONS]
url = ("https://historical-forecast-api.open-meteo.com/v1/forecast?"
       f"latitude={','.join(str(p[0]) for p in pts)}&longitude={','.join(str(p[1]) for p in pts)}"
       f"&start_date={DATE}&end_date={DATE}&hourly=wind_speed_{LEVEL},wind_direction_{LEVEL}"
       f"&models={MODEL}&timezone={TZ}")
res = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "airtribune-redesign wind bake"}), timeout=60))
assert len(res) == len(pts), len(res)

grid = [[[None] * len(LONS) for _ in LATS] for _ in range(H0, H1 + 1)]
for k, r in enumerate(res):
    j, i = divmod(k, len(LONS))
    t = r["hourly"]["time"]
    for hi, hr in enumerate(range(H0, H1 + 1)):
        n = t.index(f"{DATE}T{hr:02d}:00")
        s, d = r["hourly"][f"wind_speed_{LEVEL}"][n], r["hourly"][f"wind_direction_{LEVEL}"][n]
        a = math.radians(d)   # direction the wind blows FROM
        grid[hi][j][i] = [round(-s * math.sin(a), 1), round(-s * math.cos(a), 1)]

W = dict(src="ECMWF IFS 0.25°", lvl="3,200 m (700 hPa)", lat=LATS, lon=LONS, h0=H0, h=grid)
os.makedirs(os.path.join(ROOT, "src", "data", "wind"), exist_ok=True)
json.dump(dict(W, query=url), open(os.path.join(ROOT, "src", "data", "wind", "tapalpa-t3-700hPa.json"), "w"), ensure_ascii=False, indent=1)

line = "const WINDGRID = " + json.dumps(W, ensure_ascii=False, separators=(",", ":")) + ";"
for f in ("src/live-tracker.html", "concepts/flythrough.html"):
    p = os.path.join(ROOT, f); s = open(p).read()
    s2, n = re.subn(r"(/\*WINDGRID\*/\n)[^\n]*", lambda m: m.group(1) + line, s)
    assert n == 1, f"no /*WINDGRID*/ marker in {f}"
    open(p, "w").write(s2); print("updated", f)
for hr in (12, 14):
    print(hr, "h:", [[f"{math.hypot(*uv):.0f}" for uv in row] for row in grid[hr - H0]])
