# Three user feedback reports

- Task branch: `codex/three-feedback-reports`
- Integration branch: `main`
- Starting revision: `35cbccd`
- Status: in progress
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

Read metadata and annotated screenshots for all three reports; implementation inspection underway. No fixes yet. Unrelated root `__init__.py` is preserved.

## Verification

Pending. All validation remains background-only; no visible windows or desktop input. Deliver one `dist/0.2.1/AnthroForge.dist` and `dist/AnthroForge-0.2.1-source.zip`. Recheck running processes before replacing the canonical build.

## Next actions and blockers

1. Implement native temporary projection and shared image import intent; integrate tabs and actions.
2. Verify regressions and interaction, run gate, build and qualify the portable package.
3. Update current docs, merge and push validated work.

## Recovery inputs

Reports: `%LOCALAPPDATA%/AnthroForge/Reports/<id>.afreport.zip`.
Ignored inspected copies: `build/report-triage/<id>/`.
Standard Windows setup and tooling apply. No blocker currently identified.
