# AnthroForge 0.2.0 construction objects

- Task branch: `codex/020-construction`
- Integration branch: `main`
- Starting revision: `b539697`
- Status: in progress; not release-ready
- Last updated: 2026-10-18, Europe/Bucharest
- Active writer: local desktop implementation chat

## Outcome and acceptance

Implement the approved [0.2.0 specification](../specification_020.md) and
[implementation plan](../implementation_020.md). Includes first-class curves,
reference images, fibers and curve-based surfaces in desktop and headless use.
Muscles and soft tissues belong to 0.2.1. Preserve the unrelated root `__init__.py`.

## Current state

Consolidated specification and plan are committed. Baseline docs link to the superseding
contract; the previous Free/Controlled normative paragraph now describes curve engines.
Added typed construction objects, Fiber subclass/binding cardinality, generic registry,
distinct parenting/membership validation, incremental construction changes and schema 3
round trips. Old schemas are rejected. Primitives now store CurveUse references; owned
ResolvedPrimitive inputs exist only at evaluation/edit presentation boundaries. Primitive
creation, point/handle editing, duplication, deformers, deletion, dependencies, scheduling
and existing desktop authoring projections use these references. Generic curve creation/
point edits, object rename/transform/reparent/delete/inspect, primitive.from_curves,
primitive.curve_mode and primitive.make_independent are integrated with shared commands.

Native owned paths now evaluate BEZIER and exact POLYLINE, preserve closed-path starts,
omit duplicate endpoints, and retain allocations through read-only array leases. Resources
have typed mesh/path/image catalogues, retained across history/checkpoints/jobs and snapshots.
Schema 3 stores path buffers and deduplicated embedded PNG/JPEG sources; Pillow is promoted
to a runtime dependency and applies EXIF orientation once without Qt. Save/inspection callers
use complete resource snapshots. Native path/typed-resource tests and style checks pass.
Coordinated path jobs now publish accepted buffers/provenance and drive primitive consumers.
Manual source edits retain accepted construction (including inputs for control deformers),
report pending upstream state, and reevaluate live consumers after explicit path publication.
Native sampling reuses accepted paths and preserves existing body/loft sampling behavior.
Curve jobs use the common cancellation/history/checkpoint contracts and task Issues.
Generic workspace associations determine curve editability and task priority.
Profiler memory snapshots now include typed mesh/path/image totals and per-kind ownership,
with bounded native path enumeration, weak job observations and bounded catalogue/history
collection. Disabled profiling performs no inventory queries. Image resource identity avoids
hashing image payloads during observations; reports contain sizes and provenance, not pixels.
Standalone curves now have Construction navigation, shared editing, staged native display
and picking (details below). ROUTED is not implemented in the standalone engine and is
explicitly rejected by native path dispatch. Image import/replacement/calibration and native
texture preparation, image UI/display and picking are implemented (evidence limits below).
Fiber/Surface production operations/native algorithms/UI remain unfinished.
Direct control.attach is still present and must be retired as planned.
No 0.2.0 release qualification or version bump has occurred.
The current coordinator, attachment kernels, Issues, profiler, transactions and
staged renderer must be extended at their owning boundaries, not duplicated.

## Verification

Read-only inspection completed; `main` and fetched `origin/main` both at `b539697`.
Current shared-curve increment: `uv run --no-sync pytest -q`: 573 passed (32 new cases).
Owned path/resource checkpoint: 586 tests passed, Ruff and mypy pass; native build/contract
and clang-tidy on the modified curve/path implementation pass. Full gate on this increment
has not yet run; the preceding shared-curve full-gate evidence remains scoped below.
Coordinated accepted-path increment: `./tools/check.ps1` passed with 596 tests, full native
style/build/contract checks, Ruff, mypy, numerical imports and doctor. Includes exact old/new
native sampling comparisons for transformed open/closed lofts and body deformation; this is
not a claim of complete new fiber/drawing/surface Blender parity or interactive acceptance.
Resource attribution increment: 598 tests pass, Ruff/mypy pass, native build/contract and
modified native inventory clang-tidy pass. No new full-gate or GUI qualification claimed.
`./tools/check.ps1` passed on the shared-curve checkpoint: native build/contract, native
and script style, Ruff, mypy, all 573 tests, numerical imports and doctor. 0.2.0 GUI/package
qualification has not run. One earlier full run saw the existing global native-allocation
count test change during collection; targeted and subsequent full run pass. Investigate
resource ownership if this recurs; do not weaken the allocation assertions.
An initial suite overlapped source editing and its subprocess saw an intermediate invalid
dataclass definition; it is not baseline evidence. Subsequent checks used stable content.
No visible applications or desktop input permitted while the user is gaming.
Use background/offscreen checks and state their limits.

