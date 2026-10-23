# Windows review of the Cloud 0.3 continuation

Work in progress on `codex/shortcuts-parametric-030`; no release claim.

## Real addon attachment references

`tools/capture_shortcut_parity.py` opens the original sources in Blender 5.0.1
background/factory/disabled-autoexec mode, registers only SCP properties, reads
evaluated geometry, and calls the addon's capture/apply kernels. It does not save
either source. Explicit property storage avoids unrelated live update handlers.

- `skeleton_comb_base.blend`: SHA256
  `1049c9cef5d0e94735e20e1f3e313cdb845a67c6554ccf3a98e81da98b813ff2`.
  Pubis Arc Angle changes by -0.35 rad. The recorded Ilium override uses Surface
  Nearest, Face Center, Follow Rotation, Deformation Flow. A second capture uses Auto.
- `skull_muscles.blend`: SHA256
  `4855042f259135c569c3e89b50df5d0441e6794bef5e774aebf924fd8372287e`.
  Cheekbone SuperHook AF Local X changes by 0.08 source units, then retained owner
  anchor backsolve applies translation.

`tools/check_shortcut_parity.py` compares native evaluation on the captured meshes,
poses and retained material bindings. Maximum absolute matrix-component differences:
Pubis explicit and Auto **1.94485e-5**; Cheekbone **7.89165e-8**; tolerance **3e-5**.
This verifies numerical application of real retained attachments. It is not a full
Blender-project migration or a claim that every native capture chooses the identical
nearest triangle. Existing synthetic capture parity and application wrapper lifecycle
tests cover those separate boundaries. Original files are preserved.

The source investigation found Auto previously resolved to Stable in standalone,
regardless of a Body's curve deformation. Shared capability policy now selects flow
for Body construction and Stable for other providers; explicit strategies remain
available. Existing bindings without a secondary flow sample retain their fallback.

## Desktop evidence

- `tools/shortcuts_reorder_acceptance.py`: production-QML mouse reorder, one-action
  undo, Escape cancellation including continued pointer motion before release.
- `tools/shortcuts_workflow_acceptance.py`: full Main-window shortcut scrubbing,
  cancel/undo, downstream Parametric and Body work, and a runtime profiler capture.
  Offscreen software window captures do not establish native 3D rendering.
- `tools/shortcuts_scene_acceptance.py`: native D3D11 texture renderer, invisible
  QQuick window, initial Body, variable edit, exact vertex Undo, and generated-point
  edit presentation. Captures inspected in `build/shortcuts-scene-review/`.

The scene harness drains deferred Qt deletion between frames, matching a running
event loop. An earlier harness without that step showed obsolete outline objects;
that was a harness artifact, not evidence for a production renderer change.

No interactive desktop acceptance is claimed. Raw captures and source geometry are
ignored/local artifacts; the maintained tools reproduce the checks.

## Existing assembly compatibility

`tools/shortcuts_compatibility.py` used the released 0.2.4 executable and a copy of
`2026-10-21-standalone-all-muscle-transfer-958f7969/candidates/current.anthroforge`
under the muscle workflow runs directory: 59 SCPs and 548 construction/tissue objects.
The old executable opened/saved a schema-4 baseline with its existing startup behavior.
The reviewed application then opened that baseline without changing any document
record, and saved schema 5 with identical hashes for every stored resource buffer.

Both versions then translated Clavicle (`SCP_6`) by 3 mm. Complete saved document
states match after replacing nondeterministic resource IDs with their buffer-content
hashes, including geometry, bindings, poses, correspondence and revision provenance.
The original project was never opened for writing. This is actual old-executable
compatibility evidence, not a manifest-version rewrite. Logs/copies are local in
`build/shortcuts-compatibility/`.

The real 0.2.4 executable rejects the resulting schema-5 file with exit code 1 and
`Unsupported AnthroForge project format/version.`

## Final independent qualification checkpoint

The stable code checkpoint `57873c1` completed `tools/check.ps1`: **1,928 tests passed,
one strict expected failure**, five CTests passed, native/script style, Ruff/mypy,
numerics and headless doctor passed. The expected failure is the unresolved generated
point-reference policy below, not an accepted release limitation.

The executable built from that checkpoint under
`build/shortcuts-portable-review/AnthroForge.dist` passed the complete
`tools/check_portable.py --offscreen` suite with a minimal PATH. This includes the
existing tissue/attachment workflows and new shortcut formulas, Parametric paths,
schema-5 persistence, complete profiling and native consumer rendering. The final
`build/shortcuts-portable-check/shortcuts.png` was inspected: the selected thin circular
Body follows its Parametric source without the earlier oversized fixture overlap.
Rendering used a hidden QQuickRenderControl; no visible desktop interaction is claimed.

The package still identifies as 0.2.4. This is a temporary qualification build, not the
canonical 0.3.0 release. Main merge, version advancement and final distribution remain
pending the point-reference decision, repair and affected-path qualification.

## Ownership and coupling review

This is a coordinator-authored code review, separate from test counts:

- Core property descriptors preserve identity, numerical type/dimensions and scalar
  versus vector shape. They do not invoke editing policies or import Qt/Blender.
  Application adapters reuse semantic object operations and validation; driven and
  topology restrictions are shared by the UI and headless path.
- Drivers and Parametric use the same bounded native expression service. Python
  owns dependency ordering, owned-input packing and publication; there is no Python
  expression interpreter, iterative numerical fallback or competing worker pool.
- Temporary attachment contexts capture before a wrapper edit, retain immutable
  inputs through asynchronous work and restore authored settings. Ordinary properties
  do not activate wrapper policy. Auto strategy is resolved once through shared core
  capability policy in both native capture and propagation preparation.
- Desktop models, numerical edit ownership and drag ordering are presentation
  adapters over shared operations. QObject destruction/cancel paths are exercised;
  context menus do not become an alternative command or validation implementation.
- The Qt model collector is isolated from documents and calculation scheduling.
  Its scoped event filter exists only during recording; bounded signal connections
  and pending discovery retain explicit loss reporting. Signal-name metadata is
  immutable and reused during discovery rather than allocated per visited method.

Open finding: generated point IDs currently follow sample index. A resolution change
can therefore move an existing Hook to another parameter location. The regression is
explicitly expected to fail while the user chooses locking versus parameter-preserving
remapping. It must be resolved and qualified before main/release; the expected failure
is not release acceptance. The existing consumer-attachment and junction locks remain
enforced and independently tested.
