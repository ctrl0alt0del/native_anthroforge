# Routed conversion failure in solver_fail1

- Task branch: `codex/solver-fail1`
- Integration branch: `main`
- Starting revision: `9cc6c7cd64ae3a0090bf3f715f434378653d441f`
- Status: investigating
- Last updated: 2026-10-20, Europe/Bucharest
- Active writer: local desktop chat, direct work

## Outcome and acceptance

Reproduce the reported failure when switching the supplied curve to ROUTED, identify
the actual rejected condition and correct the responsible implementation if defective.
Validate the original geometry and complete path, not just successful solver return.
Preserve user-authored points, original file, routing safety and retained-output semantics.
Any real authored conflict or behavior choice must be explained before choosing a repair.

## Current state

Created an isolated copy of the project under ignored `build/solver-fail1/`.
Project SHA-256: `61df6958b6d63f8974d88935007ee9d727504af1e89c1ffe252761c10f2e51b2`.
The original was not modified. No cause is established yet.

## Verification

Inspection through the shared CLI succeeds; document revision 208.
Official libigl winding-number/signed-distance and CGAL path documentation consulted
before investigation. Existing native route diagnostics and regressions are the first
tools to use; no algorithm replacement is selected.

## Next actions

1. Reproduce conversion and inspect authored points, obstacle roles and native rejection.
2. Establish whether a valid path exists under unchanged authored constraints.
3. Fix the owning boundary if defective; log any computation change and qualify source,
   native, background GUI and one canonical portable package before normal integration.

## Recovery inputs

Original: `E:/development/WIP_models/solver_fail1.anthroforge`.
Local copy/evidence: `build/solver-fail1/`. Normal `.venv` and native build environment.
Keep all validation background-only and preserve unrelated root `__init__.py`.
