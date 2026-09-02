"""
Jain Magazine — standing configuration.

This file encodes every persistent requirement agreed on for this publication.
Nothing here should be edited per-issue — per-issue data goes in a separate
content JSON file (see content_schema_example.json). Change this file only
when the actual standing requirements change.
"""

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
MAGAZINE_TITLE = "Jain Magazine"
PUBLISHER_LINE = "A devotional publication compiled through AI curation of verified community portals, temple announcements, and recognised Jain news organisations — a sourced synthesis of spiritual community news across all sects."

# ---------------------------------------------------------------------------
# Cadence
# ---------------------------------------------------------------------------
CADENCE = "quarterly"  # one issue every 3 months
# Suggested quarter windows (adjust the year each cycle):
QUARTER_WINDOWS = [
    ("Q1", "01-01", "03-31"),
    ("Q2", "04-01", "06-30"),
    ("Q3", "07-01", "09-30"),
    ("Q4", "10-01", "12-31"),
]

# ---------------------------------------------------------------------------
# The 15 required sections, in required display order.
# Every issue's content JSON must include ALL 15 keys — a section with no
# genuine news for the period gets "items": [] and is omitted from the
# rendered output entirely (see render_magazine.py).
#
# These 15 are a COVERAGE CHECKLIST, not an exhaustive restriction on what
# may be reported: this is not a fixed format every issue must fit into.
# Genuine, sourced Jain community news that doesn't cleanly belong to one of
# the other 14 named categories can still be included — place it under
# "Other Community News / Announcements", the deliberate flexible catch-all.
# ---------------------------------------------------------------------------
SECTIONS = [
    "Global Jain Community News",
    "Top News",
    "New Diksha Announcements",
    "Tirthankar Kalyanak",
    "Jain Festivals / Parva",
    "Guru Maharaj Pravesh & Chaturmas Announcements",
    "New Temples & Tirth Renovation",
    "Jain Tirth News",
    "Jain Vihar",
    "Other Community News / Announcements",
    "Jain Leadership / Forums",
    "Jain Business & Trade",
    "Historical Data / Archaeological News",
    "Controversial Data",
    "Jain People Recognized Anywhere",
]
# Note: "Community News" (a section from the earlier 13-category version) was
# folded into "Global Jain Community News" (worldwide roundup) and "Other
# Community News / Announcements" (miscellaneous/catch-all) under the new
# 15-category structure — do not use the old "Community News" key.

# ---------------------------------------------------------------------------
# Scope: general Jain community / foundation news — NOT spiritual-only.
# This is a Jain Foundation publication, so its remit is the full breadth
# of genuine Jain community life: spiritual/devotional events (diksha,
# kalyanak, festivals, chaturmas, vihar, temple/tirth activity) AND civic,
# business/trade, leadership, and institutional news involving the Jain
# community. The only hard content restriction is CRUELTY_BLOCKLIST below
# (no violence/cruelty/harm) — everything else genuine and sourced is in
# scope for its matching section.
# ---------------------------------------------------------------------------
SCOPE_RULE = (
    "Content covers the full breadth of genuine Jain community news — "
    "spiritual/devotional events, civic and community life, business/trade, "
    "leadership, and institutional news. The only hard exclusion is content "
    "depicting cruelty, violence, or harm (see CRUELTY_BLOCKLIST); nothing "
    "is excluded merely for being civic, commercial, or leadership-related."
)

# ---------------------------------------------------------------------------
# Content restriction: nothing depicting cruelty, violence, or harm.
# This is a SECONDARY mechanical safety net — the primary filter is the
# research agent's own judgment (see RESEARCH_AGENT_PROMPT.md). Any item
# whose text matches these terms is flagged and excluded automatically
# rather than silently published; render_magazine.py refuses to render an
# item that trips this filter without an explicit override.
# ---------------------------------------------------------------------------
CRUELTY_BLOCKLIST = [
    "attack", "attacked", "mauled", "mauling", "killed by", "kills",
    "murder", "murdered", "assault", "assaulted", "violence", "violent",
    "cruelty", "abuse", "abused", "wildlife attack", "animal attack",
    "lion attack", "gore", "gored", "stabbed", "shooting", "shot dead",
    "beaten", "lynch", "riot", "bloodshed", "poaching", "poached",
]
# Note: this list intentionally does NOT include words like "death",
# "samadhi", "sallekhana", or "passed away" — voluntary religious death
# observances (e.g. a Sallekhana/Samadhi Marana obituary) are legitimate
# spiritual content and must not be auto-excluded by this filter.

