# Curves, fibers, surfaces and reference images

The Construction tab contains editable curves, fibers, surfaces and images separately from
the anatomical hierarchy in the Anatomy tab. You can start with curves or images in an empty document. New
objects are associated with the active anatomy context, without automatically becoming
transform children. Unassigned construction stays accessible.

## Create and shape a curve

Use the viewport icons below Move/Rotate/Scale: **Add Curve at cursor**, **Place Points**,
**Draw Curve**, **Cursor**, and **Patch**. Hover for tooltips. In Place Points, the first click
starts a curve; from point two, plain left-click finishes and exits. Shift-click continues.
Hold Ctrl to snap the preview and new point to the nearest visible SCP surface under
the pointer; Ctrl+Shift snaps and continues. Releasing Ctrl restores your drawing-depth
setting. A missed surface uses that setting's normal fallback; existing offsets apply.
Enter also finishes; Backspace removes the last draft point and Escape cancels.
Closed placement requires three points; an early finish preserves the draft.
Draw finishes on mouse release and stays ready for another stroke. Each completed curve
is one undo action. Cursor settings support numeric coordinates and surface placement.

Drawing depth can use the view plane through the cursor, visible SCP surfaces, or the
selected reference image plane. Surface options include selection filtering, first-point
planes, normal offsets and radius-relative offsets. Choose REFIT, SPLIT or exact POLYLINE.
Fitting uses native Blender 5.0.1 curve_fit_nd; exact mesh picking replaces raster depth.
Fitting cancellation takes effect around the upstream fit call, not within it.

Select the curve and enter editing to move authored points and handles. G/R/S, Shift
insertion, Ctrl surface snapping, wheel offset, axis views 1/2/3 and camera restore 4 retain
their existing behavior. Entering edit mode never refits or resamples the curve.

Select a curve or Fiber and choose its **Path engine** directly in the inspector.
The selection applies immediately as one undo action; no edit mode, separate button,
preview or acceptance is required. All existing authored points, identities and handles
remain; the chosen engine defines the path. Switching back from ROUTED does not turn its
solved samples into new points. Fiber changes use the current resolved authored shape.
Snapping points or creating a Fiber does not switch engines; a new Fiber preserves its
source curve's engine.

BEZIER exposes handles;
POLYLINE keeps exact segments; ROUTED solves between authored structural points around
automatic obstacles. Recalculation follows Live/On Release/Manual settings and keeps the
accepted geometry visible while pending. Topology locks also apply to engine changes.
Generated routing samples never become editable knots. Closure requires three points.

**Automatic obstacles** considers all eligible SCP surfaces across the document, independent
of visibility and workspace. Optional exclusions are searchable; bulk actions affect shown
rows. Manual mode remains available and a manual empty list warns that SCPs are ignored.
Older files with explicit obstacle lists retain Manual behavior; switch them to Automatic
to adopt the new policy. Geometry depending on the routed path is excluded automatically
and explained separately from an explicit dependency failure. Fiber binding/support surfaces
remain required. Points placed directly on an included surface may remain in contact
without becoming anatomical attachments. Points inside an obstacle must be moved out.

## Use curves in construction

Ctrl-select curves or fibers in the Construction list in the desired order, then click
the **Patch / Surface** icon below the transform tools. One closed curve creates a patch;
two or more compatible curves create a standalone loft surface. The tooltip describes
the current action. All loft sources must be open, or all closed. Accepted creation selects
the surface and exits curve editing. Closed lofts show a preview to Accept or Cancel.
**Create Primitive** remains available when the desired result is an SCP loft or body.
Consumers retain live references and own their
ordering, sampling, reversal, range and placement. The source inspector lists its users.
**Shape and transform** follows source shape and pose; **Shape only** retains consumer
placement. Switching modes preserves the visible result. **Make Independent** gives that
consumer its own editable copy. Referenced sources cannot be deleted until their uses are
resolved; deleting a consumer preserves sources.

