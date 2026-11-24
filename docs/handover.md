# Handover: Airtribune redesign concept

Last updated 24 Nov 2026 by the chat "Airtribune logo rollout" (follows "Airtribune standards upgrade").

## Live

| Page | Public URL |
|---|---|
| Landing | https://paraglidingatlas-maker.github.io/Misc/airtribune-redesign/ |
| Season calendar | …/airtribune-redesign/events/ |
| Live tracker (has a Broadcast view: button, `B` key or `#broadcast`) | …/airtribune-redesign/events/live.html |
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
- Images: `events/img/` (photos cropped from the owner's SRS Tapalpa 2026 calendar set; low resolution, about 900 px; full-size originals are probably on the assets branch of the `Website` repository).

## Decisions the owner made

- Dark, SailGP/race-series look; racing orange `#FF5F00`; deep teal-black base.
- Buttons solid orange (glass buttons were rejected).
- Typographic, broadcast-style info blocks (distance board, headline figures, slash-separated word runs) instead of boxed icon cards.
- SRS logo shown wherever possible; it is the highlight.
- Thumbnails: task map on cards, live race in round details.
- **Logo is final: Heritage (study direction No. 1)**: red triangle + blue square, lowercase wordmark with triangle dots on the i's. Live on every page, the favicon, the live-tracker top bar (tile) and the broadcast-view corner bug. The owner briefly picked Thermal/Pinwheel with a switch, then settled on Heritage; the switch was removed.

## Open items

- **Rounds section redesign (owner asked; next job).** Owner: "rounds page is too long, endless and samey; present it well and elegantly; ask designers". Today it is 26 identical cards with terrain task maps, 3-col grid under 11 month headings, ~5,100 px tall at 1440 (`src/season-calendar.html`, section `#rounds` ~line 610, renderer near `#months` ~line 1240). Three designers (broadcast, editorial, product) were asked separately and agreed:
  - one ruled typographic row per round (timing-board / race-schedule style), ~64–76 px at 1440; columns: month rail (sticky, replaces month headings) / R01 / big dates / flag bar + COUNTRY 26–28/800 caps with event name + slash run (place / days / type) / distance board (`81.8 KM · 4 TP`) / status (`IN 18 DAYS`) + arrow; whole row opens the existing modal;
  - cut the always-on terrain map from normal rows (main cause of "samey"); show it on hover only, or as a thin route-only line glyph (designer 1's idea; needs a route-only mode in `drawTaskMap`);
  - SRS rows taller (~112–152 px) with SRS mark, gradient rule, `ROUND 2 OF 5`, and a permanent task map or SRS photo;
  - next round = expanded strip with orange left rule, headline countdown and the only button (solid orange "Race details"); live round = same with pulsing dot + "Watch live"; completed rounds collapse into one "N completed / show" row;
  - filters → one sticky bar: type toggles with counts, region as a single dropdown, search on the right; header becomes left-aligned "All rounds" + live slash run `26 ROUNDS / 12 COUNTRIES / 5 SRS`;
  - 390 px: 3-line rows (~90 px), sticky month strip, type chips scroll inside their own strip; target total height ~2,600 px at 1440.
- **Live broadcast with real Task 3 of the latest SRS round (owner asked; not started).** The live tracker currently shows a simulated "SRS Slovenia 2027 Task 3". Owner wants it to run Task 3 of the latest held SRS event (check which one: probably SRS Tapalpa 2026, the owner's photo set). Find real task data (turnpoints, radii, start/goal, results, ideally tracklogs) on Airtribune or the SRS site; if no tracks are public, replay the real task geometry and real finishing order with simulated tracks, and say so on the page.
- Swap in full-resolution photos if the owner provides them or approves access to the `Website` repository.
- Feed and thumbnail pages still use the earlier styles.
- Known small issue fixed this chat: live tracker overflowed 5 px at 390 px (map hint and bottom controls); empty toast box showed in broadcast view.
