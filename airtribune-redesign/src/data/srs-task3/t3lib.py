"""Shared helpers for the Task 3 key-moments analysis (SRS Tapalpa 2026, Task 3, 10 Nov 2026).

Reads the official 1 s IGC files (archive listed in SOURCES.md) and task3.json (task, results).
Local frame: km, x east, y north, origin = take-off D01. Time t = seconds from the 12:15:00 start gate (local, UTC-6).

IGC extension note: the archive's I-record names columns 41-42 WSP and 43-45 WDI, but the values match the
ground speed (km/h) and ground track (deg) computed from the fixes, so they are read as such. Columns 46-49 (GND)
are the ground elevation under the pilot (m), used for heights above ground.
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = 12 * 3600 + 15 * 60
UTC_OFFSET = -6 * 3600

T3 = json.load(open(os.path.join(HERE, "task3.json"), encoding="utf-8"))
TPS = T3["task"]["turnpoints"]
TO = TPS[0]
LAT0 = math.radians(TO["lat"])
RES = {r["id"]: r for r in T3["results"]}


def km(lat, lon):
    return (lon - TO["lon"]) * 111.32 * np.cos(LAT0), (lat - TO["lat"]) * 110.574


CYL = TPS[1:]                                   # SSS, TP2, TP3, TP4, goal
CX = np.array([km(c["lat"], c["lon"]) for c in CYL])
CR = np.array([c["radius_km"] for c in CYL])
NAMES = ["Start (El Asoleado)", "TP2 Las Gemelas", "TP3 Tamazula", "TP4 Amacueca", "Goal"]


def hms(t):
    """seconds from gate -> 'hh:mm:ss' local"""
    s = int(round(GATE + t))
    return "%02d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60)


def read_igc(path):
    t, lat, lon, alt, gs, trk, gnd = [], [], [], [], [], [], []
    for line in open(path, encoding="ascii", errors="replace"):
        if not line.startswith("B") or len(line) < 49:
            continue
        s = int(line[1:3]) * 3600 + int(line[3:5]) * 60 + int(line[5:7])
        la = int(line[7:9]) + int(line[9:14]) / 60000
        lo = int(line[15:18]) + int(line[18:23]) / 60000
        t.append((s + UTC_OFFSET) % 86400 - GATE)
        lat.append(-la if line[14] == "S" else la)
        lon.append(-lo if line[23] == "W" else lo)
        pa, ga = int(line[25:30]), int(line[30:35])
        alt.append(ga or pa)
        gs.append(int(line[40:42]) if line[40:42].isdigit() else 0)
        trk.append(int(line[42:45]) if line[42:45].isdigit() else 0)
        gnd.append(int(line[45:49]) if line[45:49].isdigit() else 0)
    t = np.array(t, float)
    o = np.argsort(t, kind="stable"); t = t[o]
    keep = np.concatenate([[True], np.diff(t) > 0])
    lat, lon = np.array(lat)[o][keep], np.array(lon)[o][keep]
    x, y = km(lat, lon)
    return dict(t=t[keep], x=x, y=y, alt=np.array(alt, float)[o][keep], gs=np.array(gs, float)[o][keep],
                trk=np.array(trk, float)[o][keep], gnd=np.array(gnd, float)[o][keep])


def resample(f, step=1.0):
    """Uniform 1 s grid (linear interpolation) so windows are in seconds."""
    tg = np.arange(math.ceil(f["t"][0]), math.floor(f["t"][-1]) + 1, step)
    out = dict(t=tg)
    for k in ("x", "y", "alt", "gnd", "gs"):
        out[k] = np.interp(tg, f["t"], f[k])
    return out


def tags(f):
    """SSS exit after the gate, then entry of each TP and goal (same rule as extract_task3.py)."""
    out, k, inside = [], 0, False
    d = lambda i, k: math.hypot(f["x"][i] - CX[k][0], f["y"][i] - CX[k][1])
    for i in range(len(f["t"])):
        if k >= len(CYL):
            break
        if k == 0:
            if f["t"][i] < 0:
                continue
            if d(i, 0) < CR[0]:
                inside = True
            elif inside:
                out.append(f["t"][i]); k += 1
        elif d(i, k) <= CR[k]:
            out.append(f["t"][i]); k += 1
    return out


def _best_on_circle(A, B, c, r, ang):
    """For each row, the point on circle (c, r) minimising |A-p| + |p-B| (B may be None), sampled at angles ang."""
    px = c[0] + r * np.cos(ang)[None, :]
    py = c[1] + r * np.sin(ang)[None, :]
    cost = np.hypot(px - A[:, :1], py - A[:, 1:2])
    if B is not None:
        cost = cost + np.hypot(px - B[:, :1], py - B[:, 1:2])
    j = np.argmin(cost, axis=1)
    return j


def dist_to_go(P, k0, iters=8):
    """Optimised remaining distance (km) from positions P (N x 2) through cylinders k0..goal.
    Returns (dist, first touch point N x 2)."""
    P = np.asarray(P, float)
    N = len(P)
    ks = list(range(k0, len(CYL)))
    pts = [np.repeat(CX[k][None, :], N, 0) for k in ks]
    coarse = np.radians(np.arange(0, 360, 3.0))
    for it in range(iters):
        for i, k in enumerate(ks):
            A = P if i == 0 else pts[i - 1]
            B = pts[i + 1] if i + 1 < len(ks) else None
            if it == 0 or True:
                j = _best_on_circle(A, B, CX[k], CR[k], coarse)
                base = coarse[j]
            # refine +-3 deg per row
            fine = base[:, None] + np.radians(np.linspace(-3, 3, 25))[None, :]
            px = CX[k][0] + CR[k] * np.cos(fine); py = CX[k][1] + CR[k] * np.sin(fine)
            cost = np.hypot(px - A[:, :1], py - A[:, 1:2])
            if B is not None:
                cost = cost + np.hypot(px - B[:, :1], py - B[:, 1:2])
            jj = np.argmin(cost, axis=1)
            pts[i] = np.stack([px[np.arange(N), jj], py[np.arange(N), jj]], 1)
    d = np.hypot(*(pts[0] - P).T)
    for i in range(1, len(pts)):
        d = d + np.hypot(*(pts[i] - pts[i - 1]).T)
    return d, pts[0]
