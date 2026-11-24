"""Write a compact copy of task3.json into src/live-tracker.html (between the
/*T3-DATA*/ and /*END-T3-DATA*/ markers). Run from airtribune-redesign/:

  python3 -I src/data/srs-task3/embed_task3.py

Track encoding per pilot: flat int list [dt/10 s, dx, dy, dalt, ...] where the first
group is absolute (t/10 from the start gate, x and y in 10 m units, altitude in m)
and the rest are deltas. x east, y north from take-off. The last fix is the goal
tag at its exact second (dt in seconds then, flagged by tg[-1]).
"""
import json, re

SRC = "src/live-tracker.html"
d = json.load(open("src/data/srs-task3/task3.json", encoding="utf-8"))
tk = d["task"]
res = {r["id"]: r for r in d["results"]}

pilots = []
for tr in d["replay"]["tracks"]:
    r = res[tr["id"]]
    goal = tr["tags"][-1]
    pts = [p for p in tr["pts"] if p[0] % 10 == 0 and p[0] < goal] + [next(p for p in tr["pts"] if p[0] == goal)]
    flat, prev = [], None
    for p in pts[:-1]:
        q = [p[0] // 10, round(p[1] * 100), round(p[2] * 100), p[3]]
        flat += q if prev is None else [a - b for a, b in zip(q, prev)]
        prev = q
    g = pts[-1]
    goal_fix = [round(g[1] * 100), round(g[2] * 100), g[3]]
    pilots.append(dict(id=r["id"], n=r["name"], c=r["nation"], gl=r["glider"], rk=r["rank"], tm=r["time"], sc=r["score"],
                       tg=tr["tags"], d=flat, gf=goal_fix))

T3 = dict(
    ev=dict(name=d["event"]["name"], place=d["event"]["place"], country=d["event"]["country"], dates=d["event"]["dates"],
            date="Tue 10 Nov 2026", dist=tk["distance_km"], gate=tk["start_gate_local"][:5]),
    tps=[[t["code"], t["name"], t["check"], t["radius_km"], t["lat"], t["lon"], t["elev_m"], t["ss_es"]] for t in tk["turnpoints"]],
    wind=d["replay"]["wind_estimate"],
    stats=dict(pilots=int(tk["scoring"]["Total Pilots"]), goal=int(tk["scoring"]["Pilots in Goal"])),
    top=[[r["rank"], r["name"], r["nation"], r["score"]] for r in d["results"][:3]],
    pilots=pilots,
)
blob = json.dumps(T3, ensure_ascii=False, separators=(",", ":"))
s = open(SRC, encoding="utf-8").read()
s2, n = re.subn(r"/\*T3-DATA\*/.*?/\*END-T3-DATA\*/", lambda m: "/*T3-DATA*/" + blob + "/*END-T3-DATA*/", s, flags=re.S)
assert n == 1, "markers not found"
open(SRC, "w", encoding="utf-8").write(s2)
print("embedded", len(blob), "bytes,", len(pilots), "pilots")
