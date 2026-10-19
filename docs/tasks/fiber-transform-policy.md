# Fiber object transforms and creation selection

- Task branch: `codex/fiber-transform-policy`
- Integration branch: `main`
- Starting revision: `573405c`
- Status: implementation and delivery validated; integration recorded in Git ancestry
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

Implemented shared object-transform policy, separate component eligibility, capability
gating in the keyboard manager and consistent toolbar/gizmo/numeric-field availability.
Added desktop selection intent for single-output asynchronous creation, with context
invalidation and accepted-output adoption. The fiber UI uses this path; job outputs and
the existing scheduler remain authoritative. No extra document transactions are added.

Actual offscreen clicks exposed disabled toolbar controls passing clicks to the viewport
and clearing selection. The toolbar container now consumes otherwise unused pointer
events. Tests cover this without changing the fiber policy or the shared button class.

Targeted tests pass, including failure/cancellation, supersession, history, component
availability and successful creation selection. Full offscreen fiber editing, general
construction editing and view-gesture scripts pass. Full development gate passes:
916 tests, 3 native tests, static analysis, Ruff, mypy on 191 modules and function limits.
The implementation is committed as `1d6af1d`. Its clean portable build passes the complete
relocated suite and a direct packaged API check of six rejected local/world TRS changes
with unchanged authored objects. All 94 QML/JS/SVG assets match source.
Preserve previous releases, user fixtures and unrelated root `__init__.py`.

## Validation and delivery constraints

Qt Action/Shortcut APIs support shared enabled state. Existing application policies,
keyboard manager and asynchronous authored-object creation remain the owning boundaries.
Keep functions within 15 physical lines. Background-only validation; no visible
windows or desktop input. Test object restrictions separately from component editing,
and successful creation separately from failure/cancellation and undo/redo.

New interaction tests plus architecture checks: 17 passed. Existing Qt property-map
deprecation warnings remain. Full gate log: `build/fiber-policy-gate.log`; offscreen
evidence: `build/fiber-transform-policy/fiber-object.png` and `build/fiber-editor-policy.log`.
The capture was inspected; no visible desktop window was used. Deliver a separate
`dist/0.2.1-fiber-edits/AnthroForge.dist` and matching source archive, preserving the
feedback-reporting distribution. Build/test outputs remain ignored.

## Final validation and integration

The final executable is `dist/0.2.1-fiber-edits/AnthroForge.dist/AnthroForge.exe`; matching
source is `dist/AnthroForge-0.2.1-fiber-edits-source.zip`. Portable evidence is
`build/fiber-policy-portable/portable-check.json` and `fiber-transform-denial-results.json`.
Full build log: `build/fiber-policy-package.log`. Tests use copies/fixtures only.

Additional feedback and curve-workflow checks exposed teardown crashes after successful
assertions: their C++-owned Qt applications were not explicitly destroyed. Both harnesses
now match the desktop/profiler cleanup order. Feedback passes with clean process exits
at normal/200% scale, and the 120-item curve-workflow/placement suite also exits cleanly.
These test-only fixes need no executable rebuild; Ruff and function-limit checks pass.

Architecture review is in `docs/development_status.md`: shared transform policy,
component availability, generic keyboard capability gates, desktop-only selection intent
and toolbar event ownership. No new numerical algorithms or scheduler semantics.
Merge the validated branch normally; Git ancestry records the integration revision.
