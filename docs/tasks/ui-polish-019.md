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
- Status: shared styles and progressive details implemented. Source UI and ruler/camera
  acceptance pass with no QML warnings. Full visual matrix, regression gate and packaging pending.

## Findings and ownership

- Qt Basic MenuItem uses palette.light/midlight for highlight/press, but Main
  overrides only some palette roles. Light system backgrounds conflict with our
  light text. Shared palette/menu components own contrast and menu alignment.
- Combo delegates use the entire control width inside an inset popup, overrunning
  the popup's padded content area. Shared controls own sizing and focus states.
- Inspection coordinates, issue evidence and workspace instructions are always
  expanded. Detail disclosures should preserve access without dominating controls.
- Existing lazy relationship inspection and incremental Activity models must remain.

## Next

Run tools/ui_polish_acceptance.py and inspect captures, finish regression/gate, then
package and deliver 0.1.9. Existing UI test had a stale key 7 expectation (current key 3);
ruler test now waits for displayed picking revisions instead of assuming a 50ms frame.

## References

- [Qt customization](https://doc.qt.io/qt-6/qtquickcontrols-customize.html)
- [MenuItem alignment](https://doc.qt.io/qt-6/qml-qtquick-controls-menuitem.html)
- [Engineering guidelines](../engineering_guidelines.md)
