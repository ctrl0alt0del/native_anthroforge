# AnthroForge 0.3 — Shortcuts and parametric curves implementation plan

**Status: implementation in progress; no 0.3 release qualification yet.** Current
implementation and evidence are tracked in the [local review](tasks/shortcuts-parametric-030.md)
and historical [cloud continuation](tasks/shortcuts-parametric-030-cloud.md).
The plan below retains the original baseline diagnosis and required acceptance.
Product authority is
[specification_030.md](specification_030.md); apply the
[engineering guidelines](engineering_guidelines.md). The inspected baseline is 0.2.4
at `4029809`, including the completed shortcut research. The
[consolidation task](tasks/shortcuts-030-specification.md) delivers documentation only.

## Architectural diagnosis

The command catalogue already supplies shared desktop/headless operations, transactions,
validation and coordinated calculations. Extend it; do not build a second property-edit
or scheduling framework. The current Curve record assumes at least two authored points
and one of three engines. Engine changes replace settings while retaining those points.
Parametric requires engine-owned definitions and generated, stable point identities at
that boundary, not fake editable points appended to the existing assumption.

Current format loading accepts schema 4 exactly. Add explicit schema-4 decoding into the
new model and schema-5 writing, preserving existing results rather than recomputing them.
Current Fiber creation copies its source engine; evaluated conversion resamples paths.
Neither establishes the required exact Parametric-to-Bézier Fiber copy. The native VECTOR
handle representation can preserve every finite polyline segment; qualify its integration,
attributes, frames and material correspondence, not only its geometric locus.

Research captured 116 shortcuts and 40 drivers, all source shortcuts SCP-owned. Add VCP
acceptance cases explicitly. Their absence from those files is not a scope exemption.
Observed addon owner-backsolve and descendant-override behavior must be adapted to owned
transactions; Blender callbacks, RNA paths and timeout session caches are not architecture
to reproduce. Source observations are not dynamic parity or application performance proof.

## Ownership and interfaces

| Owner | Required responsibility | Boundary |
| --- | --- | --- |
| Core | Stable property/component references, typed descriptors, wrapper/driving definitions, inferred ownership, parametric authoring records and accepted-output provenance. | No Qt, Blender objects, native handles or property-owned shortcut policies. |
| Application | Semantic edit adapters, policy checks, formula graph, candidate validation, originating edit contexts, lifecycle/copies, persistence and publication. | UI and headless share operations; direct property edits do not acquire wrapper policies. |
| Native C++ | Restricted expression compilation/evaluation, curve sampling/conversion, numerical attachment preparation/backsolve and repeated geometry work. | Owned batched input/output; no per-sample Python calls or competing worker pool. |
| Existing coordinator | Task policies, dispatch-time capture, complete reservations/read validation, coalescing, safe cancellation and publication. | Formula and curve stages use existing history, checkpoint and workspace contracts. |
| Desktop | Shortcut tabs, formula/variable editors, policy controls, point display/picking, diagnostics and navigation. | Project shared capabilities through existing Ui/theme/tool models; no UI-only enforcement. |
| Storage/resource lifetime | Schema-4 reader, schema-5 writer, revision-selected data and reachability across history, checkpoints, jobs and viewport. | No persisted native/compiled caches or undo history. |

### Property and expression contracts

- Property references use stable entity/part/point/variable identity plus semantic field
  and component, not display names, list offsets or Blender RNA paths. Descriptors carry
  numerical type, unit, range, edit capability, getter and existing semantic edit adapter.
- Keep wrappers separate from this lower-level catalogue. Exposure, labels/order and
  attachment policy belong to wrappers; values and normal validation remain below them.
  Direct API/property edits still reject driven outputs through a shared write policy.
- Driving records hold virtual values, named input references and explicit output formulas.
  Infer control ownership through the graph and construction consumers. An attachment
  propagation edge does not confer shortcut ownership.
