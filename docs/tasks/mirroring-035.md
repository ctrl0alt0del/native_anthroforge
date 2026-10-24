# Mirroring 0.3.5 runtime implementation

- Task branch: `codex/mirroring-035`
- Integration branch: `main`
- Starting revision: `1696687`
- Status: in progress; not release-qualified
- Last updated: 2026-10-24, Europe/Bucharest
- Active writer: local Codex session

## Outcome and acceptance

Implement [the confirmed specification](../specification_035.md) through
[the integrated plan](../implementation_035.md), desktop and Qt-free headless clients.
Strict read-only source reflection is invariant. No independent mirror solvers,
tree nodes, per-object mirror action, detachment or counterpart migration.

## Current state

Read specifications, engineering rules and current typed model. Starting from main;
unfinished `codex/parity-workflows-034` and unrelated root `__init__.py` are preserved.
Research: Qt 6.12 material front faces use counterclockwise winding; reflection/query
and render orientation must be handled explicitly, not hidden with double-sided shading.
No runtime implementation or acceptance evidence yet.

## Next actions

1. Trace provider/reference, persistence, mutation and viewport ownership boundaries.
2. Implement foundations with shared API and desktop controls and contract tests.
3. Integrate reflected queries, relationships, symmetric constructions and lifecycle.
4. Qualify correctness/performance/packaging; update versions only when complete.

## Verification

Pending. Checks remain background-only; do not claim interactive acceptance.
Checkpoint coherent increments and push before long checks or interruptions.

## Recovery inputs

Use existing .venv, native build/load infrastructure and tools/check.ps1.
No new production anatomy assets belong in Git. Prior source inventory is in the plan.
