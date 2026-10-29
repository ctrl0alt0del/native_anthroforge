# Painting System — Step 1

- Task branch: `codex/painting-system-step1`
- Integration branch: `main`
- Starting revision: `713d963ecc5cad9aad939141acc140a73180324e`
- Status: implementation in progress
- Active writer: local implementation session
- Last updated: 2026-10-30

## Outcome and acceptance

Implement the confirmed shared Painting System, migrating tissue weights and collagen.
Preserve numerical kernels, existing controls, one-stroke-at-a-time interaction and
one-action undo. Keep schema 9 and version 0.4.3. Muscle Paint, outer-region painting,
world-width brushes, envelopes and transient painting history are separate increments.

## Decisions and relevant files

The application owns stroke/preview/finalization state per editing context. Explicit
consumer adapters own effects. The existing coordinator remains the only scheduler;
native painting calculations and bounded projection cache remain unchanged. Legacy
inspection and commit operations delegate to the same service. Desktop becomes an adapter.

## Current state

Shared core/application stroke contracts, explicit consumers, headless operations,
coordinator finalization, legacy adapters and desktop migration are implemented.
Native numerical code is unchanged. Follow-up hardening, style/type checks, save
coordination, resource/performance evidence and packaging remain unfinished.
Primary checkout contains unrelated unfinished assembly changes;
work occurs in `build/painting-system-step1` and must not stage those changes.

## Verification

Focused native/legacy tests: 14 passed. Offscreen desktop painting tests: 6 passed.
New shared lifecycle tests: 20 passed, including finish-before-preview, undo/redo,
cancel, changed baseline, paging, no-op, limits and Qt-free execution. Style/type and 15-line checks now pass. Save coordination regression fixed through
the shared admitted-publication edit boundary. Sixteen further lifecycle cases pass
(resource release, delayed cancellation, exact candidate reuse, failure and contexts).
Eight numerical parity matrix cases and pending-save/export checks also pass.
Hidden GPU captures exist under build/painting/visual; no physical-window interaction.
Full gate is running (native build/CTest/style complete; full pytest in progress).
Required: full development gate; dense
and 96-muscle performance comparison; offscreen images; relocated portable checks.
No interactive desktop evidence may be claimed.

## Next actions

1. Complete numerical/client parity matrix and representative profiling.
2. Run full development gate and hidden-render/relocated portable qualification.
3. Record evidence and ownership review; merge only validated work.

## Recovery inputs

Primary repository and reusable environment/native builds: `E:/development/anthroforge`.
No production anatomy files may be modified. Numerical algorithms must remain unchanged.
The containing commit identifies this checkpoint; inspect remote reachability.
