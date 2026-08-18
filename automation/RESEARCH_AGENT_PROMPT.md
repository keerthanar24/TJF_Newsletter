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
  specific date within the quarter window, and a 2–4 sentence factual
  summary with no embellishment.
- **If nothing genuine is found for a section, leave it empty.** Do not
  stretch dates, do not paraphrase an out-of-window event into looking
  current, and do not invent an item. An empty section in the output JSON
  (`"items": []`) is the correct, honest result — `render_magazine.py`
  renders it as a clean empty-note automatically.

## 1b. Geographic balance — ~80% India, ~20% overseas

Aim for roughly 80% of the issue's total items to be India-based and 20%
overseas/diaspora (see `config.py`'s `GEOGRAPHIC_SPLIT_RULE`). This is a
target across the whole issue, not a per-section quota, and it never
overrides the sourcing or scope rules — do not invent an overseas item to
hit the ratio, and do not drop a genuine India item to rebalance it.

## 2. Scope filter — spiritual and happening events only

Before including anything, ask: **is this a spiritual/devotional event
itself**, not just a story that happens to involve a Jain person,
organisation, or place?

- Include: diksha ceremonies, kalyanak observances, festivals/parva,
  chaturmas entries and programs, vihar/pilgrimage journeys, temple
  consecrations and renovations, tirth-related religious/security matters
  directly tied to the site's sanctity.
- Exclude: business launches, sports/franchise news, civic felicitation
  ceremonies, leadership awards, legal disputes, and any other story where
  the "Jain" connection is incidental rather than the substance of the
  event. (See `config.py`'s `SCOPE_RULE`.)

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

## 4. Cover image — exactly one, generated automatically

Produce (or select) exactly one cover-quality image depicting a real Jain
temple, tirth, or spiritual subject for this issue:

- If an image-generation tool is available and has credit/quota, generate
  one fresh image appropriate to the quarter's leading story or a general
  devotional/tirth scene.
- If generation is unavailable, fall back to the most recent previously-used
  cover image rather than leaving the cover blank or using a placeholder.
- Save it to `assets/cover.jpg` (or update `cover_image_path` in the
  content JSON to point at wherever it's saved) and write a real, literal
  `cover_image_alt` description of what's in the photo.

## 5. Write the content JSON

Populate a copy of `content_schema_example.json` for the quarter:
`issue` metadata (volume, edition, coverage dates, cover image path, 2–3
cover teaser headlines drawn from the strongest items), `editors_note`, and
`sections` — all 13 keys present, each either populated with real items or
`"items": []`.

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
