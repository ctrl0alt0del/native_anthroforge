# Mirroring 0.3.5 runtime implementation

- Task branch: `codex/mirroring-035`
- Integration branch: `main`
- Starting revision: `1696687`
- Status: complete; runtime and portable qualification passed
- Last updated: 2026-10-24, Europe/Bucharest
- Active writer: none after validated integration

## Outcome and acceptance

Implement [the confirmed specification](../specification_035.md) through
[the integrated plan](../implementation_035.md), desktop and Qt-free headless clients.
Strict read-only source reflection is invariant. No independent mirror solvers,
tree nodes, per-object mirror action, detachment or counterpart migration.

## Current state

0.3.5 is implemented and qualified. The final development gate passed 2,102 tests,
five native CTests, typing/style/function limits and numerics. The full minimal-PATH
portable suite passed on the canonical executable, followed by an extended selected-
mirror bilateral capture which was visually inspected. No interactive acceptance claim.
Runtime binary source is pinned to clean `11a93e8`; later changes are documentation
and an external qualification-tool camera. Source assets and unrelated work are preserved.

## Delivery and continuation

- Canonical executable: `dist/0.3.5/AnthroForge.dist/AnthroForge.exe`.
- Companion final source: `dist/AnthroForge-0.3.5-source.zip`.
- User workflow/evidence: [mirroring_035.md](../mirroring_035.md).
- Gate: `build/mirroring-035-gate-final.log`; portable: `build/035-portable/portable-check.json`.
- Source/mirror GPU/profile evidence: `build/035-mirroring/`.
- Validated task branch is ready for normal integration into main; Git history determines
  whether that merge has already happened. No runtime implementation remains pending.
- Next work is user testing. Do not revive unfinished 0.3.4 or migrate old counterparts
  implicitly. Root `__init__.py` remains unrelated and untracked.

## Verification

`pytest tests/test_mirroring.py tests/test_construction_objects.py -q`: 28 passed.
These cover hierarchy/plane identity, exact provider transforms/resource reuse, basic
read-only behavior, history, persistence and reuse after result publication.
Added instance-aware Fiber/Anchor capture, plane-input graph leaves and Anchor update
without rebinding, structural Issues, shared-target inspection, source/mirror display
modes and removal blockers. Desktop tests confirm read-only viewport selection without
tree entries. Source/role reference and schema expectations are updated intentionally.
Initial full regression: 2,063 passed; failures were the function-size guard and two
reference/schema expectations. Focused fixes now pass 26 tests including architecture,
mirror, desktop, point-interaction and tissue-contract tests. Mypy passed at the earlier
foundation checkpoint; rerun after subsequent changes is required. CH-071 records the
actual computational boundary change. Full rerun, complete provider integration,
symmetric construction, stacking and release acceptance remain pending.
Native symmetric-half path expansion and mirrored-row ordering now build successfully;
all five native CTests passed. Seven source-construction tests cover Bézier/polyline/
routed exact half reflection, invalid input rollback, one-row surface creation,
direct mirrored-row updates/undo and persistence. Mirrored provider graph aliases now
let original routed curves avoid reflected obstacles; a dedicated case passes.
Further work remains on stacking providers, full attachment/query/presentation coverage,
seam edit constraints, native style, profiling, offscreen visuals and packaging.
Checks remain background-only; do not claim interactive acceptance.
Checkpoint coherent increments and push before long checks or interruptions.

## Recovery inputs

Use existing .venv, native build/load infrastructure and tools/check.ps1.
No new production anatomy assets belong in Git. Prior source inventory is in the plan.

### Relationship checkpoint