# ---------------------------------------------------------------------------
# Sourcing policy
# ---------------------------------------------------------------------------
SOURCING_POLICY = (
    "Only real, live-researched, dated, and attributed news, drawn from "
    "trusted sources. Never fabricate an item to fill a section. If "
    "genuinely no verifiable news exists for a section in the period, "
    "render that section as honestly empty. Every item must carry an "
    "outlet name and a date, and the item's real source URL should be "
    "captured in its 'url' field whenever the research step has it, so "
    "readers can click through to the full original article — never invent "
    "a URL if the real one wasn't captured; omit the field instead. When a "
    "real image accompanying the story is found (from the article, or the "
    "outlet's/organiser's own Facebook/Instagram post), capture its URL in "
    "the item's 'image_url' field, shown as a link beneath the source line "
    "— never invent or substitute a generic/stock image link."
)

# ---------------------------------------------------------------------------
# Item count: no artificial cap. As many genuine, sourced items as are
# actually found for a period should be included — never trimmed down for
# length or a target item-per-section count. (The renderer's page-packing
# logic handles however many items result; it does not impose a limit.)
# ---------------------------------------------------------------------------
NO_ITEM_CAP = True

# Preferred/trusted outlet families. Not an exhaustive allowlist — the
# research step should favor these when available, and treat any other
# outlet as needing corroboration (a second independent source, or a
# direct primary source such as an official temple/organisation site)
# before an item is included.
#
# Hindi-language regional outlets, and Facebook/Instagram posts FROM NAMED,
# IDENTIFIABLE Jain organisations/Sanghs/temples (not anonymous accounts),
# are a PRIMARY source tier here — not a fallback — because a large share of
# genuine, on-the-ground Jain community news (local Chaturmas, vihar,
# temple events) is only ever covered by these, never by national English
# outlets. Individual Sangh/community-published newsletters are likewise a
# primary source: many Jain communities already publish their own regular
# newsletters, and these often carry local news that never reaches
# mainstream coverage at all.
TRUSTED_SOURCE_TIERS = {
    "national_news": [
        "The Times of India", "Hindustan Times", "The Hindu", "Indian Express",
        "Free Press Journal", "ANI", "PTI", "The Tribune",
    ],
    "hindi_regional_news": [
        "Patrika", "Amar Ujala", "Dainik Bhaskar", "Gujarat Samachar",
        "Haribhoomi", "Prabhat Khabar", "Rajasthan Patrika", "Jagran",
        "Pratahkal", "Paliwalwani", "Amar Bharti", "Lalluram", "ASR24 News",
        "Daily Hindi Milap",
    ],
    "diaspora_community": [
        "Eastern Eye", "American Bazaar", "New India Abroad", "YJA (Young Jains of America)",
    ],
    "jain_institutional_primary": [
        "JITO (official chapters)", "Jain Vishva Bharati", "official temple/trust press releases",
        "recognised Jain panchang/calendar publishers (e.g. Samyakdarshan, Sus Jain Mandir)",
        "individual Sangh/community-published newsletters",
    ],
    "social_media_primary": [
        "Facebook posts from named, identifiable Jain temples/Sanghs/organisations",
        "Instagram posts from named, identifiable Jain temples/Sanghs/organisations",
    ],
}
SOURCING_TIER_RULE = (
    "A single-outlet item from a regional, community-newsletter, or "
    "identifiable social-media source is publishable but must be marked "
    "with a confidence note internally for editorial review. What's still "
    "excluded: anonymous/unidentifiable social accounts, unverified blogs, "
    "and aggregator sites with no named, traceable outlet or organisation "
    "behind them."
)

