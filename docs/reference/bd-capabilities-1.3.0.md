# bd capabilities — bd 1.3.0

What `bd` can do, grouped by capability, with every command and subcommand
and what we can use it for. This is the short companion to
[the full CLI reference](bd-cli-1.3.0.md), which holds usage, examples and
every flag. Derived from the 1.3.0 `--help` text (checked 2026-09-30). Notes
marked *Our use* are recommendations, not bd behavior.

## The model in one page

- **Bead (issue).** The unit of work. It has a hash ID with the project
  prefix (for example `vip-8fw`); children get hierarchical IDs (`vip-8fw.1`).
  Fields: title, description, design, acceptance criteria, notes, priority
  0–4, type, status, assignee, owner, labels, metadata (arbitrary JSON), due
  and defer dates, estimate, external ref and spec ID.
- **Types.** `task`, `bug`, `feature`, `chore`, `epic`, `decision` (ADR),
  `spike`, `story` and `milestone`, plus custom types (`types.custom`).
- **Statuses and categories.** `open` (active); `in_progress`, `blocked` and
  `hooked` (wip); `deferred` and `pinned` (frozen); `closed` (done). Custom
  statuses (`status.custom`) take a category, and the category decides whether
  they appear in `bd ready` and in the default `bd list`.
- **Dependencies.** Typed edges: `blocks` (the default, and the only kind
  that gates readiness), `parent-child`, `tracks`, `related`, `relates-to`,
  `discovered-from`, `caused-by`, `validates`, `supersedes`, `until`,
  `waits-for` (fan-out gates), and external `external:<project>:<capability>`.
- **Ready front.** Open beads with no active blocker. `bd ready` answers
  "what can be worked on now", and parallel agents draw from it.
- **Claims and leases.** Claiming sets the assignee and `in_progress`
  atomically and grants a lease. Workers heartbeat it; a dead worker's lease
  goes stale and can be reclaimed.
- **Storage.** A Dolt database (embedded by default) with full history,
  branches, merges and push/pull to a Dolt remote, which can ride a git remote.
  Some beads are *ephemeral* (wisps): kept locally, excluded from sync.
- **Templates.** Formulas (TOML/JSON) are cooked into protos (templates),
  then poured into persistent molecules or spawned as ephemeral wisps.
- **Agent memory.** Persistent memories (`bd remember`) and a key-value store,
  injected into agent sessions by `bd prime`.
- **Machine interfaces.** `--json` on every command, a JSON Schema
  (`bd schema`), an HTTP API (`bd serve`), raw SQL (`bd sql`) and an ordered
  events journal (`bd events`).

## 1. Capture and edit work

Create beads in any granularity, from one-line captures to whole dependency
graphs, and change any field later.

- `bd create` — Create a bead with any field set, or a batch from a markdown
  file or a JSON dependency graph. It can also wire dependencies, parent,
  labels, due/defer dates, estimates, required skills, spec links and
  ephemeral storage in one call, and validate required description sections.
- `bd create-form` — Interactive terminal form for creating a bead (humans
  only).
- `bd q` — Quick capture that prints only the new ID, for scripts and agents
  that need to chain commands.
- `bd todo` — Lightweight TODOs as ordinary task beads.
  - `bd todo add` — Add a TODO (a priority-2 task).
  - `bd todo done` — Close TODOs.
  - `bd todo list` — List open TODOs.
- `bd update` — Change any field on one or more beads: status, priority,
  assignee, labels, metadata, parent, dates and text sections. `--claim` takes
  work atomically. The `--if-assignee` and `--if-status` guards make it a
  compare-and-swap that exits 13 if another actor got there first.
- `bd edit` — Edit a text field (description, design, notes, acceptance) in
  `$EDITOR` (humans only).
- `bd note` — Append to a bead's notes, for progress logs without
  overwriting.
- `bd comment` — Add a comment (shorthand for `bd comments add`).
- `bd comments` — View a bead's comment thread.
  - `bd comments add` — Add a comment, optionally as another author or from a
    file.
  - `bd comments list` — Not a working command: it only points you to
    `bd comments <id>`.
