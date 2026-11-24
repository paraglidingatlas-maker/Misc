"""Build the 8th British Winter Open page (Panchgani, India, 23 Feb – 2 Mar 2027) from the SRS page template.
Run from airtribune-redesign/:  python3 src/build/build_bwo.py
Inputs: src/data/bwo/bwo.json (from src/data/bwo/extract_bwo.py) and the event text on airtribune.com/bwo2027/
(summarised by hand below; retrieved 24 Nov 2026). Writes events/bwo/british-winter-open.html.
"""
import html, json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL = open(f"{ROOT}/src/build/srs-template.html").read()
HELPERS = open(f"{ROOT}/src/build/helpers.js").read()
D = json.load(open(f"{ROOT}/src/data/bwo/bwo.json"))
esc = html.escape

AT = "https://airtribune.com/bwo2027/"
LIVE = AT  # Airtribune shows live tracking on the event page once tasks are flown
PLAY = "https://airtribune.com/play/{}/2d"
Y = D["y2027"]

def nm(s):
    """'Juan Sebastian OSPINA RESTREPO' -> 'Juan Sebastian Ospina Restrepo'"""
    return " ".join(w.capitalize() if (w.isupper() and len(w) > 1) or w.islower() else w for w in s.split())

def board(rows, cls=""):
    return f'<div class="ground {cls}">' + "".join(
        f'<div class="gs"><span class="k">{esc(k)}</span><span class="big">{esc(b)}</span><span class="sm">{esc(s)}</span></div>' for k, b, s in rows) + "</div>"

def words(items, neg=()):
    return '<p class="words">' + ' <i>/</i> '.join(f'<span class="w{" no" if x in neg else ""}">{esc(x)}</span>' for x in items) + '</p>'

def run(k, items, neg=(), need=False, n=None):
    n = len(items) - len(neg) if n is None else n
    return (f'<div class="run{" need" if need else ""}"><div class="run-h"><span class="k">{esc(k)}</span>'
            f'<span class="n">{n}</span></div>{words(items, neg)}</div>')

# ---------- What's on ----------
STORY = ["Eight days in Panchgani, the week after the PWC at the same venue, with a rest day between the two for pilots flying both.",
         "The British Winter Open keeps pilots flying through the northern winter: seven tasks, CCC and Sports wings in one field, PWCA letters, and a party to finish."]
SCHEDULE = [("Tue 23 Feb", "Registration & equipment check 14:00–18:00 · mandatory safety briefing 19:00"),
            ("24 Feb – 2 Mar", "Competition flying days · window opens around 10:30"),
            ("Tue 2 Mar", "19:00 prize giving, celebration meal and closing")]
DAILY = [("07:00", "HQ opens"), ("08:00", "Transport to take-off"), ("09:30", "Task & safety committees"), ("10:00", "Pilot briefing"),
         ("10:30", "Take-off window opens"), ("16:30", "Scoring office opens"), ("20:00", "Provisional results")]

# ---------- Flying site ----------
SITE_TILES = [("East · Harrison's Folly", "1,100 m"), ("South · Khingar", "1,174 m"), ("West", "Panchgani West"), ("Landing", "Boat Club")]
SITESHORT = ("East, west and south-facing launches, all reachable by car, on the hills around the Table Land, a volcanic plateau. "
             "Sea breeze from the west meets land breeze from the east, often building convergence lines over town. "
             "Top-landing on the Table Land is easy; the official landing is the Boat Club by Dhom Lake.")
CALLOUT = ('<div class="callout"><b>Instruments in India</b><ul>'
           '<li>Only phone-based GPS devices (with an IMEI number) are allowed into India. Bring a phone running XCTrack or Naviter Navigator.</li>'
           '<li>Leave FLARM, Garmin inReach and SPOT devices at home: they can cause problems at customs.</li>'
           '<li>Tracking is a local Meshtastic network; the organisers may also issue Flymaster trackers. Bring USB cables so tracklogs can be downloaded.</li></ul></div>')

