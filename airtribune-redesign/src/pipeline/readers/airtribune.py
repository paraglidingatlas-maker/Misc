"""Airtribune reader.

Accepted links:  https://airtribune.com/<comp>/results/task<ID>/day/overall   (the task's results page)
                 https://airtribune.com/<comp>/  with --task N                (Nth task of the comp)

Uses only public pages and files (robots.txt disallows /api/, which is not touched), cached, one request a second:
  /<comp>/                 event name, place, dates (og: tags), time offset ("timeoffset" in the page data)
  /<comp>/results          task list (task ids in order), IGC archive per task, SeeYou .cup waypoint file
  /<comp>/results/task<ID>/day/overall   FS results export: task table, results, statistics
  waypoints .cup and the task's IGC zip (DigitalOcean Spaces, linked from the results page)
"""
import datetime as dt, re
from .common import get, rows_of, block, clean, parse_cup, fs_task_table, fs_results_table, fs_stats, gate_from_results

BASE = "https://airtribune.com"


def read(link, opts):
    m = re.match(r"https?://(?:www\.)?airtribune\.com/([^/]+)/?(?:results/task(\d+))?", link)
    if not m or m.group(1) in ("play", "api"):
        raise SystemExit("Airtribune link must look like airtribune.com/<comp>/results/task<ID>/day/overall")
    comp, task_id = m.group(1), m.group(2)

    ev = get(f"{BASE}/{comp}/")
    og = dict(re.findall(r'og:(\w+)" content="([^"]*)"', ev))
    off = re.search(r'"timeoffset": (-?\d+)', ev)
    desc = clean(og.get("description", ""))                     # "07 - 14 Nov, 2026 | Tapalpa, Mexico"
    dates, _, where = desc.partition("|")
    place, _, country = where.strip().rpartition(",")

    idx = get(f"{BASE}/{comp}/results")
    ids = list(dict.fromkeys(re.findall(rf"/{re.escape(comp)}/results/task(\d+)/", idx)))
    if not task_id:
        n = int(opts.get("task") or 0)
        if not 1 <= n <= len(ids):
            raise SystemExit(f"{comp} has {len(ids)} tasks: give --task 1..{len(ids)}")
        task_id = ids[n - 1]
    no = ids.index(task_id) + 1 if task_id in ids else None
    zips = re.findall(r'https://[^"\s]+/task/archive/[^"\s]*/' + task_id + r'/[^"\s]+\.zip', idx + ev)
    cup = re.search(r'https://[^"\s<]+\.SeeYou\.cup', idx + ev)

    page = get(f"{BASE}/{comp}/results/task{task_id}/day/overall")
    title = clean(re.search(r"<h3>(.*?)</h3>", page, re.S).group(1))
    h1 = re.search(r"<h1>(.*?)</h1>", page, re.S)
    rows = rows_of(page)
    task_rows, res_rows = block(rows, "order"), block(rows, "rank")
    tps = fs_task_table(task_rows)
    results = fs_results_table(res_rows)
    stats = fs_stats(page)

    wps = parse_cup(get(cup.group(0))) if cup else {}
    for t in tps:
        w = wps.get(t["code"])
        if not w:
            raise SystemExit(f"waypoint {t['code']} not in the .cup file")
        t.update(lat=w["lat"], lon=w["lon"], elev_m=w["elev_m"])

    # date: "Tue 10-Nov-26" in the title, else --date
    dm = re.search(r"(\d{1,2})-([A-Z][a-z]{2})-(\d{2})", title)
    date = opts.get("date") or (dt.datetime.strptime(dm.group(0), "%d-%b-%y").date().isoformat() if dm else None)
    if not date:
        raise SystemExit("task date not found: give --date YYYY-MM-DD")
    gates = opts.get("gates") or gate_from_results(results)

    igc = {}
    if zips and not opts.get("no_tracks"):
        from taskpkg import unzip_igc
        igc = unzip_igc(get(zips[0], binary=True, min_gap=2.0))
    ival = lambda k: int(stats[k]) if re.match(r"^\d+$", stats.get(k, "")) else None
    return dict(
        comp=comp, task_id=f"t{no}" if no else f"task{task_id}",
        source=dict(kind="airtribune", url=f"{BASE}/{comp}/results/task{task_id}/day/overall",
                    files=[u for u in [cup.group(0) if cup else None] + zips[:1] if u],
                    replay=f"{BASE}/play/{task_id}/2d"),
        event=dict(name=clean(og.get("title")), series=(clean(h1.group(1)) if h1 else None), place=place.strip() or None, country=country.strip() or None,
                   dates=dates.strip(), url=f"{BASE}/{comp}/"),
        task=dict(no=no, title=title, date=date, utc_offset_s=int(off.group(1)) if off else int(opts.get("utc_offset_s") or 0),
                  type="race", distance_km=tps[-1].get("dist_km"), gates=gates, deadline=opts.get("deadline"),
                  turnpoints=tps),
        scoring=dict(stats, pilots=ival("Total Pilots"), goal=ival("Pilots in Goal")),
        results=results,
        igc=igc,
    )
