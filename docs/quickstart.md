# AnthroForge 0.2.2 quick start

Start with [curves, fibers, surfaces and images](construction_020.md).
Continue with [attached construction and tissues](tissues_022.md).
Schema 4 projects reject earlier schemas, including 0.2.1 files; no conversion is included.
The existing primitive, attachment and navigation workflow below remains applicable.

The Activity panel retains its job rows while status and elapsed time update. It shows
the latest 40 jobs, newest first; Cancel and Retry continue to act on the named job.
Use Shift+F12 performance recording when reporting an editing slowdown.

See [UI polish](ui_polish.md) for compact measurements, expandable evidence and
shared menu/control styling.

## Portable Windows application

Open AnthroForge.exe in the complete AnthroForge.dist folder. Keep the folder's DLLs,
QML files and other runtime files together. Blender, Python and a Qt SDK are not
required to run this distribution.

1. Choose **Import mesh**, select examples/primitives/cube.obj, choose **metres**,
   and import. The cube is centred at the origin and has sides of one metre.
2. Select the root in the hierarchy. Import cube.obj again with **metres**,
   choosing the root as its parent. Each file becomes one independent SCP.
3. Select the child, set each scale component to 0.2 and its X position to 1 metre.
   Edit Position/Rotation/Scale in the inspector or drag the coloured axis handles.
   Entering a value commits it; a completed drag is one undo action. Escape cancels.
4. Move the parent and observe the child attachment. The inspector exposes parent
   and child anchor modes, face/vertex locks, follow rotation and rotation strategy.
   Pick a lock on the selected child, or clear it and recapture.
5. Save as a .anthroforge project, close, then reopen. The file contains its mesh data;
   the original OBJ/STL/PLY file is no longer needed.

Right/middle drag orbits; Shift plus that drag pans; the wheel zooms; F frames the
selection. **G/R/S** starts Move/Rotate/Scale: move the mouse, then left-click or press
Enter to confirm; right-click or Escape cancels. W/E selects the Move/Rotate gizmo.
**1/2/3** looks along global X/Y/Z, respectively, in orthographic projection; 5 toggles
projection. Axis views center the active selection and preserve apparent zoom. During
component editing they center the selected points; otherwise they center the SCP geometry.
Press **4** or click **Restore** to return to the camera before entering axis views,
including its position, rotation, zoom and projection. Repeated axis keys or buttons
keep that original camera until restored; afterward the next axis switch captures a
new original. Switching workspaces or documents clears this temporary return point.
Switch views or restore during a drag or modal transform to adjust another pair of coordinates;
the current edit stays open, without jumping or adding an undo step. These shortcuts leave text entry alone. Alt-click
cycles through deeper eligible SCP hits. Hover predicts ordinary selection.

Move arrows constrain to a world axis; the small planes constrain to two axes, and the
center circle moves in the view plane. Rotate rings turn around world axes. Scale squares
use an object's local axes; the center square scales uniformly. Component transforms use
world axes around their selection center. Hold Shift for a finer adjustment. Every gesture
is one undo action; Escape restores its starting state.
Modal rotation turns around the viewing direction; modal scale is uniform. Rotating or
scaling selected curve points also transforms their handles. Explicitly transformed
automatic/vector handles become editable through the existing handle-editing rules.

The selected SCP has an orange silhouette outline. Editing a loft or body curve makes its
surface translucent; **Finish editing** restores normal shading. Neither effect changes
saved anatomy or object colors.

Press **Delete**, choose **Edit > Delete selected**, or use the tree's trash icon. Only the
chosen SCP is removed: children move to its parent with their world poses preserved.
Deleting a root with children replaces it with an empty grouping root. Deleting a leaf
root leaves an empty document. Controls supported by the deleted SCP detach at their
current world poses. A shared control can also be deleted; the dialog explains that its
bindings will be removed while primitives remain. Deletion is undoable. Keyboard commands
respect text entry, modal dialogs, active transforms and blocked-save state.

Meshes use opaque studio shading by default, with lighting that follows the camera
and preserves object colors. **X-ray** beside the view buttons (or **Alt+Z**) makes
surfaces translucent for inspection; selected and hovered objects remain more visible.
Focused workspaces still show outside objects as faint, read-only context.

The searchable **Outliner** has expandable branches, an eye for visibility and a target
for viewport picking, plus a trash icon for deletion. Drag the panel dividers to resize the outliner and properties.
Properties are grouped into collapsible Transform, Attachment, and Display & evaluation
sections. X/Y/Z fields use matching axis colors; Enter commits and leaves the field.
Use the top menus for project operations and **Help > Navigation and shortcuts** for
controls. Hover toolbar icons for tooltips. **Activity** expands from the bottom of the
viewport; its summary reports pending work and failures even while collapsed.

