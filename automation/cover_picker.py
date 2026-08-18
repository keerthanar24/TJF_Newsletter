#!/usr/bin/env python3
"""
Jain Magazine — rotating cover-photo picker.

Real, deterministic code (no LLM judgment needed) that decides which cover
photo an issue should use when no freshly generated image is available that
cycle. Tracks which photo each past issue used and always picks the
least-recently-used photo from the pool in `assets/covers/`, so the cover
visually rotates over time instead of reusing the same image every quarter.

Priority order for a cover image (see RESEARCH_AGENT_PROMPT.md step 4):
    1. A freshly generated image tied to that quarter's leading story, if an
       image-generation tool is available and has quota that cycle.
    2. Otherwise, the next photo in this rotation pool (this script).
    3. Never a placeholder or fabricated image.

Usage:
    python3 cover_picker.py                    # print the chosen photo path
    python3 cover_picker.py --record cover.jpg # after using a photo, log it
"""

import argparse
import json
from pathlib import Path

COVERS_DIR = Path(__file__).parent / "assets" / "covers"
HISTORY_PATH = Path(__file__).parent / "issues" / "cover_history.json"


def _pool() -> list[Path]:
    if not COVERS_DIR.exists():
        return []
    exts = {".jpg", ".jpeg", ".png"}
    return sorted(p for p in COVERS_DIR.iterdir() if p.suffix.lower() in exts)


def _history() -> list[str]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def pick_next_cover() -> Path:
    """Return the least-recently-used photo in the pool. If the pool has
    only one photo, that photo is returned every time (nothing to rotate
    to) — the pool needs more real photos added before rotation is
    meaningful; this is stated honestly rather than faked."""
    pool = _pool()
    if not pool:
        raise RuntimeError(
            f"No cover photos found in {COVERS_DIR}. Add at least one real "
            "photo before rendering — see COVER_IMAGE_POLICY in config.py."
        )
    if len(pool) == 1:
        return pool[0]

    history = _history()  # most-recent-last
    used_recently = set(history[-(len(pool) - 1):]) if history else set()
    for candidate in pool:
        if candidate.name not in used_recently:
            return candidate
    return pool[0]  # fallback, shouldn't normally hit this


def record_used(cover_path: Path):
    """Append this cover to the rotation history after an issue is rendered."""
    history = _history()
    history.append(Path(cover_path).name)
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Pick or record the rotating cover photo.")
    ap.add_argument("--record", metavar="FILENAME", help="Record that this cover was used for the current issue")
    args = ap.parse_args()

    if args.record:
        record_used(Path(args.record))
        print(f"Recorded cover usage: {args.record}")
        return

    chosen = pick_next_cover()
    pool_size = len(_pool())
    print(str(chosen))
    if pool_size == 1:
        import sys
        print(
            f"NOTE: only 1 photo in the rotation pool ({COVERS_DIR}) — "
            "every issue will reuse it until more real photos are added.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
