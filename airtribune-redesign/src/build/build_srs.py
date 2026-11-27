"""Build one page per SRS 2027 event from the scraped official pages.
Run: python3 build_srs.py <scraped-json-dir> <helpers.js> <site-dir>
"""
import json, sys, re, html, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photos

SRC, HELPERS, SITE = sys.argv[1], sys.argv[2], sys.argv[3]
TPL = open(__file__.replace("build_srs.py", "srs-template.html")).read()
helpers = open(HELPERS).read()
esc = html.escape

EVENTS = [
  dict(slug="slovenia-lijak", at="srs-2027-1", label="SRS 2027 · Round 1 of 4", status="Confirmed", venue="Lijak", country="Slovenia",
       place="Nova Gorica, Lijak", start="2027-03-15", end="2027-03-21", tz=1, tasks=6, seed=18*97+13, hero="pink-blur", heropos="50% 40%", photo2="coral-terraces",
       evname="SRS Slovenia 2027",
       blurb="Lijak is in the south of Slovenia. Offering mild weather throughout the winter, it is the perfect place to kick off the 2027 season.",
       bullets=["Transport by minibus","Grass launch","Ridge & flatland flying","Cold but scenic","Tasks typically 40–60 km"],
       venuehead="The Vipava Valley",
       intro=["The Vipava Valley sits between the Julian Alps and the Karst Plateau in south-west Slovenia: rolling hills, vineyards, villages and views towards the Adriatic. It is one of Europe's most attractive free-flying destinations, with flying potential all year and a welcoming local community.",
              "The SRS will be one of the first competitions of the new European season, a chance for pilots to restart their racing. <strong>The event runs six full racing tasks, 16–21 March 2027.</strong>"],
       sitehead="Lijak take-off",
       tiles=[("Take-off","591 m"),("Wind","S · SW · SE"),("Launch","Broad grassy slope"),("Region","Vipava Valley")],
       site=["The Lijak take-off is one of Slovenia's best-known launch sites, above Nova Gorica in the west of the country, with views across the Vipava Valley to the Adriatic.",
             "It hosts training flights, soaring, cross-country and tandem flying. A favourable microclimate often allows flying when stronger regional winds stop it elsewhere."],
       callout=("Slovenia has special competition rules",["An FAI IPPI 5 licence is mandatory for foreign pilots. Contact your national association early.","Upload your glider certificate or inspection certificate before the event.","Flying the practice day needs pre-registration at HQ.","The road to take-off is private: park by the main road and walk up."]),
       daylabels={0:"Registration & practice"}, taskfrom=1),
  dict(slug="france-montclar", at="srs-2027-2", label="SRS 2027 · Round 2 of 4", status="Provisional", venue="St Jean Montclar", country="France",
       place="Montclar, Southern Alps", start="2027-06-20", end="2027-06-27", tz=2, tasks=7, seed=22*97+13, hero="white-blur", heropos="50% 45%", photo2="pink-close",
       evname="SRS France, Montclar 2027",
       blurb="In the heart of the French Alps. The venue offers classic alpine racing and a uniquely French setting.",
       bullets=["Ski lift to launch","Grass launch","Ridge & alpine flying","Temperatures mid 20s","Tasks typically 50–100 km"],
       venuehead="Classic alpine racing",
       intro=["Montclar is a well-known flying site in the Southern Alps, famous for its generous aerology. For twenty years it has hosted major competitions: the French Open, a World Championship, British Opens and several Pre-PWCs.",
              "The round is listed as <strong>provisional</strong> on the SRS calendar. Check the official page for confirmation before booking travel."],
       sitehead="Plateau de La Chau",
       tiles=[("Take-off","1,907 m"),("Landing","1,335 m"),("Wind","SW to NW"),("Launch","Large grassy plateau")],
       site=["The main competition take-off is the Plateau de La Chau, just under Dormillouse (2,500 m). The launch is large and grassy, and the wind usually comes from south-west to north-west. Good distance flying is possible from about 13:00, earlier if you reach the crests by the second chairlift.",
             "The easiest way out is south along the crests, the sky highway to St André les Alpes: the first 25 km are easy, as far as the Estrop (2,961 m). To the north, the Grand Morgon (2,324 m) is a common turnpoint after a 5 km crossing of Lac de Serre-Ponçon.",
             "The landing at Col Saint-Jean (1,335 m) is a large grass field at the entrance to the Montclar ski resort. Evening convergence there can lift you back to 2,000 m or higher."],
       callout=None, daylabels={}, taskfrom=0),
  dict(slug="world-sports-final-gemona", at="srs-2027-wsf", label="SRS 2027 · World Sports Final", status="Confirmed", venue="Gemona", country="Italy",
       place="Bordano, Gemona", start="2027-07-17", end="2027-07-24", tz=2, tasks=7, seed=24*97+13, hero="pod-closeup", heropos="40% 50%", photo2="gin-field",
       evname="1st SRS World Sports Final", wsf=True,
       blurb="Who will be the SRS Master for 2027? An SRS favourite, one of the best competition venues in Europe.",
       bullets=["Transport by minibus","Grass launch","Ridge & flatland flying","Temperatures high 20s","Tasks typically 70–100 km"],
       venuehead="The first World Sports Final",
       intro=["July is one of the most reliable months in Gemona: green, scenic, with temperatures around 25–30 °C. The region is famous for its ice-cream.",
              "Gemona mixes flatlands out front with mountains to the sides and rear. When the air is unstable the race explores the flatlands; when it stabilises, it heads into the mountains. The venue has become a PWCA favourite and offers a large variety of tasks.",
              "<strong>Seven full racing tasks</strong>, based at Bordano, with camping on site for pilots on a budget."],
       sitehead="Mt Cuarnan & Bordano",
       tiles=[("Take-off","Mt Cuarnan"),("HQ & landing","Bordano"),("Terrain","Alpine & flatland"),("Pedigree","PWC & CAT 2")],
       site=["Gemona, in north-east Italy, has hosted several international PWC and CAT 2 events. The arena offers both alpine and flatland racing, with the Alps to the north and the Mediterranean coast to the south.",
             "This event uses the Bordano HQ and landing field by the river: no obstructions and land-out options for those who don't make goal. The landing field has a camping area (not free) with some electricity, plenty of water, a bar, showers and toilets."],
       callout=None, daylabels={0:"Registration & practice", 7:"Last task · prize giving"}, taskfrom=1,
       sched=[("08:30","HQ opens"),("09:00","Morning briefing at HQ"),("09:30","Transport to take-off"),("10:30","Task & safety committees"),("11:15","Pilot & task briefing"),("11:30","Take-off window opens"),("16:00","Scoring office opens"),("19:00","Provisional results")]),
  dict(slug="north-macedonia-krushevo", at="srs-2027-3", label="SRS 2027 · Round 3 of 4", status="Confirmed", venue="Krushevo", country="North Macedonia",
       place="Krushevo", start="2027-08-22", end="2027-08-29", tz=2, tasks=7, seed=25*97+13, hero="orange-pod", heropos="60% 40%", photo2="white-blur",
       evname="SRS North Macedonia 2027",
       blurb="Krushevo offers a quality of venue unmatched by any other for its large task area, reliable weather and professional team.",
       bullets=["Transport by coach","AstroTurf launch","Flatland flying","Temperatures low 30s","Tasks typically 70–100 km"],
       venuehead="The highest town in the Balkans",
       intro=["At 1,350 m, Krushevo is the highest town in the Balkans: 159 km from Skopje, 55 km from Bitola, 32 km from Prilep and 68 km from the Greek border crossing.",
              "Big task area, reliable summer weather and an experienced local team make it a natural late-season race venue."],
       sitehead="East & West starts",
       tiles=[("East start","1,420 m"),("West start","1,440 m"),("Faces","E–NE · W–SW"),("Valley","Pelagonia")],
       site=["The main East start faces east-north-east over the Pelagonia valley, a few minutes' drive from town on an asphalt road that runs almost to the launch. It is a shallow grassy slope shaded by big trees on its south side, with thermals on all sides.",
             "Typical flights are out-and-returns to Prilep, triangles and zig-zags over the valley and ridge, or distance south towards the Greek border. Coming back from the south is hard against the usual light north wind of summer afternoons, but the roads make retrieves easy.",
             "The smaller West start, 500 m away, faces west-south-west and is also reachable by car."],
       callout=("Note from the event listing",["No helicopter rescue is listed for this round.","Live trackers are supplied, with a medic on take-off and radio coverage."]),
       daylabels={}, taskfrom=0),
  dict(slug="france-st-andre", at="srs-2027-4", label="SRS 2027 · Round 4 of 4", status="Confirmed", venue="St André", country="France",
       place="St André les Alpes", start="2027-09-12", end="2027-09-19", tz=2, tasks=7, seed=26*97+13, hero="coral-terraces", heropos="50% 50%", photo2="pink-forest",
       evname="SRS St. André les Alpes 2027",
       blurb="St André offers big Alpine air in a classic venue. A mix of flatland options to the west, ridges to the north and alpine adventures to the south.",
       bullets=["Transport by minibus","Rocky launch","Alpine, ridge & flatland flying","Temperatures high 20s","Tasks typically 60–100 km"],
       venuehead="Big alpine air",
       intro=["The last round of the 2027 series. St André les Alpes is one of the classic venues of European racing, with routes in every direction from its mountain, Le Chalvet.",
              "The classic route climbs north towards Briançon, the Verdon valley or Allos. The 115 km out-and-return to Fort Dormillouse is a favourite; to the south, the out-and-return to Col de Bleyne."],
       sitehead="Le Chalvet",
       tiles=[("Take-offs","3 within 1 km"),("Faces","S · SE · SW/W"),("Road","7 km · 20–25 min"),("Parking","90 cars")],
       site=["There are three take-offs within a 1 km radius: the S and SE launches sit together, with the SW/W launch a short distance away. A narrow tarmac road climbs 7 km to them, about 20–25 minutes by car, and a shuttle bus runs from July to September from near the school.",
             "St André is not a free-flying site. It is managed jointly by the Association St Andréenne de Vol Libre and the Aérogliss paragliding school; the land is rented and landing is under a special agreement."],
       callout=("Before you fly here",["Contact the Aérogliss school before flying. Their base is next to the lakeside landing field.","Aérogliss: +33 4 92 89 11 30 · divers@aerogliss.com"]),
       daylabels={}, taskfrom=0),
]


