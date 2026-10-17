# Standalone performance implementation

- Branch: codex/standalone-optimizations
- Integration: main
- Baseline: d810557795c2af002da0d86cfa7797317f9af4c4 (0.1.5)
- Status: in progress
- Updated: 2026-10-18, Europe/Bucharest
- Writer: desktop implementation chat; direct work, no delegation

## Scope and order

Implement the four measured opportunities in [the audit](standalone-optimization-audit.md):
incremental desktop projections, indexed immutable document/dependency structure,
native intermediate geometry with deliberate finalization, and active scheduling
separate from completed history. Preserve all confirmed editing, geometry, dependency,
undo/redo, cancellation, checkpoint and persistence contracts. Follow engineering guidelines.

## Acceptance and evidence

Use serial profiler/unrecorded comparisons, existing cube/Body gestures, synthetic
scaling and long-session cases, native parity, shared-contract tests, the full
development gate, actual GUI inspection and portable qualification. Do not claim
whole-app improvements from native microbenchmarks or sum inclusive profiler spans.
Review ownership separately from passing checks. No new product feature or version
number is specified; retain 0.1.5 and record the source revision of the delivered build.

## Current state and next action

Baseline source/native snapshot is preserved under ignored
build/standalone-optimizations/baseline. Initial work is desktop projection ownership,
stable inspector choices and change-specific notifications. No production edits yet.
Implement and verify each increment before proceeding to the next; checkpoint about
every ten minutes. Final integrated gate, GUI, native parity and packaging are pending.

## Recovery

Normal Windows development setup applies. Measurements and raw captures stay under
build/standalone-optimizations; commit compact evidence with its provenance. The
baseline is reproducible from the named Git revision. Preserve unrelated __init__.py.
