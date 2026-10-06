# Repo map

vip-agent is newly bootstrapped: the shared agent harness, Beads and the hub
sync are in place; the dashboard does not exist yet. Live work state is in Beads
(`bd ready`, `bd list --status=open`).

## What lives where

- `AGENTS.md`: agent operating policy; `CLAUDE.md` imports it.
- `.repo-context/`: shared agent guidance (this directory).
- `.claude/`: agent harness: `skills/`, `agents/`, `hooks/`, `settings.json`,
  `scripts/skill-catalog.py` (skill and path catalog check).
- `.codex/`: Codex harness configuration; `skills/` entries link to
  `.claude/skills/`.
- `.beads/`: Beads issue-tracker data, config and git hooks. Everything about
  Beads lives in the `beads` skill (`.claude/skills/beads/`): the policy in
  `references/`, and in `docs/` the bd capabilities, the generated CLI
  reference, upgrades, the hub design and bd's original prime text.
- `docs/`: design records, created as work lands.
- `scripts/`: `hub-sync.py` (mirrors every project's beads into the hub, see
  `.claude/skills/beads/docs/hub.md`) and `bd-cli-reference.py` (generates
  the `bd` CLI reference into `.claude/skills/beads/docs/`).
- `hub.local/`: gitignored hub database; `projects.local.json` lists the
  tracked project paths, in the format of `projects.example.json`.
- `scratchpad/`: gitignored temporary artifacts.
- `*.local.*`: gitignored machine-local configuration, such as the list of
  tracked project paths.

## Origin

The harness was copied from MVPavan/via (a parent-repo reference) on
2026-09-30. Learnings that concern only VIA's Rust code stayed there.
