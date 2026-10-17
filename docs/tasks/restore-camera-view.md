# Restore the camera after temporary axis views

- Task branch: `codex/restore-camera-view`
- Integration branch: `main`
- Starting revision: `24761722f666ff33c23f22ca9188303b80998fe5`
- Status: complete
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

Implemented the viewport-owned snapshot and shared restore lifecycle, semantic key 4,
viewport Restore button and View menu action. Consecutive axis switches preserve the
first snapshot; workspace/document camera restoration clears it. Updated user guidance.
Qt Camera/Shortcut documentation reviewed. No native or application-model changes needed.

## Verification

Passed on Windows: `uv run --no-sync python tools/camera_restore_acceptance.py`
(perspective/orthographic, mixed keys/buttons, menu action, no-op restore, fresh subsequent
snapshot, text focus, rebinding, workspace invalidation and persisted camera values).
Passed: `uv run --no-sync python tools/view_gesture_acceptance.py` with restoration during
direct/gizmo/modal transforms and Ctrl-snapping, unchanged points, undo and cancellation.
Original/restored camera captures and active-edit capture inspected visually.
Passed `./tools/check.ps1` at `a3667ad`: all 396 tests, native build/CTest, style/type checks,
numerical imports and native loading. Passed full rebuild via `./tools/package.ps1` and
`uv run --no-sync python tools/check_portable.py dist/AnthroForge.dist/AnthroForge.exe build/camera-restore-portable-check`.
Packaged QML matches qualified source; packaged desktop capture inspected. Later commits
update documentation only. Ownership review is recorded in development_status.md.
Initial repository is clean apart from the unrelated untracked root `__init__.py`.

## Next actions and blockers

No remaining implementation or acceptance work. Deliver the completed task through the normal
merge/push to main; inspect Git history for the merge and remote reachability.

## Recovery inputs

Use the existing Windows setup and ignored native build. GUI fixtures are generated
by maintained acceptance tools; no external anatomical models are required.
Ignored GUI evidence: `build/camera-restore-review` and `build/view-gesture-review`.
Portable executable: `dist/AnthroForge.dist/AnthroForge.exe`; corresponding source archive:
`dist/AnthroForge-0.1.3-source.zip`. Build/portable logs and captures are local-only ignored files.
The containing Git commit identifies this checkpoint; inspect branch/remote history.
