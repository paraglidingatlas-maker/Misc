"""Helpers shared by the readers: polite cached HTTP, HTML tables, waypoint files, results tables."""
import csv, hashlib, html, io, json, os, re, time, urllib.request

UA = "Mozilla/5.0 (compatible; airtribune-redesign task pipeline)"
_last = [0.0]


def cache_dir():
    d = os.path.join(os.environ.get("TASK_CACHE", "/tmp/task-cache"), "http")
    os.makedirs(d, exist_ok=True)
    return d


def get(url, binary=False, min_gap=1.0, headers=None, data=None):
    """GET (or POST with data) with a file cache and at most one request per min_gap seconds per run."""
    key = hashlib.sha1((url + (json.dumps(data) if data else "")).encode()).hexdigest()[:20]
    fn = os.path.join(cache_dir(), key)
    if not os.path.exists(fn):
        wait = _last[0] + min_gap - time.time()
        if wait > 0:
            time.sleep(wait)
        body = None
        if data is not None:
            body = data if isinstance(data, bytes) else urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, **(headers or {})})
        b = urllib.request.urlopen(req, timeout=120).read()
        _last[0] = time.time()
        open(fn, "wb").write(b)
    b = open(fn, "rb").read()
    return b if binary else b.decode("utf-8", "replace")


import urllib.parse  # noqa: E402


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def rows_of(src):
    """Every table row in document order (nested tables flattened); a row = list of cell texts,
    colspan cells padded with ''. Cell text runs to the next cell, row or table tag."""
    rows, cur = [], None
    toks = list(re.finditer(r"<(/?)(tr|td|th|table)\b([^>]*)>", src, re.I))
    for k, m in enumerate(toks):
        close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if tag == "tr" and not close:
            if cur: rows.append(cur)
            cur = []
        elif tag in ("td", "th") and not close and cur is not None:
            end = toks[k + 1].start() if k + 1 < len(toks) else len(src)
            cur.append(clean(src[m.end():end]))
            cs = re.search(r"colspan=\"?(\d+)", attrs)
            cur += [""] * (int(cs.group(1)) - 1 if cs else 0)
        elif tag == "table" and cur:
            rows.append(cur); cur = None
    if cur: rows.append(cur)
    return [r for r in rows if r]


def block(rows, first):
    """Rows from the header row whose first cell is `first` up to the next header-like row."""
    i = next(i for i, r in enumerate(rows) if r[0].lower() == first)
    out = [rows[i]]
    for r in rows[i + 1:]:
        if r[0].lower() in ("rank", "order") or (out and len(r) < 3):
            break
        out.append(r)
    return out


# ---------------------------------------------------------------- waypoints
def _cup_deg(v):
    hemi = v[-1]; v = v[:-1]
    n = 2 if hemi in "NS" else 3
    return (int(v[:n]) + float(v[n:]) / 60) * (-1 if hemi in "SW" else 1)


def parse_cup(text):
    """SeeYou .cup -> {code: {name, lat, lon, elev_m}}"""
    wps = {}
    for p in csv.reader(io.StringIO(text)):
        if len(p) >= 6 and re.match(r"\d{4}\.\d{3}[NS]", p[3]):
            e = re.match(r"[-\d.]+", p[5] or "0")
            elev = float(e.group(0)) if e else 0.0
            if p[5].endswith("ft"):
                elev *= 0.3048
            wps[p[1] or p[0]] = dict(name=p[0], lat=round(_cup_deg(p[3]), 6), lon=round(_cup_deg(p[4]), 6), elev_m=elev)
    return wps


# ---------------------------------------------------------------- FS-style HTML (Airtribune, many FS exports)
def fs_task_table(rows):
    """FS task table rows (header Order / Check / Radius / SS/ES / Distance / Name / Description) -> turnpoints"""
    hdr = [h.lower() for h in rows[0]]
    col = lambda *names: next(i for i, h in enumerate(hdr) if any(h.startswith(n) for n in names))
    i_ord, i_chk, i_rad, i_sses, i_dist, i_code = col("order", "#"), col("check", "type"), col("radius"), col("ss/es", "ss"), col("distance"), col("name", "id")
    i_desc = next((i for i, h in enumerate(hdr) if h.startswith("desc")), None)
    tps = []
    for c in rows[1:]:
        if len(c) <= i_code:
            continue
        o, sses = c[i_ord].upper(), c[i_sses].upper()
        role = "TO" if o in ("TO", "T/O", "TAKEOFF") else "SSS" if sses == "SS" else "GOAL" if o == "GOAL" else "ESS" if sses == "ES" else "TP"
        rad = re.match(r"([\d.]+)\s*(k?m)", c[i_rad] or "")
        r_m = (float(rad.group(1)) * (1000 if rad.group(2) == "km" else 1)) if rad else None
        d = re.match(r"([\d.]+)", c[i_dist] or "")
        tps.append(dict(code=c[i_code], name=(c[i_desc] if i_desc is not None and c[i_desc] else c[i_code]), role=role,
                        check="exit" if c[i_chk].lower().startswith("exit") else "enter", radius_m=r_m,
                        ess=(sses == "ES"), dist_km=float(d.group(1)) if d else None))
    if tps and tps[-1]["role"] != "GOAL":
        tps[-1]["role"] = "GOAL"
    return tps


def fs_results_table(rows):
    """FS results table (header Rank / ID / Name / Nation / Glider / ... / Score) -> results list"""
    hdr = [h.lower() for h in rows[0]]
    idx = {h: i for i, h in reversed(list(enumerate(hdr)))}
    g = lambda c, *names: next((c[idx[n]] for n in names if n in idx and idx[n] < len(c) and c[idx[n]]), None)
    out = []
    for c in rows[1:]:
        if not c or not re.match(r"^\d+$", c[0]):
            continue
        num = lambda v: float(v) if v and re.match(r"^-?[\d.]+$", v) else None
        fin = g(c, "finish", "ess")
        row = dict(rank=int(c[0]), id=g(c, "id", "#") or c[0], name=g(c, "name", "pilot"), nation=g(c, "nation", "nat", "country"),
                   glider=g(c, "glider"), sponsor=g(c, "sponsor"), start=g(c, "start", "ss"), finish=fin, time=g(c, "time"),
                   height_m=num(g(c, "height")), speed_kmh=num(g(c, "speed")), distance_km=num(g(c, "distance", "dist")),
                   score=num(g(c, "score", "total")))
        row["goal"] = bool(fin and re.match(r"\d\d:\d\d", fin))
        out.append(row)
    return out


def fs_stats(src):
    return {k.strip(): v.strip() for k, v in re.findall(r"<td><b>([A-Za-z \-/%]+):</b></td><td[^>]*>([^<]+)</td>", src)}


def gate_from_results(results):
    """Most common start time in the results (FS prints each pilot's gate)."""
    from collections import Counter
    c = Counter(r["start"] for r in results if r.get("start") and re.match(r"\d\d:\d\d", r["start"]))
    return sorted(c, key=lambda k: (-c[k], k))[:1]
