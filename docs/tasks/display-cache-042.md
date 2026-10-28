# Implement measured R11 display updates, then R09 cache budgeting

- Task branch: `codex/display-cache-042`
- Integration branch: `main`
- Starting revision: `b7c5d99`
- Status: in progress
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and acceptance

Implement the measured display/scene-publication improvements first, then shared cache
ownership, aggregate cost-aware retention and bounded FAST disk storage. Follow
[engineering guidelines](../engineering_guidelines.md) and the
[profiling evidence](profile-cache-display-042.md). Keep geometry algorithms, attachments,
undo history, scheduling contracts and staged display/picking correctness intact.

## Decisions and relevant files

- R11 belongs to incremental presentation projections, displayed picking inputs and
  resource reachability. GPU topology changes lack evidence and are not this increment.
- R09 belongs to engine-owned cache/resource accounting and FAST cache persistence.
  Do not trim document/history owners or add in-flight work sharing (R10).
- Qt recommends batched model updates and avoiding redundant binding work:
  <https://doc.qt.io/qt-6/qtquick-performance.html>.
- Retain 0.4.2; deliver its single canonical portable package after qualification.

## Current state

R11 implemented: journal-targeted construction/tissue projection, shared frame resolution, displayed-transform reuse, coherent frame publication, and immutable-document reachability caching. Focused regression and architecture checks pass (22 tests); lint and mypy pass. First hidden production capture: 24.167 s, 549 construction visits versus baseline 132,498; exact geometry/pose/attachment fingerprint equality. Full paired timing, delivery checks and R09 remain pending.

## Verification

Pending focused regression, paired production profiling, development gate, hidden GUI
and portable checks. No visible desktop interaction.

## Next actions and blockers

1. Implement and qualify incremental construction projection, picking and reachability.
2. Implement native resource receipts, aggregate retention and FAST disk budgeting.
3. Compare measured workloads, exact/canonical geometry and attachment fingerprints.
4. Run delivery checks, update evidence and package, merge and push.

## Recovery inputs

Use `ANTHROFORGE_NATIVE_LIBRARY=C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native/bin/af_native.dll`
and `AF_NATIVE_BUILD` pointing to that build directory. The default `build/dev` DLL is
stale. Production fixtures and baseline profiles are documented in the profiling task.
Keep new artifacts under ignored `build/display-cache-042`; preserve root `__init__.py`.
