# AnthroForge 0.2.2 — unified tissues

Status: confirmed product contract; implementation in progress. This is not a
release qualification claim. Follow [engineering guidelines](engineering_guidelines.md),
the [implementation plan](implementation_022.md), and [task status](tasks/unified-tissues-022.md).

## Release contract

Deliver production tissue construction, anatomical attachments, inflation,
relaxation, branches, cropping and stacking in desktop and Qt-free headless clients.
Mirroring, Draft Skin, Blender-project conversion, anatomical reconstruction or
automatic fitting, animation dynamics and generalized physical contact are deferred.
Apply/Bake is permanently unavailable. Product export remains built-skin-only.
Schema **4** is the only supported project format; reject all earlier schemas,
including 0.2.1 schema 3, clearly without partially loading them.

## Objects and relationships

One concrete `TissueVCP` composes construction, inflation, relaxation, constraints
and stacking settings. Muscle/fat classifications provide labels and creation
defaults; relabeling never resets settings, selects an evaluator or toggles stacking.

- `Point` is first-class construction; `Anchor(Point)` adds an anatomical binding.
- Preserve `Fiber(Curve)` and introduce `Membrane(Surface)` whose sources are all
  Fibers. A Membrane derives anchoring through those sources without its own binding.
- A Tissue references an Anchor, Fiber or Membrane. Ordinary points, curves and
  surfaces remain valid general construction but are not tissue sources.
- All-Fiber surface creation returns a Membrane using the common Surface evaluator.
  Mixed/ordinary-curve inputs produce a generic Surface. Anatomical conversion is explicit.
- Point-to-Anchor copies the authored Point independently and establishes a binding;
  it never changes the source Point. Existing curve-to-Fiber copy semantics remain.
- Sources are shared live references. Make Independent copies the required construction
  graph once, preserves internal junction sharing and keeps external attachments explicit.
- Deleting a Tissue preserves construction. Referenced source deletion is blocked until
  consumers are resolved. Removing a branch preserves the source construction.
- Anatomy contains SCPs and true VCPs; Construction contains Points, Anchors, Curves,
  Fibers, Surfaces, Membranes, controls and images. No dummy SCP wrappers.
- Anatomical organization, ordinary parenting, construction references, attachments
  and workspace associations remain distinct. Workspace inclusion follows anatomy
  and its shared construction. Outside consumers continue at lower priority.
- Generated Tissue geometry has no direct transform or vertex-edit action. Source
  and parameter edits use the shared operation policies in GUI and headless clients.

## Construction, inflation and constraints

Evaluation depends on construction capability, never anatomical names. Maintain
an explicit compatibility matrix; reject unsupported combinations with reasons,
without silently choosing another algorithm.

| Construction/feature | Required behavior |
| --- | --- |
| Surface muscle modes | Control Point and Distributed, falloff, boundary attenuation, longitudinal taper, direction, enable/disable and control initialization. |
| Section Profile | Four depths/peaks, roundness, Local/Smooth/Section directions, initialization/reset, saved inactive settings; ordinary open lofts only. |
| Parts and sides | Independent supported settings per branch and side; stable identities, reversal, two-sided envelope composition. |
| Height smoothing | Native constrained heights, exact boundaries/seams/zero-height creases, bounded change, Off bypass and separate diagnostics. |
| Branches | Existing open branch topology, explicit junctions, welded seams, connector width/fullness and per-part inflation. No nested/closed branches or overlapping root intervals. |
| Crop | Material-domain plane clipping with corresponding base/output interpolation. Crop borders are not attachments or new zero-height rims. |
| Anchor base | Radial sphere/ellipsoid with existing geometric/static relaxation capabilities. |
| Fiber base | Open/cyclic profile sweep, width/depth/power, resolution, endpoint taper, backing and existing relaxation. |
| Membrane base | Weighted normal inflation, minimum/maximum thickness, power, backing/rim and evaluated refinement without source mutation. |
| Relaxation | None, Geometric and Static PBD; gravity, sagginess, shape/volume retention, slack and solver controls. These are static construction calculations, not animation. |
| Constraints | Fixed/Soft regions, named/custom masks, weights, feather, strength, offsets, exact structural backing and conflicting-fixed-goal errors. |
| Presets | Muscle, Closed Bulk, Rim, Layer, Pouch and Custom provide editable defaults within supported capabilities. |

Absent normal-inflation fields use the existing open-boundary distance rule or
closed-surface uniform rule. Explicit fields, including all-zero fields, are
authoritative. Evaluation does not paint or otherwise mutate shared sources.
Keep authored controls separate from display tessellation and solver samples.
Topology locks apply through every affected consumer and incoming attachment.
Preserve qualified material correspondence; never reinterpret an old index against
new connectivity. Unsupported changes require removal/rebinding of dependencies.

## Attachments and surface roles

