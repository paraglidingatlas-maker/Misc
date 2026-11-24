import json, base64, io, html, os, sys
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)) + "/findings/"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/review/design-audit.html"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
groups = [("cal", "Calendar"), ("ev", "Event pages"), ("live", "Live tracker")]
order = {"high": 0, "medium": 1, "low": 2}
E = html.escape

def img64(name):
    p = D + name
    if not os.path.exists(p): return ""
    im = Image.open(p).convert("RGB")
    if im.width > 1100: im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
    if im.height > 1400: im = im.crop((0, 0, im.width, 1400))
    b = io.BytesIO(); im.save(b, "JPEG", quality=70, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

sections, counts, total = [], {}, 0
for key, label in groups:
    f = D + key + ".json"
    if not os.path.exists(f): continue
    items = sorted(json.load(open(f)), key=lambda x: order.get(x.get("severity"), 3))
    counts[label] = len(items); total += len(items)
    cards = []
    for it in items:
        sev = it.get("severity", "low")
        src = img64(it.get("img", ""))
        cards.append(f'''<article class="f" id="{E(it["id"])}">
  <label class="pick"><input type="checkbox" id="c-{E(it["id"])}" data-id="{E(it["id"])}"><span>Fix</span></label>
  <div class="txt">
    <div class="meta"><span class="fid">{E(it["id"])}</span><span class="sev {sev}">{sev}</span><span>{E(it.get("area",""))}</span><span>{E(it.get("page",""))}</span><span>effort {E(it.get("effort",""))}</span></div>
    <h3>{E(it["title"])}</h3>
    <p><b>What</b> {E(it.get("what",""))}</p>
    <p><b>Why</b> {E(it.get("why",""))}</p>
    <p><b>Fix</b> {E(it.get("fix",""))}</p>
  </div>
  {f'<figure><img src="{src}" alt="{E(it["title"])}" loading="lazy"><figcaption>{E(str(it.get("width","")))} px</figcaption></figure>' if src else ''}
</article>''')
    sections.append(f'<section><h2>{label} <small>{len(items)}</small></h2>{"".join(cards)}</section>')

summary = " · ".join(f"{k} {v}" for k, v in counts.items())
page = f'''<title>Design Audit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,600;0,800;1,800&family=Inter:wght@400;600&display=swap">
<style>
/* Review sheet: one column of findings, picture beside the words, a sticky tally to copy picks back into chat. Single dark look, matching the concept site. */
:root{{--bg:#051416;--panel:#0A1E21;--ink:#F2F6F6;--ink2:#A9BDBF;--mute:#6E8A8D;--line:rgba(255,255,255,.1);--accent:#FF5F00;--hi:#FF5F00;--med:#E8B23A;--low:#6E8A8D;
--fd:"Archivo",system-ui,sans-serif;--fb:"Inter",system-ui,sans-serif;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:400 15px/1.55 var(--fb)}}
.wrap{{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:40px 120px}}
header h1{{font:800 italic clamp(34px,6vw,60px)/1 var(--fd);text-transform:uppercase;margin:0 0 14px;text-wrap:balance}}
header p{{max-width:68ch;color:var(--ink2);margin:0 0 8px}}
.tally{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;background:var(--bg);border-bottom:1px solid var(--line);padding-block:12px;margin-top:24px}}
.tally b{{font:800 22px var(--fd);font-variant-numeric:tabular-nums}}
.tally .sp{{flex:1}}
button{{font:600 13px var(--fb);border:0;border-radius:6px;padding:10px 16px;cursor:pointer}}
.go{{background:var(--accent);color:#fff}}
.ghost{{background:transparent;color:var(--ink2);border:1px solid var(--line)}}
#out{{width:100%;margin-top:8px;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:10px;font:13px ui-monospace,monospace}}
section h2{{font:800 italic 28px var(--fd);text-transform:uppercase;margin:56px 0 4px}}
section h2 small{{font:600 14px var(--fb);color:var(--mute);font-style:normal;margin-left:8px}}
.f{{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(0,1.05fr);gap:18px 24px;padding:26px 0;border-top:1px solid var(--line);align-items:start}}
.f.on .pick span{{color:var(--accent)}}
.pick{{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;padding-top:2px}}
.pick input{{width:22px;height:22px;accent-color:var(--accent);cursor:pointer}}
.pick span{{font:600 11px var(--fb);color:var(--mute);letter-spacing:.06em;text-transform:uppercase}}
.meta{{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:12px;color:var(--mute)}}
.fid{{font-variant-numeric:tabular-nums;color:var(--ink2)}}
.sev{{font-weight:600}} .sev.high{{color:var(--hi)}} .sev.medium{{color:var(--med)}} .sev.low{{color:var(--low)}}
.f h3{{font:800 20px/1.2 var(--fd);margin:6px 0 10px;text-wrap:balance}}
.f p{{margin:0 0 8px;color:var(--ink2);max-width:62ch}}
.f p b{{color:var(--ink);font-weight:600;margin-right:4px}}
figure{{margin:0}}
figure img{{display:block;width:100%;border:1px solid var(--line);border-radius:4px}}
figcaption{{font-size:11px;color:var(--mute);margin-top:4px}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
@media (max-width:860px){{.f{{grid-template-columns:auto minmax(0,1fr)}} figure{{grid-column:1/-1}}}}
</style>
<div class="wrap">
<header>
  <h1>Design audit</h1>
  <p>Every small detail on the concept pages that reads as generated rather than designed, checked against SailGP's calendar and event pages. {total} findings: {E(summary)}. Real bugs found on the way are included.</p>
  <p>Tick <b>Fix</b> on the ones you want changed, then press <b>Copy picks</b> and paste the list into the chat. Ticks are remembered in this browser.</p>
</header>
<div class="tally"><span><b id="n">0</b> picked</span><span class="sp"></span>
<button class="ghost" id="allHigh">Tick all high</button><button class="ghost" id="none">Clear</button><button class="go" id="copy">Copy picks</button>
<textarea id="out" rows="2" readonly hidden aria-label="Picked finding ids"></textarea></div>
{"".join(sections)}
</div>
<script>
const K="audit-picks", boxes=[...document.querySelectorAll(".pick input")];
let saved=[]; try{{saved=JSON.parse(localStorage.getItem(K)||"[]")}}catch(e){{}}
const sync=()=>{{const ids=boxes.filter(b=>b.checked).map(b=>b.dataset.id);document.getElementById("n").textContent=ids.length;
  boxes.forEach(b=>b.closest(".f").classList.toggle("on",b.checked));try{{localStorage.setItem(K,JSON.stringify(ids))}}catch(e){{}};return ids}};
boxes.forEach(b=>{{b.checked=saved.includes(b.dataset.id);b.onchange=sync}});sync();
document.getElementById("allHigh").onclick=()=>{{document.querySelectorAll(".sev.high").forEach(s=>s.closest(".f").querySelector("input").checked=true);sync()}};
document.getElementById("none").onclick=()=>{{boxes.forEach(b=>b.checked=false);sync()}};
document.getElementById("copy").onclick=async()=>{{const t="Fix: "+(sync().join(", ")||"none");const o=document.getElementById("out");o.value=t;o.hidden=false;
  try{{await navigator.clipboard.writeText(t);document.getElementById("copy").textContent="Copied"}}catch(e){{o.select()}}}};
</script>
'''
open(OUT, "w").write(page)
print(OUT, total, counts, round(len(page)/1e6, 2), "MB")
