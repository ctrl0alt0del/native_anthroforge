# Muscle Paint 0.5.0 — implementation design

**Status: Proposed implementation design — not implemented or qualified.**
Prepared 2026-10-30. The [confirmed product contract](specification_050.md) is authoritative;
the [method research](muscle_paint_050_research.md) supplies rationale and alternatives.
The [implementation plan](implementation_050.md) orders delivery and required evidence.
This document changes no runtime behavior, dependency, package version or project format.

## 1. Outcome and limits

Paint a physical-width area and longitudinal direction across eligible SCPs and gaps,
then explicitly Generate/Update ordinary editable Bezier Fibers and a Membrane. Keep
painting temporary, with individual undoable strokes and a named Paintings list. Creating
Tissue remains an ordinary separate action and discards the associated painting.

Use the implemented [Painting System](painting_system.md) for the stroke lifecycle.
Extend it for ordered geometric effects, physical width and multiple supports; preserve
the numerical and interaction contracts of tissue weights and collagen. One stroke or
pending stroke finalization per editing context remains the rule. No queued stroke feature.

The output follows existing attachments and later fiber propagation. Do not introduce an
implicit ROUTED solve, collision repair, different inflation, automatic Tissue creation,
automatic nested/closed branching, envelope generation or Paint Outer. A live envelope
remains a later experiment. Existing algorithms are not replaced by this design.

## 2. Observed boundaries and required extensions

Inspection baseline: `2ec68ce4`, after the application-boundary refactor. Local unrelated
assembly changes are outside this design. These are source observations, not geometry tests.

| Current owner | Observed contract | Required change and affected callers |
| --- | --- | --- |
| [Core painting](../src/anthroforge/core/painting.py), [consumer adapters](../src/anthroforge/application/painting_consumers.py) | One screen-space brush, two-dimensional samples, one surface reference; scalar adapters are explicitly composed | Typed input/capability and surface-set contracts; geometric effect reader and draft edit destination. Preserve both existing scalar consumers. |
| [Painting jobs](../src/anthroforge/application/painting_jobs.py) | Coordinator owns computation/finalization; native brush packing and document-writer targets assume field painting | Consumer supplies owned capture/effect data and declared edit intent; lifecycle does not inspect consumer names or scalar buffers. |
| [History](../src/anthroforge/application/history.py) | Commits only when Document changes | Optional transient contributions in the same chronology, without fabricated Document revisions. Audit asynchronous publication, save, variants and undo callers. |
| [Authored publication](../src/anthroforge/application/authored_jobs.py) | Revision membership connects asynchronous results to initiating and surviving history entries | Preserve that ownership when several transient entries share a Document state; never replay a generation merely because a paint stroke was undone. |
| [Surface records](../src/anthroforge/core/surfaces.py), [application correspondence](../src/anthroforge/application/surface_correspondence.py), [native correspondence](../native/src/surface_correspondence.cpp) | Explicit stations accept complete open curves; closed alignment stores phase/direction but not a cyclic station period | Shared periodic material-map contract, persistence and native sampling. Ordinary arc-length consumers keep their existing behavior. |
| [Branch assembly](../native/src/surface_branches.cpp) | Explicit root intervals, seam station merging and fading child correction | Fit and validate this same assembled operator; do not substitute separate independently fitted patches. |
| [Commands](../src/anthroforge/application/command_contracts.py), [service lifecycle](../src/anthroforge/application/service_lifecycle.py) | Feature registration, declared guards and registered context hooks exist | Use these mechanisms; no prefix dispatch, extra central guard sets or feature reset code in Session. |

## 3. Ownership and records

| Owner | Responsibility |
| --- | --- |
| Core | Immutable physical-stroke, support, part/junction intent, quality-setting and provenance values; no Qt types or mutable sessions |
| Application Painting System | Stroke admission, sequence/currentness, owned capture, preview replacement, finalization and cancellation |
| Muscle Paint consumer and draft service | Named draft revisions, coverage/flow intent, support invalidation, target-sheet/candidate ownership, generation association and domain validation |
| History | One chronology of document and optional transient contributions; commit, cancel, redo, truncation and ownership |
| Native C++ | Projection, ribbon sampling, geometric grouping, chart/polygon work, gaps, line fields, fit assembly/solve, sparse row selection, validation and binding calculations |
| Existing coordinator | All worker dispatch, reservations, coalescing, cancellation, read validation and publication |
| Desktop Muscle Paint model/tool | Camera/pointer capture, settings and direct viewport controls; display shared status and staged resources |