# ---------- concise, SailGP-style copy (from the official pages, shortened) ----------
ICON = {
 "Plane": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/></svg>',
 "Train": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="14" rx="3"/><path d="M4 11h16M12 3v8M8 21l2-4M16 21l-2-4"/><circle cx="8.5" cy="14" r=".5"/><circle cx="15.5" cy="14" r=".5"/></svg>',
 "Car": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17h14M6 17v2M18 17v2M3 13l2-6a2 2 0 0 1 2-1.4h10a2 2 0 0 1 2 1.4l2 6v4H3z"/><circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/></svg>',
 "Bus": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="15" rx="2"/><path d="M4 10h16M8 21v-3M16 21v-3"/></svg>',
 "Base": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
}
C = {
 "slovenia-lijak": dict(
   cards=("gin-field","orange-blur","pod-closeup"),
   story=["The Vipava Valley, between the Julian Alps and the Karst, is one of Europe's best free-flying regions, flyable all year round.",
          "SRS opens the 2027 season here: one of the first competitions of the European spring."],
   sched=[("15 March","Registration & practice day"),("16–21 March","Six racing tasks"),("Daily","Transport to launch, retrieves and lunch packs")],
   siteshort="A broad grassy slope above Nova Gorica, with views over the Vipava Valley to the Adriatic. Its microclimate often stays flyable when stronger winds stop flying elsewhere.",
   travel=[("Plane",["<b>Trieste</b> ~50 km","<b>Ljubljana</b> 100–120 km","<b>Venice</b> ~150 km"]),
           ("Train",["To <b>Nova Gorica</b> station","Then taxi or transfer to Lijak"]),
           ("Car",["<b>Ljubljana</b> 1 h 15 – 1 h 40","<b>Trieste airport</b> 45–60 min","Park on the main road, walk up: the take-off road is private"])],
   trip="Trieste airport is about 50 km away; Ljubljana around 100 km."),
 "france-montclar": dict(
   cards=("orange-blur","pod-closeup","coral-terraces"),
   story=["Montclar in the Southern Alps has hosted the French Open, a World Championship, British Opens and Pre-PWCs.",
          "This round is listed as provisional. Check the official page before you book."],
   sched=[("20–27 June","Seven racing tasks"),("From 13:00","Typical start of good distance flying"),("Daily","Transport to launch, retrieves and lunch packs")],
   siteshort="A large grassy plateau at 1,907 m under Dormillouse. The classic line runs south along the crests towards St André; north, across Lac de Serre-Ponçon.",
   travel=[("Plane",["<b>Marseille</b> ~2 h","<b>Nice</b> ~3 h"]),
           ("Car",["<b>Gap</b> ~1 h","<b>Calais</b> ~10 h","Car hire at all airports"])],
   trip="Fly to Marseille (about 2 hours) or Nice (about 3 hours)."),
 "world-sports-final-gemona": dict(
   cards=("pink-forest","orange-blur","coral-terraces"),
   story=["The first SRS World Sports Final crowns the SRS Master for 2027.",
          "Flatlands out front, mountains behind: unstable days race the plain, stable days go into the Alps. Expect 25–30 °C, and ice-cream."],
   sched=[("Sat 17 July","Registration & practice day"),("Sun 18 July","08:30 mandatory safety briefing · Task 1"),("18–24 July","Seven racing tasks · window opens ~11:30"),("Sat 24 July","18:00 trophies & prize draw")],
   siteshort="Launch from Mt Cuarnan; HQ, landing and camping at Bordano by the river, with land-out options all around.",
   travel=[("Base",["HQ & landing: <b>Via Campo Sportivo, Bordano (UD)</b>","Camping on site (paid) with showers and a bar"]),
           ("Car",["Practice-day shuttles: book via the <b>Navetta VLF</b> Telegram bot","Event-day transport to launch included"])],
   trip="Base at Bordano, with camping, showers and a bar on site."),
 "north-macedonia-krushevo": dict(
   cards=("pink-close","coral-terraces","pod-closeup"),
   story=["At 1,350 m, Krushevo is the highest town in the Balkans: a huge task area, reliable summer weather and a seasoned local team.",
          "Flights run out and back to Prilep, around triangles in the Pelagonia valley, or south towards Greece."],
   sched=[("22–29 August","Seven racing tasks"),("Daily","Coach transport to launch, retrieves included")],
   siteshort="The East start (1,420 m) faces the Pelagonia valley, with a road almost to launch. The smaller West start (1,440 m) sits 500 m away.",
   travel=[("Plane",["<b>Skopje</b> ~2 h by car","<b>Ohrid</b> ~1 h 40","Belgrade, Sofia, Thessaloniki within a few hours"]),
           ("Train",["Ljubljana–Thessaloniki line via Skopje","Connections on to <b>Prilep</b>, 35 km away"]),
           ("Car",["E-75 north–south through the country","Car hire from about €40–50 a day"])],
   trip="Fly to Skopje (about 2 hours' drive) or Ohrid (about 1 h 40)."),
 "france-st-andre": dict(
   cards=("white-blur","orange-blur","pod-closeup"),
   story=["The last round of the 2027 series, at one of Europe's classic race venues.",
          "Routes in every direction from Le Chalvet: north to Briançon and Allos, the 115 km out-and-return to Fort Dormillouse, south to Col de Bleyne."],
   sched=[("12–19 September","Seven racing tasks"),("Daily","Transport to launch, retrieves included")],
   siteshort="Three take-offs within 1 km (S, SE and SW/W), 7 km up a narrow road. Not a free site: contact the Aérogliss school before flying.",
   travel=[("Car",["Take-off road 7 km, <b>20–25 min</b>","Parking for 90 cars"]),
           ("Bus",["<b>Fly St André</b> shuttle, July–September","Stop near the Aérogliss school"]),
           ("Base",["Lakeside landing field by the school","Travel details still to be published"])],
   trip="Shuttle to launch from July to September; full travel details to come."),
}
SHORT_INCL = {"Daily transport to launch":"Transport to launch","Retrieves daily":"Daily retrieves","Daily lunch packs":"Lunch packs",
  "Trackers":"Live trackers","Typical tasking":"Tasking & scoring","T-shirt":"T-shirt & souvenirs","Discounts":"Bad-weather activity discounts",
  "Other event benefits":"Event benefits","Access to social":"Social evenings","Entry to any prize":"Prize draws"}
