# Muscle Paint 0.5.0 — implementation plan

**Status: Proposed ordered delivery plan — runtime implementation not started.**
Prepared 2026-10-30 against `2ec68ce4`. Product behavior is confirmed in
[specification_050.md](specification_050.md); architecture and methods are proposed in
[design_050.md](design_050.md). The [Painting System foundation](painting_system.md) is
already implemented. Do not redo that refactor or describe it as completed Muscle Paint.

## 1. Delivery contract

Deliver the complete Directional/Perimeter workflow, physical-width multisurface paint,
editable gaps, main/branch/closed construction, sparse fitted Bezier Fibers/Membrane,
ordinary bindings and all specified temporary-history behavior through desktop and
Qt-free authoring. Every integrated increment has both shared operations and its usable
desktop entry point before advancing; intermediate limits must be visible and honest.

Preserve existing tissue-weight/collagen results, commands, visibility, one-action undo
and resource ownership. Preserve attachment propagation, ROUTED, inflation, stacking,
mirroring and ordinary surface evaluation. The explicit cyclic-map extension is the only
planned shared surface-evaluation capability addition; existing default behavior stays intact.

No Muscle Paint numerical method is qualified yet. Experiments select variants within
the documented design. If evidence calls for a different algorithm, extra rejection rule,
new workflow or weaker accuracy policy, explain it and discuss it with the user first.
No approval is inferred from silence, elapsed time or the fact that a prototype completed.

## 2. Owners and interface obligations

| Responsibility | Owning modules/boundary | Integration obligation |
| --- | --- | --- |
| Input records and capabilities | `core/painting.py` and focused Muscle Paint value modules | Keep legacy screen brush unchanged; add typed physical strokes, surface sets and explicit coordinate conventions. |
| Shared stroke execution | `application/painting*`, explicit consumers | Generalize capture/commit intent and effect reading without per-consumer lifecycle branches. |
| Temporary draft state | Focused `application/muscle_paint*` service, composed under context painting | Named drafts, immutable revisions, source association, domain status and registered lifecycle hooks. |
| Undo and save separation | `application/history.py`, authored publication, context/save/resource owners | One chronology, optional transient contributions, no phantom document changes or replay on paint-only undo. |
| Native geometry | Existing library with focused paint-sheet/chart/fit/quality units and batched ABI | Numerical preparation and all loops in C++; retain cancellation/ownership and upstream attribution. |
| Generated construction | Existing curve/Fiber, junction, Membrane, binding and topology policies | New graph assembled atomically; verified identity reuse, no dummy SCP or alternate propagation. |
| Cyclic correspondence | Core SurfaceAlignment, application/native correspondence, codecs and typed remappers | Explicit periodic semantics and coordinated schema transition; all consumers see the same mapping. |
| Commands/status/inspection | Feature command declarations, shared status projections and source adapters | Authoring and UI obtain the same availability/evidence; explicit guards and expected revisions. |
| Desktop | Dedicated typed panel model, construction tool and staged viewport | Capture input/present results; no timers, job completion or automatic commit in QML. |

New filenames are responsibility suggestions, not permission to create a framework per
stage. Reuse existing policies/owners first. Functions remain at most 15 physical lines;
use cohesive helpers, not compressed statements or numbered fragments. No new worker pool,
Python numerical fallback, global context property, string-prefix router or service locator.

## 3. Ordered increments

### P0. Contract fixtures and numerical prototypes

**Dependencies:** design/product review; no production changes required to start.

1. Preserve replayable input fixtures: samples, physical width, camera/projection, allowed
   supports, occluders, intended part connections, bindings, expected geometry and source hashes.
2. Inventory the addon sparse planner and smooth-base fitter from the research source list.
   Preserve compact provenance-backed inputs and expected outputs. Keep Blender-only
   publication and Python numerical preparation out of the new production boundary.
3. Build bounded native prototypes under `build/` using the existing build infrastructure.
   Compare the specified gap, chart and fitting variants; include actual final loft evaluation,
   not only fit control points. Record rejected variants and their observed causes.
4. Inspect a simple strip, broad fan, background-bone gap, true Y branch and closed band
   from multiple angles. Calibrate length/angular/depth quantities over model scale, zoom
   and event-rate changes; do not copy unrelated Draw/solver defaults.
5. Set native allocation/refinement/cancellation limits from evidence. Record license/build
   implications before adopting additional headers. Include inequality-QP correctness tests
   against the addon's ordering heuristic; a faster infeasible solve cannot win.

**Exit evidence:** method-choice record for each comparison, concrete feasible open-strip
path, known branch/loop boundary requirements, measurements and images. No broad speed,
convergence or shape guarantee from research papers. Prototypes do not ship as a fallback.
Use these fixtures again throughout the integrated increments rather than restarting research.