- Native compilation consumes an explicit symbol/type/unit layout and returns a reusable
  owned program plus diagnostics. Evaluation receives immutable values and returns typed
  results/errors; it never directly mutates documents or resolves names against UI state.
- Separate definitions/authored values, accepted effective property outputs and geometry
  results. Dependent jobs consume coherent validated snapshots. Formula publication must
  not recursively trigger wrapper policies or impersonate another user edit.
- A formula transaction carries one initiating wrapper policy context. Normal reevaluation
  without such a context uses authored attachment settings. Never accumulate policies
  from driven wrappers; preserve the initiating context through queued/native work.

### Shared API additions

Extend the existing catalogue with these operation families. Implemented signatures and
a runnable example are documented in the [development walkthrough](shortcuts_030.md).

| Family | Required operations and result information |
| --- | --- |
| Property discovery | Search/describe eligible properties and components, units, read/write capability, anatomy ownership and restriction reasons. |
| Shortcut lifecycle | Expose/hide, inspect/configure labels/order/vector mode, and edit a wrapper value with its policy context. Hiding does not remove a formula. |
| Driving formulas | Create/configure virtual controls, named inputs and output rows; enable/disable/remove relationships; inspect writers, dependencies, accepted values and failures. |
| Attachment policies | Inspect/configure eligible owner backsolve and descendant overrides; expose inferred ownership and unavailable-policy reasons. No manual owner/backsolve-target selector. |
| Parametric authoring | Configure XYZ/range/resolution, create/edit/remove variables through reference validation, inspect stored definitions and generated-point state. |
| Existing operations | Extend curve engine/configuration, Fiber creation, junctions, evaluation, duplication/deletion, transactions and project load/save rather than adding parallel lifecycles. |

Use existing IDs, job handles, structured errors and transaction conventions. Rename and
reorder must not retarget references. Apply existing reference-integrity policies to
deletion/copying; duplicate internal references once and retain explicit external inputs.
Expose pending/cycle/invalid/locked reasons through existing Issues and inspection APIs.

## Ordered integrated increments

### 1. Property, wrapper and model foundations

Inventory editable numeric fields in current command families and map each descriptor
to its existing semantic operation. Include shared construction and tissue part/side
settings; exclude derived transforms/geometry from writable targets. Add typed wrapper,
driving and accepted-value contracts with ownership and component-writer rules.

Establish engine-specific Curve authoring and schema-5 state contracts before callers
depend on them. Prepare explicit schema-4 decoding without changing accepted results.
Deliver ordinary wrapper discovery/exposure and a basic desktop entry point through the
same API. Contract tests cover lower-level property edits, exposure and ownership.

### 2. Qualify the native expression boundary

