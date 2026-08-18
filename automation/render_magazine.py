#!/usr/bin/env python3
"""
Jain Magazine — print-format renderer.

Turns a per-issue content JSON (see content_schema_example.json) into a
print-ready magazine PDF: full-bleed cover, table of contents, editor's
note, article pages grouped by the 13 standing sections, and a back cover.

This script is deliberately "dumb" about content — it does NOT research
news or judge what is spiritual/appropriate. That judgment happens in the
quarterly research step (an LLM/agent run — see RESEARCH_AGENT_PROMPT.md)
BEFORE this script ever runs. This script's only content-safety job is a
mechanical second check: it refuses to render any item whose text matches
the CRUELTY_BLOCKLIST in config.py, so a bad item can't slip through into
print even if the research step missed it.

Usage:
    python3 render_magazine.py content.json output.pdf [--chrome PATH]
"""

import argparse
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

import config as cfg


# ---------------------------------------------------------------------------
# Content safety net
# ---------------------------------------------------------------------------
def item_is_blocked(item: dict) -> str | None:
    """Return the matched blocklist term if this item should be excluded, else None.

    Uses whole-word/phrase boundary matching (\\b...\\b), not plain substring
    containment — a naive `term in text` check would false-positive on things
    like "riot" inside "patriotism" or "gore" inside "category".

    Also guards against negated mentions: "non-violence" / "nonviolence" /
    "without violence" contain the word "violence" but mean the opposite —
    ahimsa (non-violence) is core Jain terminology that must never trip this
    filter. A blocklist term preceded by a negation prefix is not a match.
    """
    text = f"{item.get('headline', '')} {item.get('body', '')}".lower()
    for term in cfg.CRUELTY_BLOCKLIST:
        pattern = r"\b" + re.escape(term) + r"\b"
        for m in re.finditer(pattern, text):
            preceding = text[max(0, m.start() - 15):m.start()]
            if re.search(r"(non[- ]|anti[- ]|without\s+|no\s+)$", preceding):
                continue  # negated — e.g. "non-violence", not a real match
            return term
    return None


def filter_sections(sections: dict) -> tuple[dict, list[str]]:
    """Drop blocked items; return (clean_sections, list of rejection notices)."""
    clean = {}
    rejections = []
    for name, data in sections.items():
        items = data.get("items", [])
        kept = []
        for item in items:
            hit = item_is_blocked(item)
            if hit:
                rejections.append(
                    f'REJECTED from "{name}": "{item.get("headline", "(no headline)")}" '
                    f'(matched blocklist term: "{hit}")'
                )
            else:
                kept.append(item)
        clean[name] = {"items": kept}
    return clean, rejections


