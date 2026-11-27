# Automatic skin pipeline qualification

Implementation: [specification](specification_skin_pipeline.md),
[architecture](architecture.md), [workflow](skin_workflow.md),
[computational rationale](computation_history.md) and [integration record](tasks/skin-pipeline.md).
Evidence recorded on 2026-11-27, Europe/Bucharest. Raw build outputs and captures are local,
ignored artifacts; the checked-in tests and acceptance tools are the reproducible entry points.

## Automated checks

- The complete Python run finished with **2,943 passed and 14 failed** in 1,072.10 seconds.
  All 14 failures were corrected: five tests assumed all background work must succeed even
  when their unrelated low-resolution Draft failed; three legacy fixtures removed skin but
  still expected the newly automatic Draft; four undo cases expected no prior Draft; one
  reference test expected fallback despite an available Draft; one expected schema 9.
  The cached-failure rerun passed 12 remaining cases. The separately corrected schema case
  and split reference cases passed in their focused groups. This is a full run plus verified
  corrections, **not a claim of a subsequent single clean full run**.
- Additional contracts cover repair interleavings, source membership, display precedence,
  builder isolation, packaged adapter import and runtime dependency identity. The acceptance
  map below points to behavior assertions, including controlled workers for race conditions.
  The final interleaving/configuration/architecture group passed 17 tests; all four frozen
  export cases passed, including changing mode after the export request.
- Fresh native build: 376 targets; all six CTest checks passed. Native style and PowerShell
  style checks passed. Ruff, formatting, the architecture/function-length audit and configured
  strict mypy passed; mypy checks 710 source modules. New/modified functions remain at most
  15 physical lines.
- QML API validation passed for 186 QML files and 46 model types. Lock consistency,
  numerical-boundary checks and native/runtime doctor passed.

General Session/Controller tests use FIELD resolution 24 and a 64 MiB worker budget to bound
repeated background construction. Production defaults remain resolution 220 and the normal
resource budget. The actual Qt and packaged checks below exercise production FIELD settings.
This distinction matters: low-resolution gap failures do not prove failure at production settings.

## Requirement evidence

Each row names the principal test module or tool; the assertions within it establish the
stated result. Planner tests isolate decisions; lifecycle tests use controlled completion;
native/Qt/portable checks supply the complementary real execution evidence.