Assess [muparser](https://beltoforion.de/en/muparser/) and
[ExprTk](https://www.partow.net/programming/exprtk/index.html) against a common restricted
language/type/unit suite before choosing and pinning a dependency. Neither is qualified
today. Publish the supported operator/function/type table and notices with the chosen
adapter. Backend defaults must not enable conditionals, assignments, loops or I/O.

Qualify integer literals, promotion, real division, explicit integer conversion, dimensions,
finite/range failures and actionable error locations. A backend that treats every number
as floating point is not sufficient without an application-owned typed boundary.
Use the same compiled-expression service for formulas and XYZ/range evaluation.

Compare compile cost separately from repeated scalar and curve-batch evaluation. Test
owned symbol storage, concurrent jobs, bounded caches, cancellation boundaries and Linux/
Windows builds. Disable optional library worker pools. Record the actual selection and
evidence before dependent integration; never claim a candidate is faster based only on
its vendor benchmark. There is no silent production Python expression evaluator.

### 3. Driving graph and attachment edits

Add property/formula outputs and reverse dependencies to the existing graph. Detect
strongly connected formula components and their blocked downstream formulas without
discarding authored definitions. Reserve complete component outputs, capture inputs at
dispatch and revalidate every read before publication. Keep unrelated components running.

Evaluate candidate values in batches. Shared semantic validators determine independent
failures and jointly constrained groups, such as minimum/maximum thickness or a nonzero
vector. Retain only failing groups and blocked dependents; never use publication order
to choose a winner. Accepted values retain their input revisions and freshness.

Integrate native owner backsolve and descendant overrides with explicit gesture contexts.
Capture before mutation, preserve temporary bindings across pauses and async work, and
restore authored attachment settings. Cancel/undo must retire incompatible work and
restore the correct poses/bindings. Configure policies without moving anatomy. Complete
desktop driving controls and policy inspection as part of this increment.

### 4. Parametric paths and conversion

Implement native XYZ sampling over the typed interval, generated-point identities,
closure, bounds, frames and diagnostic results through the common path interface.
Apply supported deformers after formula evaluation with stable membership/correspondence.
Keep formulas and variables authored; generated coordinates remain calculated output.

Integrate native picking and existing branch creation with generated point identities.
Extend shared topology policy so any junction locks resolution in the inspector, API
and formula writes; expose exact reasons and unlock only when all applicable locks end.
Preserve existing source/follower and accepted Manual-result behavior. Formula-controlled
junction disagreement is validation, not permission to sculpt a formula indirectly.

Engine selection restores a stored Parametric definition or a valid default straight
line immediately. Leaving it uses current generated points and retains the inactive
definition. Maintain required identities and deformation-stage ownership; avoid double
deformation or exposing Apply/Bake. Add focused desktop formula/variable controls now.

Extend Fiber creation at its shared capture/copy boundary: clone the exact accepted
resolved path into an independent Bézier construction with straight handles and required
structural relationships remapped to new copy identities. Preserve dispatch/restart and
Manual provenance. Reject direct
Parametric selection on Fibers. Qualify closure, attributes, frames, attachments and
dependent surfaces separately from centerline coincidence.

### 5. Persistence and complete interaction

Complete schema-4 loading and schema-5 round trips, including inactive definitions,
formula/policy intent, exposure, accepted values and native resource provenance for the
selected revision. No blanket rerouting, recapture or recalculation on open. Existing
atomic saves, locks, checkpoints and historical-state resource selection remain intact.
No source file is rewritten merely by opening it.

Complete exactly two shortcut tabs, search, labels/reordering, context exposure, target
and input pickers, driven-value navigation and policy controls. All shows exposed controls
and accommodates multi-owner/unassigned entries with incremental/virtualized models.
Maintain stable numerical-field layouts,
focus and gestures while calculations/Issues update. Headless uses the same operations
without importing Qt. Keep native picking aligned with displayed accepted revisions.

### 6. Qualification and release

Add compact examples, fixture provenance, API signatures and walkthroughs. Profile
compilation, repeated expression evaluation, downstream geometry, preparation, publication,
model churn and retained resources. Update computation inventory/history in the same
runtime changes with rationale, previous/new approaches and actual evidence.

Run the acceptance matrix, development gate, native/parity tests, Qt-free headless checks,
background/offscreen interaction/render inspection and portable checks. Review ownership
and coupling separately from test counts. Only then advance package/build versions and
deliver `dist/0.3.0/AnthroForge.dist` plus `dist/AnthroForge-0.3.0-source.zip`.

Each increment must work through its shared API and applicable desktop entry points
before advancing. Apply the 15-physical-line function limit with cohesive helpers, not
compressed code. Follow task-branch/checkpoint/push and validated-merge practices;
intermediate checkpoints are recoverable work, not completed release claims.

## Acceptance matrix

| Area | Required evidence |
| --- | --- |
| Properties/wrappers | Same value through ordinary property and wrapper; only wrapper activates its policies; exposure/hiding preserves formulas; generated/locked/driven fields remain protected through UI and API. |
| Ownership | One SCP, one VCP, multi-object chains, shared construction, unassigned controls and ownership changes. Ordinary child motion does not create extra owners. No manual owner/backsolve selector. |
| Writers/vectors | Component and whole-vector conflicts; Uniform sets equal components; explicit proportional formulas; disabling/removing preserves current values and restores editability. |
| Types/units | Integer/real literals and promotion, division, round/floor/ceil, dimensional validity, local/world read inputs, invalid names/references, nonfinite values and target ranges. |
| Failures | Cycles with dependent formulas, independent successful outputs, coupled invalid groups, missing inputs, recovery, retained provenance and deterministic results independent of output order. |
| Attachment parity | Pubis Arc Angle descendant override, Cheekbone owner backsolve, all supported override modes, no unintended rotation/backsolve, Keep/off defaults and only initiating A's policy through chains. |
| Gestures/lifecycle | Pause longer than the addon's cache timeout, live drag/typing, cancellation, undo/redo, coalescing, queued/worker execution, overlapping outputs, newer edits, Manual inputs, workspace priority and historical saving. |
| Parametric geometry | Circle/arc/general XYZ fixtures, interval and point count, closed/straight closure, no duplicate seam endpoint, transforms, Hook/lattice order and stable membership. Inspect actual resulting shapes. |
| Junctions/conversion | Formula-source following, disagreement errors, resolution lock/unlock including API/formulas, restored definitions, current generated points when leaving, exact independent Fiber path and direct-Fiber rejection. |
| Consumers/failure display | Shared primitives/surfaces, attachment/material stability, unchanged source after Fiber creation, accepted Manual capture, retained geometry and non-authoritative initial failure placeholder. |
| Persistence | Representative 0.2.4/schema-4 load with unchanged geometry, bindings/poses/identities/results/workspaces; continued attachment edits after load; schema-5 round trip and old-reader rejection; no startup blanket work. |
| Performance/resources | Compile versus repeat cost; preparation/native/publication/UI attribution; cancellation, cache invalidation, history/job/viewport retention and release, no Python numerical fallback. |
| Delivery | Development/native/parity gates, Qt-free headless, background/offscreen GUI, relocated Windows portable build, notices/examples and independent ownership/coupling checklist. |

Use the [116-shortcut/40-driver inventory](research/shortcuts_030/inventory.md) to select
pelvic multi-output chains, rib/sternum relationships, affine local Hook controls, uniform
scales and digit parameters. Add VCP tissue numerical fields, since the inspected source
files contain no VCP shortcuts. Preserve source hashes and compact fixture provenance;
do not commit production .blend/anatomy assets or migrate them as part of qualification.

Compare canonical geometry, retained material/binding records, poses and subsequent
attachment behavior when qualifying compatibility. A successful load, renderer screenshot
or solver return alone is insufficient. Record intentional differences separately from
parity failures, including generic parametric examples versus the source's four-point
Bézier loops.

## Evidence, defaults and current limits

Confirmed defaults are t in 0..1, valid straight-line first definition, Backsolve off,
override Keep, exact rather than fitted Fiber conversion and direct one-action edits.
Reuse existing creation-scale, numerical-control, lifecycle and presentation conventions;
do not introduce adaptive sampling, inverse parameter fitting or new approximation gates
under the guise of implementation defaults.

The [expression qualification](research/shortcuts_030/expression_qualification.md) selected
the restricted native typed compiler after candidate comparison; no parser dependency
was added. Formula evaluation, generated-point interaction and schema-4 reading exist
on the feature branch. [Windows review](research/shortcuts_030/windows_review.md) records
actual source-addon parity, UI and old-executable compatibility evidence. Release
qualification remains unfinished, including the generated-point reference policy.
Fixed sampling does not prove analytic continuity, and exact finite-path conversion does
not promise an exact unsampled analytic curve.

Validate in the background while the user uses the computer. Offscreen checks establish
only their observed render/interaction scope, not unperformed interactive acceptance.
The original documentation-consolidation task did not require an application rebuild;
the subsequent runtime implementation follows the full delivery gate above.
