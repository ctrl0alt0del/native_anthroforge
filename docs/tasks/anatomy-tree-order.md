# Anatomy tree expansion order

- Task branch: `codex/anatomy-tree-order`
- Integration branch: `main`
- Starting revision: `e37cc4e3`
- Status: implemented, qualified and delivered; ready to integrate
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

- Native build, six CTests, native style and PowerShell checks pass. Ruff/format, mypy
  (711 files), lock consistency and QML validation (186 files / 46 types) pass. Full pytest
  passes all 3,001 tests in 1,061.84 seconds. Numerics and native doctor pass too.
- Standalone runtime `e25a9f52` was built cleanly and relocated to the main checkout's
  ignored `build/anatomy-tree-delivery-20261127/AnthroForge.dist`. All 3,424 files match
  the source package by SHA-256 (421,411,838 bytes).
- Minimal-PATH native doctor, primitive creation/inspection/render and GUI smoke pass.
  A packaged native window verified collapse as Root/Arm/Leg/Foot and reopening as
  Root/Arm/Upper/Hand/Lower/Leg/Foot. The generated test project was saved before closing.
- The first empty-group fixture used surface attachments and correctly failed packaged
  warning-free startup. The acceptance fixture now uses Object Origin attachments. Its
  source GUI and packaged startup were rerun successfully; application code is unchanged.

- Replaced `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist` and the matching
  `dist/AnthroForge-0.4.3-source.zip`. All delivered package hashes and the source archive
  hash match staging. Canonical-path minimal-PATH native startup and GUI smoke pass;
  its anatomy screenshot was visually inspected. Other versions were preserved.
- Source archive checkpoint is `68b03137` (24,411 entries; CRC and implementation/acceptance
  byte comparisons pass). Changes after runtime `e25a9f52` affect only acceptance fixtures
  and documentation, not shipped application code. Local evidence: `build/anatomy-tree-review`
  and `build/anatomy-tree-portable-review`; the previous package is retained in the main
  checkout under `build/anatomy-tree-delivery-20261127/previous-build`.

The canonical app was closed at publication; no user process was stopped. The main checkout contains
unrelated assembly changes; implementation uses the clean existing instructions worktree.

Next: integrate the reviewed task branch into `main` and verify remote ancestry.

## Separate AVBD setup finding

The user's AVBD runtime-unavailable message is the expected missing-runtime preflight.
The external runtime's Python and worker exist in `build/application-boundaries`, but
neither User nor Machine environment defines `ANTHROFORGE_AVBD_RUNTIME`. Existing AVBD
qualification explicitly sets it; normal executable launch does not. The portable app
ships the adapter, not that external solver environment. No runtime configuration or
AVBD packaging changes were made as part of this anatomy-tree correction.

## Recovery inputs

Shared venv: `E:/development/anthroforge/.venv`; native build: `build/skin-pipeline`;
Qt SDK: `E:/development/anthroforge/.tools/qt/6.12.0/msvc2022_64`.
Set explicit PYTHONPATH to this checkout. External AVBD runtime:
`E:/development/anthroforge/build/application-boundaries` (read-only).
