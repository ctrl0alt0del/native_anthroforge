# Selectable fiber propagation methods

- Branch: `codex/fiber-propagation-methods`, based on the reviewed SCM experiment.
- Integration: `main`; preserve unfinished 0.3.4 and unrelated root `__init__.py`.
- Status: implementation in progress. No production qualification yet.

## Confirmed contract

Preferences selects **Smooth Shape Preservation** (new default) or **Local Surface
Following** (existing behavior). Applies to future calculations only; queued work
captures at dispatch. Current results, running work, project state and undo stay intact.
The method belongs to Fiber attachment propagation, not the SCM muscle or a path engine.
ROUTED remains distinct; no planner or collision repair is introduced by smoothing.

## Ownership and delivery

Native attachment preparation owns reference geometry, regional fits, arc-length weights,
exact pins and sparse differential reconstruction. Python packs immutable inputs and
uses the existing bounded/profiler-visible cache. Existing material correspondence handles
changing parent topology. Preserve pins, junctions, closed curves, handles and current-shape
editing. Capture reference frames explicitly for new fields; qualify older field loading.
Shared evaluation, edits, conversion, inspection/replay and desktop preference controls
must use dispatch-captured policy. No global native method switch or competing scheduler.

## Validation pending

- Exact reviewed SCM case, production parity with the prototype and local-method parity.
- Neutral/rigid transforms, open/closed paths, interior pins, handles, junctions, changing
  material topology, cancellation, cache lifetime, save/reopen and preference lifecycle.
- Development gate; offscreen UI; canonical 0.3.5 portable build and source archive.
- Profiler, actual shape review and ownership review; no interactive acceptance claim.

Research/evidence: [SCM experiment](scm-ribs-distortion.md), CH-077 and
[Eigen sparse LDLT](https://eigen.tuxfamily.org/dox/classEigen_1_1SimplicialLDLT.html).
