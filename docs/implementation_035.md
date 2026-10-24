# AnthroForge 0.3.5 — Mirroring implementation plan

**Status: Implemented — release qualification in progress.**

See the [runtime walkthrough and observed evidence](mirroring_035.md) and
[recovery/qualification record](tasks/mirroring-035.md). The original ordered plan
and acceptance requirements remain below; unperformed interactive checks are not claimed.

Product authority: [specification_035.md](specification_035.md). Follow the
[engineering guidelines](engineering_guidelines.md) and
[work-continuity workflow](work_continuity.md). This preserves the ordered runtime plan;
the original consolidation delivery was documentation only. Runtime now uses project schema 6 with
schema-4/5 loading. Qualification status is recorded separately from this original plan.

## 1. Baseline diagnosis and source inventory

The pre-0.3.5 integrated baseline used typed authored objects, separate accepted results,
role-aware surface providers, a single coordinator, shared application operations,
staged viewport resources, Issues and the runtime profiler. It had no live anatomical
mirror model. Existing migrated opposite-side bones are independent authored objects.
The separate unfinished 0.3.4 task is not implicitly merged or qualified by this plan.

Current `SurfaceReference` distinguishes target identity and surface role; the provider
enumerates authored anatomy. Extend this owning reference/provider boundary with spatial
instance identity rather than fabricating SCP wrappers or teaching each caller to find
mirror objects by name. Trace affected attachment, routing, snapping, measurement,
inspection, workspace, selection and persistence callers before implementing them.

The following addon paths are relative to the original `anthroforge` addon root, not
standalone import dependencies. They record inspected implementation, not new runtime
parity tests. Preserve original source and fixture provenance during qualification.

| Addon source family | Observed capability to retain or intentionally replace | Standalone owner / required evidence |
| --- | --- | --- |
| `ui/panels/scp_create_sections.py`, `properties/scp_properties.py`, `core/scp_runtime/mirror_roles.py` | Mirror Children, inherited/opt-out/nested rules, axis and shift | Core rule resolution; hierarchy and plane fixtures |
| `core/scp_runtime/mirror_scene.py`, `viewport_picker.py` | Evaluated reflected proxies, stable object reuse, instance-aware picking | Provider/resource/picking boundaries; stable IDs and no allocation growth |
| `operators/fiber_attachment.py`, `core/visualization/attachment_mirror_rules.py` | Inherit/explicit-plane conflict resolution and attachment settings | Shared policies and Issues; incompatible rules and explicit midline sharing |
| `core/vcp/surface_reference.py`, `fiber_instance.py`, `core/visualization/fiber_instance_runtime.py` | Source/mirror surface roles and mapped bindings; independent route solving in some cases | Retain references; replace independent solving with strict reflection plus findings |
| `core/visualization/volume_instance_runtime.py`, `vcp_mirror_runtime.py` | Muscle stages, independent mirror evaluation and mirror-specific stacking | Reflect corresponding source stages only; asymmetric-support fixtures prove no drift |
| `core/vcp/free_surface_stations.py`, `core/visualization/branched_surface_capture.py` | Mirrored-row ordering, central-row handling and unsupported branches | Common surface evaluator; no duplicate complete-surface instance |
| `core/vcp/fiber_symmetry.py`, `app/use_cases/fiber_create.py` | Half-path loop expansion and seam validation | Common curve/Fiber construction; editable half and shared seam fixtures |
| `core/topology/symmetry.py`, `properties/topology_properties.py` | Separate skin/custom-plane workflow | Historical context only; no skin or oblique anatomical plane scope |

Blender's [Mirror modifier reference](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/mirror.html)
is external context, not the addon entity-mirroring contract. Do not import its arbitrary
Mirror Object planes, multi-axis options, Apply or editing behavior into this release.
The [recommendations](../standalone_application_recommendations.md) provide identity,
resource and regression motivations; strict reflection supersedes independent mirrors.

## 2. Responsibilities and public interfaces

