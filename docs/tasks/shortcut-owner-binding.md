# Retain owner bindings during shortcut transform edits

- Branch: `codex/shortcut-owner-binding`
- Integration: `main`; starting revision `4d24d6e`
- Status: in progress
- Active writer: desktop; background validation only

## Outcome and acceptance

Fix the Humerus shortcut attachment recapture diagnosed by
[the analytical comparison](shortcut-update-parity.md). Implement through the shared
property/shortcut editing contracts, preserving ordinary direct transforms, explicit
rebind, shortcut backsolve/overrides, transactions, async jobs and undo/redo.
Do not change the independent Thumb/Ribs behaviors or approved crop/exterior policies.

## Evidence and approach

The existing Humerus +5% test produces matching local geometry but ~.148258 world
response error. App transform operations recapture the edited owner's binding; addon
shortcut operations resolve its retained binding. A read-only retained-binding probe
matches the addon pose within 1.81e-6. Inspect the owning application boundary before
editing; no native deformation replacement is needed for this defect.

## Verification pending

Regression contracts; actual 96-muscle project Humerus edit and Blender comparison;
development gate; packaged/offscreen qualification; ownership review.

## Recovery inputs

Original project and prior baseline/case captures:
`E:/development/WIP_models/shortcut_update_parity_20261023/` (plan.json points to source).
Preserve source projects and the unrelated root `__init__.py`.
Use existing tools/shortcut_parity_* scripts; keep new captures in a separate folder.
No subagents. Existing engineering guidelines, 15-line function limit and checkpoint
workflow apply. Keep all work background-only.
