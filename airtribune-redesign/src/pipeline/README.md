# Task pipeline: one link in, one task package out

```
cd airtribune-redesign
python3 -I src/pipeline/new_task.py https://airtribune.com/srs-2026-6/results/task6991/day/overall --short "Las Gemelas La Cueva=Las Gemelas" --relief
```

Writes `events/tasks/<comp>/<task>/` and adds the task to `events/tasks/index.json` (listed on `events/tasks/`).
Pages open a package with `?task=<comp>/<task>`: `events/live.html`, `concepts/flythrough.html`
(default `srs-2026-6/t3`). Both pages show every pilot with a tracklog, goal and landed out; `&n=20` keeps the first 20 in
results order. Downloads are cached in `$TASK_CACHE` (default `/tmp/task-cache`); rerunning is fast.

## Readers (picked by the link's domain, `readers/__init__.py`)

| Source | Module | Input | Status |
|---|---|---|---|
| Airtribune | `readers/airtribune.py` | task results page (or comp page + `--task N`) | done |
| Files fallback | `readers/files.py` | `--files` task (.xctsk / .cup / .fsdb) + tracks (zip / folder / .igc) [+ results .csv / FS .html] | done (tested on Task 3: goal times within 1 s, distances within 0.15 km) |
| FS `.fsdb` | `readers/fsdb.py` | `.fsdb` link or file + `--files` tracks, `--task N` | done (tested on a real FS 3.5 file, Soca Open 2019; no tracks there) |
| AirScore | `readers/airscore.py` | airscore.cc task link | blocked: on 27 Nov 2026 airscore.cc lists one comp with no task set, so its result data routes cannot be seen; use the files fallback |
| PWCA / Livetrack24 / Flymaster | `readers/*.py` | event / task link | planned |

Files fallback without a results file: date from the IGC headers, time zone from Open-Meteo (`timezone=auto`),
results worked out from the tracklogs (goal time, then distance on the optimised route; marked `estimated`).

A reader returns a RAW TASK (documented at the top of `taskpkg.py`); everything after that is shared:
tags from the tracklogs, track encoding, area box, wind, KK7, relief, package writer.

## Package format (`airtribune-task/1`)

`data.json`
- `id` `"<comp>/<task>"`, `built`, `source {kind, url, files, replay}`
- `event {name, short, series, place, country, dates, url}`
- `task {no, title, date, utc_offset_s, type, distance_km, gates ["HH:MM:SS"], deadline,
  turnpoints [{code, name, short, lat, lon, elev_m, radius_m, role TO|SSS|TP|ESS|GOAL, check enter|exit, ess}]}`
- `scoring {pilots, goal, …free-form FS statistics}`
- `results [{rank, id, name, nation, glider, sponsor, start, finish, time, height_m, speed_kmh, distance_km, score, goal}]`
- `wind {drift (estimate from the tracks), aloft {src, lvl, h [[hour, km/h, from°]]} (take-off, caption),
  grid {src, lvl, lat[5], lon[5], h0, h[hour][lat][lon] = [u, v] km/h} (animation), query, credit}`
- `sky {box {s, n, w, e}, z, skyways, thermals, credit}` (KK7 images on a plain lat/lon grid)
- `relief {file, x0, x1, y0, y1 (km, local frame), res_m, credit}` (optional)
- `box` area box; `tracks {file, count, step_s, units}`

`tracks.json`: `{pilots: [{id, tags [s from first gate], goal, d}]}`, in results order. `d` is a flat int list
`[t, x, y, alt, dt, dx, dy, dalt, …]`: t s from the first gate, x/y metres east/north of take-off
(x = (lon − lon0)·111.32·cos(lat0) km, y = (lat − lat0)·110.574 km), GPS altitude m; first group absolute, then deltas.
One fix every 5 s from 20 min before the gate to 2 min after goal or landing, plus the exact tag fixes.
