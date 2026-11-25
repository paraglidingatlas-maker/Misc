# Handover: Airtribune redesign concept

Last updated 25 Nov 2026 by the chat "Design audit batch 2" (after "Design audit batch 1") (after "Tour map plan A + design audit") (after "Live view navigation + tour review") (after "BWO import") (after "Rounds redesign + real Task 3") (follows "Airtribune logo rollout").

## Live

| Page | Public URL |
|---|---|
| Landing | https://paraglidingatlas-maker.github.io/Misc/airtribune-redesign/ |
| Season calendar | …/airtribune-redesign/events/ |
| Live tracker (has a Broadcast view: button, `B` key or `#broadcast`) | …/airtribune-redesign/events/live.html |
| 8th British Winter Open (Panchgani) | …/airtribune-redesign/events/bwo/british-winter-open.html |
| SRS event pages (5) | …/airtribune-redesign/events/srs/slovenia-lijak.html and siblings |
| Logo study | …/airtribune-redesign/logo/ |
| Feed redesign | …/airtribune-redesign/feed/ |
| Thumbnail study | …/airtribune-redesign/thumbnails/ |

Private preview of the calendar (owner only): https://claude.ai/artifact/4YVdfeKT38CnqwNS29j1HM

## Sources and how to rebuild

Sources are in `airtribune-redesign/src/`:

