# Computation inventory and approach history

- Task branch: `codex/computation-history`
- Integration branch: `main`
- Starting revision: `a93b5149e853eefd71a7875a3885a3a68a1d4a3a`
- Status: complete; documentation validated
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Inventory the computations implemented in the standalone application and establish
one maintained document recording changes to computational approaches: why the old
approach failed, what replaced it, why that addresses the cause, and observed evidence.
Include the recent tissue correction and evidence-backed earlier changes.

## Decisions and relevant files

- [Computation history](../computation_history.md) combines stable computation IDs, current source
  ownership, validation entry points, and chronological change records.
- Keep numerical work separate from scheduling, presentation and storage workloads.
  Planned skin/mirroring/dynamics are not implemented computations.
- Link the register from README/architecture and require updates in engineering
  guidelines and AGENTS.md. No runtime or product-behavior changes.
- Use existing task records, source and fixture provenance; do not invent historical
  timings or claim local-only artifacts are available in a cloud checkout.

## Current state

Completed the inventory of 57 computational families across mesh/primitive/deformer,
curve, attachment, surface, tissue, stacking, spatial/image and supporting runtime work.
Each row links current ownership and maintained validation entry points. Registered job
families are mapped; planned/unimplemented capabilities are explicitly excluded.

Backfilled 10 qualified approach-change records from existing source/task/fixture
evidence, including the recent inflation, refinement, geometry validation and
iteration-limit corrections. Records distinguish outcomes, failed alternatives,
historical revisions and local-only artifacts. The entry template defines future updates.

README and architecture link the register. AGENTS and engineering guidelines require
updating it with every computational approach change. No runtime files, tests, package
artifacts or user projects were changed.

## Verification

Content reviewed against native public interfaces/build sources, application evaluation
and scheduler registrations, current specifications, and cited historical task evidence.
Corrected the stacking-validation ownership link after inspecting the actual call path.
Verified unique stable IDs (57 computations, CH-001 through CH-010), all 17 referenced
commit IDs via `git cat-file -e`, and relative files/headings with a local Python link audit.
The main register and four navigation/rule documents passed all 325 checked relative links;
the task record adds its validated link to the register. `git diff --check` passes.
No runtime tests/build or interactive desktop work: this change is documentation only.

## Next actions and blockers

No remaining content blockers. Commit/push this validated documentation and integrate
against unchanged `main` through the normal merge/push workflow. Git ancestry records
completion of that step; do not infer remote delivery from this file alone.

## Recovery inputs

Current implementation baseline is the starting revision above. Earlier evidence lives
in `docs/tasks/` and `native/migration/`; local tissue reproductions are under
`build/muscle-height-smoothing/` and are not committed. Preserve unrelated `__init__.py`.

The containing commit identifies this checkpoint; confirm remote reachability before
assuming it is recoverable elsewhere.
