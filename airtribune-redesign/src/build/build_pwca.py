"""Build the PWCA Asian Tour India, Panchgani 2027 page from the SRS page template.
Run from airtribune-redesign/:  python3 src/build/build_pwca.py
Writes events/pwca/india-panchgani.html. Facts come from the official PWCA page
(saved as text in src/data/pwca-panchgani/pwca-page.txt, retrieved 24 Nov 2026).
"""
import html, json, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL = open(f"{ROOT}/src/build/srs-template.html").read()
HELPERS = open(f"{ROOT}/src/build/helpers.js").read()
esc = html.escape

URL = "https://pwca.org/events/2026-pwca-asian-tour-india-panchgani-2027-season-2026"
PILOT = URL + "#pilot-information"
MAP = "https://drive.google.com/file/d/1_1DYozclJPhy5E6ntz7BoOghSrsvwAfn/view?usp=sharing"

def board(rows):
    """Typographic figure row (same look as the SRS travel/entry boards)."""
    return '<div class="ground">' + "".join(
        f'<div class="gs"><span class="k">{esc(k)}</span><span class="big">{esc(b)}</span><span class="sm">{esc(s)}</span></div>' for k, b, s in rows) + "</div>"

def words(items, neg=()):
    return '<p class="words">' + '<i>/</i>'.join(
        f'<span class="w{" no" if x in neg else ""}">{esc(x)}</span>' for x in items) + '</p>'

def run(k, items, neg=(), need=False):
    return (f'<div class="run{" need" if need else ""}"><div class="run-h"><span class="k">{esc(k)}</span>'
            f'<span class="n">{len(items) - len(neg)}</span></div>{words(items, neg)}</div>')

# ---------- tab: team (replaces "Entry") ----------
team = ('<div class="tb-h"><span class="eyebrow">Organising team</span><span>As listed on pwca.org</span></div>'
        + board([("Meet director", "Goksal", "Dora Goksal"),
                 ("Organiser", "Bhagra", "Krishan Kant Bhagra · WhatsApp +91 98166 48041"),
                 ("Rescue lead", "Geeth", "Ganesh Geeth, rescue at earlier Pre-PWCs in Panchgani")])
        + board([("PWCA scorer", "Dimov", "Daniel Dimov"),
                 ("Safety & retrieve", "Lukanov", "Ivan Lukanov"),
                 ("Event manager", "Dimiskovski", "Goran Dimiskovski")])
        + '<div class="runs">'
        + run("Supported by", ["Directorate of Tourism, Maharashtra", "Aero Club of India (NAC)"])
        + run("Still to come", ["Selection list", "Waypoints & airspace", "Rescue operations lead (TBC)"], need=True)
        + '</div>'
        + f'<p class="tnote"><b>Entry</b><span>Entry fee and pilot numbers are not published yet. Register and follow the selection list on the PWCA page.</span><a class="btn btn-o" href="{PILOT}">Pilot information</a></p>')

# ---------- tab: safety (replaces "On site") ----------
safety = ('<div class="tb-h"><span class="eyebrow">Safety &amp; rescue</span><span>As listed by the organisers</span></div>'
          + board([("Ambulances", "2", "Take-off and landing, advanced life support"),
                   ("Medical", "1 + 4", "Doctor at take-off, two nurses per ambulance"),
                   ("Rescue boat", "Dhom", "Power boat on Dhom Lake for water landings")])
          + '<div class="runs">'
          + run("On the ground", ["Flymaster live trackers", "LoRa radio tracking network", "2 off-road rescue SUVs", "No heli-rescue yet"], neg=("No heli-rescue yet",))
          + run("Panchgani · ~10 km", ["Bel Air General Hospital (X-ray, ECG)", "Bel Air Wai unit (MRI)"])
          + run("Within 45 min", ["Ajinkya Hospital", "Satara Hospital", "Trauma & MRI"])
          + run("Pune · ~4 h", ["Apollo Hospital", "Columbia Asia Hospital"])
          + '</div>'
          + '<p class="tnote"><b>Heli-rescue</b><span>Not available at present. The organisers are working with the authorities on a heli-ambulance and will confirm.</span></p>')

