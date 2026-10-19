# AnthroForge 0.2.1 — curve workflow improvements

Status: implemented and qualified, 2026-10-19. Confirmed behavior below is implemented;
release qualification is tracked in [development status](development_status.md#curve-workflows-021).
Muscles, soft tissues and other VCP work move to **0.2.2**. The qualified 0.2.0 runtime
remains described by [its specification](specification_020.md) and
[validation record](development_status.md). Follow the [engineering guidelines](engineering_guidelines.md).

## Confirmed changes

### Viewport tools

Place five distinct icon buttons below Move, Rotate and Scale in the viewport toolbar:
Add Curve at Cursor, Place Points, Draw Curve, Cursor, and Patch. Provide tooltips and
visible active-tool state, reuse Ui controls/Theme, and keep relevant tool settings
accessible. These actions must invoke shared operations and the existing tool lifecycle.
Patch uses the selected compatible closed curve and existing shared validation.

Remove the separate **Loft selected curves** menu entry. Selected curves can already
feed Create Primitive. This removes the redundant user-facing entry; it does not authorize
deleting the generic Surface model or surface construction used by patches and fibers.
The existing entry creates a standalone construction Surface, while Create Primitive
creates an SCP. Preserve that distinction in the core even when simplifying entry points.

### Place Points

The user explicitly confirmed that “starting from 2nd curve” means the second **point**:

- The first left-click starts a curve and places its first point.
- From the second point onward, plain left-click adds the final point, completes the
  curve and exits Place Points.
- Shift + left-click adds a point and keeps Place Points active.
- A completed curve is one undo action; provisional points are not separate commits.
- Route the continuation modifier through the keyboard/action abstraction, not a
  hardcoded Shift check in QML. Retain existing cancel, last-point removal and camera tools.
- Closed-curve placement still requires at least three points. An early finish attempt
  must retain the draft and explain the minimum rather than discard it or create invalid data.

The final rule is an implementation safeguard for the existing closure contract, not a
change to the confirmed open-curve interaction. Draw remains a separate tool whose
release finishes one stroke while leaving it ready for another.

## Previous 0.2.0 controls: verified meaning and motivation

| Current control | Meaning in 0.2.0 |
| --- | --- |
| Path samples | Number of evaluated path samples, distributed between authored routing points. These are numerical/output samples, not new editable points. Higher values increase detail and computation; they do not guarantee a valid route. |
| Surface clearance | Desired distance of the routed centerline from obstacle surfaces, in document display units. The screenshot's 0.0020 m means 2 mm. Local contact at bound/touching routing points is permitted; this is not rendered curve thickness. |
| Accepted solve steps | Budget for accepted numerical optimization updates. The solver may finish earlier and may also perform rejected trials; it is not a time limit or an exact count of all internal work. |
| Routing obstacles | Explicit SCP surfaces supplied to the solver, plus automatic Fiber binding/support surfaces. Ordinary curves with none selected ignore SCP geometry. |
| Point checkboxes in conversion | Select existing authored points retained as routing constraints. Unchecked points are removed from the converted definition; generated samples are never silently turned into constraints. Open endpoints, bindings and junctions must be retained. |
| Preview conversion | Evaluate a provisional conversion. Accept commits it; Cancel discards the preview. |
| Create fiber from curve | Make an independent curve copy with anatomical bindings; it is not required to use routing on an ordinary curve. |
| Control point selector | Choose which existing authored point to inspect/edit; separate from conversion point selection. |

The two obstacle sections in the screenshot edit different state: conversion options and
the current curve's settings. Showing them together obscures that distinction.

Implementation evidence: `core/curve_engines.py`, `core/curve_conversion.py`,
`application/conversion_geometry.py`, `core/curve_dependencies.py`,
`desktop/qml/CurveConversion.qml`, `desktop/qml/RoutingSettings.qml`, and native
`routing_reference.cpp`, `routing_world.cpp`, `routing_solve.cpp`.

## Confirmed routing defaults and scale requirements

### Automatic obstacles

Automatic obstacle selection is the default. The user confirmed that the addon already
has this behavior; explicitly excluding an obstacle is optional. A new ordinary routed
curve must work without manually checking every SCP. Fiber binding/support surfaces
remain automatic. Visibility and the active workspace should not silently determine
physical obstacles. Exclusion changes collision participation, not an existing binding.

The addon implementation confirms automatic enumeration of root-associated SCP mesh
geometry: `core/vcp/fiber_collision.py::_build_colliders_uncached`, called through
`CollisionOracle.colliders()` by `core/vcp/fiber_v2_runtime.py`. Its shared query layer
also has bounds-based active-collider selection and caches, with spatial indexing from
32 colliders. Required colliders are retained. Explicit muscle supports supplement SCPs;
muscle/VCP implementation remains deferred to 0.2.2. Port the policy through native data
contracts rather than copying Blender access or Python numerical loops.

This is a shared routing-input policy, not a UI select-all action. The implementation reuses
immutable native collision captures through a bounded cache and keeps the existing native
spatial index. All eligible geometry remains in the capture; no straight-segment-only
pruning is used. Solves validate against that complete scene. The measured 100-cube fixture
is dominated by solving, not capture; reuse does not establish a general solve speedup.

Automatic policy must account for eligible geometry across the document, safe exclusion
of geometry dependent on the path itself, and the distinction between an exclusion and
a dependency error. Missing accepted geometry cannot silently become empty space.
Candidate filtering must cover the explored route, expand when necessary, and validate
the result against the eligible scene. Testing only the initial straight segments can
miss obstacles encountered by a detour.

Track scene-query membership as well as individual captured surface revisions. A new or
moved obstacle entering the route must invalidate affected work even if it was absent
from the previous candidate set. Preserve Manual provenance, outside-workspace priority,
dispatch capture, cancellation and stale-publication protection through the coordinator.

Acceptance needs the user's two-cube case and larger scenes; compare route correctness,
preparation, native execution and retained memory in profiler reports. Include obstacles
moving into a route, newly created/deleted geometry, changing workspaces, exclusions,
consumer cycles and missing/Manual results. See qualification for measured scope and limits.

### Conversion points

Retain all existing authored points by default when switching to routing. Choosing a
subset is optional; all authored points remain accessible in that editor. Preview shows
which points will be retained. Endpoints, bound points and junctions remain protected.
Never silently use every tessellated/rendered sample or reduce the curve to endpoints only.

This changes the earlier requirement for manually checking each structural point. The
reason for structural points remains valid: the solver must pass through them, so a dense
drawn curve can constrain its freedom. Explicit subsets remain available in the optional editor.

### Lists with 100 or more items

Both obstacle exclusions and optional point selection must remain comfortable with at
least 100 items. The ordinary inspector shows a compact summary and an optional Edit
action, not an expanded column of 100 checkboxes.

Recommended interaction: a bounded-height searchable list with scrolling, virtualized
rows and incremental updates; show all versus excluded/selected filters, counts, bulk
selection/restoration, and preserved search/scroll state. Give obstacles unambiguous
names plus hierarchy context; keep authored point numbers stable under filtering and
highlight a focused point in the viewport. Search/filtering must not change membership.
Define whether bulk actions affect the visible filtered results and label that scope.

The user confirmed default behavior, optional overrides and usability at 100 items;
the exact list layout and button wording remain design recommendations. Validate the
actual offscreen UI with 100+ obstacles and 100+ points, including duplicate object names,
filtering, scrolling, bulk changes, required-point protection, preview and undo. Profile
model churn and input handling; a screenshot alone does not establish responsiveness.

## Presentation

Numerical budgets appear in an Advanced section, using clearer labels such
as Path Resolution and Iteration Budget, and showing one contextual obstacle editor.
Surface clearance remains directly accessible with a short tooltip and explicit units.

## Delivery boundaries

The implemented list uses incremental keyed Qt models, bounded virtualized rows, search,
filters and explicitly scoped bulk actions. Automatic obstacles and all-authored-points
defaults are settled. Preserve the current native engine, shared operations,
transactions, topology restrictions and 15-line function limit. Validation remains
background/offscreen while the user is using the computer.

Reference: [CGAL AABB-tree documentation](https://doc.cgal.org/latest/AABB_tree/) describes
spatial intersection/distance queries. It provides background, not a substitute for
AnthroForge's own geometry and responsiveness qualification.