- `bd priority` — Set priority 0 (critical) to 4 (backlog).
- `bd assign` — Set the assignee. It refuses to overwrite another actor's
  live claim without `--force`.
- `bd tag` — Add one label (shorthand).
- `bd label` — Manage labels, which are the main axis for scoping queries
  and claims.
  - `bd label add` — Add labels to beads.
  - `bd label remove` — Remove labels from beads.
  - `bd label list` — Labels on one bead.
  - `bd label list-all` — Every label in the database; useful for building
    filters.
  - `bd label propagate` — Copy a parent's label to all its direct children,
    for example to tag an epic's subtasks with a branch.
- `bd set-state` — Set an operational state dimension (`health:failing`,
  `mode:degraded`) atomically: it records an event and swaps the
  `dimension:value` label.
- `bd state` — Read the current value of one state dimension.
  - `bd state list` — All state dimensions on a bead.
- `bd rename` — Change a bead's ID and rewrite every reference, dependency,
  label, comment and event.
- `bd delete` — Permanently delete beads and clean up references. It refuses
  if dependents exist, unless you cascade or orphan them.
- `bd promote` — Turn an ephemeral wisp into a permanent bead, keeping its ID
  and links.

## 2. Lifecycle and status

Move beads through their life and record why.

- `bd close` — Close beads with per-ID reasons. It can then show newly
  unblocked work, claim the next ready bead, or advance to the next molecule
  step. It can record the Claude Code session ID.
- `bd reopen` — Reopen closed beads and emit a Reopened event.
- `bd defer` — Put beads on ice: until a date (a snooze that wakes up
  automatically) or indefinitely (icebox). They leave `bd ready` but stay in
  `bd list`.
- `bd undefer` — Bring deferred beads back to open.
- `bd duplicate` — Close a bead as a duplicate of a canonical one, linking
  them.
- `bd supersede` — Close a bead as replaced by a newer one; suited to
  evolving designs and specs.
- `bd statuses` — List valid statuses and their categories, including custom
  ones.
- `bd types` — List valid bead types, including custom ones, and the
  sections each type requires.

## 3. Find the next work

Decide what to do now, and notice work that has stalled or slipped.

- `bd ready` — The ready front: open beads with no active blocker
  (in-progress, blocked, deferred and hooked beads are excluded). Filters: labels, type, priority, parent, molecule, metadata, assignee.
  `--claim` takes the first match atomically, and `--explain` shows the
  dependency reasoning.
- `bd blocked` — Beads waiting on open blockers.
- `bd stale` — Beads not updated in N days, such as abandoned claims or
  forgotten work.
- `bd orphans` — Beads referenced in commit messages but still open: work
  that shipped without being closed.
- `bd human` — A short menu of the ~15 essential commands for humans, plus
  the queue of beads labelled `human` that need a person.
  - `bd human list` — Beads waiting on a human decision or action.
  - `bd human respond` — Answer one: add the response as a comment and close
    it.
  - `bd human dismiss` — Close one without responding.
  - `bd human stats` — Counts of pending, responded and dismissed beads.

*Our use:* `bd human list` is the natural source for the dashboard's "needs
you" panel.

## 4. Search, view and report

Look at any slice of the data, now or in the past.

- `bd list` — The general filterable listing: every field, date ranges, text
  contains, labels (any, all, pattern, regex), metadata, parent, overdue,
  deferred and pinned. It can render a tree, a Graphviz or digraph graph, or
  a Go template, and can watch and refresh live.
- `bd show` — Full detail of beads. It can also show the bead as of any
  commit or branch, its children, beads that reference it, its dependents,
  the currently active bead, or a message thread, and can watch for changes.
- `bd children` — All children of a parent, closed included.
- `bd search` — Text search over titles and IDs, closed beads included by
  default, with the same filters as `list`.
- `bd query` — A small query language with comparisons, AND/OR/NOT, fields
  and relative dates (`status=open AND updated<7d`), for filters flags cannot
  express.
