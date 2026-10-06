#!/usr/bin/env python3
"""Mirror every registered project's beads into the local hub database.

vip-agent is the hub over the owner's projects (.claude/skills/beads/docs/hub.md). The hub is a
separate Beads database in hub.local/: gitignored, with its own git repo and
no Dolt remote, so nothing it holds leaves the machine. Project paths come
from the gitignored projects.local.json (see projects.example.json).

Sources are only read (`bd --readonly ... export`). The hub receives just the
beads that changed, so an unchanged sync writes nothing, and beads that
vanished at their source are deleted from the hub.

    python3 scripts/hub-sync.py           # sync
    python3 scripts/hub-sync.py --check   # sync, then compare hub with sources
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "hub.local"
PROJECTS_FILE = ROOT / "projects.local.json"
# No remote adoption from git origin, ever: the hub must stay local.
ENV = {**os.environ, "BD_NO_REMOTE_ADOPT": "1", "NO_COLOR": "1"}
UNLIMITED = "100000"


class SyncError(Exception):
    pass


def bd(*args, stdin=None, cwd=None):
    r = subprocess.run(["bd", *args], input=stdin, capture_output=True,
                       text=True, env=ENV, cwd=cwd)
    if r.returncode != 0:
        raise SyncError(f"bd {' '.join(args)}: {r.stderr.strip()[-400:]}")
    return r.stdout


def hub_bd(*args, stdin=None):
    return bd("--directory", str(HUB), *args, stdin=stdin)


def src_bd(beads_dir, *args):
    return bd("--readonly", "--directory", str(beads_dir.parent), *args)


def ensure_hub():
    """Create the hub on first use; refuse to run if it could leave the machine."""
    if not (HUB / ".beads" / "embeddeddolt").exists():
        (HUB / ".beads").mkdir(parents=True, exist_ok=True)
        if not (HUB / ".git").exists():
            subprocess.run(["git", "init", "-q"], cwd=HUB, check=True)
        # Seed the config first: without it bd init finds vip-agent's config
        # and bootstraps from its GitHub remote (.repo-context/learnings.md).
        config = HUB / ".beads" / "config.yaml"
        if not config.exists():
            config.write_text("issue-prefix: hub\n")
        bd("init", "--non-interactive", "--prefix", "hub", "--skip-hooks",
           "--skip-agents", cwd=HUB)
    where = hub_bd("where").splitlines()[0].strip()
    if Path(where) != HUB / ".beads":
        raise SyncError(f"hub resolves to {where}, not {HUB / '.beads'}")
    if json.loads(hub_bd("--json", "dolt", "remote", "list") or "[]"):
        raise SyncError("hub has a Dolt remote; remove it before syncing")
    git_remotes = subprocess.run(["git", "remote"], cwd=HUB, capture_output=True,
                                 text=True, check=True).stdout.strip()
    if git_remotes:
        raise SyncError(f"hub git repo has remotes ({git_remotes}); remove them")


def rows(jsonl):
    return {r["id"]: r for r in map(json.loads, filter(str.strip, jsonl.splitlines()))}


def registered_databases():
    """Map each distinct source .beads dir to one registered path (worktrees
    share one), and list the registered paths that did not resolve."""
    paths = json.loads(PROJECTS_FILE.read_text())["projects"]
    dbs, unresolved = {}, {}
    for p in paths:
        try:
            beads_dir = Path(bd("--readonly", "--directory", os.path.expanduser(p),
                                "where").splitlines()[0].strip())
        except SyncError as e:
            unresolved[p] = e
            continue
        if beads_dir == HUB / ".beads":
            raise SyncError(f"{p} resolves to the hub itself")
        dbs.setdefault(beads_dir, p)
    return dbs, unresolved


def export(beads_dir):
    try:
        return rows(src_bd(beads_dir, "export"))
    except SyncError as e:
        return e


def sync():
    ensure_hub()
    dbs, unresolved = registered_databases()
    with ThreadPoolExecutor() as pool:
        exported = dict(zip(dbs, pool.map(export, dbs)))
    failed = {dbs[db]: e for db, e in exported.items() if isinstance(e, SyncError)}
    failed.update(unresolved)
    source, owner = {}, {}
    for db, beads in exported.items():
        if isinstance(beads, SyncError):
            continue
        for bead_id, row in beads.items():
            if bead_id in owner:
                raise SyncError(f"{bead_id} exists in both {owner[bead_id]} and {db}")
            owner[bead_id] = db
            source[bead_id] = row
    hub = rows(hub_bd("export"))
    changed = [row for bead_id, row in source.items() if hub.get(bead_id) != row]
    if changed:
        # --allow-stale: the source always wins, even over a newer hub row.
        hub_bd("import", "--allow-stale", "-",
               stdin="".join(json.dumps(r) + "\n" for r in changed))
    # A failed export must not look like its project's beads were deleted.
    gone = [] if failed else sorted(set(hub) - set(source))
    if gone:
        hub_bd("delete", "--force", *gone)
    for path, e in failed.items():
        print(f"FAILED {path}: {e}", file=sys.stderr)
    print(f"hub sync: {len(dbs)} databases, {len(source)} beads, "
          f"{len(changed)} imported, {len(gone)} deleted, {len(failed)} failed"
          + (" (deletions skipped)" if failed else ""))
    return dbs, owner, not failed


def ids(jsonl):
    return {r["id"] for r in json.loads(jsonl or "[]") or []}


def check(dbs, owner):
    """Compare the hub with every source: statuses, ready and blocked sets."""
    ok = True
    hub = rows(hub_bd("export"))
    hub_ready = ids(hub_bd("--json", "ready", "--limit", UNLIMITED))
    hub_blocked = ids(hub_bd("--json", "blocked"))
    for db, path in dbs.items():
        mine = {i for i, d in owner.items() if d == db}
        source = rows(src_bd(db, "export"))
        checks = {
            "beads": (set(source), mine & set(hub)),
            "rows": ({i: r for i, r in source.items()},
                     {i: hub[i] for i in mine if i in hub}),
            "ready": (ids(src_bd(db, "--json", "ready", "--limit", UNLIMITED)),
                      hub_ready & mine),
            "blocked": (ids(src_bd(db, "--json", "blocked")), hub_blocked & mine),
        }
        bad = [name for name, (want, got) in checks.items() if want != got]
        ok &= not bad
        print(f"{'OK  ' if not bad else 'DIFF'} {path}: {len(source)} beads, "
              f"{len(checks['ready'][0])} ready, {len(checks['blocked'][0])} blocked"
              + (f"; mismatched: {', '.join(bad)}" if bad else ""))
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="after syncing, compare the hub with every source")
    args = parser.parse_args()
    try:
        dbs, owner, complete = sync()
        if args.check and not check(dbs, owner):
            return 1
        return 0 if complete else 1
    except SyncError as e:
        print(f"hub sync stopped: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
