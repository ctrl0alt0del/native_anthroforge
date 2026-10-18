# AnthroForge 0.2.0 construction objects

- Task branch: `codex/020-construction`
- Integration branch: `main`
- Starting revision: `b539697`
- Status: in progress; not release-ready
- Last updated: 2026-10-18, Europe/Bucharest
- Active writer: local desktop implementation chat

## Outcome and acceptance

Implement the approved [0.2.0 specification](../specification_020.md) and
[implementation plan](../implementation_020.md). Includes first-class curves,
reference images, fibers and curve-based surfaces in desktop and headless use.
Muscles and soft tissues belong to 0.2.1. Preserve the unrelated root `__init__.py`.

## Current state

Consolidated specification and plan are committed. Baseline docs link to the superseding
contract; the previous Free/Controlled normative paragraph now describes curve engines.
Added typed construction objects, Fiber subclass/binding cardinality, generic registry,
distinct parenting/membership validation, incremental construction changes and schema 3
round trips. Old schemas are rejected. Primitives now store CurveUse references; owned
ResolvedPrimitive inputs exist only at evaluation/edit presentation boundaries. Primitive
creation, point/handle editing, duplication, deformers, deletion, dependencies, scheduling
and existing desktop authoring projections use these references. Generic curve creation/
point edits, object rename/transform/reparent/delete/inspect, primitive.from_curves,
primitive.curve_mode and primitive.make_independent are integrated with shared commands.

Native owned paths now evaluate BEZIER and exact POLYLINE, preserve closed-path starts,
omit duplicate endpoints, and retain allocations through read-only array leases. Resources
have typed mesh/path/image catalogues, retained across history/checkpoints/jobs and snapshots.
Schema 3 stores path buffers and deduplicated embedded PNG/JPEG sources; Pillow is promoted
to a runtime dependency and applies EXIF orientation once without Qt. Save/inspection callers
use complete resource snapshots. Native path/typed-resource tests and style checks pass.
Coordinated path jobs now publish accepted buffers/provenance and drive primitive consumers.
Manual source edits retain accepted construction (including inputs for control deformers),
report pending upstream state, and reevaluate live consumers after explicit path publication.
Native sampling reuses accepted paths and preserves existing body/loft sampling behavior.
Curve jobs use the common cancellation/history/checkpoint contracts and task Issues.
Generic workspace associations determine curve editability and task priority.
No standalone curve viewport/Construction UI exists yet; ROUTED is not implemented in the
standalone engine and is explicitly rejected by native path dispatch.
Images/Fiber/Surface records exist but their production operations/native algorithms/UI
remain unfinished. Direct control.attach is still present and must be retired as planned.
No 0.2.0 release qualification or version bump has occurred.
The current coordinator, attachment kernels, Issues, profiler, transactions and
staged renderer must be extended at their owning boundaries, not duplicated.

## Verification

Read-only inspection completed; `main` and fetched `origin/main` both at `b539697`.
Current shared-curve increment: `uv run --no-sync pytest -q`: 573 passed (32 new cases).
Owned path/resource checkpoint: 586 tests passed, Ruff and mypy pass; native build/contract
and clang-tidy on the modified curve/path implementation pass. Full gate on this increment
has not yet run; the preceding shared-curve full-gate evidence remains scoped below.
Coordinated accepted-path increment: `./tools/check.ps1` passed with 596 tests, full native
style/build/contract checks, Ruff, mypy, numerical imports and doctor. Includes exact old/new
native sampling comparisons for transformed open/closed lofts and body deformation; this is
not a claim of complete new fiber/drawing/surface Blender parity or interactive acceptance.
`./tools/check.ps1` passed on the shared-curve checkpoint: native build/contract, native
and script style, Ruff, mypy, all 573 tests, numerical imports and doctor. 0.2.0 GUI/package
qualification has not run. One earlier full run saw the existing global native-allocation
count test change during collection; targeted and subsequent full run pass. Investigate
resource ownership if this recurs; do not weaken the allocation assertions.
An initial suite overlapped source editing and its subprocess saw an intermediate invalid
dataclass definition; it is not baseline evidence. Subsequent checks used stable content.
No visible applications or desktop input permitted while the user is gaming.
Use background/offscreen checks and state their limits.

## Next actions and blockers

1. Extend remaining inspection/Issues/profiler clients to generic objects, including path/image
   memory attribution; retire control anatomical attachments in favor of ordinary relationships.
2. Add Construction UI and standalone curve editing/creation; curve consumers already have
   shared command operations. Then complete native drawing, embedded reference images,
   Fiber bindings/routing/junctions and generic surfaces in the planned order.
3. Keep removing contradictory active baseline text as each boundary is integrated.
4. Run native/parity, headless, offscreen and portable release qualification before merge.

Important findings: ordinary parenting and consumer frames need an atomic rebind to avoid
double transforms after a new shared ancestor is introduced. Local path/local-pose ports
must not depend on the consumer's world pose, otherwise a pure SCP transform unnecessarily
obsoletes geometry jobs. `consumer_parenting.py` and shared-curve regression cases cover
these boundaries. Newly created primitive children now capture their origin attachment
through the existing evaluation contract. Profiler changes include construction-object
fields (e.g. points), not a fictitious change to the primitive reference definition.
Path prerequisite admission must avoid inline publication before its consumer is registered;
queued consumers already waiting on that path are retained rather than superseded. Regression
coverage preserves the first construction job during an SCP pose edit. Generic paths retain
analytic tangents; Blender body deformation separately reconstructs bevel tangent bisectors.
Sharing the body-specific tangent preparation with loft sampling caused a measured parity
difference and was corrected at the native frame boundary, not by relaxing tolerances.

## Recovery inputs

Normal Windows environment and native toolchain already exist in this checkout.
Addon migration reference: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Original geometry references remain under `E:/development/WIP_models`; do not commit
large source assets. Copy compact reproducible fixtures with source provenance.
Push every coherent checkpoint; incomplete work stays on this branch.