def short_incl(x):
    for k,v in SHORT_INCL.items():
        if x.startswith(k): return v
    return x
REQ_SHORT = [(r"An FAI IPPI (\d)", lambda m: f"FAI IPPI {m.group(1)}"), (r"An FAI Sporting", "FAI Sporting Licence"),
  (r"Medical", "Medical & travel insurance"), (r"Third party", "Third-party liability"), (r"A mobile phone", "Mobile phone"),
  (r"A paraglider certified", None), (r"Recently repacked", "Repacked reserve"), (r"Helmet", "Certified helmet"),
  (r"Harness", "Harness with back protection"), (r"2M Radio", "2 m radio · 143.900 MHz"), (r"Compliance with all SRS", "SRS rules")]
def short_req(reqs, glider):
    """You-bring list from the round's own REQUIRED list; the glider line follows the official class rule (summary page)."""
    out = []
    for r in reqs:
        for pat, v in REQ_SHORT:
            m = re.match(pat, r)
            if not m: continue
            if v is None: v = f"Glider: {glider[0]}" if glider else None
            elif callable(v): v = v(m)
            if v and v not in out: out.append(v)
            break
    return out
def glider_class(t):
    """Allowed / not-allowed wing classes from the ✅ / ❌ lines above 'FAI Status' on the summary page; None if unspecified."""
    seg = t[:t.find("FAI Status")]
    ok = re.findall(r"✅\s*(.+)", seg); no = re.findall(r"❌\s*(.+)", seg)
    if not ok and not no: return None
    a = re.sub(r"\s*allowed$", "", ok[-1].strip()).replace(" & ", " and ") if ok else ""
    n = re.sub(r"\s*(wings\s*)?prohibited$", "", no[-1].strip()) if no else ""
    parts = [x.strip() for x in n.split("&") if x.strip()]
    n = ("No " + (", ".join(parts[:-1]) + " or " + parts[-1] if len(parts) > 1 else parts[0]) + " wings") if parts else ""
    return (a, n)


