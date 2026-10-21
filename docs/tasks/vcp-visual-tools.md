# VCP visual tools: recommendations 4–7

- Task branch: `codex/vcp-visual-tools`
- Integration branch: `main`
- Starting revision: `f6a4b68df3ae5a4f577dce3500d567405dab77bc`
- Status: in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: current desktop chat; direct work, no delegation

## Outcome and acceptance

Implement the remaining four recommendations from the VCP audit:

4. Evaluated stacking relationships: providers/receivers, calculated overlap footprints,
   and stacking displacement, distinct from authored relationship settings.
5. Tissue field brush painting: radius/falloff, surface colors, one undo action per stroke,
   and inspection of constraint goals and resulting displacement.
6. Tissue cross-sections: movable planes, contours, local cutaways and matched stage views.
7. Routed curve/Fiber diagnostics: optional native capture of planner/solver paths, contacts
   and termination details, with bounded storage and revision-qualified report evidence.

Keep existing inflation, smoothing, stacking and routing semantics. Inspection is read-only;
painting uses shared authored-field operations. All numerical loops and geometry queries
remain native. Self-intersections remain allowed. Background-only GUI qualification.

## Decisions and relevant files

User confirmed visible-surface painting by default, with optional Paint Through.
Optional UX questions remain unanswered: selected-tissue versus scene section default;
separate route diagnostic run versus capture during regular recalculation.
Working section default is selected tissue plus its comparison stages, with an explicit
surrounding-geometry toggle. This is an implementation assumption, not a confirmed answer.
Reuse tissue inspection jobs, accepted material data, stage comparisons, Issues, staged
render leases and frozen report export. Reuse transactions and keyboard routing for painting.
One canonical 0.2.3 distribution and source archive; no release-version change requested.
Source audit recovered from this chat, recommendation IDs E03/F05, E05, F07/F11 and F09.

Official references: Qt 6.12 CustomMaterial shader/discard contract;
CGAL Polygon_mesh_slicer; Blender weight-paint radius/falloff/stroke semantics.
Research informs adapter choices, not a claim of geometry qualification.

## Current state

Implemented read-only native production support-mask queries, accepted-plan validation,
provider/receiver display, intrinsic footprints, displacement comparison, matching staged
picking and frozen report evidence. Reused the inspection scheduler through query policies.
Excluded relationships report geometric order separately from active support.
Weight painting now has native visibility/material sampling, bounded projection caches,
worker previews, direct desktop brush controls and one shared commit per released stroke.
Visible-only/Paint Through, external occlusion, rate independence, Base/Rest undo, stale
inputs, cancellation and staged colors have focused tests. Hidden GPU preview/export passed;
the colored tissue capture was inspected. Sections now have native contours, shader cutaways,
matching original-triangle picking, comparison stages, controls and frozen report settings.
Native/API/view tests and hidden GPU section captures passed. Optional bounded native route
capture now records planner/seed/trial/final paths, contacts and termination, with shared
Fiber/junction input resolution and read-only jobs. Desktop step selection and frozen export
are integrated; route-specific hidden GPU, failure and storage-limit checks passed. Both solver
backends match normal output in focused tests, including moved Fiber attachments (25 tests).
Working route default is an explicit separate diagnostic run, starting at the planner;
users can retain the normal warm-start policy. This does not publish geometry.
Unrelated root `__init__.py` is preserved.

## Verification

Baseline main passed 1,557 tests, native/style checks and portable/offscreen qualification
for recommendations 1–3. New behavior requires focused native/API/lifecycle tests, actual
offscreen editing/render review, profiler evidence, full gate and packaged verification.
Focused stacking/API/view/lifecycle/architecture checks: 14 passed. Native build and
all five CTest checks passed. Actual GUI captures and full gate remain pending.

Constraint inspection now shows production goal/result vectors and residuals, distinguishing
accepted source-relative goals from current target-relative goals. No constraint mathematics
changed. QTest exercised painting release/undo/cancel and section/route controls. Hidden GPU
captures and report exports succeeded for all four tools. Full pytest: 1,592 passed; all five
native CTests and native function-length checks passed before final presentation adjustments.

A real 8,192-point footprint exposed a QML reference-sequence stall. Geometry is now copied
once per change through ViewSnapshot and excluded from small status property maps. The same
hidden scene completes with profiling on and off. This performance correction still needs
its regression test and final profiler rerun. Those now pass, including copied snapshot,
live/frozen route selection, failure/capture limits and camera-save continuity. Final profiles
are under build/vcp-visual-tools; CH-024–026 records timings and limitations. Contacts and
stacking displacement were visually inspected. Camera persistence exposed broad revision
invalidation; signatures now exclude presentation while retaining scene/backend validation.
Separate ownership review: numerical work remains native; all new queries share the existing
read-only coordinator; paint commits use authored-field commands; cached inputs own meshes;
displayed stages/picking share leases; diagnostic traces are bounded and never publish paths.
No competing scheduler or Python numerical fallback was added.

## Next actions and blockers

1. Finish saved-view review, snapshot/replay regressions and packaged qualification commands.
2. Rerun profiler scenes and complete ownership/coupling review.
3. Update recommendations/computation records and run the development gate.
4. Package the canonical 0.2.3 build, qualify relocation, then merge validated work.

## Recovery inputs

Use E:/development/anthroforge and tools/common.ps1. Keep generated evidence under
ignored build/vcp-visual-tools; preserve production projects and avoid desktop takeover.
Native painting build: build/vcp-visual-paint-native.log (all five CTests passed).
Hidden GPU: tools/vcp_visual_scene.py, build/vcp-visual-tools/paint-preview.png and
paint.afinspection.zip. Full QML pointer-input acceptance and profiler trials remain pending.
Section build: build/vcp-visual-section-native.log (all five CTests passed). Actual captures:
build/vcp-visual-tools/section-tissue.png and section-scene.png. Shader compilation exercised
on hidden D3D11. Portable and complete UI qualification are still required.
