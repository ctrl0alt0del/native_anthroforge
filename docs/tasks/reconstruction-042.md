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

Specification and repository boundaries inspected. Existing skeleton-update candidate
evaluation and comparison, typed graph copying, resource leases, history and command catalogue
provide the foundations. Session currently binds one mutable editing context; this is the
owning boundary to generalize before variants use normal tools.

## Verification

No runtime changes or new tests yet. Previous main qualification: 2,722 tests, six native
suites and 34 portable checks. That is baseline evidence, not qualification of this work.

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