### P1. Transient history and geometric painting contracts

**Dependencies:** P0 input/ownership contracts; geometry prototypes may continue independently.

1. Add narrow consumer input/effect/edit-intent contracts. Existing field consumers retain
   their numerical calls and exact argument compatibility. Do not pass the physical brush
   through legacy scalar native packing.
2. Extend History for document and optional transient contributions; audit every navigation,
   asynchronous publication, pending save, historical save, redo and resource-owner caller.
   Introduce tests before migrating paint commits to the new boundary.
3. Add context-local named Muscle Paint drafts, bounded immutable stroke storage, revisioned
   status and lifecycle registration. No serialized sessions or new central Session switches.
4. Add the planned draft/stroke operation declarations and a typed Paint Muscle panel/tool
   with draft selection, Directional/Perimeter and physical width. Pending/error feedback
   uses stable layout and existing toasts/Issues. Generation is unavailable with a reason
   until a qualifying candidate exists.

**Exit evidence:** identical scalar-paint results; paint-only Undo/Redo does not dirty the
document or rerun anatomy; context isolation, cancel and close release resources. Desktop
and headless share draft revisions and capabilities. A paint-only edit after asynchronous
authored work must not corrupt its history membership or save checkpoint.

### P2. Physical capture, target sheet and direct editing

**Dependencies:** P1; P0 selection for gap/capture behavior.

1. Implement batched visible ribbon contacts, physically adaptive sampling and support-set
   provenance. Capture per-stroke camera/settings and per-sample threshold override.
2. Implement physical-neighborhood depth continuation across the full width. Reject background
   hits without seeding the predictor from them. Keep curved support, thin backs and grazing
   conditions separate in diagnostics. Target filters do not remove collision obstacles.
3. Implement grouping/Keep Separate, independent flow/coverage, initial per-part charts and
   polygon Perimeter edits. Retain source stroke identity/order through merging.
4. Implement target-sheet gap interpolation and baseline-relative normal handles, endpoint
   strip proposals and unfinished-contact findings. Use the P0-qualified method; do not add
   an automatic ROUTED or repair stage.
5. Integrate overlay resources and draft inspection through the existing capture/geometry
   services. Make source freshness, support/gap labels and normals inspectable headlessly.

**Exit evidence:** meaningful editable target-sheet preview in desktop and API; identical
physical coverage under zoom/event replay; opposite strokes merge, crossing/different layers
do not; narrow coverage survives; gap depth is reversible and supported ends stay fixed.
Cancellation preserves the prior valid preview. Still no document construction on strokes.

### P3. Open-strip generation end to end

**Dependencies:** P2 and qualified fixed-correspondence fit from P0.

1. Port numerical input normalization, constrained cubic fit assembly and sparse-row selection
   to the existing C++ library. Shared material stations define the evaluator being fitted.
2. Capture endpoint proposals through existing confirmed exterior placement, constrain their
   qualified positions, fit and evaluate bound Fibers through the actual native loft.
3. Compute independent spatial/coverage/material/direction findings. Add refinement in the
   correct dimension with bounded attempts, no implicit tolerance relaxation and explicit
   exhausted/inconclusive outcomes.
4. Implement Generate/Update automatic candidate finalization, writer/save admission and atomic
   construction transaction. Register provenance and transient association in the same history
   entry. Revalidate the complete read set and prevent repeat publication.
5. Preserve Membrane identity on Update; reuse compatible source identities and enforce shared
   consumer/topology/deletion policies. Ordinary manual source edits discard the draft through
   change provenance, not special cases in every editing command.
6. Deliver the desktop Generate/Update action, editable binding strips, count/accuracy controls
   and inspectable failed candidate. Show measured dimensions and sampled-evidence limits.

**Exit evidence:** real single/multiple-SCP open Membrane creation and regeneration through
both clients, ordinary subsequent propagation, one-action undo, unchanged source SCPs,
matching bindings after reopen, no hidden dummy anatomy. Undo Generate preserves painting;
next Undo removes the preceding stroke. Failure/no-op leaves no partial graph/history step.

### P4. Flow, broad regions and controlled refinement

**Dependencies:** P3 working strip workflow; P0 field/chart comparison evidence.

1. Complete stroke-guided axial field interpolation and checked chart integration for broad,
   curved and fan-shaped regions. Preserve perimeter edits during direction redraw and preserve
   attachment strips unless deliberately moved.
2. Complete group consistency and topology checks, boundary/narrow-region holdouts and spatial
   versus angular error reporting. The coincident-square/90-degree-flow case must fail direction
   acceptance despite zero surface-distance error.
3. Qualify row-count override, automatic sparse choice, exact knot insertion and fit-system
   caching. Record condition/constraint/layout keys; use equality/inequality solvers only for
   their declared problem class. No automatic change of algorithm to force a passing result.
