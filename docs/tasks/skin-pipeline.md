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

Configuration ownership is implemented: FIELD and AVBD have separate immutable parameter
records, capture policies, validation and dependency signatures. Common contributor records
contain topology settings only. Pending, applied and unknown legacy provenance are distinct;
the legacy migration freezes saved builder settings without inventing an accepted revision.
Painted data remains reachable through pending and applied configurations.

Validation: 45 focused configuration, migration, capture, builder and job tests passed;
strict mypy passed for all 695 checked source files. These checks use the existing native
DLL, not a fresh build. Numerical behavior is unchanged. The initial failures were test
coupling to the former FIELD resolution constant and an assertion on a pre-undo snapshot;
the tests now inspect the owning policy and current document. GUI and packaging are pending.

The next increment adds typed stage assessments, a skin-domain planner hosted by the
existing lifecycle, committed Draft updates, exclusive Final routing, applied configuration
promotion and captured intent checks. Generic cancellation now respects a per-job capability;
automatic draft construction cannot be user-cancelled. Activity counts active jobs separately
from cancellation availability. The UI has a saved mode checkbox and mode-driven AUTO display.

Eight new integration tests passed for initial automatic draft/undo, committed-edit timing,
applied-versus-pending configuration, cancellation rejection, failed builder-selection recovery
and Final deformation preserving Draft, late-final rejection, reopening without work and
edits while building. The planning/job/builder/retry group passed 31 tests; the expanded
configuration/planner/Activity group passed 40. Ten focused mode/status/deformation tests
also passed against the fresh DLL, after preserving explicit Update's forced evaluation.
Strict mypy passed 699 source files. These are intermediate checks, not full qualification.
The shared pytest Session fixture uses FIELD resolution 24 to bound repeated automatic
construction; the shipped resolution remains 220. Real default-resolution qualification is
still required. The clean native/Qt build in `build/skin-pipeline` succeeded and all six
CTest checks passed. Typed native material/topology incompatibility assertions passed.
QML API validation passed for 186 files and 46 model types. This is not visual QA.

Next: finish lifecycle edge cases (late results, history, no-build-on-open, source readiness,
retry suppression), qualify the typed native compatibility result, then implement owned AVBD
prefix checkpoints and ordinary/extended persistence. Runtime packaging, full suite and real
GUI inspection are pending. No user decision is pending.

## Recovery inputs

The newer builder source was inspected at
`E:/development/anthroforge/build/application-boundaries`, HEAD `b3b92969`, plus its
existing uncommitted files. The shared local Python environment is
`E:/development/anthroforge/.venv`; generated native/runtime binaries are local-only.
Do not claim the original working tree can be recovered from its HEAD alone.
