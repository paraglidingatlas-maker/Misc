# Working rules for this repository

## Switch to a new chat before a chat gets long and expensive

Long chats re-send everything said so far on every turn, so cost grows with length. Hand over to a fresh chat as soon as **any** of these is true:

- the conversation has been summarised or compacted once;
- about 30 back-and-forth turns of heavy work (screenshots, builds, publishing) have happened;
- you are about to start a new, separate piece of work in a chat that is already long;
- you notice yourself re-reading files or images you already looked at earlier in the chat.

How to hand over (do all of it, in this order):

1. Finish or cleanly stop the current step. Commit and push everything to `main`, including sources, not only built pages.
2. Update `docs/handover.md`: what was done, live links, where the sources are and how to rebuild, open items, decisions the owner made, and any background work still running.
3. Start the new chat with the `create_session` tool, in the same environment, with this repository as the source and a first message telling it to read `CLAUDE.md` and `docs/handover.md` and then wait for the owner.
   Title it **"Airtribune redesign & updates N"**, where N is one more than this chat's number (owner, 27 Nov 2026).
   This chat's number is in its own title (`get_session`); chats 1–18 run from 23 to 27 Nov 2026, 18 being the one that
   set this rule. Side chats for this project get the next number too.
   Give it the tag `airtribune` (`tags` on `create_session`); all chats 1–18 carry it.
4. Give the owner the new chat's link in one line, then stop doing work in the old chat.

Do not wait to be asked. Say in one line that you are switching and why.

## Project conventions (Airtribune redesign concept)

- The owner is **officially hired by Airtribune** for this project (owner, 25 Nov 2026): no "concept / not affiliated" banner or footer wording. Keep factual notes where data is illustrative (feed, thumbnail study).
- Photos are by Aninder Singh / Paragliding Atlas (SRS Tapalpa 2026): always credit them. SRS logo © Sports-Class Racing Series.
- Event place photos (`events/img/places/<airtribune-slug>.jpg`) are the organisers' own uploads on each Airtribune event page; the owner approved using them (25 Nov 2026). Picks and sources: `events/img/places/SOURCES.json`.
- Buttons are **solid orange** (`#FF5F00`, white text). Do not make them translucent or glassy; the owner rejected that. Cards may be frosted glass.
- Layout references the owner likes: SailGP (sailgp.com) event and calendar pages; typographic, broadcast-style information instead of boxed cards with icons.
- Check every page at 1440 px and 390 px wide with Playwright before pushing; no console errors, no horizontal scroll.
- Public site: https://paraglidingatlas-maker.github.io/Misc/airtribune-redesign/ (GitHub Pages from `main`; note the capital M in `Misc`).
