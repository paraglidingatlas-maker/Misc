"""Write concepts/flythrough-data.js for the 3D fly-through prototype (concepts/flythrough.html).
Run from airtribune-redesign/:   python3 -I src/build/build_flythrough_data.py

Source: src/data/srs-task3/task3.json (official SRS Tapalpa 2026 Task 3: task, results, top-20 IGC tracks).
Track encoding per pilot: flat int list [dt s, dx, dy, dalt, ...]; first group absolute
(t = seconds from the 12:15 start gate, x/y = metres east/north of take-off D01, alt = GPS m MSL),
the rest deltas. The page converts x/y back to lon/lat with the same equirectangular formula as extract_task3.py.
"""
import json

d = json.load(open("src/data/srs-task3/task3.json", encoding="utf-8"))
tk = d["task"]
res = {r["id"]: r for r in d["results"]}
pilots = []
for tr in d["replay"]["tracks"]:
    r = res[tr["id"]]
    flat, prev = [], None
    for p in tr["pts"]:
        q = [p[0], round(p[1] * 1000), round(p[2] * 1000), p[3]]
        flat += q if prev is None else [a - b for a, b in zip(q, prev)]
        prev = q
    pilots.append(dict(id=r["id"], n=r["name"], c=r["nation"], gl=r["glider"], rk=r["rank"], tm=r["time"],
                       fin=r["finish"], sc=r["score"], tg=tr["tags"], d=flat))
FT = dict(
    ev=dict(name=d["event"]["name"], place=d["event"]["place"], country=d["event"]["country"],
            date="Tue 10 Nov 2026", dist=tk["distance_km"], gate=tk["start_gate_local"][:5], url=d["event"]["airtribune"]),
    tps=[dict(code=t["code"], name=t["name"], check=t["check"], r=t["radius_km"], lat=t["lat"], lon=t["lon"],
              elev=t["elev_m"], ss=t["ss_es"], order=t["order"]) for t in tk["turnpoints"]],
    stats=dict(pilots=int(tk["scoring"]["Total Pilots"]), goal=int(tk["scoring"]["Pilots in Goal"])),
    pilots=pilots,
)
blob = json.dumps(FT, ensure_ascii=False, separators=(",", ":"))
with open("concepts/flythrough-data.js", "w", encoding="utf-8") as f:
    f.write("/* Built by src/build/build_flythrough_data.py from src/data/srs-task3/task3.json; do not edit. */\n")
    f.write("window.FT=" + blob + ";\n")
print("wrote", len(blob), "bytes,", len(pilots), "pilots")
