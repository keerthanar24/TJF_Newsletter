# Jain Magazine — Quarterly Research & Production Instructions

This is the standing prompt an AI agent (Claude, run manually or via a
scheduled quarterly trigger) follows every cycle to produce one issue.
`render_magazine.py` only lays out and prints what this step hands it — it
does no research and makes no editorial judgment calls itself.

## 1. Research — real news only, trusted sources only

Research genuine, live news for the quarter's date window across all 13
required sections (listed in `config.py`, `SECTIONS`). For each section:

- Search multiple angles: English and Hindi/Devanagari queries, outlet-
  specific searches, lineage-specific searches (Terapanth, Sthanakvasi,
  Digambar, Shwetambar Murtipujak, etc.), and regional portals.
- Prefer the outlets listed in `config.py`'s `TRUSTED_SOURCE_TIERS`. A
  single-outlet item from a smaller regional source is usable but should be
  corroborated with a second source where possible before inclusion.
- Never use unattributed blogs, anonymous aggregators, or unverified social
  posts as a sole source.
- Every item must have: a real headline, location, source outlet name, a
  specific date within the quarter window, and — whenever you have it — the
  article's real **`url`**, so readers can click through and read it in
  full. Never invent a URL; if the real one wasn't captured, omit the `url`
  field for that item rather than guessing or reusing another item's link.
- **Do not artificially shorten the news.** Write as much genuine factual
  detail as the source actually supports — full context, names, figures,
  quotes if reported, background — not a minimal 2-4 sentence blurb. A
  thin one-line source only supports a short item; a well-covered story
  should get a correspondingly full write-up. Never pad with invented
  detail to make an item look longer than the source supports, either —
  length should track how much the source actually said, in both
  directions.
- **Cover more ground, not just longer entries.** Where multiple genuine,
  distinct items exist for a category within the window, include all of
  them rather than picking just one or two representative examples.
- **If nothing genuine is found for a section, leave it empty.** Do not
  stretch dates, do not paraphrase an out-of-window event into looking
  current, and do not invent an item. An empty section in the output JSON
  (`"items": []`) is the correct, honest result — `render_magazine.py`
  omits that section entirely from the rendered output (no header, no
  placeholder text).
- The 13 sections are a coverage checklist, not an exhaustive limit — real,
  sourced Jain community news that doesn't fit one of the other 12 named
  categories can still go under "Other Community News / Announcements",
  the deliberate flexible catch-all.

## 1b. Geographic balance — ~80% India, ~20% overseas

Aim for roughly 80% of the issue's total items to be India-based and 20%
overseas/diaspora (see `config.py`'s `GEOGRAPHIC_SPLIT_RULE`). This is a
target across the whole issue, not a per-section quota, and it never
overrides the sourcing or scope rules — do not invent an overseas item to
hit the ratio, and do not drop a genuine India item to rebalance it.

## 2. Scope — general Jain community / foundation news

This is a Jain Foundation publication, not a spiritual-only newsletter.
Scope is the full breadth of genuine Jain community life:

- Spiritual/devotional: diksha ceremonies, kalyanak observances,
  festivals/parva, chaturmas entries and programs, vihar/pilgrimage
  journeys, temple consecrations and renovations, tirth news.
- Civic and community life, business/trade (e.g. JITO chapter launches and
  events), leadership (awards, appointments, forums), and institutional
  news (foundations, educational programs) — all in scope for their
  matching section (see `config.py`'s `SECTIONS`).

The only hard exclusion is content depicting cruelty, violence, or harm
(see step 3 and `config.py`'s `SCOPE_RULE`/`CRUELTY_BLOCKLIST`). Nothing is
excluded merely for being civic, commercial, or leadership-related.

## 3. Content restriction — no cruelty or violence

Do not include anything depicting attacks, violence, cruelty, or harm —
including wildlife/animal-attack stories — even if it occurred at or near a
tirth or temple. This applies regardless of how newsworthy the story is.

This is a judgment call you make during research, not just a keyword
filter — `render_magazine.py`'s `CRUELTY_BLOCKLIST` is a mechanical
second check, not the primary gate. Use editorial judgment first.

Note the one deliberate exception: voluntary religious death observances
(Sallekhana / Samadhi Marana) are legitimate spiritual content and should
be included when genuinely reported — they are not "cruelty."

## 4. Cover image — exactly one, different from last time when possible

Produce (or select) exactly one cover-quality image depicting a real Jain
temple, tirth, or spiritual subject for this issue, in this priority order:

1. **Generate fresh, if possible.** If an image-generation tool is
   available and has credit/quota, generate one image appropriate to the
   quarter's leading story or a general devotional/tirth scene. Add it to
   `assets/covers/` (a real, literal filename) so it joins the rotation
   pool for future issues too.
2. **Otherwise, rotate.** Run `python3 cover_picker.py` — it deterministically
   returns the least-recently-used real photo from `assets/covers/`, so the
   cover is deliberately different from the last few issues rather than a
   repeat. (With only one photo currently in the pool, it will say so and
   return that same photo — that's expected until more real photos are
   added, not a bug.)
3. **Never** leave the cover blank or use a placeholder/fabricated image.

Set `cover_image_path` in the content JSON to whichever photo was chosen,
write a real, literal `cover_image_alt` description of what's in it, and
after rendering, run `python3 cover_picker.py --record <filename>` so the
rotation history reflects this issue's choice for next quarter.

## 5. Write the content JSON

Populate a copy of `content_schema_example.json` for the quarter: `issue`
metadata (volume — reuse the same volume number as the most recent past
issue in `issues/`, don't increment it just because a new quarter ran;
edition, coverage dates, cover image path, 2–3 cover teaser headlines drawn
from the strongest items) and `sections` — all 13 keys present, each either
populated with real items (each with `url` when available, see step 1) or
`"items": []`.

`editors_note` is optional internal record-keeping only — it is NOT
rendered in the magazine (no Editor's Note page is produced). Fill it in or
leave it blank as you prefer; it has no reader-facing effect.

Do not include a visible confidence/caveat line in `headline` or `body` —
if you want to track sourcing confidence for internal review, put it in an
underscore-prefixed field like `_confidence_internal` (see the example
file); `render_magazine.py` never prints underscore-prefixed fields.

## 6. Render

```bash
python3 render_magazine.py path/to/issue_Q3_2026.json path/to/JainMagazine_Q3_2026.pdf
```

The script validates that all 13 sections are present, runs the mechanical
cruelty-filter safety net, embeds the cover image, and produces a print-
ready magazine PDF (full-bleed cover, table of contents, editor's note,
article pages, back cover) — not a newsletter/email layout.

## 7. Next cycle

Three months later, repeat with the next quarter's window (see
`QUARTER_WINDOWS` in `config.py`). Nothing in this process changes issue to
issue except the researched content and the cover image.
