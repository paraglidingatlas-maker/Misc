"""Common task package: one format for every comp and task, whatever website it came from.

A reader (readers/*.py) turns a link or a set of files into a RAW TASK (plain dict, below). build() then does the
shared steps (tags from the tracklogs, tracks encoding, area box, wind, KK7, relief) and writes the package:

  events/tasks/<comp>/<task>/data.json     event, task, turnpoints, results, wind, sky images, track index
  events/tasks/<comp>/<task>/tracks.json   every pilot's track (delta-encoded ints, see encode_track)
  events/tasks/<comp>/<task>/sky-<layer>.webp, relief.jpg   (optional images)
  events/tasks/index.json                  list of all packages (the index page reads it)

The pages (live tracker, fly-through, broadcast, voice-over) read only this package (?task=<comp>/<task>).

RAW TASK (what a reader returns):
  comp      slug, e.g. "srs-2026-6"            task_id  slug, e.g. "t3"
  source    {kind, url, files:[...], note}
  event     {name, series, place, country, dates, url}
  task      {no, title, date "YYYY-MM-DD", utc_offset_s, type "race"|"elapsed", distance_km (official, optional),
             gates ["HH:MM:SS", ...] (local), deadline "HH:MM:SS" (optional),
             turnpoints [{code, name, lat, lon, elev_m, radius_m, role "TO"|"SSS"|"TP"|"ESS"|"GOAL",
                          check "exit"|"enter", short (optional)}]}
  scoring   {pilots, goal, ...}  (optional, free-form; pilots/goal are ints)
  results   [{rank, id, name, nation, glider, start, finish, time, distance_km, score, goal}]
  igc       {pilot_id: path-or-bytes}   (pilot_id matches results[].id; unknown ids are kept with the IGC's name)
"""
import io, json, math, os, re, time, zipfile

FORMAT = "airtribune-task/1"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))           # airtribune-redesign/
TASKS = os.path.join(ROOT, "events", "tasks")

STEP = 5                # seconds between stored fixes
PRE = 20 * 60           # keep tracks from 20 min before the first gate
POST = 120              # and up to 2 min after goal / landing


# ---------------------------------------------------------------- time and geometry
def hms_s(s):
    """'HH:MM[:SS]' -> seconds of the day"""
    p = [int(x) for x in s.split(":")] + [0]
    return p[0] * 3600 + p[1] * 60 + p[2]


def s_hms(s):
    s = int(round(s)) % 86400
    return "%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60)


