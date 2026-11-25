# Immersion review: season calendar (events/index.html), 25 Nov 2026

Owner: "the tour section is nice but there's no immersiveness"; "run the full page for an immersiveness check and find where, and which techniques, can make a big difference".

Reviewed from a full-page capture at 1440 px (7,900 px tall), section by section.

## What holds it back (whole page)

1. **Little photography, little sense of place.** Four photos in 7,900 px, all close-ups of gliders from one event (Tapalpa). Nothing shows a *place*: no take-off, valley, cloudbase, town or crowd. Immersion in SailGP comes from the venue (harbour, city skyline) as much as from the boats.
2. **Every section is a box on the same dark teal.** Centred heading, then content, then a hard edge, eight times. It reads as a brochure, not a journey. Nothing carries from one section into the next.
3. **Data sections stack up.** Strip → tour map → stats → gantt → 2,400 px rounds list: about 4,500 px of type on a flat background, with one photo break.
4. **Motion is decoration, not story.** The count-ups and the slow zoom don't move anything you care about. The one real story (a race unfolding) sits on another page (live.html).
5. **Everything stays inside the 1,320 px column.** Only the hero and the Gemona photo go edge to edge.

## Where, and which technique (ranked by impact)

| # | Where | Technique | Impact | Effort | Needs |
|---|---|---|---|---|---|
| 1 | Calendar strip (owner asked) | **Place photo on hover/open**, as on SailGP: the column fills with the venue (darkened so the type stays readable); the open column shows it full height | High | S | place photos |
| 2 | The tour | **Scroll-driven journey**: a sticky full-screen stage; scrolling moves stop by stop through the season (place photo crossfades, big city + dates + round count, small map in the corner draws the route so far); or, lighter, a **photo backdrop** that crossfades to the place under the hovered label | Very high | M–L | place photos |
| 3 | Hero | **Moving image**: a 6–10 s muted loop from the owner's footage (launch, gaggle, glide past the camera) instead of a still close-up; or the hero *is* the next round's place, full bleed | Very high | M | owner video |
| 4 | Rounds list | **Sticky image panel**: on the right, a large photo that follows the hovered/scrolled row (place, or race photo for SRS); **month breaks as thin full-bleed photo bands** instead of only type | High | M | place photos |
| 5 | Between sections | **Continuity**: photos fade into the page (done for the Gemona photo); headings left-aligned at the content edge; one section on a light ground for contrast (SailGP alternates) | Medium | S | – |
| 6 | Next round / hero card | **Live presence**: a small live map (or the Tapalpa replay, muted) of the next/last task inside the page, instead of a link out | High | M | reuse live.html code |
| 7 | SRS section | Its photo is almost invisible under the overlay. **Show it**: photo full bleed on one side, list on the other, or a slow sequence of the five round photos | Medium | S | – |
| 8 | Gemona feature | Already the strongest moment. **Move the card off the subject** (beside or below) and add a gentle depth shift on scroll (photo moves slower than the page) | Medium | S | – |
| 9 | Season at a glance | Least immersive part, and repeats the strip and the list. **Remove it or merge it** into the tour journey (the month scrubber) | Medium | S | – |
| 10 | Whole page | **Edge to edge where it matters** (strip, tour, photos), denser type only where data is | Medium | S | – |

All motion must stop for "reduce motion" and stay off the critical path (no layout shift, lazy-loaded images, under ~250 KB per photo).

## The blocker: place photos

Items 1, 2 and 4 need one landscape photo per venue or country (26 venues, 12 countries). Commons/Wikipedia rate-limit this container, and Unsplash search needs a key. Options, in order of fit: the owner's own Paragliding Atlas photos (Website repo, assets branch), an Unsplash API key, or links the owner picks.

## Suggested order

1 (strip hover) → 2 (tour journey, mockup first) → 4 (rounds panel) → 3 (hero loop, with batch 3 hero concepts). 5–10 are small and can ride along.
