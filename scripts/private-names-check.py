#!/usr/bin/env python3
"""Fail if bead text would publish private project names or local paths.

This repository is public, and its beads reach GitHub twice: through the
tracked .beads/issues.jsonl and through `bd dolt push` (refs/dolt/data).
Names come from the gitignored projects.local.json (the folder name of every
registered project except this one), so the list itself is never committed.

    python3 scripts/private-names-check.py           # scan the bead database
    python3 scripts/private-names-check.py FILE...   # also scan these files

Run it before refreshing issues.jsonl, committing beads, or `bd dolt push`.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_FILE = ROOT / "projects.local.json"
# Names that are also English words count only when they cannot be prose:
# next to a comma, apostrophe, hyphen, slash or bracket, or at the end.
COMMON_WORDS = {"via"}
LOCAL_PATH = r"(?:/home/|/Users/|/data/|/mnt/[a-z]/|[A-Z]:\\)"


def patterns():
    paths = json.loads(PROJECTS_FILE.read_text())["projects"]
    names = {Path(p).name for p in paths} - {ROOT.name}
    pats = [re.compile(LOCAL_PATH)]
    for n in sorted(names):
        word = rf"(?<![\w-]){re.escape(n)}(?![\w])"
        if n.lower() in COMMON_WORDS:
            word = rf"(?:(?<=[(/'\"]){word}|{word}(?=[,)'/\"-]|\s*$))"
        pats.append(re.compile(word, re.I))
    return pats


def scan(label, text, pats):
    hits = 0
    for i, line in enumerate(text.splitlines(), 1):
        for p in pats:
            for m in p.finditer(line):
                ctx = line[max(0, m.start() - 40):m.end() + 40]
                print(f"{label}:{i}: {m.group(0)!r} in …{ctx}…")
                hits += 1
    return hits


def main():
    pats = patterns()
    export = subprocess.run(["bd", "--readonly", "export"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout
    hits = scan("bead database", export, pats)
    for f in sys.argv[1:]:
        hits += scan(f, Path(f).read_text(), pats)
    print(f"private-name hits: {hits}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
