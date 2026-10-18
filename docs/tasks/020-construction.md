# AnthroForge 0.2.0 construction objects

- Task branch: `codex/020-construction`
- Integration branch: `main`
- Starting revision: `b539697`
- Status: in progress; not release-ready
- Last updated: 2026-10-18, Europe/Bucharest
- Active writer: local desktop implementation chat

## Outcome and acceptance

Implement the approved [0.2.0 specification](../specification_020.md) and
[implementation plan](../implementation_020.md). Includes first-class curves,
reference images, fibers and curve-based surfaces in desktop and headless use.
Muscles and soft tissues belong to 0.2.1. Preserve the unrelated root `__init__.py`.

## Current state

Starting from the validated 0.1.9 release. Documentation consolidation is underway.
No 0.2.0 feature implementation or release qualification is complete yet.
Existing curves are embedded inside primitives; object lookup assumes SCPs.
The current coordinator, attachment kernels, Issues, profiler, transactions and
staged renderer must be extended at their owning boundaries, not duplicated.

## Verification

Read-only inspection completed; `main` and fetched `origin/main` both at `b539697`.
The previously recorded 541-test baseline has not been rerun in this task.
No visible applications or desktop input permitted while the user is gaming.
Use background/offscreen checks and state their limits.

## Next actions and blockers

1. Consolidate authoritative specifications and remove active contradictory clauses.
2. Implement and test typed objects, relationship policies, path inputs and schema 3.
3. Continue the ordered integration milestones in the implementation plan.
4. Run native/parity, headless, offscreen and portable release qualification before merge.

## Recovery inputs

Normal Windows environment and native toolchain already exist in this checkout.
Addon migration reference: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Original geometry references remain under `E:/development/WIP_models`; do not commit
large source assets. Copy compact reproducible fixtures with source provenance.
Push every coherent checkpoint; incomplete work stays on this branch.
