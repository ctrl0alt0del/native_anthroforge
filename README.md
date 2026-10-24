# AnthroForge 0.3.1

Shortcut inspection adds affected-output navigation, captured formula evidence, effective
attachment policies and propagation status, with optional viewport effects. See the
[0.3.1 walkthrough](docs/shortcuts_031.md). Numerical geometry, attachments and schema 5
remain unchanged.

0.3 adds numerical-property shortcuts, typed driving formulas, attachment-edit policies
and general XYZ Parametric curves. See the [walkthrough](docs/shortcuts_030.md),
[specification](docs/specification_030.md) and [qualification](docs/research/shortcuts_030/windows_review.md).
Projects save in schema 5; existing 0.2.4/schema-4 projects remain readable with their
accepted geometry and attachments preserved. Blender shortcut migration is separate.

The current Windows gate passes 1,996 tests and all five native tests.
The packaged executable passes the full minimal-PATH portable suite and the
generated-point resolution-lock check. The subsequent one-file skeleton migration adds
retained Bézier construction and an explicit attachment-policy scope for multi-SCP controls.
See [delivery evidence and limits](docs/development_status.md#shortcuts-and-parametric-curves-030).

Shared priority propagation now keeps dependent pose updates responsive during broad
shortcut edits. The Ribs Top Radius/Ulna case is qualified with unchanged geometry and
attachments; see [timings and validation](docs/tasks/task-priority-propagation.md).

0.2.4 improves tissue editing and evaluation performance: prepared inspection UI,
incremental collision checks, retained stacking preparation, a smaller height-smoothing
QP, and reusable native tissue frames/operators. Geometry, attachments and schema 4
remain unchanged. See [measurements and validation](docs/performance_024.md).

**Edit → Preferences… → ROUTED solver** selects Custom (default) or sparse PIQP for
curves and Fibers. The choice saves automatically across projects and launches. It
applies to future calculations; current results and running jobs stay unchanged.
Use Recalculate when you want existing routes updated. See the
[0.2.3 contract](docs/specification_023.md) and [API](docs/authoring_api.md#application-preferences-023).

[0.2.2 unified tissues](docs/specification_022.md) adds attached Point/Anchor and Membrane
construction, muscle/soft-tissue inflation, relaxation, constraints, cropping and stacking.
Start with the [tissue walkthrough](docs/tissues_022.md) or [headless example](examples/tissues.json).
**Create Tissue** is on the main toolbar and Create menu. Select a Point, Curve or Surface
(including Anchor, Fiber or Membrane) to create directly. Generic construction obtains
independent attached copies automatically; source objects remain unchanged. **Create Fiber** is
available from an ordinary curve's inspector and binds to nearest SCP surfaces by default.
See [validation and limitations](docs/development_status.md#unified-tissues-022).

Tissue self-intersections are intentionally permitted without changing inflation or
height smoothing. This policy may be revisited for demonstrated downstream defects;
see [the intersection contract](docs/specification_022.md#release-contract) and
[downstream integration status](docs/tasks/tissue-intersection-policy.md).

Standalone curves, reference images, fibers and curve-based surfaces follow the
[confirmed specification](docs/specification_020.md) and
[implementation plan](docs/implementation_020.md). See the
[release validation](docs/development_status.md#curve-workflows-021) for source,
native parity, profiling, offscreen interaction and relocated portable evidence.

A standalone anatomical construction editor for Windows, built with a shared Python
application core, C++ geometry and attachment kernels, and a Qt Quick 3D desktop.

Open **AnthroForge.exe** in the complete portable folder `dist/0.3.1/AnthroForge.dist`.
Builds use `dist/<version>/AnthroForge.dist`, replacing the previous build of the same version.
Do not add feature/task suffixes. Running installations remain intact until closed.
Start with [the walkthrough](docs/quickstart.md) and the included
[cube fixture](examples/primitives/cube.obj). Keep the entire distribution folder
together. The executable supports desktop use and a numerical headless JSON API.

Start construction with [the curves/fibers/images walkthrough](docs/construction_020.md)
or [the shared API example](examples/construction.json). Curves use Bézier, exact polyline
or native routing engines. Fibers add anatomical bindings and use the same curve/surface
tools. Reference images are embedded, and explicit junctions support branched open lofts.
Schema 4 rejects earlier formats, including 0.2.1 projects; legacy conversion is deferred.
[0.2.1 curve workflows](docs/specification_021.md) remain available. Tissues use shared
Anchor/Fiber/Membrane construction and retain all editable parameters. Anatomical labels
choose creation defaults, not different evaluators. General physical contact and dynamics
are outside this release. Failed calculations retain usable accepted geometry with Issues.

Curve creation and cursor/patch tools sit below the transform gizmos. Place Points finishes
on plain left-click from the second point; Shift-click continues. Hold Ctrl to snap to
SCP surfaces; Ctrl+Shift snaps and continues. New routed curves use
automatic obstacles. Select **Path engine** directly in the inspector: one undoable change,
preserving existing authored points, with no preview/accept steps. Obstacle exclusions use
bounded searchable lists. Numerical budgets live under Advanced.
The Patch / Surface icon creates a patch from one closed curve, or a standalone loft
from two or more selected curves/fibers. Ctrl-click in Construction to select sources.
Right-click **Place Points → Place Branched Points** to start a curve at an existing control
point with a shared junction. **Surface** detects selected branch groups automatically,
asking only when the grouping is ambiguous. See the [construction walkthrough](docs/construction_020.md)
and [headless branch example](examples/branched_curves.json).
Anatomy and Construction have separate full-height tabs. Import world reference images
with the image icon beside the projection control; use Add reference image in Properties
for an image parented to the selected object. Orthographic axis views set initial alignment.

0.1.9 refined the editor with consistent dark menus, aligned controls and expandable
inspection details. See [UI polish](docs/ui_polish.md).

0.1.8 added [two-point surface rulers with XYZ readouts and named camera bookmarks](docs/workflow_inspection.md#measurements-and-named-views-018).
Rulers and views persist per workspace and are included in inspection reports.
[Profiler reports](docs/profiling.md#recalculation-cache-and-memory-evidence-018) now explain
invalidation, base-cache reuse and native geometry retention by overlapping owners.
Relationship inspection, workspace management, display units and shareable reports
remain available. The Issues panel distinguishes cycle
participants from downstream blocked outputs. Existing checks, dismissal, navigation
and verified repairs remain available; diagnostics never change anatomy or block saving.

Activity updates incrementally: job rows retain their identity, changed fields
update without rebuilding the list, and the header uses separate status summaries.
Cancel/Retry, errors, target names, diagnostics and the latest 40 jobs remain available.

Bug/recommendation reporting: **Help → Report a bug / recommendation** or **F12** captures
the window and opens a screenshot editor with red rectangles, arrows and text. Add a
description and submit to the version-independent local `AnthroForge/Reports` inbox.
The [report format and replaceable destination](docs/feedback_reports.md) are independent
of project files. No network submission is enabled.
Use **Help → View reports…** to preview existing reports, edit their description text,
or delete a report after confirmation.

Runtime performance recording: press **Shift+F12**, reproduce a slowdown, then
press Shift+F12 again and share the `.afprofile.zip` under your local AnthroForge `Profiles`
folder. Recording works during edits; no restart or rebuild is needed. See
[recording and interpreting reports](docs/profiling.md).

The editor includes distinct move/rotate/scale gizmos, selection outlines, translucent curve editing,
and keyboard/tree deletion that preserves children. Hold Shift to preview curve-point insertion
and click repeatedly; hold Ctrl during a point drag to snap to other SCP surfaces. Curves,
points and handles have distinct colors. G/R/S starts mouse transforms; 1/2/3 centers X/Y/Z
views without ending an edit; 4 restores the original camera, including zoom and projection.
While snapping, the wheel adjusts surface offset and middle-click
or Ctrl release resets it. Snapping stays outside the hit face; scrolling inward stops
at a small numerical safety margin. Numeric fields accept decimal points or commas:
click to type, or drag horizontally for live adjustment with one undo action; Escape
cancels a drag. Integer settings retain whole-number input.
It includes editable Bézier lofts and curve-deformed box/cylinder/capsule bodies,
shared Hooks and lattice cages, Simple Solidify thickness, and OBJ/STL/PLY imports.
It retains explicit units, SCP hierarchy and transforms,
attachments and anchor controls, transactions/undo, background calculation scheduling,
portable project files, focused workspaces, precise picking and diagnostics.
The [primitive specification](docs/primitives_012.md) defines the implemented scope.
Try **Create Primitive**, then **Edit Primitive**, or run the shared authoring example
[examples/primitives.json](examples/primitives.json). Skin construction and export are
later milestones. Editable anatomy is preserved permanently; Apply/Bake is unavailable.

## Development

```powershell
cd E:\development\anthroforge
./tools/setup.ps1
./tools/check.ps1
./tools/run.ps1
```

For Codex Cloud or Ubuntu development, run `bash tools/cloud/setup.sh`.
See [cloud development and phone workflow](docs/cloud_development.md) for environment
creation, dependency refresh, verification and the Windows GUI/release boundary.
Use [work continuity](docs/work_continuity.md) for task branches, frequent pushed
checkpoints and resuming the same work after a power outage.

See [development commands](docs/development.md), [implementation contract](docs/implementation_01.md),
[observed validation](docs/development_status.md), and [architecture](docs/architecture.md).
Follow the [engineering guidelines](docs/engineering_guidelines.md) for fixes, features and design review.
The [computation inventory and history](docs/computation_history.md) lists implemented
calculations, their owners/tests, and why computational approaches changed.
The [research reading list](docs/research_sources.md) bookmarks Pixar's research library
and distinguishes candidate methods from qualified application algorithms.
The [confirmed specification](standalone_application_recommendations.md) remains authoritative;
the [stack analysis](standalone_technology_stack_analysis.md) records the technology decisions.

| Directory | Responsibility |
| --- | --- |
| src/anthroforge/core | Immutable documents, entities and job contracts |
| src/anthroforge/application | Operations, scheduler, history and project storage |
| src/anthroforge/native | Owned C ABI bindings; no Blender or Qt dependency |
| src/anthroforge/desktop | Qt/QML presentation, interaction and GPU publication |
| native | C++ mesh import/query, migrated attachment kernel and Qt geometry bridge |
| tests | Behavioral, native, Blender-reference and architecture checks |
| tools | Setup, builds, deployment and desktop acceptance tools |

Application source is GPL-3.0-or-later. Third-party code retains its own licenses;
see [notices](licenses/THIRD_PARTY.md) and [native provenance](native/vendor/PROVENANCE.md).
The original Blender addon is a migration reference and is not required at runtime.
The unrelated pre-existing root __init__.py is preserved outside the standalone package.
