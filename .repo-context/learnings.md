# Learnings

Verified, likely-to-recur patterns: tool quirks, failed approaches, and
gotchas that would cost the next agent time. Add an entry only when it is
verified and likely to recur; state the pattern, the evidence (repo-relative
path, command, or version), and the fix. Design decisions belong in the
design record (`docs/`), not here. Entries dated before 2026-09-30 were
carried over from MVPavan/via.

- `codex exec -c` silently accepted invalid keys or values on CLI 0.144.1,
  including a bogus effort value. Validate safety-critical overrides before
  dispatch; prefer native `-s` for plain `exec`. `exec resume` and `exec review`
  did not accept `-s`; verify current CLI behavior before changing a wrapper.
- `codex exec` launched without a terminal waits on stdin ("Reading additional
  input from stdin..."); redirect `< /dev/null`.
- Writing a Codex review brief with an unquoted heredoc (`<<EOF`) executes
  backticked names as commands and silently drops them from the brief. Use
  `<<'EOF'`, and check the brief before launch.
- Codex review sandboxes (`-s read-only`) cannot open the Beads database.
  Paste the relevant Beads notes into the review brief rather than citing
  `bd show`.
- Claude Code cloud sessions (2026-09-25): `git push` works once the Claude
  GitHub App covers the repo, but `bd dolt push` gets HTTP 403 from the
  session's git proxy. Cloud sessions carry Beads changes back through the
  committed `.beads/issues.jsonl` / `interactions.jsonl`; sync Dolt locally.
- `claude --cloud` (CLI 2.1.283, 2026-09-27) decides clone vs upload by asking
  claude.ai whether the Claude GitHub App is installed on the repo. If the
  answer is empty ("status is null" in `--debug-file` output) it uploads a
  bundle: the session has no remote and the git proxy refuses pushes. Opening
  claude.ai → Connectors → GitHub Integration → "Check repository status" for
  the repo fixed it. `--cloud` also needs a TTY (run it in tmux).
- Claude Code subagent transcripts (`<session>/subagents/*.jsonl`, CLI
  2.1.283) log each message's stream-start usage: `output_tokens` is 2–16,
  never the final count; input and cache fields are complete. Estimate
  subagent output from content size and label it an estimate.
- `bd init` inside a checkout nested in another beads repo can bootstrap the
  outer repo's issue database. Initialize from a standalone clone.
- `bd init` (1.1.0, 2026-09-30) commits its own files ("bd init: initialize
  beads issue tracking"), including any already-present files it adopts, and
  sets `sync.remote` from the git `origin`. Inspect `git log` after init.
- Local implementer workers have committed trees that fail the gate despite
  the brief; once a `| tail -1` pipe hid the failing exit status. Dispatch
  must say: run the gate in order, stop at the first failure, never pipe a
  check so its status is lost. The orchestrator gates the merged tree.
- Review-driven patch rounds on stateful code did not converge when each fix
  added a new unowned state. Design the state machine first, restate the
  requirement narrowly before adding a mechanism, and check whether the
  producer already keeps the data before designing durability for it.
