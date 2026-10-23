# 0.3 shortcuts and parametric curves

- Task branch: `codex/shortcuts-parametric-030`
- Integration branch: `main`
- Starting revision: `c74b28085c31f894f6ce343265d999da526a6feb`
- Status: resumed; reviewing Cloud continuation and completing release qualification
- Last updated: 2026-10-23, Europe/Bucharest
- Active writer: local Codex implementation chat (direct work)

## Outcome and acceptance

Implement the confirmed [0.3 specification](../specification_030.md) through the
[ordered implementation plan](../implementation_030.md): property wrappers,
driving formulas and attachment policies, native parametric curves, desktop and
headless operations, schema-4 reading/schema-5 writing, and qualified 0.3.0 release.
Preserve existing geometry, attachments, scheduling, undo and resource ownership.

## Current state

Cloud continuation `cf7234b` (including main through `0de6a11`) was reviewed on
`codex/shortcuts-030-cloud-review` and merged into the original feature branch in
`6f7a048`. Review fixes and qualification tools through `57873c1` are pushed to
`codex/shortcuts-parametric-030`. Main has not been merged or modified for this release.

Completed review repairs: stable Parametric symbol renaming, persistent numeric scrub
delegates, safe QObject destruction, drag reordering/cancellation, native integer limits
and sample diagnostics, Body-aware Auto attachment strategy, scalar/vector shape, and
complete bounded profiler model discovery. The shared contracts and evidence are in
[Windows review](../research/shortcuts_030/windows_review.md) and
[performance qualification](../research/shortcuts_030/performance_qualification.md).

Real Blender 5.0.1 sources qualify Pubis descendant overrides and Cheekbone backsolve.
The real 0.2.4 executable and 59-SCP/548-construction-or-tissue assembly qualify unchanged
loading, resource hashes, continued Clavicle editing and old-reader rejection of schema 5.
Production-QML mouse harnesses qualify editing, reorder, cancellation and one-action Undo.
Texture-only D3D11 captures qualify generated curves and consumer geometry while asserting
that their window stays invisible. No interactive desktop acceptance is claimed.

The temporary executable under `build/shortcuts-portable-review/AnthroForge.dist` at
`57873c1` passed the complete portable suite with a minimal PATH, including shortcut
formulas, Parametric geometry, dependent Body rendering, schema 5 and profiler completeness.
The final thin circular-body image was inspected. It is a qualification artifact, not an
additional release distribution. The stable full Windows gate at `57873c1` passed:
1,928 pytest cases plus the one explicit expected failure below, five CTests, native
and script style, Ruff/mypy, numerics and Qt-free headless doctor. Documentation-only
follow-up checked 92 local links with no missing targets. No code changed after that gate.

The user confirmed resolution locking for generated-point membership, weights and formula
references. The shared policy now enforces it through API/property/shortcut/formula writes
and engine restoration; property inspection supplies the UI reason. Disabled references
also lock. The regression is now an ordinary passing test, with additional removal/Undo,
weighted Hook/lattice, formula input/target, recovery and restoration cases. The focused
26-case run and production-QML editor check pass; the screenshot was inspected. No native
sampling or deformation arithmetic changed. The final full gate is next.

Next: complete the final full gate, finish version/release updates, build the single
canonical `dist/0.3.0/AnthroForge.dist` plus source archive, and merge/push the fully validated
feature into main. Runtime/package version remains 0.2.4 until qualification. Preserve the
unrelated root `__init__.py`; all checks remain background-only.

## Historical pause and implementation checkpoints

Paused by user on 2026-10-23. Resume this branch, not a fresh branch. Latest completed
Parametric checkpoint before this pause is `08bb678`; the pause checkpoint contains
additional in-progress UI/catalogue changes. Do not merge or release this checkpoint.

