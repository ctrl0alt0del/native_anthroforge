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

Checkpoint integration now owns portable file bundles with per-file checksums, ordered
content-prefix identities, runtime/binary identity and warm SCP material state. One complete
matching SCP prefix and an eligible complete/transient VCP prefix seed an isolated worker;
the existing external numerical implementation is unchanged. Accepted partial checkpoints
can publish on later-stage failure without promoting the failed builder or replacing Draft.
History retains resources, ordinary archives omit checkpoints, and extended archives retain
durable SCP stages and the complete combined VCP checkpoint. Open/import dialogs and Windows
registration support both extensions. Schema 10 remains backward-readable from versions 4–9.

Validation: 7 new checkpoint protocol/publication tests passed; 6 storage/checksum tests
passed; the configuration/automatic/creation group passed 37 tests. Strict mypy passed all
707 modules. The real installed AVBD runtime built one cube SCP in 11.20 s, then a saved
extended project reopened without computation and reused the same checkpoint in 2.15 s.
The local qualification script/log/archive are ignored under `build/`; this limited smoke
case is not whole-anatomy or multi-stage qualification. External runtime provenance and
availability requirements remain explicit; it is not bundled into the portable app yet.

The full pytest run exposed unrelated creation tests asserting global scheduler success
despite expected background Draft gap-precision failures at the reduced test resolution.
The affected creation helper now checks failures of the requested object. A long-running
case was observed in `test_junction_identity` after duplicated BODY SCPs change; py-spy
places the active worker inside FIELD envelope construction. This is not yet diagnosed as
a particular native loop. The full suite is incomplete and must not be reported passed.

The FIELD probe observed adaptive refinement to approximately 375 million cells rather
than an established infinite loop. General Session tests now use a 64 MiB worker budget
as well as resolution 24; production remains unchanged. A second slow case exposed missing
upstream readiness checks: Draft now waits on the complete dependency closure, including
Manual membranes/curves. All five material/persistence regressions passed in 4.69 seconds
after that correction. No numerical approximation or fallback was added to FIELD.

Final handoff now requires a current Draft even when an older reference remains compatible.
Automatic Retry retains its captured configuration, and repeated prerequisite repair for
unchanged effective inputs reports failure rather than cycling. The shared read-only status
projection exposes mode, phase, stage, readiness and Retry in headless and desktop clients.
Seventeen planning/edge checks and 21 combined lifecycle/status/transport checks passed.
Ruff, formatting, lock consistency, numerical imports and native doctor passed; strict mypy
passed 710 modules. New/modified Python functions passed the 15-line audit.

Real numerical reuse qualification: a resumed three-SCP build has identical connectivity
and coordinates within 1e-10 of fresh construction. A full 27-SCP fixture plus the first VCP
completed. The initial VCP append comparison exposed missing regional material in the bundle:
connectivity matched but positions differed by up to 0.053. Retaining validated geometry,
regional labels/corners and rest geometry fixes the cause; checkpoint protocol is now 3.
The corrected appended second VCP (12.83 s) matches replay of both VCPs (18.10 s), including
connectivity and coordinates within 1e-10. This comparison reused the same accepted skeletal
checkpoint. Eight checkpoint tests now include incomplete regional material rejection.

The worker adapter is now a small owned source package under `avbd_runtime`, launched using
the explicitly configured external AVBD Python interpreter with `-I`. Packaging copies this
adapter; numerical dependencies remain in the configured runtime, separate from desktop Qt.
The new bootstrap passed build/save/reopen/reuse smoke qualification. Qualification scripts,
raw captures and reports are local-only under `build/` and owned temporary directories.

Next: finish the full development gate (third full run is active), resolve remaining
regressions, finish actual GUI inspection, and qualify the portable build. The first package
build started before the checkpoint protocol-3 fix and needs a source refresh/rebuild before
final qualification. Native style checking is active. No user decision is pending.

## Recovery inputs

The newer builder source was inspected at
`E:/development/anthroforge/build/application-boundaries`, HEAD `b3b92969`, plus its
existing uncommitted files. The shared local Python environment is
`E:/development/anthroforge/.venv`; generated native/runtime binaries are local-only.
Do not claim the original working tree can be recovered from its HEAD alone.
