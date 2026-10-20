# Inspection, measurements and repeatable views

Select an SCP or control and expand **Relationships & attachments** at the bottom of
Properties. Each output lists its inputs (**Driven by**) and consumers (**Drives**).
**Select** and the frame icon navigate to related objects, including read-only context.
The panel shows accepted/authored revisions, captured attachment coordinates, world
anchors, geometry counts and the objects preventing topology edits. Inspection is
read-only; collapsed details do no refresh work. Navigation is disabled during edits.

The Issues panel distinguishes **DEPENDENCY_CYCLE** (an output in a strongly connected
cycle component) from **DEPENDENCY_BLOCKED** (an output downstream of a cycle). Evidence
lists the causal components and their named outputs. This is output-level causality,
not a claim that every listed object participates in every cycle. Pose following that
feeds another object's geometry remains a valid dependency. Breaking a relationship
is always an explicit authoring operation.

## Workspaces and presentation

**Focus** immediately creates a named workspace from selected anatomy and its descendants.
Use **Manage…** beside the workspace selector to rename it inline or adjust membership
and presentation. This panel is nonmodal: viewport navigation remains available while
it is open. A named workspace can contain any mix of SCPs and controls.
Removing the active workspace returns to the whole document. Other
objects remain transparent and read-only, with their dependencies still evaluated.
Membership changes wait until the active edit/save finishes. An empty named workspace
is valid. Deleted object references are retained for undo; they are not shown as live
members. Updating membership explicitly replaces the chosen set.

Show/select filters independently cover geometry, curves, points, handles, hooks and
lattice cages. Attachment markers have a show filter. Hidden elements cannot be picked;
unpickable visible elements remain context. These filters govern viewport picking, not
explicit outliner selection or API authoring. In Edit Primitive, hiding geometry still
allows curve editing. Imported vertices use the point category. Cage coordinates remain
normalized cage coordinates. Transform gizmos retain their separate overlay switch.

**All elements**, **Shape editing**, **Surface review** and **Attachment inspection**
are reusable category presets. They do not change workspace membership or object-level
visibility, and do not calculate geometry. Existing object/overlay switches still apply.
Presentation settings are stored per workspace outside anatomical undo history.

## Units

Choose **m**, **cm** or **mm** under **Display lengths**. Position fields, curve points
and handles, body dimensions, hook falloff distances, shell thickness, attachment
coordinates and the snap-offset marker display/accept that unit. For example, entering
250 with mm selected stores 0.25 metres. Angles, normalized cage coordinates, curve
sampling fractions, radius multipliers, scale and thickness ratios are unchanged.

All geometry, project coordinates and JSON API length arguments remain metres. Import
source units remain explicit and independent. Changing display units never rescales
geometry, invalidates calculations or adds an anatomical undo action.

## Measurements and named views (0.1.8)

Open **Measurements & views** at the lower right of the viewport. Press **Ruler**,
then click two visible, pickable SCP surfaces. They may belong to different SCPs.
The cursor shows the candidate XYZ; saved rulers show A/B XYZ, delta XYZ and the
straight-line distance in the workspace's chosen m/cm/mm unit. Alt-click cycles deeper
surfaces using the same picking policy as selection. Escape exits; another pair of
clicks creates another ruler. Hidden, unpickable and read-only workspace context cannot
be picked. Rulers are an inspection mode, unavailable while an anatomical drag is active.

Rulers capture fixed coordinates. Moving, regenerating or deleting a source surface
marks them **stale** and draws a yellow dashed line; their numbers stay unchanged for
comparison. Remove a ruler with its delete icon and pick again for a fresh measurement.
They do not follow deformation and do not measure clearance between entire surfaces.
Lines whose endpoints are behind the camera are omitted from the overlay; their values
remain in the panel. Saved projects and inspection exports retain the ruler evidence.

Enter a name under **Named cameras** and choose **Save** to bookmark the exact camera and projection.
**Go** restores it; edit its name or delete it using the adjacent controls. Bookmarks
belong to the current workspace and persist with the project. Restoring one during an
active transform preserves that edit and rebases its pointer movement. The existing
axis-view/4 restoration workflow remains available. Rulers and bookmarks do not add
an anatomical undo step or trigger geometry calculation.

## Sharing an inspection report

Choose **File → Export inspection report…**. The current document, workspace, camera,
selection, edit-mode presentation and accepted geometry are frozen when export starts.
Continue editing while the background job writes a single **`.afinspection.zip`**.
The footer offers **Report folder**; Activity reports progress, cancellation or errors.
An export failure preserves an existing destination file; choose Export again to retry.
Only one inspection export runs at once. It does not block document commitment/saving.

The archive contains `inspection.json` (schema version 1) and `image.png`. JSON includes
document/revision, provisional-edit flag, explicit view/camera, full-document relationship
and attachment data, authored/result revisions and pending inputs, geometry counts/bounds,
and issue evidence with its completeness/freshness. Geometry payloads and the editable
project are not included. Names, IDs, transforms and diagnostic errors are included;
review the report as project information before sharing it. An inspection report is
not a project backup or skin export.

An isolated GPU renderer reads a temporary package of that frozen revision. The report
verifies the revision plus camera, projection and selection observed by the renderer.
It does not recalculate pending geometry or silently frame a different object. The
fixed image size is 1280×960; its aspect may differ from your live viewport. It uses
the standard grid/material view, rather than capturing transient hover or X-ray state.
Temporary geometry files are removed when the job finishes, fails or is cancelled.
The last accepted surfaces can legitimately be stale or failed; JSON preserves that
status instead of presenting the image as a fresh geometry validation.

For an exact saved revision without opening a visible application window:

```powershell
AnthroForge.exe --cli report model.anthroforge review.afinspection.zip --revision 42 --selected <object-id> --workspace 1
```

The CLI rejects a mismatched revision and uses that workspace's saved camera. Omit
`--selected` for no selection or `--workspace` for the whole document. For an in-memory
headless session, use `inspection.export` with `path`, optional `selected`, `editing`,
and `wait=true`. It freezes current accepted results without waiting for other geometry
calculations. `wait` waits for this report job. Use `inspect.target`/`inspect.snapshot`
for JSON-only inspection; these require no Qt or GPU. Image export runs the Qt renderer
in a child process, so the calling headless core itself remains Qt-free. Missing desktop
dependencies or unavailable GPU rendering are explicit export errors.
