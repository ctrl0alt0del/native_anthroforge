# AnthroForge 0.4.1 preparation

- Task branch: `codex/release-041`
- Integration branch: `main`
- Starting revision: `9363267` (qualified 0.4.0 merge)
- Status: in progress; inventory only, no runtime changes
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

The user accepted 0.4.0, requested its merge into main, and requested starting 0.4.1.
The merge is complete. The previously confirmed next-version direction is broader use
of operation-specific status providers, following SkinStatusProvider. See
[architecture](../architecture.md#shared-operation-status-providers) and
[roadmap](../roadmap.md). An asynchronous question about additional 0.4.1 priorities
has not received an answer; do not infer new skin algorithm or quality changes.

Status assessments must stay read-only, share application policies with command execution,
and use existing notifications. Preserve operation-specific reasons and warnings, workspace
editability, read-only mirrors, transaction rules and execution-time revalidation. Do not
introduce a universal status manager, polling, or a second authoritative eligibility store.

## Current state and initial inventory

No new release version, project schema, numerical algorithm or UI behavior has changed.
The following are observed ownership boundaries, not claims that their current results
are wrong. Existing shared policies should be reused, not replaced with parallel checks.

| Candidate | Observed existing boundary | Next investigation |
| --- | --- | --- |
| Change tissue source | `desktop/qml/TissueInspector.qml` composes editing/waiting/read-only conditions. `application/tissue_retarget.py` independently guards the active gesture and blocked save before assessment. | Extract one cheap eligibility assessment used by the action and API; retain separate candidate compatibility review. |
| Replace imported mesh | `desktop/qml/PrimitiveInspector.qml` composes the same interaction conditions. `application/mesh_replacement.py` owns imported-type/editability and gesture/save guards. | Share assessment with the UI while preserving required correspondence reviews and candidate revalidation. |
| Curve topology and sampling | `desktop/authoring_state.py` already projects `construction_policy.topology_locks`. `application/parametric_policy.py` already provides resolution and sampling reasons. | Audit which controls consume these existing reasons and which reconstruct broader booleans; avoid replacing working policy projection. |
| Object transforms | `application/transform_policy.py` owns Fiber/Anchor/Tissue restrictions; `desktop/object_interaction.py` invokes shared editability and transform checks. | Verify toolbar, keyboard and numeric properties use the same eligibility without adding a second transform policy. |
| Workspace changes | `application/workspace_policy.py` owns membership and blocks changes during a gesture or blocked save. | Trace desktop actions and notification dependencies before deciding whether a provider adds value. |

Presentation-only conditions, such as showing parameters for the selected inflation mode,
do not automatically need an application status provider. `tissue_retarget_policy.py` and
`mesh_replacement_policy.py` assess proposed compatibility changes, not generic action
availability. Keep these responsibilities distinct.

## Proposed first increment

Start with Change tissue source and Replace imported mesh: the UI and application
currently express overlapping operation conditions in identifiable places. Establish a
shared read-only assessment at each owning application boundary, then have both the Qt
presentation and execution guard consume it. Reuse existing replacement lifecycle and
review state rather than building another state machine.

Before implementation, enumerate all entry points and relevant invalidation events:
selection, document/workspace changes, mirror access, gesture start/end, blocked-save
changes and candidate lifecycle. Retain the current product rules. Any proposed rule
change needs a separate explanation and user discussion.

Acceptance for that increment includes UI/API agreement, immediate availability changes
after relevant events, preserved reasons, no computation or authored changes from status
reads, safe undo/cancel and unchanged replacement/review semantics. Check profiler
notification counts if the integration expands refresh work. Background/offscreen evidence
does not establish interactive desktop acceptance.

## Completed 0.4.0 handoff

- Main merge: `9363267`, pushed to `origin/main`.
- Detailed qualification: [skin task](skin-040.md).
- Canonical executable: `dist/0.4.0/AnthroForge.dist/AnthroForge.exe`.
- Runtime build stamp: `0992a512a06813e64487e6a7075f5f4cca0d240a`; subsequent release
  changes were documentation only.
- Packaged native DLL SHA-256:
  `639cdc5520a9448cb43bc9623f92b1f481e2be6d507baa4d1f231758e11e086b`.
- All 31 portable checks passed with the optimized DLL under a minimal environment.
- Final source archive: `dist/AnthroForge-0.4.0-source.zip`, 47,329,280 bytes,
  23,971 unique entries, valid CRCs. Selected optimized source files match the merged
  commit after newline normalization. SHA-256:
  `c115e6ff7048e67b3f79de4d8a90803235ba8946747f951fa145785f02b48f62`.
- Local evidence: `build/skin-040/portable-optimized/portable-check.json`,
  `build/skin-040/source-archive-check.json`, and
  `build/skin-040/whole-body-comparison/review.html`.

The full-body comparison matched the addon exactly. Shared banding and 18 non-manifold
edges were accepted for 0.4.0, not repaired. Acceptance does not authorize a new algorithm
or policy. Preserve the user's requirement to discuss such changes before implementing.

## Next actions and recovery

1. Incorporate any answer about 0.4.1 priorities; preserve the confirmed provider direction.
2. Complete caller/event mapping for the first increment, then implement shared assessment
   and desktop integration with focused contract tests.
3. Expand only where the inventory establishes duplicated rules or missing shared reasons.
4. Run relevant headless and background desktop checks, and qualification before release.

Preserve the unrelated root `__init__.py`. No new artifacts belong in WIP_models. The
optimized local native build used for 0.4.0 is
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`; `build/dev` contains an
older DLL and must not be mistaken for the qualified release. Follow normal development
setup for new runtime work rather than assuming a temporary directory exists on Cloud.

The containing commit identifies this checkpoint. Inspect history and remote reachability
before resuming; keep one active writer and preserve unrelated changes.
