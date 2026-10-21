# Reuse geometry already valid for confirmed placement

- Task branch: `codex/confirmed-query-reuse`
- Integration branch: `main`
- Starting revision: `c8751c3`
- Status: in progress
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Qualify original geometry against the complete confirmed-placement policy, then reuse
it when no cleanup is required. Otherwise retain the existing exterior Boolean build.
No user option, change to inflation, new release number or weakened placement rule.
Preserve cache ownership, temporary closure, original material bindings, cancellation,
dispatch/revision checks and background-only validation. Deliver the canonical 0.2.3
application and source archive after qualification.

## Findings and approach

The current native query always remeshes intersections, classifies exterior cells and
builds a new prepared mesh on a cache miss. The preceding read-only experiment measured
2.0/5.4 ms detection/full extraction on a clean radial mesh, 3.0/11.8 ms on the actual
clean tissue base, and 5.3/670 ms on intersecting tissue. Detection alone cannot exclude
sealed cavities; the nested-shell fixture has no crossings but requires removal of its
inner shell. Initial hypothesis: native topology/intersection/exterior qualification can
reuse the accepted source and its acceleration structure while preserving all rules.

Native Boolean code owns geometric eligibility; the shared surface-query adapter owns
source/closure correspondence and retaining the original resource. Python retains its
existing bounded cache and application callers. Any unproven case uses full cleanup.

## Current implementation and verification

Shared native qualification and original-mesh reuse are implemented. Conservative
topology checks route duplicate/degenerate/nonmanifold inputs to the existing builder;
exact predicates and exterior-cell classification protect crossing/cavity/orientation
semantics. Source/closure correspondence must cover every original face unchanged.
The current 63 targeted tests and five native contracts pass, including actual compact
crossed tissue, Fiber/Anchor material binding and authored-snapping lifecycle cases.

Found and corrected a related existing cache bug: query accounting called the
draft-only storage function on prepared meshes, silently returning zero. A scoped
native accounting operation now includes prepared allocations and counts aliases once.
Byte eviction, oversized bypass and retained leases are covered by regressions.

## Remaining work

1. Compare actual query geometry and native timing against the previous packaged build.
2. Run the development/portable gates and independent ownership review.
3. Finalize release artifacts,
   update computation history and release evidence, checkpoint/push and integrate.

Prior experiment is local-only under `build/boolean-prefilter-probe`; actual source is
`E:/development/WIP_models/tissue_create.anthroforge`, unchanged. Other production files
are read-only. Preserve the unrelated root `__init__.py`. No desktop input is authorized.
