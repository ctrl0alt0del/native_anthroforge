# AnthroForge 0.4.1 skin audit completion

- Task branch: `codex/release-041`
- Integration branch: `main`
- Starting revision: `9363267` (qualified 0.4.0 merge)
- Status: in progress; seven audited skin gaps authorized for implementation
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local desktop chat

## Outcome and acceptance

The user accepted 0.4.0, requested its merge into main, and requested starting 0.4.1.
The merge is complete. On October 28, the user authorized implementing all seven skin
audit findings below according to the engineering guidelines. This is the current scope.
The previously confirmed next-version direction is broader use of operation-specific
status providers, following SkinStatusProvider. See
[architecture](../architecture.md#shared-operation-status-providers) and
[roadmap](../roadmap.md). The provider inventory below is retained for later integration;
do not displace the newly authorized skin corrections with that generic refactoring.

## Authorized skin work, ownership and acceptance

1. Restore addon reference preparation: prefer the draft envelope, reduce it with the
   existing Blender Decimate subset to approximately 64,000 triangles, and tetrahedralize.
   Preserve explicit initialization without an envelope by using topology as in the addon.
   Application owns source selection/read dependencies; native code owns geometry.
   Compare actual proxy input with Blender before connecting the production path.
2. Complete final-deformation diagnostics: report native convergence/inversion/embedding
   and contact-motion findings, restore final intersection/baseline comparison and sampled
   anatomy clearance. Numerical queries stay native; publication/Issues consume retained
   reports. Findings remain advisory, never a new repair or rejection rule.
3. Restore achieved subtree topology budgets and the addon's 20% deviation warnings.
   Native code counts output ownership; application maps counts to named budget regions.
4. Restore checksummed persistent FAST weight reuse with owned atomic disk-cache IO.
   Preserve solver settings and in-memory preparation; invalid/unavailable cache falls
   back to actual computation. Prove reuse across new preparations/processes.
5. Correct effective inherited gap and Auto collagen presentation through shared resolved
   settings. Preserve authored override values, scalar defaults and one-action undo.
6. Add the addon's one-action draft field Reset Defaults through a shared command.
7. Display active fitted-bone count and moving-region validation error already calculated
   by the fitter, alongside the existing whole-mesh measurements.

Audit evidence: with document gap 2%/25%, the UI showed 0.5%/100% while capture correctly
used 2%/25%. Auto Ear collagen showed scalar 1 while capture used 0. A synthetic report
with 80 FAST steps, negative proxy Jacobian, outside embeddings and motion violations
generated no Issues. Reference preparation used topology directly; retained FAST files
were temporary. No production code was changed during the audit.

Preserve approved physical source exclusions, tissue-surface preference, both-side
sampling, topology identity, retained attachments, cancellation and save/undo semantics.
Any further algorithm or policy change requires user discussion before implementation.
Use background/offscreen checks, native/addon comparisons, the development gate and one
canonical portable release. Store temporary evidence under `build/skin-041`, not WIP_models.

Status assessments must stay read-only, share application policies with command execution,
and use existing notifications. Preserve operation-specific reasons and warnings, workspace
editability, read-only mirrors, transaction rules and execution-time revalidation. Do not
introduce a universal status manager, polling, or a second authoritative eligibility store.

## Current state and initial inventory

Runtime integration is in progress. Shared effective settings/reset/fit summaries,
reference source selection and Decimate, native budget counts, persistent FAST weights,
and final diagnostics are connected. Release version changes follow qualification;
schema 7 remains sufficient for these corrections.

Checkpoint evidence: native build and six CTests pass. The dedicated reference adapter
matches Blender exactly on 4,481,616 torso triangles, reduced to 64,000 (33.931 s app,
35.416 s Blender, single runs). Match Blender's eight edge-ordering partitions: a four-thread
oracle produced different collapse order. Below-target float conversion and the reference
adapter's absence of topology's 1% floor are covered separately.
Captured addon intersection, contact, clearance and ownership examples pass native parity.
FAST weights survive a fresh process with identical outputs; corrupted checksums, invalid
metadata and unavailable storage fall back to computation. The broad skin suite exposed a
NumPy boolean serialization defect in new FAST metadata; corrected and rechecked.
The development gate passes: 2,598 Python tests, six native CTests, native style, Ruff,
formatting, mypy and doctor. An additional retained-report reload/no-mutation test passes.
Offscreen actual-QML checks cover inherited values, Auto collagen, reset/undo, fit controls
and retained diagnostic inspection. Hidden GPU views show the accepted whole-body result.

Whole-body qualification uses the saved 58-SCP/96-tissue assembly. Reference construction
takes 83.339 s; the unchanged-input update takes 2.091 s. These are profiled observations
with other checks active, not controlled speed benchmarks. Of the update, native
intersection/clearance/topology diagnostics take 188/198/40 ms and existing contact takes
1,253 ms. Initialization preserves final vertices exactly; identity update differs by at
most 3.55e-15. Anatomy, bindings and topology remain exact. A Ribs Top Radius 1.05 update
finishes in 28.397 s including all anatomy; reference and skin topology remain unchanged.
The retained topology has 4,706 crossing pairs; all 256 bounded current witnesses also
occur in the reference. This is not evidence that no additional intersections exist.
Sampled nearest-normal clearance remains a limited diagnostic, not a volume test.

Version advanced to 0.4.1 after runtime qualification. Portable packaging/checks and final
source archive remain pending. Outputs are under `build/skin-041`; do not claim release
acceptance yet. No physical interactive desktop acceptance is claimed.
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

1. Compare reference proxy inputs with the addon, then integrate source selection,
   Decimate and complete provenance; test fallback, stale publication, retry and undo.
2. Complete diagnostics and achieved budgets using shared native numerical boundaries.
3. Add persistent FAST cache and the effective-setting/reset/fitting UI corrections.
4. Run focused checks, full development gate, background GUI and portable qualification;
   update computation history, workflow, version and release evidence before integration.

Preserve the unrelated root `__init__.py`. No new artifacts belong in WIP_models. The
optimized local native build used for 0.4.0 is
`C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`; `build/dev` contains an
older DLL and must not be mistaken for the qualified release. Follow normal development
setup for new runtime work rather than assuming a temporary directory exists on Cloud.

The containing commit identifies this checkpoint. Inspect history and remote reachability
before resuming; keep one active writer and preserve unrelated changes.
