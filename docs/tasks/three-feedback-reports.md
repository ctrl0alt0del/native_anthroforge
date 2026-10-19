# Three user feedback reports

- Task branch: `codex/three-feedback-reports`
- Integration branch: `main`
- Starting revision: `35cbccd`
- Status: complete
- Last updated: 2026-10-19, Europe/Bucharest

## Outcome and acceptance

Resolve the three reports in the user's local AnthroForge Reports folder:

- `2e8e597083234d2981aeb073f6d3daba`: remove the redundant top-toolbar Import Mesh button; retain existing import entry points.
- `58aa689abd4d44a497df365f7cb29164`: full-height Anatomy/Construction tabs, world image import beside the viewport projection control, and object-parented import in Properties. Initialize image alignment from an orthographic axis view.
- `6bd8fa39332240a39b9293c93841a071`: temporary surface snapping during Place Points through the keyboard manager; Ctrl and Shift continuation must compose.

The actual report archives remain unchanged. Acceptance includes shared image creation/parenting, native projection, undo, modifier transitions, actual offscreen QML interaction and visual inspection, the development gate, and the canonical portable build.

## Decisions and relevant files

Use existing drawing projection, ordinary parenting, creation jobs, keyboard bindings and Ui/Theme controls. Preserve source curves and user document data. Capture import intent before opening the file picker. Keep numerical projection and transforms native.

Primary boundaries: `desktop/qml/Main.qml`, Construction/Inspector/DrawingOverlay, `desktop/image_tools.py`, `desktop/drawing_tools.py`, native stroke projection and shared image operations.

Qt references: [TabBar](https://doc.qt.io/qt-6/qml-qtquick-controls-tabbar.html), [StackLayout](https://doc.qt.io/qt-6/qml-qtquick-layouts-stacklayout.html), [MouseArea](https://doc.qt.io/qt-6/qml-qtquick-mousearea.html).

## Current state

Implemented tabs and image actions, captured import intent, shared world-axis image placement, and temporary native surface projection through the keyboard manager. Native/projection/image tests and actual QML acceptance pass. Unrelated root `__init__.py` is preserved.

## Verification

Native build and 3 CTests pass. 47 focused tests cover transforms, nearest hits, fallback, offsets, unchanged projection policy, image import/undo and captured parent intent. `uv run --no-sync python tools/feedback_fixes_acceptance.py` passes actual modifier transitions, remapped snapping, Ctrl+Shift continuation, one-step undo/cancel, image picker/parent/alignment and tab actions. Captures at 1440x900 and 1050x680 in `build/three-reports-acceptance` were inspected. QPA offscreen captures validate controls/layout, not Quick3D mesh pixels.

The file-picker harness must target Qt's separate offscreen popup window and click its file delegate; setting the public selectedFile property alone does not select an entry in an open dialog. UI projection tolerance is 1e-6 (observed float error 2.4e-8); native tests retain tighter tolerances.

Code `9850849`: `./tools/check.ps1` passes (941 tests, 307 existing-constructor deprecation warnings, 3 native CTests, native analysis, Ruff, mypy on 195 modules, function limits, numerics/doctor). Log: `build/three-reports-gate.log`.

Additional passing background commands:

- `uv run --no-sync python tools/image_scene_acceptance.py`
- `uv run --no-sync python tools/curve_workflow_acceptance.py`
- `uv run --no-sync python tools/construction_editor_acceptance.py`
- Local fixture `uv run --no-sync python build/three_reports_render.py`: actual GPU pixels for X/Y/Z image import under a rotated, nonuniformly scaled parent. Captures `build/three-reports-acceptance/parented-image-*.png` inspected.

Ownership review completed: no Python numerical loop, no new scheduling/publication path, shared image transform policy, captured input intent, native temporary projection, and presentation-only tab selection.

`./tools/package.ps1` passed at clean build revision `37111d632410f9960a0bebbc4cf219cad2390530`.
The canonical executable SHA256 is `d3266e5627387d34502defc41fddfb771655f773ea9bddc142fa0b3632a2f6d9`.
`uv run --no-sync python tools/check_portable.py <temporary-copy>/AnthroForge.exe build/three-reports-portable --offscreen` passed the full portable suite with minimal PATH, including hidden GPU rendering, profiling and QA-only report preview/edit/delete. Evidence: `build/three-reports-portable/portable-check.json` and `feedback-probe.json`; temporary location is in `build/three-reports-portable-location.txt`.

An additional packaged headless scenario imports X/Y/Z-aligned images under a rotated/scaled parent and checks saved relationships and distinct transforms. Inputs and result: `build/three-reports-image-api/commands.json` and `result.json`.

All validation remains background-only; no visible windows or desktop input. Deliver one `dist/0.2.1/AnthroForge.dist` and `dist/AnthroForge-0.2.1-source.zip`. Recheck running processes before replacing the canonical build.

## Next actions and blockers

Merged into `main` as `ee64f1a` and pushed. The packaged documentation is refreshed;
the canonical source archive accompanies the existing version's replacement build.
No outstanding implementation work or known blocker. Actual hands-on Windows interaction
remains user acceptance, as required by the background-only validation constraint.

## Recovery inputs

Reports: `%LOCALAPPDATA%/AnthroForge/Reports/<id>.afreport.zip`.
Ignored inspected copies: `build/report-triage/<id>/`.
Standard Windows setup and tooling apply. No blocker currently identified.
