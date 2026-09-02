# Jain Magazine — Research & Production Instructions

This is the standing prompt an AI agent (Claude, run manually or via a
scheduled trigger) follows every cycle to produce one issue.
`render_magazine.py` only lays out and prints what this step hands it — it
does no research and makes no editorial judgment calls itself.

## 1. Research — real news only, trusted sources only

Research genuine, live news for the period's date window across all 15
required sections (listed in `config.py`, `SECTIONS`). For each section:

- Search multiple angles: English and Hindi/Devanagari queries, outlet-
  specific searches, lineage-specific searches (Terapanth, Sthanakvasi,
  Digambar, Shwetambar Murtipujak, etc.), regional portals, and — per
  `config.py`'s `TRUSTED_SOURCE_TIERS` — Facebook/Instagram posts from
  named, identifiable Jain temples/Sanghs/organisations, and individual
  Sangh/community-published newsletters. These social and community-
  newsletter sources are PRIMARY here, not a fallback: a large share of
  genuine local Jain news (Chaturmas, vihar, temple events) never reaches
  national English coverage at all, and Hindi-language regional outlets and
  these community channels are often the only place it's reported.
- A single-outlet item from a regional, community-newsletter, or
  identifiable social-media source is publishable (mark it for internal
  confidence tracking per step 5's `_confidence_internal` convention).
  What's still excluded: anonymous/unidentifiable social accounts,
  unverified blogs, and aggregator sites with no named, traceable source.
- Every item must have: a real headline, location, source outlet name, a
  specific date within the window, and — whenever you have it — the
  article's real **`url`** (so readers can click through and read it in
  full) and **`image_url`** (a real image from the article or the
  organisation's own social post, shown as a link beneath the source
  line). Never invent either URL; if the real one wasn't captured, omit
  that field for the item rather than guessing or reusing another item's
  link.
- **Do not artificially shorten the news, and do not cap how much you
  include.** Write as much genuine factual detail as the source actually
  supports — full context, names, figures, quotes if reported, background
  — not a minimal blurb. A thin one-line source only supports a short
  item; a well-covered story should get a correspondingly full write-up.
  Never pad with invented detail to make an item look longer than the
  source supports, either — length should track how much the source
  actually said, in both directions. Where multiple genuine, distinct
  items exist for a category within the window, include ALL of them
  rather than picking one or two representative examples — there is no
  target item count per section or per issue.
- **If nothing genuine is found for a section, leave it empty.** Do not
  stretch dates, do not paraphrase an out-of-window event into looking
  current, and do not invent an item. An empty section in the output JSON
  (`"items": []`) is the correct, honest result — `render_magazine.py`
  omits that section entirely from the rendered output (no header, no
  placeholder text).
- The 15 sections are a coverage checklist, not an exhaustive limit — real,
  sourced Jain community news that doesn't fit one of the other 14 named
  categories can still go under "Other Community News / Announcements",
  the deliberate flexible catch-all.
- "Global Jain Community News" (a worldwide roundup) and "Other Community
  News / Announcements" (miscellaneous/catch-all) are two DIFFERENT
  sections — don't merge them or use the old "Community News" key from
  earlier versions of this pipeline.
- "Historical Data / Archaeological News" covers NEW findings/discoveries/
  published research reported within the window — not general historical
  background. If nothing new was reported, it stays empty.
- "Controversial Data" needs extra care — see `config.py`'s
  `CONTROVERSIAL_DATA_POLICY`: state disputes factually, describe each
  side's position without the magazine taking a side, still subject to the
  cruelty/violence exclusion (step 3), and say explicitly when facts are
  genuinely contested between sources rather than presenting one version
  as settled.

## 1b. Geographic balance — ~80% India, ~20%+ overseas (15% hard floor)

Aim for roughly 80% of the issue's total items to be India-based and 20%
overseas/diaspora (see `config.py`'s `GEOGRAPHIC_SPLIT_RULE`), with 15% as
a hard floor (`GEOGRAPHIC_SPLIT_MINIMUM_PCT`) — search deliberately for
overseas/diaspora items if the count is running low, rather than treating
20% as a soft aspiration only. This is a target across the whole issue,
not a per-section quota, and it never overrides the sourcing or scope
rules — do not invent an overseas item to hit the ratio, and do not drop a
genuine India item to rebalance it.

## 2. Scope — general Jain community / foundation news

This is a Jain Foundation publication, not a spiritual-only newsletter.
Scope is the full breadth of genuine Jain community life:

- Spiritual/devotional: diksha ceremonies, kalyanak observances,
  festivals/parva, chaturmas entries and programs, vihar/pilgrimage
  journeys, temple consecrations and renovations, tirth news.
- Civic and community life, business/trade (e.g. JITO chapter launches and
  events), leadership (awards, appointments, forums), institutional news,
  historical/archaeological findings, notable recognitions of Jain
  individuals anywhere in the world, and genuinely newsworthy controversial/
  disputed topics (handled per step 1's `Controversial Data` note) — all in
  scope for their matching section (see `config.py`'s `SECTIONS`).

The only hard exclusion is content depicting cruelty, violence, or harm
(see step 3 and `config.py`'s `SCOPE_RULE`/`CRUELTY_BLOCKLIST`). Nothing is
excluded merely for being civic, commercial, leadership-related, or
sensitive/controversial in subject matter.

## 3. Content restriction — no cruelty or violence

Do not include anything depicting attacks, violence, cruelty, or harm —
including wildlife/animal-attack stories and anything touching poaching/
animal harm, even tangentially — even if it occurred at or near a tirth or
temple, and even for the Controversial Data section. This applies
regardless of how newsworthy the story is.

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
   period's leading story or a general devotional/tirth scene. Add it to
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
rotation history reflects this issue's choice for next time.

## 5. Write the content JSON

Populate a copy of `content_schema_example.json` for the period: `issue`
metadata (volume — reuse the same volume number as the most recent past
issue in `issues/`, don't increment it just because a new period ran;
edition, coverage dates, cover image path, 2–3 cover teaser headlines drawn
from the strongest items) and `sections` — all 15 keys present, each either
populated with real items (each with `url` and `image_url` when available,
see step 1) or `"items": []`.

`editors_note` is optional internal record-keeping only — it is NOT
rendered in the magazine (no Editor's Note page is produced). Fill it in or
leave it blank as you prefer; it has no reader-facing effect.

Do not include a visible confidence/caveat line in `headline` or `body` —
if you want to track sourcing confidence for internal review, put it in an
underscore-prefixed field like `_confidence_internal` (see the example
file); `render_magazine.py` never prints underscore-prefixed fields.

## 6. Render

```bash
python3 render_magazine.py path/to/issue.json path/to/JainMagazine_issue.pdf
```

For a Word doc instead (or as well):

```bash
cd docx_build && npm install && node build_from_json.js ../path/to/issue.json ../path/to/JainMagazine_issue.docx
```

The script validates that all 15 sections are present, runs the mechanical
cruelty-filter safety net, embeds the cover image (PDF only), and produces
a print-ready magazine (full-bleed cover, table of contents, article
pages, back cover) — not a newsletter/email layout. There is no Editor's
Note page in the rendered output.

## 7. Next cycle

Repeat with the next period's window (quarterly: see `QUARTER_WINDOWS` in
`config.py`; bi-weekly or monthly: use the appropriate date range for that
run). Nothing in this process changes cycle to cycle except the researched
content and the cover image.