- `season-calendar.html` → copy to `events/index.html`, wrapped in `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` … `</html>` (the source has no doctype because it is also published as an Artifact).
- `live-tracker.html` → `events/live.html`, wrapped the same way, with `</style>` followed by `</head><body>` and `</body></html>` at the end.
- Calendar + live tracker in one go: `python3 src/build/build_pages.py` (run from `airtribune-redesign/`) does both wraps below.
- Logo: `assets/brand.js`, loaded by every page, renders the Heritage logo into every `a.logo`, every `[data-brand]` element (`""` lockup, `"mark"`, `"tile"`) and the favicon. Change the logo there only.
- SRS pages: `python3 src/build/build_srs.py src/data/srs-events src/build/helpers.js <out-dir>` writes `<out-dir>/srs/*.html`; use `airtribune-redesign/events` as `<out-dir>`. Event copy, travel facts and schedules are in the `C`, `TRAVEL2` and `EVENTS` dicts in `build_srs.py`; scraped official data is in `src/data/srs-events/`.
- BWO page: `python3 src/data/bwo/extract_bwo.py <cache-dir>` (fetches Airtribune bwo2027 + past editions boc2020, bwo2022, bwo2023, v2_bwo2024, bwo2025, bwo2026 → `src/data/bwo/bwo.json`), then `python3 src/build/build_bwo.py` (from `airtribune-redesign/`; reuses `srs-template.html`, copy summarised in the script).
- Calendar: `AT_SLUG` in `src/season-calendar.html` maps every round to its Airtribune slug; "Live tracking" and "Event page" buttons now go to airtribune.com/<slug>/ (the demo replay stays at events/live.html).
- Images: `events/img/` (photos cropped from the owner's SRS Tapalpa 2026 calendar set; low resolution, about 900 px; full-size originals are probably on the assets branch of the `Website` repository).

## Decisions the owner made

- Dark, SailGP/race-series look; racing orange `#FF5F00`; deep teal-black base.
- Buttons solid orange (glass buttons were rejected).
- Typographic, broadcast-style info blocks (distance board, headline figures, slash-separated word runs) instead of boxed icon cards.
- SRS logo shown wherever possible; it is the highlight.
- Thumbnails: task map on cards, live race in round details.
- **Logo is final: Heritage (study direction No. 1)**: red triangle + blue square, lowercase wordmark with triangle dots on the i's. Live on every page, the favicon, the live-tracker top bar (tile) and the broadcast-view corner bug. The owner briefly picked Thermal/Pinwheel with a switch, then settled on Heritage; the switch was removed.



## NOW: expert "key moments" analysis of Tapalpa Task 3 (owner said "ok", 25 Nov 2026)

Owner asked whether we can analyse tracklogs like an expert paragliding coach and commentate on the big moves. Agreed first step: a **key-moments analysis of SRS Tapalpa 2026 Task 3** for the owner to review (the owner is a pilot; they check tone and calls before anything is published).
- Data: `src/data/srs-task3/task3.json` (top-20 tracks, all fixes, local km from take-off, t = s from the 12:15 gate, tags = SSS/TP/goal times; see SOURCES.md). The IGC zip with all 106 tracks is listed in SOURCES.md if more are needed.
- Measure per pilot and leg: thermals (location, avg climb, entry/exit height, time to centre, leaving early/late vs the gaggle), glides (L/D, speed, height lost per km), deviation from the optimised route and gaggle splits, start timing, leading vs following, TP tagging efficiency, final-glide commit point and goal arrival height; time gained/lost per leg vs the winner and the gaggle.
- Known swing to explain: Abel Varga was 10th (30.6 km to go) at 13:11:40 and 1st, 2.7 km clear, at 13:26:40 (seen in the 3D replay's race order).
- Limits to state plainly: no wind (only the ~1.5 km/h drift estimate), no airspeed or speed-bar data (bar use is inferred), reasons are inferences.
- Output first: a Python analysis script in `src/data/srs-task3/` plus a readable "Key moments" review (time, pilot, what happened, time gained, the evidence) for the owner. Later, if approved: broadcast captions in `concepts/flythrough.html` that jump the camera to each moment, and a short race report.

## DONE: organiser photos on the event pages (25 Nov 2026, live on main)

- Fetched every cover (`slideshow/photo`) and gallery (`contest/photo`) image from the six Airtribune pages into `events/img/places/<slug>/` (`s00..` = cover, `g00..` = gallery; max 1600 px, q80). Source URL of every file: `events/img/places/SOURCES.json` → `files.events` (the calendar strip picks moved to `calendar_picks`). Slugs: srs-2027-1 Lijak, -2 Montclar, -3 Krushevo, -4 St André, -wsf Gemona/Bordano, bwo2027 Panchgani.
- Which photo goes where: `src/build/photos.py` (used by `build_srs.py` and `build_bwo.py`). Organiser photos: hero, intro figure, "Plan your trip" card, a photo on the Flying site tab, and an "On the hill" strip under the cards (four photos). The "Race" and "Follow live" cards keep the owner's Tapalpa racing photos. Credits: hero/figures say "Photo: event organiser, via Airtribune"; footer names both.
- St André has only one cover photo on Airtribune, and Gemona and BWO have only covers (940×380, soft on large screens). So those pages have no strip and no site photo, and St André's intro figure is still the owner's photo. Re-run the fetch if organisers add more (script was ad hoc: grep the page HTML for `/media/(slideshow|contest)/photo/`, skip `CACHE/` thumbnails).
- Owner said all photos may come from the Airtribune page, so the BWO hero is now the organiser's aerial (s02). The calendar strip still uses the owner's lake shot.
- Also fixed: the hero title overflowed on phones for long names (KRUSHEVO, PANCHGANI); minimum size is now 40 px.

## DONE: 3D fly-through prototype, satellite on terrain (built 25 Nov 2026, awaiting owner review)

Page: `airtribune-redesign/concepts/flythrough.html`, live at https://paraglidingatlas-maker.github.io/Misc/airtribune-redesign/concepts/flythrough.html (merged to main 25 Nov; owner offered a "3D" button from live.html once approved). Not linked from live.html yet; the ← goes to the live tracker.
- Data: `concepts/flythrough-data.js`, built by `python3 -I src/build/build_flythrough_data.py` (run from `airtribune-redesign/`) from `src/data/srs-task3/task3.json` (real Task 3, top-20 IGC tracks, every fix, metres from take-off, delta-encoded).
- Stack: MapLibre 4.7.1 (Esri World Imagery raster + AWS terrarium DEM terrain, exaggeration 1, sky/fog), deck.gl 9.0.38 `MapboxOverlay` interleaved (TripsLayer trails at GPS altitude, orange full trail for the followed pilot, SRS-blue leader, drop line to the ground, translucent cylinder walls, take-off/TP/goal labels). Draped ground: cylinder rings, dashed optimised route, shadow of the followed track.
- Camera: Follow (chase cam ~2.6 km behind, heading averaged over ±45 s so thermalling does not spin the view), Course (fitBounds, pitch 58), Orbit, Free (any drag switches to Free). Satellite / Dark (hillshade in site colours). Replay 10–120×, scrubber with gate/TP/goal ticks. Race order board (click a pilot to follow; phone: "Race order" opens a sheet).
- URL hash for demos/screenshots: `#t=1500&cam=course&base=dark&pilot=1709&paused=1` (t = seconds from the 12:15 gate).
- AGL uses the loaded DEM tiles (`map.terrain.getElevationForLngLatZoom`), so it is approximate (SRTM ~30 m).
- Production note for the owner: Esri imagery tiles are keyless test use only; Airtribune would need a licensed satellite provider/key (MapTiler, Mapbox, Esri with a key).
- Screenshots need software WebGL in this container (SwiftShader): Playwright with `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`, serve files via `page.route` (a local http.server was refused by the permission classifier), and wait ~15 s + `map.areTilesLoaded()`.

### Original plan (kept for reference)


Owner shared a screen recording of xcstats.app (tilted 3D vector map, sky/haze, tracks at real altitude) and chose **satellite imagery draped over 3D terrain** as the background. Build it as a **separate prototype page** (`airtribune-redesign/concepts/flythrough.html`), not in live.html, until the owner approves.

Plan:
- MapLibre GL JS (`cdn.jsdelivr.net/npm/maplibre-gl@4.7.1`) with a raster-dem terrain source from AWS Terrain Tiles (terrarium encoding, `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`, keyless), `sky` + fog for the horizon.
- Satellite: Esri World Imagery raster tiles (`https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`, keyless; attribution "Esri, Maxar, Earthstar Geographics"). Fine for the prototype; for production Airtribune needs a licensed provider/key (MapTiler or Mapbox satellite). Tell the owner.
- Tracks: deck.gl (`unpkg.com/deck.gl@9.0.38`) via `MapboxOverlay` (interleaved): PathLayer/TripsLayer with z = GPS altitude (m MSL), animated trail for the selected pilot and the leader; task cylinders as translucent extruded rings; take-off and goal markers.
- Data: real SRS Tapalpa 2026 Task 3 (20 IGC tracks, task, results) in `airtribune-redesign/src/data/srs-task3/task3.json` (see SOURCES.md there; live-tracker.html embeds the same via embed_task3.py).
- Camera: follow mode flying behind the pilot (pitch 60–75°, bearing along the track), course overview, free orbit; timeline scrubber + play speed like live.html; a dark-map toggle in the site colours as an alternative.
- All four hosts above returned 200 from this container (25 Nov 2026), so Playwright screenshots should render.
- Check at 1440 and 390, screenshot fly-through frames, send to the owner.

## DONE 25 Nov 2026 (later in the same chat)
- Concept banner removed from every page (owner: officially hired); footers keep sources, credits and "check the official event page"; root page text updated. CLAUDE.md updated.
- Calendar strip: each column has a place photo (organisers' photos from its Airtribune event page, `events/img/places/<slug>.jpg`, BWO uses the owner's Panchgani lake shot) that fades in on hover/focus; SRS columns crossfade from their race photo to the venue; the open column shows its photo behind the details, which sit at the bottom. The generated task map in the open column is gone (it was invented data). Photos load when the strip nears the viewport.
- Live tracker: zoom goes down to about 50 m across the view (5–10 m scale bar); a scale bar (bottom-left, top-left on phone) shows the real distance; follow camera locks to the pilot when zoomed in.
- Photos still unused: the other organiser photos per event are in the session scratchpad only; re-run the fetch (event pages: `slideshow/photo` = cover, `contest/photo` = gallery) if more are needed for the tour/rounds immersion work.

## ALSO OPEN (25 Nov 2026, same chat)
- Done and live: the Gemona photo fades into the page (no hard band); the live tracker's pilot data card opens only when a pilot is clicked and closes with × or Esc; the map help strip has a × and hides on the first drag/scroll.
- Owner asked: place photos on hover in the calendar strip (SailGP style), a more immersive tour, and a whole-page immersion review. The review is in `docs/design-audit/immersion.md` (ranked techniques). **Blocked on place photos**: Commons/Wikipedia rate-limit this container (429); Unsplash search needs a key. Waiting for the owner to choose: their own photos (Website repo, assets branch), an Unsplash API key, or links they pick.

## NOW: rethink the calendar hero (owner asked 25 Nov 2026: "the home page hero need rethink, try using some other concept")

Assumed to mean the hero of the season calendar (events/index.html, source `src/season-calendar.html`, markup at `<section class="hero"`), because the site root is only a list of the concepts. **Confirm this with the owner first.**

Current hero: the race bar above it (next round, country, countdown), a full-bleed `orange-pod` photo with a slow zoom, the label "Paragliding · Season 2026/27", the big "World calendar 2026/27" title, a short intro, and a frosted info card (next round, dates, Round details button, Live tracker replay link). Below it is the stat band with count-ups. Audit findings that apply (docs/design-audit/cal.json): cal-09 (next round shown three times above the fold), cal-28 (slow zoom, glass card over the photo's subject), cal-33 (card inside a card), cal-07 (stat rows repeat each other), cal-02 (city as the headline).

Way of working (same as batch 3, which this merges into): **don't change the live page first.** Build 2–3 distinct concepts as static mockups in `airtribune-redesign/concepts/` (e.g. hero-a.html, hero-b.html, hero-c.html, reusing the page's fonts, colours and photos), screenshot each at 1440 and 390 px, and send them to the owner. Only after the owner picks one, roll it into `src/season-calendar.html`, rebuild with `python3 src/build/build_pages.py`, check, and commit to main. Keep the owner decisions: solid orange buttons, SRS logo prominent, Heritage logo, the concept label, photo credits, a SailGP-style look.

Direction ideas to start from (the owner said "some other concept", so they should differ clearly from today's photo + title + card):
- A. Broadcast title card: the next round is the headline (city in huge type, dates, a live countdown on one line, one orange button), the photo full-bleed behind it, no card and no repeated race bar.
- B. The season is the headline: a typographic month-by-month run of all 26 rounds (city names, SRS rounds in blue, the next round in orange) fills the hero; the photo is secondary or a strip.
- C. Live first: the hero is the Tapalpa Task 3 replay itself (map + top-5 ribbon, autoplaying muted), with the title and "Watch replay" over it.

## NOW: fix the design audit, batches 1 and 2 (owner said "Ok", 24 Nov 2026)

A full audit found 98 details that read as generated rather than designed, or are plain bugs: calendar 38, event pages 30, live tracker 30. Review page for the owner: https://claude.ai/artifact/Qh394Ym3DANTECr7Bms3mp (private). Data: `docs/design-audit/cal.json`, `ev.json`, `live.json` (fields: id, title, what, why, fix, severity, effort, where = source file:line, img), screenshots in `docs/design-audit/img/`, page generator `docs/design-audit/build_review.py` (expects findings/*.json + png beside it; adapt paths).

Owner agreed to this plan ("Will it help or will we degrade?" → answered, then "Ok"):
- **Batch 1, bugs and wrong data, do first:** real flags (flag-icons SVG via cdn.jsdelivr.net, or inline SVG) everywhere the stripe flags are (`COUNTRY.c` arrays, `.flag`, `.col-flag`); remove invented content (route doodle + "81.8 km · 4 TP · PREVIEW" on calendar rows, fake podium in the drawer for unflown races); SRS pages: Included/You-bring lists run off the edge (`build_srs.py` ~201/213 join without spaces + `.words .w` nowrap), per-round glider rule (Kruševo allows EN-D), placeholder fact cells and 278-vs-100 registration figures; phone: header logo wraps "airtri / bune", "100–120 km" clipped, "LIGHTWEIG/HT"; live tracker: captions/toasts never fully hide and go stale after scrubbing, board order contradicts gaps/heights, rows fly through each other on reshuffle, empty flag gap in the broadcast lower third, B/Space stop working after clicking a control, map label overlap ("AmacuecaGoal"), Leaderboard header wraps at Result stage, phone broadcast cuts the stats bar. See all severity high + any finding that is a bug.
- **Batch 1: DONE and live (commit "Design audit batch 1: bugs and wrong data").** Before/after sheets sent to the owner, also saved in `docs/design-audit/batch1/`. What changed:
  - Calendar: flags are `<img>` from flag-icons 4:3 SVG on cdn.jsdelivr.net (`flagImg()`; `COUNTRY` no longer has colour arrays). Row km/route doodle removed (non-SRS rows now have 4 grid columns; SRS rows keep the photo only). The drawer's simulated race/podium/board and the whole `startRace` code were deleted. `bigDates()` writes "27 Jan – 03 Feb" across months. Phone: race bar one line (country + countdown; dates hidden ≤480), "Create event" → "Create" ≤480, `.nav-srs` hidden ≤480. `assets/brand.js` sets `white-space:nowrap` on the logo (fixes "airtri / bune" on every page). Search placeholder is "Search".
  - SRS pages (`build_srs.py`): `words()` joins with `&nbsp;<i>/</i> ` so lists wrap; `glider_class()` reads the ✅/❌ lines of each summary (Lijak CSC only, Kruševo EN-D and below, Montclar/Gemona EN-C, St André none → line dropped); `short_req()` builds You-bring from each round's REQUIRED list. **Source conflict to tell the owner:** Kruševo's details page still says EN-C or below; the summary says EN-D, and the page follows the summary as the audit asked. Band shows only facts that exist (`Confirmed · N registered`, no "Soon"/"—"); the template takes `{{BANDN}}` (cell count) for the grid. Phone distance board and prize names fixed.
  - Live tracker: flags via `ISO2` map + `flagHTML(code)`; toast hides with opacity/visibility and `clearToast()` runs on jump/scrub/broadcast toggle; **the board now ranks strictly every 2 s (the 15 m / 50 m hysteresis `settle()` was removed, because it made the order contradict the gaps); flag this to the owner in case they see more swapping**; map tags and "Highest pilot" use the same snapshot (`pl.sAlt`, `M.hi`); only moved rows animate (staggered, opaque, risers on top; no animation on seeks); pointer clicks blur buttons so B/Space/arrows keep working; TP labels within 3 km merge ("Amacueca · Goal"), stay in view and block pilot tags; panel header is one phase title (Start gaggle / Race / Goal order / Result), phone tab just "Leaderboard"; phone broadcast lower third shows P/flag/name/alt/vario, broadcast button hidden there; `PEEK = 196`.
  - Not done in batch 1 (left for batch 2 or later): ev-05 random task map on SRS "Flying site" tab (needs real map data, or drop it), cal-23 generated task map in the calendar strip, live-11 grouping goal arrivals in the feed, live-19 TV names.
  - Screenshot helper: `docs/design-audit/shot.js` (Playwright; serves the repo through `page.route` on http://local/ because a local http.server was refused here; passes the agent proxy so the jsDelivr flags load). Usage: `node docs/design-audit/shot.js jobs.json` with jobs `{url, w, h, out, actions, scrollTo, clip}`.
- **Batch 2, strip generated touches, then (NEXT, owner already approved):** gradient bars/fills on SRS, gradient-clipped text and glow blobs in the host block, coloured bars on prize cards, glassy rounded captions on the live tracker; cut accent colours from ~10 to three (+ SRS blue on SRS only); thin uppercase micro-labels to nav/buttons/one label per block; stop reusing the pink glider photo four times on a page.
  **Careful (owner decisions):** keep SRS prominent (logo + blue), keep some slash-separated broadcast runs (owner liked them; thin, don't remove), keep one or two motion touches (next-round orange, maybe one count-up). Flag, don't silently change, anything that touches an owner decision.
- **Batch 2: DONE and live (commit "Design audit batch 2: strip generated touches").** Sheets in `docs/design-audit/batch2/` (sent to the owner). What changed:
  - Colours: teal and yellow tokens are now white in all three sources, so leftovers can't add colour; SRS gradient token is solid SRS blue. Accent set is orange (buttons, next round, active states, lead changes), white/greys, SRS blue on SRS things only, and red only for the Live dot.
  - Calendar: no gradient bar/tint on SRS strip columns; "Show SRS rounds" solid orange; SRS section rings removed, Final as blue text (no red pill); gantt SRS bars solid blue, hike & fly outlined, next round orange ring, Today a white hairline (label dropped, legend explains it); host block without glow blobs or gradient text, ruled list instead of diamonds; status pills, type tags, drawer header, SRS drawer box, strip time box made plain; micro-labels (band, KPI, month rail, spec, status, done row, countdown units) are sentence case 13 px; Live dot red but no pulse; nav SRS shows the logo only; footer headings white.
  - SRS/BWO pages: status chip is plain text; prize cards without colour bars; local-rules callout is a plain sub-section; tab/link/track glows removed; duplicate "Entry"/"On site"/"Awards"/rail eyebrows removed, figure labels grey sentence case; slash runs kept (owner liked them) with grey slashes and struck-through grey negatives; "You are here" pill replaced by an orange bottom rule. Photos: every page uses five different photos (hero + intro + three cards, one per canopy: pink / white / orange / coral landscape / pod), assignments in `EVENTS` + `C[...]["cards"]` in build_srs.py and `HERO`/`PHOTO2`/`CARD*` in build_bwo.py. The season rail still shows each round's hero (that's its identity). Calendar photos unchanged.
  - Live tracker: caption is a solid orange square strip (no glass); broadcast lower third, board rows, bug and exit button are opaque, square; P-number sits in a solid orange block; REPLAY is a flat outlined tag (no red, no blink); feed tags plain text (orange only for LEAD), no tinted rows; phase dot removed; timeline ticks white/grey (orange diamonds for lead changes stay); task cylinders, wind arrow, take-off white. Terrain relief keeps its teal tint (the base colour).
  - Not changed, for the owner to decide: the 20-colour pilot palette on map/board (live-06, needed to tell trails apart), green/red position arrows, glass cards (cal-31), task maps (ev-05, cal-23), layout items (batch 3).
- **Batch 3, layout (city as headline, stacked dates, calendar under the title, next round once, fewer stat rows/ledes): do NOT build live.** Make a mockup page first (`airtribune-redesign/concepts/`), screenshot, owner approves. This merges with the "NEXT JOB: high-quality design concepts" below.
- Way of working promised to the owner: one commit per batch (easy revert), before/after screenshots of every change sent to the owner before the next batch, 1440 + 390 checks with Playwright, no console errors.

## Next job: modern live view (owner asked 24 Nov 2026: "let's work on the modern live view, how can we improve it")

Review of events/live.html (src/live-tracker.html) at 1440, 390 and broadcast view found these problems:
- Before the start gate the leaderboard ranks pilots by distance to goal with "+0.1" gaps; meaningless. Pilot names are cut off ("POL BE…").
- The top bar shows "Leader on SSS → SSS"; the map's leader chip (e.g. CASTRO) disagrees with leaderboard P1.
- The "drag to pan" hint covers the Task chip; pilot labels overlap in the gaggle ("P1 SIGEL" over "…ERKE").
- The map is stylised relief only: no real terrain, no thermals or wind, nothing that explains why the race unfolds as it does.
- No altitude story: no barogram or altitude band, the 3D view is basic.
- The race feed is almost empty and the timeline has no event markers.
- Phone: the header and stats fill half the screen, the leaderboard is hidden, the map is cramped.

Proposed improvements, in priority order. **Owner picked 1, 3, 5, 6 and 8 (24 Nov 2026); built and live.** Still open for later: 2, 4, 7, 9, 10.
1. ✅ Race states: before the gate the board ranks by height (gap in m below the top); racing ranks by distance flown with time gaps (time since the leader was at the same distance); arrivals list goal order with times; at the end the official result by score. Top bar shows "Gate 12:15 · in m:ss" / "Leader on X → Y" / "In goal n of 20". One ranking snapshot (every 2 s, with a 15 m / 50 m pass margin so it doesn't flicker) feeds the board, map tags, map chip, strip and broadcast board, so they always agree.
2. Real terrain + satellite basemap, thermal hotspots from the IGC climbs, wind arrow.
3. ✅ Gaggle clustering: 3+ pilots within 22 px become one bubble with a count and the best-placed pilot's tag ("P1 SPANCERSKI +12"); click a bubble to zoom in. Labels are placed in one of four spots and skipped if they would overlap.
4. Barogram / altitude band under the map for the selected pilot vs leader.
5. ✅ Timeline markers on the scrubber: gate, TP1/TP2 first tags, lead changes (orange diamonds), first goal, all in, result. Click to jump there; hover for the text.
6. ✅ Generated race feed (`EVENTS` in src/live-tracker.html): pre-start stack, gate, first/last out of the start, first / half / all through each TP, lead changes (held 2 min by >250 m), strongest climbs (2-min average, each time the day's best is beaten by 0.3 m/s), highest altitude, every goal arrival with gap, result. Big moments also show as a toast.
7. Compare mode: pick 2–3 pilots, ghost lines and live gap.
8. ✅ Phone (≤820 px): full-screen map, compact top bar and telemetry card, bottom sheet with Leaderboard / Race feed tabs (tap the handle to cycle peek → half → full, or drag it), controls in two rows with the timeline full width.
9. Shareable moments: link to a timestamp + camera, clip/still export.
10. Broadcast polish: lower-third captions from the feed, auto-director camera.

**Map navigation is now Google Earth style (owner asked 24 Nov 2026, built and live):** drag grabs the ground (the point under the pointer stays under it, also when tilted) and flings with momentum; scroll, pinch and double-click zoom towards the pointer (shift+double-click zooms out; while following a pilot, zoom stays centred on the pilot); shift-, ctrl-, right- or middle-drag rotates (left/right) and tilts (up/down, 0–60°); two fingers: pinch, twist, or slide up/down together to tilt; double-tap zooms in; keys: arrows pan, shift+arrows rotate/tilt, +/− zoom, N north up, U level, R reset; the compass resets north and tilt. The 2D/3D buttons and broadcast view animate the same continuous tilt. Code: `/* ---------- Google Earth style navigation` in src/live-tracker.html (the tilted plane is scaled just enough to always fill the view). Also fixed: the pre-start board showed "−-6 m" when a lower-ranked pilot was briefly higher; it now shows "+6 m".

**Live view reachable from the calendar (owner asked 24 Nov 2026):** the calendar top bar has a permanent red-dot **Live** pill (with "Tapalpa replay" above 1560 px; also shown on phone) and the hero's next-round card has a "Live tracker · Replay SRS Tapalpa 2026 · Task 3" link, both to live.html. Styles: `.nav-live` / `.hc-live` in src/season-calendar.html. Calendar nav links no longer wrap.

**Host banner photo (owner, 24 Nov 2026):** the photo is now a `.host-photo` layer sized to the banner height (3:2, right-aligned, left edge masked into the dark) so the whole glider shows instead of being cropped by `cover`; on ≤1000 px it shifts right (`right:-25%`).

**Tour map: plan A built and live (24 Nov 2026).** World view (cropped, centred east, no route) + "Alps & Balkans" close-up with the SRS route (arcs, raced legs dimmed). Venue dots: raced (hollow), next (orange), coming up (white), SRS (blue). Area labels are HTML buttons (`AREAS` / `AREAS_EU` in the `/* MAP: The tour */` block of src/season-calendar.html, hand-placed offsets, short names on phone); a label with several rounds opens a list popover (`.tm-pop`), a single round opens the drawer. Glencoe is an off-map note. Stats: rounds/countries, 6 real continents (`CONT`), SRS tour km, season span; the top stat band shows Continents instead of the fake travel total. Plan B (season replay) still possible on top.
Earlier review, for reference: route wraps at the date line (legs R7→R8, R8→R9, R10→R11 cut into 4 subpaths; glider jumps); 13 of 25 legs join overlapping events, so "Season travel 150,691 km" and "Longest transfer 16,103 km" are fictional (SRS-only route ≈ 3,300 km); Europe pins overlap (R22 hidden under R24); clusters "2×/3×" open only one round (R7, R9, R17, R18, R20 unreachable from the map); pins 6–11 px on phone; tooltip never seen on touch; "Continents 5" counts regions. Design proposals: three visual states (past / next / upcoming), SRS as the star, only the next leg bright, crop to the racing, Europe inset, broadcast labels; bolder option: an auto-playing "season replay" with a month scrubber.

**"AI look" cleanup (owner, 24 Nov 2026):** the owner said subtle tells like the coloured accent bars on rows "give away the AI touch", missing the craft of SailGP. Removed: the orange 4 px bar + orange gradient tint on the next-round row, the SRS gradient bar + blue tint on SRS rows, the SRS bar on the SRS spotlight list (`.srs-r`), and the inset orange bar on the live tracker's selected leaderboard row.

## NEXT JOB: high-quality design concepts (owner asked 24 Nov 2026)

Owner: "there are still subtle hints like these bar lines etc which give away the AI touch; in SailGP this is missing; I think we need some concepts like in Midjourney or some high quality results." Goal: move the calendar (start with the All Rounds list and The Tour map) from "competent generated UI" to editorial, broadcast-grade design. Suggested approach, confirm with the owner first:
1. Study sailgp.com (calendar + event pages) and 2–3 other references (F1 calendar, Red Bull X-Alps live, Nike/Rapha editorial) and write down what makes them feel crafted: real photography at full bleed, restrained palette, few UI chrome elements, big confident type with tight tracking, generous negative space, no pills/chips/bars/icon-in-circle buttons, data set in tabular type, motion that serves content.
2. Audit the calendar for remaining AI tells: segmented pill filters with counts, arrow-in-circle buttons, accent bars, gradient tints, frosted cards everywhere, mini route "sparkline" glyphs on every row, uppercase letter-spaced micro-labels everywhere, slash-separated runs everywhere, **fake striped flags that are wrong** (Australia renders as a French tricolour, India as Ireland, Slovenia/UK generic) — use real flag SVGs (e.g. flag-icons via jsDelivr) or drop flags.
3. Produce 2–3 distinct concept directions as static high-fidelity mockup pages (e.g. airtribune-redesign/concepts/rounds-a.html …) and screenshot them for the owner; optionally generate mood imagery with the connected Canva image generation, but the owner wants page-quality results, not just pictures.
4. Owner picks, then roll the chosen direction into src/season-calendar.html.

Owner chose: tour map first (plan A, done), then the full "AI tells" audit (step 2 above), done thoroughly across calendar, event pages and live tracker. Pre-existing issue spotted: on phone the header logo wraps to "airtri / bune".

Notes: the map hint moved to the bottom-left so it no longer covers the Task chip; the Local clock is hidden below 1600 px so the top bar fits at 1440. Long double surnames show the first one on the board (DIAZ, TELLO); full name on hover.

## Open items

- **Done this chat:** Rounds section redesigned to the agreed brief (ruled timing-board rows, sticky month rail, SRS rows with photo + route glyph, next-round strip with the only orange button, completed-rounds fold row, one filter bar with region dropdown; ~2,450 px at 1440). Renderer: `/* ROUNDS: timing-board rows */` in `src/season-calendar.html`.
- **Done this chat:** live tracker replays the REAL SRS Tapalpa 2026 (Airtribune srs-2026-6) Task 3, task 6991, 10 Nov 2026, 58.7 km: official task, results, top-20 IGC tracks. Data + scripts + SOURCES.md in `src/data/srs-task3/` (`embed_task3.py` writes data into live-tracker.html; run before `build_pages.py`).
- **Done this chat:** photo credits made thin/subtle everywhere (300 italic 11px, 45% white, "© Aninder Singh · Paragliding Atlas"); full credit line stays in footers.
- **Done:** 8th British Winter Open page from Airtribune data: 2027 info, entry, on-site, travel, 2027 field (163 registered, 38 nations on 24 Nov 2026), past editions 2020–2026 with podiums and a replay link (airtribune.com/play/<task>/2d) for every past task. Linked from the calendar.
- **Done:** tracking links: every calendar round's Live tracking / Event page button points to its own Airtribune page.
- **NEXT:** import the other rounds the same way. What Airtribune has (checked 24 Nov 2026): big pilot lists + past editions for Porterville, Roldanillo Primera Válida, Copa Niviuk, Copa de las Américas, Piedechinche, Bright, Corryong PG Open, Corryong Sports Cup, Vipava Valley Open, Naviter Open, SRS Slovenia, SRS WSF Gemona; some data for Manilla, Andes Tour, Costa Rica, Apía, Chabre, X-Scotia, SRS Montclar/Krushevo/St André; almost none for Punjab Cup, the two RS Brazil events, Glencoe. Owner said BWO first, then the rest; confirm the format (full page vs round drawer) before the next one.
- **Discarded (owner):** PWCA Asian Tour Panchgani page. Branch `panchgani-draft` still exists on GitHub (the proxy refused to delete it); the owner can delete it, it is not on main.
- Swap in full-resolution photos if the owner provides them or approves access to the `Website` repository.
- Feed and thumbnail pages still use the earlier styles.
- Known small issue fixed this chat: live tracker overflowed 5 px at 390 px (map hint and bottom controls); empty toast box showed in broadcast view.