Mirrored accepted-final providers participate in original stacking without mirror writers.
SCPs can retain material attachments to mirrored geometry; native parent-first propagation
applies the current reflection frame and plane changes preserve the stored binding.
The focused mirror, desktop, symmetric construction and stacking suite passes 24 tests;
mypy passes 400 modules. Latest native build passes all five CTests.
A deliberately shifted provider is incompatible with 23 fixed receiver boundary points
(maximum 0.01 m deficit); it remains a rejected constrained configuration, not evidence
for relaxing structural preservation. Full release qualification remains pending.
Remaining: seam editing, complete instance presentation/inspection, lifecycle/removal,
profiler/offscreen evidence, full development gate and one canonical portable build.

### Interaction and symmetric construction checkpoint

Added cached instance projection, independent visibility, Point/Anchor and control markers,
read-only source inspectors/shortcuts, searchable removal blockers and retained conflict
frames (including schema-6 persistence). Symmetric authored endpoints are constrained
natively without changing their half-path's public closed-Curve/Fiber contract. Native
field interpolation now supports automatic open tails for internal half-path capture;
ordinary authored open Fibers still require both endpoint bindings.
The 32 focused tests plus the function-length guard pass. A preceding full regression
passed 2,085 tests with only the then-unfixed size guard failing. Latest native build
passes five CTests. Headless desktop smoke loaded without QML warnings.
Hidden-GPU qualification and runtime profile are in build/035-mirroring. Hover/click
agree on mirrored tissue; four plane edits preserve exact source geometry (121–128 ms
including settle/refresh/readback). Trace has no inflation/routing/relaxation calls in
this plane-only workload. An actual visual inspection caught read-only dimming and
negative-transform winding; presentation now separates dimming and reverses render-only
triangle indices. Reinspected source/mirror images show consistent shading. No reflected
anatomical mesh asset is generated. Release and packaging remain pending.

### Query and shared-junction checkpoint

A previous full gate passed 2,090 tests, five native CTests and style/type checks;
newer additions require a final rerun. Focused measurement, inspection, relationship
and junction checks pass. Latest native build passes five CTests. Hidden full QML
inspection selected mirrored Tissue/Fiber/Membrane with no warnings. Source-only
plane edits reused geometry; repeat hidden-GPU timings varied 121–343 ms including
eight rendered/readback frames, settling and refresh, under uncontrolled background load.
Production read-only probe: 59 SCPs/96 muscles, 620 instances in 49 ms, settled under
0.7 s, zero new source geometry assets and no scheduler failures. WIP file not saved.
Portable release and final full gate are not yet complete.

Repeated-plane resource and Manual-source lifetime tests pass: 16 plane edits add no
mesh assets, undo restores the prior plane, and Manual mirrors retain the accepted
source until explicit evaluation. Qualification trace validation also checks absence
of independent mirror output writers and inflation/routing/relaxation calls. A final
hidden-GPU repeat measured 194–343 ms with about 47% system busy time; all observed
trials span 121–343 ms, including eight GPU frames/readbacks. No low-latency claim.


### Release candidate preparation

Runtime workflows and focused additions pass; release metadata advances to 0.3.5 for
the canonical candidate. Final all-source native/static gate remains running, followed
by full pytest/numerics. Portable qualification and integration are still required;
this checkpoint is not a release-complete claim. No new numerical dependency is added.


### Final development gate

`tools/check.ps1` passed on the release-candidate source: 2,102 Python tests,
five native CTests, typing for 405 source files, configured native/Python/PowerShell
style, function limits, numerical checks and doctor (application 0.3.5). Log:
`build/mirroring-035-gate-final.log`. Runtime code is qualified; the canonical
Nuitka executable is still building and relocated portable checks remain next.
Pinned executable source revision is `11a93e8`; later evidence edits change docs only.


### Portable release acceptance

The canonical executable built successfully. Full minimal-PATH portable checks pass,
including existing workflows and new mirroring. An explicit bilateral capture with
selected mirror also passes; actual image shows both cubes, symmetric loop and correct
reflection shading/outline. Artifacts are under build/035-portable. Final source/docs
are copied into the canonical distribution and companion source archive. All evidence
is background/offscreen; no interactive desktop or full anatomical parity claim.
Ownership/coupling review is recorded separately in the walkthrough.
