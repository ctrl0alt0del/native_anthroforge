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

## Implementation checkpoint

The shared shortcut context now retains existing bindings for SCP transform targets,
including transitive driving targets; defaults need no extra capture job. Existing
optional override capture composes over retained bindings. No native algorithm or
ordinary transform/explicit rebind behavior changed. Multi-owner contexts may retain
bindings without claiming an owner for SCP-specific policies.

20 focused tests, Ruff and mypy pass. Actual 96-muscle Humerus +5% edit, unchanged
SCP/Fiber references and undo/redo pass. Anchor movement is 4.44e-16, Humerus response
error against addon <=6.55e-7, absolute surface distance <=5.78e-6 (baseline differs).
New local evidence: `E:/development/WIP_models/shortcut_owner_binding_20261024/`.
`tools/qualify_shortcut_owner_binding.py` reproduces the edit and all-object comparison.
Full gate, package, rendered-shape review and final ownership review remain pending.
The user's follow-up asks whether the Humerus geometry origin equals its attachment;
read-only Blender inspection is running, and must not trigger an unsolicited origin move.