# ---------- tab: getting there ----------
travel = ('<div class="tb-h"><span class="eyebrow">Fly in</span><span>Distance to Panchgani</span></div><ol class="board2">'
          '<li class="jr"><span class="code" aria-hidden="true">PNQ</span><span class="city">Pune<small>International airport · 2.5–3 h by road</small></span>'
          '<span class="track"><i data-w="47%"></i></span><span class="val">120<small>km</small></span></li>'
          '<li class="jr"><span class="code" aria-hidden="true">BOM</span><span class="city">Mumbai<small>Chhatrapati Shivaji Maharaj · ~6 h</small></span>'
          '<span class="track"><i data-w="100%"></i></span><span class="val">255<small>km</small></span></li></ol>'
          + board([("Taxi from Pune", "₹3,000", "About €30 one way, 2 people with 2 glider bags"),
                   ("Taxi from Mumbai", "₹6,000", "About €60 one way. Ola Outstation or Uber Intercity"),
                   ("Bus", "redbus.in", "State and private buses to Panchgani or Mahabaleshwar")])
          + '<div class="tb-h" style="margin-top:56px"><span class="eyebrow">Stay at HQ</span><span>Cloudmist Resort &amp; Spa</span></div>'
          + board([("Single", "₹3,500", "About €35 a night, with breakfast"),
                   ("Double", "₹4,500", "About €45 a night, with breakfast. Few twin beds in Panchgani"),
                   ("Rooms", "30", "First come, first served for pilots who book early")])
          + '<p class="tnote"><b>HQ</b><span>Panchgani–Mahabaleshwar Road, 4.8 km from the town centre: briefing hall, restaurant, pool. Taxi to town about ₹200; an evening shuttle runs at a fixed time.</span></p>')

STORY = ["Panchgani is one of India's top paragliding destinations: a hill station among five hills of the Sahyadri range in Maharashtra, crowned by the Table Land, a vast volcanic plateau.",
         "February is the best month to fly here: mild temperatures, strong thermals and moderate winds. Sea breeze from the west meets land breeze from the east, often building convergence lines over Panchgani."]
SCHEDULE = [("Sat 6 Feb 2027", "Event opens"), ("6–12 February", "Seven days of competition"), ("Daily", "Briefing in the HQ conference hall at Cloudmist")]

SITE_TILES = [("Region", "Satara, Maharashtra"), ("Range", "Sahyadri"), ("Landing", "Boat Club"), ("Launches", "Green mats, by car")]
SITESHORT = ("Small hills and flatlands make good cross-country and race terrain. Every take-off is reachable by car, with green mats and sunshades. "
             "Top-landing on the Table Land is easy; the official landing is the obstacle-free Boat Club by Dhom Lake.")
CALLOUT = ('<div class="callout"><b>Trackers: India exception</b><ul>'
           '<li>Satellite trackers are mandatory at PWCA events from 2026, but are <strong>not required here</strong> because of import rules in India. PWCA recommends leaving them at home.</li>'
           '<li>Flymaster trackers are supplied, backed by a LoRa radio network on the ground at no extra cost.</li>'
           f'<li><a href="{MAP}" style="color:var(--yellow);text-decoration:underline">Official flying-area map ↗</a></li></ul></div>')

BAND = [("6–12 Feb", "2027"), ("7", "Days"), ("2", "Ambulances"), ("120 km", "From Pune"), ("€35", "HQ room from"), ("Asian Tour", "PWCA")]

rep = {
  "TITLE": "Panchgani · PWCA Asian Tour 2027",
  "DESC": "PWCA Asian Tour India, Panchgani: 6–12 February 2027, Maharashtra, India. Flying site, safety, team and travel.",
  "REG": PILOT, "REGSHORT": "pwca.org/events",
  "HERO": "white-blur", "HEROPOS": "50% 45%", "PHOTO2": "orange-blur",
  "ROUNDLABEL": "PWCA Asian Tour · Season 2026", "STATUS": "Confirmed", "STATUSCLS": "ok",
  "VENUE": "Panchgani", "COUNTRY": "India", "DATES": "6–12 Feb 2027", "EVNAME": "PWCA Asian Tour India 2027", "TASKS": "7",
  "BAND": "".join(f"<div><b>{esc(v)}</b><span>{esc(l)}</span></div>" for v, l in BAND),
  "VENUEHEAD": "Racing over the Table Land",
  "BLURB": "One of India's top flying sites: five hills of the Sahyadri range, a volcanic plateau and convergence lines over the town.",
  "STORY": "".join(f"<p>{esc(x)}</p>" for x in STORY),
  "SCHEDULE": "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in SCHEDULE),
  "SITEHEAD": "Panchgani & the Table Land",
  "SITETILES": "".join(f'<div><span class="eyebrow">{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in SITE_TILES),
  "SITESHORT": esc(SITESHORT), "CALLOUT": CALLOUT,
  "ENTRY": team, "FEATURES": safety, "TRAVEL": travel, "PRIZES": "", "RAIL": "",
  "PLACE": "Panchgani, Maharashtra", "CARD1": "pink-close", "CARD2": "gin-field", "CARD3": "coral-terraces",
  "RACELINE": "Seven days of PWCA racing in February, the best flying month in Panchgani.",
  "TRIPLINE": "Fly to Pune (120 km) or Mumbai (255 km), then a taxi. HQ rooms from about €35.",
  "EVTJSON": json.dumps({"start": "2027-02-06", "end": "2027-02-12", "tz": 5.5, "seed": 6 * 97 + 29}),
  "HELPERS": HELPERS,
}
out = TPL
for k, v in rep.items():
    out = out.replace("{{" + k + "}}", v)
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)

