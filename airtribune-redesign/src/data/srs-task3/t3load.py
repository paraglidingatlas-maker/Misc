"""Load every pilot of Task 3 on a 1 s grid with tags, distance to go, circling flags and thermals.
Caches to t3cache.npz-like pickle in the scratch dir given by T3_CACHE (default: next to the IGC dir)."""
import os, pickle, sys, math
import numpy as np
from t3lib import *

def unwrap_heading(x, y):
    dx, dy = np.gradient(x), np.gradient(y)
    h = np.unwrap(np.arctan2(dx, dy))
    return np.degrees(h)

def segments(mask):
    m = np.concatenate([[False], mask, [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))   # [a, b)

def fit_wind(gs, trk):
    """gs = V + W cos(trk - wdir_to) over a full circle -> wind speed (km/h) and direction FROM (deg)."""
    th = np.radians(trk)
    A = np.stack([np.ones_like(th), np.cos(th), np.sin(th)], 1)
    c, *_ = np.linalg.lstsq(A, gs, rcond=None)
    W = math.hypot(c[1], c[2]); to = math.degrees(math.atan2(c[2], c[1])) % 360
    return c[0], W, (to + 180) % 360

def load_pilot(path):
    raw = read_igc(path)
    f = resample(raw)
    rf = dict(x=f["x"], y=f["y"], t=f["t"])
    tg = tags(rf)
    # interpolate track too (needs unwrap)
    trk = np.degrees(np.unwrap(np.radians(raw["trk"])))
    f["trk"] = np.interp(f["t"], raw["t"], trk) % 360
    f["tags"] = tg
    # flight window: launch .. goal (or last fix)
    end = tg[-1] if len(tg) == len(CYL) else f["t"][-1]
    # heading from positions, 1 s
    h = unwrap_heading(f["x"], f["y"])
    f["head"] = h
    W = 30
    turn = np.full(len(h), 0.0)
    turn[W//2:-W//2] = h[W:] - h[:-W]
    circ = np.abs(turn) >= 270
    # merge small gaps, drop short
    segs = segments(circ)
    merged = []
    for a, b in segs:
        a, b = max(0, a - W//2), min(len(h), b + W//2)
        if merged and a - merged[-1][1] <= 20:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    th = []
    for a, b in merged:
        if b - a < 40:
            continue
        dt = f["t"][b-1] - f["t"][a]
        dz = f["alt"][b-1] - f["alt"][a]
        sl = slice(a, b)
        try:
            V, Wk, wfrom = fit_wind(f["gs"][sl], f["trk"][sl])
        except Exception:
            V = Wk = wfrom = float("nan")
        # time to centre: first time the 20 s climb reaches the thermal's mean climb (if positive)
        mean = dz / dt if dt else 0
        v20 = (f["alt"][a+20:b] - f["alt"][a:b-20]) / 20 if b - a > 25 else np.array([])
        tc = next((i for i, v in enumerate(v20) if v >= mean), None) if mean > 0 else None
        # best 60 s climb inside the thermal
        v60 = (f["alt"][a+60:b] - f["alt"][a:b-60]) / 60 if b - a > 65 else np.array([mean])
        th.append(dict(a=int(a), b=int(b), t0=float(f["t"][a]), t1=float(f["t"][b-1]), dur=float(dt),
                       z0=float(f["alt"][a]), z1=float(f["alt"][b-1]), climb=float(mean),
                       best60=float(v60.max()) if len(v60) else float(mean),
                       x=float(f["x"][sl].mean()), y=float(f["y"][sl].mean()),
                       agl0=float(f["alt"][a] - f["gnd"][a]), agl1=float(f["alt"][b-1] - f["gnd"][b-1]),
                       t_centre=tc, wind_kmh=Wk, wind_from=wfrom, airspeed_circ=V,
                       turn_dir="L" if np.sign(h[b-1]-h[a]) < 0 else "R"))
    f["thermals"] = th
    f["circling"] = np.zeros(len(h), bool)
    for t_ in th:
        f["circling"][t_["a"]:t_["b"]] = True
    # distance to go every 5 s (target = next untagged cylinder; before SSS: via SSS)
    tgo = np.full(len(f["t"]), np.nan)
    idx = np.arange(0, len(f["t"]), 5)
    tt = f["t"][idx]
    tagarr = np.array(tg + [np.inf] * (len(CYL) - len(tg)))
    k = np.searchsorted(tagarr, tt, side="right")       # number of tags passed
    for kk in range(len(CYL)):
        sel = (k == kk) & (tt >= -60) & (tt <= end)
        if sel.any():
            P = np.stack([f["x"][idx[sel]], f["y"][idx[sel]]], 1)
            d, _ = dist_to_go(P, kk)
            tgo[idx[sel]] = d
    good = ~np.isnan(tgo)
    if good.sum() > 2:
        tgo = np.interp(np.arange(len(tgo)), np.where(good)[0], tgo[good])
        tgo[(f["t"] < -60) | (f["t"] > end)] = np.nan
    f["dtg"] = tgo
    f["end"] = end
    return f

def load_all(igc_dir, cache):
    if os.path.exists(cache):
        return pickle.load(open(cache, "rb"))
    P = {}
    for r in T3["results"]:
        p = os.path.join(igc_dir, r["id"] + ".igc")
        if os.path.exists(p):
            P[r["id"]] = load_pilot(p)
            print("loaded", r["rank"], r["name"], len(P[r["id"]]["thermals"]), "thermals", file=sys.stderr)
    pickle.dump(P, open(cache, "wb"))
    return P
