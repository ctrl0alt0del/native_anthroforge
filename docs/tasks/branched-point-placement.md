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
ambiguous group membership opens a virtualized editor. Offscreen interaction and actual
hidden GPU geometry inspections pass. The full gate passed with 1,414 tests and the first relocated portable suite passed.
A final dense-graph allocation correction is being requalified and repackaged.
Preserve unrelated root `__init__.py`. Base is synchronized with origin/main.

## Verification

Baseline: 23 related point-placement, surface-branch and attached-conversion tests passed.
Current increment: 33 focused tests pass, including existing-junction reuse, Fiber-root
following, transforms, hidden/behind-camera candidates, cancellation/undo, ambiguous drafts,
stale draft rejection, 102-curve inference and attached conversion. Three native CTests pass.
`tools/branch_placement_acceptance.py` verifies actual right-click menu, preview, click/Shift
gestures, one undo and explicit group selection in offscreen QML. Menu positioning is
anchored beside the tool, including synthetic input. `tools/branch_placement_scene.py`
renders a continuous T-shaped branched surface and its identical converted Membrane via
hidden Direct3D; images inspected. Reports/shapes/saved fixture are under the evidence path.
Native cached picking microcheck: 10k controls, 500 queries, median 0.0271 ms/p95 0.039605 ms;
not a whole-app responsiveness measurement. Full development gate and initial portable checks passed at `3d02ab4`.
Final review reproduced a search-cap defect on 30 cross-connected curves; exact identity
matching now replaces the cutoff, with three extra regression/oracle tests passing.
Final Python/UI qualification and updated packaging are pending; native code is unchanged.

## Next actions and blockers

1. Finish the running development gate and any discovered failures.
2. Package the canonical 0.2.2 app, run relocated portable qualification (including new branch
   and membrane flow), and rebuild the companion source archive.
3. Record final evidence; merge/push the validated result.

## Recovery inputs

Use existing `.venv`/native runtime. Keep all GUI validation background-only. Evidence
belongs under ignored `build/branched-point-placement/`; source fixtures remain in tests.
