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
Runtime variants, committed save/autosave projection, pinned-support policies and basic dockable
desktop navigation are implemented. Normal tools edit scoped alternatives; immutable checkpoints
fork independently. Path/attachment metadata copies include archived inputs. Initial promotion/
support refresh use existing candidate evaluation, precise reads, conflict choices and retained
previous-anatomy checkpoints, with shared before/after review UI. Catalogue/type/collections/
regions/reviews/queue API exists with focused tests; desktop, evidence and stages remain unfinished.
Promotion still needs production qualification, stronger topology lineage proof and support-scope
lifecycle testing. Do not treat these initial candidates as release-qualified.

## Verification

Focused context/scheduler/active-job tests: 16 passed. Existing skeleton-update command tests:
3 passed. Context tests cover ordinary edit/Undo isolation, same-identity concurrent jobs and
non-recursive schema round trips. Relevant mypy checks pass. Python function-limit/import
architecture checks pass. New variant/desktop tests pass. Regression run stopped at 6 failures
after 541 passes: formula validation expected a Session-only context and resource reachability
allocated a fresh projection each pass. Both causes fixed; focused driver/import/replay/resources/
variant/architecture suite now 27 passed. Broad rerun: 2733 passed, 2 failed solely on schema8
assertions, updated to9. This run preceded newest catalogue/UI additions. Variant review tests5
passed (one Undo/checkpoint, explicit conflicts, stale preparation, tissue source sharing and support
refresh). Catalogue tests4 pass. Embedded reference/evidence import and frozen comparison tests3 pass; UI and export integration remain unfinished. Hidden GPU panel and promotion window render without QML warnings
or visible windows; comparison framing is too close for narrow split views and needs correction.

## Next actions

1. Finish scope/copy/lifecycle validation and rerun regressions.
2. Implement refresh/promotion using isolated candidate evaluation and precise read validation.
3. Deliver catalogue/reviews/regions/queue, imported stages and comparisons.
4. Qualify production assembly, background GUI, profiler and canonical package; merge/push.

## Recovery inputs

Native: C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native.
Production: E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge.
Keep byproducts under ignored build/reconstruction-042. See tools/skeleton_update_* for
maintained production/hidden-render qualification infrastructure.

## Current checkpoint

Latest qualification: 2,750 regression tests passed before the final evidence/region UI
changes; the new catalogue/assembly/architecture subset passes 11 tests. Configured mypy
passes 622 sources and ruff passes. Assembly imports now copy catalogue/stage/region/review
evidence and explicitly selected variants, with independent identities. Regional reviews retain
their decision but become outdated after explicit patch redefinition. Hidden inspection export
passes end to end: corrected comparison/workspace camera conversion, held QML component
lifetime until capture, and JSON-normalized report metadata. Visually inspected exported split
view; no Qt imported into the calling headless process.

Production SCM experiment on the 96-muscle assembly: open 5.705s, create variant 0.105s,
inflation edit 0.346s, prepare/promote 1.152s (Apply 0.0067s), save 12.828s, reopen 10.746s.
Preview/commit geometry and bindings match exactly; Undo restores accepted state. Source hash
unchanged. Save peak working set about 3.04GB. Local reports/profile/project are under
build/reconstruction-042/production. These are not full production or release acceptance.

Remaining: reference/capability audit, populated/narrow GUI and stage availability,
production support refresh and shortcut follow-up/multiangle previews, docs/coupling review,
complete gate, canonical package and relocated portable qualification. No release claim yet.

Comparison desktop supports split/overlay, sections, picked material regions, and frozen
inspection export. Hidden GPU captures of every panel, promotion and comparison are clean;
corrected framing for narrow split views. Native batched region outlines built and 6 native
tests pass. Export still needs end-to-end qualification. Shared driver copying now retains
outside consumers; 5 added lifecycle tests pass for driver isolation/promotion, required
formula failures, support freshness, removal, and Undo/Redo context resource release.
Candidate required-output/editable scopes are explicit; stable topology requires native
connectivity/material and construction-lineage proof. Mirroring relationships merge by typed
identity. Python lint/function limits pass; remaining type correction applied. Full regression,
assembly metadata/explicit variant import, populated UI workflows, full96 production profiling,
and release qualification remain pending.

Explicit persisted EditingScope separates editable variant records from refreshed external supports.
Catalogue, independent review and resumable queue desktop pages are added; hidden-page verification
is pending. Immutable stage/evidence imports run through shared authored jobs and embed resources.
Frozen stage comparisons use existing native distance/section queries, without invented material
lineage. Focused variant/catalogue/desktop/architecture checks16 pass; embedded import/undo/save/
comparison checks3 pass. Full assembly, stages UI/export, assembly metadata transfer, lifecycle
review and release checks still required.