| Case | Evidence and verified behavior |
| --- | --- |
| AC-01 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py): first import builds Draft and belongs to the import undo action; Qt/portable also use first import. |
| AC-02 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [migration](../tests/test_skin_foundations.py), [builder migration](../tests/test_skin_builder_configuration.py): no work on open, legacy output/settings retained, next edit catches up without fabricated applied provenance. |
| AC-03 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [interleavings](../tests/test_skin_pipeline_interleavings.py), [material persistence](../tests/test_material_domain.py): committed edits, membership and required upstream geometry determine work. |
| AC-04 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py): generic cancellation rejects automatic Draft even with `obsolete=True`; shared job capability drives desktop Activity controls. |
| AC-05 | [Edge cases](../tests/test_skin_pipeline_edge_cases.py), [planner](../tests/test_skin_pipeline_planning.py): Final handoff waits for current/inflight Draft, including when a retained reference exists. |
| AC-06 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [updates](../tests/test_skin_updates.py), Qt and relocated AVBD checks: compatible Final updates preserve Draft, topology and reference. |
| AC-07 | [Repair/timing](../tests/test_skin_pipeline_repair.py): Live, On Release and Manual retain their gesture/evaluation rules. |
| AC-08 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [interleavings](../tests/test_skin_pipeline_interleavings.py): switching to Draft rejects late Final/repair output and reaches Draft. |
| AC-09 | [Planner](../tests/test_skin_pipeline_planning.py), [repair](../tests/test_skin_pipeline_repair.py): typed missing/incompatible prerequisites automatically request their producer. |
| AC-10 | [Interleavings](../tests/test_skin_pipeline_interleavings.py): mode stays Final and AUTO displays the prior Final during required construction. |
| AC-11 | [Repair](../tests/test_skin_pipeline_repair.py): numerical failure retains Final/Draft and does not trigger a reconstruction loop. |
| AC-12 | [Interleavings](../tests/test_skin_pipeline_interleavings.py), [native supports](../tests/test_skin_support.py): contributor add/remove and lost material identity lead to typed required work. |
| AC-13 | [Repair](../tests/test_skin_pipeline_repair.py), [fit preview](../tests/test_skin_fit_preview.py): replacement retains saved fits, marks them stale and leaves independent preview supported. |
| AC-14 | [Builder configuration](../tests/test_skin_builder_configuration.py), [draft builders](../tests/test_skin_draft_builder.py): FIELD parameters do not enter AVBD validation or dependency identity. |
| AC-15 | [Builder configuration](../tests/test_skin_builder_configuration.py): invalid inactive AVBD configuration leaves FIELD validation and automatic dependency identity unchanged. |
| AC-16 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), Qt: anatomy updates use applied settings and preserve pending edits. |
| AC-17 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [job lifecycle](../tests/test_skin_job_lifecycle.py): captured settings promote with accepted output; later edits remain pending. |
| AC-18 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [draft builders](../tests/test_skin_draft_builder.py), Qt: failed selection/rebuild retains accepted Draft and applied configuration. |
| AC-19 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py): initial automatic construction captures selected settings and records applied configuration. |
| AC-20 | [Repair](../tests/test_skin_pipeline_repair.py), [edge cases](../tests/test_skin_pipeline_edge_cases.py): failures do not repeat unchanged; Retry retains captured settings; no-progress repair is explicit. |
| AC-21 | [Interleavings](../tests/test_skin_pipeline_interleavings.py), [fit preview](../tests/test_skin_fit_preview.py), [render tool](../tools/skin_pipeline_render.py): AUTO follows requested mode; explicit stages, NONE and independent fitted preview retain precedence. |
| AC-22 | [Repair](../tests/test_skin_pipeline_repair.py): last contributor removal hides Draft, exposes the empty state and preserves undo resources. |
| AC-23 | [Automatic pipeline](../tests/test_skin_automatic_pipeline.py), [job lifecycle](../tests/test_skin_job_lifecycle.py), [checkpoints](../tests/test_skin_avbd_checkpoints.py): undo/redo and late publication preserve the authored branch and resource ownership. |
| AC-24 | [Checkpoint storage](../tests/test_skin_checkpoint_storage.py), [autosave](../tests/test_autosave.py), [interleaving/save](../tests/test_interleaving.py), [issue/save policies](../tests/test_issue_integration.py): accepted storage, wait/checkpoint/pending policies, recovery and project replacement remain coherent. |
| AC-25 | [Export](../tests/test_skin_export.py): export keeps its captured Final after a mode switch, preserves quads, and requires an accepted Final. |
| AC-26 | [Checkpoint protocol](../tests/test_skin_avbd_checkpoints.py), [storage](../tests/test_skin_checkpoint_storage.py), numerical comparisons below: complete matching prefixes only; source/order/version/material integrity and portable ownership are checked. |
| AC-27 | [Edge cases](../tests/test_skin_pipeline_edge_cases.py), [status](../tests/test_skin_status.py), [Activity](../tests/test_activity_model.py): reads/observers do not submit work, alter authored state or create history. |
| AC-28 | [Qt acceptance](../tools/skin_pipeline_acceptance.py), [portable headless acceptance](../tools/skin_pipeline_portable.py): both clients use the same mode/settings/retry operations and publication. |
| AC-29 | [Planner](../tests/test_skin_pipeline_planning.py), [repair](../tests/test_skin_pipeline_repair.py): missing Draft/topology/reference providers are requested through the single coordinator. |
| AC-30 | [Interleavings](../tests/test_skin_pipeline_interleavings.py): mode or anatomy changes during required repair reject obsolete output and preserve accepted resources. |

Planning additions U1–U4 are covered by automatic selection/cancellation and captured Retry,
the existing combined-build undo tests, and ordinary/extended checkpoint storage plus relocated
reopening. Candidate/variant isolation remains covered by the full reconstruction suite and
portable reconstruction/skeleton workflows.

## Actual desktop and portable application

[Qt acceptance](../tools/skin_pipeline_acceptance.py) passed with real QTest interactions,
production FIELD resolution 220 and the configured AVBD runtime. It exercises the mode
checkbox, builder selection, pending fields, unavailable-builder failure, Retry and extended
reopening. Normal and narrow layouts were captured and inspected; controls retain their bounds.
Offscreen Qt captures validate controls, not a rendered 3D viewport.

[Hidden GPU rendering](../tools/skin_pipeline_render.py) separately captured and visually
verified the saved Draft and Final surfaces. The small low-budget topology fixture has visible
coarse edges; it is an execution/display check, not whole-body surface-quality certification.