Pause checkpoint changes: searchable owner/descendant attachment policy editor, driver
removal, right-click numerical-property exposure, driven-component read-only fields,
virtualized shortcut value editing, display-unit conversion, expanded segment/cage/field
property discovery, escaped property-port names, Parametric generated-point dependency
edges, and display-only invalid-curve placeholders. Inspector references were added across
primitive, tissue, control, routing and Parametric controls. Named fields and positional
array members now have property addresses. Formula references to lattice points/weights
block resolution changes to prevent their addresses silently changing meaning.

Verification at pause: 36 focused Parametric/Fiber/shared-curve/junction cases passed;
21 shortcut/formula/desktop-adapter cases passed. Driver and Parametric QML probes loaded
without warnings after fixes. Ruff/mypy passed before the final lattice-reference guard;
that final guard still needs formatting/checks. Full gate, native style, broader lifecycle,
actual addon parity, profiler and portable qualification remain pending. The initial empty
UI probe was corrected; geometry and full editor interaction still require proper offscreen
render qualification. No interactive acceptance or completed release is claimed.

Immediate resume tasks: format/check the pending guard and run focused tests; add coverage
for new catalogue addresses, policy editor, placeholders and formula/path cycles. Review
positional address and copy/remapping behavior. Finish ordinary field exposure/read-only
coverage and UI units, then remaining specification qualification and packaging. Runtime
version stays 0.2.4. Preserve unrelated root `__init__.py`. Work remains background-only.

Runtime remains 0.2.4; this branch is incomplete and must not be merged yet.
Initial property/wrapper records, stable numerical references, inferred ownership,
discovery/exposure/configuration API, and coherent nested candidate writes exist.
Schema 5 writes these records; schema 4 remains readable with empty shortcut state.
Ten foundation contract tests pass. Numerical transforms use canonical metres/radians;
curve point changes use native handle editing and cage resizing reuses native interpolation.
Common authored mutation guards reserve active formula components. A first incremental
shortcut panel exposes properties and edits wrappers with default policies. Nondefault
attachment policies explicitly remain unavailable in this incomplete checkpoint.
The driver editor now provides native-backed values, type/quantity selection, formulas,
searchable targets/inputs, enable/remove, labels, hide and shared ordering. This is not
a usable 0.3 release: complete catalogue/context exposure, attachment policies and
parametric evaluation still need integration and qualification.
The unrelated untracked root `__init__.py` remains untouched.

### Historical decisions and relevant files

The specification is authoritative. Property edits and wrapper edits are distinct;
ownership is inferred; only the initiating wrapper applies attachment policies.
Formula evaluation and numerical sampling belong in C++; parser candidates need
qualification against typed/unit-aware semantics before selection. Any junction
locks parametric resolution. Parametric-to-Fiber conversion preserves the exact
accepted finite path as an independent Bezier curve. Older 0.2.4 projects must load.

### Historical verification

The full current pytest run completed with 1,796 passes and one obsolete schema-4-only
assertion in `test_tissue_contracts`; that assertion now checks schema 5 plus reading 4.
Five added candidate/persistence tests and three desktop adapter tests pass. Actual
offscreen driver-editor rendering loaded without QML warnings and was inspected in
`build/driver-editor.png`. The probe exposed native-returned point scalars disappearing
from discovery; native scalar boxing and descriptor recognition were corrected, with a
regression case. Property pickers now avoid evaluating every world transform for metadata.
This does not establish interactive acceptance or final release qualification.

Driving lifecycle operations and a batched formula job now use the existing coordinator.
Property/formula ports distinguish numerical inputs from geometry dependencies. Eight new
public-API cases cover chains, cycles/dependents, independent failure, types/units, uniform
vectors, undo/redo, Manual provenance, and captured cancellation. The combined expression,
foundation, scheduling/interleaving and Issues run passed 104 cases. Manual publication
initially missed downstream reevaluation; the test exposed it and publication now registers
dependent work before the parent job terminates. Further coupled-field, lifetime, offscreen
editor and full-suite checks remain required. No driver editing UI or attachment policies
have been qualified yet.

