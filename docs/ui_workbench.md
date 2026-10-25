# AnthroForge workbench

The 0.3.7 workbench reorganizes existing tools. Geometry, attachments, formulas,
calculation scheduling and project schema remain unchanged.

## Where to find things

| Work | Location |
| --- | --- |
| New/open/save, recent projects, recovery, import and inspection export | File menu and existing shortcuts |
| Undo, redo, delete and Preferences | Edit menu and existing shortcuts |
| Primitives, curves, points, fibers, surfaces, tissues and images | Create menu; common tools also on the viewport rail |
| Workspace selection, focus and management | Above the viewport |
| Projection, framing and overlays | Above the viewport; axis views, restoration and X-ray remain inside it |
| Object shaping | **Shape**, the default context-editor page |
| Exposed properties and drivers | **Shortcuts**, retaining Selected SCP/VCP and All |
| Dependencies, tissue stages, geometry findings and point explanations | **Inspect** |
| Calculation progress and failures | Activity and Issues in the bottom strip |
| Attachment enablement, update mode and Recalculate | Bottom strip |
| Last operation details | Details in the bottom strip |
| Object count, document revision and display units | Hover Saved/Unsaved in the bottom strip |
| Profiler, reports and keyboard help | Existing View/Help actions; recording indicator in the menu strip |

Both navigation views offer search. Anatomy row actions appear on hover or selection,
leaving more room for inactive object names. Clipped names expose their full text on hover.

The inspector remembers the page for each object category. Pane widths, Focus editor
and named disclosure sections persist locally, beside the preferences file in
`workbench.ini`. They do not change the project or create Undo entries. **View → Focus
editor** hides document navigation without changing the anatomical workspace.

## Context editors

Tissues start with inflation and principal dimensions. Boundary/taper, control-point
position and preview editing have their own disclosures. Existing smoothing, cropping,
relaxation, fields, constraints and stacking remain in Shape. **Source & settings**
contains naming, classification, presets, source replacement, source editing and
independence. Preview/cancel remains available; it is not a prerequisite for direct edits.

Curves start with their engine and editing controls. Fiber supports, pin workflows and
display radius remain available under **Fiber supports**. Source use, conversion and
creation actions follow the primary editor. Ordinary construction transforms and
parenting are grouped under **Transform & relationships**. Fibers retain their transform
restriction. Hook/lattice transforms and following have a separate disclosure.

SCPs start with primitive controls. Transform, Attachment, display/evaluation, duplication,
deletion, deformers, replacement, splitting and mirroring retain their existing operations.
Mirrors are read-only and offer **Select source** on every context page. Images retain
assignment, dimensions, presentation, calibration and parenting controls. Surfaces retain
source order, correspondence, branches, sampling and Realign. No controls are invented for
unsupported combinations.

Menu and selector text uses readable names; persisted codes and command arguments stay
unchanged. Dynamic calculation messages use the reserved status area or existing toasts,
not rows inserted between numerical fields. Editors remain instantiated across page
changes so those changes do not discard active drafts.

Inspect bounds long related-object lists to eight visible rows with scrolling and
search. Filtering keeps the search field and list height stable. Delegates are reused;
the application does not create a control for every related object at once.

## Retention and qualification

| Retained workflow | Qualification performed |
| --- | --- |
| Numerical entry/drag, cancellation and one-action Undo | Real Qt events, decimal/comma locales, integer and vector fields |
| Curve editing and tissue previews across pages | Workbench acceptance asserts edit/draft retention and unchanged document identity |
| Inspector values and modes | Raw command IDs tested separately from displayed labels |
| Tissue stages, geometry findings and dependency inspection | Existing collectors and operations through the Inspect page |
| Support/pin, replacement, retarget and mirror workflows | Existing portable authoring suite and shared capability checks |
| Recovery, Preferences and reports | Existing background interaction and portable suites |
| Visibility, focus and panel dimensions | Two window sizes, 150% scale and text audits |
| UI workload | Serial before/after Qt profiler recordings on the migrated assembly |

Final validation results and physical-interaction limits are recorded in the
[task evidence](tasks/ui-workbench.md). The [reviewed design](ui_overhaul_design.md)
remains the rationale; its HTML concept is illustrative, not the runtime application.
