# Confirmed addon/standalone parity findings

Recorded 2026-10-24 against standalone runtime `51ff0af` (0.3.3).
**These are unresolved fidelity findings, not completed repairs.** Preserving the
standalone's existing results in a performance test does not establish Blender parity.
The [detailed investigation](tasks/shoulder-thumb-parity.md) records captures,
counterfactuals, source hashes and limitations. See also the broader
[functionality audit](addon_functionality_audit.md).

## F01 — Ribs shortcut moves the shoulder Hook using a different attachment frame

For Ribs Top Radius `0.9829999208450317 -> 3`, both curve ends remain connected in the
app within `2.4e-15`. Both accepted body surfaces also reach the Hook within `2.4e-8`.
The shared control itself is at a different world position from Blender.

The dependency chain is Ribs -> grouping SCP_7 -> shared Hook -> Clavicle/Acromion.
Scapula Shrinkwrap is on a separate branch; it cannot cause that Hook's displacement.
It still influences Acromion through its own attachment and has separate baseline
construction differences.

Migration recaptured the surface point and parent tangent instead of preserving the
source attachment frame. The current native propagation kernel reproduces Blender's
Hook matrix from the same source inputs within `3.90e-7`. A disposable candidate
retaining the source tangent while preserving initial placement reduces the Hook
position gap from `1.12826` to `.13955`; transferring the source point as well gives
`.11088`. These candidates do not establish complete shoulder parity. Ribs' sampled
surface differs between the two constructions, and correspondence still needs work.

Correction belongs first to migration/frame transfer and construction correspondence.
An arbitrary joint translation or a global change to Hook/Shrinkwrap is not supported
by this evidence. The candidate must preserve the initial scene and be requalified
after edits, undo/redo, reopening and downstream muscle updates.

## F02 — Thumb shortcut exported a raw value instead of effective backsolve policy

For Thumb Metacarpal Thickness `0.07000002264976501 -> 0.07350002229213715`, the addon
actually executes owner backsolve. Its RNA value is `False`, but the property was not
explicitly set; `owner_backsolve_enabled` applies its legacy `True` default. The source
inventory recorded only the raw `False`, and the migrated app wrapper has backsolve off.

Disabling backsolve in a disposable Blender process leaves the Thumb pose unchanged
and reduces the app/addon surface gap from `.00628144` to `7.82e-6`. Enabling the
existing app option reduces the ordinary comparison gap to `.00059519`.

Migration must inspect effective policy, including unset-property semantics, and
configure direct property wrappers as well as driving shortcuts. This finding does
**not** change the standalone's confirmed default of backsolve off for new shortcuts.

## F03 — Owner backsolve needs consistent child anchors after Boolean remeshing

Backsolve-on alone does not eliminate the Thumb discrepancy. Blender uses quad face 6
as its child anchor; its four vertices remain the same through the edit. The app
captures triangle face 12. That face's membership changes from `[1,4,3]` to `[3,5,1]`
when its Boolean output changes from 415 to 401 vertices. Equal face numbers are not
equal material anchors, and triangulation also changes the meaning of Face Center.

Preserve the intended child anchor through triangulation/topology changes and validate
its motion against the source before claiming exact backsolve parity. This is narrower
than changing all anatomical attachment resolution. Existing retained parent bindings,
approved exterior following and material-preserving tissue cropping remain separate
contracts.

## Evidence and scope

Inputs are the migrated 96-muscle standalone assembly and
`shortcut_update_parity_20261023/matching_96_muscles.blend`; hashes remained unchanged.
Evidence is local under `build/shoulder-thumb-parity`: snapshots, native replay,
actual attachment-wave operations, effective policy, face membership and fixed-camera
mesh comparisons. The maintained entry points are
[app capture](../tools/shortcut_attachment_probe.py),
[Blender capture](../tools/shortcut_attachment_blender_probe.py) and
[native replay](../tools/shortcut_attachment_counterfactual.py).

Distances use the recorded common scene-coordinate scale. Blender has no declared
physical-unit contract in this fixture; these numbers must not be interpreted as
anatomical centimetres. The addon assembly's existing two failed FDS radial bindings
remain explicit. These tests do not certify all tissue outputs or change the approved
crop, symmetry or exterior-following differences.
