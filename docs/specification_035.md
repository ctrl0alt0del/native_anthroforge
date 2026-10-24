# AnthroForge 0.3.5 — Mirroring

**Status: Implemented — release qualification in progress.**

Runtime operations, storage and evidence are in the [0.3.5 walkthrough](mirroring_035.md).

This is the authoritative 0.3.5 product contract, consolidated from the confirmed
mirroring interview. The [implementation plan](implementation_035.md) defines ownership,
delivery order and required evidence. Apply the [engineering guidelines](engineering_guidelines.md).
This document is not runtime qualification or an announcement of an available release.

## 1. Release boundary and authority

Deliver source-linked, read-only mirrored instances of SCPs, TissueVCPs and their required
construction through the desktop and shared headless core. Preserve existing source
geometry, attachments, drivers and lifecycle behavior. Authoring remains on the source.

The defining invariant is **strict reflection**: every mirrored geometry stage is exactly
the corresponding source stage reflected through its rule's plane. Independent mirrored
attachment deformation, routing, inflation, relaxation, cropping, smoothing and stacking
are forbidden. Asymmetric surroundings cannot change a mirrored object's geometry.

Make Independent, local editable overrides, bidirectional editing, Mirror This Object,
rotated/object-relative planes and mirror tree nodes are outside 0.3.5. Reference images
and unrelated unassigned construction are not automatically mirrored. Existing independent
opposite-side objects are not automatically paired, replaced or deleted. Their migration
is a separate task. Skin symmetry and new export formats are not included; Apply/Bake
remains unavailable.

### Superseded proposals and addon differences

| Earlier proposal or addon behavior | Confirmed 0.3.5 decision |
| --- | --- |
| Independently solve mirrored attachments, routes or tissue/stacking geometry | Reflect the source exactly; report incompatible relationships without reshaping. |
| Missing mirrored target prevents otherwise valid reflected geometry | Report the missing relationship; preserve valid source-reflected display. |
| Edit through either side; local overrides or detachment | Mirrors are read-only; Select Source is the editing route. No Make Independent. |
| Arbitrary reference-frame planes or a single-object mirror action | Document X/Y/Z plus shift; Mirror Children and inherited/required construction only. |
| Show mirror entries in Anatomy or Construction | No additional tree nodes; viewport selection and read-only inspection. |
| Allow an extra mirror of an already symmetric closed path | Suppress the redundant instance; retain the complete symmetric construction. |

