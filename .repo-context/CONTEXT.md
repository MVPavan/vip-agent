# vip-agent

vip-agent gives the owner one view over their coding agents and the
projects those agents work on. Terms below are provisional until the
dashboard design is approved.

**Tracked project**:
A local repository with a Beads workspace, registered with the dashboard by
its folder path. The list of tracked projects is machine-local configuration.
_Avoid_: workspace (Beads' own term for `.beads/`)

**Stored status**:
An issue's status as Beads records it: `open`, `in_progress`, `blocked`,
`deferred` or `closed`. The only source for status and counts.

**Rollup**:
A figure the dashboard derives from an issue's children, such as "5/7 closed".
Shown next to the stored status, never in place of it.
_Avoid_: derived status

**Progress file**:
A fixed-format file an agent writes per active task in a tracked project,
carrying what Beads does not: current activity, a short summary and open
questions for the owner.
