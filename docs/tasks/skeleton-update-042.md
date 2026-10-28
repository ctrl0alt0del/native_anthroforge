# Whole-skeleton updates — 0.4.2

- Task branch: `codex/skeleton-update-042`
- Integration branch: `main`
- Starting revision: `5ed212a`
- Status: in progress; implementation and qualification pending
- Active writer: local desktop Codex
- Last updated: 2026-10-28, Europe/Bucharest

## Outcome and decisions

Implement the user-approved [whole-skeleton update contract](../skeleton_update_042.md).
Replace matched SCP construction/placement while preserving destination identities,
hierarchy, compatible controls, mirror rules and update modes. Independently copy required
construction; explicitly add unmatched source bones. Keep destination unmatched definitions.
Prepare and evaluate dependents in isolation, review incompatible bindings and newly failed
dependents, then commit once with Undo. Existing numerical algorithms remain unchanged.

## Current state

Read assembly copying, resource/provenance remapping, individual replacement reviews,
native capture and propagation, tissue retarget evaluation, coordinator and comparison.
The missing boundary is a multi-object candidate evaluation context, not a new optimizer.
Existing mesh replacement evaluates one target and propagates only after commit; existing
report replay creates a separate Session and is not the candidate execution architecture.

Initial contracts and graph-copy increment is implemented: one-to-one provenance matching,
ambiguous-match protection, identity-preserving SCP replacement, explicit additions and owned
candidate evaluation adapters. Evaluator adapters are not yet connected to public operations;
binding/control review, complete lifecycle/UI/qualification remain unfinished.

## Verification

`uv run --no-sync pytest tests/test_skeleton_update_contracts.py tests/test_skeleton_update_graph.py tests/test_architecture.py -q`:
9 passed on Windows with qualified native DLL. Full gate not yet run. Main is synchronized
with origin. Unrelated root `__init__.py` preserved.
All GUI/testing remains background/offscreen. No interactive acceptance will be claimed.

## Next actions

1. Add typed contracts/matching, candidate graph copying and shared lifecycle integration.
2. Add attachment/property review, isolated dependency evaluation and atomic publication.
3. Complete shared API/desktop comparison, correction and optional skin preview.
4. Run contracts, full gate, production profiler/shape tests and portable qualification;
   update the single canonical distribution, then validated merge/push.

## Recovery inputs

Production source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
Source hash: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`.
Qualified native runtime: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`.
Set `ANTHROFORGE_NATIVE_LIBRARY` to its `bin/af_native.dll` and `AF_NATIVE_BUILD` to that root.
Use `QT_QPA_PLATFORM=offscreen` for GUI tests. All task artifacts go under ignored
`build/skeleton-update-042`, not WIP_models. No new distribution names or versions.
