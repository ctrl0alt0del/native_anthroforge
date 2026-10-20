# Direct tissue creation and stable editing layouts

- Task branch: `codex/direct-tissue-stable-inspectors`
- Integration branch: `main`
- Starting revision: `6f72018aae47e85a281fb9a45311c1d8615d41f3`
- Status: complete
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
API tests pass for Point/Curve/Surface conversion, independent shape preservation,
single undo, and missing-target rejection. Development, offscreen GUI and portable
qualification are complete.

Verified mixed fibers, branched seams/junction copies, failure atomicity, running
cancellation, undo/redo (including historical captures), superseding inputs/graph changes,
bone following, independence and persistence. Full pytest passed 1,393 tests before the
last source-graph regression was added.

Offscreen QML direct actions pass. Actual scrubbing with pending/long error feedback
kept the numeric field bounds `[1314,187,100,30]` at all three sampled positions,
retained focus and produced one undo action. Hidden Direct3D automatic tissue geometry
was saved and visually inspected. No visible desktop interaction was performed.

Initial runtime checkpoint: `7267773` (pushed). The complete `tools/check.ps1` gate passes:
1,394 pytest tests, 3 native CTests, typing, native/Python/PowerShell function/style
checks, numerical boundary/import checks and doctor. The 886 Qt deprecation warnings
are reported, not suppressed. A 1050px-wide UI layout check also passes.

Ownership/coupling review (coordinator-authored): conversion policy is separate from the
strict Tissue source contract; graph planning, native worker computation and atomic
publication have separate modules. Original numerical kernels and resource ownership
are reused. Desktop only projects shared eligibility and selection intent. Toast state
belongs to presentation and does not touch document, history or scheduler state.

Final runtime: `be7e506f0dd6c5cc99d4611e3204eb66f38142f9` (pushed). Final API review added
a validation guard: omitted automatic Anchor parents cannot silently substitute SCP
geometry for a requested Tissue surface role. The final source passes 1,397 pytest
tests, lint, formatting and typing. Its rebuilt canonical package passes the complete
relocated/minimal-PATH suite, including Point/Curve/Surface automatic creation and
standalone Membrane conversion. Copied and canonical executable hashes match:
`5ba07cb4c8b1a6b21bb238debe77e72e66313e20fbd3c22ca587b72499884f2b`.
Native DLL hashes also match development. Build logs and hidden-render evidence are
local-only under the evidence directory; no foreground/manual acceptance is claimed.

## Next actions and blockers

No implementation blockers remain. The canonical release and companion source archive
contain the validated runtime and updated documentation. Preserve checkpoint history
when merging/pushing this task into main.

## Recovery inputs

Preserve unrelated root `__init__.py`. Keep all GUI validation background-only.
Local evidence belongs under `build/direct-tissue-stable-inspectors/`.
