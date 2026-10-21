# Tissue intersections and downstream query policy

- Task branch: `codex/tissue-intersection-policy`
- Integration branch: `main`
- Starting revision: `6918888`
- Status: investigation and implementation in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Permit self-intersections within one tissue without repairing or changing inflation
and height-smoothing formulas. Document this explicit product decision and revisit it
if downstream defects appear. Keep nonfinite/degenerate-geometry protection.

Centralize preview versus confirmed attachment queries. Confirmed placement uses a
Boolean-cleaned target query representation; Fiber/Anchor conversion and explicit
rebind must use it. Preserve original material identities and ongoing binding
resolution; temporary cleanup must not mutate the displayed target or shared sources.
Resolve ambiguous stacking support at the farthest surface along the base normal.
Skin construction remains deferred.

## Current findings

- `tissue_create.anthroforge` CTRL_POINT inflation is rejected by shared deformation
  validation before smoothing. Prior diagnosis reproduced 106 new transverse
  crossings at amount 0.599 and zero collapsed faces. The unchanged inflation kernel
  has a discontinuous direction at its zero-depth control point and can overtake
  fixed boundaries. This task changes acceptance, not that formula.
- Point/Anchor and Curve/Fiber conversion already share native nearest-surface
  capture, but that capture and interactive snapping currently query raw triangles.
- Stacking material correspondence currently picks minimum absolute chart distance.
- Confirmed decision: build an actual Boolean-cleaned mesh, retain it only in memory
  for query validation, and never replace the original tissue. Temporary closure
  against the material base is authorized; added backing/closure faces are not
  attachment targets. Preserve original triangle and barycentric provenance.

## Implemented checkpoint

Native tissue acceptance now permits crossings while preserving finite-coordinate,
identity and new-collapse checks. Inflation, parts, smoothing and direct/native
relaxation share this policy; strict diagnostic validation remains unchanged.
The production formulas and smoothing solver are untouched. README, specification,
architecture, migration notes and computation history CH-016 record the decision.
Attachment query cleanup and stacking changes are not implemented yet.

## Verification

- Windows native build and all three CTest targets pass.
- 29 targeted pytest cases pass (intersection policy, relaxation acceptance,
  mesh-quality diagnostics, native inflation and earlier inflation regressions).
- Full pytest suite: **1,421 passed** in 112.97 seconds on the acceptance checkpoint
  `e922aeb`; only existing Qt deprecation warnings. Mypy and focused Ruff checks pass.
- Clang-tidy passes for all five changed C++ translation units; only suppressed
  external/header diagnostics are reported.
- The actual user file, adopted in memory and recomputed at amounts 0.2 then 0.599,
  now reports ready base/rest/intrinsic/final results. Original file unchanged.
- Base and single-sided output each have 168 open boundary edges. The user approved
  temporary base-backed closure; qualification against this actual fixture is next.
- Full development gate, visual and portable qualification are pending. Not merge-ready.

### Temporary query qualification (2026-10-21)

Read-only experiment on the actual source, using the installed compiled libigl/CGAL
diagnostic wheel. Both raw and height-smoothed outputs close against the original
material base with zero boundary edges. Original triangles keep their source IDs;
added base/side faces are tagged unselectable. No document geometry is replaced.

- Ordinary positive-winding union takes about 0.7 seconds here but drops a visible
  reversed-orientation lobe. A closed input alone does **not** establish suitable
  placement semantics. This variant is not accepted as the production solution.
- Exterior-cell extraction retains 5,127 selectable fragments and preserves the
  exposed lobe. Nonzero winding is another candidate; it can retain sealed-cavity
  boundaries, whereas exterior-cell extraction excludes them. This policy distinction
  is not evidence that this fixture has a meaningful sealed cavity. Initial diagnostic
  emulation using two unions generated extra fragments; use the direct native custom
  winding operation for qualification, not the double-rounded two-union emulation.
