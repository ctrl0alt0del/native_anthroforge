# Tabs and compact icon alignment

- Task branch: `codex/tab-and-icon-alignment`
- Integration branch: `main`
- Starting revision: `ff3901cd4f64c08544708556c7481e1994210fbb`
- Status: in progress
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
Inspect UiButton's shared content/padding contract before fixing compact controls;
the suspected cause is fixed padding leaving less space than the icon/text needs.
Preserve left-aligned section headers and ordinary icon/text buttons.

Official references: [Control layout](https://doc.qt.io/qt-6/qml-qtquick-controls-control.html#control-layout)
and [TabBar](https://doc.qt.io/qt-6/qml-qtquick-controls-tabbar.html).

## Current state

Both report descriptions and annotated screenshots inspected. Source changes pending.

## Verification

Pending: measured before/after layout; offscreen QML captures at 100%, 150%, 200%;
tab mouse/keyboard/selection and pane-state checks; previous report regressions;
development gate; canonical build and relocated portable qualification.
Keep validation background-only. Offscreen captures do not establish manual acceptance.

## Next actions and blockers

1. Measure reported compact controls, then implement shared layout and real tabs.
2. Validate, checkpoint/push, package, merge and push after combined checks.

## Recovery inputs

Reports: `%LOCALAPPDATA%/AnthroForge/Reports/<id>.afreport.zip`.
Extracted screenshots: ignored `build/report-triage/<id>/`.
Preserve unrelated untracked root `__init__.py`.
