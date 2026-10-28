# 0.4.2 preparation: remaining cross-thread recommendations

Status: **coverage audit complete; R01–R03 and R06 extensions delivered in 0.4.2**.
The table below preserves the pre-implementation audit. See [delivery](inspection_042.md)
and [current validation](tasks/inspection-workflows-042.md) for implemented extensions and limits.
Audited on 2026-10-28 against 0.4.1, commit
`6970a5713e2812e5e7962238f6ffe905e28f76be`.

This reviews all **66 consolidated requirements and 132 original recommendation
items** in the [recommendation inventory](../standalone_application_recommendations.md).
It compares current code, public operations, desktop entry points, existing tests and
release evidence. It is not a fresh execution of those tests, a performance benchmark,
an interactive acceptance claim or a commitment to implement everything in 0.4.2.

The six source lists contain S1: 22, S2: 21, S3: 18, S4: 26, S5: 24 and S6: 21 items.
The corrected S3 is included. The originally duplicated S4 attachment is counted once.
The existing source-to-requirement appendix preserves all individual mappings; the
matrix below accounts for every resulting requirement. Later confirmed product
decisions take precedence over original suggestions.

## What remains

These are the distinct gaps after removing duplicates and already-delivered work.
“Partial” means a useful implementation exists, but not the entire original proposal.
The IDs R01–R18 identify entries in this audit, not approved release requirements.

### Extensions to existing workflows

| Item | Existing capability | Remaining work and boundary | Requirements |
| --- | --- | --- | --- |
| R01 — Shared operation status providers | Activity, Issues, shortcut propagation status and SkinStatusProvider already exist. | Extend operation-specific readiness/eligibility providers to the other UI consumers identified in the skin follow-up. Replace duplicated workspace/document gates with shared application assessments and notifications. This is a confirmed architectural follow-up, not a request for another global manager or polling loop. | B04, C07, G02 |
| R02 — Consistent spatial findings | Tissue checks identify crossing/degenerate triangles and can frame witnesses. Skin has advisory quality/coverage reports. | Give skin and other non-tissue findings suitable selectable spatial witnesses, stage/revision-aware navigation and matching evidence exports. Broader containment, measured penetration and consolidated scale/conditioning explanations are not a general diagnostic capability today. Keep unsupported measurements explicitly unavailable; diagnostic extensions do not authorize automatic geometry repair. | A05, F10, G01, G03 |
| R03 — Explain attachment placement and recovery | Exterior-qualified placement, snap previews, parent/role/material bindings, frames, pin checks and explicit rebind are implemented. | Present requested versus accepted placement, displacement, rejecting collider and local-exit/approach evidence together. Expose relevant existing recovery operations from findings. Complete the connection between route/contact evidence, loft participation and support-distance inspection; do not reimplement the existing route trace. Named anatomical regions depend on R16. | D02, F05, F09, G03 |
| R04 — Measured tightening workflow | ROUTED has budgets, length weighting, warm/cold behavior and diagnostic trials. | No dedicated tightening operation combines a bounded proposal with before/after shortening, displacement, clearance and fixed-anchor checks, then a coherent undoable batch. Existing solver controls and development experiments are not this workflow. Qualify the intended numerical approach before implementation; more steps are not a percentage of tightening. | D07, C02, H06 |
| R05 — Additional local tissue profile controls | Material correspondence, four-station Section Profiles, proportional depth scaling and independent sides are present. | Allow additional local profile controls at explicit material positions where four stations cannot describe the shape. `SectionProfile` still requires exactly four depths and peaks. This changes the model/evaluator, not just the inspector; discuss interpolation and compatibility before changing algorithms. | E02 |
| R06 — More useful anatomical inspection views | Category presets, workspaces, saved cameras, axis/restore views, sections/cutaways, silhouettes and two-point XYZ/distance measurements exist. | Add task views that select relevant supports/neighbors rather than only changing category visibility; dedicated width/depth or cross-section measurements and obstruction-focused framing. Existing frozen point rulers are not continuous section measurements. | F07, F09, F10 |
| R07 — Concurrent independent views | Presentation is separate from anatomy; workspaces and comparison modes retain cameras/styles. | Display two or more live viewports with independent presentation and optional synchronized cameras. The main window currently contains one 3D Viewport; Before/After/Overlay uses that viewport. | F01, F07 |
| R08 — Intermediate calculation previews | Last accepted geometry stays visible; explicit tissue previews and bounded route diagnostics exist. | Where worth the cost, stream useful provisional results during a long calculation. Route trial inspection is collected by a separate diagnostic job, not a live stream from every ordinary solve. Requires explicit revision, lifetime and non-authoritative-preview contracts. Optional per operation, not a reason to stream every stage. | C06, F09 |
| R12 — General experiments and reproducible edits | Frozen inspection exports, shortcut baselines/replay, profiler files and scripted regression fixtures exist. | Extend reproducible semantic capture beyond shortcut edits, and provide reusable frozen-input parameter sweeps/comparisons for construction, fibers, tissues and skin. Current replay explicitly becomes incomplete for unsupported authored changes. Developer test scripts are not an integrated experiment workspace. | H06, I03 |

