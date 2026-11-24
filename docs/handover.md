# Handover: Airtribune redesign concept

Last updated 24 Nov 2026 by the chat "Rounds redesign + real Task 3" (follows "Airtribune logo rollout").

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

- **Done this chat:** Rounds section redesigned to the agreed brief (ruled timing-board rows, sticky month rail, SRS rows with photo + route glyph, next-round strip with the only orange button, completed-rounds fold row, one filter bar with region dropdown; ~2,450 px at 1440). Renderer: `/* ROUNDS: timing-board rows */` in `src/season-calendar.html`.
- **Done this chat:** live tracker replays the REAL SRS Tapalpa 2026 (Airtribune srs-2026-6) Task 3, task 6991, 10 Nov 2026, 58.7 km: official task, results, top-20 IGC tracks. Data + scripts + SOURCES.md in `src/data/srs-task3/` (`embed_task3.py` writes data into live-tracker.html; run before `build_pages.py`).
- **Done this chat:** photo credits made thin/subtle everywhere (300 italic 11px, 45% white, "© Aninder Singh · Paragliding Atlas"); full credit line stays in footers.
- **NEXT JOB (owner asked): event pages look empty → import data from civlcomps.org, British Winter Open first, then the rest.** Owner first wanted to know which events exist there; list given (below), awaiting go-ahead. civlcomps.org is reachable (list pages render via JS; use Playwright; search URL `https://civlcomps.org/events?search%5Bdates%5D=&search%5Bq%5D=<q>`). Ambiguity to confirm with owner: "event pages" = round details drawer on the calendar (non-SRS rounds have no own page) or new per-event pages like the SRS ones (`build_srs.py`).
  Found on CIVL (slug after civlcomps.org/event/): R03 `4%C2%AA-etapa-gaucho-de-parapente-2026-sapiranga-rs`; R04 `porterville-paragliding-open-2026-south-africa-pwc`; R06 `primera-valida-nacional-open-roldanillo-2027`; R07 `copa-niviuk-2027-iv-edition`; R09 `copa-de-las-americas-roldanillo-2027`; R10 `2nd-cup-dedalo-s-piedechinche-2027`; R11 `brigth-open-2027`; R12 `corryong-pg-open-2027`; R15 `andes-tour-hike-and-fly-2026` (2026 edition, check); R16 `vipava-valley-open-2027`; R17 `corryong-sports-cup-2027` (+ duplicate `...20272`). Possibly: R02 Encantado = `iii-etapa-do-campeonato-gaucho-de-parapente` (check).
  Not found: R01 Punjab Cup, R05 Apía, R08 Manilla, R13 **8th British Winter Open** (only 3rd–7th editions exist: `7th-british-winter-open` etc.; past ones can supply venue/format/history), R14 Costa Rica, R18/R22/R24/R25/R26 SRS 2027 rounds (past SRS editions exist e.g. `srs-naviter-edition-2026-tolmin-slovenia`), R19 Glencoe, R20 X-Scotia, R21 11th Naviter Open (7th 2023 latest listed), R23 Chabre.
- Swap in full-resolution photos if the owner provides them or approves access to the `Website` repository.
- Feed and thumbnail pages still use the earlier styles.
- Known small issue fixed this chat: live tracker overflowed 5 px at 390 px (map hint and bottom controls); empty toast box showed in broadcast view.