# ---------------------------------------------------------------------------
# HTML building blocks
# ---------------------------------------------------------------------------
CSS = """
@page { size: %(page_w)sin %(page_h)sin; margin: 0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin:0; padding:0; background:#f5efe1; font-family:"Liberation Sans","Helvetica Neue",Arial,sans-serif; color:#241f1a; }
.page { break-after: page; page-break-after: always; position: relative; }
.page:last-child { break-after: auto; page-break-after: auto; }

/* ---- Cover page ---- */
.cover { width:100%%; height:%(page_h)sin; position:relative; overflow:hidden; background:#1c1712; }
.cover img.bleed { position:absolute; inset:0; width:100%%; height:100%%; object-fit:cover; }
.cover .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(28,23,18,0.05) 0%%, rgba(28,23,18,0.15) 55%%, rgba(28,23,18,0.88) 100%%); }
.cover .cover-content { position:absolute; left:0; right:0; bottom:0; padding:0.6in 0.7in 0.55in 0.7in; color:#fbf3e6; }
.cover .kicker { font-size:12px; letter-spacing:3px; font-weight:700; text-transform:uppercase; color:#e8c896; margin-bottom:8px; }
.cover h1 { font-family:"Liberation Serif",Georgia,"Times New Roman",serif; font-weight:700; font-size:64px; margin:0 0 10px 0; letter-spacing:0.3px; }
.cover .issue-line { font-size:12.5px; letter-spacing:1.5px; text-transform:uppercase; font-weight:700; color:#e8c896; margin-bottom:18px; }
.cover .teasers { list-style:none; margin:0; padding:0; border-top:1px solid rgba(251,243,230,0.35); padding-top:12px; }
.cover .teasers li { font-family:"Liberation Serif",Georgia,serif; font-size:15px; line-height:1.4; margin-bottom:6px; }

/* ---- Inner pages ---- */
.page-pad { padding:0.55in 0.75in 0.5in 0.75in; height:100%%; }
h2.page-title { font-family:"Liberation Serif",Georgia,serif; font-weight:700; font-size:30px; color:#1c1712; margin:0 0 16px 0; border-bottom:3px solid #1c1712; padding-bottom:12px; }

/* ---- Table of contents ---- */
.toc-list { list-style:none; margin:0; padding:0; }
.toc-list li { display:flex; justify-content:space-between; align-items:baseline; font-size:15px; padding:10px 0; border-bottom:1px solid #d8cdb4; font-family:"Liberation Serif",Georgia,serif; }
.toc-list li .tnum { color:#b9541f; font-weight:700; margin-right:12px; font-family:Arial,sans-serif; font-size:12px; }

/* ---- Editor's note ---- */
.editors-note p { font-size:14px; line-height:1.7; color:#4a4033; }

/* ---- Article sections ---- */
.section-block { margin-bottom:28px; break-inside:avoid; page-break-inside:avoid; }
.section-block + .section-block { border-top:2px solid #1c1712; padding-top:22px; margin-top:0; }
.section-title { font-family:"Liberation Serif",Georgia,serif; font-weight:700; font-size:24px; color:#1c1712; margin:0 0 4px 0; }
.section-rule { border:none; border-top:1px solid #d8cdb4; margin:6px 0 16px 0; }
.item { margin-bottom:20px; padding-bottom:4px; break-inside:avoid; page-break-inside:avoid; }
.item + .item { border-top:1px solid #d8cdb4; padding-top:18px; }
.item .loc { font-size:10.5px; letter-spacing:1.5px; color:#b9541f; text-transform:uppercase; font-weight:700; margin-bottom:4px; }
.item .headline { font-family:"Liberation Serif",Georgia,serif; font-weight:700; font-size:19px; margin:0 0 8px 0; color:#1c1712; }
.item .body-text { font-size:14.5px; line-height:1.5; color:#33291f; margin:0 0 6px 0; }
.item .source-line { font-size:10.5px; letter-spacing:0.5px; color:#9a8c6e; text-transform:uppercase; font-weight:700; }
.empty-note { font-size:13px; font-style:italic; color:#6b5f4d; padding:4px 0 8px 0; }

/* ---- Back cover ---- */
.back-cover { height:%(page_h)sin; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; background:#1c1712; color:#fbf3e6; }
.back-cover .fn-title { font-family:"Liberation Serif",Georgia,serif; font-weight:700; font-size:26px; margin-bottom:14px; }
.back-cover p { font-size:13px; line-height:1.7; color:#d8cdb4; max-width:4.5in; margin:0 0 16px 0; }
.back-cover .copyright { font-size:10px; letter-spacing:1.5px; text-transform:uppercase; color:#8a7a5c; }
"""


def esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_cover(issue: dict, cover_b64: str) -> str:
    teasers = "".join(f"<li>{esc(t)}</li>" for t in issue.get("cover_teasers", []))
    return f"""
<div class="page">
  <div class="cover">
    <img class="bleed" src="data:image/jpeg;base64,{cover_b64}" alt="{esc(issue.get('cover_image_alt',''))}">
    <div class="scrim"></div>
    <div class="cover-content">
      <div class="kicker">Volume {esc(issue.get('volume',''))} &middot; {esc(issue.get('edition',''))}</div>
      <h1>{esc(cfg.MAGAZINE_TITLE)}</h1>
      <div class="issue-line">Coverage: {esc(issue.get('coverage_start',''))} &mdash; {esc(issue.get('coverage_end',''))}</div>
      <ul class="teasers">{teasers}</ul>
    </div>
  </div>
</div>
"""


def build_toc(sections: dict) -> str:
    rows = "".join(
        f'<li><span><span class="tnum">{i+1:02d}</span>{esc(name)}</span></li>'
        for i, name in enumerate(cfg.SECTIONS)
        if name in sections
    )
    return f"""
<div class="page"><div class="page-pad">
  <h2 class="page-title">Contents</h2>
  <ul class="toc-list">{rows}</ul>
</div></div>
"""


