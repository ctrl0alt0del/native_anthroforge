# Whole-skeleton updates — 0.4.2

- Task branch: `codex/skeleton-update-042`
- Integration branch: `main`
- Starting revision: `5ed212a`
- Status: in progress; implementation and qualification pending
- Active writer: local desktop Codex
- Last updated: 2026-10-29, Europe/Bucharest

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
candidate evaluation adapters. Shared inspect/prepare/status/cancel/apply operations now use
the existing coordinator and owned candidate resources. Initial placement, dependent bone,
cancel, Apply and undo/redo tests pass. Binding review is started; driver remapping, mirrors,
complete evaluator coverage, UI and qualification remain unfinished. This checkpoint is not
release-ready and must remain on the task branch.

Second integration checkpoint: destination mirror policy is separated from assembly copying;
material compatibility requires native connectivity plus authored lineage (or exact content).
Destination control references are remapped from verified identities; formula value conflicts
require a deliberate choice. Candidate adapters now include tissue final groups and optional
fixed-topology skin deformation. Initial Manual tissue preview/adoption tests pass. Complete
mapping/correction UI, broad lifecycle and production acceptance are still pending.

## Verification

`uv run --no-sync pytest tests/test_skeleton_update_contracts.py tests/test_skeleton_update_graph.py tests/test_skeleton_update_commands.py tests/test_architecture.py -q`:
11 passed on Windows with qualified native DLL. Focused Ruff/mypy checks pass. Full gate not yet run. Main is synchronized
with origin. Unrelated root `__init__.py` preserved.
All GUI/testing remains background/offscreen. No interactive acceptance will be claimed.

Latest focused run: 27 tests passed (skeleton contracts/commands/controls/dependents,
architecture, existing shortcut reference lifecycle and assembly mirror tests). Full gate,
whole-assembly visual/performance evidence, optional skin/group-stack acceptance and portable
qualification have not run. Do not treat this checkpoint as completed functionality.

## Next actions

2026-10-29 continuation: the unchanged production assembly prepares successfully after
selecting Include for its three pelvic driver frames. Its saved Thumb Boolean mesh has
the same counts as a fresh reconstruction, but different ordered connectivity. Candidate
reuse now proves unchanged numerical definitions/accepted input revisions and retains
that saved resource, instead of rebuilding it and manufacturing a topology change.
The production candidate has two bone recapture findings; these are not yet accepted
as a qualified whole-body update. The first comparison window is wired into File and
the shared operations. Offscreen application smoke reports no warnings; focused reuse,
attachment-retention, desktop preparation/Apply/Undo/cancel and architecture tests pass.
Visual review of the dialog, anchor corrections, full lifecycle/skin/group-stack tests,
production edits/profile comparison, full gate and packaging remain incomplete.

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

Current checkpoint: added native comparison metrics, reviewed world-space attachment
corrections, coherent formula batches, stale-candidate status, synchronized comparison
publication, source-resource mirror/skin display and advisory geometry checks. The real
review window is inspected through hidden QQuickRenderControl (GPU); ordinary platform
'offscreen' captures test layout but do not render Quick3D on this Windows machine.
`build/skeleton-update-042/review-gpu.png` shows the translated fixture with no warnings.
Seven focused placement/native-distance/architecture tests passed before final UI additions.
Next: qualification of curve/region corrections, full lifecycle and production assembly;
full development gate and canonical packaging are still outstanding. Keep this task off main.