The final application source was compiled at `9a61d4a3`, then copied into a different directory
containing spaces. The [feature portable check](../tools/skin_pipeline_portable.py) passed with
minimal PATH and no developer Python/Qt paths: fresh AVBD construction, unavailable runtime
failure retaining Draft, `.anthroforgex` reopen without compute, checkpoint reuse, ordinary-save
checkpoint omission, and Final deformation with fixed Draft/topology/reference.
The [general portable check](../tools/check_portable.py) also passed for this binary, including
import, attachment/construction, tissues, mirrors, painting, skin/fits/export, reconstruction,
preferences and recovery. Desktop dialogs were tested offscreen; native window presentation
was not verified by this check. Hidden GPU rendering verified actual viewport pixels, including
the newly automatic Draft shown by default.

Local evidence directories: `build/skin-pipeline-ui/modes`, `build/skin-pipeline-portable-final`
and `build/skin-portable-final`. Executable: `build/skin-relocated-final/AnthroForge app/AnthroForge.exe`.

## Numerical reuse evidence and limits

The AVBD numerical implementation was not replaced. The application owns input capture,
worker isolation, checkpoint files, validation and publication. The initial qualification used
an explicitly configured external runtime. The November 27 packaging change below bundles
that numerical environment; source development retains its explicit override. FIELD and the
other packaged native tools remain available independently.

- Three-SCP resume versus fresh construction: identical connectivity; coordinates within `1e-10`.
  The observed resumed trial took 4.65 s versus 7.74 s for fresh construction.
- A 27-SCP skeleton plus the first VCP completed. A second appended VCP was compared with replay
  of both VCPs from the same accepted skeleton: identical connectivity and coordinates within
  `1e-10`; 12.83 s versus 18.10 s in these single local trials.
- An initial failed comparison (maximum coordinate difference 0.053) exposed missing regional
  material in VCP checkpoints. Protocol 3 retains validated/rest geometry and regional labels/
  corners, and rejects incomplete material. The corrected comparison above passed.
- Prefix identity includes ordered sources/recipes, effective base/final geometry, normalized
  frame, runtime source/binaries and installed dependency metadata. Older/incompatible prefixes
  replay. A complete combined VCP prefix supports append; changed earlier VCPs replay from the
  matching skeletal prefix. No independent branch reuse is claimed.

These results do not establish universal numerical equivalence, whole-body quality, a real-time
latency guarantee or a general speedup. Checkpoints retain full material state and can consume
substantial storage; extended projects opt into those bytes. In the packaged one-SCP fixture,
the extended archive was 387,247 bytes, including 239,970 checkpoint payload bytes; the ordinary
archive after reuse was 141,129 bytes with no checkpoints. This is storage accounting, not a
peak-memory bound for larger anatomy. Ordinary files and recovery copies
retain accepted project results but omit construction checkpoints. No cache eviction policy or
numerical fallback was introduced.

## Bundled-runtime qualification — November 27, 2026

Release candidate `63b468e9` was relocated across drives to a path containing spaces. With a Windows-only
PATH and no developer Python/Qt/AVBD settings, the executable completed fresh SCP generation,
an attached limb and a muscle case. SCP/VCP checkpoints were published. The portable pipeline
check also passed damaged-bundle failure retention, compatible checkpoint reuse with an invalid
external override, ordinary-save checkpoint omission, Final construction and direct deformation
with unchanged Draft/topology/reference. The saved Final fixture contains 1,054 quads.

The complete portable pipeline check passed again on final release `59adb7a4`, including
damaged runtime metadata together with missing application build metadata. Compiled discovery
still rejected the incomplete bundle instead of selecting a developer runtime, and retained
the accepted Draft. The full development gate passed 3,010 Python tests and six native tests;
the final discovery guard then passed 29 focused AVBD/runtime/checkpoint tests, lint and typing.

The final canonical `dist/0.4.3/AnthroForge.dist/AnthroForge.exe` was launched normally, without
arguments or environment setup. Through its visible UI, an embedded bone-and-muscle fixture
was opened and its builder changed from FIELD to AVBD. The visible envelope changed; the panel
reported **Applied: AVBD** and **Requested skin is current**. Saving and reading the result
confirmed 690 finite vertices and 1,376 triangles. This is an actual native-window acceptance,
separate from automated/headless tests.

All 8,536 bundled files passed SHA-256 verification, 1,166 file-backed modules loaded exclusively
inside the private runtime, and generation left its files unchanged. Evidence is local-only in
`E:/development/anthroforge/build/bundled-avbd-release-check`, including the normal-launch
screenshot, saved project, mesh counts and route receipts. These small fixtures establish the
deployment boundary, not whole-body shape quality or compatibility with other GPU architectures.
