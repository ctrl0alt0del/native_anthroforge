# AnthroForge 0.1.7

A standalone SCP and primitive editor for Windows, built with a shared Python
application core, C++ geometry and attachment kernels, and a Qt Quick 3D desktop.

Open **AnthroForge.exe** in the portable folder (`dist/AnthroForge.dist` in the project).
Start with [the walkthrough](docs/quickstart.md) and the included
[cube fixture](examples/primitives/cube.obj). Keep the entire distribution folder
together. The executable supports desktop use and a numerical headless JSON API.

0.1.7 adds [relationship inspection, workspace management, display units and shareable
inspection reports](docs/workflow_inspection.md). The Issues panel distinguishes cycle
participants from downstream blocked outputs. Existing checks, dismissal, navigation
and verified repairs remain available; diagnostics never change anatomy or block saving.

Activity updates incrementally: job rows retain their identity, changed fields
update without rebuilding the list, and the header uses separate status summaries.
Cancel/Retry, errors, target names, diagnostics and the latest 40 jobs remain available.

Runtime performance recording: press **F12**, reproduce a slowdown, then
press F12 again and share the `.afprofile.zip` under your local AnthroForge `Profiles`
folder. Recording works during edits; no restart or rebuild is needed. See
[recording and interpreting reports](docs/profiling.md).

The editor includes distinct move/rotate/scale gizmos, selection outlines, translucent curve editing,
and keyboard/tree deletion that preserves children. Hold Shift to preview curve-point insertion
and click repeatedly; hold Ctrl during a point drag to snap to other SCP surfaces. Curves,
points and handles have distinct colors. G/R/S starts mouse transforms; 1/2/3 centers X/Y/Z
views without ending an edit; 4 restores the original camera, including zoom and projection.
While snapping, the wheel adjusts surface offset and middle-click
or Ctrl release resets it. It includes editable Bézier lofts and curve-deformed box/cylinder/capsule bodies,
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
