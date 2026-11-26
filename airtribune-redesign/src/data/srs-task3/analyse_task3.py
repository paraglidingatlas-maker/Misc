"""Key-moments analysis of SRS Tapalpa 2026, Task 3 (10 Nov 2026), from the official 1 s IGC files.

Usage (from airtribune-redesign/src/data/srs-task3/):
    python3 -I analyse_task3.py <unzipped-igc-dir> [cache.pkl]
The IGC zip is listed in SOURCES.md (106 files named by pilot id). Writes analysis/key_moments.json and
analysis/tables.md. Every number in docs/task3-key-moments.md comes from those two files.

Method (all inferred from GPS tracks; there is no airspeed, speed-bar or measured wind data):
- 1 s grid; "circling" = heading turns >= 270 deg within 30 s; thermals = circling spells >= 40 s (gaps <= 20 s merged).
- Distance to go = optimised remaining route from the pilot's own position through the cylinders still to tag
  (re-optimised every 5 s), so line choices are scored fairly. Flat-earth km: the full task comes out 58.56 km
  against the official 58.7 km (WGS84), so distances are ~0.25 % short.
- Time gaps: the clock time each pilot first reached each 1 km of distance to go, minus the fastest pilot there.
- Wind: per thermal, ground speed fitted against ground track (gs = V + W cos(track - dir)) over the circles.
- Goal-pilot field = 87 pilots with a complete set of tags (88 made goal; one IGC lacks the SSS crossing).
"""
import json, os, sys, math, pickle
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t3lib import T3, RES, CX, CR, CYL, NAMES, hms           # noqa: E402
from t3load import load_all                                  # noqa: E402

GOAL_ELEV = TP_GOAL_ELEV = CYL[-1]["elev_m"]                 # 1346 m, LZ Amacueca
igc_dir = sys.argv[1]
cache = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(igc_dir.rstrip("/")), "t3cache.pkl")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis")
os.makedirs(OUT, exist_ok=True)

P = load_all(igc_dir, cache)
goal = [r["id"] for r in T3["results"] if r.get("goal") and r["id"] in P and len(P[r["id"]]["tags"]) == 5]
top = goal[:20]
nm = lambda p: RES[p]["name"]
short = lambda p: RES[p]["name"].split()[-1].title()
r1 = lambda v, n=1: None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), n)


def idx(f, t):
    return int(round(t - f["t"][0]))


# ---------- 1. start ----------
start = []
for p in top:
    f = P[p]; i = idx(f, 0); j = idx(f, f["tags"][0])
    start.append(dict(id=p, name=nm(p), edge_m_at_gate=round((CR[0] - math.hypot(f["x"][i] - CX[0][0], f["y"][i] - CX[0][1])) * 1000),
                      alt_at_gate=int(f["alt"][i]), crossed=hms(f["tags"][0]), crossed_s=r1(f["tags"][0], 0), alt_cross=int(f["alt"][j])))
st_all = np.array([P[p]["tags"][0] for p in goal])

# ---------- 2. legs ----------
LEGS = ["Start - TP2", "TP2 - TP3", "TP3 - TP4", "TP4 - Goal"]


def legstats(f, a, b):
    i0, i1 = idx(f, a), idx(f, b)
    c = f["circling"][i0:i1]
    dz = np.diff(f["alt"][i0:i1]); path = np.hypot(np.diff(f["x"][i0:i1]), np.diff(f["y"][i0:i1]))
    cc = c[:-1]
    tc = int(cc.sum()); g = ~cc
    gl_drop = -dz[g].sum()
    return dict(time_s=int(b - a), circling_s=tc, circling_pct=round(100 * tc / max(1, b - a)),
                climb_ms=r1(dz[cc].sum() / tc, 2) if tc else None,
                glide_kmh=r1(path[g].sum() / g.sum() * 3600) if g.sum() else None,
                glide_ld=r1(path[g].sum() * 1000 / gl_drop) if gl_drop > 50 else None,
                path_km=r1(path.sum(), 1), thermals=sum(1 for t in f["thermals"] if a <= t["t0"] < b))


