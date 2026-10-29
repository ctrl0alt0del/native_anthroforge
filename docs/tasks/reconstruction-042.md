# Persistent variants, anatomical catalogue and reconstruction comparisons

- Task branch: `codex/reconstruction-042`
- Integration branch: `main`
- Starting revision: `16f550b`
- Status: in progress; not qualified
- Last updated: 2026-10-29 Europe/Bucharest
- Active writer: local Codex; no subagents authorized

## Outcome and decisions

Implement [confirmed contract](../reconstruction_042.md), integrating shared API and desktop
at each increment. 0.4.2 update, schema 9 with 4–8 readers. Preserve all existing anatomical
algorithms and unrelated root __init__.py. Background/hidden tests only.

## Current state

Added schema-9 reconstruction records/codecs and resource reachability, plus explicit editing
contexts with separate history/services and coordinator-owned scheduling namespaces. There
is one executor/resource admission/inline budget. Jobs retain their context identity; callback
publication runs under that context. Context switching pauses authored work without waiting.
Runtime variants, save/autosave projection, scope policies and desktop are not yet delivered.

## Verification

Focused context/scheduler/active-job tests: 16 passed. Existing skeleton-update command tests:
3 passed. Context tests cover ordinary edit/Undo isolation, same-identity concurrent jobs and
non-recursive schema round trips. Relevant mypy checks pass. Python function-limit/import
architecture checks passed before the last small helper edits. Full gate not yet run.

## Next actions

1. Add typed reconstruction state and schema-9 codecs/resource reachability.
2. Introduce explicit editable contexts with one coordinator and scoped publication.
3. Implement variants, refresh/promotion, catalogue/reviews/regions/queue and comparisons.
4. Qualify production assembly, background GUI, profiler and canonical package; merge/push.

## Recovery inputs

Native: C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native.
Production: E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge.
Keep byproducts under ignored build/reconstruction-042. See tools/skeleton_update_* for
maintained production/hidden-render qualification infrastructure.