### Performance work that needs measurements first

These are concrete missing mechanisms, **not demonstrated bottlenecks**. Profile a
representative case before choosing which to implement or claiming a speedup.

| Item | Existing capability | Remaining work and distinguishing evidence | Requirements |
| --- | --- | --- | --- |
| R09 — Aggregate cache budgeting | Individual cache byte/entry limits, ownership tracking, cache events and job resource admission exist. | Coordinate aggregate retained-cache memory instead of independently granting each cache its own allowance; include cost-aware eviction/accounting. The persistent FAST-weight disk cache also has no retention quota. Job memory admission is a different responsibility. Measure long-session retained memory and rebuild/thrashing cost. | B09 |
| R10 — Share identical work already running | Completed native preparations/results are cached; compatible queued requests coalesce. | Reuse identical in-flight preparation across separate consumers. For example, tissue preparation currently performs cache lookup, builds outside the cache, then stores: concurrent misses can both build. This establishes a possible duplicate path, not its frequency or cost. Capture overlapping identical keys before adding shared-job ownership/cancellation machinery. | B03 |
| R11 — Cheaper display updates | Native render chunks, staged complete publication and shared mirror resources exist. | Reuse unchanged GPU topology and update only changing position/normal data where valid; optionally lower display tessellation/helper detail during navigation. The Qt mesh adapter currently clears and installs a full interleaved chunk after an asset change. Keep computation/attachment geometry unchanged and measure upload/frame time first. | C05, F08 |
| R18 — Close profiling and responsiveness evidence gaps | Input/task/native/UI/frame traces, invalidation reasons, cache events, retained-resource snapshots and production experiments exist. | Extend attribution only where current reports leave consequential native subphases unknown; measure complete gestures on the current combined app in repeatable cold/warm trials. CPU-owned resource estimates omit Qt/GPU/allocator overhead. Actual physical display/input latency is not established by current callbacks. This is measurement work, not proof the app is slow. | I01, I02 |

### Larger workflows, not minor addon omissions

| Item | Existing capability | Remaining work and boundary | Requirements |
| --- | --- | --- | --- |
| R13 — Cross-project anatomical assembly | SCP subtree duplication, construction graph copies, Make Independent and guarded deletion exist. One-off migration scripts produced the current assembly. | Import/merge a selected mixed anatomy/construction graph from another project, preserve internal sharing once, and explicitly map external skeleton/support identities and provenance. Opening a project replaces the document; OBJ import does not provide project assembly. General region copy also needs full mixed-entity coverage. | A08, E06, H01 |
| R14 — Whole-skeleton replacement/update | An imported SCP mesh can be replaced through affected-binding review; tissue construction can be retargeted. | Compare an old and new skeleton as assemblies, map correspondences, preview affected fibers/tissues and expose ambiguous assignments before commit. One-object replacement is useful but does not fulfill the complete skeleton-update proposal. | D06 |
| R15 — Persistent variants and explicit promotion | Undo, committed saves, recovery copies and one session-only shortcut baseline exist. | Keep multiple lightweight candidate configurations/stage checkpoints, sharing unchanged assets, with evidence and explicit promotion. Reopen and compare alternatives without overwriting accepted work. A baseline or Save As is not a persistent variant system. | E07, H01, H03 |
| R16 — Anatomical catalogue and review queue | Named entities, workspaces, strict mirrors, computation status and Issues exist. | Represent anatomical types separately from numbered instances, named regions and review collections; persist separate anatomical/route/attachment/persistence/display approval, evidence revisions and work ownership. Add resumable reconstruction work above the geometry scheduler. External atlas HTML and reconstruction journals are not an integrated app workflow. | A01, A07, G02, G04, G05, H01 |
| R17 — Complete reconstruction-stage comparison | Tissue Base/Rest/Intrinsic/Stack Plan/Final comparison, point explanations and source navigation exist. | Represent original reference anatomy and transferred candidates as first-class reconstruction stages with correspondence and review provenance, then include them in comparisons. This belongs to the separately deferred reconstruction/transfer workflow; do not label the current tissue-stage inspector missing. | A01, A06, F05, F11, H06 |