- Every selectable output corner maps to its original source triangle. Maximum
  reconstructed position error is 1.03e-12 metres; minimum computed barycentric
  weight is -1.64e-11 from floating-point reconstruction near edges. These are
  per-face correspondences, not unique source identities for intersection vertices.
- Confirmed: exclude sealed-cavity faces. Use exterior-cell extraction for confirmed
  placement; preserve the original target and original material coordinates.
- Follow-up scope: implement farthest-normal ambiguity handling in stacking and inspect
  desktop ellipses, correcting unnecessary truncation without destabilizing layouts.
- Native C++17 qualification compiled successfully with CGAL 6.1.1 and Boost 1.89.0
  under ignored `.tools/boolean`, serial libigl work and Boost exact arithmetic.
  On this fixture: positive union 2,442 selectable fragments / 0.682 seconds;
  direct nonzero winding 5,125 / 0.658 seconds; exterior cell 5,127 / 0.646 seconds.
  These are single diagnostic timings, not application responsiveness measurements.
  Production dependency configuration and query integration are not implemented.

Local diagnostics: `build/tissue-intersection-policy/boolean_trial.py`,
`inspect_proxy.py`, `provenance_check.py`, `native/`, `query-winding.png`,
`provenance.json`. CGAL archive SHA256
`52506935f70e247ed2777e3c65f20e86f79208c2a2d0e180ae7475daf11c96ef`;
Boost archive SHA256
`85a33fa22621b4f314f8e85e1a5e2a9363d22e4f4992925d4bb3bc631b5a0c7a`.

Stacking inspection: its `Side.direction` is the inflation displacement/limiting
direction, not necessarily the geometric base normal (especially Control Point mode).
The current inverse chart query chooses minimum absolute distance along that field.
Simply replacing minimum with maximum would not implement the user's requested
farthest-normal support. Preserve vector transport and exact constraints while adding
and testing an explicit support-selection policy; no stacking kernel has been edited.

