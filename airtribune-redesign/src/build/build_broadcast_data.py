"""Build concepts/broadcast-data.js (all 106 Task 3 tracks with altitude and distance to go) for the 3D broadcast replay.

Run from airtribune-redesign/:  python3 -I src/build/build_broadcast_data.py <unzipped-igc-dir> <cache.pkl>
Same loader and re-optimised distance to go as src/data/srs-task3/analyse_task3.py.
Per pilot, every STEP s from T_FROM: x, y (10 m units), GPS altitude (m) and distance to go (100 m units), delta-encoded.
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "data", "srs-task3"))
from t3lib import T3, RES, CYL, TO                          # noqa: E402
from t3load import load_all                                 # noqa: E402

P = load_all(sys.argv[1], sys.argv[2])
OUT = os.path.join(HERE, "..", "..", "concepts", "broadcast-data.js")
T_FROM, T_TO, STEP = -300, 9000, 4
order = [r["id"] for r in T3["results"] if r["id"] in P]

pilots = []
for p in order:
    f = P[p]; r = RES[p]
    end = min(T_TO, (f["tags"][4] + 90) if len(f["tags"]) == 5 else f["t"][-1])
    t0 = max(T_FROM, math.ceil(f["t"][0] / STEP) * STEP)
    d, last = [], [0, 0, 0, 0]
    for t in range(int(t0), int(end), STEP):
        i = int(t - f["t"][0])
        if i >= len(f["t"]):
            break
        g = f["dtg"][i]
        v = [round(f["x"][i] * 100), round(f["y"][i] * 100), int(f["alt"][i]), -1 if np.isnan(g) else round(float(g) * 10)]
        d += [a - b for a, b in zip(v, last)]; last = v
    up = [w for w in r["name"].split() if w.isupper() and len(w) > 1]
    first = " ".join(w for w in r["name"].split() if w not in up)
    pilots.append(dict(id=p, first=first, last=" ".join(up) if up else r["name"].split()[-1].upper(), nat=r["nation"],
                       rank=r["rank"], glider=r.get("glider"), sponsor=r.get("sponsor"), time=r.get("time"),
                       finish=r.get("finish"), goal=bool(r.get("goal")), tags=[round(t) for t in f["tags"]], t0=int(t0), d=d))

tps = [dict(name=c["name"], code=c["code"], lat=c["lat"], lon=c["lon"], elev=c.get("elev"), r=c["radius_km"],
            kind=["SSS", "TP", "TP", "TP", "Goal"][k]) for k, c in enumerate(CYL)]
data = dict(event="SRS Tapalpa 2026", task=3, date=T3["task"]["date"], dist=T3["task"]["distance_km"], gate="12:15:00",
            step=STEP, takeoff=dict(name=TO["name"], lat=TO["lat"], lon=TO["lon"], elev=TO.get("elev")), tps=tps, pilots=pilots)
open(OUT, "w").write("/* Built by src/build/build_broadcast_data.py from the official Task 3 IGC files; do not edit. */\nwindow.BC="
                     + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n")
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB", len(pilots), "pilots")
