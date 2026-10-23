# Retain owner bindings during shortcut transform edits

- Branch: `codex/shortcut-owner-binding`
- Integration: `main`; starting revision `4d24d6e`
- Status: implemented; full development gate running, integration pending
- Active writer: desktop; background validation only
- Runtime implementation: `6d9bae8`

## Outcome and design

Fix the Humerus shortcut attachment recapture diagnosed by
[the analytical comparison](shortcut-update-parity.md). The shared shortcut edit context
retains existing bindings for SCP transform targets, including transitive driving targets.
Default retention is immediately ready and adds no capture job. Existing temporary
backsolve/descendant policies compose over those bindings. Multi-owner drivers can retain
controlled bindings without acquiring an owner for SCP-specific policy overrides.

Ordinary direct property/transform editing and explicit recapture still capture a new
binding. Non-transform shortcuts do not acquire extra attachment evaluation. No native
solver, geometry, schema or presentation changes. Existing transaction/job/history/save
ownership carries the retained intent. CH-067 records the computational rationale.
Unrelated Thumb/Ribs differences and approved crop/exterior policies are unchanged.

## Actual-assembly and visual acceptance

Source project:
`E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Unchanged SHA256: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Prior addon/app captures: `E:/development/WIP_models/shortcut_update_parity_20261023/`.
New evidence: `E:/development/WIP_models/shortcut_owner_binding_20261024/`.

- Exact requested Humerus length `3.1134088039398193` (+5%) retains every SCP/Fiber
  attachment. Shoulder anchor displacement is 4.44e-16 world units, versus .14825748
  before this correction. Undo restores every tissue vertex exactly; redo agrees.
- Humerus response error against Blender is <=6.55e-7. Absolute surface distance is
  <=5.78e-6, including the existing baseline discrepancy. Radius absolute distance is
  <=1.02e-5 and Ulna <=1.34e-5. Cropped tissues intentionally retain CH-065 behavior;
  this does not claim universal addon geometry parity.
- All four fixed-camera comparisons were inspected: arm bones, shoulder attachment,
  anterior muscles and posterior muscles. Corrected anchor and bone movement match
  the addon. PNGs are under `visual_review/sheets/` in the new evidence directory.
  These render frozen evaluated geometry through identical Workbench presentation.
- User's origin question checked directly in `skeleton_comb_base.blend` and the matching
  96-muscle Blender assembly. Humerus geometry and transform share the same object;
  origin is near the bone center, not the shoulder attachment (distance ~2.96523 world
  units). The app keeps that same frame. Local child anchor is approximately
  (-1, -.0148, .07765). No source file or origin was moved. `origin-check.json` records it.

## Qualification

22 focused regressions cover all update modes, paused/rapid drags, cancellation,
undo/redo, Manual save/reopen, direct-edit/explicit-recapture supersession, multi-owner
drivers, existing override/backsolve behavior and formula/geometry barriers. Ruff,
mypy and 15-line function checks pass. Full `tools/check.ps1` is still running.

The canonical `dist/0.3.0/AnthroForge.dist` passes the full minimal-PATH portable suite.
Actual packaged Humerus edit, undo/redo and save/reopen preserve all 625 geometry/pose/path
fingerprints and 914 attachment/reference/field fingerprints exactly against the corrected
source result. Hidden desktop opens 59 SCPs without QML warnings. Native hidden rendering
was inspected; offscreen UI capture alone is not viewport pixel evidence. No physical
mouse/keyboard interaction or interactive-display acceptance is claimed.

Reproduction:
- `tools/qualify_shortcut_owner_binding.py <prior-captures> <new-evidence>`
- `tools/check_shortcut_owner_portable.py <executable> <new-evidence> <output>`

Logs: `build/shortcut-owner-binding-{gate,package,portable,packaged-assembly}.log`.
Packaged evidence: `build/shortcut-owner-binding-portable/` (including profiler report).
Local anatomy, renders and captures are ignored; they are not in the remote checkpoint.

## Ownership review and remaining delivery

Coordinator-authored review: shortcut intent belongs to the existing shortcut context;
property operations remain unaware of wrapper policies. Effective bindings, resource
ownership, input validation and result restoration reuse the existing attachment adapter.
No feature-name checks, SCP identity exceptions, competing queues or native algorithm
changes. Policy ownership remains distinct from a default retained transform binding.

Finish the full development gate, update its actual result here and CH-067, refresh
packaged documentation/source archive, then validated merge/push. Preserve unrelated
root `__init__.py`. No subagents or visible desktop control.
