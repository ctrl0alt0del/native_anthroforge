# 0.3 shortcuts and parametric curves

- Task branch: `codex/shortcuts-parametric-030`
- Integration branch: `main`
- Starting revision: `c74b28085c31f894f6ce343265d999da526a6feb`
- Status: complete — 0.3.0 implemented and qualified
- Last updated: 2026-10-23, Europe/Bucharest
- Active writer: local Codex implementation chat (direct work)

## Outcome and acceptance

Implement the confirmed [0.3 specification](../specification_030.md) through the
[ordered implementation plan](../implementation_030.md): property wrappers,
driving formulas and attachment policies, native parametric curves, desktop and
headless operations, schema-4 reading/schema-5 writing, and qualified 0.3.0 release.
Preserve existing geometry, attachments, scheduling, undo and resource ownership.

## Current state

Cloud continuation `cf7234b` (including main through `0de6a11`) was reviewed and merged
into the original feature branch in `6f7a048`. Local fixes, evidence and final resolution
policy are pushed. Runtime/package versions are 0.3.0; final production code is the clean
`7bc0ab2` checkpoint. Subsequent delivery changes are documentation only. The integration target
is main; all required implementation and qualification work is complete.

Implemented: property wrappers and exposure, native typed driving formulas, inferred
ownership, initiating-wrapper attachment contexts, XYZ Parametric curves, direct engine
switching, independent exact-path Fiber conversion, full desktop/headless operations and
schema-4 reading/schema-5 writing. Final review repaired variable renaming, scrub delegates,
QObject destruction, drag reorder cancellation, native integer limits/diagnostics, Body-aware
Auto attachments, scalar/vector shape, bounded profiler discovery and point-reference locks.

The user confirmed resolution locking while generated points have deformer membership,
weights or formula references. It is enforced through shared configuration, property,
shortcut, formula and engine-restoration paths; inspection supplies the UI reason. Disabled
references retain the lock. Clearing an empty selection unlocks without making the Hook
apply to the entire curve; Undo restores the assignment and lock. No native sampling or
deformation arithmetic was changed. The expected-failure marker was removed.

**Final evidence:** 1,945 tests pass with no expected failures, all five CTests,
native/script style and function limits, configured typing, numerics and Qt-free headless
doctor pass. The complete canonical 0.3.0 minimal-PATH portable suite passes. An additional
packaged batch verifies configuration/property/shortcut rejection, retained count and
unlocking on binding removal. Native texture captures were inspected. Earlier work qualifies
real Blender source attachment parity and real 0.2.4 assembly loading/editing without changing
source geometry or bindings. Details: [Windows review](../research/shortcuts_030/windows_review.md)
and [performance evidence](../research/shortcuts_030/performance_qualification.md).

Delivery is the single `dist/0.3.0/AnthroForge.dist` and companion
`dist/AnthroForge-0.3.0-source.zip`. Temporary qualification copies remain under `build/`.
Preserve unrelated root `__init__.py`; no user project or source .blend was rewritten.
All checks were background/offscreen; physical interactive acceptance is not claimed.

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
