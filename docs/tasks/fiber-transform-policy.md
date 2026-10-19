# Fiber object transforms and creation selection

- Task branch: `codex/fiber-transform-policy`
- Integration branch: `main`
- Starting revision: `573405c`
- Status: investigating and implementing
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

Fiber objects cannot be translated, rotated or scaled through object commands,
keyboard shortcuts, toolbar buttons or gizmos. Shared application capability rules
own this restriction; UI presents the same decision. Authored point/handle editing
and attachment-driven deformation remain supported. Creating a fiber from a curve
exits editing and selects the newly accepted fiber. Failed/canceled creation must
not select an absent object or discard unrelated editing context.

## Current state and next actions

Inspected the generic construction transform command, desktop object/component
interaction paths and asynchronous fiber creation. Establish shared transform policy,
reuse creation-completion handling, then validate API and actual offscreen QML gestures.
Run the development gate, package/relocation checks and a validated merge/push.
Preserve previous releases, user fixtures and unrelated root `__init__.py`.

## Validation and delivery constraints

Qt Action/Shortcut APIs support shared enabled state. Existing application policies,
keyboard manager and asynchronous authored-object creation remain the owning boundaries.
Keep functions within 15 physical lines. Background-only validation; no visible
windows or desktop input. Test object restrictions separately from component editing,
and successful creation separately from failure/cancellation and undo/redo.

No checks run yet. Build/test outputs stay in ignored `build/` and `dist/` folders.