Use the shared attachment subsystem for SCP geometry and explicit Tissue base/final
surface roles. A role exists only when its construction provides it; no silent role
fallback. Bindings retain target identity, role, material location, offsets, frame,
topology and revision provenance. Resolving deformation is not closest-point recapture.
Preserve current-shape Fiber editing and explicit rebind operations.

Skeletal anchoring may be indirect: SCP → Fiber → Membrane → Tissue → attached
construction → Tissue. This needs no redundant direct Tissue-to-SCP binding.
Source-relative region goals are the default. Explicit target-relative regions use
the shared attachment service and never rewrite shared sources. Keep anatomical
attachment, path support, collision participation and stacking as separate relations.

## Stacking

Both provider and receiver must be surface-based in 0.2.2. Eligibility is a capability
check on the construction adapter, not on Muscle/Fat classification. The adapter owns
reference geometry, intrinsic output, material correspondence, exact constraints and
provenance; future base adapters can extend it without replacing TissueVCP.

Preserve the production vector stacker: candidate detection, geometric automatic
ordering, explicit/requested order, exclusions, selected regions, multiple providers,
provider-first chains, localized constrained smoothing and independent validation.
Do not sum redundant provider/ancestor displacement. Retain intent separately from
transient evidence; stale evidence never activates a relationship. Preserve current
known rejection cases and exact constraints, including interpolated bindings.

Muscle creation defaults retain automatic stacking. Other tissue presets begin with
stacking disabled; compatible stacking can be enabled explicitly. Regional influence
does not convert stacking into a general sliding/contact or mutual compression solver.

## Results, scheduling and failure

Source/base, inflated rest, intrinsic output and final stacked output are distinct
owned results with independent revision/provenance. Numerical completion is not
anatomical approval. Static relaxation, height smoothing and stacking are separate
stages; combining them adds no new volume-preservation or physical-contact guarantee.

- Intrinsic failure retains the last accepted geometry and reports an Issue.
- If intrinsic evaluation succeeds and stacking fails, show current unstacked output
  with explicit failed-stacking status. It is not a successful final surface.
- Final-surface consumers retain their accepted output and report the failed prerequisite;
  unrelated valid components continue. No incomplete component can wait indefinitely.
- `ITERATION_LIMIT` is a usable current result with a warning when the native contract
  allows it; distinguish it from numerical failure and successful convergence.
- A relaxed candidate introducing transverse self-intersections or collapsed faces is
  unusable and fails intrinsic acceptance. Large normal rotation alone is not failure.
  This is a geometry check, not self-contact resolution or a guarantee of collision-free
  motion between iterations. It preserves reported pre-existing crossings separately.
- Preserve Live/On Release/Manual, dispatch-time inputs, reservations, safe cancellation,
  stale-result rejection, dependency registration, undo/redo and save checkpoint semantics.
- Inflation changes reuse accepted source paths; stacking-only changes reuse intrinsic
  output. Manual accepted inputs retain pending provenance. Startup does not blanket solve.

## Interaction and storage

Use shared operations for all clients. Provide creation from selected construction,
source navigation, per-part/side controls, inflation previews, fields/masks, region
editing, footprint overlays, relationships and rebind. Preview/Cancel is non-mutating;
accepted gestures are one undo action. Selection/inspection never changes anatomy.
Use native cached picking and existing staged publication so hover/click refer to
displayed geometry. Relationship lists remain searchable and virtualized. Technical
details belong in disclosures, with concise actionable status in the primary UI.

Persist editable definitions, source relationships, fields, relationship intent,
workspace state and accepted outputs from the selected revision. Exclude native
handles, transient numerical caches and undo history. Geometry ownership covers
documents, history, checkpoints, jobs and viewport leases. Use one canonical portable
0.2.2 distribution and source archive only after release qualification.

## Intentional differences from the addon

Unified TissueVCP replaces separate Muscle/SoftTissue/Blob entities. Attached typed
construction replaces raw Blender object bases and guarded source-object rewrites.
Legacy Blender schemas, NURBS-specific source evaluation, proxy objects, RNA callbacks,
addon schedulers, mirrors and import converters are not standalone runtime dependencies.
Current standalone curve engines remain authoritative. Native preparation, field
construction and assembly replace remaining addon Python numerical loops.

These architecture changes do not authorize changing the qualified inflation,
relaxation, attachment or stacking algorithms. Record numerical differences against
representative fixtures; do not disguise a parity failure as an intended difference.

The raw relaxation kernels retain addon parity. Standalone publication additionally
rejects newly self-intersecting/collapsed candidates instead of exposing them as usable
iteration-limit output. The donor Pouch preset can produce such output on strongly
curved, thick shells; its defaults do not guarantee validity for every source. Explicit
thickness, relaxation and constraint edits can recover valid output. No silent preset
change, alternate solver or automatic parameter reduction is applied.
