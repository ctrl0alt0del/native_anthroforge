# Selectable fiber propagation methods

- Branch: `codex/fiber-propagation-methods`, based on the reviewed SCM experiment.
- Integration: `main`; preserve unfinished 0.3.4 and unrelated root `__init__.py`.
- Status: implementation and focused qualification complete; final gate, packaging and merge pending.

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

## Qualification checkpoint

Native sparse reconstruction, capture metadata, preference/UI selection, dispatch
integration and inspection replay are implemented. The SCM production paths match the
approved prototype within 7.5e-11 model units. In 15 warm counterbalanced trials, the
three paths take median 2.90 ms (old method 2.98 ms). Surface/base/rest/final findings
contain zero crossings and degenerates; original method has 222 base and 245 rest/final
crossings. Profiler and geometry evidence: `build/fiber-propagation/scm/`.

All 326 assembly fibers retain their neutral positions within 1.13e-10 model units.
The complete Ribs Top Radius 3 update now finishes without calculation errors (7.24 s,
single trial, not a speedup claim). History/save checks are pending completion.
Offscreen Preferences passes, screenshot inspected; no interactive acceptance claim.
Focused propagation/material/architecture tests: 16 pass. Ruff/format/mypy pass.

Compatibility fixes: materialize Eigen's solve before indexed assignment; solve for
correction relative to the candidate to avoid cancellation; group historical duplicate
supports without rewriting exact pin records; validate legacy bind frames against stored
capture evidence and document-frame hints. Ignore loose vertices and irrelevant tissue
sides. Synthetic material records must mark the absent secondary flow binding as -1,
not zero. Dense (>512 sample) compact filtering uses prefix moments rather than quadratic
convolution. No silent switch to the old propagation method.

Remaining: full development gate, actual production geometry visual review, canonical
portable package/source archive, ownership review, final documentation and validated merge.

- Exact reviewed SCM case, production parity with the prototype and local-method parity.
- Neutral/rigid transforms, open/closed paths, interior pins, handles, junctions, changing
  material topology, cancellation, cache lifetime, save/reopen and preference lifecycle.
- Development gate; offscreen UI; canonical 0.3.5 portable build and source archive.
- Profiler, actual shape review and ownership review; no interactive acceptance claim.

Research/evidence: [SCM experiment](scm-ribs-distortion.md), CH-077 and
[Eigen sparse LDLT](https://eigen.tuxfamily.org/dox/classEigen_1_1SimplicialLDLT.html).
