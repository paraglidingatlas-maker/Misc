"""Files fallback: any comp, any website. Give the task file, the tracklogs and (optionally) the results.

  new_task.py --files <task> <tracks> [<results>] --comp <slug> [--task-id t1] [--event "…" --place … --country …]
      <task>     XCTrack .xctsk (JSON), SeeYou .cup with a task section, or FS .fsdb (then see fsdb.py)
      <tracks>   a .zip of IGC files, a folder of IGC files, or several .igc files
      <results>  optional: .csv (columns rank,id,name,nation,glider,start,finish,time,distance_km,score; any
                 subset, header names are matched loosely) or an FS results .html export
  Missing facts come from options (--date, --gate, --utc-offset) or are worked out: the date from the IGC
  headers, the time zone from Open-Meteo for take-off, results from the tracklogs (goal time, then distance).
Pilot ids are the IGC file names (without .igc) unless the results file maps them.
"""
import csv, datetime as dt, io, json, math, os, re, urllib.request
from .common import get, rows_of, fs_results_table, parse_cup


# ---------------------------------------------------------------- tracks
def load_tracks(paths):
    """zips, folders and .igc files -> {stem: bytes}"""
    from taskpkg import unzip_igc
    out = {}
    for p in paths or []:
        if "://" in p:
            b = get(p, binary=True, min_gap=2.0)
            out.update(unzip_igc(b) if p.lower().split("?")[0].endswith(".zip") else {os.path.basename(p).rsplit(".", 1)[0]: b})
        elif os.path.isdir(p):
            for dp, _, fs in os.walk(p):
                for f in fs:
                    if f.lower().endswith(".igc"):
                        out[f[:-4]] = open(os.path.join(dp, f), "rb").read()
                    elif f.lower().endswith(".zip"):
                        out.update(unzip_igc(os.path.join(dp, f)))
        elif p.lower().endswith(".zip"):
            out.update(unzip_igc(p))
        elif p.lower().endswith(".igc"):
            out[os.path.basename(p)[:-4]] = open(p, "rb").read()
    return out


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(sorted(re.findall(r"[a-z]+", s)))


def match_tracks(igc, results, filenames=None):
    """{stem: bytes} -> {pilot_id: bytes}: by the scorer's file name, by id = stem, by a number in the stem,
    by CIVL id, then by the pilot name in the IGC header. Unmatched tracks keep their stem as id."""
    from taskpkg import igc_pilot_name
    filenames = filenames or {}
    by_stem = {k: v for k, v in igc.items()}
    out = {}
    ids = {str(r["id"]): r for r in results}
    for pid, fn in filenames.items():
        st = os.path.basename(fn.replace("\\", "/")).rsplit(".", 1)[0]
        if st in by_stem:
            out[pid] = by_stem.pop(st)
    for st in list(by_stem):
        if st in ids and st not in out:
            out[st] = by_stem.pop(st); continue
        nums = re.findall(r"\d+", st)
        hit = next((n for n in nums if n in ids and n not in out), None) or next(
            (r["id"] for r in results if r.get("civl") and r["civl"] in nums and r["id"] not in out), None)
        if hit:
            out[hit] = by_stem.pop(st)
    names = {_norm(r["name"]): r["id"] for r in results if r.get("name")}
    for st in list(by_stem):
        head = by_stem[st][:4000].decode("ascii", "replace")
        m = re.search(r"^HF?PLT[^:]*:(.*)$", head, re.M)
        pid = names.get(_norm(m.group(1))) if m else None
        if pid and pid not in out:
            out[pid] = by_stem.pop(st)
        else:
            out[st] = by_stem.pop(st)
    return out


def igc_date(b):
    m = re.search(rb"HFDTE(?:DATE:)?(\d\d)(\d\d)(\d\d)", b[:4000])
    return f"20{m.group(3).decode()}-{m.group(2).decode()}-{m.group(1).decode()}" if m else None


