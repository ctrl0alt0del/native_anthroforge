# Preferences and ROUTED backends — 0.2.3

- Task branch: `codex/preferences-routing-023`
- Integration branch: `main`
- Starting revision: `e703c68`
- Status: in progress
- Last updated: 2026-10-21
- Active writer: desktop chat, direct work

## Outcome and acceptance

Deliver Preferences with a persistent Custom / PIQP choice for ROUTED curves and
fibers, backed by the shared headless application API. Release 0.2.3 with one canonical
portable distribution and companion source archive. Background-only validation.

## Decisions and ownership

- Default remains Custom; PIQP means the sparse backend qualified in the
  [benchmark](routing-piqp-benchmark.md), using existing pinned PIQP 0.6.4.
- Preferences belong to the application, outside project revisions and undo.
- Native per-invocation options select the QP implementation; no ambient thread-local
  backend switch, fallback, Python numerical loop, or separate worker pool.
- Preserve routing planning, exact pins, corner retention, collision acceptance,
  cancellation, dependent surfaces and attachments. Document computation changes.
- Asked whether changing the preference applies on future evaluations or schedules
  existing routes immediately; answer pending. Independent foundation work can proceed.

## Current state

Native per-invocation backend, sparse adapter, preference storage and desktop editor
implemented. Custom remains default. Future-dispatch semantics implemented provisionally
while the optional question is pending. Both ordinary path jobs and conversion previews
capture preferences at dispatch. Reports retain backend provenance. Shared reference
fixtures moved into a test helper used by the benchmark and production qualification.

Also corrected the measured Custom active-set cap mismatch: do not change the active
list after the final candidate solve. This preserves matching multipliers/candidate and
removes a possible out-of-bounds downstream read; no acceptance checks weakened.

## Verification

50 focused tests passed: both backends on 18 compact cold/warm fixtures, independent
clearance/pins/layout, concurrent calls, cancellation, preference persistence, running
and queued dispatch, Manual mode, saved backend provenance, and function limits.
Initial native build/three contracts and mypy passed. New native cap regression,
dependent material tests, offscreen UI, full gate and portable release remain pending.

## Next actions

1. Implement native per-job backend contract and sparse PIQP adapter.
2. Add persisted application preferences and desktop editor; integrate dispatch capture.
3. Validate, document, package 0.2.3, merge and push under continuity workflow.

## Recovery inputs

Use normal Windows setup. Benchmark fixtures are under `tests/fixtures/routing`;
optional local skull capture is `build/skull-routing-inputs.json`. No interactive
desktop acceptance is authorized by this task. Read current diff before resuming.