def build_editors_note(text: str) -> str:
    return f"""
<div class="page"><div class="page-pad">
  <h2 class="page-title">Editor's Note</h2>
  <div class="editors-note"><p>{esc(text)}</p></div>
</div></div>
"""


def build_section_block(name: str, data: dict) -> str:
    """One section's HTML — NOT wrapped in a page/page-pad. Multiple of these
    get packed together onto a shared physical page by pack_into_pages()
    below, so an empty or short section doesn't burn a whole blank page."""
    items = data.get("items", [])
    if not items:
        body = '<div class="empty-note">No verifiable news was found for this section within the coverage window.</div>'
    else:
        parts = []
        for it in items:
            parts.append(f"""
  <div class="item">
    <div class="loc">{esc(it.get('location',''))}</div>
    <div class="headline">{esc(it.get('headline',''))}</div>
    <div class="body-text">{esc(it.get('body',''))}</div>
    <div class="source-line">Source: {esc(it.get('source',''))} &middot; {esc(it.get('date',''))}</div>
  </div>""")
        body = "".join(parts)
    return f"""
<div class="section-block">
  <div class="section-title">{esc(name)}</div>
  <hr class="section-rule">
  {body}
</div>
"""


# ---------------------------------------------------------------------------
# Page-packing: estimate each section's real printed height in inches (not
# an arbitrary unit) so multiple sections fill a page close to its actual
# capacity, instead of leaving large blank gaps below short sections.
# Constants below are calibrated against the actual CSS in `CSS` above at
# the page size in config.PAGE_SIZE — a body-text line wraps at roughly
# CHARS_PER_LINE characters given the content column width and font size.
# ---------------------------------------------------------------------------
CHARS_PER_LINE_BODY = 92     # .body-text @ ~4.75in usable width, 14.5px font
CHARS_PER_LINE_HEADLINE = 42  # .headline (serif, larger, bolder) wraps sooner

# Empirically calibrated against actual rendered pages: the raw CSS-derived
# estimates below ran ~20% high versus measured page-1/page-2 output when
# first tested (5.84in estimated vs. 4.55in actual; 7.59in vs. 6.14in) — this
# factor corrects for line-height/margin-collapsing effects the estimate
# doesn't model exactly. Re-measure and adjust if the CSS layout changes.
CALIBRATION_FACTOR = 0.80

IN_SECTION_TITLE_RULE = 0.62   # .section-title + .section-rule block
IN_SECTION_DIVIDER = 0.42      # .section-block + .section-block border/padding
IN_EMPTY_NOTE = 0.35
IN_ITEM_LOC_LINE = 0.20
IN_ITEM_SOURCE_LINE = 0.22
IN_ITEM_MARGIN = 0.28          # .item margin-bottom + divider between items
IN_LINE_HEIGHT_BODY = 0.225    # one wrapped line of .body-text at 1.5 line-height
IN_LINE_HEIGHT_HEADLINE = 0.30  # one wrapped line of .headline at 1.2 line-height


