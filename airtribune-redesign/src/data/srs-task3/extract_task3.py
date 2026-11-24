"""Build task3.json for the live tracker from the public Airtribune files of
SRS Advance Edition 2026 (Tapalpa, Mexico), Task 3, 10 Nov 2026.

Inputs (download first, see SOURCES.md):
  results.html  https://airtribune.com/srs-2026-6/results/task6991/day/overall
  wp.cup        https://airtribune.fra1.digitaloceanspaces.com/media/contest/waypoints/2026/11/v2-srs-2026-6.SeeYou.cup
  igc/          the unzipped https://airtribune.fra1.digitaloceanspaces.com/media/task/archive/2026/11/6991/2710_31.zip

Usage:  python3 -I extract_task3.py <results.html> <wp.cup> <igc-dir> <out.json> [n_tracks]
"""
import html, json, math, os, re, sys

res_path, cup_path, igc_dir, out_path = sys.argv[1:5]
N_TRACKS = int(sys.argv[5]) if len(sys.argv) > 5 else 20
UTC_OFFSET = -6 * 3600           # Airtribune "timeoffset": -21600, IGC header HFTZN:-6.0
GATE = 12 * 3600 + 15 * 60       # start gate 12:15:00 local (every pilot's "Start" in the results)
WIN_FROM = GATE - 20 * 60        # replay window opens 20 min before the gate
STEP = 10                        # downsample tracks to one fix every 10 s

clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
src = open(res_path, encoding="utf-8").read()

