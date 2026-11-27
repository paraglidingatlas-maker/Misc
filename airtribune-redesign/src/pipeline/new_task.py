"""One link in, one task package out.

  python3 -I src/pipeline/new_task.py <link> [options]          (run from airtribune-redesign/)

<link> is the task's page on any supported site; the reader is picked by its domain:
  airtribune.com     results page of the task (…/<comp>/results/task<ID>/day/overall), or the comp page + --task N
  airscore.cc        task result page
  pwca / livetrack24 / flymaster   see readers/<name>.py
  anything else      not supported: use the files fallback (a local folder or files instead of a link):
      new_task.py --files <task.xctsk|.cup|.fsdb> <tracks.zip|igc-folder> [results.csv|.html] --comp <slug> --task-id t1 ...

Options:
  --task N              task number (when the link is the comp page)
  --date YYYY-MM-DD     task date (when the source does not say)
  --gate HH:MM[,HH:MM]  start gate(s) local (when the source does not say)
  --utc-offset H        local time offset from UTC in hours (when the source does not say)
  --short "Long name=Short"   short turnpoint name for the pages (repeatable)
  --no-wind --no-sky    skip the Open-Meteo wind / KK7 bakes
  --relief              also bake a shaded-relief image (voice-over studio)
  --cache DIR           download cache (default $TASK_CACHE or /tmp/task-cache)

Writes events/tasks/<comp>/<task>/ (data.json, tracks.json, images) and updates events/tasks/index.json.
Open it with events/live.html?task=<comp>/<task> (and the fly-through / broadcast / voice-over the same way).
"""
import argparse, importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import taskpkg                      # noqa: E402
from readers import pick           # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("link", nargs="?")
    ap.add_argument("--files", nargs="+")
    ap.add_argument("--comp"); ap.add_argument("--task-id"); ap.add_argument("--task", type=int)
    ap.add_argument("--date"); ap.add_argument("--gate"); ap.add_argument("--deadline"); ap.add_argument("--utc-offset", type=float)
    ap.add_argument("--event"); ap.add_argument("--place"); ap.add_argument("--country"); ap.add_argument("--series")
    ap.add_argument("--short", action="append", default=[])
    ap.add_argument("--no-wind", action="store_true"); ap.add_argument("--no-sky", action="store_true")
    ap.add_argument("--no-tracks", action="store_true"); ap.add_argument("--relief", action="store_true")
    ap.add_argument("--cache")
    a = ap.parse_args(argv)
    if a.cache:
        os.environ["TASK_CACHE"] = a.cache
    opts = dict(task=a.task, date=a.date, deadline=a.deadline, comp=a.comp, task_id=a.task_id, files=a.files,
                gates=[g if g.count(":") == 2 else g + ":00" for g in a.gate.split(",")] if a.gate else None,
                utc_offset_s=int(a.utc_offset * 3600) if a.utc_offset is not None else None,
                event=dict(name=a.event, place=a.place, country=a.country, series=a.series),
                no_tracks=a.no_tracks, no_wind=a.no_wind, no_sky=a.no_sky, relief=a.relief, cache=a.cache,
                short=dict(s.split("=", 1) for s in a.short))
    if a.files:
        name = "files"
    elif a.link:
        name = pick(a.link)
        if not name:
            raise SystemExit(f"no reader for {a.link}: download the task file and tracks and use --files")
    else:
        ap.error("give a link or --files")
    print(f"reader: {name}")
    raw = importlib.import_module(f"readers.{name}").read(a.link, opts)
    for k, v in opts["event"].items():
        if v:
            raw["event"][k] = v
    if a.comp:
        raw["comp"] = a.comp
    if a.task_id:
        raw["task_id"] = a.task_id
    tk = raw["task"]
    print(f"  {raw['event'].get('name')} · {tk.get('title') or tk.get('no')} · {tk['date']} · "
          f"{len(tk['turnpoints'])} turnpoints · {len(raw.get('results', []))} results · {len(raw.get('igc') or {})} tracklogs")
    out = taskpkg.build(raw, opts)
    print(f"done: events/live.html?task={raw['comp']}/{raw['task_id']}")
    return out


if __name__ == "__main__":
    main()