# ---------------------------------------------------------------------------
# Geographic balance: ~80% India-based news, ~20% overseas.
# Applied across the issue as a whole, not necessarily per-section — some
# sections (e.g. New Diksha) may be entirely India-based some quarters,
# while diaspora-heavy sections (e.g. Jain Leadership/Forums) may skew
# overseas. Target the 80/20 split across all filled items in the issue.
# ---------------------------------------------------------------------------
GEOGRAPHIC_SPLIT = {
    "india_target_pct": 80,
    "overseas_target_pct": 20,
}
GEOGRAPHIC_SPLIT_RULE = (
    "Aim for roughly 80% of the issue's items to be India-based and 20% "
    "overseas/diaspora, counted across the whole issue. This is a target, "
    "not a hard quota — never invent an overseas item just to hit the "
    "ratio, and never drop a genuine India item to rebalance. If overseas "
    "spiritual news is thin for a quarter, the split can lean more India-"
    "heavy; the sourcing and scope rules always take priority over the ratio."
)
GEOGRAPHIC_SPLIT_MINIMUM_PCT = 15  # hard floor, distinct from the 20% target above

# ---------------------------------------------------------------------------
# "Controversial Data" — the one section that needs deliberate, careful
# handling rather than the default "include everything genuine" approach.
# ---------------------------------------------------------------------------
CONTROVERSIAL_DATA_POLICY = (
    "This section covers sensitive/debated topics within or touching the "
    "Jain community (e.g. sectarian disputes, contested religious-site "
    "access, public policy disagreements) — genuinely newsworthy, but "
    "requiring more care than other sections: (1) still subject to the "
    "cruelty/violence exclusion like everything else; (2) state the dispute "
    "factually and describe each side's stated position without the "
    "magazine itself taking a side; (3) prefer stories with substantive "
    "community/religious stakes over minor personal disputes; (4) when a "
    "story's facts are genuinely contested or unclear between sources, say "
    "so explicitly rather than presenting one version as settled fact."
)

# ---------------------------------------------------------------------------
# "Historical Data / Archaeological News" — findings, discoveries, and
# research about Jain history/archaeology reported within the coverage
# window (a NEW archaeological finding, a newly published research result,
# a heritage-site development) — not a general Jain-history reference
# section. If nothing new was reported in the window, it stays empty like
# any other section; do not fill it with static historical background.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Output format: a print-ready MAGAZINE, not an email/newsletter layout.
# ---------------------------------------------------------------------------
PAGE_SIZE = {"width_in": 8.5, "height_in": 11}  # US Letter; swap for A4 if needed
HAS_COVER_PAGE = True          # full-bleed cover image + masthead, not a plain header
HAS_TABLE_OF_CONTENTS = True   # a real magazine has a contents page
HAS_BACK_COVER = True

# ---------------------------------------------------------------------------
# Cover image
# ---------------------------------------------------------------------------
COVER_IMAGE_POLICY = (
    "Exactly one cover image per issue, chosen automatically as part of the "
    "quarterly run, in this priority order: (1) a freshly generated image "
    "tied to that quarter's leading story, if an image-generation tool is "
    "available and has quota; (2) otherwise, the next photo from the "
    "rotation pool in assets/covers/ (see cover_picker.py) — a deliberately "
    "different photo than the last few issues used, not a repeat; "
    "(3) never a placeholder or fabricated image. It must always depict a "
    "real Jain temple/tirth/spiritual subject — never text, logos, or "
    "unrelated imagery."
)
COVER_ROTATION_NOTE = (
    "The rotation pool currently holds only one real photo (Girnar/"
    "Shatrunjaya), so every issue reuses it until more real photos are "
    "added to assets/covers/ — cover_picker.py reports this honestly "
    "rather than silently faking variety. Add more real photos to the pool "
    "over time to make the rotation meaningful."
)