# ---- task table ----
task_tab = re.search(r"<h3>(Task T6\.3.*?)</h3><table>(.*?)</table>", src, re.S)
task_title = clean(task_tab.group(1))
task_rows = []
for r in re.findall(r"<tr>(.*?)</tr>", task_tab.group(2), re.S)[1:]:
    c = [clean(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
    task_rows.append(dict(order=c[0], check=c[1] or None, radius_km=float(c[2].split()[0]) if c[2] else None,
                          ss_es=c[3] or None, dist_km=float(c[4].split()[0]), code=c[5], name=c[6]))

# ---- waypoints ----
def cup_deg(v):
    hemi = v[-1]; v = v[:-1]
    d = int(v[:2 if hemi in "NS" else 3]); m = float(v[2 if hemi in "NS" else 3:])
    return (d + m / 60) * (-1 if hemi in "SW" else 1)
wps = {}
for line in open(cup_path, encoding="utf-8", errors="replace"):
    p = next(__import__("csv").reader([line]))
    if len(p) >= 6 and re.match(r"\d{4}\.\d{3}[NS]", p[3]):
        wps[p[1]] = dict(name=p[0], lat=round(cup_deg(p[3]), 6), lon=round(cup_deg(p[4]), 6), elev_m=float(p[5].rstrip("m")))
for t in task_rows:
    t.update({k: wps[t["code"]][k] for k in ("lat", "lon", "elev_m")})

# ---- results ----
results = []
for rk, r in re.findall(r"<tr><td>(\d+)</td>(.*?)</tr>", src[src.find("<th>Rank</th>"):], re.S):
    c = [clean(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
    row = dict(rank=int(rk), id=c[0], name=c[1], nation=c[2], glider=c[3], sponsor=c[4] or None)
    if len(c) == 17:
        row.update(start=c[5], finish=c[6], time=c[7], height_m=int(c[8]) if c[8] else None,
                   speed_kmh=float(c[10]), distance_km=float(c[11]), score=float(c[16]), goal=True)
    else:   # landed out: finish/time/height/speed columns are merged
        tail = c[-6:]
        row.update(start=c[5] if re.match(r"\d\d:\d\d", c[5]) else None, distance_km=float(tail[0]), score=float(tail[5]), goal=False)
    results.append(row)
stats = dict(re.findall(r"<td><b>([A-Za-z \-]+):</b></td><td[^>]*>([^<]+)</td>", src))

# ---- geometry (local km, x east, y north, origin = take-off) ----
TO = task_rows[0]
LAT0 = math.radians(TO["lat"])
def km(lat, lon):
    return ((lon - TO["lon"]) * 111.32 * math.cos(LAT0), (lat - TO["lat"]) * 110.574)
cyl = task_rows[1:]
C = [km(t["lat"], t["lon"]) for t in cyl]

# ---- tracks ----
def read_igc(path):
    fixes = []
    for line in open(path, encoding="ascii", errors="replace"):
        if not line.startswith("B") or len(line) < 35: continue
        hh, mm, ss = int(line[1:3]), int(line[3:5]), int(line[5:7])
        lat = int(line[7:9]) + int(line[9:14]) / 60000; lat = -lat if line[14] == "S" else lat
        lon = int(line[15:18]) + int(line[18:23]) / 60000; lon = -lon if line[23] == "W" else lon
        pa, ga = int(line[25:30]), int(line[30:35])
        t = (hh * 3600 + mm * 60 + ss + UTC_OFFSET) % 86400
        fixes.append((t, lat, lon, ga or pa))
    return fixes

def tags(fixes):
    """Times the pilot achieved SSS (exit after gate), each TP (entry) and goal (entry)."""
    out, k, inside_after_gate = [], 0, False
    for t, lat, lon, _ in fixes:
        if k >= len(cyl): break
        x, y = km(lat, lon); c = cyl[k]; d = math.hypot(x - C[k][0], y - C[k][1])
        if c["check"] == "Exit":
            if t < GATE: continue
            if d < c["radius_km"]: inside_after_gate = True
            elif inside_after_gate:   # first crossing from inside to outside after the gate
                out.append(t); k += 1
        elif d <= c["radius_km"]:
            out.append(t); k += 1
    return out

def wind_from_drift(all_fixes):
    vx = vy = n = 0
    for fx in all_fixes:
        for i in range(0, len(fx) - 60, 20):
            a, b = fx[i], fx[i + 60]
            if not (GATE - 3600 <= a[0] <= GATE + 3 * 3600) or b[0] - a[0] != 60: continue
            seg = fx[i:i + 61]
            path = sum(math.hypot(*(p - q for p, q in zip(km(*seg[j][1:3]), km(*seg[j + 1][1:3])))) for j in range(60))
            (x0, y0), (x1, y1) = km(a[1], a[2]), km(b[1], b[2])
            net = math.hypot(x1 - x0, y1 - y0)
            if (b[3] - a[3]) / 60 > 1.0 and path > 3 * net:   # climbing and circling
                vx += (x1 - x0) / 60; vy += (y1 - y0) / 60; n += 1
    if not n: return None
    vx, vy = vx / n * 3600, vy / n * 3600
    to_deg = math.degrees(math.atan2(vx, vy)) % 360
    return dict(speed_kmh=round(math.hypot(vx, vy), 1), from_deg=round((to_deg + 180) % 360), samples=n)

tracks, all_fixes = [], []
goal_rows = [r for r in results if r.get("goal")]
for r in goal_rows[:N_TRACKS]:
    p = os.path.join(igc_dir, r["id"] + ".igc")
    if not os.path.exists(p): continue
    fx = read_igc(p); all_fixes.append(fx)
    tg = tags(fx)
    if len(tg) != len(cyl): print("incomplete tags", r["name"], tg); continue
    end = tg[-1]
    keep = {t for t in tg}
    pts = [f for f in fx if WIN_FROM <= f[0] <= end and (f[0] % STEP == 0 or f[0] in keep)]
    if fx[0][0] > WIN_FROM: pts = [f for f in fx if f[0] <= end and (f[0] % STEP == 0 or f[0] in keep or f is fx[0])]
    arr = []
    for t, lat, lon, alt in pts:
        x, y = km(lat, lon); arr.append([t - GATE, round(x, 2), round(y, 2), alt])
    tracks.append(dict(id=r["id"], tags=[t - GATE for t in tg], pts=arr))
    fin = r["finish"].split(":"); off = tg[-1] - (int(fin[0]) * 3600 + int(fin[1]) * 60 + int(fin[2]))
    print(f'{r["rank"]:>3} {r["name"]:<28} goal tag {tg[-1]//3600:02d}:{tg[-1]//60%60:02d}:{tg[-1]%60:02d}  official {r["finish"]}  diff {off:+d}s  pts {len(arr)}')

data = dict(
    event=dict(name="SRS Advance Edition 2026", series="Sports-Class Racing Series 2026", round=6,
               place="Tapalpa", country="Mexico", dates="7–14 Nov 2026", airtribune="https://airtribune.com/srs-2026-6/"),
    task=dict(number=3, title=task_title, date="2026-11-10", type="Race to goal",
              distance_km=task_rows[-1]["dist_km"], start_gate_local="12:15:00", utc_offset_h=-6,
              start_gate_note="Inferred: every pilot's Start in the official results is 12:15:00 (single start gate).",
              turnpoints=task_rows, scoring=stats),
    results=results,
    replay=dict(note="Tracks: official IGC archive of the task, top finishers only, downsampled to one fix per 10 s. "
                     "Local km coordinates: x east, y north, origin = take-off D01; t = seconds from the 12:15 start gate.",
                step_s=STEP, window_from_s=WIN_FROM - GATE, wind_estimate=wind_from_drift(all_fixes), tracks=tracks),
)
json.dump(data, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("wrote", out_path, os.path.getsize(out_path), "bytes;", len(tracks), "tracks;", len(results), "results")