TRAVEL2 = {
 "slovenia-lijak": dict(fly=[("TRS","Trieste","Friuli Venezia Giulia",50,"KM","50"),("LJU","Ljubljana","Jože Pučnik",110,"KM","100–120"),("VCE","Venice","Marco Polo or Treviso",150,"KM","~150")],
    ground=[("By car","1h15","From Ljubljana, up to 1 h 40 with traffic"),("By car","45′","From Trieste airport, up to an hour"),("By train","Nova Gorica","Then a taxi or transfer to Lijak")],
    note=("Parking","The take-off road is private. Park on the main road and walk up.")),
 "france-montclar": dict(fly=[("MRS","Marseille","Provence",2,"H","~2"),("NCE","Nice","Côte d'Azur",3,"H","~3")],
    ground=[("By car","1h","From Gap"),("By car","10h","From Calais or Dunkirk"),("To launch","Ski lift","Chairlift up to the Plateau de La Chau")],
    note=("Car hire","Available at every airport in the region.")),
 "world-sports-final-gemona": dict(fly=[],
    ground=[("Base","Bordano","HQ, landing and camping · Via Campo Sportivo, 33010 Bordano (UD)"),("Practice day","Shuttle","Book through the Navetta VLF bot on Telegram"),("Task days","Included","Transport to launch and retrieves")],
    note=("Camping","Paid camping at the landing field, with water, showers, toilets and a bar.")),
 "north-macedonia-krushevo": dict(fly=[("OHD","Ohrid","St. Paul the Apostle",120,"KM","120"),("SKP","Skopje","International",160,"KM","160")],
    ground=[("By train","Prilep","Nearest station, 35 km away"),("By road","E-75","The main highway, Serbia to Greece"),("Car hire","€40","Per day, from")],
    note=("Further out","Belgrade, Sofia and Thessaloniki airports are all within a few hours' drive.")),
 "france-st-andre": dict(fly=[],
    ground=[("To launch","7 km","Narrow tarmac road, 20–25 minutes"),("Parking","90","Cars at the take-offs"),("Shuttle","Jul–Sep","Fly St André bus from near the school")],
    note=("Before you fly","Contact the Aérogliss school: St André is not a free-flying site. Full travel details are still to be published.")),
}
def travel_board(slug, venue):
    d = TRAVEL2[slug]; h = ""
    if d["fly"]:
        mx = max(x[3] for x in d["fly"])
        h += f'<div class="tb-h"><span class="eyebrow">Fly in</span><span>Distance to {esc(venue)}</span></div><ol class="board2">'
        for code, city, sub, v, unit, label in sorted(d["fly"], key=lambda x: x[3]):
            w = f"{max(8, round(100*v/mx))}%"
            h += (f'<li class="jr"><span class="code" aria-hidden="true">{code}</span><span class="city">{esc(city)}<small>{esc(sub)}</small></span>'
                  f'<span class="track"><i data-w="{w}"></i></span><span class="val">{esc(label)}<small>{"km" if unit=="KM" else "h drive"}</small></span></li>')
        h += "</ol>"
    else:
        h += f'<div class="tb-h"><span class="eyebrow">Arrive</span><span>Airport details not published yet</span></div>'
    h += '<div class="ground">' + "".join(f'<div class="gs"><span class="k">{esc(k)}</span><span class="big">{esc(big)}</span><span class="sm">{esc(sm)}</span></div>' for k,big,sm in d["ground"]) + "</div>"
    nk, nt = d["note"]
    h += f'<p class="tnote"><b>{esc(nk)}</b><span>{esc(nt)}</span></p>'
    return h