The addon's independent-instance paths and the original
[A07 recommendations](../standalone_application_recommendations.md#a07--model-anatomical-types-instances-and-symmetry-separately-p0)
remain historical evidence, not permission to weaken strict reflection.

## 2. Rules, coverage and identity

Expose **Mirror Children**, **Inherit Parent Mirror**, **Axis** and **Shift** on the
source anatomy. A rule mirrors applicable descendants, not its owner's own geometry.
Opt-out stops inherited participation; a nested rule establishes a new source for its
subtree. Rules default disabled; inheritance defaults enabled, axis X and shift zero.
Changing an enabled setting applies directly with one coherent undo action.

Each rule uses one document/world-axis-aligned plane. For the selected coordinate q and
shift s, reflection is q' = 2s - q; the other coordinates are unchanged. Moving/rotating
the owner does not rotate the plane. There is no simultaneous multi-axis rule.

Include required Points/Anchors, Curves/Fibers, Surfaces/Membranes, hooks, lattice cages
and junction relationships. Association, transform parenting, anatomical attachments
and construction references remain distinct; do not infer relationships from names.
An explicit construction plane override resolves incompatible inherited rules without
introducing an individual-object mirror action. Report unresolved conflicts through
Issues, retaining accepted output rather than choosing a parent by traversal order.

One source/rule pair has one stable shared instance, regardless of consumer count.
Different rules may require distinct instances. Plane edits preserve instance identities
and material references. Shared controls remain shared: reflecting two curves using one
hook yields one reflected hook relationship, not two independent copies. Mirrors do not
become authored anatomy or construction nodes.

## 3. Geometry, attachments and dependency behavior

Share source geometry/resources and reflect spatial frames where valid. Do not rerun
source algorithms for mirrors or deform twice. Correct reflected normals, winding,
orientation and signed frame quantities without changing the reflected geometric locus.
Keep base, inflated rest, intrinsic and final stacked stages distinct and reflect each
corresponding stage exactly, including any accepted unstacked fallback label.

Mirrored surfaces are eligible for snapping, confirmed placement, attachments, routing,
measurements and geometry inspection. References distinguish source versus mirrored
spatial instance and preserve SCP/tissue surface roles, material coordinates and revision
provenance. Never silently substitute another role or spatial instance.

Map mirrored attachment relationships to opposite target instances, preserving retained
material bindings, offsets and reflected orientation. **Use same target on both sides**
is an explicit per-attachment choice for shared midline supports; it is not an automatic
fallback when a counterpart is missing. Ordinary deformation and plane edits must not
perform nearest-surface reassignment.

These mapped relationships support inspection and validation, not a second deformation
pass. A missing target or a mismatch against asymmetric supports reports an Issue while
the exact reflected geometry remains. Distinguish relationship findings from source
evaluation failures. Structural relationship failures report automatically; expensive
collision/self-intersection checks run only through **Check Geometry**, identifying the
checked revision. Existing global tissue self-intersection policy is unchanged.

Source tissues may stack against other tissues' mirrored providers through valid
dependencies. Exclude a tissue's own mirror from automatic providers and reject cyclic
stacking dependencies. Evaluate stacking on originals only; their mirrors reflect that
output, never discover or solve separate mirrored stacking geometry. All source drivers,
Parametric definitions and shortcuts remain authored/evaluated once.

## 4. Complete symmetric constructions

Mirrored-row and half-path expansion are source-construction operations, not independent
mirrored-instance evaluation or exceptions to strict reflection.

**Use Mirrored Rows** constructs one surface/Membrane from source and reflected Fiber
rows, not a second bilateral surface. Preserve applicable addon ordering, reversed
reflected rows and avoidance of duplicate plane rows. Keep existing open-loft branch
restrictions: branched mirrored-row constructions are unsupported and return reasons.
Suppress an additional automatic mirror of the complete surface and tissues built from it.

**Create Symmetric Loop** acts on a selected existing open Curve/Fiber. Use its authored
half-path to construct one ordinary closed entity, retaining the selected engine where
supported. Require endpoints on the selected plane and interior points on one side with
an off-plane interior. Invalid inputs produce actionable reasons; never silently move
points to make them eligible. The conversion is one undo action.

Users edit the authored half only. Generate the reversed reflected half read-only,
share the two seam endpoints without duplication and constrain them to the plane.
Preserve Fiber binding requirements and existing topology restrictions. Engine/formula
configurations unable to honor the half-path contract must be rejected explicitly.
Do not introduce a special loop-Fiber entity. Suppress redundant automatic mirrors of
complete symmetric closed paths. Their other consumers may still mirror unless those
consumers themselves represent a complete symmetric construction.

## 5. Selection, presentation and editing

Mirrors have no additional Anatomy or Construction tree nodes. Viewport selection
identifies the actual instance and its source. Show applicable properties, controls,
shortcuts and findings read-only, with **Select Source** for editing. Do not redirect
a mirror edit to the source silently. Enforce read-only policies through shared API,
keyboard tools and direct manipulation, not only disabled inspector fields.

Hover, selection, hiding, isolation and inspection remain allowed presentation operations.
Source and mirror share workspace scope, with **Both**, **Source only** and **Mirror only**
display modes. Hiding either instance does not change computation or attachment validity.
Keep native category colors and distinct source/instance identification. No transient
status should shift fields during editing; reuse existing Ui controls and theme.

Direct mirror deletion is unavailable. Disable participation through the source rule or
inheritance setting. Before removing instances, identify all references. Block removal
when consumers remain and provide one searchable affected-consumer list with navigation;
do not remove a subset or silently redirect references.
Deleting a source also removes its instances and must use the same reference-safety
policy. Existing topology locks must account for incoming bindings to mirrored surfaces.

## 6. Lifecycle, persistence and completion

Display source and mirror at matching source revisions, including supported provisional
previews. Stage compatible replacements together and pick the displayed revision.
Accepted downstream input must never silently consume previews. If source evaluation
fails, retain corresponding last accepted source/mirror geometry and expose the source
failure; there is no independently drifting mirror calculation.

Use the existing coordinator and dependency graph for real source work and reflected
provider readiness. Preserve Live/On Release/Manual behavior, dispatch capture,
cancellation, stale rejection, outside-workspace priorities, undo/redo and save checkpoints.
Share geometry ownership across source/instances while respecting history, jobs,
checkpoints and displayed/staged leases. Do not copy payloads for every drag intermediate.

Persist rules, stable instance identities, plane overrides, explicit same-target choices,
symmetric construction definitions and intentional workspace presentation. Reuse source
accepted geometry instead of storing duplicate reflected payloads. Restore appearance
and relationships without blanket source recalculation or independent mirror solvers.
Do not serialize native handles, transient hover state or undo history.

The documentation-only consolidation assigned no format change. Runtime storage now
uses schema 6, reads schemas 4/5/6 and reuses source geometry. It does not pair existing
independent objects or migrate Blender counterparts. Older applications reject schema 6.
0.3.5 is complete only after the shared API, desktop, geometry, lifecycle, persistence,
performance and portable-package evidence in the implementation plan passes.
