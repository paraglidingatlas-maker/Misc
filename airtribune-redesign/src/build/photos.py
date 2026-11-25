"""Photo choices for the event pages (SRS rounds + British Winter Open).

Organiser photos are the organisers' own uploads on each Airtribune event page
(cover = slideshow, gallery = contest photos), saved in events/img/places/<airtribune-slug>/
by the fetch logged in events/img/places/SOURCES.json ("files.events"; calendar strip picks are in "calendar_picks"). Owner approved their use, 25 Nov 2026.
The owner's SRS Tapalpa 2026 photos stay on the racing cards (Race, Follow live).

Each entry: hero (file, background-position, alt), photo2 (intro figure), trip (Plan-your-trip card),
site (Flying site tab figure or None), gallery (list of (file, alt)) shown as a strip under the cards.
Files are paths under events/img/ without .jpg.
"""
import html

ORG = "Photo: event organiser, via Airtribune"
OWN = "© Aninder Singh · Paragliding Atlas"
esc = html.escape


def P(slug, f):
    return f"places/{slug}/{f}"


PHOTOS = {
  "srs-2027-1": dict(  # Slovenia, Lijak
    hero=(P("srs-2027-1", "g06"), "50% 70%", "A gaggle of paragliders over the Lijak cliffs"),
    photo2=(P("srs-2027-1", "g04"), "The view from Lijak take-off over the Vipava Valley"),
    trip=P("srs-2027-1", "g03"),
    site=(P("srs-2027-1", "s00"), "Pilots launching from the grass at Lijak"),
    gallery=[(P("srs-2027-1", "g00"), "Above the Vipava Valley"), (P("srs-2027-1", "g05"), "Task briefing at take-off"),
             (P("srs-2027-1", "g01"), "Gliders over the green ridge"), (P("srs-2027-1", "g02"), "The gaggle climbing out")]),
  "srs-2027-2": dict(  # France, Montclar
    hero=(P("srs-2027-2", "g08"), "50% 45%", "A paraglider over the Montclar valley"),
    photo2=(P("srs-2027-2", "g01"), "The Montclar ridge from the air"),
    trip=P("srs-2027-2", "s01"),
    site=(P("srs-2027-2", "g04"), "Gliders laid out on the Montclar take-off"),
    gallery=[(P("srs-2027-2", "g02"), "Gaggle above the clouds"), (P("srs-2027-2", "g06"), "Launch on the grass slope"),
             (P("srs-2027-2", "g07"), "Reading the task board"), (P("srs-2027-2", "g05"), "Waiting for the window")]),
  "srs-2027-3": dict(  # North Macedonia, Krushevo
    hero=(P("srs-2027-3", "g04"), "50% 35%", "Racing gliders in the sky over Krushevo"),
    photo2=(P("srs-2027-3", "s01"), "A pilot over the Pelagonia plain"),
    trip=P("srs-2027-3", "s00"),
    site=(P("srs-2027-3", "g05"), "Pilots queuing on the Krushevo launch"),
    gallery=[(P("srs-2027-3", "g00"), "The gaggle over the plain"), (P("srs-2027-3", "g06"), "Registration at the event HQ"),
             (P("srs-2027-3", "g03"), "The landing field"), (P("srs-2027-3", "g02"), "Climbing out")]),
  "srs-2027-4": dict(  # France, St André les Alpes (one cover photo on Airtribune)
    hero=(P("srs-2027-4", "s00"), "50% 55%", "The valley below St André les Alpes"),
    photo2=("coral-terraces", None), trip="pink-forest", site=None, gallery=[]),
  "srs-2027-wsf": dict(  # World Sports Final, Gemona / Bordano
    hero=(P("srs-2027-wsf", "s02"), "50% 45%", "Paragliders above the Tagliamento river near Gemona"),
    photo2=(P("srs-2027-wsf", "s01"), "A glider over the forested slopes near Bordano"),
    trip="gin-field", site=None, gallery=[]),
  "bwo2027": dict(  # 8th British Winter Open, Panchgani
    hero=(P("bwo2027", "s02"), "50% 55%", "The Sahyadri hills and a lake below Panchgani, from the air"),
    photo2=(P("bwo2027", "s01"), "A lake in the hills near Panchgani"),
    trip=P("bwo2027", "s00"), site=None, gallery=[]),
}


def is_org(f):
    return f.startswith("places/")


def fields(at, venue):
    """Template replacements for one page."""
    p = PHOTOS[at]
    hero, pos, halt = p["hero"]
    f2, alt2 = p["photo2"]
    rep = {
        "HERO": hero, "HEROPOS": pos, "HEROALT": esc(halt),
        "HEROCREDIT": ORG if is_org(hero) else OWN,
        "PHOTO2": f2,
        "PHOTO2ALT": esc(alt2) if alt2 else "Paraglider in a racing glide, SRS Tapalpa 2026",
        "PHOTO2CAP": "Event organiser, via Airtribune" if is_org(f2) else "© Aninder Singh",
        "TRIP": p["trip"],
    }
    site = ""
    if p["site"]:
        f, alt = p["site"]
        site = f'<figure class="sitephoto"><img src="../img/{f}.jpg" alt="{esc(alt)}" loading="lazy"><figcaption>{ORG}</figcaption></figure>'
    rep["SITEPHOTO"] = site
    gal = ""
    if p["gallery"]:
        figs = "".join(f'<figure><img src="../img/{f}.jpg" alt="{esc(a)}" loading="lazy"></figure>' for f, a in p["gallery"])
        gal = (f'<section class="gal" aria-labelledby="gH"><div class="wrap"><div class="sh"><div><span class="eyebrow">{esc(venue)} · from the organisers</span><h2 class="up" id="gH">On the hill</h2></div></div>'
               f'<div class="gal-row">{figs}</div><p class="gal-note">Photos: event organiser, from the Airtribune event page.</p></div></section>')
    rep["GALLERY"] = gal
    rep["PHOTOCREDITS"] = ("Venue photos: event organiser, via the Airtribune event page. "
                           "Racing photos: Aninder Singh / Paragliding Atlas, SRS Tapalpa 2026.")
    return rep
