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

- Dark, SailGP/race-series look; racing orange `#FF5F00`; deep teal-black base.
- Buttons solid orange (glass buttons were rejected).
- Typographic, broadcast-style info blocks (distance board, headline figures, slash-separated word runs) instead of boxed icon cards.
- SRS logo shown wherever possible; it is the highlight.
- Thumbnails: task map on cards, live race in round details.
- **Logo is final: Heritage (study direction No. 1)**: red triangle + blue square, lowercase wordmark with triangle dots on the i's. Live on every page, the favicon, the live-tracker top bar (tile) and the broadcast-view corner bug. The owner briefly picked Thermal/Pinwheel with a switch, then settled on Heritage; the switch was removed.


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
