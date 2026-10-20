# AnthroForge 0.2.0 specification

Status: confirmed and implemented product contract. This document governs
0.2.0 and supersedes conflicting earlier proposals. Observed evidence and its limits
are recorded in [release validation](development_status.md#construction-objects-020).
See [delivery plan](implementation_020.md),
[engineering rules](engineering_guidelines.md), and [task status](tasks/020-construction.md).

Roadmap update, 2026-10-19: [0.2.1 curve-workflow requirements](specification_021.md)
reserve the next release for improvements; VCPs/muscles/soft tissues move to 0.2.2.
The original 0.2.1 deferral below is historical, not the current release target.

## Release and compatibility

0.2.0 delivers standalone curves, reference images, fibers and curve-based surfaces
through the same desktop and headless application operations. Muscles and soft tissues
move to 0.2.1. Mirroring, simultaneous multi-curve component editing, addon-project
conversion and broader export formats are deferred. Object multi-selection for choosing
construction inputs is included. Apply/Bake remains permanently unavailable.

Keep Python 3.12, C++17 and Qt/PySide 6.12.0. Numerical headless use does not initialize
Qt or Blender. Use the current production routing solver without legacy/public version
selectors. Old project schemas are rejected clearly; no compatibility loader is required.

## Objects and relationships

Documents can contain only curves or images. The single SCP root requirement applies
to the anatomical tree, not to the whole document. Construction objects never need dummy
SCPs/VCPs. Objects have stable identity, names, transforms, visibility, selection,
transactions, persistence and declared capabilities.

Keep ordinary transform parenting, anatomical attachments, construction references and
workspace membership distinct. Images cannot parent anything. Generic curves, images,
Hook controls and lattice controls cannot receive custom anatomical attachments.
SCP/VCP anatomy and the explicit Fiber subclass can. Fibers may only be children in
the anatomical attachment graph and cannot supply attachment surfaces; this does not
prohibit ordinary transform parenting or their use as construction curves.

The anatomical outliner contains SCPs and true VCPs. A separate Construction view
organizes Curves, Fibers, Surfaces and Reference Images, with workspace/whole-document
filters and accessible unassigned objects. Organizational collections are not parents.

Workspace inclusion follows SCP/VCP membership and related construction, including a
shared curve when only some of its consumers belong to the workspace. New construction
is associated with active anatomy without automatically parenting it; otherwise it is
unassigned. Outside anatomy remains transparent/read-only. Outside consumers still
evaluate at lower priority: there is no deferred-update approval state. Workspace
changes reprioritize queued work without canceling valid running work.

## Curves and path engines

A Curve contains ordered authored points, a selected path engine, typed engine settings
and an open/closed property. Engines are BEZIER, POLYLINE and ROUTED. One object is one
connected path; separate strokes create separate objects. The routed engine also works
on ordinary curves with explicit routing positions and obstacles, without bindings.

Closure requires at least three authored points and joins last to first without storing
a duplicate endpoint. Loops are ordinary closed curves; there is no loop subclass or
special loop-anchor model. Geometric routing points are not anatomical bindings.

Bézier points retain handles, handle modes, radius and tilt. Polyline points remain exact.
Routed editing changes authored routing points, never generated solver samples. Merely
selecting a curve or entering edit mode cannot fit/resample/change it. Updated user decision,
2026-10-20: selecting the Path engine applies it directly with one undo action, retaining
all existing authored control points and allowing the engine to define the path. No separate
Change path engine button or preview/accept gate is required. This replaces the original
mandatory preview and structural-point selection workflow. Never promote sampled output
into authored points during this action. Fibers use their current resolved authored points.
Optional headless conversion previews can explicitly resample or select a structural subset;
they are a separate operation and do not define ordinary engine selection.

Provide Add Curve (two-point Bézier by default), Place Points and Draw. Place Points:
Enter completes, Backspace removes the last draft point, Escape cancels the draft or
exits the idle tool. Draw release completes one curve while the tool remains ready;
each completed curve is one undo action. Native fitting must not stall the UI.

Retain handles, numeric editing, Shift insertion, Ctrl surface snapping and wheel offset,
G/R/S, axis views 1/2/3, camera restore 4 and uninterrupted gestures through the keyboard
manager. Add a numeric/surface-placeable 3D cursor for creation and drawing depth.

Match applicable Blender 5.0.1 curve drawing behavior: cursor/view depth, surface projection,
selected-only projection, normal offset, first-hit plane options, misses/fallback,
fitting error and corner handling. Reference-image plane tracing is an explicit extension.
Tracing creates no lasting image-to-curve attachment; common ordinary parenting is allowed.

Draw defaults to screen-pixel fitting tolerance and closes endpoints within eight logical
pixels; both behaviors can be overridden. Only fitted surface strokes add depth substeps.
Changing the camera during a stroke preserves the gesture and disables automatic closure
for that stroke, since its endpoint screen coordinates no longer share a view.

## Curve consumers

Primitive and surface creation accepts preselected curves and stores live references.
Curves formerly embedded in primitives become the same first-class objects. Source
points, handles, radius and tilt are shared. Each consumer owns ordering, direction,
sampling ranges/density and placement.

Each use supports Shape and transform (default) and Shape only. Shape only follows shape
while retaining consumer placement. Switching preserves the visible result; shared parent
transforms cannot apply twice, and moving one SCP cannot move other consumers or sources.
Show usage counts and Make Independent. Independent copies remap internal identities once
while preserving sharing within a copied set. External references remain explicit.

Block source deletion while consumers exist and identify them. Consumer deletion preserves
sources. Ordinary transform children are promoted preserving world placement. Retain the
existing SCP deletion behavior: promote anatomical children, or replace a deleted root
with an empty grouping root when necessary. Never silently retarget nonhierarchical bindings.

Topology locks traverse every consumer with incoming anatomical bindings, including fibers.
Report locking consumers and unlock when bindings are removed. No topology remapping is
introduced. Deformation resolves stable authored membership to native indices at dispatch.

## Fibers and shared junctions

Fiber is an actual subclass of Curve, adds anatomical binding capabilities and honors the
same generic curve interfaces. There are no Free/Controlled fiber types or a presentation-only
fiber wrapper. The selected curve engine determines authored-shape or routed behavior.

Creating a fiber from a curve copies its construction with new object/point identities,
engine/settings and initial world placement. The original remains unchanged with no live
relationship. Open fibers require both endpoint bindings; closed fibers require at least
one chosen binding. Unbound drafts remain ordinary curves. Three geometric loop points
do not mean three required anatomical attachments.

In the desktop, successful curve-to-fiber creation exits component editing and selects
the accepted fiber. Pending or failed creation does not select a missing object, and
completion must not take over a newer selection or workspace. Fibers have no direct
object translation, rotation or scale: the shared command policy rejects these changes,
and keyboard, toolbar, numeric fields and gizmos reflect that restriction. Authored
point/handle transforms, ordinary parenting and attachment-driven deformation remain
available; this restriction does not make the entire fiber read-only.

Use the shared attachment subsystem and qualified capture/resolve policy for structural
bindings and interior deformation. Parent movement resolves existing bindings, never
silently choosing new parents. Authored-engine editing shows the current resolved shape,
preserves editable parameters, and rebinds moved endpoints in the same transaction.
Capture policy is Current parent (default) or Any eligible parent. Routed curves may
reroute around obstacles; Bézier/polyline fibers retain authored shape and report collisions.
Failure preserves accepted output and produces an actionable Issue.

Shared junctions are explicit curve-level identity relationships inherited by fibers.
Proximity never welds points. A junction edit updates all incident authored records
atomically, then each engine evaluates. Shared binding identity is explicit; independent
fiber creation does not infer junction sharing with its source.

Fibers may be used wherever curves are accepted, including primitive/surface inputs.
The existing dependency graph and Issues system handle invalid dependency cycles.

## Surfaces

One general surface service accepts Curve, Fiber and compatible mixtures. Surface objects
own ordering, direction, sampling and correspondence; source curves remain independent.
Supported forms: open lofts, compatible closed lofts, a single closed-curve patch, and
branched open lofts. Mixed open/closed loft inputs fail validation. Retain addon branch
constraints; closed/nested branch expansion is out of scope.

Branches reference explicit junction/point identities, not near-position welding.
Closed-loft initial alignment has a preview, then persists per-source direction and start
correspondence. Realign is explicit; ordinary deformation cannot recalculate correspondence.
Share suitable native kernels with SCP lofts without changing qualified connectivity.
Deleting a surface preserves sources. Invalid input retains accepted output with diagnostics.

## Reference images

PNG/JPEG still images are embedded once per unique source asset; multiple instances are
allowed. Import/decode works headlessly. Use the already-locked Pillow dependency and
apply EXIF orientation consistently once. Keep source bytes separate from derived textures.

Images have world transforms or ordinary local parents. Reparent/unparent preserves world
placement and later follows parent TRS. Images cannot parent any object or participate as
collision/attachment surfaces. Asset identity, dimensions, calibration and transform are
authored state. Opacity, depth (normal/front/back), side (front/back/both), orthographic/
perspective visibility, optional axis alignment, visibility and pickability are presentation.

Two-point known-distance calibration preserves aspect and position and forms one undo action.
Replacing a selected image assignment preserves position and physical width, adjusts height
for the new aspect and invalidates its old landmark calibration. Other instances keep their
assignments. Undo restores all affected state. Project use requires no external image files.

## Evaluation, persistence and presentation

Reuse the coordinator, dedicated task policies, dispatch-time input capture, output
reservations, full-read revision validation, safe cancellation, obsolete-result rejection,
dependent registration before terminal state, and Manual prerequisite provenance.
Add path/binding/junction/image outputs without conflating pose and geometry.

Authored state, accepted results, previews and per-view presentation have different owners.
Native work returns complete owned buffers and diagnostics; Python orchestrates, validates,
serializes and publishes. All fitting, iterative numerical work and repeated geometry
queries run in C++, including addon code previously limited to Python by Blender access.

Schema 3 keeps atomic ZIP64/JSON/NPY storage, canonical metres and file ownership. Persist
authored relationships, embedded assets, selected-revision accepted results and intentional
workspace state. No native handles, undo history or paused workers are serialized. Older
schemas fail clearly. Preserve existing startup computations, not blanket rerouting.

Retain earliest-active-write checkpoint semantics, queued-write blocking, read-only job
exemption, wait-save queue draining, terminal failure states, undo cancellation and redo
restart. Own path/mesh/image resources across state, history, checkpoints, jobs and rendering.

Use incremental UI models, cached native picking and complete staged viewport publication.
Picking matches displayed revisions. Reuse Issues and profiler attribution. Follow Theme
and Ui controls; concise primary controls, detailed help in disclosure, no text walls.

## Superseded decisions

The former embedded-only curves, live fiber/source sharing, Free/Controlled classes,
special loop classes, anatomical outliner placement of fibers/surfaces, direct Hook/lattice
surface attachments, deferred outside-workspace approvals, old-schema migration and split
0.2.0/0.2.1 construction release are no longer active requirements. Historical evidence
keeps its original context; it does not override this contract.

## Evidence and completion

The [implementation plan](implementation_020.md) defines required contract, native parity,
interaction, persistence, lifecycle, performance and packaging evidence. Source references
and intended parity differences must be recorded. No API success or numerical proxy alone
establishes visual correctness or release acceptance.

Reference: [Blender 5.0.1 drawing source](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/editors/curve/editcurve_paint.cc).
