"""Fetch and extract British Winter Open data from Airtribune.
Run from anywhere: python3 extract_bwo.py <cache-dir>   -> writes bwo.json next to this script.
Sources: airtribune.com/<edition>/ (event page) and /<edition>/results/task<last>/comp/<class> (final standings)."""
import json, re, html, subprocess, sys, os
CACHE = sys.argv[1]; os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bwo.json")
EDITIONS = [("2020", "boc2020", "1st"), ("2022", "bwo2022", "3rd"), ("2023", "bwo2023", "4th"), ("2024", "v2_bwo2024", "5th"),
            ("2025", "bwo2025", "6th"), ("2026", "bwo2026", "7th")]
CLASSES = ["overall", "female", "sports", "british-overall"]
dec = json.JSONDecoder()

def fetch(path):
    f = os.path.join(CACHE, path.strip("/").replace("/", "_") + ".html")
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        subprocess.run(["curl", "-sL", "-o", f, "https://airtribune.com" + path], check=True)
    return open(f, encoding="utf-8").read()

def atdata(s, key):
    i = s.find(f"window.ATDATA.{key} = ")
    return dec.raw_decode(s[i + len(f"window.ATDATA.{key} = "):])[0] if i >= 0 else None

def cells(tr):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]

def standings(s):
    tasks, rows, hdr = [], [], None
    for tr in re.findall(r"(?is)<tr[^>]*>.*?</tr>", s):
        c = cells(tr)
        if len(c) >= 3 and re.match(r"^[\d.]+ km$", c[2]) and re.search(r"\d", c[1]) and c[0] not in ("Task", "#"):
            tasks.append(dict(task=c[0], date=c[1], km=float(c[2].split()[0])))
        elif "Name" in c and ("Nat" in c or "Nation" in c):
            hdr = {k: c.index(k) for k in ("Name", "Nat", "Nation", "Glider") if k in c}
        elif hdr and c and c[0].isdigit() and len(c) > hdr["Name"] + 2:
            nums = [x for x in c if re.match(r"^\d+(\.\d+)?$", x)]
            rows.append(dict(rank=int(c[0]), name=c[hdr["Name"]], nation=c[hdr.get("Nat", hdr.get("Nation"))],
                             glider=c[hdr["Glider"]] if "Glider" in hdr else "", score=int(float(nums[-1]))))
    seen = set(); tasks = [t for t in tasks if not (t["task"] in seen or seen.add(t["task"]))]
    return tasks, rows

data = {"editions": []}
for year, slug, nth in EDITIONS:
    ev = fetch(f"/{slug}/")
    meta = atdata(ev, "meta")["info"]
    res = fetch(f"/{slug}/results")
    ids = sorted(set(re.findall(rf"/{slug}/results/task(\d+)/comp/", res)), key=int)
    last = ids[-1]
    links = set(re.findall(rf"/{slug}/results/task{last}/comp/([a-z-]+)", res))
    ed = dict(year=year, slug=slug, edition=nth, title=meta["title"], when_where=meta["description"], classes={})
    ed["replays"] = sorted({int(x) for x in re.findall(r'href="/play/(\d+)/2d"', ev + res)})
    ed["task_ids"] = [int(x) for x in sorted(set(re.findall(rf"/{slug}/results/task(\d+)/", res)), key=int)]
    for cl in CLASSES:
        name = next((l for l in (cl, cl + "-class") if l in links), None)
        if not name: continue
        tasks, rows = standings(fetch(f"/{slug}/results/task{last}/comp/{name}"))
        if cl == "overall": ed["tasks"] = tasks; ed["pilots"] = len(rows); ed["nations"] = len({r["nation"] for r in rows})
        ed["classes"][cl] = rows[:3]
    data["editions"].append(ed)
    print(year, slug, ed["when_where"], len(ed.get("tasks", [])), "tasks", ed.get("pilots"), "pilots", {k: [r["name"] for r in v] for k, v in ed["classes"].items()})

# 2027 edition: registrations, HQ and photos from the event page
ev = fetch("/bwo2027/")
p = atdata(ev, "pilots")
pil = p["pilots"]
from collections import Counter
data["y2027"] = dict(
    confirmed=p["confirmed"], registered=len(pil), nations=len({x["country"]["code"] for x in pil}),
    by_nation=Counter(x["country"]["ioc_code"] for x in pil).most_common(12),
    by_status=Counter(x.get("status") for x in pil).most_common(),
    women=sum(1 for x in pil if x.get("gender") == "F"),
    gliders=Counter((x.get("glider_manufacturer") or x.get("glider", {}).get("manufacturer") if isinstance(x.get("glider"), dict) else x.get("glider_manufacturer") or "") for x in pil).most_common(10),
    hq=[float(x) for x in re.search(r'"lat": ([\d.]+), "lon": ([\d.]+)', ev).groups()], keys=sorted(pil[0].keys()) if pil else [])
json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
print(json.dumps(data["y2027"], ensure_ascii=False)[:1500])