- `bd count` — Counts matching filters, grouped by status, type, priority,
  assignee or label.
- `bd status` — A `git status`-like overview: counts by state, ready work,
  pinned count, lead time and the last 24 hours of activity.
- `bd epic` — Epic reporting.
  - `bd epic status` — Completion of each epic, and which epics are eligible
    to close.
- `bd history` — Every committed version of a bead, or its audit events.
- `bd diff` — What changed in the issue data between two commits or branches.

*Our use:* `count --by-*`, `status`, `epic status` and `history` cover most
of the dashboard's overview page.

## 5. Dependencies and structure

Model how work relates, and check that the graph makes sense.

- `bd dep` — Manage dependency edges; `bd dep <a> --blocks <b>` is shorthand.
  - `bd dep add` — Add a typed edge. It accepts external
    `external:<project>:<capability>` targets and bulk NDJSON wiring.
  - `bd dep remove` — Remove an edge.
  - `bd dep list` — Dependencies or dependents of beads, filterable by type.
  - `bd dep tree` — Tree of what blocks a bead, what it blocks, or both.
  - `bd dep relate` — A bidirectional "see also" link that neither blocks nor
    nests.
  - `bd dep unrelate` — Remove that link.
  - `bd dep cycles` — Find dependency cycles.
- `bd link` — Shorthand for `bd dep add`.
- `bd graph` — Visualise the graph: a terminal DAG, boxes, compact tree,
  Graphviz DOT, self-contained interactive HTML (D3), or an LLM-friendly
  view of open beads only. Layers show execution order and parallelism.
  - `bd graph check` — Integrity check for cycles and orphans; exit code 1 if
    problems are found.
- `bd swarm` — Treat an epic's DAG as parallel work for several agents.
  - `bd swarm create` — Create a swarm molecule that coordinates an epic.
  - `bd swarm list` — Swarms with progress and active workers.
  - `bd swarm status` — Completed, active, ready and blocked children,
    computed live from the beads.
  - `bd swarm validate` — Check that an epic is ready to swarm (dependency
    direction, orphans, cycles, disconnected parts) and report the waves of
    parallel work and maximum parallelism.

## 6. Multi-agent coordination

Let several agents share one database without stepping on each other.

- `bd update --claim` / `bd ready --claim` — Atomic claiming; claim pools
  (`claim.pools`) let a dispatcher pre-assign work to a pool.
- `bd unclaim` — Release a claim. Only the holder can do it without
  `--force`, and it has a compare-and-swap form for supervisors.
- `bd heartbeat` — Keep your claim's lease alive while working.
- `bd reclaim` — The reaper: return beads whose leases went stale to the
  ready front. It is replica-aware for federated setups.
- `bd gate` — Asynchronous wait conditions that block a step until something
  happens: a human, a timer, a GitHub run, a PR merge or another bead.
  - `bd gate create` — Block a bead on a new gate.
  - `bd gate list` — Open gates, or the gates on one bead.
  - `bd gate show` — A gate and its waiters.
  - `bd gate check` — Evaluate gates and close the resolved ones (it queries
    GitHub through `gh`).
  - `bd gate resolve` — Close a gate by hand.
  - `bd gate discover` — Find the GitHub run ID for CI gates that lack one.
  - `bd gate add-waiter` — Register an agent to be woken when a gate closes.
- `bd merge-slot` — A one-holder lock that serialises merge-conflict
  resolution between agents.
  - `bd merge-slot create` — Create the project's slot.
  - `bd merge-slot acquire` — Take it, or join the wait queue.
  - `bd merge-slot check` — Available, or who holds it.
  - `bd merge-slot release` — Give it back.