Compose the Muscle Paint draft service under the existing context-owned painting service,
with typed access and registered lifecycle callbacks. Do not add another catch-all Session
field or string-based service locator. The general service never decides anatomical branch
topology, attachment placement or whether a weight array is the appropriate output.

Use explicit consumer registration and narrow contracts for input validation, eligibility,
capture, workload, compute, effect reading and application. Add an edit-intent record that
declares **document** versus **transient** contribution, reads and output reservations.
One application publication path enforces it. Numerical strategies return data and
diagnostics; they cannot submit jobs, mutate history or publish geometry themselves.

Concrete immutable records, with public identities rather than native handles:

- `PhysicalStroke`: original stroke identity/order, mode, captured view, width, sample
  sequence and overrides. Derived samples retain correspondence to original input.
- `SupportSet`: eligible target identities/roles, geometry revisions, local frames,
  captured occluders and membership signature. Store hits/material coordinates separately.
- `MusclePaintDraft`: name, revision, ordered stroke edits, grouping/Keep Separate choices,
  main/branch intents, closure/seam, endpoint strips and gap-control values.
- `TargetSheet`: owned temporary geometry, charts, coverage, axial flow, support/gap labels,
  confidence and input provenance. This is a computational resource, not a scene object.
- `MembraneCandidate`: proposed ordinary construction graph, qualified bindings, sampled
  output, fit evidence, stable source associations and complete read set.
- `GenerationAssociation`: draft identity/revision, generated IDs and accepted construction
  signatures. It is session-only; generation does not serialize a paint recipe.

## 4. Input, surfaces and coverage

Retain legacy screen-space inputs unchanged. The new consumer declares physical-width
support and interprets width as a model-space distance in metres, with normal display units.
Do not reinterpret the existing `radius_px` brush or apply new sampling to scalar painting.
Settings/view remain fixed for a pointer-down stroke; users can change width/settings and
rotate the camera between strokes. Preserve existing camera navigation/cancellation rules.

Capture ordered screen samples and the displayed support/occluder resources. Use native
projection across the entire ribbon width, not just its center. Resample by physical travel
and geometric error, retaining source intervals and corners; a lower event rate must not
change width or turn an invalid layer transition into a valid one. Keep the existing
4,096 public sample limit per stroke; bound derived native samples separately.

Use a support-oriented local frame to form footprint rays; adapt near silhouettes and
depth discontinuities. Visibility prevents painting hidden backs. At grazing/degenerate
locations show uncertainty rather than inventing a well-defined width or normal.
Read-only mirrored surfaces are supports only where existing provider/binding eligibility
permits them; this never permits editing a mirrored object.

Predict the painting layer from nearby accepted same-layer contacts in a physical
neighborhood. Compare each proposed hit's excess view depth to the user's threshold.
Never compare only adjacent mouse events, and never let a rejected background hit become
the next prediction anchor. Continue across curved support; do not freeze the whole
painting to its first tangent plane. The existing keyboard abstraction owns the configurable
threshold-override modifier. Capture its state per input, with highlighted proposed targets.

Preserve captured 3D positions across later camera changes. Target restrictions and depth
settings affect new input; visibility changes do not erase existing paint. Occluding and
collision geometry remain distinct from eligible paint targets.

Group spans by same-sheet support, world-width overlap, transported axial direction and
compatible longitudinal stations. Reverse strokes agree; perpendicular crossings do not.
Recheck group consistency instead of using transitive proximity alone. Keep original
stroke records so merging never merges undo steps. User Keep Separate and branch decisions
are hard constraints. Stable ordering/tie handling must not depend on worker completion.

Directional strokes own flow evidence; Perimeter additions/erasures own coverage edits.
After a valid per-part chart exists, use CGAL regularized polygon union/difference for
boundaries, holes and component tests. A raster overlay is only a display cache. Resolve
3D sheets before planar operations. Disconnected/point-width regions and unsupported holes
remain visible findings; do not fill, drop or reinterpret them silently.

## 5. Target sheet and numerical formulation