Closed lofts preview their initial correspondence. **Preview realignment** explicitly
changes it; ordinary deformation does not silently choose another starting point. Branches
use explicit shared junctions at interior points of a main boundary. Closed/nested branches
are unsupported. Branch controls validate these restrictions through the same API as the UI.

## Create and edit fibers

Select a curve, choose attachment surfaces in **Create independent fiber**, then create it.
Both open endpoints need bindings; a closed curve needs at least one chosen binding. The
new fiber has new identities and remains independent of its source. A Fiber is a Curve with
anatomical bindings and can be used by the same primitives and surface tools.

After creation finishes, editing closes and the new fiber is selected. Whole-fiber
Move/Rotate/Scale, their shortcuts, gizmos and numeric transform fields are disabled.
Use **Edit Curve** and select points or handles to shape a fiber; their transform tools
remain available. Fibers continue following their anatomical bindings. A failed or
canceled creation preserves the source editing context.

Authored-engine editing operates on the current resolved shape. Moving a bound point
rebinds it in the same undo transaction. Choose Current parent or Any eligible parent;
ordinary parent movement resolves the retained binding and does not switch parent choices.
Routing can change the path around obstacles. Bézier/polyline fibers preserve their shape
and report sampled-centerline intersections in Issues. These checks do not prove continuous
curve clearance or anatomical correctness. Failed evaluation keeps the last accepted result.

**Shared junction → Join points** creates explicit sharing; proximity alone does not.
Editing a junction updates incident authored points together. **Detach junction** preserves
their current shape and bindings. Surfaces accept curves and fibers through one common path
contract. Lofting does not collision-conform a surface or produce a muscle volume.

## Place and trace reference images

The image icon beside Perspective/Orthographic imports a world reference image.
**Add reference image…** in the selected object's Properties imports an image with
that ordinary parent. Orthographic X/Y/Z views automatically set world-axis alignment,
including under rotated parents; other views use default placement. These actions import
PNG/JPEG, normalize EXIF orientation and embed the source.
Use Instance for another placement sharing the asset. Ordinary parenting preserves world
placement; images cannot be parents. Width, axis alignment, opacity, depth, sides,
orthographic/perspective visibility and viewport pickability are exposed in the inspector.
**Only axis-aligned views** hides the image when the view deviates from its local Z axis;
it changes visibility and picking rather than rotating the image. Face axis buttons rotate
the authored placement separately.

**Calibrate distance…** takes two image landmarks and a known distance as one undo action.
Replace changes the selected assignment, retains position/physical width, adjusts aspect
ratio and clears its old calibration. Other instances are unaffected. Tracing against the
image creates an independent curve, without a continuing image dependency.

## Save and automate

Current schema 4 projects contain editable relationships, accepted results and embedded images.
Earlier schemas, including the original 0.2.0/0.2.1 schema 3, are rejected; conversion is deferred. Opening
preserves the existing startup calculation policy rather than rerouting everything.
Live, On Release, Manual, save checkpoints and undo retain their established behavior.
Outside-workspace consumers continue at lower priority. Apply/Bake is unavailable.

From a writable copy of the portable folder, run:

```powershell
./AnthroForge.exe --cli run examples/construction.json
./AnthroForge.exe --project construction.anthroforge
```

The example creates two sources, two independent fibers, a shared loft and an embedded
synthetic reference grid. Its fixed sequence uses `inspect` to obtain the asynchronously
created fiber IDs. Applications should inspect completed jobs/objects rather than infer IDs.
See [the API](authoring_api.md) for image operations, conversion, bindings, junctions,
surface sources and branches. Shift+F12 records reports without rebuilding the application.

Muscles, soft tissues, mirroring, legacy-project conversion and broader export remain deferred.
Observed development, parity, profiling and offscreen evidence is tracked in
[the implementation record](tasks/020-construction.md); offscreen checks do not establish
physical input/display latency or a performed interactive desktop session.
