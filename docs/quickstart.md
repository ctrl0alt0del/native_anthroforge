# AnthroForge 0.1.2 quick start

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
selection. W/E/R selects Move/Rotate/Scale; 1/3/7 selects Front/Right/Top and 5 toggles
orthographic projection. These viewport shortcuts leave text entry alone. Alt-click
cycles through deeper eligible SCP hits. Hover predicts ordinary selection.

Meshes use opaque studio shading by default, with lighting that follows the camera
and preserves object colors. **X-ray** beside the view buttons (or **Alt+Z**) makes
surfaces translucent for inspection; selected and hovered objects remain more visible.
Focused workspaces still show outside objects as faint, read-only context.

The searchable **Outliner** has expandable branches, an eye for visibility and a target
for viewport picking. Drag the panel dividers to resize the outliner and properties.
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

0.1.2 imports OBJ and ASCII/binary STL/PLY, keeps canonical polygons and derives render
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
   points, click a point/handle for a component, and Shift-click to extend selection.
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
