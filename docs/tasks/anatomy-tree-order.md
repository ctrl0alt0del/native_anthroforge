# Anatomy tree expansion order

- Task branch: `codex/anatomy-tree-order`
- Integration branch: `main`
- Starting revision: `e37cc4e3`
- Status: in progress
- Last updated: November 27, 2026, Europe/Bucharest
- Active writer: desktop anatomy-tree fix chat

## Outcome and diagnosis

Expanding an anatomy node must show its children immediately below it, before the next
sibling, retaining authored sibling order. The outliner filters a flat scene projection
whose SCP order currently comes from the document index's breadth-first traversal. This
places descendants after their parent's sibling list. Correct the presentation order;
preserve document storage, evaluation order, selection, collapse and search behavior.

The relevant owners are `desktop/scene_projection.py` and `desktop/qml/Outliner.qml`.
Qt model/view ordering and notification contracts were reviewed in the
[official documentation](https://doc.qt.io/qt-6/qabstractitemmodel.html).

## Validation and next actions

The controller regression reproduced the breadth-first failure before the fix. The four
new cases and related scene/tissue/index checks pass (15 tests). Native-window mouse
acceptance passes nested collapse, reopen, search while collapsed, authored sibling order
and retained selection; expanded screenshot visually inspected. The acceptance tool
settles hover layout before clicking the expand button. Ruff/format and the 15-line
function limit pass. See [CH-099](../computation_history.md) for the preserved boundaries.

Next: run the complete development gate, package and qualify the app. Deliver the same version to
`E:/development/anthroforge/dist/0.4.3/AnthroForge.dist` with its matching source archive.

The canonical app is currently running. Preserve its session and ask the user to close
it only after a qualified replacement is ready. The user's main checkout contains
unrelated assembly changes; implementation uses the clean existing instructions worktree.

## Recovery inputs

Shared venv: `E:/development/anthroforge/.venv`; native build: `build/skin-pipeline`;
Qt SDK: `E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`.
Set explicit PYTHONPATH to this checkout. External AVBD runtime:
`E:/development/anthroforge/build/application-boundaries` (read-only).