def words(items, cls=""):
    out=[]
    for x,neg in items:
        out.append(f'<span class="w no">{esc(x)}</span>' if neg else f'<span class="w">{esc(x)}</span>')
    return f'<p class="words">' + '&nbsp;<i>/</i> '.join(out) + '</p>'
def entry_block(e, nums, incl, reqs, det, glider):
    sel = "Selection by WPRS on Sports wings" if "WPRS" in det else "Selection by the organisers"
    figs = [("Entry fee", f"€{nums['fee']}", "Per pilot, by PayPal once accepted"),
            ("Membership", "€45", "Per season, covers every SRS round"),
            ("Field", str(nums["max"]), f"Pilots max · {sel}"),
            ("Refund window", "45 days", "Cancel before for a full refund less €60")]
    h = f'<div class="tb-h"><span>{esc(e["evname"])}</span></div>'
    h += '<div class="ground figs4">' + "".join(f'<div class="gs"><span class="k">{k}</span><span class="big">{esc(v)}</span><span class="sm">{esc(sm)}</span></div>' for k,v,sm in figs) + '</div>'
    inc = [short_incl(x) for x in incl]; need = short_req(reqs, glider)
    h += '<div class="runs">'
    h += f'<div class="run"><div class="run-h"><span class="k">Included</span><span class="n">{len(inc)}</span></div>{words([(x,False) for x in inc])}</div>'
    needw = '<p class="words">' + '&nbsp;<i>/</i> '.join((f'<b class="w">{esc(x)}</b>' if x.startswith(("FAI","Glider")) else f'<span class="w">{esc(x)}</span>') for x in need) + '</p>'
    h += f'<div class="run need"><div class="run-h"><span class="k">You bring</span><span class="n">{len(need)}</span></div>{needw}</div>'
    h += '</div>'
    rule = f'<b>Glider class</b><span>{esc(glider[0][0].upper() + glider[0][1:])}{". " + esc(glider[1]) if glider[1] else ""}.</span>' if glider else ""
    h += f'<p class="tnote">{rule}<a class="btn btn-o" href="https://airtribune.com/{e["at"]}/">Register on Airtribune</a></p>'
    return h
