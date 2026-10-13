#!/usr/bin/env bash
# SessionStart hook: prime the agent with Beads workflow context (`bd prime --hook-json`).
#
# A silent no-op when `bd` is not on PATH: the hook must never fail the session.

command -v bd >/dev/null 2>&1 && bd prime --hook-json
exit 0