def _lines(text: str, chars_per_line: int) -> int:
    return max(1, -(-len(text or "") // chars_per_line))  # ceil div


def item_height_in(item: dict) -> float:
    headline_lines = _lines(item.get("headline", ""), CHARS_PER_LINE_HEADLINE)
    body_lines = _lines(item.get("body", ""), CHARS_PER_LINE_BODY)
    raw = (
        IN_ITEM_LOC_LINE
        + headline_lines * IN_LINE_HEIGHT_HEADLINE
        + body_lines * IN_LINE_HEIGHT_BODY
        + IN_ITEM_SOURCE_LINE
        + IN_ITEM_MARGIN
    )
    return raw * CALIBRATION_FACTOR


def section_height_in(data: dict) -> float:
    """Estimated printed height of one section block, in inches."""
    items = data.get("items", [])
    if not items:
        return (IN_SECTION_TITLE_RULE + IN_EMPTY_NOTE) * CALIBRATION_FACTOR
    return IN_SECTION_TITLE_RULE * CALIBRATION_FACTOR + sum(item_height_in(it) for it in items)


def pack_into_pages(sections: dict) -> list[str]:
    """Greedily group section HTML blocks into page-pad wrappers so pages
    fill up close to their real capacity instead of one section per page."""
    page_h = cfg.PAGE_SIZE["height_in"]
    top_pad, bottom_pad = 0.55, 0.5  # matches .page-pad CSS padding
    capacity = page_h - top_pad - bottom_pad

    pages = []
    current_blocks = []
    current_height = 0.0

    for name in cfg.SECTIONS:
        if name not in sections:
            continue
        data = sections[name]
        h = section_height_in(data)
        divider = (IN_SECTION_DIVIDER * CALIBRATION_FACTOR) if current_blocks else 0.0
        if current_blocks and current_height + divider + h > capacity:
            pages.append(current_blocks)
            current_blocks = []
            current_height = 0.0
            divider = 0.0
        current_blocks.append(build_section_block(name, data))
        current_height += divider + h

    if current_blocks:
        pages.append(current_blocks)

    return [
        f'<div class="page"><div class="page-pad">{"".join(blocks)}</div></div>'
        for blocks in pages
    ]


def build_back_cover() -> str:
    return f"""
<div class="page">
  <div class="back-cover">
    <div class="fn-title">{esc(cfg.MAGAZINE_TITLE)}</div>
    <p>{esc(cfg.PUBLISHER_LINE)}</p>
    <div class="copyright">&copy; {'{{YEAR}}'} {esc(cfg.MAGAZINE_TITLE).upper()}</div>
  </div>
</div>
"""


def build_html(content: dict, cover_b64: str) -> str:
    issue = content["issue"]
    sections = content["sections"]

    # Sections with no items are omitted entirely — no header, no "no news
    # found" block, and no line in the table of contents — rather than
    # rendered as a visible empty placeholder.
    filled_sections = {k: v for k, v in sections.items() if v.get("items")}

    year = str(issue.get("publish_date", ""))[:4] or "2026"

    parts = [f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(cfg.MAGAZINE_TITLE)}</title><style>"
              + (CSS % {"page_w": cfg.PAGE_SIZE["width_in"], "page_h": cfg.PAGE_SIZE["height_in"]})
              + "</style></head><body>"]

    parts.append(build_cover(issue, cover_b64))
    if cfg.HAS_TABLE_OF_CONTENTS:
        parts.append(build_toc(filled_sections))
    parts.append(build_editors_note(content.get("editors_note", "")))

    parts.extend(pack_into_pages(filled_sections))

    if cfg.HAS_BACK_COVER:
        parts.append(build_back_cover().replace("{{YEAR}}", year))

    parts.append("</body></html>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------
def find_chrome() -> str:
    import glob
    candidates = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")
    if candidates:
        return candidates[0]
    for name in ("google-chrome", "chromium", "chromium-browser"):
        from shutil import which
        found = which(name)
        if found:
            return found
    raise RuntimeError("No Chrome/Chromium binary found — pass --chrome explicitly.")


def render_pdf(html_path: Path, pdf_path: Path, chrome_bin: str):
    cmd = [
        chrome_bin, "--headless", "--disable-gpu", "--no-sandbox", "--no-margins",
        f"--print-to-pdf={pdf_path}", str(html_path),
    ]
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Render a Jain Magazine issue to print-ready PDF.")
    ap.add_argument("content_json", help="Path to the per-issue content JSON")
    ap.add_argument("output_pdf", help="Path to write the rendered PDF")
    ap.add_argument("--chrome", default=None, help="Path to a Chrome/Chromium binary")
    args = ap.parse_args()

    content = json.loads(Path(args.content_json).read_text(encoding="utf-8"))

    # Validate: all 13 required sections must be present.
    missing = [s for s in cfg.SECTIONS if s not in content["sections"]]
    if missing:
        sys.exit(f"ERROR: content JSON is missing required sections: {missing}")

    # Mechanical content-safety net.
    clean_sections, rejections = filter_sections(content["sections"])
    content["sections"] = clean_sections
    if rejections:
        print("Content-safety filter removed the following items before rendering:")
        for r in rejections:
            print(" -", r)

    # Cover image.
    cover_path = Path(content["issue"]["cover_image_path"])
    if not cover_path.exists():
        sys.exit(f"ERROR: cover image not found at {cover_path} — see COVER_IMAGE_POLICY in config.py.")
    cover_b64 = base64.b64encode(cover_path.read_bytes()).decode("ascii")

    html = build_html(content, cover_b64)

    html_path = Path(args.output_pdf).with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    chrome_bin = args.chrome or find_chrome()
    render_pdf(html_path, Path(args.output_pdf), chrome_bin)
    print(f"Wrote {args.output_pdf}")


if __name__ == "__main__":
    main()