def onsite_block(e, feats):
    h = f'<div class="tb-h"><span>As listed by the organisers</span></div><div class="runs" style="margin-top:0">'
    for g in ("Safety","Organisation","Benefits","Environment"):
        items = feats.get(g)
        if not items: continue
        pos = sum(1 for _,n in items if not n)
        h += f'<div class="run"><div class="run-h"><span class="k">{g}</span><span class="n">{pos}</span></div>{words(items)}</div>'
    return h + '</div>'

WEEKDAY = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# venue coordinates for the Flying site skyways map (same points as the season calendar rows)
VENUE_LL = {"srs-2027-1": [45.95, 13.73], "srs-2027-2": [44.40, 6.33], "srs-2027-wsf": [46.28, 13.14], "srs-2027-3": [41.37, 21.25], "srs-2027-4": [43.97, 6.51]}

def text_of(slug, part=""):
    return json.load(open(f"{SRC}/{slug}{part}.json"))["text"]

def bullets_after(t, head, stop_words):
    i = t.find(head)
    if i < 0: return []
    seg = t[i+len(head):]
    end = min([seg.find(w) for w in stop_words if seg.find(w) > 0] or [len(seg)])
    return [re.sub(r"\s+", " ", ln.strip("♦ ").strip()) for ln in seg[:end].split("\n") if ln.strip().startswith("♦")]

def summary_numbers(t):
    def num(label):
        m = re.search(r"(\d+)\s*\n\s*" + label, t)
        return int(m.group(1)) if m else None
    return dict(confirmed=num(r"Pilots\s*\n\s*Confirmed"), registered=num(r"Pilots\s*\n\s*total registered"),
                fee=num(r"EUR\s*\n\s*Entry fee"), max=num(r"Pilots\s*\n\s*max allowed"), countries=num(r"Countries\s*\n\s*presented"))

def features(t):
    i = t.find("days left before start of event"); j = t.find("Prize funds", i)
    groups, cur = {}, None
    for ln in t[i:j].split("\n")[1:]:
        s = ln.strip()
        if s in ("Safety","Organisation","Benefits","Environment"): cur = s; groups[cur] = []; continue
        if cur and s:
            neg = "❌" in s
            clean = re.sub(r"[^\w\s&'’\-+/().,]", "", s).strip()
            clean = re.sub(r"^(No )?", "No " if neg else "", clean).strip()
            groups[cur].append((clean, neg))
    return groups

