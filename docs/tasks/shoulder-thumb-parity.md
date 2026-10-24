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

## Verified evidence

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

The Hook also lies on both accepted app body surfaces: native nearest-surface gaps
after Ribs=3 are 1.77e-8 (Acromion) and 2.40e-8 (Clavicle). Thus the visible error is
the position of the shared joint, not lost Hook membership or separated body ends.
Scapula world surface gap is .09459 before and .10444 after; the much larger
Acromion/Clavicle gaps after the edit are 1.11488/1.06575. The Hook's dependency chain
is Ribs -> grouping SCP_7 -> shared control -> both bodies, without Scapula Shrinkwrap.
Scapula still feeds the Acromion attachment through a separate branch of the graph.

Thumb's source FACE_CENTER anchor is quad face 6, vertices [6,7,19,18], before and
after the edit. App face 12 is a triangle: membership changes [1,4,3] -> [3,5,1]
as its Boolean output changes 415 -> 401 vertices. Blender uses 427 -> 405 vertices
and 422 -> 401 polygons. The surfaces are close, but equal face numbers do not define
equal material anchors. Backsolve-on is a diagnostic improvement, not full parity.

## Proposed correction boundary

1. Preserve source attachment tangent/orientation and transfer its surface reference
   during migration, calibrating against the unchanged baseline pose. The hint-only
   experiment removes about 88% of the Hook position discrepancy. Resolve the remaining
   Ribs construction/correspondence difference before claiming shoulder parity; do not
   compensate with arbitrary translations or change global Hook behavior.
2. Export effective shortcut policy, including legacy unset-property defaults, and
   apply it to direct property wrappers as well as drivers. Preserve the Thumb owner
   anchor through triangulation/Boolean topology changes before calling it exact.
   The existing app backsolve operation already produces the expected direction/size
   of motion; no new shortcut mode is needed.

These are evidence-backed next implementation steps, not authorized changes to the
production attachment contract in this diagnostic task. Raw Blender property=False
alone was insufficient: the actual native operation and policy inspector both show
effective backsolve=True. Earlier hypotheses about Thumb's plain retained propagation
are superseded by this observed shortcut-session behavior.

## Validation, reproduction and limits

- Current runtime: 51ff0af; diagnostic tools only. No package, schema or source project
  changes. Existing unrelated root __init__.py remains untouched.
- Run tools/shortcut_attachment_probe.py PLAN OUTPUT CASE for app snapshots; Blender
  background tools/shortcut_attachment_blender_probe.py accepts ADDON SOURCE OUTPUT CASE.
  Optional --disable-backsolve changes only the disposable Blender process.
- tools/shortcut_attachment_counterfactual.py OUTPUT replays frozen inputs through the
  native propagation kernel. Shortcut backsolve is deliberately inspected separately
  through captured actual wave operations; plain propagation cannot explain it alone.
- Ruff/format and 15-line AST checks pass. Real baseline/edited captures completed in
  both runtimes; native replay, source policy toggle and app policy toggle were tested.
  No full application rebuild/test repeat was needed for tooling-only changes.
- Evidence: {ribs,thumb}/app and blender snapshots, counterfactual.json,
  calibration.json, endpoint-results.json, shoulder-distances.json, thumb-faces.json,
  actual waves.json and policy.json. shoulder-diagnosis.png and thumb-diagnosis.png
  show actual captured meshes at identical camera/scale; inspected background renders.
- Distances use the existing common scene-coordinate normalization; Blender has no
  declared physical-unit contract. Do not infer anatomical centimetres from them.
- Baseline construction differences remain explicit. These experiments do not certify
  all 96 muscles or supersede approved crop/exterior-following behavior. The paired
  addon assembly still has its previously recorded two failed FDS radial bindings.
