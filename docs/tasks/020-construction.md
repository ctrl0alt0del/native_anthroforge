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

No standalone curve viewport/Construction UI or path-result job exists yet. BEZIER is
the only evaluated engine; POLYLINE/ROUTED remain model contracts, not implemented engines.
Images/Fiber/Surface records exist but their production operations/native algorithms/UI
remain unfinished. Direct control.attach is still present and must be retired as planned.
No 0.2.0 release qualification or version bump has occurred.
The current coordinator, attachment kernels, Issues, profiler, transactions and
staged renderer must be extended at their owning boundaries, not duplicated.

## Verification

Read-only inspection completed; `main` and fetched `origin/main` both at `b539697`.
Current shared-curve increment: `uv run --no-sync pytest -q`: 573 passed (32 new cases).
Ruff check/format and mypy pass. The full native/development gate and 0.2.0 GUI/package
qualification have not run. One earlier full run saw the existing global native-allocation
count test change during collection; targeted and subsequent full run pass. Investigate
resource ownership if this recurs; do not weaken the allocation assertions.
An initial suite overlapped source editing and its subprocess saw an intermediate invalid
dataclass definition; it is not baseline evidence. Subsequent checks used stable content.
No visible applications or desktop input permitted while the user is gaming.
Use background/offscreen checks and state their limits.

## Next actions and blockers

1. Complete the standalone Curve engine/result contract: native owned path buffers,
   BEZIER/POLYLINE evaluation, engine strategies, resource lifetime/persistence and coordinated
   path jobs. Extend remaining ports/workspace/Issues/profiler clients to generic objects.
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

## Recovery inputs

Normal Windows environment and native toolchain already exist in this checkout.
Addon migration reference: `C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
Original geometry references remain under `E:/development/WIP_models`; do not commit
large source assets. Copy compact reproducible fixtures with source provenance.
Push every coherent checkpoint; incomplete work stays on this branch.