## Next actions and blockers

1. Extend remaining inspection/Issues clients to generic objects; retire control anatomical
   attachments in favor of ordinary relationships. Path/image profiler ownership is integrated.
2. Add Construction UI and standalone curve editing/creation; curve consumers already have
   shared command operations. Then complete native drawing, embedded reference images,
   Fiber bindings/routing/junctions and generic surfaces in the planned order.
3. Keep removing contradictory active baseline text as each boundary is integrated.
4. Run native/parity, headless, offscreen and portable release qualification before merge.

Important findings: ordinary parenting and consumer frames need an atomic rebind to avoid
double transforms after a new shared ancestor is introduced. Local path/local-pose ports
must not depend on the consumer's world pose, otherwise a pure SCP transform unnecessarily
obsoletes geometry jobs. `consumer_parenting.py` and shared-curve regression cases cover
these boundaries. Newly created primitive children now capture their origin attachment
through the existing evaluation contract. Profiler changes include construction-object
fields (e.g. points), not a fictitious change to the primitive reference definition.
Path prerequisite admission must avoid inline publication before its consumer is registered;
queued consumers already waiting on that path are retained rather than superseded. Regression
coverage preserves the first construction job during an SCP pose edit. Generic paths retain
analytic tangents; Blender body deformation separately reconstructs bevel tangent bisectors.
Sharing the body-specific tangent preparation with loft sampling caused a measured parity
difference and was corrected at the native frame boundary, not by relaxing tolerances.

## Recovery inputs

Normal Windows environment and native toolchain already exist in this checkout.
Addon migration reference: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Original geometry references remain under `E:/development/WIP_models`; do not commit
large source assets. Copy compact reproducible fixtures with source provenance.
Push every coherent checkpoint; incomplete work stays on this branch.

## Standalone editor checkpoint

Construction has its own incremental list and selection records. Existing point/handle editing,
transforms, insertion previews and undo now accept standalone curves. Generic inspection reports
path resources, ordinary parents and source-consumer topology locks without an anatomical proxy.
Object transforms accept an explicit world-space request and resolve ordinary parent-local state.
Resolution changes through both primitive and source APIs enforce the shared lock. Construction
visibility/pickability can be stored independently. Keyboard deletion resolves construction objects.

Validation: 602 tests pass; Ruff and mypy pass. `tools/construction_editor_acceptance.py` loads the
actual desktop QML on the offscreen platform and exercises standalone selection, inspection,
framing, point drag/undo, insertion and canceled transforms without warnings. This is controller/
QML acceptance only: no visible desktop input, full interaction rendering or package acceptance.
Curves still need staged native display/picking outside edit mode. Image/fiber/surface production
workflows, drawing, complete Construction controls, legacy control-attachment retirement and
release qualification remain incomplete. Do not release or merge this checkpoint as 0.2.0.

## Native path presentation checkpoint

Native accepted paths now own bounded float render chunks and a segment AABB index, built
before publication. Batched picking uses world-space distance with exact nonuniform/reflected
transforms and cached local trees. The existing staged renderer now accepts explicit resource
leases; paths use their own handle namespace/model and switch picking to the displayed revision.
Profiler viewport ownership includes path leases and native inventory includes derived buffers.
A native single-affine-instance adapter preserves shear from ordinary transform parenting instead
of discarding it through TRS decomposition. Curve category visibility/pickability is respected.
Empty-document presentation uses the generic object registry rather than only the anatomical tree.

Validation: 608 tests pass, Ruff/mypy pass, native build/contracts and changed-native clang-tidy
pass. `tools/path_scene_acceptance.py` renders the actual viewport through QQuickRenderControl
into a D3D11 texture without a visible window. Hover/click results agree; replacement retains
old buffers and releases them after activation; a pixel check verifies a rotated path under a
nonuniformly scaled ordinary parent. Captures were inspected in build/020-path-scene. Generic
Qt offscreen QPA could not initialize D3D11, so this render check uses the platform backend with
an explicitly invisible render-control window. No desktop input or interactive acceptance.
The controller/QML standalone editor acceptance also passes. Full 0.2.0 remains incomplete.

