# Outward surface snapping and numeric fields

- Task branch: `codex/outward-snap-numeric-fields`
- Integration branch: `main`
- Starting revision: `a816ee3a7d2950fda759c0f5ad84eb7fffa6a57f`
- Status: implementation, validation and canonical package complete; final integration pending
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Surface snapping must place curve points on the outside of the hit face, including
transformed geometry and drawing/point placement. Decimal entry must work in every
numeric field; horizontal value dragging must preserve coherent undo and text editing.
Validate actual Qt input offscreen, native snapping and routed paths, then run the
development gate and qualify one canonical 0.2.2 package.

## Decisions and relevant files

- Reproduced the decimal-entry cause: locale-dependent DoubleValidator rejected dot
  input under `uk_UA`, while Number/toFixed required it.
- Curve editing and native drawing applied signed offsets independently; double ray
  results were also narrowed to floats. Outward placement now has one native owner.
- Keep exact measurement/picking separate from outward snap placement.
- Preserve original project files and unrelated root `__init__.py`.
- All validation remains background/offscreen.

## Current state

Implemented native double-precision picking and shared outward placement for curve
editing, drawing/point placement and cursor placement. Negative snap offsets stop at
the surface safety margin. Implemented shared scalar/vector/transform number fields:
dot/comma decimal entry, live horizontal scrubbing, one undo and cancellation.

Added real scalar/vector/integer key+drag coverage, canceled drags on window
deactivation and control destruction, and integer lattice steps. Fixed NumPy scalar
conversion at the Qt boundary after real vector testing exposed displayed -1/empty
values despite correct authored edits. GPU texture-only capture shows the snapped
route around the cube's exterior. Runtime package revision: `275ff9d`.

## Verification

- `pytest tests/test_surface_snapping.py tests/test_numeric_edits.py tests/test_view_gestures.py tests/test_snapped_routing.py -q`: 31 pass.
- `QT_QPA_PLATFORM=offscreen python tools/numeric_input_acceptance.py`: passes real
  key/mouse events on production QML under Ukrainian, Romanian and English locales.
  Covers dot/comma/negative values, scalar/vector/integer dragging, one undo, Escape
  and window-deactivation cancellation. `numeric-acceptance.json`, `numeric-fields.png`.
- `tools/curve_interaction_acceptance.py` and `tools/view_gesture_acceptance.py`:
  insertion, target switching, camera changes, offset reset, both projections and undo pass.
- Development checks: lock, Ruff, formatting, mypy, native rebuild, 3 CTests,
  native/script style, function limits, numerical imports and native doctor pass.
  The full gate exposed a test fixture that assumed construction dispatched in one
  tick despite an asynchronous curve prerequisite. It now waits for actual dispatch;
  production scheduling is unchanged. The complete pytest rerun passes **1,344 tests**.
  Remaining numerical/doctor checks were run separately after that correction.
- `tools/check_portable.py --offscreen`: passed in a minimal-PATH environment,
  including Qt-free CLI/native operation, GUI, hidden GPU rendering, profiling,
  construction, tissue and persistence checks. Packaged native DLL matches the tested
  development DLL (SHA-256 `4f8054cd769639d346969af0c7408e1a8ff3b5b3c66143d9431670ec4c59c084`).
- Saved `snapped-route.anthroforge`, `route-evidence.json` and inspected
  `snapped-route-gpu.png`: the route follows the cube's exterior from its snapped
  top endpoint to its snapped bottom endpoint. Segment collision checks pass too.
- All GUI evidence is offscreen input or hidden texture rendering, not interactive
  visible-window acceptance. No user's foreground application was controlled.
- No original project was changed; an existing deeply interior authored point remains
  a separate authoring condition, not something an outward snapping policy repairs.

## Ownership review

Native geometry owns transformed normals, hit precision and safe outward placement.
All placement callers reuse that policy; exact measurement and attachment queries do
not acquire display offsets. The routing solver and its tolerances remain unchanged.
The shared numeric widget owns parsing and mouse interaction, while `NumericEdits`
adapts existing session transactions and cleans them up on interrupted gestures.
The shared Qt value adapter normalizes scalar types; individual inspectors do not
implement conversion workarounds. Core/headless code remains Qt-independent.

## Delivery

- Canonical executable: `dist/0.2.2/AnthroForge.dist/AnthroForge.exe`.
- Packaged runtime: `275ff9da0fc769250883d8e263ae5561a610170d`; later changes only
  synchronize a test and record qualification/product documentation.
- Executable SHA-256:
  `b6eec961159ad0af71c46af9415f3c5b17adfe1e5f522b5ba94963cee7c0005a`.
- Companion source: `dist/AnthroForge-0.2.2-source.zip`. One canonical distribution
  and source archive remain for this version; previous build is under ignored `build/`.
- Final action: commit/push this evidence and merge/push normally into `main`.
  The upstream integration tip was unchanged at final validation. Git ancestry
  records integration; no code validation or packaging remains outstanding.

## Recovery inputs

Normal `.venv/Scripts/python.exe` and `tools/check.ps1` environment.
Local evidence goes under ignored `build/outward-snap-numeric-fields/`.
No original anatomy fixtures may be modified.
