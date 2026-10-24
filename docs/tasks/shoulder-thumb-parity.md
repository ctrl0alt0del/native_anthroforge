# Shoulder and Thumb shortcut parity diagnosis

- Branch: codex/shoulder-thumb-parity; baseline: 51ff0af; integration: main.
- Request: isolate the remaining Ribs shoulder/Clavicle and Thumb differences from
  Blender. Explain actual causes and approach before changing attachment behavior.
- Background-only investigation; preserve source projects and unrelated __init__.py.
- References: tasks/shortcut-update-parity.md and tasks/shortcut-owner-binding.md.
- Compare baseline and edits on the same paired 96-muscle fixtures. Trace parent
  geometry, retained bindings, control transforms, curve endpoints and final poses.
- Test Hook and Shrinkwrap contributions separately rather than assuming either.
- Production behavior changes are outside this diagnosis until the approach is discussed.
- Local evidence: build/shoulder-thumb-parity; source parity fixtures remain untouched.
- Status: causes isolated in bounded experiments; no production behavior changes.

## Verified intermediate evidence

- App guide endpoints at the shared Hook coincide within 2.4e-15 before/after Ribs=3;
  their distance to the Hook is only the source's 1.19e-7 offset. The Hook deformer
  does not disconnect the curves. Its controlling SCP_7 follows Ribs directly, so
  Scapula Shrinkwrap cannot be the cause of that control's wrong world position.
- The native attachment kernel reproduces Blender's Hook pose from Blender inputs
  within 3.90e-7 maximum matrix component error. Migrated bindings recaptured a
  substantially different tangent and surface point. Keeping the source tangent
  while preserving baseline placement reduces Hook position gap 1.12826 -> .13955;
  source tangent plus transferred source surface point gives .11088. These are
  diagnostic candidates, not complete shape fixes; changed Ribs construction remains.
- Thumb addon wave actually has backsolve=True. The source property's raw value is
  False but is_property_set=False; owner_backsolve_enabled applies the legacy True
  default. The exported inventory retained only False; the migrated wrapper is off.
- Disabling backsolve in the disposable Blender session leaves Thumb pose exactly
  unchanged and reduces app/addon surface gap .00628144 -> 7.82e-6. Enabling the
  existing app backsolve gives .00059519 gap; differing child face anchors still
  require correspondence work. Neither source project was overwritten.
- Native frozen-input replay normalizes the geometry-versus-transform tangent frame;
  treating the addon's geometry-local hint as transform-local gave a false mismatch
  and was corrected before interpreting results.
