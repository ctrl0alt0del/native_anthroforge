# AnthroForge 0.2.0 implementation plan

Status: approved plan, implementation in progress. Product authority:
[specification](specification_020.md). Recovery and observed evidence:
[task record](tasks/020-construction.md). Baseline: 0.1.9 at `b539697`; its recorded
541-test qualification is historical until rerun against the changed implementation.

## Owners and interfaces

- Core owns immutable typed object identity, relationships, authored curve engines,
  Fiber substitution, accepted path/mesh results and revision declarations.
- Application operations own validation, topology locks, copies, reparenting, bindings,
  transactions and shared desktop/headless behavior. UI disabling is not enforcement.
- Native library owns drawing/fitting, evaluation, attachment blending, routing,
  resampling, surface/branch construction, bounds and spatial queries. No Python fallback.
- The existing coordinator owns queues and publication. New scheduling policies estimate
  path, routing, attachment, image and surface work; no new queue/lifecycle infrastructure.
- Persistence owns schema 3, embedded assets and atomic snapshots. Resource owners include
  current state, history, checkpoints, running jobs and viewport staging.
- Desktop owns presentation and tools, cached native picking, incremental Construction
  models and staged display. Headless operations do not import Qt.

Extend the shared command catalogue with object lifecycle, curve creation/engine conversion,
fiber copy/rebind, explicit junctions, surfaces and reference images. Retire direct control
surface attachments. Path engine inputs contain owned points/settings/constraints; outputs
contain owned samples, correspondence, bounds and diagnostics. Surface engines consume this
common path contract, never inspect a fiber type to choose duplicate geometry algorithms.

## Ordered increments

1. Consolidate specifications and implement typed objects, distinct relationship policies,
   generic lookup, ownership and schema 3. Add contract tests before migrating callers.
2. Replace embedded primitive curves with live references. Integrate consumer placement,
   both transform modes, Make Independent, deletion protection and topology locks. Preserve
   existing primitive geometry and desktop editing through the same application operations.
3. Implement Add Curve, Place Points, native drawing/fitting, cursor tools and images with
   headless import, embedded assets, calibration and tracing. Generalize the existing async
   authored-creation/undo contract; keep fitting and decoding off the UI thread.
4. Integrate the shared attachment subsystem with Fiber, native routing, endpoint rebind,
   closed paths and junctions. Retain editable engine parameters and accepted output on
   failure. Port numerical preparation/deformation loops as well as the routing solver.
5. Generalize native loft/patch/branch construction for Curve and Fiber inputs. Persist
   correspondence and provide explicit Realign. Validate constraints and live dependencies.
6. Complete Construction navigation, focused inspectors, workspace policies, picking,
   profiler attribution, examples, notices, portable packaging and release qualification.

Each increment must work through shared APIs and applicable desktop entry points before
proceeding. Keep old release version metadata until the candidate actually qualifies.
Use narrow adapters for Blender 5.0.1 drawing and addon kernels; preserve provenance.

## Acceptance matrix

| Area | Required evidence |
| --- | --- |
| Objects | Curve/image-only documents, no dummy anatomy, actual Fiber subclass substitution, independent copies and explicit sharing. |
| Transforms | Shared consumers with different/shared parents, both modes, no double transforms, no jump on switching/reparenting. |
| References | Source deletion protection, consumer deletion preserving sources, complete topology-lock reasons and unlocking. |
| Geometry | Compact provenance-backed fixtures for authored/routed paths, attachment deformation, closed paths, lofts, patches and branches; inspect actual shapes. |
| Editing | Drawing, insertion, snapping/offsets, conversion preview, unchanged selection, current-shape edits, rebind, cancel, one-action undo. |
| Lifecycle | Queued/running jobs, reservations, superseding changes, cycles/missing inputs, Manual provenance, historical saves, undo/redo and disposal. |
| Storage | Full editable round trips, old-schema rejection, embedded asset portability, calibration/replacement undo, Qt-free headless import. |
| Workspace | Shared construction inclusion, unassigned access, outside low-priority updates, valid running work survives workspace switch. |
| Performance | Profiler evidence for input/preparation/native/publication/picking, model churn and retained resources on representative workloads. |
| Release | Development gate, native/parity checks, headless checks, offscreen interaction/render checks and Windows portable package. |

Record intentional differences from addon behavior separately from parity failures.
Preserve original source .blend files; commit compact extracted fixtures and provenance,
not production binaries. Release needs ownership/coupling review independently of tests.

## Delivery constraints

Functions stay within 15 physical lines with cohesive helpers. Preserve existing scheduler,
save, undo, startup, units and skin-only export contracts. Reuse Issues, profiler, keyboard
manager and Ui/Theme controls. Follow the task-branch/checkpoint/push workflow; incomplete
checkpoints remain off main. No visible windows or desktop input while the user is gaming.
Report offscreen limits honestly; do not claim an unperformed interactive acceptance.

Finish 0.2.0 with package/build versions, API examples, notices, walkthroughs and source
archive naming updated only after the complete desktop/headless workflow is qualified.
