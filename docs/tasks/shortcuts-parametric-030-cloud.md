# 0.3 shortcuts and Parametric — cloud continuation

- Task branch: `codex/shortcuts-parametric-030-cloud`
- Parent feature branch: `codex/shortcuts-parametric-030`
- Starting revision: `e7d464e3a4cf401249b6c96be2eb8eb5387b7fb6`
- Status: implementation in progress; cloud baseline pending
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

The cloud branch starts at the exact pushed desktop pause checkpoint. No desktop
branch changes are made. The first work is checking the pending lattice-reference
guard and qualifying the new catalogue, policy UI, generated-curve placeholders,
formula/path dependencies and structural reference handling.

## Verification

Baseline has not yet been run on this branch. Earlier desktop counts and limits
are preserved in the desktop handoff; they are not evidence for new cloud changes.

## Next actions and blockers

1. Merge the validated main changes into this cloud branch and inspect the result.
2. Check the pending guard, rebuild native code, and run focused 0.3 tests.
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
