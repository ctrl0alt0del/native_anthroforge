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
build/standalone-optimizations/baseline.

Stage 1 is integrated: a bounded application ChangeJournal describes record/field
changes, SceneProjection caches scene metadata and parent choices, and desktop-owned
PropertyProjection objects notify individual QML fields while preserving curve/point
and outliner identities. Authored dataclasses are projected without repeated deep
serialization. Visual-layer arrays are prepared once per component geometry update.
RenderModel retains existing staged leases; picking changes with displayed results.

425 tests, lint and mypy pass. Primitive and curve interaction GUI acceptance pass;
loft/lattice screenshots were inspected. A transient undefined-to-bool warning in the
outline visibility binding was fixed. Serial ABBA open-Activity mouse drags (80 events
per normal/Ctrl gesture) measured baseline handler means 12.41-13.83 ms and candidate
5.21-5.97 ms. Both recorded comparison runs stopped successfully. The candidate pilot
capture retained all events and reported zero curveChoice model replacements. Complete
comparison artifacts: build/standalone-optimizations/stage1-comparison. These are stage
measurements, not final integrated results. PySide 6.12 exposes only QQmlPropertyMap's
deprecated constructor; Python emits a deprecation warning, while actual QML has no
warnings. This adapter is isolated in desktop/property_projection.py.

Stage 2 is integrated: snapshot-owned, immutable entity/control lookups and hierarchy/
dependency indexes reuse fully validated relationship structure across value-only
changes. Relationship changes still run complete validation and rebuild their graph.
Revision-only replacements reuse the entire index. Runtime indexes are excluded from
project serialization. Native attachment ordering is linear instead of repeated scans.
431 tests and configured mypy pass, including structural invalidation, identity
collisions, cycle classification, historical snapshot isolation and serialization.
The 1,024-SCP synthetic admission median is approximately 1.4 ms versus the audit's
86.8 ms. This measures admission without worker dispatch or GUI. Evidence and an
ordinary runtime profiler capture are in build/standalone-optimizations/stage2.

Next: native intermediate geometry/finalization and active-job indexing, in that order.
Final integrated gate, broader GUI/native parity and packaging remain pending.

## Recovery

Normal Windows development setup applies. Measurements and raw captures stay under
build/standalone-optimizations; commit compact evidence with its provenance. The
baseline is reproducible from the named Git revision. Preserve unrelated __init__.py.
