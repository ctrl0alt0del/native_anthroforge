# AnthroForge 0.2.1 implementation

- Task branch: `codex/021-curve-workflows`
- Integration branch: `main`
- Starting revision: `58a28a3`
- Status: implementation in progress
- Last updated: 2026-10-19, Europe/Bucharest
- Active writer: local desktop chat

## Outcome

Implement [0.2.1](../specification_021.md): viewport creation icons, click/Shift-click
placement, removal of redundant loft entry, automatic obstacles with optional exclusions,
all authored conversion points by default, scalable 100+ item editors and concise solver
controls. VCP work remains 0.2.2. Follow engineering guidelines and background-only QA.

## Delivery sequence

1. Shared routing/default/eligibility/dependency contracts and native capture ownership.
2. Reusable bounded selection UI, conversion/settings integration, toolbar and placement.
3. Native/headless, lifecycle, 100-item interaction and profiler qualification.
4. Version/docs/examples, full gate, relocated portable build, source archive and merge.

## Current evidence

Baseline 0.2.0 correction passes 877 tests and portable/offscreen acceptance. Its routing
inputs are explicit; geometry capture rebuilds selected colliders/snapshot each solve.
The addon automatic root-associated SCP policy and cached spatial queries were inspected
during specification. Reuse native infrastructure; do not add Python geometry loops.
Qt ListView reuse and proxy-model APIs were researched before implementation.

## Checkpoint: routing contracts

Implemented AUTO/MANUAL obstacle policy with optional exclusions. Explicit obstacle
arguments retain manual intent. The graph adds automatic inputs then removes only
automatically introduced cyclic edges; explicit cycles remain errors. A structural
scene-membership read detects new/deleted surfaces and preview staleness. Ordinary pose
and geometry revisions remain dependencies, including distant obstacles moving inward.
Curve conversion defaults to all authored points; explicit empty selection remains invalid.

Full pytest: 883 passed, 9 existing Qt warnings (build/check-021-initial.log). Mypy passes
on 154 core/application files. New tests cover scene additions, pose changes, exclusions,
deletion/undo, persistence, cyclic consumers and preview staleness. Existing contact/warm
fixture explicitly starts in MANUAL to preserve its original no-obstacle regression case.
UI, native capture reuse/performance, broader lifecycle cases and release remain unfinished.

Native capture checkpoint: immutable collision worlds now have independent native leases
and an engine-owned 64 MiB / 8-entry cache through shared bounded resource-cache machinery.
Profiler observes capture/solve separately, cache actions and retained capture capacities.
Native contract tests pass; 100-cube profile captures once (0.60 ms) across 8 solves
(mean 72.34 ms versus prior uncached 72.64 ms). This establishes reuse, not a meaningful
whole-solve speedup: numerical solving dominates this fixture. Reuse/eviction, concurrent
solves, cancellation and parity with uncached routing pass. Native style gate also passes.

## Checkpoint: interaction implementation

Implemented five viewport icons, semantic continue-placement modifier, plain-click finish,
closed-draft protection and one-action undo. Added reusable incremental/proxy choice models
and bounded virtualized/searchable editors, scoped bulk actions, locked required rows,
hierarchy context, point focus, all-authored defaults, contextual obstacles and Advanced
budgets. Removed redundant loft menu; generic surface API remains.

Full-QML offscreen 120-point/120-obstacle editor checks pass, including defaults, required
points, duplicate names, filtering, scroll retention, preview/accept and undo. Captures
under `build/021-curve-workflows` inspected with real fonts. Software offscreen captures
validate controls/layout, not Quick3D geometry. Routing editor and targeted gesture/model
tests pass. Profiling exposed repeated candidate graph construction; descriptions now
reuse structural graph identity. Measured obstacle binding inclusive total fell from
127 ms to 64 ms across 38 refreshes in serial runs; not a general responsiveness claim.
Full regression, lifecycle additions, hidden GPU geometry checks, packaging and release
documentation remain pending. Versions are still 0.2.0 until qualification.

## Recovery

Preserve untracked root `__init__.py` and original
`E:/development/WIP_models/solver_test.anthroforge`. Never use visible test windows or
desktop input. Work directly without delegation. Push coherent checkpoints before long
checks; implementation and validation are not yet complete.
