# Direct tissue creation and stable editing layouts

- Task branch: `codex/direct-tissue-stable-inspectors`
- Integration branch: `main`
- Starting revision: `6f72018aae47e85a281fb9a45311c1d8615d41f3`
- Status: in progress
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Transient calculation/status messages must not move editing controls horizontally or
vertically. Present short-lived feedback in a bottom-right overlay without stealing a
numeric drag or focus. Keep persistent diagnostics available in Activity/Issues.

Create Tissue acts on selected construction without a modal. Generic Points, Curves
and Surfaces obtain attached construction automatically using shared application
operations. Surface-to-Membrane conversion must also create Fibers from its ordinary
source curves, including when requested independently of Tissue creation. Preserve
original construction, internal sharing, editable parameters and coherent undo.

## Decisions and relevant files

The latest user request supersedes the old specification's prohibition on automatic
attached-source conversion. Existing Point/Curve conversion creates independent copies;
reuse that behavior and nearest-SCP defaults. Do not introduce UI-specific conversion,
blocking waits, numerical Python loops or partial authored graph publication.

Qt 6.12 Overlay/Popup documentation was consulted. Existing transient inspector labels
use conditional visibility inside layouts; Create Tissue still opens a source modal
for generic construction. No standalone Surface-to-Membrane command currently exists.

## Verification

Implemented shared atomic attached-graph jobs, nearest-SCP defaults, direct Tissue and
Membrane actions, multi-output creation selection, and layout-independent notices.
Initial API tests pass for Point/Curve/Surface conversion, independent shape preservation,
single undo, and missing-target rejection. Development gate and GUI not yet qualified.

Verified mixed fibers, branched seams/junction copies, failure atomicity, running
cancellation, undo/redo (including historical captures), superseding inputs/graph changes,
bone following, independence and persistence. Full pytest passed 1,393 tests before the
last source-graph regression was added.

Offscreen QML direct actions pass. Actual scrubbing with pending/long error feedback
kept the numeric field bounds `[1314,187,100,30]` at all three sampled positions,
retained focus and produced one undo action. Hidden Direct3D automatic tissue geometry
was saved and visually inspected. No visible desktop interaction was performed.

Runtime checkpoint: `7267773` (pushed). The complete `tools/check.ps1` gate passes:
1,394 pytest tests, 3 native CTests, typing, native/Python/PowerShell function/style
checks, numerical boundary/import checks and doctor. The 886 Qt deprecation warnings
are reported, not suppressed. A 1050px-wide UI layout check also passes.

Ownership/coupling review (coordinator-authored): conversion policy is separate from the
strict Tissue source contract; graph planning, native worker computation and atomic
publication have separate modules. Original numerical kernels and resource ownership
are reused. Desktop only projects shared eligibility and selection intent. Toast state
belongs to presentation and does not touch document, history or scheduler state.

The canonical `7267773` package passed the complete relocated/minimal-PATH portable
suite, including Point/Curve/Surface automatic creation and standalone Membrane creation.
Final API review then added a validation guard: omitted automatic Anchor parents cannot
silently substitute SCP geometry for a requested Tissue surface role. All 21 focused
conversion/lifecycle/architecture tests, lint, formatting and typing pass with that guard.
Repackaging and final Python regression qualification are pending for this last guard.
Build logs and hidden-render evidence are local-only under the evidence directory.

## Next actions and blockers

1. Finish/qualify the single canonical portable build and update validation records.
2. Generate the source archive, then merge/push normally.

## Recovery inputs

Preserve unrelated root `__init__.py`. Keep all GUI validation background-only.
Local evidence belongs under `build/direct-tissue-stable-inspectors/`.