The global update mode and each SCP's override support **Live**, **On Release** and
**Manual**. Manual changes keep the previous dependent results until **Recalculate**.
Disabling attachments freezes dependent poses; re-enabling captures the current poses
before subsequent parent changes. **Move origin to anchor** preserves mesh position.

Small Live attachment updates move parents and children together immediately. Larger
updates run in the background with a short, workload-dependent delay that combines
rapid edits. Enable diagnostics to see estimated cost, planned wait and actual execution
time in Activity. Imports, project opening, saving and explicit recalculation have no
added coalescing delay.

Use **Focus…** beside the workspace selector to create a named workspace, optionally including existing
descendants. Other SCPs remain transparent and read-only; their dependency relations
still participate in calculations. Workspace cameras, visibility and overlays are
saved separately from anatomical undo. Copies are independent; no linked mirroring.
Viewport **Overlays** controls handles, anchors and diagnostics. The reference grid is
spaced at 0.25 metres and can be toggled beside the orientation buttons. Panel widths,
grid visibility, X-ray, search and collapsed sections are temporary editor layout settings.

When calculations are pending, Save offers cancel, the latest committed checkpoint,
or wait for running and queued writes and then save. Waiting blocks edits. The
checkpoint is the revision before the earliest remaining started writer, rather than
an arbitrary partially completed result. Failed calculations finish and can be saved;
Activity shows the error and permits retry. Saving a checkpoint may leave newer edits
unsaved, as indicated by the title's asterisk.

## Headless authoring

From PowerShell in the portable application directory:

```powershell
./AnthroForge.exe --cli doctor --require-native
./AnthroForge.exe --cli run examples/assembly.json
./AnthroForge.exe --cli run examples/primitives.json
./AnthroForge.exe --cli inspect assembly.anthroforge
./AnthroForge.exe --cli render assembly.anthroforge assembly.png --revision 11
```

Use the saved revision reported by inspect for render; it rejects a different revision.
Rendering uses a Qt/GPU texture without showing a window. Numerical commands do not initialize Qt.
When capturing console output from a GUI executable, use a subprocess and wait for its
exit; PowerShell may return before the process exits. Automated clients should use
standard input/output pipes and inspect the exit code.

**serve** accepts one JSON request per input line and emits one JSON response per line.
Background calculations continue between requests. **run** accepts a JSON array.
Optional request IDs allow later arguments such as "$root.entity_id". Paths resolve
relative to the process working directory. Both transports use the desktop's core API.
They are local authoring transports; an MCP server is a later adapter.
The complete operation catalogue is in [authoring_api.md](authoring_api.md).

Save requests must explicitly specify blocked_policy: **wait**, **checkpoint**, or
**pending**. A pending response does not save. Use wait before inspecting completed
results and explicitly save before ending a session; EOF does not save automatically.

## Boundaries

0.1.3 imports OBJ and ASCII/binary STL/PLY, keeps canonical polygons and derives render
triangles. OBJ objects are combined into one SCP. Mesh materials/textures are ignored.
Source units and optional Y-up conversion are explicit; documents use metres.

This release edits imported SCP assemblies, native primitives and shared deformers.
It does not build skin,
export geometry, edit mesh vertices, migrate Blender projects, merge documents, preserve
undo across sessions, or provide crash recovery. Fibres, muscles, tissues, skin and
topology are later milestones. Simple Solidify is supported; Complex mode is deferred.

## Create and edit primitives

1. Choose **Create Primitive > Loft**. A new SCP starts with two Bézier curves.
   **Edit Primitive** exposes its curve points and handles. Click a curve to select its
   points, click a point/handle for a component, and Ctrl-click to extend selection.
   Use Move/Rotate/Scale or the matching numeric fields. Radius and tilt are geometric
   parameters; tilt is in radians. Control cages show authored coordinates before deformers.
2. In **Curves**, add/copy/remove and reorder curves. Adjacent pairs form connected
   strips with shared boundaries. Sampling start/span can be overridden per curve.
   Closed cross-sections can be capped; **Thickness** adds an editable shell.
3. Create a **Box**, **Cylinder** or **Capsule** to start a curve-driven body. Edit its
   path and body width/depth. It fits the entire curve by default; disable that option
   for a fixed length and position along the path. Additional curves create body pieces.
4. Select an SCP and use **Deformers > Add Lattice**. The fitted cage appears separately
   in the outliner. Select cage points and move them, or edit coordinates numerically.
   Resolution, interpolation and Outside are cage settings. Resizing uses Blender's
   linear transfer semantics and clears cage weights; it need not preserve exact shape.
