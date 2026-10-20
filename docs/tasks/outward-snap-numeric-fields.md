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

Investigation only. No runtime changes yet. Official Qt validator/drag-handler docs
and PBRT rounding-error treatment reviewed as implementation references.

## Verification

Pending. No claimed fix or GUI acceptance yet.

## Next actions and blockers

1. Reproduce locale rejection and inspect shared numeric/transaction ownership.
2. Implement native outward snap placement and reusable numeric dragging.
3. Validate, update computation history, package, merge and push.

## Recovery inputs

Normal `.venv/Scripts/python.exe` and `tools/check.ps1` environment.
Local evidence goes under ignored `build/outward-snap-numeric-fields/`.
No original anatomy fixtures may be modified.
