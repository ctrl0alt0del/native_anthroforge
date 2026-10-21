# Preferences and ROUTED backends — 0.2.3

- Task branch: `codex/preferences-routing-023`
- Integration branch: `main`
- Starting revision: `e703c68`
- Status: in progress
- Last updated: 2026-10-21
- Active writer: desktop chat, direct work

## Outcome and acceptance

Deliver Preferences with a persistent Custom / PIQP choice for ROUTED curves and
fibers, backed by the shared headless application API. Release 0.2.3 with one canonical
portable distribution and companion source archive. Background-only validation.

## Decisions and ownership

- Default remains Custom; PIQP means the sparse backend qualified in the
  [benchmark](routing-piqp-benchmark.md), using existing pinned PIQP 0.6.4.
- Preferences belong to the application, outside project revisions and undo.
- Native per-invocation options select the QP implementation; no ambient thread-local
  backend switch, fallback, Python numerical loop, or separate worker pool.
- Preserve routing planning, exact pins, corner retention, collision acceptance,
  cancellation, dependent surfaces and attachments. Document computation changes.
- User confirmed future calculations only; preserve existing results and running work.

## Current state

Native per-invocation backend, sparse adapter, preference storage and desktop editor
implemented. Custom remains default; future-dispatch semantics confirmed. Both ordinary
path jobs and conversion previews
capture preferences at dispatch. Reports retain backend provenance. Shared reference
fixtures moved into a test helper used by the benchmark and production qualification.

Also corrected the measured Custom active-set cap mismatch: do not change the active
list after the final candidate solve. This preserves matching multipliers/candidate and
removes a possible out-of-bounds downstream read; no acceptance checks weakened.

## Verification

50 focused tests passed: both backends on 18 compact cold/warm fixtures, independent
clearance/pins/layout, concurrent calls, cancellation, preference persistence, running
and queued dispatch, Manual mode, saved backend provenance, and function limits.
Development gate passed: 1,494 tests, four native contracts including the active-set cap,
mypy, native/script style, lint/format and numerics. Subsequent explicit ABI-preserving
entry points and additional preview/failure/ABI checks pass 53 focused tests, mypy/style.
Eleven material/architecture checks and actual offscreen Preferences UI pass. No native
desktop input was used. Final full-suite check and portable release remain pending.

Production comparison: 22 inputs, six alternating AB/BA trials per cold/warm/backend
(528 routes), full-route timings including setup. The heavy 256-sample attached warm
case is 325.55 ms Custom / 61.51 ms PIQP; actual four-point/24-sample cold fixture is
9.21 / 11.82 ms. These are local timings, not UI latency. 21/22 inputs pass independent
clearance for both backends; the same historical skull pin slightly inside Cranium
remains the known counterexample. All pins/finite/correspondence checks pass. Overlaid
actual route geometry was inspected. Local evidence: `build/preferences-023/backends.json`
and `routes.png`; optional skull input is not committed. No user projects modified.

## Next actions

1. Complete final gate and package 0.2.3.
2. Qualify relocated package, headless reports and offscreen Preferences.
3. Finalize documentation/source archive, merge and push.

## Recovery inputs

Use normal Windows setup. Benchmark fixtures are under `tests/fixtures/routing`;
optional local skull capture is `build/skull-routing-inputs.json`. No interactive
desktop acceptance is authorized by this task. Read current diff before resuming.