def travel(t):
    i = t.find("How to get here"); j = t.find("Downloads", i)
    seg = t[i+len("How to get here"):j]
    parts, cur = [], None
    for ln in seg.split("\n"):
        s = ln.strip()
        if s in ("Plane","Train","Car","Bus","Ferry"):
            cur = [s, []]; parts.append(cur); continue
        if cur and s and not s.startswith("http") and not re.match(r"^[A-Za-z ]+ (http|www)", s): cur[1].append(s)
    return parts

def fmt_dates(e):
    a = dt.date.fromisoformat(e["start"]); b = dt.date.fromisoformat(e["end"])
    return f"{a.day}–{b.day} {MON[b.month-1]} {b.year}" if a.month == b.month else f"{a.day} {MON[a.month-1]} – {b.day} {MON[b.month-1]} {b.year}"

for e in EVENTS:
    summ = text_of(e["at"]); det = text_of(e["at"], "-details")
    nums = summary_numbers(summ)
    incl = bullets_after(det, "INCLUDED", ["REQUIRED BY YOU"])
    req = bullets_after(det, "REQUIRED BY YOU", ["If you do not have", "IMPORTANT", "The Sports Racing"])
    req = [r for r in req if not r.lower().startswith("you must comply")] + ["Compliance with all SRS rules, published before the event"]
    prizes_draw = bullets_after(det, "EVENT AWARDS", ["There will not be"]) if "EVENT AWARDS" in det else []
    feats = features(summ)
    trav = travel(det)
    e["dates"] = fmt_dates(e)

    glider = glider_class(summ)
    # only facts that exist: no 'Soon' or '—' cells; confirmed vs registered said plainly
    reg = ([(nums["confirmed"], f"Confirmed · {nums['registered']} registered")] if nums["confirmed"] else
           [(nums["registered"], "Registered · none confirmed yet")] if nums["registered"] else [])
    band = [(nums["fee"] and f"€{nums['fee']}", "Entry fee"), (e["tasks"], "Racing tasks"), (nums["max"], "Places")] + reg + \
           ([(nums["countries"], "Countries")] if nums["countries"] else []) + [("CAT 2", "FAI status")]
    band = [(v,l) for v,l in band if v]
    band_html = "".join(f"<div><b>{esc(str(v))}</b><span>{l}</span></div>" for v,l in band)

    # event days
    a = dt.date.fromisoformat(e["start"]); b = dt.date.fromisoformat(e["end"]); n = (b-a).days + 1
    days = []
    for k in range(n):
        d = a + dt.timedelta(days=k)
        lab = e["daylabels"].get(k) or ("Race day" if k >= e["taskfrom"] else "")
        days.append(f'<div class="day {"task" if k >= e["taskfrom"] else ""}"><div class="d">{d.day:02d}</div><div class="w">{WEEKDAY[d.weekday()]} · {MON[d.month-1]}</div><div class="l">{esc(lab) if lab else "&nbsp;"}</div></div>')
    sched = ""
    if e.get("sched"):
        sched = '<h3 class="up" style="font-size:22px;margin-top:40px">Daily schedule on task days</h3><ul class="sched">' + "".join(f"<li><b>{t}</b>{esc(x)}</li>" for t,x in e["sched"]) + "</ul>"

    feat_html = ""
    for g in ("Safety","Organisation","Benefits","Environment"):
        if feats.get(g):
            feat_html += f'<div class="pgroup"><span class="eyebrow">{g}</span><div class="pills">' + "".join(f'<span class="pill {"no" if neg else ""}"><i></i>{esc(s)}</span>' for s,neg in feats[g]) + "</div></div>"

    prizes = ""
    if prizes_draw:
        cats = [("Overall","All gliders in the competition"),("Women","All female pilots"),("Lightweight","Pilots 85 kg or under"),("Medium weight","Pilots 85–100 kg")]
        draws = [p for p in prizes_draw if "drawn" in p or "prize" in p.lower()]
        drawtxt = " and ".join(re.sub(r"^A (brand new )?|\. The winners.*$|[*]", "", p).strip() for p in draws)
        prizes = ('<section class="prz" id="prizes" aria-labelledby="pH"><div class="wrap"><div><h2 class="up" id="pH">Prizes &amp; categories</h2>'
                  f'<p>Four categories, no cash prizes. Prize draws: {esc(drawtxt)}.' + (' Plus the <b>Constructors Trophy</b> for manufacturer teams.' if "Constructors Trophy" in det else "") + '</p></div>'
                  '<div class="prizes">' + "".join(f'<div class="prize"><b>{c}</b><span>{d}</span></div>' for c,d in cats) + '</div></div></section>')

    cc = C[e['slug']]
    trav_html = travel_board(e['slug'], e['venue'])

    rail = ""
    for o in EVENTS:
        cur = o is e
        rail += (f'<a class="rc {"cur" if cur else ""}" href="{o["slug"]}.html" aria-label="{esc(o["evname"])}{", this page" if cur else ""}">'
                 f'<img src="../img/{photos.PHOTOS[o["at"]]["hero"][0]}.jpg" alt="" loading="lazy"><span class="t"><span>{esc(o["label"].replace("SRS 2027 · ",""))}</span><b>{esc(o["venue"])}</b><em>{fmt_dates(o) if "dates" not in o else o["dates"]}</em></span></a>')

    callout = ""
    if e["callout"]:
        h, items = e["callout"]
        callout = f'<div class="callout"><b>{esc(h)}</b><ul>' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></div>"

    out = TPL
    rep = {
      "TITLE": f"{e['venue']} · SRS 2027", "DESC": f"{e['evname']}: {e['dates']}, {e['place']}, {e['country']}. {e['blurb']}",
      "REG": f"https://airtribune.com/{e['at']}/", "REGSHORT": f"airtribune.com/{e['at']}",
      "HERO": e["hero"], "HEROPOS": e["heropos"], "PHOTO2": e["photo2"],
      "ROUNDLABEL": esc(e["label"]), "STATUS": e["status"], "STATUSCLS": "wsf" if e.get("wsf") else ("ok" if e["status"]=="Confirmed" else "prov"),
      "VENUE": esc(e["venue"]), "COUNTRY": esc(e["country"]), "DATES": e["dates"], "EVNAME": esc(e["evname"]), "TASKS": str(e["tasks"]),
      "BAND": band_html, "BANDN": str(len(band)), "VENUEHEAD": esc(e["venuehead"]), "BLURB": esc(e["blurb"]),
      "INTRO": "".join(f"<p>{p}</p>" for p in e["intro"]),
      "BULLETS": "".join(f'<span class="feat"><i></i>{esc(b)}</span>' for b in e["bullets"]),
      "SITEHEAD": esc(e["sitehead"]), "SITETILES": "".join(f'<div><span class="eyebrow">{esc(k)}</span><b>{esc(v)}</b></div>' for k,v in e["tiles"]),
      "SITE": "".join(f"<p>{esc(p)}</p>" for p in e["site"]), "CALLOUT": callout,
      "DAYS": "".join(days), "SCHED": sched, "FEE": str(nums["fee"]),
      "INCLUDED": "".join(f"<span>{esc(short_incl(x))}</span>" for x in incl), "REQUIRED": "".join(f"<span>{esc(x)}</span>" for x in short_req(req, glider)),
      "FEATURES": onsite_block(e, feats), "ENTRY": entry_block(e, nums, incl, req, det, glider), "PLACE": esc(e["place"]), "CARD1": cc["cards"][0], "CARD2": cc["cards"][1], "CARD3": cc["cards"][2],
      "RACELINE": f"{e['tasks']} racing tasks · €{nums['fee']} entry · {nums['max']} places.", "TRIPLINE": esc(cc["trip"]),
      "STORY": "".join(f"<p>{esc(x)}</p>" for x in cc["story"]),
      "SCHEDULE": "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a,b in cc["sched"]),
      "SITESHORT": esc(cc["siteshort"]), "PRIZES": prizes, "TRAVEL": trav_html, "RAIL": rail,
      "EVTJSON": json.dumps({**{k: e[k] for k in ("start","end","tz","seed")}, "ll": VENUE_LL[e["at"]], "at": e["at"], "venue": e["venue"]}), "HELPERS": helpers,
    }
    ph = photos.fields(e["at"], e["venue"])
    rep.update(ph); rep["CARD3"] = ph.pop("TRIP"); rep.pop("TRIP")
    for k, v in rep.items(): out = out.replace("{{"+k+"}}", v)
    assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
    open(f"{SITE}/srs/{e['slug']}.html", "w").write(out)
    print(e["slug"], nums, len(incl), len(req), len(prizes_draw), [h for h,_ in trav], {g:len(v) for g,v in feats.items()})