legs = {p: [legstats(P[p], P[p]["tags"][k], P[p]["tags"][k + 1]) for k in range(4)] for p in goal}
leg_summary = []
for k in range(4):
    T = np.array([legs[p][k]["time_s"] for p in goal])
    best = goal[int(np.argmin(T))]
    leg_summary.append(dict(leg=LEGS[k], fastest=nm(best), fastest_s=int(T.min()), median_s=int(np.median(T)),
                            top20_median_s=int(np.median([legs[p][k]["time_s"] for p in top]))))

# ---------- 3. gap to the fastest at each km to go ----------
MS = np.arange(57, 0, -1.0)


def t_at(f, m):
    i0 = idx(f, f["tags"][0]); d = f["dtg"][i0:]
    ok = np.where(d <= m)[0]
    return float(f["t"][i0 + ok[0]]) if len(ok) else float("nan")


TM = {p: np.array([t_at(P[p], m) for m in MS] + [P[p]["tags"][4]]) for p in goal}
BEST = np.nanmin(np.array([TM[p] for p in goal]), 0)
GAP = {p: TM[p] - BEST for p in goal}
leader_at = [short(min(goal, key=lambda p: TM[p][i])) for i in range(len(MS) + 1)]

# ---------- 4. race order by clock time (re-optimised distance to go) ----------
def order_at(t):
    rows = []
    for p in goal:
        f = P[p]; i = idx(f, t)
        if t >= f["tags"][4]:
            rows.append((-1e9 + f["tags"][4], p, 0.0, None)); continue
        if 0 <= i < len(f["t"]) and not np.isnan(f["dtg"][i]):
            rows.append((f["dtg"][i], p, f["dtg"][i], int(f["alt"][i])))
    rows.sort()
    return rows


snapshots = {}
for T in (0, 900, 1679, 2400, 2700, 3000, 3300, 3400, 3700, 4000, 4300, 4600, 5000, 5300, 5600, 5900, 6000, 6100):
    rows = order_at(T)
    snapshots[hms(T)] = [dict(pos=i + 1, name=short(p), dtg_km=r1(d), alt=a) for i, (_, p, d, a) in enumerate(rows[:12])]

leads = []
prev = None
for T in range(0, 6200, 10):
    rows = order_at(T)
    if not rows:
        continue
    p = rows[0][1]
    if p != prev:
        lead = (rows[1][0] - rows[0][0]) if len(rows) > 1 and rows[0][0] > -1e8 else None
        leads.append(dict(time=hms(T), leader=short(p), dtg_km=r1(rows[0][2]), margin_km=r1(lead, 2)))
        prev = p

# ---------- 5. biggest gains / losses per 3 km window (top 20) ----------
moves = []
W = 3
for p in top:
    g = GAP[p]
    for i in range(0, len(MS) - W):
        dg = g[i + W] - g[i]
        if abs(dg) >= 120:
            moves.append(dict(name=nm(p), frm_km=float(MS[i]), to_km=float(MS[i + W]), gap_change_s=int(dg),
                              clock=hms(TM[p][i]) + " - " + hms(TM[p][i + W])))
# keep the strongest non-overlapping window per pilot and direction
moves.sort(key=lambda m: -abs(m["gap_change_s"]))
kept = []
for m in moves:
    if any(k["name"] == m["name"] and (k["gap_change_s"] > 0) == (m["gap_change_s"] > 0)
           and not (m["to_km"] >= k["frm_km"] or m["frm_km"] <= k["to_km"]) for k in kept):
        continue
    kept.append(m)