- `bd mail` — Delegate to an external mail provider configured with
  `mail.delegate` (for example an orchestrator's mail); bd has none of its
  own.

## 7. Templates and repeatable workflows

Capture a workflow once and stamp out real beads from it.

- `bd formula` — Workflow templates in TOML or JSON, with variables, steps,
  composition and inheritance.
  - `bd formula list` — Formulas across the project, repo, user and shared
    search paths.
  - `bd formula show` — A formula's variables, steps, dependencies and
    composition rules.
  - `bd formula schema` — The formula file schema (alias `primitives`).
  - `bd formula convert` — Convert JSON formulas to TOML.
- `bd cook` — Compile a formula into a proto, with placeholders kept or
  variables substituted.
- `bd mol` — Molecules: real beads spawned from templates.
  - `bd mol show` — A proto's or molecule's structure, highlighting steps
    that can run in parallel.
  - `bd mol pour` — Instantiate a template as persistent, synced work.
  - `bd mol wisp` — Instantiate a template as ephemeral local work, or
    manage wisps.
    - `bd mol wisp create` — Spawn a wisp from a proto.
    - `bd mol wisp list` — Wisps here, flagging old ones.
    - `bd mol wisp gc` — Delete abandoned wisps; live, blocked and frozen
      steps are never reclaimed.
  - `bd mol bond` — Combine protos and molecules sequentially, in parallel
    or conditionally, with readable child IDs.
  - `bd mol squash` — Condense a molecule's ephemeral steps into one
    permanent digest bead (an agent can supply the summary).
  - `bd mol burn` — Delete a molecule without a trace.
  - `bd mol distill` — Reverse direction: extract a reusable formula from an
    epic that grew organically.
  - `bd mol current` — Where you are in a workflow: done, current, ready and
    blocked steps.
  - `bd mol progress` — Completed/total, rate and ETA, even for very large
    molecules.
  - `bd mol ready` — Molecules whose gate has closed and can resume.
  - `bd mol seed` — Check that a formula can be found and cooked.
  - `bd mol stale` — Molecules whose children are all closed but whose root
    is still open.

## 8. Cross-project work

Link work between projects and move beads between them.

- `bd ship` — Publish a capability from a closed bead labelled
  `export:<capability>`. Other projects' `external:<project>:<capability>`
  dependencies then resolve.
- `bd repo` — Hydrate beads from several projects into one database for a
  unified view.
  - `bd repo add` — Add a project to hydrate from (writes the tracked
    `config.yaml`).
  - `bd repo list` — Configured projects.
  - `bd repo remove` — Remove one and its hydrated beads.
  - `bd repo sync` — Import each project's `issues.jsonl` now.
- `bd migrate issues` — Move beads to another repository, keeping their
  dependencies.
- `bd migrate-personal` — Move your personal planning beads out of a shared
  project into your own planning repo.
- `bd federation` — Peer-to-peer sync between separate Beads databases.
  - `bd federation add-peer` — Add a peer (DoltHub, a SQL server or a file
    path) with stored credentials.
  - `bd federation list-peers` — Configured peers.
  - `bd federation status` — Commits ahead/behind each peer and conflicts.
  - `bd federation sync` — Pull from and push to peers with a conflict
    strategy.

*Our use:* `bd repo` only reads the other projects, but it lists their paths
in the hub's tracked `config.yaml` (it reads no other file for this; checked
in the 1.3.0 source), and `repo sync` pushes through the hub's Dolt remote.
In a public hub that publishes the project list and every project's beads.
It also reads the auto-exported JSONL rather than the live database.

## 9. Provenance, audit and change feeds

Know who changed what, why, and tie beads to the artifacts they produced.

- `bd provenance` — An append-only log binding beads to external artifacts:
  commits, PRs, branches, transcripts.
  - `bd provenance record` — Record a binding; running it twice is harmless.
  - `bd provenance log` — Bindings for one bead.
  - `bd provenance by-ref` — Beads bound to one artifact (for example which
    beads a commit touched).
- `bd audit` — An optional log of agent interactions (prompts, responses,
  tool calls) in `.beads/interactions.jsonl`, for "why did the agent do
  that?" and for training datasets. Off by default in 1.3.0.
  - `bd audit record` — Append an interaction entry.
  - `bd audit label` — Label an earlier entry (for example good or bad).
