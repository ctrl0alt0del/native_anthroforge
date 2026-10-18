# AnthroForge 0.1.2: primitives and deformers

Historical release contract. For current development, the
[0.2.0 specification](specification_020.md) supersedes embedded curve ownership,
direct anatomical attachments on controls and older-schema compatibility. Primitives
reference first-class curves; per-consumer placement/sampling remains independent.
The geometry/deformer parity requirements below remain applicable where not superseded.

Status: confirmed product specification, 2026-10-16. The user confirmed primitive
interview Q1–Q31 and the consolidated scope in Q32. This document records required
behavior. Implementation evidence and its limits are recorded in
[development status](development_status.md#primitive-and-deformer-release-012).

This extends the [general product specification](../standalone_application_recommendations.md).
For primitive and deformer behavior, these later decisions supersede its earlier
descriptions. The existing document, workspace, transaction, scheduler, saving,
startup, and headless contracts continue to apply. The target is **0.1.2**, replacing
the earlier allocation of curve primitives to 0.1.1.

## 1. Responsibilities and permanent editability

| Responsibility | Contents and contract |
| --- | --- |
| Primitive definition | Imported mesh, loft, or curve-deformed body; owns the source geometry or construction parameters. |
| Deformation | Independently addable/removable Hook and Lattice operations; modifies supported geometry or construction controls. |
| Other geometry modifiers | Thickness is reusable and separate from primitive construction; it can change topology. |
| Shared controls | Hook target controls and lattice cages, distinct from the individual bindings that connect them to targets. |
| SCP | Anatomical entity with an overall transform, an authoritative evaluated geometry result, construction controls, and attachment relationships. |
| Presentation | Selection, control visibility, hover, and workspace styling; does not change authored geometry or trigger unrelated computation. |

The defining curve of a curve-deformed body belongs to that primitive construction.
Optional hooks and lattices remain separate deformers. Their addition or removal
does not change the primitive family.

**Apply/Bake is permanently unavailable, in every version and through every UI,
authoring, or headless API.** Do not replace an editable construction with its
evaluated mesh, flatten its modifier history, or silently bake while removing a
deformer. Primitive definitions, source assets, and remaining deformer parameters
stay editable. Derived mesh caches and saved completed results are permitted;
they never replace the authored definition. The separate skin-only export contract
does not authorize destructive changes to the project.

One SCP may contain several curves or body pieces and several attachment locations.
Keep the addon responsibilities of SCP geometry, overall transform, and associated
controls, without requiring users to recreate Blender's helper-object bookkeeping.
Mixing different primitive families within one SCP is excluded through 1.0.
Box/cylinder/capsule are choices within the same body family.

## 2. Primitive construction

### 2.1 Common curve authoring

- Support open and closed Bézier curves, insertion/removal of control points,
  automatic/aligned/free/vector handles, and viewport and numeric editing.
- Keep parameters geometric and anatomy-independent. Anatomical shortcuts such as
  proximal length, middle bend, and tip thickness are drivers over these parameters,
  not primitive knowledge; those shortcuts are outside 0.1.x.
- Curve-deformed bodies expose per-control-point radius and tilt with Blender's
  semantics. The inspected brow constructions already use nonzero tilt.

### 2.2 Loft

- Start with two editable curves. Add, duplicate, and reorder curves in an ordered
  list of arbitrary length. Loft adjacent pairs A–B, B–C, and so on, not every
  possible pair of curves.
- Follow the inspected node construction's sampling: resample each input curve to
  a common count, then sample positions by normalized factor along that resampled
  curve and interpolate between neighboring curves. This is not correspondence by
  authored control-point index; inputs may have different numbers of Bézier points.
- Expose a common sampling start/span with per-curve overrides, generalizing the
  reference ribcage's Angle and Lower Angle controls.
- Share boundary vertices between neighboring strips to produce one connected
  generated surface. This is an intentional change from the disconnected strips
  in the reference node graph, not an Apply/Bake operation on authored curves.
- Support open surfaces, thickness shells, and closed capped volumes. Thickness
  remains a separate modifier. Shared loft boundaries must not create internal
  seam walls when thickness is evaluated.
- Respect each curve's coordinate space and the SCP's overall transform when
  sampling; moving an SCP must not introduce a second application of its transform.

### 2.3 Curve-deformed body

- Start with a straight editable curve and a box, cylinder, or capsule base.
- A construction may contain multiple curve-driven pieces in the same SCP.
  Hook-connected pieces may also belong to different SCPs, as in the clavicle example.
- Fit the entire curve by default; provide fixed length and position along the curve.
- Preserve the relevant Blender curve-deformation behavior, including radius and
  tilt, local frames, transforms, and the open/closed curve cases in the references.
- Hook connection means maintaining the bound relationship between controls. It
  does not imply automatic tangent alignment, welding, or boolean union of bodies.

### 2.4 Imported mesh

Retain existing import and unit-conversion behavior. The source mesh stays unchanged;
TRS and editable deformers determine its evaluated shape. Lattices are available on
imported meshes as on the other primitives. Allow vertex selection and influence
weights for hooks, without introducing direct mesh-vertex editing. Material, texture,
UV, and vertex-color preservation remain outside the existing version-one scope.

## 3. Deformers, thickness, and shared controls

### 3.1 Native Hook behavior

Reproduce Blender's Hook modifier behavior for an Empty-like target control, using
its implementation as the reference. This includes binding/offset transforms,
selected point or vertex membership, strength, weights and inversion, falloff type,
radius, custom falloff, uniform falloff, and reset/recenter/selection/assignment
behavior applicable to the supported targets. An armature/bone system is not added.

Hooks may influence supported curve points/handles, lattice points, and mesh
vertices, including imported vertices and body construction geometry. One control
may drive multiple targets, including targets in different SCPs. Bind initially
without moving the selected points. Preserve native offset behavior rather than
assuming every bound point is located at the hook target's origin.

At full influence, endpoints bound together to one hook remain together when their
individual curve/SCP transforms change, as verified in the clavicle reference.
Partial strength and falloff retain their native behavior rather than guaranteeing
the same coincidence for every setting.

### 3.2 Native Lattice behavior

Lattice is available for every primitive family. Create a cage fitted around the
chosen primitive or primitives; default creation may target one SCP and the same
cage may be shared afterward. Cages are directly editable and can themselves be
controlled by hooks, as demonstrated by the brow reference.

Copy Blender's lattice deformation and resolution-change behavior, including
per-axis resolution/interpolation, Outside behavior, strength/weights/inversion,
and coordinate transforms applicable to these targets. Do not substitute a custom
exact-shape-preserving regrid or an invented regrid approval workflow. Blender
animation and shape-key systems are not implicitly added by this requirement.

The inspected Blender 5.0.1 resize implementation transfers deformation onto a new
regular grid using temporary linear interpolation, restores the interpolation
settings, and clears lattice vertex weights. Its limits and edge behavior are
reference semantics to qualify during implementation, not a promise of exact shape
preservation when cage resolution changes.

### 3.3 Ordering and removal

- Support multiple deformers and editable ordering on the same target.
- A hook on a defining curve runs before mesh generation; a deformation on the
  generated mesh runs afterward. Order operations at their actual target, rather
  than treating every control and mesh operation as one interchangeable list.
- Lattice precedes thickness for shells. Thickness is separate from both loft and
  body construction; it is not an intrinsic loft-only property.
- Add, edit, disable, and remove deformers while retaining the underlying primitive.
  Removing a deformer removes its influence; it never bakes the visible shape.
- Removing a target's binding leaves other targets and the shared control intact.
  Deleting a shared control is a separate action identifying all affected targets.
  General reference/deletion and undo contracts still apply.

Thickness uses Blender **Simple Solidify**, including offset, rims, weights/inversion,
even thickness, high-quality normals, normal flipping and clamping. Complex mode is deferred.

### 3.4 Transforms and attachments

Each shared control explicitly follows an SCP or the document frame. New controls
created for one SCP follow that SCP initially. Sharing preserves the selected
transform source. Explicitly changing the source preserves world placement.
Transform following and the targets influenced by the deformer are separate data.

Retain the SCP's overall hierarchy attachment and support distinct local control or
hook attachment sites to other SCP surfaces or controls. A construction's local
attachment sites may use different supports. The SCP hierarchy remains a single
tree even when additional control dependencies form a more general graph.

## 4. Attachment stability and dependency evaluation

### 4.1 Topology changes

The addon does not provide general preservation of SCP surface attachment locations
across resolution changes. Automatic attachment remapping across these changes is
excluded through 1.0. Therefore:

- Disable resolution and other topology-changing edits while an SCP has children
  **or** incoming surface attachments, including those from shared controls.
- This includes changes that alter attachment mesh indexing/connectivity, such as
  adding/removing loft curves or changing caps. Apply the same rule through UI and APIs.
- Unlock these operations when the SCP has neither children nor incoming surface
  attachments. A transform-following reference alone adds no surface-binding lock.
- Shape edits that preserve the evaluated attachment mesh topology remain available,
  including curve/handle movement and hook/lattice deformation. A lattice grid
  resolution change is not itself prohibited if the resulting SCP mesh topology
  remains unchanged; native lattice resize behavior still applies to the cage.
- Display-only detail changes remain separate from authoritative geometry and its
  attachment indices. Do not use display resolution to change attachment meaning.

### 4.2 Cycles and failures

Allow users to create circular hook/lattice/attachment dependencies. Do not reject
the new links merely because they form a cycle. Detect cycles for bounded evaluation:
skip the cyclic group and calculations requiring its new results, retain their last
successful output where available, and continue unrelated work. Affected jobs finish
unsuccessfully instead of remaining active indefinitely and blocking saving.

This does not permit cycles in the SCP parent hierarchy. The addon's dedicated issue
reporting system and its cycle-reporting UI are deferred to a later 0.x release;
runtime failure states continue to use the existing job/activity contract.

### 4.3 Scheduling and update modes

The task coordinator remains the single owner of work admission, output reservations,
coalescing, revision checks, safe cancellation, publication, and save checkpoints.
Use dedicated scheduling policies for the new task types, with a cheap complexity
estimate before scheduling and an appropriate delay, including zero for cheap work.

Each affected SCP retains its effective Live, On Release, or Manual update mode when
a shared deformer changes. Controls respond immediately; generated geometry updates
according to that SCP's mode. A Manual SCP retains its previous result and pending
state even if another target of the same control is Live. Preserve the existing
distinction between previews and authoritative results for downstream calculations.

Live consumers may use a Manual prerequisite's last accepted result, retaining its
revision provenance and a pending-upstream indication. A new accepted prerequisite
result triggers reevaluation. Missing required accepted input is a terminal failure.

Jobs capture their input revision when ready to execute, not when enqueued. Mark
obsolete work and cancel at a safe point; never publish obsolete results over newer
edits or undo. Multi-target work must reserve its actual outputs. Existing undo,
dependency, checkpoint, and blocked-save semantics apply without simplification.

## 5. Interaction and document integration

- Ordinary selection selects the whole SCP. Explicit **Edit Primitive** mode exposes
  its curves, points, handles, and construction controls.
- Hooks and lattice cages are independently selectable. The outliner makes their
  affected SCPs inspectable; visibility and editability follow workspace rules.
- Provide the creation workflows above: two-curve loft, straight-curve body with
  chosen base, fitted lattice, and hook bound to selected supported points.
- Use the same document operations from the UI, tests, authoring, and headless API.
  Numerical headless operation must not initialize the renderer or require Blender.
- Persist primitive definitions, source assets, deformers, controls, bindings, order,
  and their completed results at the selected save revision. Reopening must retain
  parameter editability and shared relationships. Reuse existing startup rules.
- Reuse transaction/undo and independent-copy/reference-remapping behavior. New
  authored controls are document data, not transient viewport objects.
- Focused workspaces retain the complete graph. Outside entities remain transparent
  and read-only for direct editing, with calculations at the established priority.

## 6. Implementation boundaries and acceptance

Follow the [engineering guidelines](engineering_guidelines.md). Keep construction,
deformation, shared-control binding, dependency evaluation, scheduling policy, and
presentation responsibilities distinct. Reuse the existing core/coordinator contracts;
this specification does not require a general Blender editor or a speculative plugin
framework. Numerical geometry/optimization work belongs in native C++; Python owns
orchestration, validation, serialization, and UI/API adapters under project rules.

The following are release acceptance requirements. Concrete executed checks, fixture
coverage and measurement limits are recorded in development_status.md:

| Area | Acceptance evidence |
| --- | --- |
| Construction | Create both native families from scratch; edit open/closed curves, handles, radius/tilt, fit/fixed-length bodies, and loft sampling ranges. |
| Loft topology | Neighboring strips share boundary vertices; valid capped/thickened fixtures produce the intended connected volume without internal seam walls. Preserve editable curves. |
| Native deformation | Compare Hook and Lattice outputs with pinned Blender fixtures, including nonuniform transforms, partial strengths, falloff, weights, and lattice resize. |
| Shared controls | Reproduce the two-SCP clavicle connection and shared brow cage/hook behavior; move individual owners, change follow source, remove one binding, and verify other targets. |
| Imported geometry | Hook selection/weights and lattice edits change derived output while source vertices remain intact; no Apply/Bake command exists. |
| Attachment restrictions | UI/API both lock topology-changing operations for children or surface dependents; unlock after removal; permitted shape edits still propagate correctly. |
| Cycles | Creating a cycle succeeds; affected work terminates, previous results remain available, unrelated work continues, and saving can finish. |
| Modes and responsiveness | Exercise mixed update modes on shared targets, small/large workloads, obsolete work, safe cancellation, and publication during interactive editing. Measure the existing soft goals. |
| Persistence and history | Save/reopen all parameters and shared relationships; test undo/redo, blocked-save choices, queued work, and failure states with new task types. |
| Delivery | Complete UI and headless workflows and portable Windows packaging; source/reference numerical checks alone are insufficient. |

Native Blender parity is required where adopted, with explicit exceptions for the
confirmed product changes: connected loft seams, attachment topology locks, and the
permanent absence of Apply/Bake. Pinned numerical parity is exercised by the reference
test suites; that evidence does not certify arbitrary Blender scenes or unsupported modes.

## 7. Reference evidence and its limits

The interview inspected `E:/development/WIP_models/skeleton_comb_base.blend` and
`E:/development/WIP_models/skull_muscles.blend` in separate background Blender
processes, with script execution disabled and without saving either source file.
Blender was **5.0.1**, build **a3db93c5b259**. Measurements below are in the source
scene's units, not asserted to be standalone metres. Production files can change;
pin their exact revisions when building implementation fixtures.

| Observation | Consequence |
| --- | --- |
| Rib node group uses four ordered curves, common resampling, adjacent pairs, and separate angle ranges. Finger/toe graphs instead use line segments, circle profiles, Curve to Mesh, and profile scaling. | Use the observed rib sampling for lofts; do not misidentify the finger graph as the same loft algorithm. Anatomical finger drivers remain deferred. |
| Rib geometry has three connected components: 130 vertices each before thickness, 260 each afterward. | Q30 explicitly replaces disconnected neighboring strips with shared loft boundaries. |
| Raising rib resolution from 64 to 128 changes evaluated vertices from 780 to 1,548. Reusing binding indices (279, 671, 669), weights (1, 0, 0), moves the resolved point by about 3.7043 scene units. | Resolution-independent attachment preservation is absent in this representative probe; use the confirmed topology lock. This is a binding-resolution probe, not a whole-UI propagation test. |
| Translating the clavicle owner by 5 scene units leaves the two hook-connected endpoints coincident within about 2.38e-7 scene units. | Cross-SCP hook continuity is target-relative binding behavior, not mesh welding or a requirement to merge the SCPs. |
| Brows use a shared lattice, a hook on that lattice, and nonzero curve tilt. Mandible-side geometry includes a hook before subdivision/curve deformation. | Support shared control targets, native curve orientation, and deformation at the correct construction stage. |
| Addon SCP attachments store triangle vertex indices/weights; the attachment-wave planner excludes cyclic components and affected descendants. | Preserve the useful native attachment contracts and bounded evaluation while adopting the confirmed authoring policy for additional control cycles. |

Local inspection scripts, node/object dumps, and diagnostic JSON are under ignored
`build/primitive-review/`. They are development evidence, not product deliverables
or substitutes for versioned implementation fixtures.

Primary Blender sources inspected for Hook/Lattice behavior:

- [Hook evaluator](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/modifiers/intern/MOD_hook.cc)
  and [Hook editing operations](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/editors/object/object_hook.cc).
- [Lattice modifier](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/modifiers/intern/MOD_lattice.cc),
  [deformation](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/blenkernel/intern/lattice_deform.cc),
  [resize](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/blenkernel/intern/lattice.cc),
  and [RNA properties](https://raw.githubusercontent.com/blender/blender/v5.0.1/source/blender/makesrna/intern/rna_lattice.cc).

The addon reference paths are `core/scp_runtime/attachment_runtime.py`,
`sync_runtime.py`, `surface.py`, `attachment_wave_capture.py`, and
`native/fiber_ccd/af_attachment_wave.hpp`, relative to the original addon root.
Inspect implementation dependencies and retain appropriate provenance/licenses when
porting; this specification does not claim those components have already been extracted.

## 8. Scope boundaries

- Permanent: no Apply/Bake or destructive replacement of editable anatomy parameters.
- Through 1.0: no mixed primitive families within one SCP and no automatic attachment
  preservation across resolution/topology changes.
- Outside 0.1.x: anatomy-specific shortcut/driver parameters on top of the generic primitives.
- Later 0.x: the addon's dedicated issue-reporting system, including cycle reporting.
- Existing deferrals remain: editable legacy Blender-project conversion, general mesh
  editing/sculpting, rigging/animation, and subsequent fiber/muscle/skin migrations.
  This release does not introduce geometry export before skin construction.

## 9. Decision coverage

| Interview decisions | Recorded in |
| --- | --- |
| Q1–Q7: curve editing, SCP ownership, shared deformers, shell forms, generic parameters, family restriction | Sections 1–3 |
| Q8–Q14: local attachments, cross-SCP hooks, native semantics, inspected loft sampling, body fit, reusable thickness | Sections 2–4 and 7 |
| Q15–Q20: cylinder, sampling ranges, Edit Primitive, cycles, conditional resolution lock, transform following | Sections 2–5 |
| Q21–Q24: cycle evaluation, topology/dependent locks, creation workflows and primitive/deformer separation | Sections 1–5 |
| Q25–Q28: multiple ordered deformers, permanent no-bake rule, per-target removal and update modes | Sections 1 and 3–4 |
| Q29–Q31: radius/tilt, connected loft seams, imported hook selection/weights | Section 2 and acceptance/evidence |
| Q32: consolidated specification confirmed | This document's confirmed status |
