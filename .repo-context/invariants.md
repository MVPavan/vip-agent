# Invariants

Owner-decided or recorded constraints. Changing one needs the owner; surface
conflicts rather than working around them. Add mechanical checks as the
implementation develops.

## Decided

1. **Beads is the source of truth for work state.** Status and counts come
   from each project's Beads database. The dashboard reads Beads and never
   writes to it. Source: owner brief, 2026-09-29.
2. **Public repository.** No secrets, credentials, personal data,
   machine-local paths or tracked-project lists in commits; those live in
   gitignored `*.local.*` files. Source: owner, 2026-09-30.
