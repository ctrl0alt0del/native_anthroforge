# Development guide

Apply the [engineering guidelines](engineering_guidelines.md) and [agent rules](../AGENTS.md)
when implementing, fixing or reviewing behavior. They define architectural diagnosis,
practical SOLID criteria, pattern selection and proportionate validation.

## Setup and daily use

Requirements: PowerShell, uv, Visual Studio C++/Windows SDK tools and LLVM/clang-cl.
The setup discovers the C++ and LLVM installations independently.

```powershell
./tools/setup.ps1
./tools/check.ps1
./tools/run.ps1
```

Setup installs CPython 3.12.12, the locked desktop/numerical development environment,
the matching Qt 6.12.0 MSVC x64 SDK, and builds native targets. Local Python/Qt SDKs live
under .tools; the virtual environment is .venv. The addon is not a runtime dependency.

The Qt installer has an explicit repository-layout adapter for aqtinstall 3.3.0 and the
Qt 6.12 compiler-specific archive location. It retains aqt checksum verification.
[Qt repository](https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/qt6_6120/),
[aqt docs](https://aqtinstall.readthedocs.io/en/stable/getting_started.html).

| Command | Purpose |
| --- | --- |
| ./tools/build-native.ps1 | Native rebuild and CTest |
| ./tools/check.ps1 | Lock, Ruff, configured mypy, native/style checks, pytest, numerical imports, doctor |
| uv run --no-sync python -m anthroforge run examples/assembly.json | Create and save the example assembly |
| uv run --no-sync python tools/gui_acceptance.py assembly.anthroforge | Real QQuickWindow drag/undo and save/reopen |
| uv run --no-sync python tools/scheduling_acceptance.py assembly.anthroforge | Parent/child coherence during real viewport drags, timing and captures |
| uv run --no-sync python tools/ui_acceptance.py assembly.anthroforge | Text-safe shortcuts, numeric edit/undo, search, sections, resizing and empty-state captures |
| uv run --no-sync python tools/primitive_acceptance.py | Loft/cage/Hook editing, save/reopen and actual GUI captures |
| uv run --no-sync python tools/primitive_acceptance.py --interaction | Curve/component picking, inspector selection, topology policies and imported/base Hook editing |
| uv run --no-sync python tools/primitive_acceptance.py --performance | 133,116-triangle publication, 1,000 cage points, rapid edits, cancellation, frame/picking measurements |
| uv run --no-sync python -m anthroforge run examples/primitives.json | Complete headless primitive/deformer workshop |
| ./tools/smoke-desktop.ps1 | Bounded desktop startup and capture |
| ./tools/build-package.ps1 | Development wheel/source package |
| ./tools/package.ps1 | Portable Windows executable and dependencies |
| uv run --no-sync python tools/source_archive.py | Companion source archive |
| uv run --no-sync python tools/check_portable.py PATH_TO_EXE build/portable-check | Minimal-environment runtime acceptance |

For release tooling, install the packaging group without removing desktop/numerical extras:
`uv sync --locked --all-extras --group qt-sdk --group packaging`.
The deployment uses pyside6-deploy and Nuitka 4.1.1, explicitly selects its supported
downloaded MinGW compiler, and keeps the full standalone directory. A short Nuitka cache
path avoids Windows compiler header path limits. Downloads occur only during build.
Neither packaging command publishes anything.

AF_QT_SDK can point to an existing matching SDK for native build/deployment.
UV_PROJECT_ENVIRONMENT and PYTHONPATH can select an existing environment and another source
checkout. ANTHROFORGE_NATIVE_LIBRARY overrides the numerical native library path.
The packaged app resolves its native libraries beside its own code.

## Reproducible qualification

The normal test suite contains the captured Blender reference matrices, so Blender is
not required to run it. To regenerate them explicitly:

```powershell
blender --background --factory-startup --python tools/capture_addon_parity.py -- ADDON_PATH build/addon-parity.json
uv run --no-sync python tools/check_addon_parity.py build/addon-parity.json
```

The reference script creates a temporary in-memory scene and never saves a .blend.
tools/viewport_benchmark.py accepts an anatomical STL path and creates 32 independent
instances for navigation/picking measurements. Large user assets remain outside source.

All authored functions stay within 15 physical lines. Unchanged third-party headers and
the preserved addon kernel retain upstream formatting. Shared core/application/native
Python code cannot import Blender or Qt. Numerical geometry and optimization loops belong
in C++, with owned batched inputs/results across the boundary.

CMake portable-core builds the numerical engine without the Qt viewport bridge. The shared
`tools/check_core.py` gate runs the complete pytest suite, including Qt input tests, native
contracts, a headless workshop/save/reopen and wheel checks. CI invokes the same gate on
Windows and the [cloud setup](cloud_development.md) on Ubuntu 24.04. Consult the recorded
validation for observed results; a core pass does not certify the graphical desktop or macOS.
The old root __init__.py is an unrelated Blender stub; preserve it and use the src package
and configured test paths.

The optional addon-check CMake preset still accepts AF_ADDON_SOURCE for the original
smoothing kernel qualification. It reads source in place and writes only build outputs.
Future migrations should add equivalent parity evidence instead of treating the entire
addon as already portable.

Development numerics extras remain installed for future work. They are excluded from
the 0.1.7 portable runtime because 0.1.7 does not use them. In particular pytetwild[all]
supplies its required PyVista accessor dependency while Qt remains the application renderer.

Primitive parity fixtures under tests/fixtures/primitives pin Blender 5.0.1 outputs.
Generators are capture_primitive_parity.py, capture_deformer_edges.py,
capture_solidify_edges.py, capture_curve_parity.py and capture_anatomy_primitives.py.
Read their CLI entrypoints before regeneration; anatomical capture needs the explicit
source path and output JSON path. Use `--disable-autoexec` with background Blender.
Never save either original .blend file. Native source provenance is recorded in
[BLENDER_PRIMITIVES.md](../native/migration/BLENDER_PRIMITIVES.md).

The companion archive is `dist/AnthroForge-0.1.7-source.zip`. The portable folder stays
`dist/AnthroForge.dist` and the executable's product/file version identifies 0.1.7.
Packaging includes all new QML inspectors, native algorithms, example batches and notices.
Set `AF_PACKAGE_OUTPUT` to an absolute output directory before `tools/package.ps1`
when an existing portable app is running. For example, `E:/development/anthroforge/dist/0.1.7`
produces `AnthroForge.dist` there without changing the running distribution.
`uv run --no-sync python tools/primitive_acceptance.py --workshop` runs the complete
primitives batch, opens its result in the desktop and captures the loft and curved body.


`tools/usability_acceptance.py` exercises 0.1.3 gizmos with actual mouse events,
text-safe shortcuts, modal blocking, deletion and edit opacity. Run it with `--render`
for paired orbit measurements with/without the outline and a large staged geometry
replacement, including mask resource disposal on deletion/undo. It currently uses the
assembly fixture at `build/coordinator-portable/assembly.anthroforge`, generated by
`tools/check_portable.py`. Outputs go to ignored `build/usability-review`.
The outline fragment shader is built by Qt Shader Tools through `qt_add_shaders` and
embedded in `af_viewport.dll`; no runtime shader compiler is required by the portable app.

`uv run python tools/curve_interaction_acceptance.py` exercises held-key insertion, repeated
confirmation, direct and gizmo surface snapping, target switching, modifier release,
rebound input bindings, focus loss and undo with real mouse events in both projections.
Captures and query timings are written under `build/curve-interaction-review`.

`uv run python tools/view_gesture_acceptance.py` checks centered axis views, zoom preservation,
view changes/restoration during direct/gizmo/modal transforms, one-step undo and cancellation, and signed
surface offsets with real wheel/middle-button events. Outputs go to `build/view-gesture-review`.

`uv run python tools/camera_restore_acceptance.py` checks original-camera restoration across
axis keys/buttons, projection and zoom changes, the menu action, text focus, rebinding,
workspace changes and camera persistence. Outputs go to `build/camera-restore-review`.

Runtime profiler qualification uses `tools/profiler_acceptance.py` (F12 in four drag
variants) and `tools/profiler_qualification.py --mode none|dormant|record --output ...`.
Run overhead trials serially, with counterbalanced modes and no simultaneous builds.
`tools/check_portable.py` checks both packaged headless reports and runtime Qt reports.
See [profiling](profiling.md) for report interpretation and ownership/storage limits.

Activity 0.1.5 acceptance uses `tools/activity_acceptance.py` for real Cancel/Retry,
failure/target updates, hidden progress and New-document handling. Model unit tests use
Qt's QAbstractItemModelTester and persistent indexes, including retention and role-only
updates. `tools/profiler_qualification.py` accepts `--activity-open` and
`--interaction drag|modal`; each trial verifies snapping and undo.

For a source/runtime snapshot of the baseline, run `tools/activity_comparison.py
--baseline <snapshot>/src --output build/activity-015/comparison`. The snapshot needs
the baseline `anthroforge` package and its native `_runtime/bin` and `_runtime/qml`.
The driver runs serial ABBA nonrecording trials and separate recorded comparisons,
with Activity open/closed and direct/modal movement. It uses a nonactivating window
to avoid focus interruptions and records system utilization; do not mix these absolute
timings with ordinary foreground captures or run concurrent builds during measurements.
Summarize the saved results with `tools/activity_evidence.py <comparison-directory>
<output.json> [--confirmation <final-run-directory>]`. It preserves per-run variance
and capture completeness/retention,
separates Activity notifications from other models, and does not sum nested durations.