4. Add complete typed status and candidate image/numerical evidence for failed or incomplete
   fits, extending inspection-source availability explicitly rather than pretending failure
   is a successful ready candidate.

**Exit evidence:** broad pectoral-like fan, curved SCM-like strip, narrow extensions and
conflicting direction cases; actual shapes and flow compared with the frozen target.
Demonstrate bounded work and actionable reasons where the current loft cannot represent
the requested region. The user can correct paint or explicitly change tolerance/count.

### P5. Actual branches and periodic closed construction

**Dependencies:** P3/P4; P0 branch/loop prototypes.

1. Implement main/child root proposals with direct disambiguation; exact Bezier root insertion,
   junction identities, separate part fields and existing interval restrictions.
2. Integrate the unchanged branch assembly operator into fit/evaluation. Compare the assembled
   seam correction against native evaluation numerically and visually; independently verify
   branch-root coverage/direction after welding.
3. Implement cyclic material maps through core, application, native ABI/evaluation, ordinary
   authoring and inspection. Test monotone period/wrap, phase, reversal, corners and deformation.
4. Add schema-10 encoding/validation with existing-schema readers/defaults. Update graph-copy,
   Make Independent, assembly, skeleton replacement, variants and mirror reference rewriting.
   Reuse existing identities/resources; do not add a paint-only hidden mapping.
5. Deliver explicit loop closure/seam/binding controls and branch correction in the same tool.
   Preserve prohibition of nested/closed branches, overlapping root intervals, disconnected
   output and twisted/nonorientable strips.

**Exit evidence:** genuine Y and two nonoverlapping child branches; periodic variable-width
band with stable binding regions under deformation; successful save/reopen without the
paint draft. Existing open/default closed loft fixtures remain unchanged. Earlier-schema
loads preserve results/startup policy, and older applications clearly reject schema 10.

### P6. Complete lifecycle and integration

**Dependencies:** all supported generation families from P3–P5.

1. Complete every specification discard/preserve transition, including coherent common rigid
   movement, relative movement, delayed dependent publication, successful/failed Tissue creation,
   manual geometry/binding edits, deletion and undo restoration of a discarded draft.
2. Qualify updates with shared sources, external consumers, attachments and topology locks;
   no reference may be silently removed or rebound because automatic Fiber count changed.
3. Complete large searchable Paintings/part/finding lists, return from associated Membrane,
   overlays, direct corrections, tool cancellation and variant/workspace isolation.
4. Profile cache keys, leases, repeated previews/generations, history-held resources and failure
   evidence. Retire obsolete jobs immediately when safe; capacity admission must preserve
   committed strokes and history rather than evicting user-authored temporary data silently.
5. Complete API examples using the shared operations, inspection/export of uncommitted evidence,
   stable paging and exact revisions. No desktop callback may be needed for `Session.wait()`.

**Exit evidence:** all listed product behaviors usable through desktop/headless; current
geometry and picked geometry agree; saving with pending generation follows existing save
coordination; paint-only entries do not change autosave/unsaved-project behavior. Drafts
do not survive project reload, while generated ordinary construction does.

### P7. Qualification and release

**Dependencies:** all previous exit evidence; no known required incomplete workflow.

1. Run the full development gate, native numerical/parity checks and Qt-free command files.
   Add contract tests across all three painting consumers, not implementation-mirroring tests.
2. Inspect actual hidden/offscreen desktop captures at narrow/wide layouts, multiple views,
   hover/focus and pending/error states. Check tool navigation, numeric dragging and field
   positions. Record the limits: these do not establish manual interactive acceptance.
3. Run serial counterbalanced performance comparisons with representative assemblies. Measure
   source capture, native work, validation, publication, UI and retained memory separately.
   Report variance/background load and profiler overhead; no unsupported speed claims.
4. Review ownership/coupling separately: shared lifecycle, native numerical preparation,
   context isolation, command declarations, history semantics, resource lifetime and typed UI.
5. Update actual implementation status, API/examples, computation inventory/history, upstream
   notices and measured defaults. Resolve required failures; do not label them future work.
6. Only after qualification, advance to 0.5.0 and produce one canonical
   `dist/0.5.0/AnthroForge.dist` and companion `dist/AnthroForge-0.5.0-source.zip`.
   Run relocated portable checks. Temporary builds/evidence stay under `build/`.

## 4. Research coverage and discriminating tests

Every R-number refers to the [research inventory](muscle_paint_050_research.md).

