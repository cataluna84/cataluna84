#!/usr/bin/env python3
"""Report whether the README stats block is due for a refresh.

Needs no network access and no token, so it is safe to call from a shell
profile, a git hook, or CI. Exits 1 when a refresh is due so callers can
branch on it.

    python3 scripts/check_stale.py            # default 30-day threshold
    python3 scripts/check_stale.py --days 14
    python3 scripts/check_stale.py --quiet     # exit code only
"""

import argparse
import datetime
import os
import re
import sys

MARKER = re.compile(r"<!--\s*STATS:GENERATED\s+(\d{4}-\d{2}-\d{2})\s*-->")
REFRESH_CMD = 'GITHUB_TOKEN="$(gh auth token)" python3 scripts/gen_stats.py'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    readme = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "README.md")
    )
    try:
        with open(readme, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"check_stale: cannot read {readme}: {e}", file=sys.stderr)
        return 2

    m = MARKER.search(text)
    if not m:
        print("check_stale: no STATS:GENERATED marker found", file=sys.stderr)
        return 2

    generated = datetime.date.fromisoformat(m.group(1))
    age = (datetime.date.today() - generated).days

    if age < args.days:
        if not args.quiet:
            print(f"Profile stats are {age} day(s) old. Next refresh in {args.days - age} day(s).")
        return 0

    if not args.quiet:
        print(
            f"\n  Profile stats are {age} days old (threshold {args.days}).\n"
            f"  Refresh:  cd {os.path.dirname(readme)} && {REFRESH_CMD}\n"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
