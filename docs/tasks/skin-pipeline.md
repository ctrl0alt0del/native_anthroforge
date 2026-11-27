# Automatic skin pipeline implementation

- Task branch: `codex/skin-pipeline`
- Integration branch: `main`
- Starting revision: `277af232d9393506f5c875dfaa2fdd3ac60d5181`
- Status: implementation and qualification complete; ready for integration into main
- Last updated: 2026-11-27, Europe/Bucharest
- Active writer: skin pipeline implementation chat
- Latest pushed application checkpoint: `9a61d4a3`

## Outcome and decisions

Implements [the specification](../specification_skin_pipeline.md): exclusive Draft/Final
modes, prerequisite-directed repair, builder-owned settings, captured publication intent,
AVBD prefix reuse and ordinary/extended storage. See [qualification and all 30 acceptance
cases](../skin_pipeline_validation.md), [architecture](../architecture.md),
[workflow](../skin_workflow.md) and [computational history](../computation_history.md).

Confirmed planning additions:

- U1: Selecting FIELD/AVBD immediately requests non-user-cancelable Draft construction.
- U2: Failed selection preserves the last applied builder for later anatomy edits;
  the selection remains pending, and Retry uses the captured failed configuration.
- U3: Build Skin selects Final and explicitly builds in one undo action.
- U4: Include session checkpoints and `.anthroforgex` save/reopen. Ordinary files omit
  construction checkpoints; Save retains the selected format.
- Main accepted anatomy only; automatic Draft has internal invalidation but no user Cancel.

## Implementation boundaries

- One skin-domain planner uses the existing TaskCoordinator for every execution. It waits
  for upstream anatomy, follows committed Draft edits and Live/On Release/Manual Final
  policy, rejects obsolete intent and distinguishes typed repair from numerical failure.
- FIELD/AVBD own immutable configuration, capture, validation and dependency signatures.
  Applied values promote with successful Draft; pending and unknown legacy provenance
  remain distinct. Selection failure never silently promotes a builder.
- Owned AVBD adapter captures consecutive SCP and combined VCP prefixes, warm/material
  state and checksummed bytes. Identity includes source/order/settings/frame and runtime
  source/binaries/dependency metadata. Protocol 3 rejects incomplete regional material.
- Schema 10 reads versions 4–10. Extended archives keep durable checkpoints; ordinary
  archives and recovery copies omit them while retaining accepted project results.
- Desktop and headless clients share commands/status. AUTO follows requested mode;
  explicit stages, hidden skin and fitted preview retain their presentation rules.

The existing AVBD boundary was imported from `E:/development/anthroforge/build/application-boundaries`
(HEAD `b3b92969` plus existing uncommitted work), limited to 31 required baseline files.
Its external numerical runtime remains an explicit dependency and was not modified.
The other worktrees, including the dirty `E:/development/anthroforge` checkout, are untouched.

## Verification and material findings

- Fresh native build: 376 targets, six CTest passes; native and PowerShell style passed.
- Ruff/format, 15-line architecture audit, strict mypy (710 modules), QML API validation
  (186 files/46 models), lock consistency, numerical boundary and doctor checks passed.
- Complete Python run: 2,943 passed, 14 failed in 1,072.10 s. All failures were obsolete
  assertions about global background errors, absent automatic Draft or schema 9. Twelve
  cached failures passed on rerun; the separately rerun schema and split reference cases
  also passed. Additional mode/repair/export/checkpoint contracts pass. This is a complete
  run followed by verified corrections, not a later single clean full run.
- Tests bound repeated Session/Controller FIELD work at resolution 24 / 64 MiB. Production
  remains resolution 220 / normal budget. Readiness now handles ControlResult without a
  `pending` member and waits for the complete upstream dependency closure.
- Actual Qt/QTest mode, builder, pending settings and Retry interactions passed with
  production FIELD and real AVBD. Normal/narrow captures and separate hidden GPU Draft/
  Final surfaces were inspected. Low-cost fixture quality is not whole-body qualification.
- Three-SCP resumed/fresh results have identical connectivity and coordinates within
  1e-10. A 27-SCP plus VCP trial completed. Corrected second-VCP append matches replay
  within 1e-10 (12.83 s versus 18.10 s in single local trials). Initial mismatch traced to
  missing regional material; the complete protocol-3 material bundle fixes that cause.
- Relocated feature package at `9a61d4a3` passed with minimal PATH: fresh AVBD, missing
  runtime failure retaining accepted output, extended reopen without work, prefix reuse,
  ordinary-save omission and compatible Final deformation with fixed Draft/topology.
- The packaged worker imports its own adapter rather than an installed top-level package;
  a packaged-layout regression reproduces the original shadowing failure.
- Final interleaving/configuration/architecture group: 17 passed; all four export cases
  passed. The new controlled cases cover input/mode changes during repair, add/remove
  membership and explicit display preservation.
- General relocated-package qualification also passed, including construction, tissues,
  skin/fits/export, reconstruction, painting, preferences and recovery. Offscreen dialogs
  and hidden GPU pixels were checked separately; no visible native-window claim.
- Final documentation links and task diff reviewed; no application code changed after the
  qualified `9a61d4a3` binary. Later changes are tests and documentation only.

## Next actions

Commit/push the final tests and evidence, then merge normally into main and push under the
standing continuity authorization. Origin/main remains `277af232` after the final fetch.
Verify remote ancestry includes the task result. Git ancestry establishes integration even
if this pre-merge record still says ready for integration.

Local executable: `build/skin-relocated-final/AnthroForge app/AnthroForge.exe`.
Portable reports: `build/skin-portable-final/portable-check.json` and
`build/skin-pipeline-portable-final/qualification.json`.

No user decision is pending. Raw logs/captures and generated binaries are ignored local
artifacts, not remote recovery assets. The shared environment is `E:/development/anthroforge/.venv`;
recreating external runtime experiments from their HEAD alone is not possible. See the
qualification report for executable checks and explicit scope/performance limits.
