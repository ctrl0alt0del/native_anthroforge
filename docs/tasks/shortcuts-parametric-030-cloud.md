# 0.3 shortcuts and Parametric — cloud continuation

- Task branch: `codex/shortcuts-parametric-030-cloud`
- Parent feature branch: `codex/shortcuts-parametric-030`
- Starting revision: `e7d464e3a4cf401249b6c96be2eb8eb5387b7fb6`
- Status: implementation in progress; focused cloud baseline passes
- Last updated: 2026-10-22 UTC
- Active writer: Codex Cloud, direct work

## Outcome and acceptance

Continue the paused 0.3 implementation on the separate cloud branch requested by
the user. Preserve the desktop feature branch and its checkpoint history. Keep
incomplete work on this branch; no release or integration is implied by a checkpoint.
Follow the [confirmed specification](../specification_030.md) and
[implementation plan](../implementation_030.md).

## Decisions and relevant files

- The latest [desktop handoff](shortcuts-parametric-030.md) describes the pause;
  its newest Current state section takes precedence over older progress entries.
- Incorporate the validated pipeline repair from `main` before cloud qualification.
- Preserve ordinary-property versus shortcut-wrapper behavior, inferred ownership,
  native numerical evaluation, shared scheduling, history and resource ownership.
- All GUI work remains background/offscreen. Runtime version remains 0.2.4 until
  all release acceptance is demonstrated.

## Current state

The cloud branch starts at the exact pushed desktop pause checkpoint. Main's
validated CI fixes are reconciled here; the only merge conflict was overlapping
computation-history additions. Both are retained, with the desktop expression
record reassigned CH-049 to preserve main's published CH-045. No desktop branch
changes are made. Formatting leftovers in the lattice-reference guard and resource
accounting are corrected; the guard also complies with the function-size limit.
New public-operation tests cover lattice input-reference locks (including disabled
formulas), escaped property ports, variable renaming/removal, generated-coordinate
feedback with an independent valid formula, and failure-placeholder lifetime/recovery.
Copy review found that shared geometry copies omit shortcut/formula state. The next
implementation is coherent copying/remapping at those existing copy boundaries.

## Verification

- Linux native build and all five CTests pass after reconciliation.
- Ruff lint and formatting pass; mypy passes all 361 source files.
- `pytest tests/test_expressions.py tests/test_shortcut*.py tests/test_driving*.py
  tests/test_parametric*.py tests/test_architecture.py -q`: 109 passed.
- The initial focused run found one pre-existing 16-line function in the paused
  guard; the corrected run passes. Local logs are ignored under `build/core/`.
- Full portable gate, native style and release qualification remain pending.
  Earlier desktop results retain their original scope in the desktop handoff.

## Next actions and blockers

1. Complete shared shortcut/formula copy and reference remapping contracts.
2. Qualify policy editor, catalogue coverage and remaining paused interactions.
3. Complete missing implementation/contracts from the pause, then run the full
   portable gate, applicable offscreen checks and GitHub core jobs.
4. Push coherent implementation and evidence checkpoints on this cloud branch.

## Recovery inputs

Source `tools/cloud/environment.sh` in new shells. The cloud workspace already has
the portable toolchain and dependencies from the CI repair. The host blocks the
configured Boost archive host; the verified official Boost 1.89.0 GitHub no-docs
archive is unpacked under ignored `.tools/boost-1.89.0` and selected in the local
CMake cache. See [pipeline recovery](fix-ubuntu-pipeline.md#recovery-inputs).
Repository dependency URLs/digests remain unchanged.

Original Blender assets under `E:/development/WIP_models`, desktop captures and
Windows GUI/portable qualification are not available automatically here. Checked-in
research, fixtures and provenance are available. Any remaining asset-based parity
or Windows release evidence must be reported explicitly before release.
