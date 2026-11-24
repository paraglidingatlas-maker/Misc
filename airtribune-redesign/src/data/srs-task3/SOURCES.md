# SRS Advance Edition 2026 (Tapalpa, Mexico), Task 3: sources

Round 6 of the Sports-Class Racing Series 2026, 7–14 Nov 2026, Tapalpa, Mexico. It is the latest SRS round held
before 24 Nov 2026: the 2026 rounds on Airtribune are srs-2026-1 (Colombia, Jan), -2 (Italy, May), -3 (Slovenia, Jun),
-4 (France, Jul), -5 (Spain, Aug) and -6 (Tapalpa, Nov). srs-2026-7 does not exist, and the 2027 series starts in March 2027.
Task 3 was flown on Tue 10 Nov 2026 ("Task T6.3 (Sports)", official).

| What | URL | Used for |
|---|---|---|
| Event page | https://airtribune.com/srs-2026-6/ | event name, place, dates; links to the waypoint files |
| Results index | https://airtribune.com/srs-2026-6/results | task list (task ids 6989–6993) and the IGC archive link for each task |
| Task 3 results, overall | https://airtribune.com/srs-2026-6/results/task6991/day/overall | task table (TPs, check, radii, SS/ES, distances), full results of all 106 pilots, task statistics and scoring parameters |
| Waypoints (SeeYou) | https://airtribune.fra1.digitaloceanspaces.com/media/contest/waypoints/2026/11/v2-srs-2026-6.SeeYou.cup | turnpoint lat/lon and elevation |
| Task 3 tracklogs (IGC zip, 106 files named by pilot id) | https://airtribune.fra1.digitaloceanspaces.com/media/task/archive/2026/11/6991/2710_31.zip | real tracks of the top 20 finishers |
| Airtribune 2D replay (not used; reference only) | https://airtribune.com/play/6991/2d | |

## Files

- `task3.json`: everything above, extracted by `extract_task3.py` (results.html, wp.cup and the unzipped IGC folder as inputs).
- `embed_task3.py`: writes a compact copy into `src/live-tracker.html` (between the `/*T3-DATA*/` markers). Run it from
  `airtribune-redesign/`, then `python3 src/build/build_pages.py`.

## Derived or inferred (not stated by the source)

- Start gate 12:15:00 local: every pilot's "Start" in the official results is 12:15:00; the task page does not show the window times.
- Local time = UTC−6 (Airtribune `timeoffset: -21600`, IGC header `HFTZN:-6.0`).
- Tag times (SSS exit after the gate, TP and goal entries) are computed from the IGC fixes; the goal tags match the official
  finish times to within 1 s for all 20 tracked pilots. The page shows the official times.
- "Thermal drift" in the top bar is an estimate: mean drift of the 20 tracks while climbing and circling (about 1.5 km/h from the SE),
  not a measured wind. "Highest pilot" is the highest current altitude among the tracked pilots.
- The optimised route drawn on the map is computed on the page from the official cylinders; the distance shown is the official 58.7 km.

## Not found

- SSS open time / task deadline as published, and the task's wind/weather briefing.
- Tracks of pilots ranked below 20 are in the zip but not used (kept the page light).
- The background relief on the map is stylised, not real terrain.
