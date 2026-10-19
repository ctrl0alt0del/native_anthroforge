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

## Recovery

Preserve untracked root `__init__.py` and original
`E:/development/WIP_models/solver_test.anthroforge`. Never use visible test windows or
desktop input. Work directly without delegation. Push coherent checkpoints before long
checks; implementation and validation are not yet complete.
