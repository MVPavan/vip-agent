# Repo map

vip-agent is newly bootstrapped: the shared agent harness and Beads are in
place; no application code exists yet. Live work state is in Beads
(`bd ready`, `bd list --status=open`).

## What lives where

- `AGENTS.md`: agent operating policy; `CLAUDE.md` imports it.
- `.repo-context/`: shared agent guidance (this directory).
- `.claude/`: agent harness: `skills/`, `agents/`, `hooks/`, `settings.json`,
  `scripts/skill-catalog.py` (skill and path catalog check).
- `.codex/`: Codex harness configuration; `skills/` entries link to
  `.claude/skills/`.
- `.beads/`: Beads issue-tracker config, hooks and policy (`beads.md`).
- `scratchpad/`: gitignored temporary artifacts.
- `*.local.*`: gitignored machine-local configuration, such as the list of
  tracked project paths.

## Origin

The harness was copied from MVPavan/via (a parent-repo reference) on
2026-09-30. Learnings that concern only VIA's Rust code stayed there.
