# Painting System — Step 1

- Task branch: `codex/painting-system-step1`
- Integration branch: `main`
- Starting revision: `713d963ecc5cad9aad939141acc140a73180324e`
- Status: implementation in progress
- Active writer: local implementation session
- Last updated: 2026-10-29

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
cancel, changed baseline, paging, no-op, limits and Qt-free execution. Style currently
has functions over 15 lines; initial mypy found annotation issues being corrected.
Required: full development gate; dense
and 96-muscle performance comparison; offscreen images; relocated portable checks.
No interactive desktop evidence may be claimed.

## Next actions

1. Implement immutable input contracts and context-owned service, then headless lifecycle.
2. Migrate legacy consumers and desktop; qualify behavior and resource lifetime.
3. Document API/design, profile, run gate/portable checks, and merge validated work.

## Recovery inputs

Primary repository and reusable environment/native builds: `E:/development/anthroforge`.
No production anatomy files may be modified. Numerical algorithms must remain unchanged.
The containing commit identifies this checkpoint; inspect remote reachability.
