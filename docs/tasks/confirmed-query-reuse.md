# Reuse geometry already valid for confirmed placement

- Task branch: `codex/confirmed-query-reuse`
- Integration branch: `main`
- Starting revision: `c8751c3`
- Status: complete and qualified for integration
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

Serial complete-query comparison against the packaged `98ca740` runtime: six alternating
rounds, three uncached trials per case/backend/round, nine cases. All oriented triangle
geometry hashes match across every baseline/current run. Clean actual base improves
14.895 to 8.697 ms median, radial tissue 6.014 to 4.307 ms. Dirty tissue timings overlap
normal variation; cavity qualification adds about 1.17 ms before full cleanup. Original
allocations are reused in all six eligible cases. See
[measured evidence](confirmed-query-reuse-evidence.json); no UI-latency claim.

## Final qualification and delivery

The full development gate passes **1,514 tests**, five native contracts, typing,
lint/format, function limits and numerical/runtime checks. The canonical 0.2.3 executable
at `cf02502` passes the full relocated portable suite. Added clean/cavity placement
profiles each contain one query call and four cache hits, with correct nonzero memory
accounting. Actual source/query geometry was visually inspected. Offscreen GUI and hidden
GPU rendering pass; no interactive desktop acceptance is claimed.

Ownership/coupling was reviewed directly, separately from test success. No application
caller, document revision, worker pool or presentation rule owns the geometric decision.
Final artifact identity and limitations appear in
[development validation](../development_status.md#confirmed-query-reuse-023).
Deliver one canonical distribution and source archive; integrate through the normal
validated merge/push workflow. Full logs/captures remain local under
`build/confirmed-query-reuse*`; compact measurement evidence is committed.

Prior experiment is local-only under `build/boolean-prefilter-probe`; actual source is
`E:/development/WIP_models/tissue_create.anthroforge`, unchanged. Other production files
are read-only. Preserve the unrelated root `__init__.py`. No desktop input is authorized.
