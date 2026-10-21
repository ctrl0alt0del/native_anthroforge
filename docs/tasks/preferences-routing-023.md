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

Inspected repository rules, current routing boundaries and benchmark adapters. No
implementation changes yet. Preserve unrelated untracked root `__init__.py`.

## Verification

Pending: native backend parity/lifecycle, preference persistence/API isolation,
offscreen interaction and screenshots, development gate, packaged qualification.

## Next actions

1. Implement native per-job backend contract and sparse PIQP adapter.
2. Add persisted application preferences and desktop editor; integrate dispatch capture.
3. Validate, document, package 0.2.3, merge and push under continuity workflow.

## Recovery inputs

Use normal Windows setup. Benchmark fixtures are under `tests/fixtures/routing`;
optional local skull capture is `build/skull-routing-inputs.json`. No interactive
desktop acceptance is authorized by this task. Read current diff before resuming.
