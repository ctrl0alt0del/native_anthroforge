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

## Recovery

Preserve untracked root `__init__.py` and original
`E:/development/WIP_models/solver_test.anthroforge`. Never use visible test windows or
desktop input. Work directly without delegation. Push coherent checkpoints before long
checks; implementation and validation are not yet complete.
