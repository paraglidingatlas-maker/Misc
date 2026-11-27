"""Build docs/task3-voiceover/race.json (tracks, task, live order) for the Task 3 voice-over studio.

Run from airtribune-redesign/:  python3 -I src/build/build_voiceover_data.py <unzipped-igc-dir> <cache.pkl>
Uses the same loader and distance-to-go as src/data/srs-task3/analyse_task3.py (1 s IGC, re-optimised route).
"""
import json, math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "data", "srs-task3"))
from t3lib import T3, RES, CX, CR, CYL                      # noqa: E402
from t3load import load_all                                 # noqa: E402

P = load_all(sys.argv[1], sys.argv[2])
OUT = os.path.join(HERE, "..", "..", "docs", "task3-voiceover", "race.json")
T_FROM, T_TO = -300, 6600
order = [r["id"] for r in T3["results"] if r["id"] in P]
goal = [p for p in order if len(P[p]["tags"]) == 5]
top = [r["id"] for r in T3["results"][:20]]


def nice(n):
    parts = n.split()
    return " ".join(w if not w.isupper() else w.title() for w in parts)


def track(f, step, with_alt):
    out = []
    end = min(T_TO, (f["tags"][4] + 120) if len(f["tags"]) == 5 else f["t"][-1])
    t0 = max(T_FROM, math.ceil(f["t"][0] / step) * step)
    for t in range(int(t0), int(end), step):
        i = int(t - f["t"][0])
        if i >= len(f["t"]):
            break
        out += [round(f["x"][i] * 100), round(f["y"][i] * 100)] + ([int(f["alt"][i])] if with_alt else [])
    return int(t0), out


pilots = []
for p in order:
    f = P[p]; r = RES[p]; isTop = p in top
    t0, pts = track(f, 2 if isTop else 10, isTop)
    pilots.append(dict(id=p, name=nice(r["name"]), last=nice(r["name"].split()[-1]) if r["name"].split()[-1].isupper() else r["name"].split()[-1],
                       nat=r["nation"], rank=r["rank"], finish=r.get("finish"), goal=bool(r.get("goal")), top=isTop,
                       tags=[round(t) for t in f["tags"]], t0=t0, step=2 if isTop else 10, pts=pts))
# fix 'last' for multi-word surnames shown in results as upper case
for pl in pilots:
    up = [w for w in RES[pl["id"]]["name"].split() if w.isupper() and len(w) > 1]
    pl["last"] = " ".join(w.title() for w in up) if up else pl["name"].split()[-1]
    fix = lambda s: re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), s)
    pl["last"], pl["name"] = fix(pl["last"]), fix(pl["name"])

# live order every 10 s among goal pilots (re-optimised distance to go); goal finishers by finish time
idx = {p: i for i, p in enumerate(order)}
board = []
for T in range(T_FROM, T_TO, 10):
    rows = []
    for p in goal:
        f = P[p]; i = int(T - f["t"][0])
        if T >= f["tags"][4]:
            rows.append((-1e6 + f["tags"][4], p, -1)); continue
        if 0 <= i < len(f["t"]) and not np.isnan(f["dtg"][i]):
            rows.append((f["dtg"][i], p, round(float(f["dtg"][i]) * 10)))
    rows.sort()
    board.append([[idx[p], d] for _, p, d in rows[:6]])

# optimised route from take-off through all cylinders (for drawing)
def route_points():
    pts = [np.array(c, float) for c in CX]
    A0 = np.array([0.0, 0.0])
    ang = np.radians(np.arange(0, 360, 0.5))
    for _ in range(30):
        for k in range(len(CX)):
            A = A0 if k == 0 else pts[k - 1]
            B = pts[k + 1] if k + 1 < len(CX) else None
            px = CX[k][0] + CR[k] * np.cos(ang); py = CX[k][1] + CR[k] * np.sin(ang)
            cost = np.hypot(px - A[0], py - A[1]) + (np.hypot(px - B[0], py - B[1]) if B is not None else 0)
            j = int(np.argmin(cost)); pts[k] = np.array([px[j], py[j]])
    return [[0, 0]] + [[round(p[0], 3), round(p[1], 3)] for p in pts]

tps = [dict(name=c["name"], code=c["code"], x=round(float(CX[k][0]), 3), y=round(float(CX[k][1]), 3), r=c["radius_km"],
            kind=["SSS", "TP", "TP", "TP", "Goal"][k]) for k, c in enumerate(CYL)]
data = dict(bounds=dict(x0=-9.0, x1=27.0, y0=-13.0, y1=21.0), gate="12:15:00", t_from=T_FROM, t_to=T_TO,
            takeoff=dict(name=T3["task"]["turnpoints"][0]["name"], x=0, y=0), tps=tps, route=route_points(),
            board=board, pilots=pilots)
json.dump(data, open(OUT, "w"), separators=(",", ":"), ensure_ascii=False)
print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB", len(pilots), "pilots")