# ---------- PWCA-specific edits to the SRS template ----------
EDITS = [
  ("Not affiliated with or endorsed by Airtribune or the Sports-Class Racing Series.", "Not affiliated with or endorsed by Airtribune or the PWCA."),
  ("/* Layout: SRS round page.", "/* Layout: PWCA event page (built from the SRS round template)."),
  ('<a class="srsb" href="../index.html#srs" aria-label="Sports-Class Racing Series rounds"><img src="../img/srs-mark-white.png" alt=""></a>',
   f'<a class="srsb" href="{URL}" aria-label="Paragliding World Cup Association"><img src="../img/pwca-badge.png" alt=""></a>'),
  ('<a class="btn btn-o" href="' + PILOT + '">Register</a>\n  </div>\n</header>', '<a class="btn btn-o" href="' + PILOT + '">Register</a>\n  </div>\n</header>'),
  ('<img class="hero-srs" src="../img/srs-full-white.png" alt="Sports-Class Racing Series">',
   '<img class="hero-srs hero-pwca" src="../img/pwca-badge.png" alt="Paragliding World Cup">'),
  ('<div class="lockup"><img src="../img/srs-full-white.png" alt="Sports-Class Racing Series">',
   '<div class="lockup"><img src="../img/pwca-badge.png" alt="Paragliding World Cup">'),
  ('<a href="https://sportsracingseries.org/rules/">SRS rules ↗</a><a href="https://sportsracingseries.org/faqs/">SRS FAQs ↗</a>',
   f'<a href="https://pwca.org/rules">PWCA rules ↗</a><a href="{MAP}">Flying-area map ↗</a>'),
  ('data-tab="entry">Entry</button>', 'data-tab="entry">Team</button>'),
  ('data-tab="onsite">On site</button>', 'data-tab="onsite">Safety</button>'),
  ('<a href="#info" data-open-tab="entry">Entry</a>', '<a href="#info" data-open-tab="onsite">Safety</a>'),
  ('<p>Every pilot is tracked live on Airtribune, task by task.</p>', '<p>Flymaster trackers on every pilot, with a LoRa radio network as back-up.</p>'),
  ('<span class="eyebrow">Tasks</span><span class="v">7 racing tasks</span>', '<span class="eyebrow">HQ</span><span class="v">Cloudmist Resort</span>'),
  ('Registration numbers from Airtribune on 24 Nov 2026.', 'Event facts from pwca.org on 24 Nov 2026. Entry fee and selection list not yet published.'),
  ('<p>Illustrative task shape, not an official task.</p>', '<p>Illustrative task shape, not an official task. Waypoints are still to be published.</p>'),
  ('Sources, retrieved 24 Nov 2026: <a href="https://sportsracingseries.org/events/">sportsracingseries.org/events</a> · <a href="' + PILOT + '">pwca.org/events</a>',
   f'Source, retrieved 24 Nov 2026: <a href="{URL}">pwca.org · PWCA Asian Tour India Panchgani 2027</a>'),
  ('Photos: Aninder Singh / Paragliding Atlas, SRS Tapalpa 2026. SRS logo © Sports-Class Racing Series.',
   'Photos: Aninder Singh / Paragliding Atlas, SRS Tapalpa 2026 (not taken at Panchgani). Paragliding World Cup logo © PWCA.'),
  ('Unofficial concept, not affiliated with Airtribune or the SRS.', 'Unofficial concept, not affiliated with Airtribune or the PWCA.'),
  ('.hero-srs{width:150px;margin-bottom:22px}', '.hero-srs{width:150px;margin-bottom:22px}\n.hero-pwca{width:auto;height:96px}.lockup img[src*="pwca"]{height:72px}.nav .srsb img[src*="pwca"]{height:34px}'),
]
for a, b in EDITS:
    assert a in out, a[:80]
    out = out.replace(a, b)
# no season rail for a single PWCA event
out = re.sub(r'\n<section class="s" aria-labelledby="rH">.*?</section>\n', "\n", out, flags=re.S)
body = out.split("<body>")[1].split("<script>")[0]
assert "rH" not in out and "srs-" not in body and "Sports-Class" not in body and "sportsracingseries" not in body, "leftover SRS text"
os.makedirs(f"{ROOT}/events/pwca", exist_ok=True)
open(f"{ROOT}/events/pwca/india-panchgani.html", "w").write(out)
print("wrote events/pwca/india-panchgani.html", len(out))