| Owner | Responsibility and preserved boundary |
| --- | --- |
| Core | Immutable rule/instance references, stable source/rule identities, inheritance, required-construction sharing and symmetric-half definitions. No Qt or duplicate authored hierarchy nodes. |
| Application | Rule validation, shared read-only capabilities, reference mapping, dependency registration, operations, coherent transactions, persistence and safe removal. |
| Native C++ | Batched reflection/frame/query preparation, bounds, orientation handling and repeated numerical validation. No Python geometry-query loops or per-sample callbacks. |
| Existing coordinator | Source/instance readiness, complete reservations/read sets, coalescing, cancellation, publication and historical/save semantics. No second executor or mirror solver. |
| Desktop | Source-side direct controls, read-only instance selection/inspection, Select Source, workspace display and staged source/mirror publication. Existing Ui/theme/tool/keyboard infrastructure. |
| Resource/storage lifecycle | Shared source assets, orientation-aware query/render resources, revision-selected metadata and leases across state/history/checkpoints/jobs/staging. No duplicate reflected geometry catalogue. |

Extend the shared command catalogue with operation families for rule and inheritance
configuration, conflict-plane overrides, instance/usage inspection, same-target attachment
choices, affected-consumer queries, mirrored-row settings, symmetric-loop creation and
source navigation/presentation. These were the planned operation families. Concrete runtime signatures are documented
in the [walkthrough](mirroring_035.md#shared-operations), with typed contracts and tests.

Instances expose source/rule identity, plane revision, surface role, source-result
revision/readiness, reflected frame and resource ownership. Keep geometry readiness
separate from mapped attachment findings. Mutation policies reject mirror edits through
every entry point; changing view state remains allowed. Reference removal validation
precedes any state mutation and returns navigable blockers without partial deletion.

## 3. Integrated delivery order

### Increment 1 — Foundation contracts

- Add rule resolution and instance/reference records at the existing model boundaries.
  Preserve shared source/rule identities through plane edits and consumer changes.
- Extend surface references/providers and shared capabilities, not SCP-specific patches.
  Add conflict, removal, redundant-instance and read-only policies before UI adapters.
- Define versioned serialization of the new relationships, supported-version handling
  and selected-revision ownership before modifying the runtime format. Do not infer
  pairings for existing independent objects or rewrite accepted source geometry.
- Deliver headless operations and source rule controls together; mark capabilities not
  yet supported explicitly. Contract tests must precede migrating provider callers.

### Increment 2 — Reflected geometry and queries

- Reuse source geometry with an instance reflection frame and orientation metadata.
  Reflect complete world-space results once; preserve all tissue stage/fallback labels.
- Extend native bounds, picking, surface capture, confirmed-placement validation,
  routing providers, measurements and inspection through the common instance contract.
  Preserve material identity under winding changes; do not resample or nearest-rebind.
- Stage source and mirror from the same displayed revision, with retained source leases.
  Query caches include instance/rule/result revisions; do not rebuild source acceleration
  or Boolean resources separately for every equivalent mirror consumer.
- Integrate viewport selection and read-only inspection with the shared operations.

### Increment 3 — Relationships and lifecycle

- Map counterpart bindings, roles, controls and junctions; support explicit midline
  target sharing. Validate mismatches without running an independent deformation stage.
  Include mirrored incoming bindings in existing topology-lock and source-deletion policies.
- Register actual source/provider dependencies. Missing mapped targets and conflicts
  create Issues without blocking valid reflected display. Detailed geometric findings
  remain on demand and revision-qualified.
- Integrate mirrored providers into source stacking; exclude own-mirror automatic
  candidates and reject dependency cycles. Never introduce mirror-specific stacking.
- Qualify rapid rule/source edits, cancellation, stale rejection, Manual provenance,
  undo/redo, historical saves and referenced-rule removal before continuing.

### Increment 4 — Symmetric construction and complete interaction

- Implement mirrored rows through the existing surface evaluator with central-row
  deduplication and explicit branch restrictions. Suppress redundant whole instances.
- Add one-action Create Symmetric Loop on an existing open Curve/Fiber. Validate plane
  seams and one-sided interior, preserve supported engine/binding contracts and expose
  only the authored half for editing. Reject incompatible engines rather than substituting.
- Complete source controls, Select Source, Both/Source only/Mirror only, hiding/isolation
  and searchable blocker navigation without additional tree nodes or mandatory dialogs.
  Keep source shortcuts read-only in mirror inspection and avoid duplicate driver chains.
- Round-trip rules, identities, half-path definitions, target choices and presentation;
  reopening must not launch blanket source recalculation or independent mirror work.

### Increment 5 — Qualification and release

- Update computation inventory/history for actual reflection, query/cache, scheduling
  and publication changes: old/new approaches, reasons, evidence and remaining limits.
- Capture representative profiler reports, geometry fixtures and UI evidence. Review
  ownership/coupling separately from test success; complete all clients before release.
- Only after qualification update release versions, notices, examples and API walkthroughs.
  Deliver one `dist/0.3.5/AnthroForge.dist` and one companion source archive under the
  existing packaging policy. No new export, migration or skin feature is implied.

## 4. Acceptance matrix

| Area | Required evidence |
| --- | --- |
| Rules and identity | Disabled/default rules; inheritance and opt-out; nested sources; all axes/shift; conflicts and explicit overrides; one instance per source/rule, different-rule instances; rename and plane edits retain IDs. |
| Strict geometry | Compare native reflected source coordinates/frames and corresponding stages under nonuniform transforms; verify winding/normals and tolerance. Asymmetric obstacles/supports never reroute or reshape mirrors; profiler confirms no independent solvers. |
| Construction sharing | Multiple consumers share a mirrored hook/cage/curve/junction. Connected endpoints remain connected. No repeated authored graphs or accidental finger/toe copies. |
| Surface relationships | Source/mirror and base/final roles remain distinct through snap/capture/query; explicit midline sharing; retained material references; missing target and mismatch Issues without loss of valid reflection. |
| Stacking | Valid original-on-other-mirror provider; own-mirror exclusion; cyclic rejection; changed original final output reflects exactly, without mirror-specific provider solving. |
| Symmetric construction | Half-path one-sided/plane validation, shared seams, selected engine restrictions, Fiber bindings, edit/cancel/undo; central mirrored rows; rejected branches; no redundant complete-object mirrors. |
| Editing and presentation | API, property wrappers, G/R/S and component tools reject mirror mutation. Viewport selection identifies instance; no tree nodes; Select Source works; view-only hide/isolate does not change computation. |
| Display and queries | Source/mirror switch corresponding revisions together, including previews; hover/click agree with displayed geometry; accepted consumers cannot consume preview data. |
| Lifecycle and failure | Queued/running source edits, cancellation/supersession, complete reservations, stale rejection, Live/On Release/Manual, low-priority outside consumers, source failure retention, undo/redo and historical saves. |
| Removal and persistence | Rule removal blocked atomically with searchable references; reload stable IDs/choices/workspace and accepted appearance; no duplicate payloads, native handles or undo history; no automatic pairing of old counterparts. |
| Resources and performance | Profiler separates source computation from reflection/query preparation and publication; measure warm edits, plane changes, picking, memory and leases on crowded assemblies; repeated edits do not grow retained resources without owners. |
| Delivery | Development gate, native checks, Qt-free headless operation, background/offscreen GUI/render and portable-package checks; inspect actual shapes and report unperformed interactive acceptance honestly. |

Use compact provenance-backed addon fixtures for hierarchy rules, hook elbows, mirrored
Fibers, mirrored rows, loop seams, tissue stages and stacking. Add deliberately asymmetric
supports to prove the intentional difference from independent addon evaluation. Preserve
source assets outside Git's production anatomy payloads and distinguish shape parity,
intentional product differences and numerical failures.

## 5. Documentation delivery and continuation

The [consolidation task](tasks/mirroring-035-specification.md) records current documentation
checks, not runtime acceptance. Update active recommendations, roadmap, architecture,
authoring API and addon audit together; preserve historical evidence and label source
observations separately from confirmed behavior. Validate links and decision coverage.

Runtime delivery follows task-branch/checkpoint/push and validated-merge practices,
preserving unrelated work and the root legacy `__init__.py`. Keep Python 3.12, C++17 and
Qt/PySide 6.12.0. Every new function stays within 15 physical lines using cohesive helpers.
Background-only validation must not take over the user's desktop. Do not claim portable,
interactive or anatomical acceptance from unit tests or offscreen assertions alone.
