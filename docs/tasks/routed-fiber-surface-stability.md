# Adaptive routed fibers and downstream material stability

- Task branch: `codex/routed-fiber-surface-stability`
- Integration branch: `main`
- Starting revision: `4be30b49e484957a62c548beffcb4d07f7a30021`
- Status: investigation and regression qualification
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Verify adaptive routing through actual Fiber creation and retained anatomical bindings,
then through surfaces/Membranes and downstream attached construction. Exercise evaluated
sample growth and shrinkage, source movement, persistence and undo/redo. Preserve authored
controls, endpoint bindings, consumer material correspondence and topology restrictions.
Fix demonstrated defects at their owning boundary; do not weaken collision validation.

## Current state

The preceding routing correction passes the curve/native bound-owner tests and a BODY
consumer test. It has not yet qualified complete Fiber-to-surface attachment chains.
Fibers use the same routing evaluator, with binding resolution supplying current inputs.
Surface exact sampling unions source stations; inspect its persistence/material behavior
before assuming changing route density is transparent to attached consumers.

## Verification

No new qualification result yet. Existing 1,358-test baseline passed before this task.
Official OMPL interpolation and Blender Surface Deform references were consulted;
repository material contracts and actual native results determine acceptance here.

## Next actions

1. Trace Fiber binding resolution, surface sampling and downstream attachment identity.
2. Add integrated adaptive-count regressions and inspect rendered output.
3. Correct demonstrated defects, run relevant checks and deliver through normal merge/push.

## Recovery inputs

The compact `tests/fixtures/routing/solver_fail1.json` reproduces the prior failure.
Keep local evidence under ignored `build/routed-fiber-surface-stability/`.
Preserve unrelated root `__init__.py`; all validation stays background-only.
