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
- Standard solid Boolean union needs an inside/outside definition. Single-sided
  tissue and base-role targets can be open sheets. Their intended cleanup requires
  a concrete product decision; no silent cap, thickness or replacement is authorized.

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
- Base and single-sided output each have 168 open boundary edges; clarification
  requested about a temporary base-backed volume for confirmed cleanup. No answer yet.
- Full development gate, visual and portable qualification are pending. Not merge-ready.

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

1. Settle open-sheet confirmed-query semantics using actual source topology evidence.
2. Implement scoped acceptance and query/stacking policies with material provenance.
3. Test the real fixture, shared attachment callers, stacking ambiguity and lifecycle;
   run development and packaged/offscreen checks before integration.

## Recovery inputs

User fixture: `E:/development/WIP_models/tissue_create.anthroforge` (read-only).
Ignored earlier diagnostics: `build/tissue-create-diagnosis/`; original SHA256
`3cc32677bf56f1f14fafd36dc36572a77d8c0b3ab69e8076f8740dc84a322d28`.
Unrelated untracked root `__init__.py` must remain untouched. Background-only checks.
