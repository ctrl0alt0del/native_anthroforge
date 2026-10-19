# AnthroForge standalone application: consolidated recommendations

Updated: 2026-10-20

The [confirmed 0.2.0 specification](docs/specification_020.md) is authoritative for
curves, fibers, surfaces, reference images and object relationships.
Current schema 4 compatibility is defined by 0.2.2 below. It replaces the earlier Free/Controlled classification with curve
engines, requires independent curve-to-fiber copies, and includes all these features
in 0.2.0. [0.2.1 defines curve-workflow improvements](docs/specification_021.md);
The [0.2.2 specification](docs/specification_022.md) now defines unified TissueVCP,
Anchor/Fiber/Membrane sources and surface-only stacking, with
[implementation and acceptance](docs/implementation_022.md) and [validation evidence](docs/development_status.md#unified-tissues-022). Historical source terminology in the
evidence/coverage appendix is retained only to identify the original addon behavior.

Status: general product specification confirmed by the user on 2026-10-16 after questions Q1–Q58, with the subsequent 0.1.2 primitive/deformer interview confirmed in Q32. Section 1 and its linked confirmed feature specifications are authoritative where source recommendations differ. Priorities and technology proposals are recommendations unless explicitly identified as agreed. This is not an implementation completion report or a claim of measured standalone performance.

## Contents

- [Product scope](#1-product-direction-and-scope), [sources](#2-sources-and-interpretation), [priorities](#3-priorities), and [technology direction](#4-technology-direction-and-architectural-boundaries).
- [Confirmed specification](#11-confirmed-release-and-document-contract), [jobs and saving](#14-confirmed-job-history-and-save-contract), and [explicit deferrals](#18-deferred-decisions-and-provisional-rules).
- [A — Document and identity](#5-a--anatomical-document-identity-and-representations).
- [B — Evaluation and scheduling](#6-b--evaluation-scheduling-workers-and-caches).
- [C — Transactions and publication](#7-c--edit-transactions-publication-and-interaction-state).
- [D — Attachments and fibers](#8-d--attachments-and-fiber-editing).
- [E — Muscles, tissues, and assembly](#9-e--muscle-tissue-and-assembly-workflows).
- [F — Viewport and selection](#10-f--viewport-selection-and-visual-inspection).
- [G — Diagnostics and review](#11-g--diagnostics-recovery-and-anatomical-review).
- [H — Persistence, automation, and delivery](#12-h--persistence-automation-interoperability-and-delivery).
- [I — Measurement and regression](#13-i--measurement-experiments-and-regression-coverage).
- [Existing capabilities](#14-existing-capabilities-to-preserve), [implementation order](#15-recommended-implementation-order), and [validation matrix](#16-validation-matrix-and-measurable-targets).
- [Historical evidence](#17-historical-evidence-and-its-limits), [open decisions](#18-decisions-still-to-make), and [original-item coverage](#appendix--original-recommendation-coverage).

## 1. Product direction and scope

**The primary outcome is an application that remains comfortable to edit while geometry is being computed.** Input preparation, dependency processing, validation, result publication, and rendering must support that outcome as well as the numerical solver itself.

The user has established the following scope:

- AnthroForge uses its own application framework and runs without Blender for normal editing, saving, and reopening.
- The first version has a limited collection of parametric primitives and separate, editable deformers/geometry modifiers. Apply/Bake is permanently unavailable.
- General Blender mesh editing, sculpting, retopology, rigging, and animation capabilities are outside the first-version scope.
- Blender may remain an optional conversion and downstream content-creation tool.
- Reusing Blender source under its applicable license is acceptable. Particular components still require dependency and license review when selected.

The application should own the anatomical document, evaluation scheduling, and viewport presentation. Existing native algorithms and useful orchestration contracts should be retained wherever they meet the requirements. The objective is a complete, reliable editing workflow; changing the host application alone is not evidence of improvement.

### 1.1 Confirmed release and document contract

The primary work is remapping current addon functionality, implemented in stages. Version one targets new projects; mapping existing custom Blender primitives and converting editable addon projects is separate future work. Existing workflows remain the migration inventory, not a promise to implement every source recommendation simultaneously.

- Normal authoring works offline without an account or Blender. Windows is the first target; preserve a practical route to other platforms without rewriting the engine.
- One document is open per application instance. Separate UI or headless instances can own separate documents; use one writer per project file.
- A document is not semantically a whole body. It may represent a head, limb, another partial construction, or other supported content.
- An empty document is valid. Once SCPs exist, they form one tree with exactly one parentless SCP. The root may have geometry or be an empty grouping SCP. This produces one skin target per document.
- All standalone projects use SI: one world unit equals one metre. Millimetres/centimetres/metres are display choices. Convert external geometry into canonical units; obtain an explicit scale when source units are unknown.
- Reference development machine, inspected during the interview: Ryzen 9 7900X3D (12 cores / 24 threads), 32 GiB RAM, RTX 4080 (approximately 16 GiB VRAM), Windows 11 x64. These are the initial reference conditions, not permanent minimum requirements.

### 1.2 Confirmed primitives, assembly, and export

The [confirmed 0.1.2 primitive and deformer specification](docs/primitives_012.md) defines the release behavior and supersedes the earlier 0.1.1 allocation. Primitive families are imported mesh, ordered-curve loft, and curve-deformed body with box/cylinder/capsule bases. One SCP can contain multiple curves or body pieces and attachment locations, but different primitive families cannot be mixed within one SCP through 1.0. Curves are editable open/closed Béziers; body curves expose radius and tilt. Neighboring loft strips share boundary vertices; sampling has common start/span settings and per-curve overrides.

Hooks and lattices are independently addable/removable deformers, with shared controls distinct from their per-target bindings. Reproduce Blender's native Hook behavior for Empty-like targets and native lattice behavior for the supported geometry. Thickness is a separate geometry modifier, with lattice before thickness. Hook connections between different SCPs preserve bound offsets without welding their geometry. Controls explicitly follow an SCP or the document frame. Anatomical shortcut/driver parameters are outside 0.1.x.

Imported source meshes remain unchanged and support TRS, lattice deformation, and vertex selection/weights for hooks; general mesh-vertex editing remains outside scope. Preserving imported UVs, vertex colors, materials, or textures is outside version one. This does not remove native SCP colors or diagnostic presentation. **Apply/Bake is permanently unavailable through UI and APIs:** all primitive and remaining deformer parameters stay editable, and generated meshes are derived results rather than replacements for authored definitions.

Resolution and other attachment-mesh topology changes are locked while an SCP has children or incoming surface attachments, including from shared controls. Shape edits preserving that topology remain available; the lock is removed once both conditions are absent. Automatic attachment remapping across resolution/topology changes is excluded through 1.0. Control-dependency cycles may be authored, but evaluation skips cyclic and dependent work, retains previous successful output, and terminates affected jobs unsuccessfully so saving can finish. The SCP hierarchy remains a tree. Dedicated issue/cycle-reporting UI is deferred to a later 0.x release.

Ordinary selection selects an SCP; Edit Primitive exposes its construction controls. Hooks and lattice cages are independently selectable. Multiple deformers may be ordered on the same target. Removing one target's binding preserves the shared control and its other targets. Each affected SCP retains its own effective update mode under the existing task coordinator, including when a deformer is shared. The 0.1.2 release implemented this baseline; the [0.2.0 contract](docs/specification_020.md) supersedes curve ownership and direct control attachments. Release evidence is recorded separately from these product requirements.

Import creates an independent copy with new entity identities. Remap internal relationships and preserve source document/entity/revision provenance. In a populated document, the user chooses the SCP that parents the imported root; in an empty document, the imported root establishes the tree. Missing non-hierarchy references remain visible and explicitly resolvable; block only operations needing them, and never guess a binding by name. Future transfer of changes from a copy to its source must be explicit, never automatic.

Version-one export contains only the document's skin with topology. There is no export before skin construction. Geometry/topology must be current for the chosen export revision; rebuilding can be offered when necessary. A completed skin belonging to an eligible historical revision may be exported as that revision. Other anatomy, rigs, debug objects, and general game-engine packaging are not version-one exports. Concrete interchange formats remain a feature decision.

### 1.3 Confirmed workspaces and presentation

Named workspaces contain explicitly selected entities, optionally expanded to children, and remember camera and visibility settings. Selection changes alone do not redefine membership. Workspaces may mix entity types. Outside entities remain very transparent and read-only, but continue to exist in the complete dependency graph and participate in calculation at lower priority. Switching workspaces changes editing scope/presentation rather than authored anatomy or anatomical undo history.

Hover, selection, opacity, focus, and diagnostics remain separate from authored data. Live, On Release, and Manual share consistent semantics, a document default, and per-object overrides; choose initial defaults with each feature. Display the freshest safely renderable output, including intermediate solver results when practical. Mark intermediate output provisional, including temporary constraint violations; it is not silently accepted as authoritative downstream support/collision data. Retain completed output as a fallback.

### 1.4 Confirmed job, history, and save contract

The following terms have specific product meanings and must not be replaced by a conventional fixed transaction-group policy:

1. A background write job blocks commitment of the current working state. Read-only jobs do not. Queued, preparing, running, publishing, and cancellation-pending write work remain unfinished. Success, failure, and explicit cancellation are terminal; a document with failed/cancelled calculations is a valid state for commitment.
2. Calculations normally target concrete objects. Do not run overlapping writers on the same object. A job writing several objects reserves all its outputs before execution; details are feature-specific. Independent outputs may be evaluated concurrently. Reading an input does not lock it against editing; revision checks reject obsolete output.
3. Capture owned inputs and the starting document version when the job is ready to run, not when it is enqueued. Repeated automatic requests for the same object/operation coalesce into one pending request that will read fresh inputs. Preserve distinct explicit operations that cannot replace one another.
4. New edits may mark a running job obsolete. Request cooperative cancellation and stop at a safe point; do not force immediate termination. An obsolete result cannot overwrite a newer/restored result. Obsolete write jobs still count as unfinished until terminal.
5. Undoing past a calculation's starting version cancels it. Undo also removes requests belonging to the undone edit that are still queued. Redo resubmits work; it captures new inputs/version when execution starts. Resuming a paused calculation is future work. Undo/redo history is not persisted across application sessions.
6. **Latest committed for saving** means the historical document version immediately before the earliest still-running write calculation started. When that earliest job finishes, the eligible historical checkpoint can move forward even while another job is running. During a queued-only gap with no running writer, retain the previous eligible checkpoint. When all write work is terminal, the current state can commit, including explicit failure/cancellation status.
7. Example: c1 starts on an SCP from A0; an edit creates A1; c2 starts on another object from A1 while c1 is running. When c1 finishes and c2 remains, the eligible historical checkpoint is A1, even though c1 was unfinished when A1 was recorded. Do not substitute a permanently pinned A0 epoch or a per-job last-globally-idle checkpoint.
8. Saving while blocked presents Cancel Save, Save Latest Committed, or Wait and Save. The prompt blocks editing. Wait includes all enqueued write work running to completion, then saves automatically. Cancelling the wait returns to editing without cancelling calculations. Failures are finished work, not an infinite wait condition.
9. Headless callers explicitly provide a blocked-save policy; there is no implicit default to wait. Offer waiting, saving the eligible checkpoint, or a structured pending-work response without a dialog.

Register dependency requests before declaring the parent job terminal so that the scheduler does not report a false idle gap. This does not change input capture to enqueue time. Historical snapshots must retain their own authored state, results, and freshness metadata; saving a historical revision must not combine it with the latest displayed geometry.

### 1.5 Confirmed persistence and startup

Use a self-contained portable project file containing authored state, necessary assets/provenance, intentional workspace state, and completed results belonging to the selected revision. Rebuildable acceleration structures may be disposable caches. Do not persist undo/redo history or paused worker state in version one. Plan state ownership and revision boundaries to accommodate future crash recovery, but implementing autosave/crash recovery is not a version-one completion requirement.

On opening, automatically perform the equivalents of computations that the addon already performs on Blender load. Other computations remain manual on opening; do not automatically rebuild every stale output. Startup behavior must be inventoried from the addon and validated on representative files. Existing load code does meaningful geometry synchronization; this is not a blanket no-calculation-on-open rule. Ordinary subsequent editing follows the saved update modes.

### 1.6 Confirmed shared core and headless operation

Expose the complete supported functionality through an editor-independent document API shared by UI tools, tests, authoring automation, and AI/MCP adapters. Headless clients operate independent project sessions/snapshots and explicit outputs rather than silently sharing or replacing a live UI document. Preserve one writer per project file and explicit result revisions.

Headless computation must not require a window or initialized renderer. Offscreen inspection images may use a GPU; image and numerical inspection must refer to matching document/geometry revisions. Numerical optimization remains C++ under the project rules; UI and automation may orchestrate it but must not implement iterative numerical work in Python.

### 1.7 Confirmed performance priorities

There are no hard numerical responsiveness release thresholds. Improve smoothness across preparation, solving, validation, publication, and rendering. Around 30 FPS navigation, input feedback around 50 ms, and cancellation acknowledgement around 100 ms are useful soft goals when attainable without disproportionate effort. Worker termination is separately measured and occurs at safe points. Record frame/input distributions and worst stalls on declared production fixtures and viewport sizes; averages alone are insufficient.

Follow-up decision (2026-10-16): provide a dedicated scheduling policy for each task type,
managed by one task coordinator. Before admission, quickly assess task complexity and
choose an appropriate delay, including zero for cheap or explicit work. Preserve one
authority for shared execution resources, output reservations, cancellation, publication
and checkpoints. This refines the coordinated-scheduler requirement; it does not create
independent worker pools per feature or relax the job/history/save contracts above.

### 1.8 Deferred decisions and provisional rules

- Primitive/deformer behavior and reference examples are now confirmed in [the 0.1.2 specification](docs/primitives_012.md). Native implementation details, correspondence beyond the confirmed topology lock, export format, and feature-specific scheduling mechanics remain implementation or later-feature work.
- Dependency prerequisites may inherit workspace priority. If a job genuinely requires a failed result, dependent work should finish with an explicit dependency failure while unrelated work continues. Both rules are provisionally accepted and must be revisited against actual feature dependencies rather than assuming a universal calculation chain.
- Newer copies do not automatically update their sources. Explicit copy-to-source transfer, paused-calculation resumption, persisted undo history, and actual crash recovery are outside version one.
- Q48 deliberately deferred the technology selection/prototype decision until a full analysis of this specification and the addon implementation. The earlier Qt/Python/Quick 3D proposal is not a confirmed stack. Analysis recommendations must remain distinguishable from user-approved product requirements.

The user confirmed this specification in Q58 and explicitly authorized updating this document and performing the full stack analysis. The interview is complete; feature details deliberately deferred above are not missing approval gates.

### Confirmed 0.1.3 usability update

The 0.1.3 release improves existing editing: distinct move/rotate/scale gizmos, transient
surface transparency during curve editing, geometry silhouette outlines, and deletion
through a central keyboard manager and tree icon. Deleting an SCP preserves its children
and moves them to its parent. The user explicitly chose an empty grouping replacement
when deleting a root with children. A leaf root can leave an empty document. These deletion
semantics supersede the 0.1.2 subtree-removal implementation. See the updated
[walkthrough](docs/quickstart.md) and [shared API](docs/authoring_api.md).

## 2. Sources and interpretation

The original five-file submission contained a duplicate in place of S3. The subsequently supplied missing S3 is now included, and the previously duplicated material is retained once as S4. Together with the existing 21-item requirements document and the user's inline summary, S1–S6 contain **132 original numbered recommendations**, organized below into **66 consolidated recommendations**. The appendix maps every original item to the consolidated IDs.

| Source | Material | Numbered items |
| --- | --- | ---: |
| S1 | [Native ownership, geometry engine, inspection, and delivery](<C:/Users/alexe/.codex/attachments/5545b833-455a-47f3-8136-73be215203cb/Pasted text.txt>) | 22 |
| S2 | [Evaluation control, caching, background work, and mirrors](<C:/Users/alexe/.codex/attachments/0f7b7149-381f-4932-97e5-69d4b18d9e5d/Pasted text.txt>) | 21 |
| S3 | [Semantic anatomy, shared AI inspection, reconstruction stages, variants, and queues](<C:/Users/alexe/.codex/attachments/7d683970-64f9-42ae-8380-271f8362a01e/Pasted text.txt>) | 18 |
| S4 | [Anatomical data, transactions, fibers, tissues, and migration](<C:/Users/alexe/.codex/attachments/82d66398-69e9-4ac6-904a-5a9535e6afd5/Pasted text.txt>) | 26 |
| S5 | [Anatomical reconstruction, relationships, review, and assembly](<C:/Users/alexe/.codex/attachments/ddfcc65d-7e8a-418f-b1ab-332b86a44e9c/Pasted text.txt>) | 24 |
| S6 | [Editing responsiveness and viewport requirements R01–R21](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/standalone_application_requirements.md>) | 21 |
| User summary | The 21-item table and first priorities supplied with this request | Covered by S6 |
| Confirmed interview | Q1–Q58; final confirmation on 2026-10-16 | Authoritative section 1; supersedes conflicting source proposals |

Source correction: the [initial attachment labeled S3](<C:/Users/alexe/.codex/attachments/58a60a93-f69c-40d8-8761-63d0cca6f2bf/Pasted text.txt>) is byte-identical to S4. Its former S3.01–S3.26 coverage entries are now S4.01–S4.26. S3.01–S3.18 refer exclusively to the newly supplied source. Existing consolidated requirement IDs remain unchanged; E07, F10, F11, and G05 are additions.

These sources contain several different kinds of statements. Preserve the distinction during implementation:

- **User decision:** the scope and preferences explicitly stated in this conversation.
- **Existing capability:** functionality reported in the supplied material or visible in inspected project code; its migration still requires parity tests.
- **Historical evidence:** measurements and defects scoped to the original fixture, revision, and experiment.
- **Proposed improvement:** an architectural or interaction change that must demonstrate its benefit.
- **Host boundary:** a documented Blender integration constraint, distinct from an AnthroForge defect or a product-design choice.

Blender's Python integration has documented threading limitations, and many operators depend on editor context. These do not imply that Blender's internal evaluators or renderer are single-threaded, or that all Blender data operations require operators. [Threading guidance](https://docs.blender.org/api/5.0/info_gotchas_threading.html), [operator limitations](https://docs.blender.org/api/5.0/info_gotchas_operators.html).

## 3. Priorities

Priorities below are a synthesis of the source recommendations, not a separately approved feature backlog.

| Priority | Meaning |
| --- | --- |
| P0 — foundation | Required to establish a trustworthy document and a responsive complete editing workflow. Implement and validate before broad feature migration. |
| P1 — focused editor | Required when the corresponding primitive or existing workflow enters the first release. Includes selection, inspection, and practical recovery. |
| P2 — extension | Preserve as a documented requirement, but introduce after foundations or when task evidence justifies it. Not an automatic expansion into a general modeling application. |

P2 does not authorize removing an existing behavior needed for a migrated workflow. For example, existing tissue constraints must remain correct even if an expanded visual constraint editor is deferred.

The first priorities are data/presentation separation, explicit transactions, coordinated dependency scheduling, responsive preparation and native execution, and bounded publication of complete results. S3 additionally prioritizes a universal UI/AI command API, synchronized visual/numerical inspection, reconstruction-stage comparisons, and transactional persistence. Establish the inspection contract alongside the engine; introduce its stage-comparison interface as each reconstruction workflow migrates. Save/reopen validation and responsiveness measurement apply from the first implementation milestone.

## 4. Technology direction and architectural boundaries

The completed [technology stack analysis](<E:/development/anthroforge/standalone_technology_stack_analysis.md>) recommends **Qt 6 / PySide6 / QML + the existing C++17 numerical engine + a host-independent Python application core**, using Qt Quick 3D as the first viewport behind a replaceable presentation boundary. The analysis covers the confirmed specification, inspected addon implementation, dependency availability, a bounded native DLL load probe, alternatives, and discriminating validation experiments. This is an engineering recommendation, not a user-confirmed stack selection or measured standalone performance.

| Layer | Proposed technology and ownership |
| --- | --- |
| Desktop interface | Qt Quick and QML for panels, controls, trees, menus, and layouts. |
| Viewport | Qt Quick 3D initially, with C++ geometry providers and a dedicated precise picking policy. Keep render data separate from anatomical truth. |
| Geometry and numerical engine | Existing C++ native libraries, extended with owned geometry, versioned results, and required primitive/modifier evaluation. Retain established numerical dependencies and build/load infrastructure. |
| Application services | Python and PySide6 for commands, authoring workflows, validation, serialization, publication orchestration, and automation. Keep expensive preparation and repeated numerical work out of Python/UI loops. |
| Native build/runtime | Preserve existing clang-cl/MSVC-compatible native builds and integrate CMake targets incrementally. CPython 3.12 and Qt/PySide6 6.12.0 are the initial runtime candidates; validate a locked complete bundle before adoption. |
| Project storage | A versioned package containing structured definitions and binary geometry/assets. JSON plus binary assets is the proposed baseline; the precise container and schema remain to be specified. |
| Interoperability | Version-one output is only a built skin with topology, tied to an explicit revision. Optional Blender conversion and broader game-pipeline adapters remain separate future work. |

Qt Quick 3D supports custom geometry from C++, but its documented built-in picking for custom geometry uses bounding volumes. Accurate fiber, handle, and surface selection needs explicit native implementation and testing. Partial geometry updates may still update an entire GPU resource. Qt 6.11 added order-independent transparency, which strengthens the candidate but still needs dense-anatomy validation. These APIs do not establish performance on this application. [Custom geometry](https://doc.qt.io/qt-6/qquick3dgeometry.html), [picking behavior](https://doc.qt.io/qt-6/qml-qtquick3d-model.html#picking), [transparency methods](https://doc.qt.io/qt-6/qml-qtquick3d-sceneenvironment.html#oitMethod-prop).

Numerical optimization remains native C++: iterative fitting, objectives, Jacobians, constraints, line searches, and repeated numerical geometry queries. Batch inputs and results across the boundary. Do not introduce per-sample/per-iteration Python callbacks or a silent Python optimizer fallback.

The intended flow is: explicit command → document transaction → affected dependency revisions → owned worker inputs → native evaluation and validation → revision-qualified result bundle → bounded publication → presented frame. Rendering consumes results; it does not define attachment identity or authored anatomy.

## 5. A — Anatomical document, identity, and representations

Curve editing also supports a held insertion modifier (Shift by default): preview the closest
curve location under the cursor, confirm with left click, continue inserting while held,
and hide the preview on release. A separate held snapping modifier (Ctrl by default) lets
a dragged point use any visible SCP surface except its own, switching targets during the
same gesture. Releasing it restores ordinary dragging. Both modifiers use the keyboard
manager. Curves, points and handles have distinct colors per type.

The follow-up view workflow maps 1/2/3 to global X/Y/Z orthographic views, centering the
active selection with apparent zoom preserved. View changes must preserve an ongoing edit
and its original undo/cancel boundary. G/R/S starts mouse-driven Move/Rotate/Scale, confirmed
with left-click/Enter and canceled with right-click/Escape. Bindings remain centralized.
Entering an axis view by keyboard or its UI action preserves the original camera settings.
4 and the Restore action return to that position, rotation, zoom and projection without
ending an edit. Consecutive axis switches retain the first saved camera; restoring consumes
it, and the next axis switch captures a new one. This temporary return point is scoped to
the current document/workspace and clears when another workspace camera is loaded.
During point snapping, the wheel adjusts signed surface-normal offset; middle-click or
release of the snapping modifier resets the offset. Reset must not end the current edit.

### A01 — Own a typed, parametric anatomical document [P0]

Represent SCPs/bones, anatomical regions, shared points, fibers, pins, fiber surfaces, muscles, heads, branches, tissues, attachments, and relationships as application entities. Store primitive definitions and their supported modifier parameters as authored data. Track each output's reconstruction stage, source reference, and dependencies explicitly. Viewport objects, names, collections, and generated meshes must not determine whether an anatomical entity exists.

### A02 — Separate authored intent, evaluated results, and presentation [P0]

Keep an authored fiber path distinct from resolved attachments, planner output, solver output, and its drawn curve. Keep muscle bases, own inflation, stacked results, and displayed surfaces distinguishable. Publication carries its origin and cannot be interpreted as a new artist edit. Hover, selection styling, and diagnostic overlays belong to presentation state.

### A03 — Maintain stable entity identity and explicit result revisions [P0]

Names are editable labels. Persistent IDs identify entities and surface roles; revision IDs identify evaluated versions. Replacing geometry preserves selection, references, metadata, intentional display preferences, and history. Readiness and correspondence between authored entities and evaluated results must be inspectable.

### A04 — Retain owned native geometry and solver state [P0]

Keep mesh arrays, canonical bases, intrinsic and final surfaces, fiber points, bindings, geometry provenance, collision structures, and reusable solver data in persistent native storage where appropriate. Use immutable snapshots or explicit ownership for workers, with defined buffer lifetimes. Reduce unnecessary native/Python/render conversions. Zero-copy and improved speed are possibilities to measure, not assumptions; lower publication costs do not imply faster PIQP or correspondence calculations.

### A05 — Make units, frames, and tolerances explicit [P0]

Use one world unit = one metre across standalone projects. Define world/bone-local/material coordinates, reflection orientation, clearance, attachment offsets, and numerical tolerances. Display-unit changes do not rescale geometry. Convert external data explicitly. Use native double precision and suitable local frames where required. Diagnose scale and conditioning problems. Display thickness is independent of collision radius.

### A06 — Give each geometry representation an explicit purpose [P0]

Distinguish original reference anatomy, editable construction, evaluated surfaces, attachment domains, qualified collision proxies, display tessellation, and export geometry. Maintain identity and correspondence among them. A coarse solid rib-cage proxy cannot be assumed to preserve intercostal gaps; simplified colliders must retain relevant narrow passages. Viewport modifier toggles cannot silently change attachment truth.

### A07 — Model anatomical types, instances, and symmetry separately [P0]

Separate a muscle type from numbered spaces, bilateral instances, and source/mirror relationships. Share definitions and geometry when inputs are equivalent; allow explicit local overrides or detachment. Spatial instances retain distinct picking, collision, and validation identities. Independently evaluated asymmetric stacking must survive mirror refresh. Test reflected normals and winding, and avoid accidental finger/toe instance duplication.

### A08 — Preserve references through duplication, deletion, and import [P0]

Remap complete dependency chains and shared junctions when copying a region. Identify consumers before deleting a referenced entity. Preserve missing references as explicit, inspectable problems. Import and assembly must resolve IDs deliberately rather than guessing by names or proximity.

**Category acceptance:** replace geometry and rename entities without losing references; alter display resolution without changing attachment meaning; duplicate a connected region; exercise deletion, missing imports, and asymmetric mirrors; verify units and frames against the same source fixtures.

## 6. B — Evaluation, scheduling, workers, and caches

### B01 — Use one authoritative anatomical dependency graph [P0]

Represent SCP parameters and geometry, parent/child attachments, fibers, surfaces, muscle bases, inflation, stacking, tissues, mirrors, and diagnostics as explicit dependencies. Run independent branches concurrently where valid. Preserve real parent publication barriers and reject cycles. Example anatomical chains are descriptive, not a universal fixed order; actual relationships determine scheduling.

### B02 — Distinguish change kinds and invalidate only affected work [P0]

Track topology, vertex positions, transforms, attachment definitions, appearance, visibility/selection, and organization separately. Appearance and presentation changes do not invalidate numerical geometry. A rigid transform can preserve local geometry and its index. Relative changes between Boolean operands still invalidate the evaluated solid when required.

### B03 — Share computation by exact input revision [P0]

Deduplicate both completed results and work already in progress. Evaluate an expensive operation once for a particular complete input revision, rather than promising once per gesture when that gesture creates several input versions. Share compatible station preparation, row sampling, and base surfaces across fiber-surface and muscle stages. Include settings and algorithm/backend versions in equivalence where relevant; visual similarity is insufficient.

### B04 — Make geometry reads explicit and free of hidden evaluation [P0]

Request a specified geometry version and receive a handle or a structured pending/invalid status. Reading attachment inputs must not secretly refresh unrelated scene state or invoke broad callbacks. Missing prerequisites become visible scheduled work. Consumers never treat pending or stale geometry as current.

### B05 — Coordinate priorities, concurrency, and queue budgets [P0]

Use one scheduling policy for required dependencies, interactive previews, final evaluation, and advisory checks. Apply the write-reservation, dispatch-time snapshot, coalescing, and save-blocking rules in section 1.4. Reserve resources for input and rendering, prioritize focused work, and batch invalidation/bookkeeping before dispatch. Bound concurrency, retained input snapshots, and unpublished output. Dependency-priority inheritance remains feature-specific and provisional. Debouncing after expensive preparation is too late.

### B06 — Make the whole computation path eligible for background execution [P0]

Move suitable preparation, Boolean evaluation, attachment queries, fitting, surface generation, inflation, stacking, and validation to native workers on owned inputs. Avoid long UI-held locks and UI-thread waits. Use process isolation where a risky job needs failure containment; that is a deployment decision to validate. Native job execution must not depend on Blender APIs or viewport state.

### B07 — Cancel cooperatively and reject obsolete results [P0]

Jobs carry document, entity, dependency, and transaction revisions. New edits, undo, deletion, cancellation, and document loading can supersede them. Acknowledge cancellation promptly and stop at safe native checkpoints. Distinguish a cancel request from worker termination. Stale work must never overwrite a newer or restored result, even if cancellation could not interrupt it immediately.

### B08 — Maintain indexes and deliver precise changes [P0]

Maintain indexes by stable ID, type, owner, and dependency, updating them through explicit lifecycle operations. Send targeted change sets to consumers. Avoid reconstructing membership and rescanning all objects after generic updates. Authored identity and evaluated-version identity must never be confused during membership checks.

### B09 — Budget caches centrally with visible ownership [P0]

Account for bytes, rebuild costs, active-job references, revisions, and eviction reasons. Preserve byte-budget policies rather than arbitrary entry counts that thrash preparation caches. Shared intermediate/native handles need deterministic lifetime rules. Bounded caches and completed-result queues must prevent memory growth under sustained editing.

### B10 — Reuse local-space query geometry safely [P1]

Reuse qualified surfaces and spatial acceleration structures across consumers and rigid transforms when their true inputs remain unchanged. Transform queries into local space where appropriate, respecting scale and reflection semantics. Refresh or rebuild indexes when required. Qualify Boolean/query replacements against existing failures before using them to skip computation.

**Category acceptance:** repeated equivalent requests share a job; unrelated anatomy remains untouched; parent-before-child ordering is correct; rapid edits stay bounded; cancellation, undo, deletion, and loading reject obsolete output; caches stabilize under long sessions; all work reaches a verifiable idle state.

## 7. C — Edit transactions, publication, and interaction state

### C01 — Record explicit edit intent [P0]

Commands distinguish authored pin movement, proportion edits, propagated attachment movement, explicit recomputation, generated publication, and presentation changes. Preserve cause and initiating transaction throughout propagation. Derived changes must not trigger feedback loops or unintended rerouting.

### C02 — Give each gesture an atomic editing transaction [P0]

Use begin, update, commit, and cancel events for drags and numeric edits. A complete anatomical action, including references and dependent changes, has one coherent undo entry. Batch actions such as tightening a collection or assigning shared points remain reversible. Failure and rollback restore a consistent state, and async jobs cannot republish after undo.

Apply section 1.4's cancellation/resubmission rules when history is navigated. A user-edit transaction, evaluated-result revision, and eligible historical save checkpoint are distinct concepts. Do not persist undo history or paused calculation state in version one.

### C03 — Apply consistent Live, On Release, and Manual modes [P0]

Use the same update policy vocabulary across bones, fibers, muscles, tissues, and generated surfaces, with a document default and per-object overrides. Select initial defaults per feature. Show pending changes and separate preview from final evaluation. A debounce timer is not a gesture-commit event. Manual mode and on-release evaluation still honor dependency readiness and explicit recomputation semantics.

### C04 — Publish related anatomical results atomically [P0]

Publish compatible geometry, bindings, diagnostic status, and generation metadata as a complete bundle at a defined boundary. A downstream consumer must never combine a new muscle surface with old bindings or unfinished stacking. If advisory checks remain pending, the bundle says so explicitly rather than implying that validation passed.

### C05 — Bound publication and resource-disposal work [P0]

Prepare result buffers asynchronously, stage GPU uploads under measured budgets, and switch only to complete compatible results. Reuse topology/index buffers, perform position-only updates when valid, batch changed entities, and share mirror render resources where appropriate. Resource release must also have bounded effects. Handle replacement does not make allocation, copies, synchronization, or GPU upload free.

### C06 — Keep useful, clearly identified output while waiting [P0]

Show the freshest safely renderable output, including intermediate calculation previews where practical, while retaining completed geometry as a fallback. Mark pending, stale, provisional, and accepted results distinctly. A provisional preview may temporarily violate constraints, but cannot silently become authoritative collision/support data or accepted downstream input. Preserve its origin revision. Renderable buffer consistency is required even for a geometrically provisional preview.

### C07 — Expose useful progress and a precise definition of finished [P1]

Provide one activity panel for preparation, queueing, solving, validation, publication, and failures. Show affected entities, elapsed time, queued edits, and cancellation status; let entries select the relevant entity. Distinguish geometry ready, presentation ready, diagnostics pending, and fully idle. Counts and iteration budgets are not reliable estimates of remaining time.

**Category acceptance:** sustained dragging, typing, mode changes, cancel, undo/redo, and newer edits all preserve coherence; controls acknowledge input before expensive work; no large final publication freeze occurs; the application reports remaining work accurately and becomes idle without orphan callbacks or jobs.

## 8. D — Attachments and fiber editing

### D01 — Keep attachment coordinates stable and topology changes explicit [P0]

Bindings record target identity, surface role, coordinate space, geometry/topology revision, and binding definition. Use a stable attachment domain or qualified material coordinates independent of display sampling for both bone and muscle-surface attachments. Carry selected regions and seams through the same explicit correspondence rules. Remeshing, cropping, or sampling changes must update correspondence or identify what became invalid. Never reinterpret old triangle indices against incompatible geometry or silently substitute nearby triangles.

### D02 — Make attachment inspection and qualified placement visible [P1]

Show parent bone/muscle, anatomical region, footprint, offset, approach direction, and binding status in the viewport. Preview surface snapping, collision-qualified fallback, displacement from the requested point, owner surface, unrelated blockers, and local-exit availability. Explain rejected placements and highlight unbound or questionable contacts before commit.

### D03 — Separate attachment, support, and collision roles [P1]

Present attachment of a point, influence of a supporting surface on the interior path, and obstacle participation as different relationships. A surface may have several roles, but each must be explicit. Preserve existing support policy rather than collapsing these concepts into a single object picker.

### D04 — Provide a dedicated fiber editor [P1]

Directly inspect and edit endpoints, intermediate touches, loops, shared junctions, and interior influences. Selecting a shared point reveals all incident fibers before an edit affects them. Display deformed paths and fixed anchors together, with anatomical ownership and source/mirror relationships intact.

### D05 — Preserve authored-shape and routed-engine semantics [P0]

Bézier/polyline engines preserve authored paths and expose collision problems. The routed engine may reroute while retaining structural anchors. Fiber is a Curve subclass with anatomical bindings, not a separate Free/Controlled type. Separate moving with anatomy, editing the trajectory, and explicitly running the solver. Compare previous and proposed routes before acceptance where appropriate. Failure must not silently change engines. See the [0.2.0 contract](docs/specification_020.md).

### D06 — Provide a deliberate skeleton-update workflow [P1]

Compare old and new skeletons, distinguish deformation from topology changes, preserve valid bindings, preview dependent muscle changes, and identify reassignment needs. Keep ambiguous remapping visible. Qualify replacement surfaces against affected attachments and collision requirements before committing them.

### D07 — Integrate measurable tightening previews [P1]

Carry forward bounded tightening and show displacement, shortening, clearance, and fixed attachments. Support before/after comparison, atlas collections, and one undoable batch. A step count is a computational budget, not a percentage of geometric tightening or a guaranteed anatomical improvement.

**Category acceptance:** reproduce narrow-gap and crowded-fiber cases; preserve shared points and anchors; vary display sampling independently; detect genuine topology changes; compare Free and Controlled behavior; test skeleton replacement, rejected snaps, explicit rebind, and tightening rollback.

## 9. E — Muscle, tissue, and assembly workflows

### E01 — Investigate a composable volume framework [P2]

The [0.2.2 contract](docs/specification_022.md) uses one TissueVCP with composed construction, inflation, relaxation, constraints and stacking capabilities. Anatomical labels do not choose algorithms. Source-relative and explicit target-relative goals preserve shared construction; surface-only stacking remains distinct from attachment. [Release validation](docs/development_status.md#unified-tissues-022) records observed evidence and limitations.

### E02 — Make local profile coordinates stable and extensible [P1]

Locate thickness controls in explicit anatomical or material coordinates that survive changes in sampling. Permit additional local controls where actual geometry requires them. The reported four-depth intercostal limitation is a modeling issue to address directly; moving the UI alone will not resolve it.

### E03 — Expose muscle-layer relationships and stacking [P1]

Show supporting/covering muscles, overlap footprints, automatic versus explicit ordering, and blocked dependencies. Separate own inflation from displacement received through stacking. Preserve persistent relationships and the existing vector stacking machinery, including independently evaluated sides.

### E04 — Explain constraints alongside smoothing [P1]

Display attachments, protected creases, shared seams, construction boundaries, and unconstrained regions. Preview height smoothing separately from displacement smoothing. Show which constraints limit a change; smoothing cannot repair an invalid base or erase a deliberately constrained crease without changing the model.

### E05 — Add visual tissue-constraint editing [P2]

Provide selection or domain-specific painting for fixed backing, soft suspension, feathering, strengths, and offsets. Show constraint goals and resulting displacement on the relevant surface. This is a specialized tissue tool; its inclusion does not imply general sculpting or unrestricted mesh editing in the first release.

### E06 — Assemble independently authored muscles safely [P1]

Build candidates against identified clean skeleton assets, then integrate through explicit entity IDs, revisions, and dependencies. Trigger relevant packing, stacking, attachment, and collision checks. Upstream repairs invalidate affected downstream results and review evidence. Another muscle's final scene is not an implicit construction template for the next candidate.

### E07 — Support lightweight reconstruction variants and explicit promotion [P2]

Fork transfer, base, or inflation configurations while sharing unchanged skeleton and reference assets through safe ownership. Keep stage checkpoints, settings, evidence, and downstream revisions associated with each variant. Compare variants in the same workspace and promote one explicitly without overwriting accepted work. Editing an upstream stage visibly invalidates its dependent outputs. This consolidates candidate scenes, journals, and screenshots into a controlled project workflow.

**Category acceptance:** compare original and proposed local profiles, asymmetric stacking, constrained smoothing, and tissue deformation; integrate separately built candidates without accidental dependencies; verify that changed supports invalidate affected geometry and review status; fork and reopen variants, promote one, and confirm that accepted alternatives and shared references remain intact.

## 10. F — Viewport, selection, and visual inspection

### F01 — Keep presentation independent per viewport [P0]

Hover, opacity, focus, isolation, diagnostic coloring, and helper overlays affect rendering without modifying authored anatomy or launching geometry work. Permit different presentations of the same model in separate views. Transient hover does not enter document undo or canonical saved appearance.

### F02 — Define default, hovered, and selected styling [P1]

Provide all three states across SCPs, fibers, and muscles, with selected taking precedence. Use category-appropriate opacity, preserve native SCP RGB colors, keep thin fibers readable, and maintain legible active controls. Update render state only when needed; an identical style assignment should not cause geometry work.

### F03 — Implement a dedicated hover/picking service [P1]

Coalesce movement, reuse spatial information, query relevant candidates, and handle curves and meshes explicitly. Refresh after camera or geometry changes and bound the first query after invalidation. Compare native spatial indexing with renderer-assisted approaches on real scenes; GPU readback and index maintenance have costs. Avoid scanning every mesh on every mouse move.

### F04 — Make selection through anatomy predictable [P1]

Separate visibility, pickability, and opacity. Supply category/surface-role filters, deliberate cycling through targets under the pointer, and screen-space tolerances for fibers and handles. Hover must predict the entity a click will select. Surface picks retain entity identity, geometry revision, and material coordinates where available so measurements, constraints, and region editing can reuse them. Changing hover opacity must not alter eligibility and cause flicker. Transparent context can remain visible while unpickable.

### F05 — Select anatomy and explain the selected surface [P1]

Expose selections such as muscle → inflated surface → left instance, with the reconstruction stage, source reference, and dependencies. Treat surfaces, controls, attachments, and mirrors as meaningful parts of an anatomical entity rather than unrelated helpers. Selecting a strange surface feature should reveal the fibers, loft intervals, crop, inflation controls, or mirrored instance that generated it. Provide an Explain this point operation showing its attachment, inflation/displacement directions, contributing providers, and constraints that prevented movement, including fixed bands, protected creases, seams, crop boundaries, and stacking footprints.

### F06 — Separate visibility layers and restore them predictably [P1]

Control anatomy, fibers, handles, attachment markers, and diagnostics independently. Retain the existing policy of limiting active-fiber handles to the active fiber. Temporary focus/isolation must respect manual hiding and restore prior settings reliably. Visibility does not change solver validity or obstacle participation unless an explicit model command changes those roles.

### F07 — Provide task views and anatomical comparisons [P1]

Support bone shaping, fiber editing, muscle-volume inspection, and surface review with relevant surrounding anatomy. Save calibrated front/side/top and obstruction-focused views; synchronize source/target or before/after cameras. Include sections, silhouettes, width/depth measures, selective transparency, and optional local cutaways. Evaluate hidden supporting volumes as well as visible exposed windows; more transparency may increase clutter and overdraw.

### F08 — Separate display detail from computation accuracy [P1]

Allow cheaper curve tessellation, helpers, and background display during navigation, restoring detail afterward. Keep collision, attachment, and final validation geometry at the required accuracy. Introduce display simplification where measurements justify it; renderer bottlenecks have not been established universally.

### F09 — Inspect curve, loft, planner, and solver stages [P1]

Show authored pins, DIRECT seed, planner route, exact-count solver seed, first feasible state, and current/final output separately. Show loft participation, ordering, crop boundaries, and distances from supporting surfaces. For a problematic segment, identify the collider, active contact, limiting step, and termination reason. A cropped visible surface must not conceal an invalid underlying fiber path.

### F10 — Return synchronized visual and numerical inspection packages [P0]

Make one inspection request return a matching image and numerical snapshot for a declared geometry revision: calibrated camera, coordinate frames, entity/stage IDs, relevant neighbors, attachments, and requested distances. A reported intersection includes the offending faces, measured penetration with method/limitations, and a camera that exposes it. Reuse existing inspection packages and make this a standard API for AI, scripts, and the interface. Concurrent updates must not mix an image from one state with numbers from another; return the identified snapshot or an explicit unavailable/stale status.

### F11 — Compare the complete reconstruction stages [P1]

Keep original reference anatomy, transferred anatomy, authored base, fibers, own inflation, and final stacked output separately inspectable. Provide synchronized cameras, overlays, cross-sections, and displacement comparisons between identified stage revisions. Use these comparisons to locate the first stage where an anatomical shape became wrong, rather than inspecting only the final output. Distinguish genuine stage differences from correspondence or sampling differences and expose missing or invalidated stages.

**Category acceptance:** select a thin fiber behind a transparent muscle with matching hover; reuse a surface pick for a measurement; inspect point-level constraint/provider contributions; switch views and restore manual visibility; compare source and mirror; locate the first defective reconstruction stage; verify that image/measurement snapshots stay consistent during concurrent edits; navigate during computation; test transparency cost separately from picking cost.

## 11. G — Diagnostics, recovery, and anatomical review

### G01 — Unify spatial geometry findings [P1]

Combine base intersections, bone penetration, inflated collisions, self-intersections, folds, degeneracy, unresolved anchors, attachment integrity, stacking support, mirror conflicts, and dependency cycles in a selectable workspace. Findings carry affected entities, exact location, reconstruction stage, geometry revision, and measurement limitations. Distinguish intended contact from unwanted crossing. Clicking a finding frames the responsible geometry and upstream entity and can return the synchronized inspection evidence in F10.

### G02 — Separate freshness, solver quality, and review acceptance [P0]

Represent current-but-unconverged, waiting-for-parent, collision-detected, previous-output-visible, pending-checks, and invalid states explicitly. An own-only fallback is visibly different from successfully stacked output. Keep anatomical approval, route/collision validation, attachment integrity, stacking support, persistence, and debug-visibility acceptance separate. An empty issue list while checks are pending does not mean valid, and solver completion does not mean anatomical approval.

### G03 — Offer contextual recovery with explicit effects [P1]

Provide inspect-parent, restore-assignment, change-support, retry, and explicit-rebind actions with previews and structured results. Explain what rebind changes. Preserve failed references and witnesses for inspection; never replace a triangle or support silently just to remove an error indicator.

### G04 — Integrate the anatomical atlas and review catalogue [P2]

Support spatial selection, named collections such as needs-tightening, exposure/status filters, and separate unique-type versus instance counts. Link findings and independent review dimensions to the actual geometry revision. Preserve source anatomy and review evidence when transferring or assembling candidates.

### G05 — Provide a resumable reconstruction catalogue and queue [P2]

Track muscle types separately from numbered instances and mirror copies, with approval state, approach version, evidence, remaining work, and explicit work ownership. For the sequential reconstruction workflow, finish and checkpoint one muscle before starting the next eligible unique type. Resume interrupted work from identified checkpoints, prevent duplicate ownership, and show failed or blocked work without losing accepted results. Keep this workflow queue above the geometry scheduler: its sequential ownership policy does not prohibit safe internal native parallelism.

**Category acceptance:** pending checks never appear as passed; current unconverged and own-only fallback results retain their distinct status; each reported defect is locatable; recovery previews explain changes; rebuilding geometry invalidates affected review findings without losing provenance; interrupt/restart a reconstruction queue and verify correct checkpoints, unique ownership, and no duplicate type processing.

## 12. H — Persistence, automation, interoperability, and delivery

### H01 — Save a coherent versioned project package [P0]

Store authored definitions, relationships, bindings, solver settings, source assets/provenance, journals, review findings, and schema/algorithm versions together. Include identified last-good results and intentional workspace state; keep rebuildable caches distinguishable. On load, identify missing, mismatched, or outdated components. Portable asset references must not depend on a renderer's internal object identity.

### H02 — Make migration and recomputation deliberate [P0]

Apply the confirmed startup policy: run equivalents of existing addon load computations, not every possible rebuild. Distinguish restoration from deliberate recomputation with a different engine/settings. Preserve explicit existing load-time binding/restoration behavior where required; do not introduce new silent rebinds or convert tissue semantics. Describe migrations and preserve the prior file. Existing editable Blender-project conversion is future work; version one targets new projects.

### H03 — Preserve save checkpoints and design for future recovery [P0; recovery deferred]

Implement the exact historical checkpoint and modal save choices in section 1.4. Keep geometry and revision metadata tied to the selected version. A solver failure must not destroy the editing session. Design ownership/serialization so later crash recovery is possible, but actual crash recovery, autosave recovery journals, persisted undo history, and paused-solver recovery are not version-one requirements. Source recommendations for those features remain recorded as future work.

### H04 — Save intentional presentation and preserve development debug views [P0]

Save named workspace membership, cameras, and intentional visibility preferences; separate them from transient hover and temporary focus effects. Preserve intentional inspection views, accepted geometry, and display settings after reopening. For Blender development deliverables, retain all current source/mirrored fibers in normal curve display and native SCP colors in Solid/Object mode. Use the existing StaticScene.save_debug_copy path for those authoring exports and verify the reopened file; temporary hiding or recoloring must not leak into delivery. This development requirement does not add Blender/debug export to the standalone version-one product.

### H05 — Expose one explicit document command API [P0]

UI controls, scripts, tests, and authoring/AI clients use the same operations with explicit document/entity IDs and parameters. Support preview, validation, and undo through the same transaction contract for manual edits, imports, and AI commands. Return structured results, changed entities, job handles, and diagnostics. Operations are independent of active editor, mode, and selection. Retain existing use-case and authoring contracts where useful, including matching visual/numerical inspection requests.

### H06 — Run the same engine headlessly [P0]

Evaluate primitives, transfer, fitting, tightening, stacking, validation, and deterministic replay against project snapshots without a Blender scene or application window. Use the same document operations and numerical engine as the interactive application. Development tooling can capture compact failure-reproduction packages containing inputs, settings, algorithm versions, calibrated view definitions, captured evidence where available, and expected checks; this does not expand the skin-only product export. Replaying the numerical failure must not depend on recreating the original UI history. Headless correctness tests complement, rather than replace, real interaction tests.

### H07 — Control dependencies, capabilities, and optional backends [P1]

Pin compiler/runtime/library versions, preserve backend capability checks, and make builds reproducible. Package native dependencies deliberately instead of inheriting a host Blender/Python combination. GPU acceleration remains optional and must be measured on relevant workloads; backend availability or successful execution does not establish correctness or speed.

### H08 — Export the built skin and defer broader bridges [P1]

Version one exports only the built skin with topology, current for the identified export revision. No skin means no export. Keep the editable anatomical project as the source asset. Do not include SCPs, fibers, muscles, rigs, or debug content. Choose formats during export feature design, preserving required topology rather than assuming all interchange formats do so. Optional Blender conversion, editable legacy-project mapping, and engine-specific packaging remain future work. Development-only fixture/diagnostic capture is distinct from product export.

**Category acceptance:** exercise all blocked-save choices, queued-only periods, failures, undo/redo cancellation, self-contained reopen, startup computation parity, missing assets, explicit headless save policy, and skin-only export from the intended revision. Recovery/legacy conversion checks apply only when those later features are implemented. Retain debug visibility checks for any Blender development deliverables.

## 13. I — Measurement, experiments, and regression coverage

### I01 — Explain each rebuild in an end-to-end trace [P0]

Record initiating input, dirty reasons, requested revisions, dependency work, queue waiting, capture/preparation, detection, correspondence, matrix assembly, PIQP or other solver work, planning, attachment resolution, inflation, stacking, validation, publication, rendering, downstream work, and the presented frame. Include consumers, worker utilization, cache hits/evictions, memory, cancellation delays, and disposal costs. Separate nested timings and warm updates from full solves; do not add overlapping phase durations.

### I02 — Measure and improve actual responsiveness [P0]

Measure input-to-feedback latency, frame-time distributions and worst stalls, picking, first-query costs, useful-preview time, final completion, cancellation acknowledgement, worker-stop latency, stale-result rejection, and memory use. Run reproducible gestures on declared production fixtures and hardware in cold and warm states. Setter timings and timer heartbeats alone do not establish comfortable editing.

### I03 — Keep frozen-input experiments and geometric regression sweeps [P0]

Compare transfer, fitting, smoothing, routing, and scheduling alternatives against identical inputs. Sweep inflation ranges, parent transforms, topology changes, asymmetric mirrors, and save/reopen states. Record geometry differences, attachments, route validity, diagnostics, calibrated views, and performance. Preserve difficult production failures; successful APIs or easier proxy cases do not establish a fix.

**Category acceptance:** a trace explains why work ran and when its result became visible; repeated fixtures are identifiable; geometry and interaction checks accompany timing comparisons; apparent speedups cannot hide incorrect output, dropped updates, stale publication, or degraded final accuracy.

## 14. Existing capabilities to preserve

The source material identifies the following assets. This is a preservation checklist, not a claim that every subsystem was freshly audited for this document.

| Existing capability | Preserve and extend | Relevant recommendations |
| --- | --- | --- |
| Native numerical libraries and C ABI/ctypes boundaries | Existing geometry, collision, optimization, inflation, and stacking behavior; batch native access | A04, B06, H07 |
| Native async fiber coordinator and workers | Owned inputs, useful priorities, safe background execution | B05–B07 |
| Dependency waves, dirty aspects, and publication barriers | Real ordering, readiness checks, targeted propagation | B01–B04, C04 |
| Request debounce, intent tracking, and deduplication | Preserve correct cases; generalize policy and batch earlier | B03, B05, C01–C03 |
| Stable source/mirror mapping and shared geometry | Identity reuse and efficient publication; preserve independently evaluated asymmetric results | A03, A07, C05 |
| Callback indexes and shared preparation caches | Targeted consumers, exact-input equivalence, byte budgets | B03, B08–B10 |
| Free/Controlled behavior and qualified attachment snapping | Existing distinctions, anchors, fallback qualification, and explicit rebind | D01–D05 |
| Native tightening, intersection queries, height smoothing, vector stacking, and persistent relationships | Integrate their contracts into normal editing and inspection | D07, E03–E04, G01 |
| Warning repository and background checks | Spatial witnesses, freshness, actionable recovery | G01–G03 |
| Retained output, previews, generations, and stale-result guards | Preserve correctness and qualify coverage consistently | B07, C04–C06 |
| Skin/topology/warm-update job revision checks | The October 15 documentation supersedes an earlier missing-guard finding; retain checks and test all invalidating actions | B07 |
| Use-case and authoring APIs | Explicit commands and structured diagnostics shared with automation | H05–H06 |
| Existing inspection packages | Matched calibrated views and numerical/spatial evidence; extend revision consistency and stage coverage | F10–F11 |
| Telemetry, performance probes, evidence journals, and fixture workflows | Coherent operation-to-frame traces and reusable regression evidence | H01, I01–I03 |
| Save/reopen checks and manual debug presentation | Visible source/mirror fibers and native SCP colors in delivered Blender artifacts | H04 |

Useful existing references: [runtime contract](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/runtime_contract.md>), [interaction analysis](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/interaction_ux.md>), [tightening contract](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/fiber_tightening.md>), [stacking pipeline](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/muscle_stacking.md>).

## 15. Recommended implementation order

| Stage | Deliverable | Evidence required to move on |
| --- | --- | --- |
| 0. Define a representative slice | Select a real primitive, its required built-in modifiers, a production document, and exact edit sequence. Freeze expected geometry and capture current full-path timings. | Declared input revision, reference machine, viewport size, output checks, and interaction script. A sample triangle is insufficient. |
| 1. Establish document and engine contracts | Stable entities, parameter definitions, revisions, dependency graph, command API, synchronized inspection contract, native ownership, headless execution, and initial persistence. | Correct output through the same commands, matched image/numerical revisions, deterministic references, save/reopen parity, and no hidden Blender runtime requirement. |
| 2. Complete one responsive editing loop | Drag and numeric edit → background preparation/evaluation → validation → bounded publication, with modes, cancellation, undo, and retained output. | Measured input/frame latency throughout all phases; stale-result rejection; coherent result bundles; bounded memory; verifiable idle. |
| 3. Make the workflow understandable | Semantic selection, precise hover, deeper selection, presentation layers, three-state styling, activity panel, spatial diagnostics, point explanations, stage comparisons, and recovery. | Users can select and edit intended anatomy while computation runs; hover predicts selection; pending and failed work is clear; inspection locates the responsible stage and constraint. |
| 4. Migrate the focused anatomy workflows | Selected primitive families and modifiers, bindings, Free/Controlled fibers, muscle/tissue behavior, mirrors, layering, and skin/topology export. | Existing hard fixtures preserve geometry, attachment semantics, diagnostics, persistence, and independent review dimensions. |
| 5. Add justified extensions | Atlas/review catalogue and resumable reconstruction queue, lightweight variants, richer profiles, specialized tissue painting, broader comparison tools, optional backend acceleration, or a shared volume framework. | Demonstrated improvement on the failed or incomplete task; correct checkpoint/promotion/ownership behavior; no reliance on unrelated benchmark wins. |

Instrument and test persistence at every stage. Stages describe dependency order, not time estimates or permission gates. The 0.1.2 primitive catalogue and modifier behavior are now defined in [the confirmed feature specification](docs/primitives_012.md).

## 16. Validation matrix and measurable targets

The user explicitly rejected hard numerical responsiveness thresholds. The figures below are soft improvement goals when achievable without disproportionate effort, not release gates or achieved results. Record the machine, build, fixture, and viewport size. Correctness and save/export semantics remain requirements.

| Dimension | Initial target or required check |
| --- | --- |
| Input acknowledgement/feedback | Soft goal around 50 ms; measure distributions during representative edits including preparation/publication. |
| Cancellation acknowledgement | Soft goal around 100 ms; separately report safe worker stop time and resource release. |
| Navigation | Soft goal around 30 FPS when practical; report p50/p95/p99 frame times and worst stalls, not just average FPS. |
| Final geometry | Compare accepted geometry, attachments, route/collision outcomes, and known limitations against the frozen expected result. Do not trade correctness for responsiveness silently. |
| Publication consistency | No incompatible mixtures of geometry, bindings, revisions, or stacked/parent states. Obsolete results cannot reappear after undo or newer edits. |
| Resource behavior | Bound worker concurrency, queues, snapshots, cache bytes, and unpublished output; reach stable memory use and a verifiable idle state. |
| Selection | Record mistaken targets and task completion; verify hover/click agreement, thin curves, occlusion, deeper selection, and post-edit picking. |
| Persistence | Save during work with the confirmed checkpoint rules, reopen portably, omit undo history, preserve intentional presentation, and apply existing startup behavior. Actual crash recovery is deferred. |
| Inspection consistency | Image, camera, geometry revision, entity IDs, face witnesses, and numerical measurements describe one snapshot even during concurrent edits. |
| Stage and workflow control | Locate the first incorrect reconstruction stage; preserve accepted variants; checkpoint and resume a unique-type queue without duplicate ownership. |
| Export isolation | Export only the single built skin with topology, current for the chosen revision. No skin means no product export. |

| Fixture or task from the sources | What it must discriminate |
| --- | --- |
| Skull shortcut / skull muscle editing | Setter and preparation latency versus native computation; sustained drag, typing, orbit, cancel, undo/redo, newer edits, and save/reopen. |
| Pelvis/SCP mirror shortcut | Boolean work per unique input, mirror identity reuse, unchanged anatomy, correct attachments, and true idle. |
| Crowded hand and narrow-passage fibers | Route coverage, qualified attachment placement, collider fidelity, clearance, thin-curve picking, and source/mirror behavior. |
| Abdominal Layer | Protected seams/creases, binding identity, constrained smoothing, and persistence. |
| Pectoral Pouch and iteration-limit cases | Current-but-unconverged status, constraint behavior, diagnostic location, and recovery. |
| Inflation-cutoff scene and parameter sweep | Stable attachment domain across sampling changes, validation behavior, and preservation of tissue semantics. |
| Asymmetric mirror and stacking cases | Independent evaluation per instance; no later refresh replacing solved geometry with a reflected source copy. |
| Gluteus/sacrum attachment case | Actual attachment footprint, medial extent, source context, and anatomical validity rather than plausibility in one image. |
| Intercostal/rib support cases | Representation of gaps, appropriate collision support, stable thickness coordinates, and sufficient local profile control. |
| Latissimus hook / gastrocnemius tangle / arched fibers | Surface-to-construction explanation, loft order/crop visibility, and separation of planner, solver, and inflation causes. |
| Partially exposed muscles and multi-muscle assembly | Hidden belly coverage, original surrounding anatomy, packing/stacking after integration, and separate anatomical/collision/persistence/visibility acceptance. |
| Deltoid, gluteal, and latissimus stage comparisons | Trace deviations across reference, transfer, base, fibers, own inflation, and stacked output; verify matched cameras, correspondence, and point-level influence explanations. |
| Concurrent inspection and interrupted reconstruction sequence | Match image and numerical snapshots under edits; fork/promote a variant; interrupt and resume checkpoints; verify unique-type ownership and protection of accepted work. |

Some fixtures are named only in the supplied recommendations. Resolve their exact paths, hashes, and accepted revisions before using them as release evidence. Their inclusion here does not claim they were opened or rerun during this consolidation.

## 17. Historical evidence and its limits

These records were inspected as documentation/evidence while preparing this consolidation. The experiments were not rerun, and the numbers must not be generalized to another scene or treated as predicted standalone performance.

| Record | Recorded observation | Implication for the recommendation |
| --- | --- | --- |
| [2026-09-04 native muscle pipeline](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/muscle_native_numeric_pipeline_2026-09-04.md>) | In the recorded production comparison, approximately 0.91 ms native muscle computation and 68.01 ms mesh publication. | Measure publication and full input-to-display latency rather than optimizing solver time alone. |
| [2026-10-07 SCP mirror experiment](<E:/development/WIP_models/muscle_reconstruction_workflow/performance/2026-10-07-scp-mirror-production-v1/summary.json>) | Recorded mirror rebuild/publication-related time fell from approximately 65.27 ms to 1.84 ms; the after-run median remained approximately 324.95 ms. Per-shortcut Boolean counts in the comparison fell from 15 to 5. | Preserve mirror reuse, but account for evaluation/callback work and deduplicate exact inputs across the full operation. |
| [2026-10-12 interaction audit, updated October 15](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/interaction_ux.md>) | One initial setter measured 310.91 ms with zero fiber solves/iterations. Two experimental setters changed from 302.00/293.79 ms to 193.90/168.37 ms with all 139 captured geometry hashes matching. | Bookkeeping/preparation can dominate even without solver work. These experimental results are not a universal Blender limit or a guarantee of comfortable editing. |
| [2026-09-03 attachment barrier experiment](<C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge/docs/attachment_propagation_experiments_2026-09-03.md>) | Capturing all dependency depths once produced maximum fiber and SCP round-trip errors of 0.885 and 1.805 world units in that experiment. | Do not remove real publication barriers in pursuit of parallelism. Selective fusion requires proof that evaluated local geometry and dependency semantics are preserved. |

The October 15 interaction documentation explicitly supersedes the October 12 assertion that skin/topology publication lacked a revision guard. Existing job_revision attachment/currentness checks must be preserved and their invalidation coverage tested. Do not reintroduce the outdated missing-guard claim as the reason for migration.

Other important cautions from the source threads:

- Disabling Booleans during propagation changed attachment results; a replacement query representation needs qualification.
- The inflation cutoff was an addon validation defect, not proof of an unavoidable Blender limitation.
- Selection ambiguity was an interaction-design problem; transparency alone does not fix target selection.
- Wrong gluteal extent, fiber arching, coarse rib support, limited profiles, poor pin placement, defective sources, local minima, and insufficient route coverage require anatomical or algorithmic work.
- Blender already supports shared mesh data, selective evaluation, and object alpha. The proposed improvement is consistent ownership and integration, not invention of those capabilities.
- Standalone execution still requires event loops, synchronization, safe publication boundaries, numerical safeguards, and appropriate parallel granularity.

## 18. Decisions still to make

The general specification is confirmed. The following decisions were deliberately deferred, not left silently assumed.

1. Implementation sequencing and native integration for the [confirmed 0.1.2 primitives/deformers](docs/primitives_012.md); their product scope and reference examples are settled.
2. Adopt and validate the recommended stack from the completed [technology analysis](<E:/development/anthroforge/standalone_technology_stack_analysis.md>). The representative viewport experiment, combined runtime packaging, and numerical parity checks remain implementation work; they were not performed by the analysis.
3. Attachment implementation under the confirmed topology lock. Automatic preservation across resolution/topology changes is excluded through 1.0; it is not an unresolved 0.1.2 feature.
4. Native ownership, scheduling mechanics, cancellation checkpoints, and memory/publication budgets implementing the confirmed behavior.
5. Physical project container and schema migration implementation. Self-contained assets, checkpoint behavior, canonical units, and no persisted undo history are already settled.
6. A skin/topology interchange format. Export scope is settled; broader Blender conversion and game packaging are deferred.
7. Whether shared volume algorithms or GPU acceleration address an observed need sufficiently to justify their complexity.
8. Feature-specific dependency priority/failure handling, provisionally accepted without assuming every feature has chained calculations.

## Appendix — Original recommendation coverage

S3 is the corrected 18-item source supplied after the initial consolidation. The earlier duplicated 26-item material is retained under S4, including all its original coverage. S6 item numbers correspond to R01–R21 and also cover the user's inline 21-item summary. Mapping preserves the individual requirements while allowing related ideas to be consolidated.

### S1 — Native ownership and geometry workflow

| Original item | Consolidated recommendations |
| --- | --- |
| S1.01 | A01, A04 |
| S1.02 | B06, B07, C06 |
| S1.03 | B01, B02 |
| S1.04 | C01, H05 |
| S1.05 | C05, F01 |
| S1.06 | B07, C02, C04 |
| S1.07 | A01, F05 |
| S1.08 | A03, D01 |
| S1.09 | A06, F08 |
| S1.10 | D02 |
| S1.11 | C01, D05 |
| S1.12 | A07 |
| S1.13 | A05 |
| S1.14 | F06, F07, H04 |
| S1.15 | F09 |
| S1.16 | I01, I02 |
| S1.17 | G01, G02, G03, H05 |
| S1.18 | H05 |
| S1.19 | H06 |
| S1.20 | H01, H02, H03 |
| S1.21 | H07 |
| S1.22 | H08 |

### S2 — Evaluation and lifecycle

| Original item | Consolidated recommendations |
| --- | --- |
| S2.01 | B01 |
| S2.02 | B02 |
| S2.03 | B03 |
| S2.04 | C01, C02 |
| S2.05 | B04 |
| S2.06 | B06, C04 |
| S2.07 | B05, B07, C06, I02 |
| S2.08 | A06, D01 |
| S2.09 | B10 |
| S2.10 | A07, C05 |
| S2.11 | A03 |
| S2.12 | D01 |
| S2.13 | B08 |
| S2.14 | A03, B08 |
| S2.15 | A04, B03 |
| S2.16 | B09 |
| S2.17 | C05 |
| S2.18 | I01 |
| S2.19 | C07 |
| S2.20 | H05, H06, I03 |
| S2.21 | B07, C02, H01, H02, H04 |

### S3 — Semantic anatomy, inspection, and reconstruction control

| Original item | Consolidated recommendations |
| --- | --- |
| S3.01 | A01, A03, A05, F05 |
| S3.02 | C02, H05 |
| S3.03 | F10, G01 |
| S3.04 | F11 |
| S3.05 | D02, E03, E04, F05 |
| S3.06 | F01, F06, F07, H04 |
| S3.07 | D01, F04, F05 |
| S3.08 | B01, B02 |
| S3.09 | B05, B06, B07, C03, C04, C05, C07 |
| S3.10 | A04, B10 |
| S3.11 | C02, C04, H01, H03, H05 |
| S3.12 | A06, D01 |
| S3.13 | E07, H03 |
| S3.14 | A07, G04, G05 |
| S3.15 | G01, G02, F10, F11 |
| S3.16 | H05, H06, I03 |
| S3.17 | I01, I02 |
| S3.18 | B06, H07, H08 |

### S4 — Fibers, tissues, and transaction semantics

| Original item | Consolidated recommendations |
| --- | --- |
| S4.01 | A01, A03 |
| S4.02 | A02, C01 |
| S4.03 | B01, I01 |
| S4.04 | C04 |
| S4.05 | C02 |
| S4.06 | A06, D01 |
| S4.07 | A04, B09 |
| S4.08 | B06, B07 |
| S4.09 | F05 |
| S4.10 | D04 |
| S4.11 | D03 |
| S4.12 | D05 |
| S4.13 | A07, E03 |
| S4.14 | E05 |
| S4.15 | G01 |
| S4.16 | C06, G02 |
| S4.17 | F06, F07, F09, H04 |
| S4.18 | G03, D01 |
| S4.19 | E01 |
| S4.20 | A08 |
| S4.21 | H01, H02 |
| S4.22 | H05 |
| S4.23 | I03 |
| S4.24 | I01 |
| S4.25 | A05 |
| S4.26 | H08 |

### S5 — Reconstruction and anatomical review

| Original item | Consolidated recommendations |
| --- | --- |
| S5.01 | A01, A02 |
| S5.02 | H05 |
| S5.03 | H06 |
| S5.04 | B06, B07, H03 |
| S5.05 | C02, C04, C06 |
| S5.06 | H01, H03 |
| S5.07 | B01, I01 |
| S5.08 | D02 |
| S5.09 | D06 |
| S5.10 | A06 |
| S5.11 | F05 |
| S5.12 | F09 |
| S5.13 | E02 |
| S5.14 | D07 |
| S5.15 | E03 |
| S5.16 | E04 |
| S5.17 | G01 |
| S5.18 | F07 |
| S5.19 | F01, H04 |
| S5.20 | A07 |
| S5.21 | G02, G04 |
| S5.22 | A08, E06 |
| S5.23 | I01, I03 |
| S5.24 | A05, H01, H08 |

### S6 — Editing responsiveness and viewport requirements

| Original item | Consolidated recommendations |
| --- | --- |
| S6.01 | A01, A03, A04 |
| S6.02 | B06, C05, I02 |
| S6.03 | B03, B05 |
| S6.04 | C02 |
| S6.05 | C03 |
| S6.06 | B07 |
| S6.07 | C04, C05 |
| S6.08 | C06 |
| S6.09 | C07 |
| S6.10 | A02, F01 |
| S6.11 | F02 |
| S6.12 | F03 |
| S6.13 | F04 |
| S6.14 | A01, A07, F05 |
| S6.15 | F06 |
| S6.16 | F07 |
| S6.17 | F07 |
| S6.18 | F08 |
| S6.19 | H01, H04 |
| S6.20 | H05, H06 |
| S6.21 | I01, I02, I03 |