| Research item | Delivery | Evidence that distinguishes success from an easier proxy |
| --- | --- | --- |
| R1 physical capture | P0/P2 | Same world-width ribbon at different zoom/event rates; grazing/thin-bone visibility; scalar painting unchanged |
| R2 depth layer | P0/P2 | Background rejected at ribbon edges as well as center; no event-count threshold ratchet; curved foreground still followed |
| R3 gap shape | P0/P2 | Drawn curved course retained; multiple cameras; missing end remains unfinished; fitted result measured against frozen target |
| R4 depth control | P0/P2 | Supported ends fixed, zero offset unchanged, wheel reversal exact within tolerance, no normal flip or invented degenerate normal |
| R5 merge | P0/P2/P4 | Reverse strokes agree, 90-degree crossings and nearby layers stay distinct; chain of local similarities cannot force invalid grouping |
| R6 coverage/topology | P2/P4 | Narrow appendage, erased hole, point contact, disconnected strokes; no pixel-dependent connection or omitted region |
| R7 flow/chart | P0/P4 | Positive orientation, monotone stations, singular/contradictory data reported; flat identical shapes with different flow distinguished |
| R8 sparse fit | P0/P3/P4 | Actual native loft rather than an unrelated fitted mesh; across/along refinement separated; exact knot insertion; no global-minimum claim |
| R9 bindings | P3/P6 | Multibone endpoint strips, confirmed exterior placement, no continuous attachment across the middle, subsequent parent changes |
| R10 branches | P0/P5 | Genuine partial-boundary Y and two-child cases, exact junctions, final seam correction; whole-edge shared patches cannot substitute |
| R11 loops | P0/P5 | Cyclic band, phase/reversal/corners and material stations under deformation; closed geometry alone is insufficient |
| R12 quality | P0/P3–P5 | Independent holdouts, bidirectional/boundary/material/direction measures; resolution/uncertainty exposed, exhausted check cannot pass |
| R13 execution | P1–P7 | Owned dispatch, read sets, stale/cancel, real preparation/publication/peak memory, no alternate worker pool |
| R14 history | P1/P3/P6 | Stroke A/B, Generate, Undo, Undo, Redo; source edit/discard/Undo; asynchronous results across temporary steps; unchanged saves |

## 5. Required integration scenarios

- **Models:** open strip, fan, true branches, closed loop, source/mirror support eligibility,
  shared controls and retained Manual output. No dummy SCPs or source geometry mutation.
- **Failures:** missing end, ambiguous branch, disconnected coverage, degenerate normals,
  infeasible constraints, unmet accuracy, native exception and capacity exhaustion. Keep
  preceding accepted output and relevant attempted evidence; penetration remains advisory.
- **History:** no-op stroke; Generate/Update; delete; manual edit; Create Tissue; source edit;
  common/relative support movement; undo/redo with concurrent accepted publication;
  historical save; redo truncation; project/variant/context closure.
- **Concurrency:** release before preview completion, double finish/generate, latest-preview
  coalescing, settings/support change while queued/running, undo/discard before publish,
  pending save, active gesture, obsolete callback and independent viewport lease.
- **Persistence:** accepted sources, bindings, junctions and periodic maps round-trip;
  older documents unchanged; no paint history/native handles/temporary candidates serialized.
- **Usability:** simple valid stroke + Generate, direct ambiguous-root correction, gap
  wheel gesture, ordinary numeric controls, searchable paintings and stable field bounds.
- **Resource accounting:** count unique buffers held by jobs/history/viewport/inspection;
  superseded caches release, explicit inspection retains independent leases, edit admission
  handles pressure without dropping undoable strokes.

Use a schema-compatible copy of the 96-muscle assembly for the production workload, with
SCM-like, pectoral-fan and serratus-branch paintings. Preserve original project hashes.
Store compact portable inputs in tests where licensed; large anatomy and raw recordings
remain external/ignored with manifests and provenance. Compare endpoints/shape/flow in
multiple views, then move supporting anatomy and verify ordinary propagation and persistence.

There is no existing end-to-end Muscle Paint baseline. For new stages compare explicit
prototype variants; for reused code compare against the addon/native fixture. Re-run
existing scalar-paint qualification to detect regressions. Do not infer full-app latency
from a fit microbenchmark or claim a refactor speedup from noisy differences.

## 6. Workflow and completion records

Use a task branch, recovery record and coherent checkpoints; preserve unrelated work.
Respect the current session's Git remote authorization. The design delivery is local-only
under the latest supplied no-remote instruction; do not claim remote recovery without a push.
Before each implementation checkpoint record completed behavior, unqualified variants,
observed failures, exact fixtures and the next discriminating experiment.

Update [computation history](computation_history.md) with every actual algorithm, sampling,
constraint, tolerance, validation, scheduling or cache change. Each entry names the old/new
approach, why, preserved contracts, evidence and remaining limits. This documentation-only
design is not a computation change or a release acceptance record.

Final delivery includes full API/desktop behavior, published fixture/evidence summaries,
separate design review and packaged qualification. Do not stop at an open-strip prototype,
defer confirmed branches/loops/history, or describe an untested method as production-ready.
