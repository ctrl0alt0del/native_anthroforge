# Computation inventory and approach history

- Task branch: `codex/computation-history`
- Integration branch: `main`
- Starting revision: `a93b5149e853eefd71a7875a3885a3a68a1d4a3a`
- Status: in progress
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Inventory the computations implemented in the standalone application and establish
one maintained document recording changes to computational approaches: why the old
approach failed, what replaced it, why that addresses the cause, and observed evidence.
Include the recent tissue correction and evidence-backed earlier changes.

## Decisions and relevant files

- `docs/computation_history.md` will combine stable computation IDs, current source
  ownership, validation entry points, and chronological change records.
- Keep numerical work separate from scheduling, presentation and storage workloads.
  Planned skin/mirroring/dynamics are not implemented computations.
- Link the register from README/architecture and require updates in engineering
  guidelines and AGENTS.md. No runtime or product-behavior changes.
- Use existing task records, source and fixture provenance; do not invent historical
  timings or claim local-only artifacts are available in a cloud checkout.

## Current state

Read repository rules, architecture, tissue specification and native build inventory.
Auditing native public interfaces and application task/evaluation paths.

## Verification

Pending source coverage, relative-link/anchor review and `git diff --check`.
Documentation-only task: no application rebuild or GUI interaction is needed.

## Next actions and blockers

1. Finish categorized computation and validation inventory.
2. Write confirmed history and reusable entry requirements; integrate maintenance rules.
3. Validate links/content, checkpoint and perform the validated merge/push.

## Recovery inputs

Current implementation baseline is the starting revision above. Earlier evidence lives
in `docs/tasks/` and `native/migration/`; local tissue reproductions are under
`build/muscle-height-smoothing/` and are not committed. Preserve unrelated `__init__.py`.

The containing commit identifies this checkpoint; confirm remote reachability before
assuming it is recoverable elsewhere.