# ---------- Entry ----------
entry = ('<div class="tb-h"><span class="eyebrow">Entry</span><span>8th British Winter Open</span></div>'
         + board([("Entry fee", "£300", "or €360, by PayPal once offered a place"),
                  ("Field", "120", "Pilots max · 20 places held for women until 45 days out"),
                  ("Selection", "WPRS", "BHPA pilots first, other nations about 14 days later"),
                  ("Refund", "75%", "If you cancel more than 60 days out · 40% from 60 to 30 days")], "figs4")
         + '<div class="runs">'
         + run("Included", ["Seven tasks", "Tracking for safety & scoring", "T-shirt or souvenir", "Lunch pack", "Retrieves", "Party", "PWCA letters"])
         + '<div class="run need"><div class="run-h"><span class="k">You bring</span><span class="n">8</span></div><p class="words">'
         + ' <i>/</i> '.join(['<b class="w">FAI Sporting Licence</b>', '<b class="w">IPPI 4 or 5</b>'] + [f'<span class="w">{x}</span>' for x in
             ["National licence", "Photo ID", "Liability insurance", "Rescue & medical insurance", "Phone-based GPS", "50 km goal or 100 km XC in 2 years"]])
         + '</p></div></div>'
         + f'<p class="tnote"><b>No entries at the venue</b><span>Places are only offered online, in registration order and by WPRS.</span><a class="btn btn-o" href="{AT}">Register on Airtribune</a></p>')

# ---------- On site ----------
onsite = ('<div class="tb-h"><span class="eyebrow">On site</span><span>As listed by the organisers</span></div><div class="runs" style="margin-top:0">'
          + run("Safety", ["Live trackers supplied", "Tracking mandatory", "Medic on take-off", "Radio coverage", "Good phone coverage", "No helicopter rescue"], neg=("No helicopter rescue",))
          + run("Organisation", ["Launch transport", "Retrieves included", "Tracklogs managed", "Airtribune scoring"])
          + run("Benefits", ["Lunch packs", "ID cards", "Social evening", "Party", "Free gift", "PWCA letters"])
          + run("Environment", ["Plastic reduction"])
          + '</div>')

# ---------- Getting there ----------
travel = ('<div class="tb-h"><span class="eyebrow">Fly in</span><span>Distance to Panchgani</span></div><ol class="board2">'
          '<li class="jr"><span class="code" aria-hidden="true">PNQ</span><span class="city">Pune<small>International · 2.5–3 h by road</small></span>'
          '<span class="track"><i data-w="47%"></i></span><span class="val">120<small>km</small></span></li>'
          '<li class="jr"><span class="code" aria-hidden="true">BOM</span><span class="city">Mumbai<small>Chhatrapati Shivaji Maharaj · ~6 h</small></span>'
          '<span class="track"><i data-w="100%"></i></span><span class="val">255<small>km</small></span></li></ol>'
          + board([("Taxi", "Ola · Uber", "Ola Outstation or Uber Intercity from either airport; about €30 from Pune, €60 from Mumbai for two with gliders"),
                   ("By train", "Pune", "About 3.5 h from Mumbai, then bus or taxi for the last 120 km"),
                   ("By bus", "redbus.in", "Private and state buses to Panchgani or Mahabaleshwar")])
          + '<div class="tb-h" style="margin-top:56px"><span class="eyebrow">Stay at HQ</span><span>Cloudmist Resort &amp; Spa</span></div>'
          + board([("Single", "₹3,500", "About €35 a night with breakfast"),
                   ("Double", "₹4,500", "About €45 a night with breakfast · few twin beds in Panchgani"),
                   ("Rooms", "30", "First come, first served for pilots who book early")])
          + '<p class="tnote"><b>HQ</b><span>Panchgani–Mahabaleshwar Road, 4.8 km from the town centre. Taxi to town about ₹200; an evening shuttle runs at a fixed time.</span></p>')