These are proposed baseline methods for the new consumer. Qualification compares specific
alternatives; no production method is declared verified by a paper or successful solve.
The [research R1–R14](muscle_paint_050_research.md#4-research-coverage-and-concrete-approaches)
contains failure cases, derivations and references.

### 5.1 Supports, gaps and control normals

Supported samples retain their captured contacts. For each unsupported span, reconstruct
the captured projected course using interpolated view depth between qualified contacts.
Begin with linear depth; compare Hermite depth where endpoint slopes are reliable. Treat
perspective view depth and ray length correctly. A missing far contact remains unfinished.

Use the existing minimum-twist transport and sheet derivatives to orient width/normal
frames. Freeze the baseline and oriented normal field during a depth gesture. The first
candidate handle basis is `16*s^2*(1-s)^2`: zero value/slope at supported ends, full value
at midspan. Wheel movement changes total displacement from that baseline, not accumulated
vertex positions. One hold-and-scroll gesture is one transient undo step.

Compare constrained biharmonic displacement only where irregular support boundaries make
the simple basis inadequate. Supported ends stay fixed and captured course/coverage are
checked. A collapsed normal disables that handle with a reason. Penetration remains an
advisory finding; the tool does not route or repair the sheet.

### 5.2 Flow and material coordinates

Start with the addon's directed disk chart and stroke-aligned shared longitudinal stations.
Where flow interpolation is necessary, a constrained 2-RoSy field represents axial
directions (`exp(2*i*theta)` locally), with tangent transport across the sheet. Perimeter
painting does not add direction constraints. Main and child parts have separate fields.

Compare a positive-weight directed chart against stroke-aligned least-squares integration
on the same fixtures. Validate orientation, station monotonicity, singularities and
field/chart agreement. A smooth field alone cannot guarantee ordered noncrossing Fibers.
Never normalize zero directions or hide contradictory flow by averaging across a branch.

### 5.3 Fit the actual loft

Use ordinary editable cubic Bezier paths, derived from a constrained spline fit. For fixed
material correspondence the baseline surface is:

`S(u,v) = sum_i A_i(u) C_i(v)`

`C_i` are cubic longitudinal curves; `A_i` are piecewise-linear across-Fiber weights.
Form a weighted positional least-squares objective plus fairness and directional terms.
Keep endpoints and junction positions exact. Directional terms penalize the component of
the longitudinal derivative perpendicular to the prescribed tangent; a forward-derivative
constraint prevents collapse after choosing an orientation. Independently measure actual
angles: that quadratic penalty is not an angular-error guarantee.

Use Eigen for equality-constrained reference solves and qualify existing PIQP for linear
inequalities/order constraints. The addon's permanent-equality ordering heuristic is a
comparison baseline, not a general QP solution. Compare feasibility, objective, shape and
full preparation cost before adopting a solver configuration. No new solver dependency,
Python numerical loop, per-sample callback or automatic backend switching.

Normalize the native fit in a well-conditioned local frame, scaling distance tolerances
and objective terms consistently. Report final distances in model units and angles in
the documented units. Zero-span or ill-conditioned inputs require explicit findings;
coordinate normalization must not silently change the physical accuracy requested.

Reuse fixed basis/operators/factorizations only when their structural inputs match. Variable
correspondence, group selection and topology are outside the fixed linear subproblem;
do not claim global convexity or guaranteed convergence of the whole workflow.

### 5.4 Sparse rows and refinement

Keep boundary rows, attachment changes and branch roots. Evaluate admissible bands between
fixed candidate rows, then use the addon's shortest-path idea to propose few interior
Fibers. Its minimal-count claim applies only to that fixed candidate set and band test.

Fit jointly, measure independent error, then refine the responsible dimension: add a row
for transverse error, insert exact spline knots for longitudinal error, or refine evaluation
sampling for tessellation error. Record actual improvement after each refinement. A user
Fiber count is a constraint, not permission to relax accuracy. Respect existing topology
locks and native output caps; do not increase resolution indefinitely.

### 5.5 Independent assessment

Freeze the target sheet before assessing a fit. Use holdouts independent of fitting samples
and adapt around boundaries, narrow areas, gaps, high curvature and branch correction zones.
Report separately: bidirectional surface distance, coverage/boundary error, material-station
displacement, axial tangent angle, binding displacement and junction equality. Compare
tangents in a common frame; zero derivatives/undefined fields are unmeasurable, not zero error.

Initial acceptance uses explicitly labeled **adaptive sampled evidence**, including capture
and tessellation uncertainty. It must not advertise a certified global maximum. Benchmark
the research's cancellable distance-bound/Bezier derivative-bound methods as verification
comparators before making stronger claims. A budget exhausted before the required check
completes is inconclusive, never a pass. Unsupported/folded charts are representation errors;
do not turn this into a blanket rejection of tissue self-intersection.

## 6. True branches and closed loops

Use a separate chart for every main/child part. A child start boundary maps to an explicit
ordered interval on the main's outer curve. Insert Bezier knots without changing the curve,
create shared junction identities and distribute child roots monotonically. Keep current
restrictions: at least two distinct interior roots, no overlapping/shared-end root intervals,
no nested branches and no closed branching. Ambiguous connections require direct user choice.

For fixed stations, incorporate the existing fading seam-correction operator in the fit,
or evaluate that exact operator and feed residuals back during the qualified prototype.
Parity against native assembled output selects the implementation. Require exact shared
positions; tangent-plane fairness is optional, not forced equality of main/child fiber flow.

Insert any required root knot before final endpoint qualification and native assembly.
Keep root/source identities and material stations in the fit inputs so validation measures
the same part membership and junctions that the ordinary surface evaluator will consume.

Explicit closed unbranched paintings use an annular chart cut computationally at the chosen
binding cross-section. Fit cyclic splines/piecewise Beziers; retain intentional corners
within tolerance. The seam is not a duplicated authored endpoint or physical boundary.
Do not force smooth closure when it would erase the intended shape.

Extend the **shared** material correspondence with a cyclic map: retained source seam
identity/fraction, reversal, strictly monotone stations over one positive period and wrap
interpolation. Validate once across core/API/persistence/native boundaries. Preserve
existing open maps and closed default arc-length evaluation when no explicit map exists.
Topology edits, independence, graph copying, inspection and mirroring must preserve/remap
the seam and station identities. Test reversal and seam shifts under deformation, not merely
equal sample counts. Reject nonorientable construction rather than inserting a hidden twist.

## 7. Bindings, generation and updating existing construction

Start/end strips distribute endpoint proposals across their actual supporting SCPs. Closed
loops use their chosen binding regions; branch roots use junctions. Qualify ordinary
anatomical bindings through the existing confirmed exterior-placement service. Show target,
original/proposed locations and failures; do not infer continuous attachment from coverage.

Prepare qualified endpoint candidates before the final constrained fit, then validate the
evaluated bound Fibers and actual assembled Membrane. This prevents snapping after fitting
from silently invalidating the fit. No endpoint may jump to an unrelated bone or surface role.
Bone penetration is advisory; missing bindings, unsupported topology, ambiguous branches,
disconnected strokes and unmet measured accuracy block publication with prior output intact.

Stroke finish updates only the draft. Generate/Update is the sole document-construction
action. It automatically prepares and commits a valid current candidate as one transaction;
there is no mandatory separate Preview/Accept. Inspecting a failed attempted candidate is
read-only and cannot masquerade as accepted construction.

Preserve the generated Membrane identity on Update. Reuse Fiber/point/junction identities
where correspondence is verified; allocate new identities for new construction. Remove only
superseded tool-owned sources that are unreferenced and deletion-eligible. Do not overwrite
shared sources, move incoming attachments by index guesswork, or bypass topology locks to
satisfy a requested count. Explain the affected consumers and required ordinary resolution.
An ordinary manual edit of generated construction discards the painting, per specification.

## 8. Temporary history, invalidation and persistence

Extend History with optional typed transient contributions beside its ordinary document
transition. One chronological cursor owns both; there is no second paint Undo stack.
Entries share immutable paint data and existing document snapshots. Paint-only entries
do not increment document revisions, dirty the project, alter save checkpoints or trigger
anatomy calculations. No-op strokes create no entries.

Generate/Update entries also own the association change. Undo Generate removes only its
new construction and restores the ungenerated association while preserving all paint.
The next Undo removes the preceding stroke. Redo restores the same identities and accepted
results under existing replay/currentness rules. Transient navigation must not rerun prior
authored jobs or discard accepted asynchronous results for an unchanged document state.

Source/manual edits, ordinary deletion, successful Tissue creation and explicit Discard
capture draft removal in the same initiating entry. Undo restores that draft within the
session. Failed/cancelled edits do not discard it. Historical saves and autosave serialize
only the selected Document; undo data and paint definitions never enter project packages.

Apply the specification's lifetime table through shared change provenance and context hooks:

- Shape/topology changes or relative support movement discard affected drafts.
- An unchanged set of supports under one common rigid transform preserves the draft;
  update its assembly frame, without applying deformation twice to generated geometry.
- A common scale/shear is not rigid. Unrelated geometry edits and presentation metadata
  preserve drafts; new occluder/target membership still invalidates affected pending queries.
- Distinguish authored intent from intermediate asynchronous publication. Do not discard
  on a temporarily mixed parent/child pose during a common rigid update. Wait for coherent
  dependency evidence, hide stale overlays, and attribute any eventual discard to the
  initiating history entry rather than adding an unsolicited later undo step.
- Switching active paintings or editing contexts cancels unfinished interaction; completed
  drafts remain in their owning context until their documented discard condition. Closing
  a document releases drafts, history contributions and all outstanding generation jobs.

Use immutable stroke/delta storage; derived target sheets and fit caches are reconstructible.
Bound input, derived geometry, caches, jobs and failure evidence separately. Count memory
held by history and viewport leases, not only the active service. Under pressure evict
reconstructible caches first; if essential draft/history allocation cannot be admitted,
reject the new edit with an actionable reason. Do not silently destroy undoable strokes.

**Proposed persistence decision:** retain schema 9 during foundation/open-fit increments;
introduce schema 10 when explicit cyclic material maps are delivered. Continue reading
schemas 4–9, defaulting new correspondence metadata to absent without recalculation.
Save generated ordinary construction and the cyclic map only, never paint sessions.
Older applications must reject schema 10 rather than reinterpret its correspondence.
Update all typed remappers/readers with the map. This proposal changes no files today;
if schema 10 is taken by concurrent work, coordinate the next schema at implementation.

## 9. Execution, currentness and status

Use existing Job/coordinator execution with registered workload policies. Keep stroke
projection/coverage, draft-sheet work and explicit generation as distinct workloads with
shared lifecycle invariants. Reuse interactive coalescing; finish bypasses preview delay.
Fast brush feedback must not run a full constrained loft fit on every pointer update.

At begin, capture expected displayed resources. At dispatch, validate and lease owned
inputs; at publication, revalidate draft sequence, output reservations, source geometry/
frames, target/occluder membership, settings, generation association and edit capabilities.
An unrelated name/camera edit does not invalidate an unchanged numerical input. Compatible
accepted Manual geometry remains usable with its true provenance, without forced rerouting.

Maintain one pending generation per draft. Repeated requests coalesce/reject deterministically;
generation never publishes twice. Generation admission reserves the future construction
write and participates in ordinary pending-save coordination. Commit validated prepared
records/results atomically, creating history only on success; avoid placeholder anatomy or
empty failed-generation entries. Undo/discard/context changes cancel obsolete requests.
Unrelated dependency components remain usable. `Session.wait()` requires no Qt callback.

Retain the latest valid preview during computation; hide it when its geometry is stale.
Use existing Job/Preview states with domain findings, not an independent task state machine.
A Muscle Paint status projection reports draft revision, geometry freshness, pending work,
readiness/reasons, fit measurements and available corrections for UI and headless clients.
Pending computations must not change toolbar/inspector layout or steal focus.

Cancellation is polled in native batches and refinement loops. Record uninterruptible
factorization/library-call cost and bound input sizes before dispatch. Calibrate projection,
chart, fitting, validation and retained-memory budgets on real anatomy; do not inherit a
profiler-storage budget or invent a latency promise. If an alternative algorithm or policy
is needed, establish its failure/difference and discuss it before changing the agreed path.

## 10. Shared API and desktop design

The following are **planned operations**, not existing authoring APIs. Public records use
typed identities, metres/radians, explicit frames, revisions and bounded pages.

| Family | Planned contract |
| --- | --- |
| Existing `painting.describe/begin/append/finish/preview/commit/status/result/cancel` | Add `muscle_paint` consumer with draft identity, physical-width capability, support-set/view inputs and geometric effect descriptors. Finish commits a transient stroke, never a Membrane. Preserve old scalar arguments/results. |
| `muscle_paint.create/list/inspect/select/discard` | Manage named context-local drafts; bounded stroke/part listings and expected-revision checks. Selection is presentation, not anatomy mutation. |
| `muscle_paint.configure` | Accuracy/count, eligible-target policy and settings; declare which affect existing fit versus subsequent capture. |
| `muscle_paint.part.configure`, `muscle_paint.direction.set`, `muscle_paint.binding.set` | Explicit Keep Separate, branch choice, closure/seam, direction redraw and attachment-strip intent; shared validation and transient undo. |
| `muscle_paint.gap.begin/update/end/cancel` | One baseline-relative depth gesture and undo action; reject undefined normals. |
| `muscle_paint.generate` | Generate or update the associated ordinary graph; capture draft/association revision, return job token and auto-commit on valid completion. |
| `muscle_paint.status/cancel` | Inspect generation/provenance/findings or cancel work without discarding committed paint. |
| Existing `inspection.capture/geometry/export/release` | Register paint target/candidate evidence through the existing source adapter and snapshot leases; include blocked fit evidence explicitly labeled uncommitted. |

Use feature command declarations and declared transaction/variant/workspace policies.
Generalize commit edit-intent handling at the owning boundary rather than adding a
`muscle_paint` exception in command execution. Keep the current 4,096 default/16,384 maximum
query page sizes and candidate signatures. Compatibility routes for legacy scalar paint
continue delegating to the same service. No native handles in JSON.

Provide Paint Muscle alongside the existing construction creation tools; selecting it opens
a focused panel through the typed QML model composition. Keep Directional/Perimeter, width,
painting selection and Generate/Update readily accessible. Put target restrictions, depth,
accuracy/count and diagnostic detail in existing secondary-control/disclosure patterns.
Use shared `Ui*` controls, units, numeric dragging, theme and keyboard routing.

Show brush footprint/flow, main/branch distinction, proposed endpoint strips, gap handles
and direct correction of ambiguous roots. Show the best failed fit against paint when
requested. A simple valid strip needs only strokes and Generate. Named Paintings and return
from its Membrane must be discoverable without creating scene-tree nodes. No modal preview
gate, transient row shifts or extra close warning for unsaved temporary painting.

## 11. Method qualification and dependency policy

Use the research fixture matrix to choose among the narrowly identified alternatives:
linear/Hermite gap depth; analytic versus biharmonic handle displacement; directed versus
flow-integrated charts; dense equality versus PIQP inequality fitting; and adaptive sampled
versus bounded verification evidence. Record chosen quantities, tolerances, failure modes,
full costs and actual shapes. Avoid user-facing algorithm selectors without a confirmed need.

Reuse pinned Eigen/libigl, PIQP, CGAL and existing native query/Bezier/frame code first.
StrokeStrip, Directional and SurfaceBrush inform algorithms; their availability is not
authorization to add their complete dependencies or solver licenses. Review per-file/package
licenses, provenance and cancellation before porting. Keep original addon fixtures and
attribution; replace Blender publication and Python numerical preparation at their boundaries.

After three or four unsuccessful refinements, record why the approach failed and compare
a materially different researched candidate. Do not call another local tweak a new approach.
Escalate an actual product/algorithm change for discussion; complete independent work meanwhile.

## 12. References and acceptance authority

- [Confirmed behavior](specification_050.md), [research and source inventory](muscle_paint_050_research.md),
  [ordered implementation and acceptance](implementation_050.md).
- [StrokeStrip](https://www.cs.ubc.ca/labs/imager/tr/2021/StrokeStrip/): joint longitudinal
  parameterization; adaptation to supported 3D paint remains our work.
- [Directional](https://avaxman.github.io/Directional/tutorial/): line fields and integration;
  field smoothness alone does not certify an ordered chart.
- [libigl](https://libigl.github.io/tutorial/): constrained quadratic systems and displacement
  fields; useful existing building blocks, not a complete Muscle Paint implementation.
- [CGAL 6.1.1 polygon operations](https://doc.cgal.org/6.1.1/Boolean_set_operations_2/index.html):
  coverage operations after sheet/chart interpretation.

Acceptance requires real geometry and desktop/headless workflows, not successful API calls
or solver convergence alone. Release/version advancement occurs only after the plan's full
qualification; intermediate functional increments are not the complete 0.5.0 release.