class Frame:
    """Local flat frame in km: x east, y north, origin = take-off (same formula the pages use)."""
    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.kx, self.ky = 111.32 * math.cos(math.radians(lat0)), 110.574

    def km(self, lat, lon):
        return (lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky

    def ll(self, x, y):
        return self.lat0 + y / self.ky, self.lon0 + x / self.kx


def nice_dates(s):
    """'07 - 14 Nov, 2026' -> '7–14 Nov 2026'; '28 Feb - 05 Mar, 2026' -> '28 Feb – 5 Mar 2026'"""
    if not s:
        return s
    m = re.match(r"^\s*(\d+)\s*(?:([A-Z][a-z]{2})\s*)?-\s*(\d+)\s+([A-Z][a-z]{2}),?\s*(\d{4})\s*$", s)
    if not m:
        return s
    d1, m1, d2, m2, y = m.groups()
    return f"{int(d1)} {m1} – {int(d2)} {m2} {y}" if m1 and m1 != m2 else f"{int(d1)}–{int(d2)} {m2} {y}"


def short_name(n):
    """'TAMAZULA' -> 'Tamazula', 'LZ AMACUECA' -> 'LZ Amacueca'; mixed-case names are kept."""
    if n != n.upper():
        return n
    return " ".join(w if len(w) <= 2 else w.title() for w in n.split())


# ---------------------------------------------------------------- IGC
def read_igc(src, utc_offset_s):
    """IGC (path or bytes) -> (header dict, [(t_local_s, lat, lon, alt_m)]). GPS altitude, else pressure."""
    data = open(src, "rb").read() if isinstance(src, str) else src
    head, fixes, last = {}, [], None
    day = 0
    for line in data.decode("ascii", "replace").splitlines():
        if line.startswith("H") and ":" in line:
            k, v = line[2:].split(":", 1)
            head[re.sub(r"[^A-Z]", "", k.upper())[:12]] = v.strip()
        if not line.startswith("B") or len(line) < 35 or line[24] not in "AV":
            continue
        try:
            s = int(line[1:3]) * 3600 + int(line[3:5]) * 60 + int(line[5:7])
            lat = int(line[7:9]) + int(line[9:14]) / 60000
            lon = int(line[15:18]) + int(line[18:23]) / 60000
            pa, ga = int(line[25:30]), int(line[30:35])
        except ValueError:
            continue
        if last is not None and s + day < last - 43200:     # passed midnight UTC
            day += 86400
        t = s + day + utc_offset_s
        last = s + day
        if fixes and t <= fixes[-1][0]:
            continue
        fixes.append((t, -lat if line[14] == "S" else lat, -lon if line[23] == "W" else lon, ga or pa))
    return head, fixes


def igc_pilot_name(head):
    for k in ("PLTPILOTINC", "PLTPILOT", "PILOT", "PILOTINCHARG"):
        for hk, v in head.items():
            if hk.startswith(k[:6]) and v:
                return v
    return None


def unzip_igc(path_or_bytes):
    """zip (path or bytes) -> {stem: bytes} for every .igc inside."""
    z = zipfile.ZipFile(path_or_bytes if isinstance(path_or_bytes, str) else io.BytesIO(path_or_bytes))
    out = {}
    for n in z.namelist():
        if n.lower().endswith(".igc"):
            out[os.path.splitext(os.path.basename(n))[0]] = z.read(n)
        elif n.lower().endswith(".zip"):          # some archives nest zips
            out.update(unzip_igc(z.read(n)))
    return out


# ---------------------------------------------------------------- tags
def tag_times(fixes, frame, cyl, gates):
    """Times (local s) a pilot achieved each cylinder after take-off: SSS (crossing in the start direction after
    a gate), then each TP / ESS / goal (entry, or exit when check == 'exit'). Returns a list, shorter when the
    pilot landed out."""
    out, k, ok_side = [], 0, False
    first_gate = gates[0] if gates else -1e9
    C = [frame.km(c["lat"], c["lon"]) for c in cyl]
    for t, lat, lon, _ in fixes:
        if k >= len(cyl):
            break
        x, y = frame.km(lat, lon)
        c = cyl[k]
        inside = math.hypot(x - C[k][0], y - C[k][1]) * 1000 <= c["radius_m"]
        if c["role"] == "SSS":
            if t < first_gate:
                continue
            want_inside_first = c.get("check", "exit") == "exit"
            if inside == want_inside_first:
                ok_side = True
            elif ok_side:
                out.append(t); k += 1
        elif inside != (c.get("check") == "exit"):
            out.append(t); k += 1
    return out


# ---------------------------------------------------------------- track encoding
def encode_track(fixes, frame, t0, t_from, t_to, keep=()):
    """Flat int list [t, x, y, alt, dt, dx, dy, dalt, ...]: t = s from the first gate, x/y = metres east/north of
    take-off, alt = m. First group absolute, the rest deltas. One fix every STEP s, plus the exact tag fixes."""
    keep = set(int(k) for k in keep)
    flat, prev = [], None
    for t, lat, lon, alt in fixes:
        if t < t_from or t > t_to:
            continue
        if (t - t0) % STEP and int(t) not in keep:
            continue
        x, y = frame.km(lat, lon)
        q = [int(t - t0), round(x * 1000), round(y * 1000), int(alt)]
        flat += q if prev is None else [a - b for a, b in zip(q, prev)]
        prev = q
    return flat


def wind_from_drift(tracks, frame, t_from, t_to):
    """Mean drift of all pilots while circling and climbing (km/h, FROM deg): an estimate, not a measurement."""
    vx = vy = n = 0
    for fx in tracks:
        for i in range(0, len(fx) - 60, 20):
            a, b = fx[i], fx[i + 60]
            if not (t_from <= a[0] <= t_to) or b[0] - a[0] != 60:
                continue
            seg = [frame.km(p[1], p[2]) for p in fx[i:i + 61]]
            path = sum(math.hypot(seg[j + 1][0] - seg[j][0], seg[j + 1][1] - seg[j][1]) for j in range(60))
            net = math.hypot(seg[-1][0] - seg[0][0], seg[-1][1] - seg[0][1])
            if (b[3] - a[3]) / 60 > 1.0 and path > 3 * net:
                vx += (seg[-1][0] - seg[0][0]) / 60; vy += (seg[-1][1] - seg[0][1]) / 60; n += 1
    if not n:
        return None
    vx, vy = vx / n * 3600, vy / n * 3600
    to = math.degrees(math.atan2(vx, vy)) % 360
    return dict(speed_kmh=round(math.hypot(vx, vy), 1), from_deg=round((to + 180) % 360), samples=n,
                note="Mean drift of the tracks while circling and climbing; an estimate, not a measured wind.")


# ---------------------------------------------------------------- optimised route
def optimised_route(frame, cyl):
    """Shortest route from take-off touching each cylinder (same iteration as the pages). km points + leg lengths."""
    C = [frame.km(c["lat"], c["lon"]) for c in cyl]
    R = [(c.get("radius_m") or 0) / 1000 for c in cyl]
    P = [list(c) for c in C]
    d = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    for _ in range(40):
        for i in range(len(C)):
            prev = (0.0, 0.0) if i == 0 else P[i - 1]
            nxt = P[i + 1] if i + 1 < len(C) else None
            if not R[i]:
                P[i] = list(C[i]); continue
            if nxt is None:
                a = math.atan2(prev[1] - C[i][1], prev[0] - C[i][0]); P[i] = [C[i][0] + R[i] * math.cos(a), C[i][1] + R[i] * math.sin(a)]; continue
            best, bp = 1e18, P[i]
            for k in range(360):
                a = k / 360 * 2 * math.pi; x = [C[i][0] + R[i] * math.cos(a), C[i][1] + R[i] * math.sin(a)]
                f = d(prev, x) + d(x, nxt)
                if f < best:
                    best, bp = f, x
            if cyl[i]["role"] != "SSS":   # a point inside the cylinder on the straight line is shorter still
                dx, dy = nxt[0] - prev[0], nxt[1] - prev[1]; L = dx * dx + dy * dy or 1
                t = max(0, min(1, ((C[i][0] - prev[0]) * dx + (C[i][1] - prev[1]) * dy) / L)); q = [prev[0] + t * dx, prev[1] + t * dy]
                if d(q, C[i]) <= R[i]:
                    bp = q
            P[i] = bp
    route = [[0.0, 0.0]] + P
    legs = [d(route[k], route[k + 1]) for k in range(len(P))]
    return route, legs


def derive_results(pilots, fixes_by_id, names, frame, cyl, G0):
    """No results file: rank by goal time, then by distance along the optimised route (an estimate)."""
    route, legs = optimised_route(frame, cyl)
    total = sum(legs); suffix = [sum(legs[k:]) for k in range(len(legs))] + [0]
    out = []
    for p in pilots:
        fx, k = fixes_by_id[p["id"]], 0
        tags = [t + G0 for t in p["tags"]]
        best = total
        for t, lat, lon, _ in fx:
            while k < len(tags) and t >= tags[k]:
                k += 1
            if k == 0:
                continue                    # not started
            if k >= len(route) - 1:
                best = 0; break
            x, y = frame.km(lat, lon)
            best = min(best, math.hypot(x - route[k + 1][0], y - route[k + 1][1]) + suffix[k + 1])
        fin = s_hms(tags[-1]) if p["goal"] else None
        el = (tags[-1] - (tags[0] if cyl[0]["role"] == "SSS" else G0)) if p["goal"] else None
        out.append(dict(rank=None, id=p["id"], name=names.get(p["id"]) or p["id"], nation=None, glider=None,
                        start=s_hms(tags[0]) if tags else None, finish=fin, time=s_hms(el) if el else None,
                        distance_km=round(total - best, 2), score=None, goal=p["goal"], estimated=True))
    out.sort(key=lambda r: (not r["goal"], r["finish"] or "", -(r["distance_km"] or 0)))
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out, round(total, 1)


# ---------------------------------------------------------------- area box
def area_box(tps, margin_km=6.0):
    """Lat/lon box around every cylinder plus a margin (km)."""
    fr = Frame(tps[0]["lat"], tps[0]["lon"])
    xs, ys = [], []
    for t in tps:
        x, y = fr.km(t["lat"], t["lon"]); r = (t.get("radius_m") or 0) / 1000
        xs += [x - r, x + r]; ys += [y - r, y + r]
    m = margin_km
    return dict(s=round(fr.ll(0, min(ys) - m)[0], 3), n=round(fr.ll(0, max(ys) + m)[0], 3),
                w=round(fr.ll(min(xs) - m, 0)[1], 3), e=round(fr.ll(max(xs) + m, 0)[1], 3))


# ---------------------------------------------------------------- build
def build(raw, opts=None, log=print):
    """Shared steps for every source. opts: {tracks_n, no_wind, no_sky, relief, cache, short{name: short}}"""
    opts = opts or {}
    tk = raw["task"]
    off = tk["utc_offset_s"]
    tps = tk["turnpoints"]
    assert tps and tps[0]["role"] == "TO", "first turnpoint must be take-off"
    for t in tps:
        t["short"] = (opts.get("short") or {}).get(t["name"]) or t.get("short") or short_name(t["name"])
    frame = Frame(tps[0]["lat"], tps[0]["lon"])
    cyl = tps[1:]
    gates = [hms_s(g) for g in tk.get("gates") or []]
    if not gates:
        raise SystemExit("no start gate: give --gate HH:MM")
    G0 = gates[0]
    deadline = hms_s(tk["deadline"]) if tk.get("deadline") else None
    res = {r["id"]: r for r in raw.get("results", [])}

    # ---- tracks
    pilots, fixes_all, fixes_by_id, igc_names = [], [], {}, {}
    for pid, src in (raw.get("igc") or {}).items():
        head, fx = read_igc(src, off)
        if len(fx) < 30:
            log("  skip", pid, "(too few fixes)"); continue
        tg = tag_times(fx, frame, cyl, gates)
        if deadline:
            tg = [t for t in tg if t <= deadline]
        r = res.get(pid) or dict(id=pid, name=igc_pilot_name(head) or pid, rank=None)
        in_goal = len(tg) == len(cyl)
        end = (tg[-1] + POST) if in_goal else fx[-1][0]
        if deadline:
            end = min(end, deadline + POST)
        flat = encode_track(fx, frame, G0, G0 - PRE, end, keep=tg)
        if len(flat) < 8:
            continue
        fixes_all.append(fx); fixes_by_id[pid] = fx; igc_names[pid] = igc_pilot_name(head)
        pilots.append(dict(id=pid, tags=[t - G0 for t in tg], goal=in_goal, d=flat, _rank=r.get("rank") or 10 ** 6))
    if raw.get("derive_results") and pilots:
        raw["results"], tk["distance_km"] = derive_results(pilots, fixes_by_id, igc_names, frame, cyl, G0)
        rk = {r["id"]: r["rank"] for r in raw["results"]}
        for p in pilots:
            p["_rank"] = rk.get(p["id"], 10 ** 6)
        log("  results: worked out from the tracklogs (no results file)")
    if not tk.get("distance_km"):
        tk["distance_km"] = round(sum(optimised_route(frame, cyl)[1]), 1)
    pilots.sort(key=lambda p: (p["_rank"], p["id"]))
    for p in pilots:
        p.pop("_rank")
    log(f"  tracks: {len(pilots)} pilots, {sum(p['goal'] for p in pilots)} reached goal by the tracklog")

    comp, tid = raw["comp"], raw["task_id"]
    out = os.path.join(TASKS, comp, tid)
    os.makedirs(out, exist_ok=True)
    box = area_box(tps)
    wind = dict(drift=wind_from_drift(fixes_all, frame, G0 - 3600, G0 + 3 * 3600) if fixes_all else None)
    if not opts.get("no_wind"):
        from shared import fetch_wind
        try:
            wind.update(fetch_wind(box, tps[0], tk["date"], off, G0, log=log))
        except Exception as e:                       # wind is a nice-to-have: never block the package
            log("  wind: failed,", e)
    sky = None
    if not opts.get("no_sky"):
        from shared import bake_kk7
        try:
            sky = bake_kk7(box, out, opts.get("cache"), log=log)
        except Exception as e:
            log("  KK7: failed,", e)
    relief = None
    if opts.get("relief"):
        from shared import bake_relief
        relief = bake_relief(box, frame, out, opts.get("cache"), log=log)

    dist = tk.get("distance_km")
    ev = dict(raw["event"])
    ev["dates"] = nice_dates(ev.get("dates"))
    if not ev.get("short"):
        w = (ev.get("name") or "").split()
        abbr = w[0] if w and w[0].isupper() and 2 <= len(w[0]) <= 5 else ""
        ev["short"] = f"{abbr} {ev['place']} {tk['date'][:4]}" if abbr and ev.get("place") else ev.get("name")
    data = dict(
        format=FORMAT, id=f"{comp}/{tid}", built=time.strftime("%Y-%m-%d"), source=raw.get("source", {}),
        event=ev,
        task=dict(no=tk.get("no"), title=tk.get("title"), date=tk["date"], utc_offset_s=off, type=tk.get("type", "race"),
                  distance_km=dist, gates=[s_hms(g) for g in gates], deadline=tk.get("deadline"),
                  turnpoints=[{k: t.get(k) for k in ("code", "name", "short", "lat", "lon", "elev_m", "radius_m", "role", "check", "ess")}
                              for t in tps]),
        scoring=raw.get("scoring") or {},
        results=raw.get("results", []),
        wind=wind, sky=sky, relief=relief, box=box,
        tracks=dict(file="tracks.json", count=len(pilots), step_s=STEP, t0="first gate",
                    units="t s from the first gate; x, y m east/north of take-off; alt m (GPS)"),
    )
    if data["scoring"].get("pilots") is None and data["results"]:
        data["scoring"]["pilots"] = len(data["results"])
    if data["scoring"].get("goal") is None and data["results"]:
        data["scoring"]["goal"] = sum(1 for r in data["results"] if r.get("goal"))
    json.dump(data, open(os.path.join(out, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(dict(format=FORMAT, pilots=pilots), open(os.path.join(out, "tracks.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    log(f"  wrote {os.path.relpath(out, ROOT)}/data.json ({os.path.getsize(os.path.join(out, 'data.json')) // 1024} KB) "
        f"and tracks.json ({os.path.getsize(os.path.join(out, 'tracks.json')) // 1024} KB)")
    update_index(data)
    return out


def update_index(data):
    p = os.path.join(TASKS, "index.json")
    idx = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else dict(format=FORMAT, tasks=[])
    ev, tk = data["event"], data["task"]
    row = dict(id=data["id"], event=ev.get("name"), series=ev.get("series"), place=ev.get("place"), country=ev.get("country"),
               task=tk.get("no"), title=tk.get("title"), date=tk["date"], distance_km=tk.get("distance_km"),
               pilots=data["scoring"].get("pilots"), goal=data["scoring"].get("goal"), tracks=data["tracks"]["count"],
               source=data["source"].get("kind"), url=data["source"].get("url"))
    idx["tasks"] = [t for t in idx["tasks"] if t["id"] != row["id"]] + [row]
    idx["tasks"].sort(key=lambda t: (t["date"], t["id"]), reverse=True)
    json.dump(idx, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
