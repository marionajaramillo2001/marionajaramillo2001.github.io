#!/usr/bin/env python3
"""Inject shared HTML partials into site pages. Run from repo root: python3 scripts/build.py"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDES = ROOT / "includes"

PAGES: dict[str, str] = {
    "index.html": "about",
    "publications.html": "publications",
    "research.html": "research",
}

START_RE = re.compile(r"<!--\s*@include-start\s+(\S+)(?:\s+(\w+))?\s*-->")
END_MARKER = "<!-- @include-end -->"


def load_partial(rel_path: str, page_key: str | None = None) -> str:
    path = ROOT / rel_path
    if not path.is_file():
        raise FileNotFoundError(f"Missing partial: {path}")

    text = path.read_text(encoding="utf-8")

    if "topnav" in rel_path and page_key:
        active = {
            "about": "ACTIVE_ABOUT",
            "publications": "ACTIVE_PUBLICATIONS",
            "research": "ACTIVE_RESEARCH",
        }
        for key, token in active.items():
            value = ' class="active"' if key == page_key else ""
            text = text.replace("{{" + token + "}}", value)

    return text.rstrip() + "\n"


def inject_includes(html: str, page_key: str) -> str:
  out: list[str] = []
  i = 0
  while i < len(html):
    match = START_RE.search(html, i)
    if not match:
      out.append(html[i:])
      break

    out.append(html[i : match.start()])
    rel_path = match.group(1)
    arg = match.group(2) or page_key
    end = html.find(END_MARKER, match.end())
    if end == -1:
      raise ValueError(f"Missing {END_MARKER} after {match.group(0)}")

    partial = load_partial(rel_path, arg)
    out.append(match.group(0))
    out.append("\n")
    out.append(partial)
    out.append(END_MARKER)
    out.append("\n")
    i = end + len(END_MARKER)

  return "".join(out)


def main() -> int:
    for filename, page_key in PAGES.items():
        path = ROOT / filename
        if not path.is_file():
            print(f"skip missing {filename}", file=sys.stderr)
            continue
        original = path.read_text(encoding="utf-8")
        updated = inject_includes(original, page_key)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"updated {filename}")
        else:
            print(f"unchanged {filename}")

    print("Done. Edit includes/sidebar.html or includes/topnav.html, then re-run this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
