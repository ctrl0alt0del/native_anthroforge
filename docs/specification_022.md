# AnthroForge 0.2.2 — unified tissues

Status: implemented product contract; release evidence and limitations are in
[development validation](development_status.md#unified-tissues-022). Follow [engineering guidelines](engineering_guidelines.md),
the [implementation plan](implementation_022.md), and [task status](tasks/unified-tissues-022.md).

## Release contract

**Intersection policy (2026-10-21): self-intersections within one TissueVCP are
intentionally allowed.** Inflation and height smoothing keep their existing numerical
behavior; they do not untangle, Boolean-repair or replace the evaluated tissue.
This is a revisitable product decision, not evidence that every downstream operation
is insensitive to intersections. Investigate concrete downstream bugs before revising
it. Separate tissues remain separate. Skin handling will be decided with skinning.
Implementation and downstream-query qualification are tracked in
[the active task](tasks/tissue-intersection-policy.md).

The confirmed downstream contract is **pending implementation and qualification**:

- Shared surface queries distinguish Preview and Confirmed Placement. Preview uses
  the original accepted target; confirmed placement uses a Boolean-cleaned query copy.
  Curve-to-Fiber, Point-to-Anchor and explicit attachment capture use confirmed mode.
  Cleanup never replaces the target, and hit provenance must map back to the original
  material binding. Existing bindings resolve their retained location rather than
  choosing a new nearest point on each update.
- For open single-sided tissue, use a temporary closure against its material base for
  the Boolean calculation. The cleaned mesh exists only in memory for confirmed
  queries. Added backing and closure faces are not selectable attachment surfaces.
  This does not authorize arbitrary thickness or caps for unrelated open meshes.
- Where intersections create ambiguous stacking support, select the farthest support
  along the base-surface normal. Keep this distinct from nearest material-chart distance
  and from any repair to the generated tissue. Separate tissues are not Boolean-unioned.
- Skin handling is deferred until skinning implementation.

Deliver production tissue construction, anatomical attachments, inflation,
relaxation, branches, cropping and stacking in desktop and Qt-free headless clients.
Mirroring, Draft Skin, Blender-project conversion, anatomical reconstruction or
automatic fitting, animation dynamics and generalized physical contact are deferred.
Apply/Bake is permanently unavailable. Product export remains built-skin-only.
Schema **4** is the only supported project format; reject all earlier schemas,
including 0.2.1 schema 3, clearly without partially loading them.

Desktop **Create Tissue** acts directly on selected Point, Curve or Surface construction
with compatible defaults; no source-selection modal. Without eligible selection it is
disabled. Existing Anchor/Fiber/Membrane sources remain shared references. Generic sources
automatically obtain independent attached copies in the same undo action, using nearest
ready SCP surfaces for new bindings. Missing supports produce actionable feedback without
partial creation. This supersedes the earlier explicit-conversion/source-chooser requirement.
Source navigation enters editing. Selecting a weight field enters component editing;
committing Weight applies to selected points in one undo action. Stacking order and
exclusion changes apply immediately; footprint drafts and inflation previews retain
their deliberate Accept/Cancel lifecycle.

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
  Mixed/ordinary-curve inputs produce a generic Surface. **Create Membrane** independently
  copies the whole required construction graph, converts ordinary curves to Fibers and
  preserves existing Fiber binding intent. It uses the same operation as automatic tissue
  conversion. Copy internal junctions once; preserve source ordering, alignment and settings.
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

Transient calculation, pending and error feedback uses a nonmodal bottom-right toast.
It cannot add/remove inspector rows, alter widths, steal focus or interrupt numeric drags.
Diagnostic detail remains in Activity/Issues and operation details. Scroll views reserve
their scrollbar gutter so changing content height cannot narrow editing controls.

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

### Supported combinations

The shared `core/tissue_policy.py` enforces this matrix for UI and API. Labels do not
expand capabilities. None always bypasses relaxation; Off always bypasses height smoothing.

| Source and inflation | Geometric / Static PBD | Height smoothing / material crop | Two-sided composition | Surface stacking |
| --- | --- | --- | --- | --- |
| Anchor, Radial | Both | Neither | No | No |
| Open or closed Fiber, Profile sweep | Both | Neither | No; sweep owns its cross-section | No |
| Membrane, Normal shell (loft, closed loft, patch or open branch) | Both | Neither | No; shell owns its backing/rim | Yes |
| Membrane loft, Control Point / Distributed | No; use height smoothing | Both | Open material axes only | Yes |
| Ordinary open Membrane loft, Section Profile | No; use height smoothing | Both | Yes | Yes |
| Branched open Membrane, Control Point / Distributed | No; use height smoothing | Both, per-part smoothing | Yes | Yes |

Section Profile excludes patches, closed axes and branches. Branch construction retains
explicit junctions and rejects nested/closed branches and overlapping root intervals.
Stacking requires both participants to opt in and pass material/geometry validation; an
eligible source is not a promise that every order or requested displacement is feasible.
Fixed backing is exact. Constraints cannot request a different fixed backing location;
contradictory goals fail rather than weakening one constraint. Normal-shell INFLATION
weights use the Base domain; named constraint fields use Base or Rest. Fields retain
material signatures and must be explicitly replaced if that domain's topology changes.

Membranes provide Tissue Base and Final roles. Radial/sweep tissues provide Final only;
their point/path sources are not substitute attachment surfaces. Final is unavailable
after failed stacking even when current unstacked geometry remains displayed.

Default muscle inflation on a loft is Distributed, 0.02 m, with height smoothing Off and
relaxation None. Muscle creation on a Membrane enables stacking; point/path construction
keeps its compatible Radial/Profile mode and cannot stack. Closed Bulk, Rim, Layer and Pouch
retain their captured donor defaults and disable stacking initially; Custom chooses
the source-compatible inflation family with relaxation None and stacking disabled.
Presets are applied only on creation. Per-mode controls and inactive side values survive
switches. Preset values and source hashes are pinned in `tests/fixtures/tissue/presets.json`.

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
- Tissue inflation, height smoothing and relaxation may introduce self-intersections.
  Nonfinite output and newly collapsed faces remain failures. Large normal rotation
  alone is not failure. Explicit geometry diagnostics can still count crossings, but
  those counts do not reject intrinsic tissue output. This supersedes the earlier
  rejection of transverse crossings; it adds no self-contact or repair computation.
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

The October 20 repair is a separately authorized numerical correction to Distributed
inflation. Its direction field uses area-weighted normals and screened surface
diffusion over the authored inflation distance, followed by normalization. The
authored amount, boundary weights and taper set displacement lengths; the inherited
local stability reduction is removed because it introduced abrupt height dips.
Fixed boundaries and all authored settings remain intact. Control Point and Section
Profile formulas retain donor parity. Original donor fixtures remain preserved;
Distributed/branch/envelope correction snapshots are explicitly labelled separately.

Material refinement subdivides existing intervals only where the requested density
requires it. It retains every original grid line, avoids introducing nearly coincident
lines, and never edits the source. Height smoothing retains the donor QP, hard pins
and change bounds. Complete-mesh validation tests new transverse intersections and
collapsed faces rather than treating a normal rotation beyond 90 degrees as a fold.
Coincident front/back boundary contact is not a transverse intersection. These
checks do not guarantee that arbitrary inflation settings are geometrically feasible;
invalid generated geometry remains a failed result without reducing user parameters.
For height smoothing, reaching PIQP's stricter iteration limit is not by itself
proof that the application tolerance was missed. Such a result can publish only
after independent KKT certification at the existing `2e-7` tolerance, exact pins,
and geometry validation. Diagnostics retain `ITERATION_LIMIT` and report measured
residuals; other solver failures and uncertified iterates remain failures.

The raw relaxation kernels retain addon parity. Standalone publication additionally
rejects newly self-intersecting/collapsed candidates instead of exposing them as usable
iteration-limit output. The donor Pouch preset can produce such output on strongly
curved, thick shells; its defaults do not guarantee validity for every source. Explicit
thickness, relaxation and constraint edits can recover valid output. No silent preset
change, alternate solver or automatic parameter reduction is applied.
