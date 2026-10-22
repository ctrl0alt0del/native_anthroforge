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
Next: step 2 provenance/validation/resource observation. Preserve baseline native DLL
at build/vcp-performance-024-release/baseline-af_native.dll; freeze edit replay before
numerical changes. Remaining steps and release qualification are pending.