Research: [libigl Boolean arrangements](https://libigl.github.io/tutorial/#boolean-operations-on-meshes)
and [CGAL Polygon Mesh Processing](https://doc.cgal.org/latest/Polygon_mesh_processing/index.html).
Splitting intersections alone (`RESOLVE`) does not remove buried faces.

## Next actions

1. Qualify temporary closure and Boolean provenance on the actual failing tissue.
2. Implement scoped acceptance and query/stacking policies with material provenance.
3. Test the real fixture, shared attachment callers, stacking ambiguity and lifecycle;
   run development and packaged/offscreen checks before integration.

## Recovery inputs

User fixture: `E:/development/WIP_models/tissue_create.anthroforge` (read-only).
Ignored earlier diagnostics: `build/tissue-create-diagnosis/`; original SHA256
`3cc32677bf56f1f14fafd36dc36572a77d8c0b3ab69e8076f8740dc84a322d28`.
Unrelated untracked root `__init__.py` must remain untouched. Background-only checks.

## Production query checkpoint (in progress)

Native CGAL/Boost adapter, source-preserving query mesh, bounded cache, shared
Fiber/Anchor/constraint captures and asynchronous final curve-snap command are now
implemented. 32 targeted attachment/query/architecture tests passed before the SCP
capture extension; the three new authored snapping lifecycle tests and function
limits also pass. Mypy passes (286 files). Original result geometry is unchanged.

Remaining: integrate drawing/point/cursor confirmation and displayed tissue targets,
qualify SCP recapture scheduling, implement normal-ray stacking ambiguity, audit UI
ellipses, run full development/visual/package gates and update dependency distribution.
This is an incomplete recovery checkpoint, not a release or merge candidate.

## Drawing and stacking checkpoint

Implemented confirmed drawing, discrete point creation, branched point continuation,
cursor placement and displayed tissue snapping. Placement intent stays native/owned;
fitting and exterior query work run in existing coordinator workers. A later point edit
supersedes the old request, while Undo restores the pending placement in its own step.
The shared headless projection API now accepts PREVIEW/CONFIRMED modes and role-aware
surfaces. Preview remains its default.

Stacking now selects the farthest distinct positive hit along geometric base normals
when support is ambiguous. Ordinary donor vector transport and exact constraints remain.
All 14 donor cases and three new ambiguity/cache cases pass. Native build/3 CTests pass.
Original donor hashes were preserved; maintained source checksums record intentional changes.

Dependency distribution now includes pinned CGAL/Boost notices and corresponding headers
in the companion source archive, with bundled offline CMake discovery. Qualification pending.

Remaining: UI ellipsis reproduction/fixes, complete gate and actual-shape/offscreen evidence,
dependency archive/configuration and canonical portable packaging. Not merge-ready.

## UI and geometry qualification

- Full pytest at the placement/stacking checkpoint: **1,438 passed**. Full native
  clang-tidy completed successfully. The combined development gate is running.
- A 280px property panel reproduced truncation of "Across strips · 0 keeps fitted
  density". Shared numeric labels now wrap; check labels and detail values can wrap;
  popup choices and menus size to content, with full text available for clipped selected
  names. Immediate Edit/Delete/footprint actions no longer carry a misleading ellipsis.
- Narrow surface and curve inspectors, long popup choices and Help menu pass offscreen
  at normal and 200% scale. Screenshots were inspected. Numeric dragging keeps its field
  bounds/focus through temporary diagnostics, and one-action Undo passes.
- Expanding tissue relationship details exposed an SCP-only attachment-inspection
  dispatch bug. The shared inspector now dispatches only SCPs to the SCP binding decoder;
  tissue relationships stay construction-based. Regression test passes.
- Actual source recomputation at 0.2 then 0.599 has ready base/rest/intrinsic/final.
  Production query: 3,240 original triangles, 5,127 selectable exterior fragments,
  0.698 seconds in one local run (not a responsiveness benchmark). Inspected the original
  and query surfaces and the folded-provider stacking cross-section. Original file SHA256
  remains unchanged. Local images are `production-query.png` and `stacking-normal.png`.
- Production held-key/mouse offscreen checks pass: snapping target switching, Ctrl release,
  insertion, undo, focus rules and both projection modes. Hidden texture-rendered drawing
  passes with no visible window. No physical desktop interaction acceptance is claimed.

Remaining: full gate completion, offline bundled dependency build and canonical package
qualification. Added a clean-CLI cavity fixture testing surface confirmation, Fiber and
Anchor original-material capture; it passes from source and awaits the portable executable.

## Final runtime checkpoint

The complete development gate passed at `010a948`: 1,439 tests, native CTests, all native
style checks, Python lint/format/typing, PowerShell limits, numerical imports and doctor.
Bundled source rebuilt `af_boolean` offline with FetchContent downloads disabled.
The real source also produced `production.afprofile.zip`; native Boolean work appears
separately in the existing trace without new feature-specific instrumentation.

Two additional lifecycle tests check target motion/Undo and transform-parent motion.
The latter exposed double movement from reusing a stale preview coordinate. Confirmed
intent now carries the actual anchor component identity and resolves its current world
position at dispatch. Six snap lifecycle tests and the production offscreen gesture
suite pass after this correction. Final full Python suite and rebuilt portable checks
are next; native code has not changed since the passing complete gate.

Final full suite after the anchor correction: **1,441 passed**, with existing Qt
deprecation warnings only. Ownership review retained one query service/cache and one
coordinator, native numerical kernels, original material ownership, and shared history
publication. Generic ray validation belongs to `placement_inputs`; cursor placement
does not depend on the curve command's component validation. That final responsibility
cleanup passes lint, typing and 13 placement/lifecycle/architecture tests.

The final ownership pass also supplies accepted triangle counts to the dedicated
surface-query scheduler, using metadata only. Its existing triangle-based estimate
now sees the actual workload for both curve and cursor placement; all such work
remains on coordinator workers. The cube lifecycle case verifies 12 input triangles.

Portable builds remain canonical under `dist/0.2.2/AnthroForge.dist`; the final executable
qualification and source archive refresh remain pending. No new release directory exists.
