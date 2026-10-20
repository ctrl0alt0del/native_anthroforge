# Branched point placement and automatic surface grouping

- Task branch: `codex/branched-point-placement`
- Integration branch: `main`
- Starting revision: `99737ca`
- Status: in progress
- Last updated: 2026-10-20
- Active writer: desktop chat, direct work

## Outcome and acceptance

Right-click Place Points to choose regular or branched placement. Before its first
click branched placement previews the nearest authored curve control point. Complete
the new curve and its shared junction in one undo action; cancel without document edits.
Preserve normal continuation, snapping, engine, and workspace contracts. The Surface
action infers branch groups from explicit junctions; ask only for ambiguous valid groups.
Reuse existing surface/membrane evaluation and its open, nonnested branch restrictions.

## Decisions and relevant files

- User confirmed automatic grouping, with a choice only when ambiguous.
- Existing `DrawingTools` owns provisional placement; native queries own repeated picking.
- Shared application commands own atomic creation and branch inference/validation.
- Existing `surface.branch.add` requires two or more distinct interior roots on an outer
  main curve. A joined single curve is construction, not by itself a surface branch.
- Qt context menus: https://doc.qt.io/qt-6.12/qml-qtquick-controls-contextmenu.html

## Current state

Implemented atomic branch-curve creation with existing-junction reuse, cached native
projected control-point selection and explicit stroke seeding. Alternate toolbar tool
and provisional marker are wired. Automatic surface grouping uses junction identities;
ambiguous group membership opens a virtualized editor. Implementation is not yet qualified.
Preserve unrelated root `__init__.py`. Base is synchronized with origin/main.

## Verification

Baseline: 23 related point-placement, surface-branch and attached-conversion tests passed.
Current increment: 14 branch-creation, projected-placement, automatic grouping and
architecture tests pass; native rebuild and three CTests pass. The automatic branch
geometry matches the existing fixture numerically. Actual GUI/shape inspection pending.
Required: targeted API/lifecycle tests, offscreen gestures/menu/preview/ambiguity checks,
actual branched surface and membrane visual inspection, development gate and portable build.

## Next actions and blockers

1. Implement shared atomic branch curve creation and native control-point picking.
2. Integrate alternate tool, first-point preview and automatic/ambiguous surface grouping.
3. Validate, update durable documentation, package canonical 0.2.2 and merge/push.

## Recovery inputs

Use existing `.venv`/native runtime. Keep all GUI validation background-only. Evidence
belongs under ignored `build/branched-point-placement/`; source fixtures remain in tests.
