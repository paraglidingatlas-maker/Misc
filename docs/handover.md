# Handover: Airtribune redesign concept

Last updated 24 Nov 2026 by the chat "Airtribune standards upgrade".

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
- SRS pages: `python3 src/build/build_srs.py src/data/srs-events src/build/helpers.js <out-dir>` writes `<out-dir>/srs/*.html`; use `airtribune-redesign/events` as `<out-dir>`. Event copy, travel facts and schedules are in the `C`, `TRAVEL2` and `EVENTS` dicts in `build_srs.py`; scraped official data is in `src/data/srs-events/`.
- Images: `events/img/` (photos cropped from the owner's SRS Tapalpa 2026 calendar set; low resolution, about 900 px; full-size originals are probably on the assets branch of the `Website` repository).

## Decisions the owner made

- Dark, SailGP/race-series look; racing orange `#FF5F00`; deep teal-black base.
- Buttons solid orange (glass buttons were rejected).
- Typographic, broadcast-style info blocks (distance board, headline figures, slash-separated word runs) instead of boxed icon cards.
- SRS logo shown wherever possible; it is the highlight.
- Thumbnails: task map on cards, live race in round details.

## Open items

- Logo: the study page has four directions plus three independent designer takes (marks in `airtribune-redesign/logo/designers/1-3/`). All three designers agreed: keep the triangle, one orange, heavy italic uppercase wordmark. Strongest candidates: Pinwheel / Thermal (same idea reached twice) and Apex. The owner has not chosen yet; next step is to refine the chosen mark and roll it into the site nav, favicon and live-tracker bug.
- Swap in full-resolution photos if the owner provides them or approves access to the `Website` repository.
- Feed and thumbnail pages still use the earlier styles.