# ---------- History: past editions with replay (tracking) links ----------
def task_count(e): return len(e["tasks"]) or len(e["task_ids"])
eds = list(reversed(D["editions"]))
hist_rows = ""
for e in eds:
    venue = e["when_where"].split("|")[1].strip()
    when = e["when_where"].split("|")[0].strip()
    win = e["classes"]["overall"][0]
    fem = (e["classes"].get("female") or [None])[0]
    gb = (e["classes"].get("british-overall") or [None])[0]
    km = sum(t["km"] for t in e["tasks"])
    sub = f'{task_count(e)} tasks' + (f' · {km:.0f} km' if km else '') + f' · {e["pilots"]} pilots · {e["nations"]} nations'
    podium = "".join(f'<li><span class="k">{lab}</span><b>{esc(nm(p["name"]))}</b><em>{esc(p["nation"])}</em></li>' for lab, p in
                     (("Overall", win), ("Women", fem), ("British", gb)) if p)
    replays = "".join(f'<a href="{PLAY.format(t)}" aria-label="Replay task {i+1}, {e["year"]}">T{i+1}</a>' for i, t in enumerate(e["replays"]))
    hist_rows += (f'<li class="ed"><div class="ed-y"><b>{e["year"]}</b><span>{esc(venue)}</span><small>{esc(when)}</small></div>'
                  f'<div class="ed-m"><p class="ed-sub">{esc(sub)}</p><ol class="pod">{podium}</ol></div>'
                  f'<div class="ed-r"><span class="k">Task replays</span><div class="rp">{replays}</div>'
                  f'<a class="res" href="https://airtribune.com/{e["slug"]}/results">Full results ↗</a></div></li>')
total_pilots = sum(e["pilots"] for e in D["editions"])
history = f'''
<section class="s hist" id="history" aria-labelledby="hH">
  <div class="wrap">
    <div class="sh"><div><span class="eyebrow">From the Airtribune archive</span><h2 class="up" id="hH">Past editions</h2></div>
      <p class="hist-k"><b>{len(eds)}</b> editions on Airtribune · <b>{total_pilots}</b> pilot entries · every task replayable</p></div>
    <ol class="eds">{hist_rows}</ol>
    <p class="hist-note">Before 2027 the event ran in Roldanillo, Colombia (and Castelo, Brazil, in 2023). Panchgani is a new venue for it. The 2021 edition is not on Airtribune.</p>
  </div>
</section>'''

# ---------- 2027 field ----------
nat = "".join(f'<li><b>{c}</b><span>{n}</span></li>' for c, n in Y["by_nation"][:10])
field = f'''
<section class="s" id="field" aria-labelledby="fH">
  <div class="wrap">
    <div class="sh"><div><span class="eyebrow">Pilot list · 24 Nov 2026</span><h2 class="up" id="fH">The 2027 field</h2></div><a class="btn btn-o" href="{AT}">Pilot list on Airtribune</a></div>
    {board([("Registered", str(Y["registered"]), f"For 120 places · {Y['women']} women"), ("Confirmed", Y["confirmed"].split("/")[0], f"Paid · {dict(Y['by_status']).get('waiting_payment',0)} more invited to pay"), ("Nations", str(Y["nations"]), "Countries on the list")])}
    <ol class="nat" aria-label="Registrations by nation">{nat}</ol>
  </div>
</section>'''

# ---------- prizes ----------
prizes = ('<section class="prz" id="prizes" aria-labelledby="pH"><div class="wrap"><div><span class="eyebrow" style="color:var(--orange)">Awards</span>'
          '<h2 class="up" id="pH">Trophies &amp; classes</h2><p>Trophies, no cash prizes; maybe small gifts from sponsors. Also British Female, British Sports and the Reynolds class. '
          'A class may be dropped with fewer than five pilots.</p></div><div class="prizes">'
          + "".join(f'<div class="prize"><b>{c}</b><span>{d}</span></div>' for c, d in
                    [("Overall", "Every pilot in the event"), ("Female", "All women pilots"), ("Sports", "Sports-class wings"), ("British overall", "Best UK-licensed pilots")])
          + '</div></div></section>')

BAND = [("£300", "Entry fee"), ("7", "Tasks"), ("120", "Max pilots"), (str(Y["registered"]), "Registered"), (str(Y["nations"]), "Countries"), ("CAT 2", "FAI status")]

