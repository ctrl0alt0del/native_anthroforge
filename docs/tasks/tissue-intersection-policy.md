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
- A focused question is pending: should confirmed snapping exclude all faces inside
  sealed cavities? Recommended exterior-cell extraction matches outside-accessible
  placement; this is not yet selected as production behavior.
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