5. Select curve controls, cage points or imported/base vertices, then **Add Hook**
   in Deformers. The new shared control initially preserves their positions. Move that control
   to deform the selected target. Imported/base vertices permit membership and weights,
   without direct coordinate editing. **Select members**, **Assign selected**, and
   selected-weight editing are available in the binding inspector.
6. Deformer bindings expose enabled state, order, strength and weights; Hooks also have
   falloff, custom curve points/handle modes, reset and recenter. A shared control can be
   bound to another SCP through its inspector. Curve/BASE/LATTICE bindings are scoped to
   their construction target; generated-geometry bindings act afterward.
7. A control can follow the document or an SCP, preserving world placement when changed.
   Local attachments can use an SCP surface or another control. The inspector lists
   affected SCPs. Removing a binding preserves the control and its other consumers.
   Deleting the shared control displays its affected SCPs before removing their bindings.
8. Topology edits lock while children or incoming surface attachments exist. Shape edits
   remain available. Remove those dependents to unlock topology. A real dependency cycle
   retains previous results and finishes as a failure shown in Activity.

Live, On Release and Manual apply per SCP even when controls are shared. During work,
the previous complete mesh remains visible until its replacement is ready. A Live target
may use a Manual support's last accepted surface and report pending upstream changes.
**Recalculate this SCP** evaluates its required prerequisites through the shared core;
the top toolbar's **Recalculate** evaluates the whole document.
Save/reopen retains construction parameters, source assets, bindings and accepted results.
Apply/Bake is never available.

While editing curves, hold **Shift** to preview a new point at the closest curve location
to the cursor. Each left click inserts a point; keep Shift held to insert more. Releasing
Shift hides the preview without adding anything. Each click is one undo step. Subdivision
preserves the authored Bézier shape, interpolates radius/tilt, and changes the two adjoining
points' handles to Free so automatic handles cannot reshape the curve. Other point identities
and Hook memberships remain stable; primitive sample resolution is unchanged.

Drag a point directly, or use its Move gizmo. Hold **Ctrl** before or during that drag to
snap the selected point to the nearest visible SCP surface under the pointer. Move across
SCPs freely; the edited SCP is excluded. Context outside a focused workspace can provide a
snap surface without being edited. Releasing Ctrl restores movement in the original view
plane; a miss also uses ordinary movement. Snapping places the point without creating a
persistent attachment. Escape or switching applications cancels an active drag.

While snapping, the mouse wheel changes a signed offset along the hit surface's world
normal. Positive values follow its authored normal; negative values go into the surface.
The marker displays the offset in the workspace display unit. One notch uses the world distance corresponding
to eight screen pixels at the selection depth; Shift makes the adjustment ten times finer.
The wheel does not zoom during snapping. **Middle-click or release Ctrl** to reset the
offset to zero. Middle-click preserves the active edit. The offset carries across snap
targets within the gesture and resets when the gesture finishes or is canceled.

Curves are purple, control points gold, and handle points/links blue. Selected and hovered
components retain their type colors with larger markers. The help menu lists the defaults;
modifier choices are owned by the keyboard manager, alongside existing shortcut bindings.

## Inspecting issues

Open **Issues** below the viewport. Select a finding for its evidence and related
objects; **Select target** and **Frame target** help locate it. Filter by text or
severity. **Dismiss** hides only the current source revision; **Dismissed** allows
restoring it. **Recheck** detects problems without editing geometry.

An available **Recalculate target** or **Retry calculation** action is explicit and
requires a fresh verification before being marked resolved. Check failures retain
old findings as stale. “No findings in available checks” is not a general geometry
or anatomical certificate. See [issue reporting](issues.md) for coverage and APIs.

## Recording a slowdown

Press **Shift+F12**, reproduce the problem, then press Shift+F12 again. You can toggle recording
while dragging and while holding Ctrl/Shift/Alt. The top bar shows recording/export
status and **Show file** after completion. Share that `.afprofile.zip` file.
Windows reports are under `%LOCALAPPDATA%/AnthroForge/Profiles`. The default capture
keeps the latest 120 seconds within its storage budget. See [profiling](profiling.md)
for headless operations, privacy, limits and interpreting costs.

## Relationships, workspaces and reports

Expand **Relationships & attachments** in Properties for inputs, consumers, surface
anchors and topology locks. Use **Manage…** beside the workspace selector to edit
mixed SCP/control membership, choose display units and adjust category show/select
filters. **File → Export inspection report…** saves a frozen image/JSON archive while
you continue working. See [the workflow walkthrough](workflow_inspection.md).