rep = {
  "TITLE": "Panchgani · 8th British Winter Open",
  "DESC": "8th British Winter Open: 23 Feb – 2 Mar 2027, Panchgani, India. Seven tasks, £300 entry, 120 pilots. Past editions and task replays from Airtribune.",
  "REG": AT, "REGSHORT": "airtribune.com/bwo2027",
  "HERO": "pink-forest", "HEROPOS": "50% 45%", "PHOTO2": "gin-field",
  "ROUNDLABEL": "British Paragliding Open · 8th edition", "STATUS": "Confirmed", "STATUSCLS": "ok",
  "VENUE": "Panchgani", "COUNTRY": "India", "DATES": "23 Feb – 2 Mar 2027", "EVNAME": "8th British Winter Open", "TASKS": "7",
  "BAND": "".join(f"<div><b>{esc(v)}</b><span>{esc(l)}</span></div>" for v, l in BAND),
  "VENUEHEAD": "Winter racing in the Sahyadri",
  "BLURB": "Keep your race form through the northern winter: a week of tasks over India's Table Land, straight after the PWC at the same venue.",
  "STORY": "".join(f"<p>{esc(x)}</p>" for x in STORY),
  "SCHEDULE": "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in SCHEDULE),
  "SITEHEAD": "Panchgani & the Table Land",
  "SITETILES": "".join(f'<div><span class="eyebrow">{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in SITE_TILES),
  "SITESHORT": esc(SITESHORT), "CALLOUT": CALLOUT,
  "ENTRY": entry, "FEATURES": onsite, "TRAVEL": travel, "PRIZES": prizes, "RAIL": "",
  "PLACE": "Panchgani, Maharashtra", "CARD1": "pink-close", "CARD2": "orange-blur", "CARD3": "coral-terraces",
  "RACELINE": "Seven tasks · £300 entry · 120 pilots max, selected by WPRS.",
  "TRIPLINE": "Fly to Pune (120 km) or Mumbai (255 km), then a taxi. HQ rooms from about €35.",
  "EVTJSON": json.dumps({"start": "2027-02-23", "end": "2027-03-02", "tz": 5.5, "seed": 13 * 97 + 13}),
  "HELPERS": HELPERS,
}
out = TPL
for k, v in rep.items():
    out = out.replace("{{" + k + "}}", v)
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)

CSS = '''
/* ---------- BWO: past editions + field ---------- */
.hist-k{font:600 13px var(--f-body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.hist-k b{font:900 italic 22px var(--f-display);color:#fff;margin-right:4px}
.eds{list-style:none;margin:0;padding:0;border-top:1px solid var(--line-2)}
.ed{display:grid;grid-template-columns:220px minmax(0,1fr) 260px;gap:32px;padding:28px 0;border-bottom:1px solid var(--line)}
.ed-y b{display:block;font:900 italic 64px/.85 var(--f-display);color:transparent;-webkit-text-stroke:1.4px rgba(255,255,255,.85)}
.ed:first-child .ed-y b{-webkit-text-stroke:0;color:var(--orange)}
.ed-y span{display:block;margin-top:10px;font:700 12px var(--f-body);letter-spacing:.16em;text-transform:uppercase;color:var(--ink-2)}
.ed-y small{display:block;margin-top:4px;font:400 italic 14px var(--f-display);color:var(--muted)}
.ed-sub{font:700 11px var(--f-body);letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}
.pod{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.pod li{display:grid;grid-template-columns:84px minmax(0,1fr) auto;gap:14px;align-items:baseline}
.pod .k{font:700 10.5px var(--f-body);letter-spacing:.16em;text-transform:uppercase;color:var(--orange)}
.pod b{font:800 italic clamp(18px,1.9vw,24px)/1.15 var(--f-display);text-transform:uppercase}
.pod em{font:700 12px var(--f-body);font-style:normal;letter-spacing:.12em;color:var(--muted)}
.ed-r .k{display:block;font:700 10.5px var(--f-body);letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
.rp{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.rp a{min-width:40px;height:34px;padding:0 10px;display:inline-grid;place-items:center;border-radius:6px;background:var(--orange);color:#fff;font:800 12px var(--f-body);letter-spacing:.08em}
.rp a:hover{background:#ff7420}
.res{color:var(--orange);font-weight:600;font-size:14px}
.hist-note{margin-top:18px;color:var(--muted);font-size:13.5px}
.nat{list-style:none;margin:28px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:0 28px;font:800 italic clamp(20px,2.2vw,28px)/1.6 var(--f-display)}
.nat li{display:flex;gap:8px;align-items:baseline}
.nat span{font:700 13px var(--f-body);color:var(--orange)}
@media (max-width:1000px){.ed{grid-template-columns:minmax(0,1fr);gap:16px}.ed-y{display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}.ed-y b{font-size:44px}.ed-y span,.ed-y small{margin:0}}
@media (max-width:640px){.pod li{grid-template-columns:70px minmax(0,1fr) auto;gap:10px}}
'''

