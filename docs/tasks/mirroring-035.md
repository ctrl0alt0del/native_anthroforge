# Mirroring 0.3.5 runtime implementation

- Task branch: `codex/mirroring-035`
- Integration branch: `main`
- Starting revision: `1696687`
- Status: in progress; not release-qualified
- Last updated: 2026-10-24, Europe/Bucharest
- Active writer: local Codex session

## Outcome and acceptance

Implement [the confirmed specification](../specification_035.md) through
[the integrated plan](../implementation_035.md), desktop and Qt-free headless clients.
Strict read-only source reflection is invariant. No independent mirror solvers,
tree nodes, per-object mirror action, detachment or counterpart migration.

## Current state

Read specifications, engineering rules and current typed model. Starting from main;
unfinished `codex/parity-workflows-034` and unrelated root `__init__.py` are preserved.
Research: Qt 6.12 material front faces use counterclockwise winding; reflection/query
and render orientation must be handled explicitly, not hidden with double-sided shading.
Foundation implementation now includes typed rules/instances, cached relationship
resolution, shared provider references/transforms, read-only guards, rule/inspection
commands and schema-6 relationship storage (reads 4/5/6). Source assets are reused.
Initial desktop rule controls and viewport projection are in progress, not qualified.
No independent mirror solvers or authored tree nodes are introduced.

## Next actions

1. Trace provider/reference, persistence, mutation and viewport ownership boundaries.
2. Implement foundations with shared API and desktop controls and contract tests.
3. Integrate reflected queries, relationships, symmetric constructions and lifecycle.
4. Qualify correctness/performance/packaging; update versions only when complete.

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
