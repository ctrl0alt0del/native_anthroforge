# Repair the saved muscle workflow

- Task branch: `codex/muscle-height-smoothing`
- Integration branch: `main`
- Starting revision: `dda3af44d2899bd27da95eb20c75ca15d743260e`
- Status: investigating; no fix qualified
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Make the tissue workflow in the user's `muscle_test.anthroforge` work. Reproduce
and fix the owning cause, inspect actual geometry, exercise edits and persistence,
and qualify the canonical portable application. Preserve the original project.
All GUI validation stays offscreen; no desktop input or visible windows.

## Observed evidence

The saved tissue's Rest result fails with
`Height smoothing: Smoothing would collapse or reverse an existing face`.
Intrinsic/stacking and two ordinary routed curves subsequently fail on that
prerequisite. Two Fibers and their Membrane have accepted ready results.
The tissue uses Distributed inflation, amount 1 m, with Height smoothing
radius 0.2, strength 0.8, maximum change 0.05.

The rejection originates in `native/migration/smoothing/src/height.cpp`.
Whether this is an actual fold or a false orientation rejection is not yet
established. Removing safety checks or suppressing Issues is not a fix.

## Verification and next actions

1. Reproduce native evaluation against the saved project and inspect geometry.
2. Diagnose the rejected faces and fix the responsible numerical/validation boundary.
3. Add representative regression coverage; validate GUI, persistence and packaging.
4. Run the development gate, checkpoint/push, then validated merge/push.

## Recovery inputs

- Original: `E:/development/WIP_models/muscle_test.anthroforge`
- SHA256: `adff36f1c75943ae808369edb26f989d0423d392a70399d0ac2267c590b6a3f7`
- Untouched local copy/evidence: `build/muscle-height-smoothing/`
- Existing untracked root `__init__.py` is unrelated and must remain untouched.

The containing Git commit identifies this checkpoint; inspect remote reachability
before treating work as recoverable from another machine.