The restricted native expression service is implemented and has 49 passing contract
cases (59 together with shortcut foundations). Candidate probes and the selection
rationale are in [expression qualification](../research/shortcuts_030/expression_qualification.md).
No parser dependency was pinned: one small typed native compiler/evaluator preserves
integer/real/unit semantics without a second floating interpreter. Program caches use
the existing engine ResourceCache; native binding calls retain profiler coverage.
Latest native dimensional bounds/input validation edits were rebuilt successfully;
the combined 59-case run passed. Full integration is pending.

Initial main and origin/main matched after fetch. `uv run --no-sync pytest
tests/test_shortcut_foundations.py tests/test_construction_objects.py
tests/test_interleaving.py -q`: 38 passed. Mypy and Ruff checks pass for current source.
Offscreen desktop smoke and an actual shortcut-panel capture loaded without QML
warnings. Font-directory configuration was necessary for readable offscreen text;
the inspected capture is local-only `build/shortcuts-panel.png`. Required full tests, profiler,
native/parity, offscreen GUI and portable packaging have not yet been run.
Validation stays background-only; no interactive desktop acceptance is implied.

### Historical next actions (superseded by Current state)

Parametric checkpoint: XYZ/interval expressions and typed variables now evaluate in a
single native path call. Uniform sampling, direct engine switching/restoration, generated
coordinate restrictions, shared primitive consumption, exact independent Fiber copying,
junction followers/locks and dispatch-time endpoint intent have focused tests. The
equation/variable inspector is implemented, but its full offscreen interaction remains
unqualified. The initial capture selected before refreshing and was empty; the corrected
capture shows the selected curve. Inspect the equations and actual geometry separately.
The full pre-Parametric suite passed 1,806 tests. Runtime version remains 0.2.4.
Next: finish placeholders, deformation/lifecycle qualification, policy UI, full property
catalogue/context exposure, copying/reference handling, profiler and release acceptance.

Attachment-policy checkpoint (2026-10-23): native owner capture/backsolve and coordinated
temporary edit contexts now work through shared shortcut operations. Six integrated cases
cover wrapper-only behavior, translation-only owner retention after geometry changes,
Follow Rotation overrides, drag pauses/cancel, and Manual edits saved/reopened before
explicit evaluation. Authored attachment settings/bindings are restored; accepted pose
receipts retain effective-binding provenance without forcing startup recomputation.
40 focused regression cases, Ruff and mypy passed. Native fixture parity, broader lifecycle
cases, policy UI, full regressions and native style checks remain pending. Context records
are portable pending intent, not native handles. Parametric implementation is still pending.

1. Complete driver validation/qualification and desktop editing. Public `driver.*` operations,
   formula output dependencies, failure retention, and scheduling now exist. Audit coupled
   validation and pending result publication, then implement initiating attachment contexts.
   Replace the explicit nondefault-policy checkpoint rejection in
   shortcut_operations.editable_wrapper when those edit contexts are implemented.
2. Finish catalogue coverage, property context actions, structural copy/reference
   handling, and full shortcut edit policies, then complete each increment in the
   implementation plan. Record checkpoints and actual evidence here.
3. Run full qualification, update versions only after success, build the canonical
   distribution/source archive, and merge the validated branch.

Attachment-policy integration is the next active stage. Reinspection of addon
`core/shortcuts/owner_backsolve.py`, `session_state.py` and `app/use_cases/shortcut_edit.py`
confirms translation-only retained child anchors; original authored attachment runtime
is restored after each update, and only anchor/strategy changes need temporary recapture.
The standalone context must follow queued work, explicit gestures, cancellation and history
without the addon's one-second cache expiry. Pending Manual edits and historical saves
must retain any needed preparation intent/resources; do not add a global settings override.

## Recovery inputs

Use repository development setup. Research fixtures and provenance are in
`docs/research/shortcuts_030/`; large original Blender files remain local under
`E:/development/WIP_models`. No source anatomy migration is included in this task.
