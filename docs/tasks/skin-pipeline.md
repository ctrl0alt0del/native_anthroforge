# Automatic skin pipeline implementation

- Task branch: `codex/skin-pipeline`
- Integration branch: `main`
- Starting revision: `277af232d9393506f5c875dfaa2fdd3ac60d5181`
- Status: in progress; implementation and qualification pending
- Last updated: 2026-11-27, Europe/Bucharest
- Active writer: skin pipeline implementation chat

## Outcome and acceptance

Implement [the specification](../specification_skin_pipeline.md): exclusive Draft/Final
targets, prerequisite-directed repair, isolated builder configurations, safe asynchronous
publication, AVBD prefix reuse and ordinary/extended project persistence. Complete all
30 acceptance scenarios plus builder-selection and checkpoint cases from planning.

## Confirmed decisions

- U1: Selecting FIELD/AVBD immediately requests a non-user-cancelable draft rebuild.
  Ordinary parameter edits remain pending until explicit successful application.
- U2: Failed selection retains the last applied builder for later automatic anatomy
  updates. The requested selection remains visibly unapplied; Retry can apply it.
- U3: Build Skin selects Final and explicitly builds in one undoable action.
- U4: Include in-session checkpoints and `.anthroforgex` save/reopen. Ordinary project
  files omit construction checkpoints; Save retains the chosen format.
- U5: Main accepted anatomy only; preserve candidate/variant isolation. Automatic draft
  work cannot be user-cancelled; internal invalidation and shutdown remain supported.

## Implementation sequence

1. Preserve and import the required existing AVBD application boundary; isolate builder
   settings, source capture and dependency contracts.
2. Add structured stage assessments and one skin-domain target planner using the existing
   TaskCoordinator for all execution, reservations and resource admission.
3. Connect committed edits, source completion, mode changes and retry; implement applied
   configuration promotion, non-cancelability and coherent history/publication.
4. Own and validate AVBD prefix checkpoints; add schema-10 migration and extended saves.
5. Integrate shared commands, stable desktop controls, mode-driven display and diagnostics.
6. Run focused tests, full development gate, real Qt and packaged/runtime qualification.

## Autonomous decisions and evidence

- D1 (implementation isolation): reuse the clean existing documentation checkout and
  branch from main. The separate `codex/avbd-envelope-cpu` working tree has unrelated
  numerical experiments and removals; it remains untouched. Import only dependencies
  required by this feature, retaining their baseline provenance. Validate imported
  application behavior separately before adding scheduling.
- D2 (complexity): index builder/contributor settings once per capture; compare ordered
  checkpoint signatures in one prefix walk. Metadata planning is O(S+C), with S sources
  and C configuration records. Hash/copy checkpoint bytes once per new immutable blob;
  reuse digest identities thereafter. Native numerical complexity remains unchanged.
  Measure capture/publication and retained storage separately from solver runtime.

## Current state and verification

Imported the 31 required application/model/desktop/native adapter baseline files from
the existing AVBD worktree. Its numerical runtime remains an explicit external runtime
dependency while checkpoint integration is being implemented. No experiments or removals
were copied into this task.

Baseline check: `pytest tests/test_skin_draft_builder.py tests/test_scp_skin_policy.py
tests/test_skin_effective_settings.py tests/test_skin_job_lifecycle.py -q` passed 24 tests
on the imported content, using the existing AVBD worktree native DLL. A fresh native
build and full qualification remain pending.
Existing runtime evidence is not evidence for this feature. The specification remains
marked implementation pending until the complete outcome is qualified.

## Next actions and blockers

Import the minimal existing builder integration, establish test environment, then
implement configuration ownership and behavioral tests. No user decision is pending.

## Recovery inputs

The newer builder source was inspected at
`E:/development/anthroforge/build/application-boundaries`, HEAD `b3b92969`, plus its
existing uncommitted files. The shared local Python environment is
`E:/development/anthroforge/.venv`; generated native/runtime binaries are local-only.
Do not claim the original working tree can be recovered from its HEAD alone.