- `bd events` — An ordered, gapless journal of every mutation, for consumers
  that follow changes incrementally. Off until `events-journal` is enabled,
  and specific to this clone and branch.
  - `bd events tail` — Records after a sequence number, or follow live.
  - `bd events export` — The whole journal from the start.
  - `bd events prune` — Cut old records earlier than retention would.
- `bd metrics` — bd's anonymous usage metrics (on by default).
  - `bd metrics on` / `bd metrics off` — Opt in or out.
  - `bd metrics example` — Show exactly what is sent.

*Our use:* `bd events tail --follow` is a live-refresh feed for the
dashboard; see the replica and re-baseline caveats in the full reference.

## 10. Agent integration and memory

Keep agents oriented across sessions and compactions.

- `bd prime` — Beads workflow context formatted for agents, plus persistent
  memories. It is what session-start hooks inject, customisable through
  `.beads/PRIME.md` and capped for large memory sets.
- `bd onboard` — The short snippet for `AGENTS.md` that points agents at
  `bd prime`.
- `bd setup` — Install Beads instructions for an AI tool (Claude, Codex,
  Cursor, Copilot, Gemini, Aider and others), per project or globally.
- `bd quickstart` — A guide to common workflows.
- `bd remember` — Store a memory that is injected into every future session.
- `bd recall` — Read one memory in full.
- `bd memories` — List or search memories.
- `bd forget` — Delete a memory.
- `bd kv` — A general key-value store for flags and settings that persist
  across sessions.
  - `bd kv set` / `bd kv get` / `bd kv list` / `bd kv clear` — Write, read,
    list and delete keys.
- `bd hooks` — Git hooks that run Beads logic on commit, merge, push and
  checkout, and add agent identity trailers to commit messages.
  - `bd hooks install` — Install into `.git/hooks`, `.beads/hooks` or a shared
    directory, preserving other hook content.
  - `bd hooks list` — Installed, outdated or missing.
  - `bd hooks run` — The hook logic that the thin hook scripts call.
  - `bd hooks uninstall` — Remove them.
- `bd rules` — Maintain Claude rule files.
  - `bd rules audit` — Find contradictions and merge opportunities.
  - `bd rules compact` — Merge related rules into composites.

## 11. Sync, versioning and branches

Treat the issue data like a git repository.

- `bd dolt` — The storage engine and its remote.
  - `bd dolt push` / `bd dolt pull` — Publish and fetch commits through the
    Dolt remote (which can ride your git origin).
  - `bd dolt commit` — Commit pending changes (the commit point in batch
    auto-commit mode).
  - `bd dolt remote` — Manage remotes.
    - `bd dolt remote add` / `list` / `remove` — Add, show and remove.
    - `bd dolt remote reset-data` — Rebuild a remote's store after a history
      squash, so it drops the old data.
  - `bd dolt status` / `bd dolt show` — Engine status and configuration.
  - `bd dolt start` / `bd dolt stop` / `bd dolt test` — Start, stop and test
    a SQL server (server mode only).
  - `bd dolt set` — Server connection settings (server mode only; secrets
    stay in environment variables or the credentials file).
  - `bd dolt killall` — Kill orphaned SQL-server processes.
- `bd sync` — One full cycle: pull, detect conflicts reliably, repair
  blocked flags, push with retries. Its exit codes are designed for timers.
- `bd vc` — Git-like operations on the issue data.
  - `bd vc status` — Branch, commit and uncommitted changes.
  - `bd vc commit` — Commit with a message.
  - `bd vc merge` — Merge a branch.
- `bd branch` — List or create branches of the issue data, for example to
  plan speculatively and merge later.
- `bd conflicts` — Handle merge conflicts without the raw Dolt CLI.
  - `bd conflicts list` — What is conflicted.
  - `bd conflicts show` — Base, ours and theirs, field by field.
  - `bd conflicts resolve` — Take ours or theirs per bead or per table, then
    conclude the merge.
- `bd bootstrap` — Set up the database on a fresh clone or new machine
  without destroying data: clones from the remote, or restores from a backup
  or JSONL.

