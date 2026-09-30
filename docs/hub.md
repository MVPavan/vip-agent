# Hub database

vip-agent is the owner's vantage point over every project, so it holds a
single local Beads database that mirrors all of their beads. The dashboard
and cross-project queries read that hub instead of opening each project.
Owner decision, 2026-09-30. Tracking bead: vip-8fw.2.

## Shape

- `hub.local/` holds the hub (gitignored). It has its own git repo and
  `.beads/`, prefix `hub`, and no Dolt or git remote, so nothing it holds
  leaves the machine.
- `projects.local.json` lists the project paths (gitignored, see invariant 2).
  `projects.example.json` shows the format. Worktrees of a project resolve to
  the same database and are synced once.
- `scripts/hub-sync.py` refreshes the hub; `--check` then compares it with
  every source.

## Sync

1. Every source is read with `bd --readonly --directory <project> export`, in
   parallel. Sources are never written (invariant 1).
2. Only rows that differ from the hub are imported, using
   `import --allow-stale` so the source always wins. Re-importing unchanged
   rows would still add a Dolt commit of about 1MB per sync.
3. Beads that no longer exist in any source are deleted from the hub, because
   import only inserts and updates. If any project fails to resolve or
   export, deletion is skipped so that its beads do not look deleted.
4. If a bead ID exists in two projects, the sync stops rather than let one
   overwrite the other.

Bead IDs keep their project prefix, so a hub row's prefix names its project.
Measured with 6 databases and 1,749 beads: the first sync (hub creation plus
full import) took 42s; a sync with no changes takes 3s and writes nothing.

## Why not `bd repo`

`bd repo add` and `bd repo sync` do hydrate one database from others, but
they read the repo list only from the tracked `.beads/config.yaml`, which
would put tracked-project paths into a public commit. They read each
project's auto-exported JSONL rather than its database, and they sync through
the Dolt remote. Details are in `.repo-context/learnings.md`.

## Reading the hub

Run the read commands with `bd --readonly --directory hub.local`: `count
--by-status`, `list`, `ready --limit 100000`, `blocked`, `status`,
`human list` and `export`. Two things to know when reading:

- **Two meanings of "blocked".** `count` and `list` report the stored
  `blocked` status. `blocked` and the `status` summary report beads that
  are waiting on a dependency.
- **Dependencies inside a project are preserved.** Dependencies that cross
  projects appear only if a source records them.

## Limits

- The hub is only as fresh as its last sync. Revisit this when the dashboard
  needs live data; a scheduled sync is the likely answer.