# ---------- 6. thermals (top 20) and the low points ----------
thermals = {}
for p in top:
    f = P[p]; a, b = f["tags"][0] - 600, f["tags"][4]
    thermals[nm(p)] = [dict(start=hms(t["t0"]), end=hms(t["t1"]), dur_s=int(t["dur"]), alt_in=int(t["z0"]), alt_out=int(t["z1"]),
                            agl_in=int(t["agl0"]), agl_out=int(t["agl1"]), climb_ms=r1(t["climb"], 1), best60_ms=r1(t["best60"], 1),
                            dtg_km=r1(f["dtg"][t["a"]]), x_km=r1(t["x"], 2), y_km=r1(t["y"], 2),
                            wind_kmh=r1(t["wind_kmh"]), wind_from=r1(t["wind_from"], 0))
                        for t in f["thermals"] if a <= t["t0"] < b - 30]
lows = []
for p in top:
    f = P[p]; i0, i1 = idx(f, f["tags"][1]), idx(f, f["tags"][3])   # after TP2: near launch the IGC ground model is too coarse
    agl = f["alt"][i0:i1] - f["gnd"][i0:i1]
    j = int(np.argmin(agl))
    lows.append(dict(name=nm(p), time=hms(f["t"][i0 + j]), agl_m=int(agl[j]), alt=int(f["alt"][i0 + j]), dtg_km=r1(f["dtg"][i0 + j])))
lows.sort(key=lambda r: r["agl_m"])

# ---------- 7. final glide and goal ----------
final = []
for p in top:
    f = P[p]; tg = f["tags"]
    th = [t for t in f["thermals"] if t["t1"] < tg[4] - 30 and t["climb"] > 0.3]
    L = th[-1]; i = L["b"] - 1; ig = idx(f, tg[4])
    d = f["dtg"][i]; h = f["alt"][i] - GOAL_ELEV
    # last thermal used to set up the glide: the last one that ended >= 3 km out
    S = [t for t in th if f["dtg"][t["b"] - 1] >= 3.0][-1]
    si = S["b"] - 1
    final.append(dict(name=nm(p), rank=RES[p]["rank"], finish=RES[p]["finish"],
                      last_climb=dict(start=hms(L["t0"]), left=hms(L["t1"]), dtg_km=r1(d), above_goal_m=int(h),
                                      climb_ms=r1(L["climb"]), dur_s=int(L["dur"])),
                      glide_from=dict(left=hms(S["t1"]), dtg_km=r1(f["dtg"][si]), above_goal_m=int(f["alt"][si] - GOAL_ELEV),
                                      needed_ld=r1(f["dtg"][si] * 1000 / max(1, f["alt"][si] - GOAL_ELEV)),
                                      climb_ms=r1(S["climb"]), thermal_x=r1(S["x"], 2), thermal_y=r1(S["y"], 2)),
                      arrival_above_goal_m=int(f["alt"][ig] - GOAL_ELEV), official_height_m=RES[p]["height_m"],
                      tp4_to_goal_s=int(tg[4] - tg[3]),
                      circling_after_tp4_s=int(f["circling"][idx(f, tg[3]):ig].sum())))

# ---------- 8. wind from the circles ----------
wind = []
for k, (a, b) in enumerate([(-1200, 0), (0, 1700), (1700, 4300), (4300, 6300)]):
    ws = [(t["wind_kmh"], t["wind_from"]) for p in top for t in P[p]["thermals"]
          if a <= t["t0"] < b and t["dur"] >= 90 and not math.isnan(t["wind_kmh"])]
    if ws:
        vx = np.mean([w * math.sin(math.radians(d)) for w, d in ws]); vy = np.mean([w * math.cos(math.radians(d)) for w, d in ws])
        wind.append(dict(phase=["before start", "leg 1", "leg 2", "legs 3-4"][k], thermals=len(ws),
                         median_speed_kmh=r1(np.median([w for w, _ in ws])),
                         mean_vector_kmh=r1(math.hypot(vx, vy)), from_deg=r1(math.degrees(math.atan2(vx, vy)) % 360, 0)))

