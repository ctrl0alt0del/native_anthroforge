# Restore the camera after temporary axis views

- Task branch: `codex/restore-camera-view`
- Integration branch: `main`
- Starting revision: `24761722f666ff33c23f22ca9188303b80998fe5`
- Status: in progress
- Last updated: 2026-10-17 (Europe/Bucharest)
- Active writer: desktop chat implementing camera restoration

## Outcome and acceptance

Preserve the original camera when entering axis views through 1/2/3 or their UI
buttons. Restore it with 4 and a matching UI action, including position, rotation,
zoom and projection. Repeated axis switches retain the first original view.
Switching or restoring must preserve active gestures and their undo/cancel boundary.

## Decisions and relevant files

`Viewport.qml` already owns camera state and shares `setView` between shortcuts
and buttons. Extend that boundary and reuse the existing gesture rebasing. Bind 4
through `KeyboardManager.qml`; keep the temporary bookmark outside authored anatomy.
Clear it when loading another document/workspace camera. No application/schema changes.

## Current state

Inspected camera navigation, controller camera restoration and real-window gesture
acceptance. No implementation yet. Qt Camera/Shortcut documentation reviewed.

## Verification

Not yet run: development gate, GUI regression and portable runtime checks.
Initial repository is clean apart from the unrelated untracked root `__init__.py`.

## Next actions and blockers

1. Add shared camera capture/restore, keyboard binding and visible restore controls.
2. Extend actual QQuickWindow acceptance for navigation, active edits and text focus.
3. Run gates, inspect GUI evidence, qualify packaged runtime and integrate normally.

## Recovery inputs

Use the existing Windows setup and ignored native build. GUI fixtures are generated
by maintained acceptance tools; no external anatomical models are required.
The containing Git commit identifies this checkpoint; inspect branch/remote history.