## 12. Import, export and backup

Move beads in and out, and keep recoverable copies.

- `bd export` — Beads as JSONL (optionally with memories and infrastructure
  beads, or scrubbed of test records). It is an interchange format, not a
  full backup.
- `bd import` — Upsert JSONL into the database. Older rows never overwrite
  newer local ones unless forced, and a re-run is safe.
- `bd backup` — Dolt-native backups that keep full history.
  - `bd backup init` — Set a destination (a directory or DoltHub).
  - `bd backup sync` — Take a backup (atomic).
  - `bd backup status` — The last backup.
  - `bd backup restore` — Restore a database from a backup.
  - `bd backup remove` — Forget the destination (the data stays).
- `bd restore` — Recover the original text of a bead that was compacted.
- `bd schema` — The JSON Schema of bd's `--json` and export records, for
  generating typed models.

## 13. External trackers

Two-way sync with other issue trackers; each has the same shape: `pull` and
`push` specific items, `status`, and a bidirectional `sync` with a conflict
preference.

- `bd github` — GitHub Issues.
  - `bd github sync` / `pull` / `push` / `status` / `repos` — Sync, pull
    items, push beads, show state, list accessible repos.
- `bd gitlab` — GitLab issues (project or group level).
  - `bd gitlab sync` / `pull` / `push` / `status` / `projects` — As above;
    list accessible projects.
- `bd jira` — Jira.
  - `bd jira sync` / `pull` / `push` / `status` — As above.
- `bd linear` — Linear, including priority, state, label and relation
  mappings and milestones.
  - `bd linear sync` / `pull` / `push` / `status` / `teams` — As above;
    list teams for configuration.
- `bd ado` — Azure DevOps work items with area/iteration filters.
  - `bd ado sync` / `pull` / `push` / `status` / `projects` — As above.
- `bd notion` — Notion databases.
  - `bd notion init` — Create a dedicated Beads database in Notion.
  - `bd notion connect` — Connect to an existing one.
  - `bd notion sync` / `pull` / `push` / `status` — As above.

## 14. Programmatic access

Drive bd from programs instead of by hand.

- Global `--json` — Structured output on every command. Other global flags:
  `--actor` (attribution), `--readonly`, `--sandbox`, `--db` / `--directory`
  (target another project), `--quiet`, `--verbose`, `--no-color`.
- `bd serve` — An HTTP API (OpenAPI at `/v0`) over the same operations as
  the CLI, for clients that would otherwise spawn bd per call. Loopback only
  unless given a token file; no TLS; hooks do not fire. Requires a Dolt SQL
  server: embedded workspaces refuse it (checked 2026-09-30).
- `bd sql` — Raw SQL against the database, for debugging or queries the CLI
  cannot express. Writes through it bypass the events journal. Not supported
  in embedded mode (checked 2026-09-30).
- `bd batch` — Many writes (close, update, create, dep add/remove) in one
  transaction and one commit, all-or-nothing.
- `bd completion` — Shell completion scripts.
  - `bd completion bash` / `zsh` / `fish` / `powershell` — One per shell.

*Our use:* our projects run embedded Dolt, so `bd serve` and `bd sql` are
unavailable. The dashboard reads through `--readonly --directory <project>`
CLI calls with `--json` or `export`, typed with `bd schema`. Even under
`--readonly`, `bd show` rewrites `.beads/last-touched`, the fallback target
of an interactive `bd close` or `bd update` with no ID, so the dashboard
must not call it (checked 2026-09-30).

## 15. Setup, configuration and diagnostics

Initialise projects, configure them, and find out what bd is actually using.

- `bd init` — Create `.beads/` and its database: embedded or server,
  prefix, role, stealth mode (invisible to collaborators), agent files and
  hooks.
- `bd init-safety` — Explains `init`'s safety rules, the destroy-token
  format and refusal exit codes.
