# Tabs and compact icon alignment

- Task branch: `codex/tab-and-icon-alignment`
- Integration branch: `main`
- Starting revision: `ff3901cd4f64c08544708556c7481e1994210fbb`
- Status: pending release validation
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local Codex chat

## Outcome and acceptance

Resolve both new local feedback reports without changing document behavior:
`22301967f3f5478595777eb751c93263` requests actual Anatomy/Construction tabs;
`2f4815be5165470680437e032b2c0966` highlights misaligned delete and help icons.
Keep the user's reports intact. Deliver into the single canonical 0.2.1 distribution.

## Decisions and relevant files

Use Qt's TabBar/TabButton semantics with themed presentation in ObjectBrowser.
Keep full-height panes, selection-driven navigation and retained pane state.
UiButton owns adaptive padding and centered content groups. Baseline measurement:
a 23x24 delete control gave its 16x16 icon only 7x12 pixels of content space; its
center was displaced 4.5px horizontally and 2px vertically. Help text was 2px low.
Padding now yields to content, and the icon/label group centers in available space.
Explicit left padding/alignment on section headers remains supported.

Official references: [Control layout](https://doc.qt.io/qt-6/qml-qtquick-controls-control.html#control-layout)
and [TabBar](https://doc.qt.io/qt-6/qml-qtquick-controls-tabbar.html).

## Current state

Both fixes implemented in UiButton, UiTabBar, UiTabButton and ObjectBrowser.
Native tab semantics replace manually checked ordinary buttons. Both panes stay alive.
No document/core/scheduler changes or per-icon offsets.

## Verification

Passed `uv run --no-sync python tools/button_tabs_acceptance.py` in separate processes
with QT_SCALE_FACTOR=1, 1.5 and 2. Actual full-editor QML verifies centered/contained
buttons, custom left alignment, hover/focus/disabled state, help contrast, native arrow-key
navigation, selection-driven switching and retained search text. Normal and narrow
captures were inspected. Evidence: `build/tab-and-icon-alignment/<scale>/`.
The baseline is `build/tab-and-icon-alignment/before.json` and `before.png`.

Passed previous `tools/feedback_fixes_acceptance.py` (images, Ctrl placement, tabs),
plus both architecture tests. Pending: full development gate, remaining UI regressions,
canonical build and relocated portable qualification. All checks are background-only;
offscreen control captures do not establish 3D rendering or hands-on Windows acceptance.

## Next actions and blockers

1. Run full gate and existing UI regression tools.
2. Build canonical distribution, qualify relocation, merge and push.

## Recovery inputs

Reports: `%LOCALAPPDATA%/AnthroForge/Reports/<id>.afreport.zip`.
Extracted screenshots: ignored `build/report-triage/<id>/`.
Preserve unrelated untracked root `__init__.py`.