out = dict(note=__doc__.strip().split("\n\n")[1], pilots_in_field=len(goal),
           start=dict(top20=start, field_median_cross=hms(np.median(st_all)), crossed_within_60s=int((st_all < 60).sum())),
           legs=dict(summary=leg_summary, top20={nm(p): legs[p] for p in top}),
           gaps=dict(km_to_go=MS.tolist() + [0], leader=leader_at,
                     top20={nm(p): [None if math.isnan(v) else int(v) for v in GAP[p]] for p in top}),
           race_order=snapshots, lead_changes=leads, big_moves=kept[:40], lowest_points=lows,
           thermals=thermals, final_glide=final, wind=wind)
json.dump(out, open(os.path.join(OUT, "key_moments.json"), "w"), indent=1, ensure_ascii=False)

# ---------- tables.md ----------
L = ["# Task 3 analysis tables (generated by analyse_task3.py, do not edit)\n"]
L.append("## Leg times, top 20 (s; circling %; climb m/s; glide km/h)\n")
L.append("| # | Pilot | " + " | ".join(LEGS) + " |\n|---|---|" + "---|" * 4)
for p in top:
    L.append(f"| {RES[p]['rank']} | {nm(p)} | " + " | ".join(
        f"{l['time_s']} ({l['circling_pct']}%, {l['climb_ms']}, {l['glide_kmh']})" for l in legs[p]) + " |")
L.append("\n| Leg | Fastest | s | Top-20 median | Field median |\n|---|---|---|---|---|")
for s in leg_summary:
    L.append(f"| {s['leg']} | {s['fastest']} | {s['fastest_s']} | {s['top20_median_s']} | {s['median_s']} |")
L.append("\n## Gap to the fastest pilot at each 3 km to go (s)\n")
cols = list(range(0, len(MS) + 1, 3))
L.append("| Pilot | " + " | ".join(f"{int(MS[i]) if i < len(MS) else 'goal'}" for i in cols) + " |\n|---|" + "---|" * len(cols))
L.append("| *leader* | " + " | ".join(leader_at[i] for i in cols) + " |")
for p in top:
    L.append(f"| {nm(p)} | " + " | ".join(str(int(GAP[p][i])) for i in cols) + " |")
L.append("\n## Lead changes (re-optimised distance to go, checked every 10 s)\n")
L.append("| Time | Leader | km to go | Margin km |\n|---|---|---|---|")
for l in leads:
    L.append(f"| {l['time']} | {l['leader']} | {l['dtg_km']} | {l['margin_km']} |")
L.append("\n## Final glides\n")
L.append("| # | Pilot | Left last 3 km+ climb | km to go | m above goal | L/D needed | Climb m/s | Arrival m | TP4→goal s | Circling after TP4 s |\n|---|---|---|---|---|---|---|---|---|---|")
for r in final:
    g = r["glide_from"]
    L.append(f"| {r['rank']} | {r['name']} | {g['left']} | {g['dtg_km']} | {g['above_goal_m']} | {g['needed_ld']} | {g['climb_ms']} | {r['arrival_above_goal_m']} | {r['tp4_to_goal_s']} | {r['circling_after_tp4_s']} |")
L.append("\n## Lowest point between TP2 and TP4 (top 20; height above ground from the IGC ground model, approximate)\n")
L.append("| Pilot | Time | m above ground | km to go |\n|---|---|---|---|")
for r in lows[:10]:
    L.append(f"| {r['name']} | {r['time']} | {r['agl_m']} | {r['dtg_km']} |")
L.append("\n## Wind from the circles\n")
L.append("| Phase | Thermals | Median km/h | Mean vector km/h | From ° |\n|---|---|---|---|---|")
for w in wind:
    L.append(f"| {w['phase']} | {w['thermals']} | {w['median_speed_kmh']} | {w['mean_vector_kmh']} | {w['from_deg']} |")
open(os.path.join(OUT, "tables.md"), "w").write("\n".join(L) + "\n")
print("wrote", OUT)
