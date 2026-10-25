# UI workbench implementation

- Branch: `codex/ui-workbench`; integration: `main`; baseline: `9701c8c`.
- Scope: implement the approved [workbench design](../ui_overhaul_design.md) in 0.3.7.
- Direct work, no agents. Keep all validation background/offscreen/hidden.
- Preserve unrelated root `__init__.py`; checkpoint/push and validated merge authorized.

## Delivery sequence

1. Shell: menu, viewport-local workspace/tools, stable bottom calculation/status area,
   persistent pane dimensions and Focus editor presentation.
2. Context editor: Shape / Shortcuts / Inspect, remembered per category; move existing
   controls rather than duplicating operations. Tissue shaping and curve engine first.
3. Purpose-first copy and explicit enum labels, retaining stable data/API IDs and all
   restrictions. Optional relationships and diagnostics stay accessible.
4. Qualification: action-retention inventory, real interactions, numerical drag/focus,
   narrow/high-DPI captures, profiler comparison, development gate, portable package.
5. Update walkthrough/design status and one canonical 0.3.7 package/source archive.

## Contracts

No geometry, attachment, engine, shortcut-policy, save/undo or scheduler changes.
Existing Qt controls, command catalogue, capability enforcement, keyboard manager,
Issues, Activity, profiler and staged viewport remain the owners. Hiding a page must
not commit/cancel an unrelated gesture or repeatedly recreate a draft/editor. Active
tools remain reachable and explicit user page changes preserve existing transactions.
Desktop layout is local presentation state, never document data or an undo action.

## Initial evidence

Read Main, Inspector, Construction/Primitive/Tissue inspectors and the approved design.
Source confirms two mixed global toolbars, setup actions before tissue shape controls,
and raw enum labels. Shared UiSection already retains expansion while instantiated;
reuse it with explicit state keys rather than creating a parallel disclosure system.
Qt's existing SplitView supports persistent sizes; native focus scopes and visibility
must be tested with the actual keyboard and editing code.

Validation and delivery pending. Preserve all currently reachable actions, including
source replacement/split, optional inflation preview, mirror inspection, reports,
recovery and workspace management; a simpler default must not remove those features.

## Shell/editor checkpoint

Implemented the menu/viewport/status shell, context pages and persisted local layout.
Moved primary tissue shaping ahead of optional settings, grouped Fiber support controls,
and added display-only enum labels without changing command identifiers. Existing
editors stay instantiated across pages; document state and computations are untouched.

Source smoke, project recovery/recent workflows at two sizes, architecture checks,
and initial workbench interactions passed. Added explicit tests for layout persistence,
enum dispatch, preview retention, on-demand geometry inspection and curve editing.
Fixed new icon/encoding issues found during these checks. Full gate, profiling,
portable qualification and final visual/copy review remain pending. No release claim.
