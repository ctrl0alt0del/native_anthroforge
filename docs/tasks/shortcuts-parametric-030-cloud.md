# 0.3 shortcuts and Parametric — cloud continuation

- Task branch: `codex/shortcuts-parametric-030-cloud`
- Parent feature branch: `codex/shortcuts-parametric-030`
- Starting revision: `e7d464e3a4cf401249b6c96be2eb8eb5387b7fb6`
- Status: implementation in progress; portable validation stages pass
- Last updated: 2026-10-23 UTC
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
Shared geometry copies now retain shortcut/formula state, remapping internal controls,
references, policies, ordering and accepted values. Explicit external inputs remain
external, and copied outputs are limited to copied construction. Independence rewrites
consumer-member addresses atomically with the copied graph, including branched tissues.
[CH-050](../computation_history.md#ch-050--copy-formula-controls-with-their-construction-graph-2026-10-22)
records ownership and evidence. Driven fields now offer navigation to their controlling
shortcut, including hidden drivers. Driver, shortcut and Parametric-variable controls
share canonical/display-unit conversion. Switching a whole-valued Parametric variable
to Integer preserves its value. Existing Qt command transport already accepts integral
QML numbers and rejects fractions for integer fields; regression evidence corrected the
initial transport hypothesis. Mixed CP1252/UTF-8 bytes in Shortcuts.qml are normalized
to valid UTF-8. Runtime/schema and numerical evaluation contracts are unchanged.
The [development walkthrough](../shortcuts_030.md) documents current command signatures
and links the runnable `examples/shortcuts_parametric.json` circle/driver example.

## Verification

- Linux native build and all five CTests pass after reconciliation.
- Ruff lint and formatting pass; mypy passes all 363 source files.
- `pytest tests/test_expressions.py tests/test_shortcut*.py tests/test_driving*.py
  tests/test_parametric*.py tests/test_architecture.py -q`: 109 passed.
- The initial focused run found one pre-existing 16-line function in the paused
  guard; the corrected run passes. Local logs are ignored under `build/core/`.
- Full portable validation at `d89c8bd`: 1,845 pytest cases, five CTests, all 170
  owned native clang-tidy inputs, headless doctor/workshop and Python package/wheel
  checks pass. The initial `check_core.py --native-style` process completed through
  the workshop, then its `uv build` dependency fetch hit sandbox network denial.
  The remaining `uv build` and `tools/check_wheel.py` steps passed with network
  access; only then was the success report recorded. Logs are
  `build/core/cloud-030-full-gate.log`, `build/core/cloud-030-packaging-resume.log`
  and `build/core/qualification/passed.json`. No source change was needed for the retry.
- [GitHub run 39873326293](https://github.com/ctrl0alt0del/native_anthroforge/actions/runs/39873326293)
  passed Ubuntu and Windows on copy checkpoint `5ce4ca8`. Editor checkpoint `52eb50b`
  and documentation/example checkpoint `d89c8bd` were still running remotely at
  00:02 UTC on 2026-10-23. Later documentation-only checkpoints do not change runtime code.
  Windows desktop/portable release qualification remains pending; earlier desktop
  results retain their original scope in the desktop handoff.
- Copy baseline: four regressions failed because controls were absent; consumer
  reference remapping also failed before implementation. The corrected copy/shared
  construction/tissue/Fiber/architecture group passes 35 cases, including pending
  Manual intent and branched tissue controls. Mypy passes 363 source files.
- Editor/control/architecture group: 10 passed. Tests cover scoped policy edits,
  fractional-input rejection and hidden-driver navigation. The new
  `tools/shortcuts_editor_acceptance.py` loads production QML and property projections
  offscreen, exercises mm/degrees edits, Parametric variable type changes and locked
  generated-point count fields, and reports no QML warnings. Both editor/list captures
  are generated under ignored `build/shortcuts-editor-review/`; both captures inspected.
  This software-rendered harness excludes the native viewport and full Main window.
- The headless example completed all 15 operations. Its radius changed from 0.03 to
  0.05 metres, the formula reached `ready`, and the saved project reopened with the
  accepted 64-point closed path and no Qt imports. Log: `build/core/cloud-030-example.jsonl`.

## Next actions and blockers

1. Inspect the remaining GitHub runs for `52eb50b` and descendants; investigate actual
   failures before making further changes. Local portable runtime validation is complete.
2. Continue catalogue/ordinary-field coverage, full-window interaction and native
   viewport qualification from the desktop handoff. Review indexed/named collection
   reference semantics against the stable-identity contract before release.
3. Complete representative 0.3 profiler evidence, original-addon parity, Windows GUI
   and portable executable acceptance. This checkpoint does not complete 0.3 release
   qualification; do not merge or bump the version on the basis of core tests alone.
4. Keep follow-ups and recovery on this cloud branch, pushing coherent checkpoints.

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