- `bd config` — Project settings (integrations, custom statuses and types,
  claim pools, lint sections, export/import, doctor suppressions).
  - `bd config get` / `set` / `unset` / `list` — Read and write keys.
  - `bd config set-many` — Set several keys in one commit.
  - `bd config show` — Every effective value and where it came from.
  - `bd config validate` — Check sync-related settings.
  - `bd config drift` — Read-only check that hooks, remote and server match
    the config.
  - `bd config apply` — Fix that drift (idempotent).
- `bd context` — Backend identity, paths and sync settings, readable even
  when the database cannot open.
- `bd where` — Which `.beads` directory and database are actually in use.
- `bd info` — Database path, counts, schema and what's new.
- `bd ping` — Quick check that the database opens and answers.
- `bd doctor` — Health checks and repairs. In embedded mode (ours) only the
  `artifacts`, `conventions` and `pollution` checks work.
- `bd version` — The installed version.
- `bd upgrade` — Track bd version changes.
  - `bd upgrade status` — Has bd changed since last use?
  - `bd upgrade review` — Everything that changed since the version you last
    used.
  - `bd upgrade ack` — Mark the current version as seen.
- `bd worktree` — Git worktrees that share the main clone's database.
  - `bd worktree create` — Create one (and gitignore it).
  - `bd worktree list` — All worktrees and their Beads state.
  - `bd worktree info` — The current worktree.
  - `bd worktree remove` — Remove one only if it is clean and merged.

## 16. Quality and hygiene

Keep the data trustworthy as it grows.

- `bd lint` — Beads missing required sections for their type (for example
  acceptance criteria), extendable per type in config.
- `bd duplicates` — Beads with identical content, with optional automatic
  merging.
- `bd find-duplicates` — Beads about the same thing in different words, by
  text similarity or an LLM.
- `bd preflight` — A pre-PR checklist aimed at contributors to the beads
  project itself (Go tests, lint, nix hash); of little use elsewhere.

## 17. Maintenance and storage

Keep the database small and fast, and fix structural problems.

- `bd prune` — Delete old closed regular beads. It skips pinned beads and
  beads still cited by open work.
- `bd purge` — Delete closed ephemeral beads (wisps).
- `bd compact` — Squash Dolt commits older than N days, keeping recent
  history.
- `bd flatten` — Squash all history into one commit (irreversible).
- `bd gc` — Delete old closed beads, compact history and garbage-collect
  storage in one pass.
- `bd admin` — Administrative operations.
  - `bd admin cleanup` — Delete closed beads by age.
  - `bd admin compact` — Replace old closed beads' text with summaries
    (agent-supplied or AI), or garbage-collect Dolt.
  - `bd admin reset` — Remove all Beads data and hooks from a project.
- `bd rename-prefix` — Change the ID prefix everywhere, or consolidate mixed
  prefixes.
- `bd migrate` — Schema and layout changes.
  - `bd migrate schema` — Apply pending schema migrations explicitly.
  - `bd migrate hooks` — Convert hook files to the marker-managed format.
  - `bd migrate sync` — Commit issue data to a dedicated branch.
  - `bd migrate issues` — Move beads between repositories (see section 8).
  - `bd migrate legacy-sqlite` — Read an old SQLite database out as JSONL.
  - `bd migrate from-server-to-proxied-server`,
    `bd migrate from-proxied-server-to-server`,
    `bd migrate from-shared-server-to-proxied-server`,
    `bd migrate from-proxied-server-to-shared-server` — Experimental
    switches between server modes; no data moves.

## Capabilities most worth adopting

*Our use*, as recommendations for the owner:

- **Claims and leases** (`ready --claim`, `heartbeat`, `reclaim`) instead of
  informal assignment, so parallel agents never double-take work.
- **Gates** for waits on CI, PRs or a human, so blocked work is explicit
  and `ready` stays honest.
- **`bd human`** as the single queue of questions for the owner.
- **Provenance** to tie beads to the commits and PRs that closed them.
- **Formulas and molecules** for workflows we repeat (reviews, releases,
  upgrades like the 1.3.0 one).
- **`bd --readonly` with `export` and `--json` reads, typed by
  `bd schema`,** as the dashboard's data interface.
