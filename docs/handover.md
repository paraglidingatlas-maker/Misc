# Handover: Airtribune redesign concept

Last updated 24 Nov 2026 by the chat "BWO import" (after "Rounds redesign + real Task 3") (follows "Airtribune logo rollout").

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

- **No repeated photos across the site** (24 Nov 2026): each photo is used in one place only. Calendar: orange-pod (hero), pink-forest (SRS section), pod-closeup (feature). Event heroes: Lijak pink-blur, Montclar white-blur, Gemona orange-blur, Krushevo pink-close, St André coral-terraces, BWO gin-field. Other blocks on event pages (venue card, 01/02/03 cards, season rail) are typographic. New pages need new photos (ask the owner).

- Dark, SailGP/race-series look; racing orange `#FF5F00`; deep teal-black base.
- Buttons solid orange (glass buttons were rejected).
- Typographic, broadcast-style info blocks (distance board, headline figures, slash-separated word runs) instead of boxed icon cards.
- SRS logo shown wherever possible; it is the highlight.
- Thumbnails: task map on cards, live race in round details.
- **Logo is final: Heritage (study direction No. 1)**: red triangle + blue square, lowercase wordmark with triangle dots on the i's. Live on every page, the favicon, the live-tracker top bar (tile) and the broadcast-view corner bug. The owner briefly picked Thermal/Pinwheel with a switch, then settled on Heritage; the switch was removed.

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
