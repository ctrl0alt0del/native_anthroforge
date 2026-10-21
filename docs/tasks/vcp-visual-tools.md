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
Questions pending: selected-tissue versus scene section default; separate route diagnostic
run versus capture during regular recalculation. Continue independent stacking work meanwhile.
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
are integrated; route-specific GUI/failure/limit qualification remains pending. Both solver
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

## Next actions and blockers

1. Implement evaluated stacking inspection with explicit input provenance and native footprints.
2. Integrate native field painting and shared stroke transactions through desktop/headless.
3. Implement section views and optional native route diagnostic collection after UX answers.
4. Qualify, document computation changes, package, checkpoint and merge validated work.

## Recovery inputs

Use E:/development/anthroforge and tools/common.ps1. Keep generated evidence under
ignored build/vcp-visual-tools; preserve production projects and avoid desktop takeover.
Native painting build: build/vcp-visual-paint-native.log (all five CTests passed).
Hidden GPU: tools/vcp_visual_scene.py, build/vcp-visual-tools/paint-preview.png and
paint.afinspection.zip. Full QML pointer-input acceptance and profiler trials remain pending.
Section build: build/vcp-visual-section-native.log (all five CTests passed). Actual captures:
build/vcp-visual-tools/section-tissue.png and section-scene.png. Shader compilation exercised
on hidden D3D11. Portable and complete UI qualification are still required.