R13–R17 overlap deliberately: the same persistent identities, external references and
evidence ownership must support assembly, variants and reconstruction review. They
should not become five unrelated storage formats or competing queues.

## Complete requirement matrix

**Covered** means the present feature addresses the operative recommendation, subject
to the linked implementation's documented limits. It does not certify every possible
input or erase unfinished extensions listed elsewhere. **Partial** names the actual
remaining portion. **Missing** means no integrated product workflow was found.
Later scope changes and intentional exclusions are explained after the matrix.

Evidence links point to current owning boundaries and existing qualification records.
An absent feature is assessed against models, operations and UI, not a failed keyword
search alone. No overall completion percentage is assigned to these differently sized
requirements.

### A — Document and geometry ownership

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| A01 | Partial | Typed anatomy/construction registry is implemented. Named anatomical regions, type catalogue and reference/transfer stage records remain R16/R17. [Model evidence](#model-and-assembly). |
| A02 | Covered | Authored construction, accepted geometry, provisional inspection and presentation have separate ownership. [Model](#model-and-assembly), [tissue inspection](#tissue-and-route-inspection). |
| A03 | Covered | Stable entity IDs, accepted/input revisions, freshness and reference-safe publication exist. [Model](#model-and-assembly), [execution](#evaluation-and-performance). |
| A04 | Covered | Owned native geometry/preparations and retained-resource tracking exist; this does not imply zero-copy everywhere. Remaining upload/cache extensions are C05/B09. [Execution](#evaluation-and-performance). |
| A05 | Partial | Canonical metres, display units, local/material/world frames, numerical checks and reflected orientation exist. Unified visible scale/conditioning diagnosis remains limited to individual operation errors; R02. [Inspection/API](#inspection-persistence-and-automation). |
| A06 | Partial | Base/final/material/query/display roles and qualified query reuse exist. Original-reference and transferred reconstruction representations remain R17. Display LOD remains F08. [Model](#model-and-assembly), [inspection](#tissue-and-route-inspection). |
| A07 | Partial | Strict shared-source mirrors, distinct instance references and reflected queries are delivered. Anatomical types versus numbered instances remain R16. Independently evaluated/editable mirrors are superseded. [Mirroring](mirroring_035.md). |
| A08 | Partial | Guarded deletion and within-document graph copying exist. Mixed-region and cross-project assembly with external identity mapping remain R13. [Model/assembly](#model-and-assembly). |

### B — Evaluation, workers and caches

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| B01 | Covered | Explicit output dependencies, valid independent work and cycle failure retention exist. Authored cycles are allowed; evaluation diagnoses affected components rather than refusing creation. [Execution](#evaluation-and-performance). |
| B02 | Covered | Targeted authored/result/presentation invalidation and revision-aware reuse exist. Broad invalidation was optimized in 0.3.3. [Execution](#evaluation-and-performance). |
| B03 | Partial | Completed-result/preparation caching and queued coalescing exist; general cross-consumer in-flight sharing remains R10. [Cache evidence](#evaluation-and-performance). |
| B04 | Covered | Explicit accepted-result reads, declared provenance and missing-prerequisite failures exist. Accepted Manual inputs are intentionally usable with pending provenance. Wider UI status-provider reuse is R01, not missing geometry-read semantics. [Execution](#evaluation-and-performance). |
| B05 | Covered | One coordinator, reservations, task policies, dispatch capture, coalescing, admission and inherited dependency priority exist. Outside-workspace updates remain lower priority. [Execution](#evaluation-and-performance). |
| B06 | Covered | Major numerical preparation/evaluation uses owned background inputs and native work. Long-operation responsiveness still needs workload-specific measurement, not an assumption from threading. [Execution](#evaluation-and-performance). |
| B07 | Covered | Cooperative cancellation, obsolete publication rejection and undo/load/deletion invalidation exist. [Execution](#evaluation-and-performance). |
| B08 | Covered | Registry/dependency indexes, changesets and incremental notifications exist. [0.3.3 delivery](shortcuts_033.md). |
| B09 | Partial | Per-cache budgets, ownership and profiler accounting exist. Aggregate budgeting/cost policy and disk-cache retention remain R09. [Cache evidence](#evaluation-and-performance). |
| B10 | Covered | Local-space surface/query/preparation reuse, scale/reflection handling and confirmed-query qualification exist. [Execution](#evaluation-and-performance). |

### C — Interaction and publication

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| C01 | Covered | Explicit commands, initiating edit causes and separate evaluated publication exist. [API](authoring_api.md), [0.3.3](shortcuts_033.md). |
| C02 | Covered | Begin/update/commit/cancel, coherent undo and async revision protection exist. New workflows such as tightening still need to use them. [API](authoring_api.md). |
| C03 | Covered | Live/On Release/Manual, per-object/default policies and pending-input provenance exist. [Execution](#evaluation-and-performance). |
| C04 | Covered | Complete accepted bundles, material provenance and downstream publication barriers exist, including source/mirror presentation. [Execution](#evaluation-and-performance), [mirrors](mirroring_035.md). |
| C05 | Partial | Complete staged render chunks and ownership are implemented. Generic position-only GPU updates/index reuse remain R11; no measured publication problem is claimed here. [Render evidence](#viewport-and-presentation). |
| C06 | Partial | Accepted fallback, explicit previews and pending/failure distinctions exist. Streaming solver intermediates during ordinary jobs is not generally implemented; R08, only where useful. [Inspection](#tissue-and-route-inspection). |
| C07 | Partial | Activity and shortcut propagation distinguish calculation/display progress. Shared readiness/eligibility providers beyond skin remain R01. [Status evidence](#status-and-findings). |

### D — Attachments and fibers

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| D01 | Covered | Retained material/role bindings, sampling/crop correspondence and explicit topology restrictions exist. General automatic arbitrary-remesh reassignment is intentionally not promised. [Workflows](workflows_036.md), [API](authoring_api.md). |
| D02 | Partial | Inspection, qualified placement, offsets, frames and pin validation exist. Unified placement witnesses/approach/blocker explanations and named anatomical region labels remain R03/R16. [Attachment evidence](#attachments-and-profiles). |
| D03 | Covered | Attachment, interior support and routing obstacle relationships are separate and editable. [0.3.6 workflows](workflows_036.md). |
| D04 | Covered | Curve/Fiber points, handles, pins, closed paths, junctions, supports and source navigation are implemented. Strict mirror editing is intentionally unavailable. [API](authoring_api.md), [workflows](workflows_036.md). |
| D05 | Covered | Authored engines and ROUTED remain distinct, with explicit direct engine switching and failure retention. Preferences provide routing-point and propagation choices. Mandatory Preview/Accept was intentionally removed. [Workflows](workflows_036.md), [API](authoring_api.md). |
| D06 | Partial | Single imported-SCP mesh replacement and tissue retarget review exist. Whole-skeleton correspondence and dependent assembly preview remain R14. [Replacement evidence](#model-and-assembly). |
| D07 | Missing | No integrated measured tightening preview/batch operation; existing ROUTED configuration is not equivalent. R04. [Routing evidence](#tissue-and-route-inspection). |

### E — Tissues and assembly

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| E01 | Covered | Unified TissueVCP composes source, inflation, relaxation, constraints and stacking; classification does not select another evaluator. [Tissues](tissues_022.md). |
| E02 | Partial | Stable material profiles and proportional four-depth scaling exist; configurable additional local stations remain R05. [Profile evidence](#attachments-and-profiles). |
| E03 | Covered | Stacking relationships, support footprints, order, exclusions, sides and intrinsic/final distinction exist. Mirror evaluation follows the later strict-reflection decision. [Visual tools](tasks/vcp-visual-tools.md). |
| E04 | Covered | Stage comparison, point constraint explanations, source/target goals, boundaries/seams and separate smoothing evidence exist. They do not claim an inverse decomposition of solver forces. [Inspection](#tissue-and-route-inspection). |
| E05 | Covered | Region/field selection and painting, visible-only default, Paint Through, goals and coherent undo exist. [Visual tools](tasks/vcp-visual-tools.md). |
| E06 | Partial | Sources/relationships can be copied and evaluated in one document; one-off migrations exist. Product-level assembly of independent candidates and revision-bound review evidence remain R13/R16. [Model](#model-and-assembly). |
| E07 | Missing | Persistent lightweight reconstruction alternatives, stage checkpoints and promotion are absent. Session-only shortcut comparison is narrower; R15. [Comparison evidence](#inspection-persistence-and-automation). |

### F — Views and inspection

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| F01 | Partial | Presentation is independent of authored state and saved per workspace. Multiple simultaneous independent 3D views remain R07. [Viewport](#viewport-and-presentation). |
| F02 | Covered | Category-specific normal/hover/selected styling and source colors exist, independent of numerical work. [Viewport](#viewport-and-presentation). |
| F03 | Covered | Cached/native geometry and component picking, revision awareness and hover coalescing exist. First-query latency remains a measurement concern under I02. [Viewport](#viewport-and-presentation). |
| F04 | Covered | Separate visibility/pickability, category/role selection and deeper picking support surface/material references. [Inspection workflow](workflow_inspection.md). |
| F05 | Partial | Entity/source navigation and tissue point/provider/constraint explanations exist. Rich qualified-placement explanation and original-reference/transfer provenance remain R03/R17. [Inspection](#tissue-and-route-inspection). |
| F06 | Covered | Separate anatomy/construction/helper layers, focus/isolation and saved workspaces exist without changing collision eligibility. [Viewport](#viewport-and-presentation). |
| F07 | Partial | Presets, calibrated camera bookmarks, sections, outlines and point rulers exist. Task-specific neighbor selection, richer width/depth measures and concurrent synchronized views remain R06/R07. [Viewport](#viewport-and-presentation). |
| F08 | Partial | Display settings such as fiber radius are independent of calculation. Adaptive display-only tessellation/background detail during navigation is not a general capability; R11, subject to measurements. [Viewport](#viewport-and-presentation). |
| F09 | Partial | Bounded route records show reference, planner, solver seed/trials/final and contacts/termination; surfaces expose source ordering and crops. A unified loft/support-distance explanation and curated first-feasible comparison are not the complete current workflow; R03/R06. Live trial streaming is separate R08. [Route evidence](#tissue-and-route-inspection). |
| F10 | Partial | Revision-matched image/JSON exports and shortcut paired evidence exist. General issue-specific spatial packages, measured penetration and automatic obstruction-aware views remain R02/R06. [Exports](#inspection-persistence-and-automation). |
| F11 | Partial | Base/Rest/Intrinsic/Stack Plan/Final comparisons exist. Original reference and transferred stages require the missing reconstruction model; R17. [Inspection](#tissue-and-route-inspection). |

### G — Findings and anatomical review

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| G01 | Partial | Shared Issues and tissue spatial witnesses exist; skin reports are largely stage-level counts/metadata. Wider spatial findings and fuller containment/penetration interpretation remain R02. [Findings](#status-and-findings). |
| G02 | Partial | Freshness, pending inputs, unconverged output and unstacked fallback are distinguished. Independent persistent anatomical/review acceptance dimensions remain R16; consistent UI eligibility reuse is R01. [Findings](#status-and-findings). |
| G03 | Partial | Registered retry/rebind/pin repair actions and reviewed replacement exist. Contextual navigation/recovery coverage is not universal; R02/R03. Explicitly accepted self-intersections must not be silently repaired. [Findings](#status-and-findings). |
| G04 | Missing | No in-app anatomical atlas/review catalogue with semantic collections, exposure filters and separate type/instance counts. R16. [Model](#model-and-assembly). |
| G05 | Missing | No integrated resumable reconstruction catalogue/work-ownership queue. The native task coordinator is not that workflow queue. R16. [Model](#model-and-assembly). |

### H — Persistence, automation and export

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| H01 | Partial | Self-contained authored/accepted geometry, bindings, relationships and workspace persistence exist. Candidate journals and reconstruction review evidence cannot yet be stored as those product records; R13/R15/R16. [Persistence](#inspection-persistence-and-automation). |
| H02 | Covered | Supported schema migration and deliberate startup behavior exist. General Blender-project conversion is explicitly deferred; one-off project migration does not make it a product feature. [Roadmap](roadmap.md), [API](authoring_api.md). |
| H03 | Covered | Historical committed saves and separate recovery autosaves, including recovery UI, are delivered. Persisted undo/paused-solver restoration remain deferred. Reconstruction variants are separate R15. [0.3.7](usability_037.md). |
| H04 | Covered | Intentional workspace cameras/visibility persist separately from transient hover. Blender debug-save requirements apply to development exports, not the standalone export menu. [Workspaces](workflow_inspection.md). |
| H05 | Covered | Shared explicit operations serve desktop, headless and authoring clients. A dedicated MCP server is not required by this contract. [API](authoring_api.md). |
| H06 | Partial | Current production engines run headlessly and shortcut changes can be replayed. General experiment/replay capture remains R12; transfer/tightening APIs await their missing product workflows R04/R17. [Automation](#inspection-persistence-and-automation). |
| H07 | Covered | Pinned native/Python/Qt dependencies, capability checks, portable packaging and cloud test scope exist. Optional GPU backends are not an unimplemented approved feature. [Architecture](architecture.md), [cloud scope](cloud_development.md). |
| H08 | Covered | Built topology skin exports as OBJ through an extensible exporter. Additional formats, rigs/debug exports and general Blender bridges remain outside current scope. [Skin workflow](skin_workflow.md). |

### I — Measurement and regression

| ID | Status | Current implementation and remaining scope |
| --- | --- | --- |
| I01 | Partial | Runtime profiling includes operation/task/native/UI/frame timing, dirty reasons, caches and resource ownership. Complete internal attribution and physical presentation are not universal; R18. The intentionally deferred integrated viewer, stack sampling and GPU execution profiling are not reinstated here. [Profiler evidence](#evaluation-and-performance). |
| I02 | Partial | Representative production benchmarks and interaction fixtures exist. Ongoing repeatable whole-workflow cold/warm gesture qualification of the combined app remains R18; this static audit did not perform it. [Profiler evidence](#evaluation-and-performance). |
| I03 | Partial | Extensive frozen native fixtures, parity sweeps and regression tests exist. The requested reusable experiment/test workspace and generic captured-edit replay remain R12. Do not confuse available developer tests with a delivered product workflow. [Automation](#inspection-persistence-and-automation). |

## Owning boundaries and evidence

The tests below are existing behavioral evidence sources, **not tests rerun for this
audit**. Release records state their actual executed checks and limits.

### Model and assembly

- [Typed registry](../src/anthroforge/core/object_registry.py) and
  [Document](../src/anthroforge/core/document.py) contain anatomy, construction,
  shared references, shortcuts, mirroring and skin, but no reconstruction catalogue,
  review axes or persistent variant records.
- [Project lifecycle](../src/anthroforge/application/projects.py),
  [mesh import](../src/anthroforge/application/importing.py),
  [SCP operations](../src/anthroforge/application/operations.py),
  [construction copying](../src/anthroforge/application/construction_copy.py) and
  [source graph copying](../src/anthroforge/application/source_graph_copy.py) establish
  the distinction between opening/importing a mesh and assembling another document.
- [Mesh replacement](../src/anthroforge/application/mesh_replacement.py) and
  [tissue retargeting](../src/anthroforge/application/tissue_retarget.py) have real
  assessments and reviewed commits. See [replacement tests](../tests/test_mesh_replacement.py),
  [retarget tests](../tests/test_tissue_retarget.py) and
  [independence tests](../tests/test_tissue_independence.py).

### Evaluation and performance

- [Coordinator](../src/anthroforge/application/coordinator.py),
  [coalescing](../src/anthroforge/application/task_coalescing.py) and
  [resource admission](../src/anthroforge/application/task_resources.py) already own
  execution. [0.2.4 performance](performance_024.md) and
  [0.3.3 performance](shortcuts_033.md) record delivered reuse/invalidation work.
- [ResourceCache](../src/anthroforge/native/resource_cache.py),
  [engine caches](../src/anthroforge/native/mesh.py) and
  [tissue preparation](../src/anthroforge/native/tissue_preparation.py) show individual
  limits and the get/build/store boundary. [FAST disk weights](../src/anthroforge/native/skin_weight_cache.py)
  are checksummed and disposable, but have no aggregate retention policy.
- [Profiler contract](profiling.md),
  [resource inventory](../src/anthroforge/profiling/resource_inventory.py) and
  [summary attribution limits](../src/anthroforge/profiling/summary.py) distinguish
  measured CPU/native work from unavailable Qt/GPU/physical-latency accounting.
  [Profile diagnostics tests](../tests/test_profile_diagnostics.py) and
  [resource group tests](../tests/test_profile_resource_groups.py) cover current evidence.
- [Confirmed-query qualification](tasks/confirmed-query-reuse.md) records existing
  exterior/query reuse; this audit does not propose another Boolean/snapping algorithm.

### Status and findings

- [SkinStatusProvider](../src/anthroforge/application/skin_status.py),
  [architecture follow-up](architecture.md#shared-operation-status-providers) and
  [0.4.1 inventory](tasks/release-041.md) identify remaining UI status consumers.
- [Skin Issue provider](../src/anthroforge/application/issues/skin.py) publishes stage
  metadata/counts. [Tissue finding navigation](../src/anthroforge/desktop/tissue_finding_view.py)
  instead consumes triangle/frame/bounds witnesses and tissue stages. It is not a
  generic witness renderer for every provider.
- [Issue resolution](../src/anthroforge/application/issues/resolution.py),
  [issue retry tests](../tests/test_issue_retries.py),
  [skin diagnostics tests](../tests/test_skin_final_diagnostics.py) and
  [tissue finding tests](../tests/test_tissue_inspection_geometry.py) establish the
  current repair/diagnostic coverage. No findings is not a collision-free certificate.

### Attachments and profiles

- [Attachment inspection](../src/anthroforge/application/attachment_inspection.py),
  [confirmed placement capture](../src/anthroforge/application/placement_inputs.py) and
  [surface queries](../src/anthroforge/application/surface_queries.py) already preserve
  role/material identity and exterior placement. More explanation should expose this
  service's evidence, not replace attachment behavior.
- [SectionProfile](../src/anthroforge/core/tissue_settings.py) validates four stations;
  [profile scaling tests](../tests/test_tissue_profile_scaling.py) cover proportional
  scaling, not arbitrary additional stations.
- [0.3.6 workflows](workflows_036.md) distinguish already-delivered pin/support,
  routing, replacement, retarget and preset features from the remaining requests.

### Tissue and route inspection

- [Stage selection](../src/anthroforge/application/tissue_inspection_stages.py),
  [tissue inspection delivery](tasks/tissue-inspection.md) and
  [visual tools delivery](tasks/vcp-visual-tools.md) cover stages, constraints,
  footprints, painting and sections. See [inspection tests](../tests/test_tissue_inspection.py),
  [constraint goals](../tests/test_constraint_goal_inspection.py) and
  [painting tests](../tests/test_tissue_painting.py).
- [Route inspection](../src/anthroforge/application/route_inspection.py),
  [bounded native trace adapter](../src/anthroforge/native/routing_trace.py),
  [route UI](../src/anthroforge/desktop/qml/RouteInspection.qml) and
  [route tests](../tests/test_route_inspection.py) show existing snapshots and contact
  evidence. Captured trials are available after the diagnostic job; they are not
  continuous ordinary-job preview publication.
- [API inspection limitations](authoring_api.md) explicitly exclude tissue containment
  and measured penetration depth, distinguish goal inputs from historical solver
  forces, and cap diagnostic records. Skin has its own coverage predicates; that is
  not general tissue penetration measurement.

### Viewport and presentation

- [Main layout](../src/anthroforge/desktop/qml/Main.qml) has one 3D viewport;
  [Viewport](../src/anthroforge/desktop/qml/Viewport.qml) owns the displayed interaction.
  [Presentation presets](../src/anthroforge/core/presentation.py) change categories;
  they do not derive anatomical task neighborhoods.
- [Qt mesh geometry](../native/qt/mesh_geometry.cpp) rebuilds complete chunks on an
  asset change; [path geometry](../native/qt/path_geometry.cpp) likewise adapts native
  output. Existing staged publication must be preserved if buffer updates change.
- [Workspace/inspection walkthrough](workflow_inspection.md) and
  [measurement delivery](tasks/inspection-measurements-profiler.md) document existing
  rulers, coordinate readouts and camera bookmarks. The chosen distance tool measures
  two picked points, not minimum surface clearance.

### Inspection, persistence and automation

- [Shared API](authoring_api.md) exposes production and inspection operations.
  [Frozen report capture](../src/anthroforge/application/inspection_report.py) binds
  images and numbers to one snapshot; [inspection export tests](../tests/test_inspection_export.py)
  cover that workflow.
- [0.3.2 comparison/replay](shortcuts_032.md) is implemented, despite the old summary
  saying deferred. [Journal](../src/anthroforge/application/comparison_journal.py)
  accepts shortcut/driver/evaluation operations and marks other authored changes
  incomplete. [Comparison tests](../tests/test_shortcut_comparison.py) cover the
  current session baseline, not persistent variants or general arbitrary-edit replay.
- [Recovery/autosave](usability_037.md), [skin export](skin_workflow.md) and
  [0.4.1 qualification](tasks/release-041.md) supersede historical “future” notes.
  Frozen tissue/skin fixture suites and production task evidence exist; no unified
  end-user parameter-sweep workspace was found in the operation/UI inventory.

## Intentional exclusions and superseded proposals

Do not reintroduce the following as accidental missing functionality:

- **Independent mirror edits or evaluation:** superseded by strict read-only
  reflection in 0.3.5. No Make Independent for mirrored instances or duplicate drivers.
- **Separate Free/Controlled fiber entities:** superseded by one Fiber subclass using
  curve engines. Direct engine changes preserve the user's chosen control policy;
  mandatory preview/accept gates were removed deliberately.
- **Rejecting authored dependency cycles or blocking all Manual inputs:** later
  contracts permit definitions, retain failed/cyclic accepted results, and explicitly
  track accepted Manual provenance. They do not silently treat it as freshly evaluated.
- **Apply/Bake and unrestricted mesh editing:** deliberately unavailable.
- **Automatically remapping every arbitrary topology change:** not a current promise.
  Existing material correspondence and topology locks remain intentional.
- **Automatically removing tissue intersections:** self-intersections are allowed;
  checks are advisory. Confirmed placement uses qualified exterior queries, and the
  user retained the agreed stacking behavior. New diagnostics do not authorize repairs.
- **Legacy Blender-project conversion and general anatomical reconstruction/fitting:**
  separately deferred product workflows. One-file migrations and external reconstruction
  tools are useful evidence, not built-in import/transfer features. R13–R17 need scope
  selection before entering this release.
- **Broader export formats, rigs or game/Blender bridges:** the current export contract
  is built topology skin, with OBJ implemented and an extension boundary for later formats.
- **Persisted undo and paused solver resume:** deferred. Separate recovery autosaves
  are already implemented and should not be listed as missing.
- **MCP transport:** the shared authoring/headless API exists; a dedicated MCP server
  is an optional adapter, not a prerequisite for fulfilling H05.
- **Profiler viewer, Python/C++ stack sampling and GPU execution profiling:** explicitly
  outside the first runtime profiler. R18 does not silently expand that scope.

## Suggested next scope discussion

R01–R03 and R06 are the closest continuation of the existing workflows: clearer status,
spatial diagnostics, attachment explanation and practical inspection. R04/R05 offer
modeling improvements but need numerical/interaction decisions before implementation.
R09–R11 should be selected only after measurements demonstrate a relevant cost. Larger
assembly/reconstruction work R13–R17 should receive its own agreed specification.

The original audit changed documentation only. Subsequent 0.4.2 work is limited to
the selected extensions; other entries remain unselected. Whole-surface containment proofs,
minimum separating translations and guaranteed local exits through arbitrary folded geometry
remain outside the implemented diagnostics; unavailable conclusions are labeled explicitly.
