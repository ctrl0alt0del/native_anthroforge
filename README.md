# AnthroForge 0.1

A standalone imported-SCP assembly editor for Windows, built with a shared Python
application core, C++ geometry and attachment kernels, and a Qt Quick 3D desktop.

Open **dist/AnthroForge.dist/AnthroForge.exe** to use the portable build.
Start with [the walkthrough](docs/quickstart.md) and the included
[cube fixture](examples/primitives/cube.obj). Keep the entire distribution folder
together. The executable supports desktop use and a numerical headless JSON API.

0.1 includes OBJ/STL/PLY import with explicit units, SCP hierarchy and transforms,
attachments and anchor controls, transactions/undo, background calculation scheduling,
portable project files, focused workspaces, precise picking and diagnostics.
Curve primitives belong to 0.1.1. Skin construction and export are later milestones.

## Development

```powershell
cd E:\development\anthroforge
./tools/setup.ps1
./tools/check.ps1
./tools/run.ps1
```

See [development commands](docs/development.md), [implementation contract](docs/implementation_01.md),
[observed validation](docs/development_status.md), and [architecture](docs/architecture.md).
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
The original Blender addon is a migration reference and is not required to run 0.1.
The unrelated pre-existing root __init__.py is preserved outside the standalone package.