EDITS = [
  ("Not affiliated with or endorsed by Airtribune or the Sports-Class Racing Series.", "Not affiliated with or endorsed by Airtribune or the BHPA."),
  ("/* Layout: SRS round page.", "/* Layout: British Winter Open page (built from the SRS round template)."),
  ("@media (prefers-reduced-motion:reduce)", CSS + "@media (prefers-reduced-motion:reduce)"),
  ('<a class="srsb" href="../index.html#srs" aria-label="Sports-Class Racing Series rounds"><img src="../img/srs-mark-white.png" alt=""></a>\n', ""),
  ('<a href="#info" data-open-tab="travel">Getting there</a></nav>', '<a href="#info" data-open-tab="travel">Getting there</a><a href="#history">Past editions</a></nav>'),
  ('    <img class="hero-srs" src="../img/srs-full-white.png" alt="Sports-Class Racing Series">\n', ""),
  ('<a class="btn btn-ghost" href="../live.html">Live tracking</a></div>\n    <div class="cdbar">', f'<a class="btn btn-ghost" href="{LIVE}">Live tracking</a></div>\n    <div class="cdbar">'),
  ('<div class="lockup"><img src="../img/srs-full-white.png" alt="Sports-Class Racing Series"><span>', '<div class="lockup"><span style="border-left:0;padding-left:0">'),
  ('<p>Every pilot is tracked live on Airtribune, task by task.</p><a class="btn btn-o" href="../live.html">Live tracking</a>',
   f'<p>Every pilot tracked live on Airtribune during the event. Until then, replay any task from past editions.</p><a class="btn btn-o" href="{LIVE}">Live tracking</a>'),
  ('<a class="btn btn-ghost" href="../live.html">Live tracking</a></div>\n      </div>\n      <div class="col-r">',
   f'<a class="btn btn-ghost" href="{LIVE}">Live tracking</a></div>\n        <h3 style="margin-top:40px">Daily schedule</h3><ul class="sched">'
   + "".join(f"<li><b>{t}</b>{esc(x)}</li>" for t, x in DAILY) + '</ul>\n      </div>\n      <div class="col-r">'),
  ('<a href="https://sportsracingseries.org/rules/">SRS rules ↗</a><a href="https://sportsracingseries.org/faqs/">SRS FAQs ↗</a>',
   f'<a href="{LIVE}">Live tracking on Airtribune ↗</a><a href="#history">Past editions &amp; task replays</a><a href="https://www.bhpa.co.uk/">BHPA ↗</a>'),
  ('Registration numbers from Airtribune on 24 Nov 2026.', 'Registration numbers from Airtribune on 24 Nov 2026.'),
  ('<p>Illustrative task shape, not an official task.</p>', '<p>Illustrative task shape, not an official task. Waypoint files are on the Airtribune page.</p>'),
  ('Sources, retrieved 24 Nov 2026: <a href="https://sportsracingseries.org/events/">sportsracingseries.org/events</a> · <a href="' + AT + '">airtribune.com/bwo2027</a>',
   f'Sources, retrieved 24 Nov 2026: <a href="{AT}">airtribune.com/bwo2027</a> (event, pilot list) · past results and replays on airtribune.com ({", ".join(e["slug"] for e in D["editions"])})'),
  ('SRS logo © Sports-Class Racing Series.', 'Not taken at Panchgani.'),
  ('Unofficial concept, not affiliated with Airtribune or the SRS.', 'Unofficial concept, not affiliated with Airtribune, the BHPA or the PWCA.'),
]
for a, b in EDITS:
    assert a in out, a[:90]
    out = out.replace(a, b)
# replace the season rail with the 2027 field + past editions
out = re.sub(r'\n<section class="s" aria-labelledby="rH">.*?</section>\n', "\n" + field + history + "\n", out, flags=re.S)
body = out.split("<body>")[1].split("<script>")[0]
for bad in ("srs-", "Sports-Class", "sportsracingseries", "../live.html"):
    assert bad not in body, bad
os.makedirs(f"{ROOT}/events/bwo", exist_ok=True)
open(f"{ROOT}/events/bwo/british-winter-open.html", "w").write(out)
print("wrote events/bwo/british-winter-open.html", len(out))