def tz_offset(lat, lon, date):
    """UTC offset (s) at take-off on that date, from Open-Meteo's time-zone lookup (timezone=auto)."""
    url = (f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&start_date={date}&end_date={date}&hourly=temperature_2m&timezone=auto")
    return int(json.loads(get(url))["utc_offset_seconds"])


# ---------------------------------------------------------------- task files
def parse_xctsk(text):
    d = json.loads(text)
    if "taskType" not in d and "t" in d:                  # XCTrack QR / compact v2
        raise SystemExit("compact XCTrack task (QR format) not supported: export the .xctsk file")
    tps, gates_utc = [], (d.get("sss") or {}).get("timeGates") or []
    n = len(d["turnpoints"])
    for k, t in enumerate(d["turnpoints"]):
        w = t["waypoint"]; ty = (t.get("type") or "").upper()
        role = "TO" if ty == "TAKEOFF" else "SSS" if ty == "SSS" else "GOAL" if k == n - 1 else "ESS" if ty == "ESS" else "TP"
        tps.append(dict(code=w.get("name"), name=w.get("description") or w.get("name"), lat=w["lat"], lon=w["lon"],
                        elev_m=float(w.get("altSmoothed") or 0), radius_m=None if role == "TO" else float(t.get("radius") or 400),
                        role=role, check="enter", ess=(ty == "ESS" or (role == "GOAL" and not any(x.get("type") == "ESS" for x in d["turnpoints"])))))
    if tps[0]["role"] != "TO":           # no take-off in the task: use the first point as take-off
        tps.insert(0, dict(tps[0], role="TO", radius_m=None, code=tps[0]["code"] + "-TO"))
    sss = next((t for t in tps if t["role"] == "SSS"), None)
    if sss:
        sss["check"] = "exit" if (d.get("sss") or {}).get("direction", "EXIT").upper() == "EXIT" else "enter"
    dl = ((d.get("goal") or {}).get("deadline") or "").rstrip("Z")
    return dict(turnpoints=tps, gates_utc=[g.rstrip("Z") for g in gates_utc], deadline_utc=dl or None,
                type="elapsed" if (d.get("sss") or {}).get("type", "RACE").upper() == "ELAPSED-TIME" else "race",
                goal_line=(d.get("goal") or {}).get("type", "").upper() == "LINE")


def parse_cup_task(text):
    """SeeYou .cup: first task after '-----Related Tasks-----'; ObsZone lines give radii (R1)."""
    wps = parse_cup(text.split("-----Related Tasks-----")[0])
    part = text.split("-----Related Tasks-----")
    if len(part) < 2:
        raise SystemExit(".cup file has no task section")
    lines = [l for l in part[1].splitlines() if l.strip()]
    names = next(csv.reader([lines[0]]))[1:]
    names = [n for n in names if n]
    radii = {}
    for l in lines[1:]:
        if l.startswith("ObsZone="):
            kv = dict(x.split("=", 1) for x in l.split(",") if "=" in x)
            r = re.match(r"([\d.]+)(km|m)?", kv.get("R1", ""))
            if r:
                radii[int(kv["ObsZone"])] = float(r.group(1)) * (1000 if r.group(2) == "km" else 1)
    byname = {v["name"]: dict(v, code=k) for k, v in wps.items()}
    tps = []
    for k, n in enumerate(names):
        w = byname.get(n) or wps.get(n)
        if not w:
            raise SystemExit(f"task point {n} not in the .cup waypoints")
        role = "TO" if k == 0 else "SSS" if k == 1 else "GOAL" if k == len(names) - 1 else "TP"
        tps.append(dict(code=w.get("code", n), name=w["name"], lat=w["lat"], lon=w["lon"], elev_m=w["elev_m"],
                        radius_m=None if k == 0 else radii.get(k, 400.0), role=role, check="enter", ess=(role == "GOAL")))
    s, to = tps[1], tps[0]
    d = math.hypot((s["lon"] - to["lon"]) * 111.32 * math.cos(math.radians(to["lat"])), (s["lat"] - to["lat"]) * 110.574)
    s["check"] = "exit" if d * 1000 < s["radius_m"] else "enter"
    return dict(turnpoints=tps, gates_utc=[], deadline_utc=None, type="race")


# ---------------------------------------------------------------- results
def read_results(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if path.lower().endswith((".html", ".htm")):
        rows = rows_of(text)
        i = next(i for i, r in enumerate(rows) if r[0].lower() in ("rank", "#", "pos"))
        return fs_results_table([["rank"] + [h.lower() for h in rows[i][1:]]] + rows[i + 1:])
    rd = list(csv.reader(io.StringIO(text)))
    hdr = [re.sub(r"[^a-z]", "", h.lower()) for h in rd[0]]
    alias = dict(rank="rank pos position place", id="id pilotid no number", name="name pilot", nation="nation nat country",
                 glider="glider wing", start="start ss", finish="finish ess goal", time="time sstime",
                 distance_km="distancekm distance dist", score="score points total")
    col = {k: next((i for i, h in enumerate(hdr) if h in v.split()), None) for k, v in alias.items()}
    out = []
    for r in rd[1:]:
        if not any(r):
            continue
        g = lambda k: r[col[k]].strip() if col[k] is not None and col[k] < len(r) else None
        num = lambda v: float(v) if v and re.match(r"^-?[\d.]+$", v) else None
        fin = g("finish")
        out.append(dict(rank=int(g("rank")) if (g("rank") or "").isdigit() else None, id=g("id") or g("name"), name=g("name"),
                        nation=g("nation"), glider=g("glider"), start=g("start"), finish=fin, time=g("time"),
                        distance_km=num(g("distance_km")), score=num(g("score")), goal=bool(fin and re.match(r"\d\d?:\d\d", fin))))
    return out


# ---------------------------------------------------------------- reader
def _utc_to_local(hms_utc, off):
    if not hms_utc:
        return None
    t = hms_utc.split("T")[-1]
    p = [int(x) for x in t.split(":")] + [0]
    s = (p[0] * 3600 + p[1] * 60 + p[2] + off) % 86400
    return "%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60)


def read(link, opts):
    files = list(opts.get("files") or [])
    task_f = next((f for f in files if f.lower().endswith((".xctsk", ".cup", ".fsdb"))), None)
    if not task_f:
        raise SystemExit("--files needs a task file (.xctsk, .cup or .fsdb)")
    if task_f.lower().endswith(".fsdb"):
        from . import fsdb
        return fsdb.read(None, opts)
    res_f = next((f for f in files if f.lower().endswith((".csv", ".html", ".htm"))), None)
    text = get(task_f) if "://" in task_f else open(task_f, encoding="utf-8", errors="replace").read()
    t = parse_xctsk(text) if task_f.lower().endswith(".xctsk") else parse_cup_task(text)
    igc_raw = load_tracks([f for f in files if f not in (task_f, res_f)])
    results = read_results(res_f) if res_f else []
    to = t["turnpoints"][0]
    date = opts.get("date") or next((igc_date(b) for b in igc_raw.values() if igc_date(b)), None)
    if not date:
        raise SystemExit("task date not found: give --date YYYY-MM-DD")
    off = opts.get("utc_offset_s")
    if off is None:
        off = tz_offset(to["lat"], to["lon"], date)
    gates = opts.get("gates") or [_utc_to_local(g, off) for g in t["gates_utc"]]
    if not gates:
        raise SystemExit("start gate not in the task file: give --gate HH:MM (local)")
    igc = match_tracks(igc_raw, results) if results else igc_raw
    comp = opts.get("comp") or "comp"
    return dict(
        comp=comp, task_id=opts.get("task_id") or f"t{opts.get('task') or 1}",
        source=dict(kind="files", url=None, files=[os.path.basename(f) for f in files]),
        event=dict(name=(opts.get("event") or {}).get("name") or comp, series=None, place=None, country=None, dates=None, url=None),
        task=dict(no=opts.get("task") or 1, title=None, date=date, utc_offset_s=off, type=t["type"], distance_km=None,
                  gates=gates, deadline=opts.get("deadline") or _utc_to_local(t.get("deadline_utc"), off), turnpoints=t["turnpoints"]),
        scoring={}, results=results, igc=igc, derive_results=not results)
