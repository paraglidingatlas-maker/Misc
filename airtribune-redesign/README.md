# Airtribune redesign concept

An unofficial design concept for [airtribune.com](https://airtribune.com), the live-tracking and competition platform for paragliding. **Not affiliated with or endorsed by Airtribune.**

| Page | Path | Based on |
|---|---|---|
| Season calendar | [`events/`](events/) | airtribune.com/events/next |
| Live feed | [`feed/`](feed/) | airtribune.com/feed |
| Thumbnail study | [`thumbnails/`](thumbnails/) | Design options for the calendar cards |

Each page is a single self-contained HTML file. Open `index.html` in a browser, or serve the folder with any static host (for example GitHub Pages). Libraries (D3, TopoJSON, world outlines from Datamaps) and fonts load from public CDNs.

## Data

- Event names, dates and venues come from the public Airtribune listings (November 2026).
- Venue coordinates and time zones are approximate.
- Countdowns assume day 1 starts at 09:00 local time.
- Competition tasks, GPS tracks, barograms and race replays are **simulated** for the concept and are seeded per round, so each round always draws the same way.
