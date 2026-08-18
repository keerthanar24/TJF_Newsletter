# Jain Magazine — Quarterly Automated Production Pipeline

Code that encodes every standing requirement for this publication, so each
quarterly issue is produced the same, correct way instead of being
re-specified from scratch each time.

## What's in here

| File | Purpose |
|---|---|
| `config.py` | Every standing requirement as code: the 13 required sections, the spiritual/happening-events-only scope rule, the cruelty/violence blocklist, the trusted-source tiers, the 80/20 India-overseas target, quarterly cadence, print-magazine format flags, title ("Jain Magazine"). |
| `RESEARCH_AGENT_PROMPT.md` | The standing instructions an AI agent follows each quarter to research real news, apply the scope/cruelty/sourcing rules, generate the cover image, and write the content JSON. This is the part that genuinely requires an LLM — a plain script cannot judge what's "real," "spiritual," or "not cruel." |
| `content_schema_example.json` | The empty-form schema for one issue's data — all 13 sections, issue metadata, cover image. |
| `demo_issue.json` | A filled-in example (the actual Aug 3–18, 2026 researched content), used to prove the pipeline works. |
| `render_magazine.py` | The deterministic part: turns a content JSON into a print-ready magazine PDF — full-bleed cover, table of contents, editor's note, article pages, back cover. Runs a mechanical cruelty-filter safety net and validates all 13 sections are present before rendering. |
| `assets/cover.jpg` | Demo cover image (reused from the Girnar/Shatrunjaya photo). |

## How one issue gets produced

```
                 ┌─────────────────────────────┐
                 │  RESEARCH_AGENT_PROMPT.md    │   ← run by an LLM/agent
                 │  (live web research,          │      each quarter
                 │   scope + cruelty + source     │
                 │   judgment, cover image)       │
                 └───────────────┬───────────────┘
                                 │ writes
                                 ▼
                 ┌─────────────────────────────┐
                 │  issue_Q_YYYY.json            │   ← per-issue content
                 │  (matches content_schema)      │
                 └───────────────┬───────────────┘
                                 │ python3 render_magazine.py
                                 ▼
                 ┌─────────────────────────────┐
                 │  JainMagazine_QX_YYYY.pdf     │   ← print-ready output
                 └─────────────────────────────┘
```

`render_magazine.py` never invents content and never decides what counts as
spiritual — that judgment is entirely in the research step. The script's
only content-safety role is a mechanical second check (the cruelty
blocklist) that stops a bad item from reaching print even if the research
step missed it.

## Running it yourself

```bash
cd automation
python3 render_magazine.py demo_issue.json JainMagazine_Demo.pdf
```

Requires `assets/cover.jpg` to exist (or whatever path `cover_image_path`
in the JSON points to) and a Chrome/Chromium binary on the machine
(auto-detected, or pass `--chrome /path/to/chrome`).

## Print-magazine format, not a newsletter

This deliberately differs from the earlier newsletter-style layout:

- **Full-bleed cover** with a hero image, masthead, coverage dates, and 2–3
  cover-teaser headlines — like a real print magazine cover, not a header.
- **Table of contents** page listing all 13 sections.
- **Packed article pages** — multiple sections share a physical page when
  they're short (instead of every section, including empty ones, wasting
  a nearly-blank page — this was tuned specifically to avoid the "gaps"
  problem from earlier drafts of this project).
- **Back cover** with the publisher line and copyright.

## Setting up true quarterly automation

This repo is the *code*; making it actually fire every quarter without a
human re-prompting it requires wiring `RESEARCH_AGENT_PROMPT.md` up to a
scheduled trigger (a quarterly cron) that starts a Claude Code session,
has it follow the prompt, and run `render_magazine.py` at the end. That's
a live, standing automation (it will run on its own, unattended, every
three months) — worth setting up deliberately rather than silently, so
it's a separate step from delivering this code. Say the word and it can be
wired up.

## Known limitation

Image generation is referenced in `RESEARCH_AGENT_PROMPT.md` (step 4) but
this codebase does not itself call an image-generation API — that also
happens inside the quarterly agent run, using whatever image-generation
tool is available in that session at the time (with a documented fallback
to reusing the previous cover if generation is unavailable, e.g. no
credits). `demo_issue.json` uses a previously-supplied real photo to prove
the rendering pipeline, not a freshly generated one.
