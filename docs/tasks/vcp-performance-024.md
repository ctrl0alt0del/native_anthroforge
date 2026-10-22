# VCP performance optimization — 0.2.4

- Status: implementing, not release-ready.
- Branch: `codex/vcp-performance-024`; integration: `main`.
- Baseline: `52690bd` (0.2.3, completed performance analysis).
- Scope: implement the six recommendations in [the analysis](../vcp_performance_024.md)
  in order; qualify geometry, attachments, lifecycle and measured performance; deliver
  one canonical 0.2.4 portable package and companion source archive.
- Direct work, no subagents; background/offscreen validation only. Preserve original
  anatomical fixtures and unrelated untracked root `__init__.py`.

## Contracts

No changes to authored geometry meaning, retained anatomical bindings, accepted/manual
provenance, correspondence, numerical tolerances, exact constraints, cancellation,
undo/checkpoint semantics, or issue findings. C++ owns numerical work. Native mutable
contexts require exclusive leases; caches remain bounded and revision-qualified.

## Delivery sequence

1. Prepared tissue-inspection presentation and narrow visibility notifications.
2. Result provenance, typed structural validation reuse, profiler resource observation.
3. Incremental Fiber collision evidence and retained native scene preparation.
4. Stacking context reuse, native obstacle handles and metadata-only planning.
5. Native height-smoothing formulation experiment; adopt only qualified improvement.
6. Native tissue material/operator/intermediate preparation, driven by measurements.
7. Combined regression/parity, profiler/off recordings, offscreen GUI and packaging;
   update computation history, documentation and versions; validated merge/push.

## Evidence

Baseline evidence and disposable probes: `build/vcp-performance-024/` (local-only).
The 96-tissue assembly is supplemented by smoothing, relaxation and stacking fixtures.
Use actual production geometry/attachment tests and frozen baseline outputs; API
success alone is insufficient. Keep profiler overhead separate from recorder-off timing.

## Recovery

Step 1 implemented and measured (CH-039): 10 targeted tests pass, dispatch 47–48 ms
versus 632–650 ms; hidden repeated-edit settling 1.21 s versus 3.56–3.66 s.
Step 2 implemented and measured (CH-040): 26 focused checks pass; recorded ribs
4.65 s versus 7.50 s, off 4.21–4.32 s versus 4.54–4.62 s. No profiler resource loss.
Step 3 implemented (CH-041): native context reuses colliders and pair evidence,
30 focused checks plus failed-capture recovery; profile-edit settle 221–324 ms.
Ribs timing needs counterbalanced recheck; do not claim its improvement.
Step 4 implemented (CH-042): exclusive pooled contexts, native obstacle handles,
metadata plans; existing 63 tests and new ownership/parity checks pass. Warm unchanged
plan ~1–2 ms and final ~5–6 ms; changed-input benefits still need measurement.
Step 5 qualified (CH-043): reduced fixed-variable/box formulation is 1.56–1.60 s
versus 1.77–1.82 s in alternating trials; original certification remains, max delta
3.94e-13 m, 24 focused checks pass.
Step 6 implemented (CH-044): immutable frames/operators, per-column coefficients and
internal draft envelope sides. Exact changed-settings parity; median profile 30.3→23.0 ms,
Distributed 67.0→39.9 ms. Focused checks pass. All 11 combined assembly replay snapshots
(1,456 arrays each) match baseline exactly; bone/Fiber motion and undo included.
Changed-provider/receiver stacking matches fresh sessions. Preparation clears cannot
retain a capture from a discarded document. Full development gate running at
build/vcp-performance-024-release/development-gate.log. Next: serial baseline/candidate
timings, profiler and hidden viewport, release package. Do not benchmark during builds.
Preserve baseline native DLL
at build/vcp-performance-024-release/baseline-af_native.dll; baseline-replay/ now freezes 11 snapshots of 1,456 arrays before
numerical changes. Remaining steps and release qualification are pending.