## Image authoring checkpoint

Extracted the existing mesh-import history/publication behavior into `authored_jobs`; mesh
and image imports now use that shared contract. Added background PNG/JPEG decoding with
EXIF orientation, cancellation, independent image instances sharing embedded assets, source
replacement, physical sizing and native two-landmark calibration. Import completion belongs
to its initiating undo step even when later edits exist. Completed same-source replacement
is not restarted by redo. Native image resources own bounded 256-pixel texture tiles; Qt
adoption is limited to one tile per staged item. Display/interaction integration is next.

Validation: full native build/contracts pass, changed-native clang-tidy passes, Ruff/format
and mypy pass, and 617 tests pass. Includes image-only documents, aspect/width preservation,
instance independence, transformed calibration and undo, interrupted import undo/redo,
embedded persistence without the original source, invalid input, and existing mesh-import
regressions. The full development gate passed on the preceding path checkpoint (608 tests).
No image rendering, interactive acceptance, or 0.2.0 packaging acceptance is claimed here.

## Image presentation and editing checkpoint

Construction now exposes image import, source replacement, shared-asset instances, numeric
size/transform, ordinary parenting, world-axis alignment and two-landmark calibration.
Per-workspace image appearance includes opacity, depth, side visibility, projection modes
and pickability. Native plane picking uses displayed dimensions/provenance and current view
projection. Images have their own staged model and asset leases, included in profiler owners.
Native image quads preserve affine transforms without decomposing shear.

Validation: 624 tests pass; Ruff/format/mypy pass; native build/contracts and changed-native
clang-tidy pass. Texture-only D3D11 checks in `tools/image_scene_acceptance.py` cover exact
quadrant orientation, hover/click, front/back/normal occlusion against a cube, calibration
with one-action undo, complete old-image retention during replacement and lease release.
Captures in `build/020-image-scene` were visually inspected. Path rendering regression and
offscreen construction-editor checks pass. No visible windows or desktop input were used;
interactive and packaged acceptance remain unperformed. The full development gate passed.

Diagnostic findings: instanced custom image quads were invisible in this setup; normals and
indices did not fix it. Non-instanced quads with six native-transformed vertices render
correctly. Reparenting existing nodes between View3D scenes lost display; staged filtered
layer models preserve it. These findings and ownership boundaries are in architecture.md.
Remaining release work still includes native drawing/fitting/cursor, conversion previews,
complete consumer/navigation controls, fibers/routing/attachments/junctions, generic surfaces,
legacy control-attachment retirement, performance evidence and full release qualification.

## Ordered sources and consumer controls checkpoint

Object selection now preserves selection order, with extension handled through the existing
keyboard abstraction. Creating a primitive from selected curves keeps live references in that
order. Inspectors expose usage, transform-consumption mode, reverse direction and Make Independent.
The document registry owns the shared reverse consumer index, avoiding repeated full scans in
usage queries. This is a structural improvement; no timing improvement is claimed without profiling.

Validation: 626 tests pass, including consumer-index changes across independence/deletion/undo
and reversing one consumer without changing its source or other consumers. Offscreen full-QML
checks cover ordered creation, usage projection and selection pruning. Ruff, configured mypy
and function-length checks pass. An exploratory `mypy src` invocation also checked desktop
modules outside the configured gate and reported existing untyped-adapter errors; it is not
the repository's type-check command. Full development gate passed immediately before this
Python/QML-only increment. Drawing/cursor and the remaining release work above are still pending.

## Native fitting checkpoint (desktop integration in progress)

Vendored Blender 5.0.1's unchanged BSD curve_fit_nd C kernel with hashes/notices and a narrow
C++ adapter. REFIT/SPLIT fitting, corner handle modes, closure, optional radius channel and exact
polyline creation share one owned-output boundary. `curve.draw` fits and prepares the accepted
path on a dedicated coordinator policy, then uses shared async authored publication. Parent
validation/placement was extracted from images into object_creation for both clients.

Native build/contracts, changed-native clang-tidy, Ruff/configured mypy and 11 focused drawing/
architecture tests pass. Tests include shape error/endpoints, closure, cancellation, interleaved
undo authorship and persistence. Image import regressions passed during the extraction. Full
suite is pending for this increment. This is not completed Draw UX: stroke projection, cursor,
desktop input/preview, actual Blender operator parity and performance evidence are next.
The kernel cannot cancel internally; measure its atomic interval before claiming responsiveness.
