# UI polish — 0.1.9

## Scope and acceptance

Fix unreadable menu hover states, uneven padding and excessive always-visible text.
Use shared Qt Quick styling and concise primary controls with accessible details.
Preserve editing, keyboard, inspection, issue, workspace and profiling behavior.
Inspect actual desktop and packaged results at normal and compact window sizes;
run the development gate and relevant GUI regressions before integration.

## Recovery

- Writer: current desktop chat; direct work, no delegated writers.
- Branch: `codex/ui-polish-019`; integration: `main`.
- Starting revision: `ca4e4e24ec9344f44fa9abe2d2dd53acc6f5beb1`.
- Preserve unrelated untracked root `__init__.py`.
- Status: implementation complete; 541-test development gate passed. Off-screen Qt
  UI polish, ruler/camera, workflow, Issues, Activity and view/gesture acceptance passed.
  Real Close/Cancel/OK buttons, deletion and undo also pass off-screen.
  Packaging and final qualification pending.
- User is playing a game: no visible windows, desktop screenshots or mouse/keyboard
  automation. Our launched 0.1.8 window is closed. Continue only background checks.
  Off-screen Qt needs QT_QPA_FONTDIR=C:/Windows/Fonts for meaningful text/layout.

## Findings and ownership

- Qt Basic MenuItem uses palette.light/midlight for highlight/press, but Main
  overrides only some palette roles. Light system backgrounds conflict with our
  light text. Shared palette/menu components own contrast and menu alignment.
- Combo delegates use the entire control width inside an inset popup, overrunning
  the popup's padded content area. Shared controls own sizing and focus states.
- Inspection coordinates, issue evidence and workspace instructions are always
  expanded. Detail disclosures should preserve access without dominating controls.
- Existing lazy relationship inspection and incremental Activity models must remain.

- Packaging found a reproducible PySide deploy boundary: the larger QML argument list
  triggers its Windows deploy_main.py wrapper and changes Nuitka output names. Explicit
  executable/distribution names now preserve the packaging contract; rebuild pending.

## Next

Package from a clean checkpoint and run tools/check_portable.py with --offscreen.
Inspect saved images without interacting with the desktop. Preserve the native-window
validation distinction in the final report. Existing UI test had a stale key 7 expectation (current key 3);
ruler test now waits for displayed picking revisions instead of assuming a 50ms frame.

## References

- [Qt customization](https://doc.qt.io/qt-6/qtquickcontrols-customize.html)
- [MenuItem alignment](https://doc.qt.io/qt-6/qml-qtquick-controls-menuitem.html)
- [Engineering guidelines](../engineering_guidelines.md)
