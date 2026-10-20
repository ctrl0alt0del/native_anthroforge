# Outward surface snapping and numeric fields

- Task branch: `codex/outward-snap-numeric-fields`
- Integration branch: `main`
- Starting revision: `a816ee3a7d2950fda759c0f5ad84eb7fffa6a57f`
- Status: in progress
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Surface snapping must place curve points on the outside of the hit face, including
transformed geometry and drawing/point placement. Decimal entry must work in every
numeric field; horizontal value dragging must preserve coherent undo and text editing.
Validate actual Qt input offscreen, native snapping and routed paths, then run the
development gate and qualify one canonical 0.2.2 package.

## Decisions and relevant files

- Shared numeric widgets currently use locale-dependent DoubleValidator with
  locale-independent Number/toFixed. Locale rejection is a hypothesis to reproduce.
- Curve editing and native drawing currently apply signed offsets independently.
  Trace their geometry and routing tolerance contracts before changing placement.
- Keep exact measurement/picking separate from outward snap placement.
- Preserve original project files and unrelated root `__init__.py`.
- All validation remains background/offscreen.

## Current state

Implemented native double-precision picking and shared outward placement for curve
editing, drawing/point placement and cursor placement. Negative snap offsets stop at
the surface safety margin. Implemented shared scalar/vector/transform number fields:
dot/comma decimal entry, live horizontal scrubbing, one undo and cancellation.

Ukrainian locale rejection reproduced with Qt's validator. Targeted native/history
checks pass (31 tests); real offscreen QML decimal, integer dragging, undo and Escape
checks pass. Full gate and portable qualification still pending. Added real scalar/vector/integer
key+drag coverage, canceled drags on window deactivation and control destruction,
and integer lattice steps. Fixed NumPy scalar conversion at the Qt boundary after
real vector testing exposed displayed -1/empty values despite correct authored edits.
GPU texture-only capture shows the snapped route around the cube's exterior.

## Verification

- `pytest tests/test_surface_snapping.py tests/test_numeric_edits.py tests/test_view_gestures.py tests/test_snapped_routing.py -q`: 31 pass.
- `QT_QPA_PLATFORM=offscreen python tools/numeric_input_acceptance.py`: passes real
  key/mouse events on production QML. This does not establish visible-window/GPU acceptance.
- Native rebuild and 3 CTests pass. Formatting/function checks being completed.
- No original project was changed; an existing deeply interior authored point remains
  a separate authoring condition, not something an outward snapping policy repairs.

## Next actions and blockers

1. Finish the full gate (running; style/native passed, pytest in progress).
2. Build and qualify a staged portable package, then replace the canonical 0.2.2 build.
3. Final evidence/documentation review, normal merge and push.

## Recovery inputs

Normal `.venv/Scripts/python.exe` and `tools/check.ps1` environment.
Local evidence goes under ignored `build/outward-snap-numeric-fields/`.
No original anatomy fixtures may be modified.
