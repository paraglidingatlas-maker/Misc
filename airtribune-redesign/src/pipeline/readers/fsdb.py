"""FS (CIVL's scoring program) .fsdb reader: competition, task definition, turnpoints, gates and results in one XML file.

  new_task.py https://…/comp.fsdb --task 3 --files tracks.zip        (link to an .fsdb, tracks from a zip/folder)
  new_task.py --files comp.fsdb tracks.zip --task 3                   (all local)

Tracklogs are not inside the .fsdb: each FsParticipant's FsFlightData names its tracklog_filename; give the
tracklogs as a zip or folder and they are matched by file name (then by CIVL ID / pilot name in the IGC header).
"""
import math, os, re, xml.etree.ElementTree as ET
from .common import get


def _hms(iso):            # '2019-05-01T12:40:00+02:00' -> '12:40:00'
    m = re.search(r"T(\d\d:\d\d:\d\d)", iso or "")
    return m.group(1) if m else None


def _offset_s(iso):
    m = re.search(r"([+-])(\d\d):(\d\d)$", iso or "")
    return (1 if m.group(1) == "+" else -1) * (int(m.group(2)) * 3600 + int(m.group(3)) * 60) if m else None


def parse(xml_bytes, task_no=None):
    root = ET.fromstring(xml_bytes)
    comp = root.find(".//FsCompetition")
    tasks = comp.findall("FsTasks/FsTask")
    if not tasks:
        raise SystemExit("no tasks in the .fsdb")
    if task_no is None:
        if len(tasks) > 1:
            raise SystemExit(f"the .fsdb has {len(tasks)} tasks: give --task 1..{len(tasks)}")
        task_no = 1
    t = tasks[int(task_no) - 1]
    td = t.find("FsTaskDefinition")
    ss, es = int(td.get("ss") or 0), int(td.get("es") or 0)
    tps_x = td.findall("FsTurnpoint")
    tps = []
    for k, x in enumerate(tps_x, 1):
        role = "TO" if k == 1 else "SSS" if k == ss else "GOAL" if k == len(tps_x) else "ESS" if k == es else "TP"
        tps.append(dict(code=x.get("id"), name=x.get("id"), lat=float(x.get("lat")), lon=float(x.get("lon")),
                        elev_m=float(x.get("altitude") or 0), radius_m=None if k == 1 else float(x.get("radius") or 400),
                        role=role, check="enter", ess=(k == es)))
    # SSS direction: exit when take-off is inside the start cylinder (FS does not store it)
    if ss:
        s, to = tps[ss - 1], tps[0]
        d = math.hypot((s["lon"] - to["lon"]) * 111.32 * math.cos(math.radians(to["lat"])), (s["lat"] - to["lat"]) * 110.574)
        s["check"] = "exit" if d * 1000 < s["radius_m"] else "enter"
    if td.get("goal", "").upper() == "LINE":
        tps[-1]["goal_line"] = True
    gates_iso = [g.get("open") for g in td.findall("FsStartGate")] or [tps_x[ss - 1].get("open") if ss else None]
    gates = [_hms(g) for g in gates_iso if g]
    off = _offset_s(gates_iso[0] if gates_iso and gates_iso[0] else tps_x[0].get("open"))
    if off is None and comp.get("utc_offset"):
        off = int(float(comp.get("utc_offset")) * 3600)
    date = (gates_iso[0] or tps_x[0].get("open") or "")[:10]
    deadline = _hms(tps_x[-1].get("close"))

    people = {p.get("id"): p for p in comp.findall("FsParticipants/FsParticipant")}
    results, files = [], {}
    for p in t.findall("FsParticipants/FsParticipant"):
        pid = p.get("id"); fd, rs = p.find("FsFlightData"), p.find("FsResult")
        who = people.get(pid)
        if fd is not None and fd.get("tracklog_filename"):
            files[pid] = fd.get("tracklog_filename")
        if rs is None or who is None:
            continue
        fin = _hms(fd.get("finished_ss")) if fd is not None else None
        in_goal = fd is not None and (fd.get("reachedGoal") == "1" or (bool(fin) and es == len(tps_x)))
        results.append(dict(rank=int(rs.get("rank") or 0) or None, id=pid, name=who.get("name"), nation=who.get("nat_code_3166_a3") or None,
                            glider=who.get("glider"), sponsor=who.get("sponsor") or None, civl=who.get("CIVLID"),
                            start=_hms(fd.get("started_ss")) if fd is not None else None, finish=fin,
                            time=rs.get("ss_time") if fin else None, distance_km=float(rs.get("distance") or 0),
                            score=float(rs.get("points") or 0), goal=in_goal))
    results.sort(key=lambda r: (r["rank"] or 10 ** 6))
    sp = t.find("FsTaskScoreParams")
    dist = float(sp.get("task_distance")) if sp is not None and sp.get("task_distance") else None
    state = t.find("FsTaskState")
    raw = dict(
        event=dict(name=comp.get("name"), place=comp.get("location"), country=None,
                   dates=f"{comp.get('from')} – {comp.get('to')}" if comp.get("from") else None, url=None, series=None),
        task=dict(no=int(task_no), title=t.get("name"), date=date, utc_offset_s=off or 0, type="race" if len(gates) else "elapsed",
                  distance_km=round(dist, 1) if dist else None, gates=gates, turnpoints=tps,
                  deadline=(_hms(state.get("stop_time")) if state is not None and state.get("task_state") == "STOPPED" else None) or deadline),
        scoring=dict(pilots=int(sp.get("no_of_pilots_flying")) if sp is not None and sp.get("no_of_pilots_flying") else len(results),
                     goal=int(sp.get("no_of_pilots_reaching_goal")) if sp is not None and sp.get("no_of_pilots_reaching_goal") else None,
                     formula=(t.find("FsScoreFormula") or comp.find("FsScoreFormula")).get("id") if (t.find("FsScoreFormula") is not None or comp.find("FsScoreFormula") is not None) else None),
        results=results)
    return raw, files


def read(link, opts):
    files = list(opts.get("files") or [])
    src = link if link and link.lower().split("?")[0].endswith(".fsdb") else next((f for f in files if f.lower().endswith(".fsdb")), None)
    if not src:
        raise SystemExit("give an .fsdb link or file")
    xml = get(src, binary=True) if "://" in src else open(src, "rb").read()
    raw, tl = parse(xml, opts.get("task"))
    from .files import load_tracks, match_tracks
    igc = load_tracks([f for f in files if f != src])
    raw["igc"] = match_tracks(igc, raw["results"], tl)
    name = re.sub(r"[^a-z0-9]+", "-", (raw["event"]["name"] or "comp").lower()).strip("-")[:40]
    raw.update(comp=opts.get("comp") or name, task_id=f"t{raw['task']['no']}",
               source=dict(kind="fsdb", url=src if "://" in src else None, files=[os.path.basename(src)]))
    return raw
