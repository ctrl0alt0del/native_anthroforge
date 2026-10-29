# Desktop and authoring audit for 0.4.3

**Audit only — fixes proposed, not implemented.** Reviewed 2026-10-29 against
`3daa3dee` (0.4.2). This document does not qualify or release 0.4.3.

## Conclusion and scope

The public authoring interface does **not yet provide every capability available to
the desktop**. The main anatomical editing and calculation workflows already use
shared operations. The remaining differences are principally queries, access to
uncommitted preview geometry, JSON argument encoding, and application-level services.
This audit found no reason to introduce a second geometry implementation or an MCP
server to address them.

Here, public authoring means `Session.command`, JSON batch `run`, persistent JSON
`serve`, and the documented CLI inspection/render commands. An embedded Python script
can import additional application helpers and inspect session resources, but that is
not equivalent to a documented, serializable operation available to both transports.
The report identifies those existing helpers rather than claiming their functionality
does not exist.

Equivalent authoring does not require simulating a mouse. Explicit component identities,
world/local coordinates, parameters, and `begin`/`commit`/`cancel` can reproduce a UI
gesture's semantic result. Conversely, a registered command or passing smoke test does
not prove every UI query, parameter combination, or lifecycle path is covered.

## Evidence and coverage

[Dispatch inventory](../tools/audit_authoring_043.py) enumerates **364 registered
operation names**. It finds **308 literal desktop dispatch sites using 244 distinct
operations**, with **zero unregistered literal names**. These are counts of code sites,
not a coverage percentage. Dynamic dispatch, helper calls, QML tool adapters and private
resource access were reviewed separately.

The review follows the existing separation of presentation and application logic,
consistent with [Qt's guidance](https://doc.qt.io/qt-6/qtquick-bestpractices.html).
Existing [Qt Quick Test](https://doc.qt.io/qt-6/qtquicktest-index.html) and repository
offscreen checks supply interaction evidence; no alternative UI framework was added.

| UI workflow | Shared authoring coverage | Audit qualification |
| --- | --- | --- |
| Mesh import, SCP hierarchy, duplication, deletion, origins and attachments | `import`, `scp.*`, `attachments.enable`, `object.delete.inspect` | Shared edits, restrictions and undo. Recovery/open semantics are separately listed in A5. |
| Loft/body/segment-chain primitives and shared curves | `primitive.*`, `body.update`, `chain.*`, `consumer.*` | Construction, source independence, sampling and topology restrictions share policies. |
| Hooks, lattices, thickness, Shrinkwrap and modifiers | `control.*`, `deformer.*`, `hook.*`, `lattice.*`, `thickness.update`, `shrinkwrap.*`, `modifier.*` | Shared numerical work and authoring operations. Resolved component discovery is incomplete (A1). |
| Curve creation, drawing, branches, engine conversion and Parametric definitions | `curve.*`, `drawing.project`, `junction.*`, `cursor.place.surface`, workspace cursor | Stroke samples replace mouse events; direct engine changes are shared. A1/A2 affect current controls and preview inspection. |
| Points, Anchors, Fibers, pin/support editing and snapping | `construction.point.*`, `anchor.*`, `fiber.*`, `surface.snap.*`, `geometry.placement` | Creation/rebinding, endpoint policy and exterior placement share application/native services. Fiber editing state is A1. |
| Surfaces, Membranes, branch grouping and correspondence | `surface.*`, `membrane.create` | Includes automatic grouping, explicit ambiguous groups, persistent correspondence and preview lifecycle. A2 limits public preview shape access. |
| Reference images | `image.*`, `object.reparent` | Import/replacement, calibration, parenting and presentation operations are shared. |
| Tissue creation, inflation, profiles, sides, relaxation, cropping and constraints | `tissue.*`, `tissue.field.*`, `tissue.constraint.*` | Shared capabilities, one-action conversion, stage semantics and retained failure output. A2 concerns preview access, not a missing inflation operation. |
| Stacking, material painting and geometry findings | `tissue.stacking.*`, `tissue.inspect.*`, `tissue.field.paint.commit`, `geometry.*` | Brush samples/view/occluders are explicit inputs; no separate Python painting algorithm is required. |
| Shortcuts, drivers, attachment policies and comparisons | `property.*`, `shortcut.*`, `driver.*`, `inspection.export`, `inspection.replay` | Shared type/write restrictions, transactions, effect/progress evidence, comparison and replay. Some contextual queries remain internal (A3). |
| Mirroring and symmetric construction | `mirror.*`, `surface.create/update` mirrored-row options, workspace display | Shared rule resolution, read-only enforcement, attachment sharing and symmetric paths. No duplicate evaluation required. |
| Skin, collagen, topology guides, bone fitting and OBJ export | `skin.*`, `skin.inspect.*`, `skin.collagen.*`, `skin.fit.*`, `skin.export` | Build/update/fit/playback operations exist. Effective contributor settings and refit availability are A3. |
| Measurements, sections, neighborhood, bookmarks and saved view settings | `measurement.*`, `geometry.*`, `bookmark.*`, `workspace.*`, `view.*`, `inspection.export` | Explicit camera/presentation state replaces viewport gestures; temporary focus restoration is desktop state. |
| Project assembly and whole-skeleton replacement | `assembly.*`, `skeleton_update.*` | Shared preparation, mapping/rebind decisions, stale checks, commit and undo. Compatible-choice enumeration and candidate visual access are A3/A2. |
| Persistent variants, catalogue, review queue and reconstruction comparison | `variant.*`, `catalogue.*`, `review.*`, `reconstruction.*` | Shared independent contexts, decisions, evidence and export. `reconstruction.compare.options` already exposes stage choices. |
| Issues, tasks, update modes, preferences and profiling | `issues.*`, `job.*`, `evaluate`, `update_mode`, `preferences.*`, `profile.*`, `inspect` | Includes repair, cancellation/retry, Manual behavior and profiler export retry. Headless profiling truthfully lacks desktop Qt/frame collectors. |
| Project recovery/history and user bug reports | Existing runtime services outside the operation catalogue | A5/A6. Passing their desktop tests does not establish public JSON coverage. |

## Confirmed gaps and proposed responsibilities

### A1 — Query the current editable component state

**Observed behavior:** after a bound Fiber's parent moves by +1 metre in Z, the
desktop's three editable points have Z values `1.7, 1.8, 1.7`. Public
`object.inspect(target).state.points` still has authored Z values `0.7, 0.8, 0.7`.
Both reads leave the document unchanged. The Fiber result is ready.

The desktop obtains current points through
[`curve_context.owner`](../src/anthroforge/desktop/curve_context.py) and
[`curve_edit_state.current`](../src/anthroforge/application/curve_edit_state.py).
[`authoring_state`](../src/anthroforge/desktop/authoring_state.py) also resolves automatic
handles and component positions for display. Public `inspect.target` supplies frame,
resource metadata and topology locks, not this resolved editing snapshot.

This is **not** evidence that Fiber edits use the wrong algorithm, or that authored
inspection should be changed to mean evaluated state. An automation client computing
a delta from the authored points can choose the wrong starting coordinates; the UI has
the correct read model.

**Proposed:** an application-owned current-component query returning stable identities,
local positions/handles, world frame, accepted revision/provenance and edit restrictions.
Use the same query in the desktop. Preserve raw authored inspection, Manual provenance,
and the rule that querying never authors or resamples geometry. Qualify ordinary/Fiber/
Parametric/junction curves and deformer component categories separately.

### A2 — Inspect uncommitted candidates visually

**Observed behavior:** a 12-point curve-conversion preview completes through public
operations. Its status returns token, state, engine, settings and point count. The
desktop obtains the actual candidate path directly from `session.conversion.asset`.
The ordinary saved document still contains the original curve, correctly.

The same architectural distinction exists in
[`tissue_preview.status`](../src/anthroforge/application/tissue_preview.py),
[`surface_scene`](../src/anthroforge/desktop/surface_scene.py) and
[`skeleton_scene`](../src/anthroforge/desktop/skeleton_scene.py): the operation can
prepare/accept a result while the UI accesses transient resource owners to display it.
[`capture`](../src/anthroforge/desktop/capture.py) renders saved revisions; ordinary
[`inspection.export`](../src/anthroforge/application/inspection_report.py) freezes
document state, not these candidate slots. There is no equivalent public candidate
snapshot/image operation for these previews.

Accepted tissue-stage, shortcut-comparison and reconstruction-comparison exports already
exist; this finding does not apply indiscriminately to every comparison tool.

**Proposed:** extend the existing inspection/capture boundary with explicit candidate
tokens and owned snapshots. Expose bounded geometry evidence and optional images through
the existing renderer, without applying then undoing the candidate, leaking native
handles, or pretending a preview is accepted geometry. Headless numerical work must
remain Qt-free; image rendering remains a separate desktop-capable adapter.

### A3 — Discover compatible choices and effective settings

Several UI queries call shared policies directly, but no corresponding public operation
returns their full result:

- [`assembly_choices.targets/properties`](../src/anthroforge/application/assembly_choices.py)
  filters external-reference candidates and type/dimension/component-compatible properties
  for both assembly and skeleton replacement. Public status exposes references/evidence,
  but clients must reconstruct these choices or import the helper.
- [`surface_choices`](../src/anthroforge/desktop/surface_choices.py) combines available
  anatomical roles, mirror identity and readiness into target choices. Raw inspection
  and mirror operations expose ingredients, not the same combined eligibility query.
- [`skin_contributor`](../src/anthroforge/desktop/skin_contributor.py) exposes stored and
  effective settings plus editing restrictions; `skin.inspect` returns stored state.
  Probe: an SCP named `Nasal cartilage` with no contributor override has UI effective
  collagen `0.0` and inherited gap strength `0.4`, while stored contributor rows are
  empty and default authored values would be `1.0`/`1.0`.
- [`skin_fit_results.refit_eligibility`](../src/anthroforge/application/skin_fit_results.py)
  supplies the UI's existing-result refit availability. Public fit inspection and
  eligibility expose supporting information but not this combined query.

The writes validate through shared policies. This is a **read/discovery gap**, not a
claim that invalid target writes bypass those policies or that the underlying values
cannot be computed in Python.

**Proposed:** small domain-specific public queries over the existing owners. Reuse the
operation-status-provider pattern where readiness is involved. Return reasons and
revision provenance; avoid replicating policy in clients or building a universal manager.

### A4 — JSON cannot represent every literal string

**Reproduced:** the UI and direct Python command accept SCP name `$pelvis`. The same
JSON request fails with lookup error `'pelvis'`.
[`authoring.resolve`](../src/anthroforge/authoring.py) interprets every string beginning
with `$` as a stored-result reference, including nested values, with no literal escape.
Other text fields have the same transport restriction. Existing `$id.path` references
are useful and must remain supported.

**Proposed:** an unambiguous literal/reference encoding at the JSON transport boundary,
with regression cases for literal text, nested arrays/objects and existing references.
No document command, naming rule or formula parser needs to change.

### A5 — Recovery and project-library lifecycle

**Reproduced:** opening a generated recovery copy using public `open` keeps its path,
writer lock and `saved_revision=1`. The desktop recovery completion clears the path,
releases the lock and sets `saved_revision=-1`, requiring Save As.
[`ProjectLibrary.opened`](../src/anthroforge/desktop/project_library.py) chooses
[`projects.finish_recovery`](../src/anthroforge/application/projects.py).

There are no public operations for recovery discovery/open semantics or recent-project
list/clear. Autosave preferences are public, but the desktop instantiates/polls the
Qt-independent `Autosave` service; setting those preferences does not start a headless
autosave lifecycle. Persistent JSON `serve` also has no new-document/reset operation;
embedded Python can construct a new Session and CLI `new` starts a new process.

Ordinary `open` is not inherently incorrect: the missing public operation is **recovery**,
with its distinct ownership semantics. Recent-project bookkeeping is likewise a runtime
service, not an anatomical edit.

**Proposed:** expose explicit project-library operations using existing services, including
recovery ownership safeguards and isolated storage. Discuss headless autosave activation
and persistent-session reset behavior before implementing either; do not infer policy from
the desktop timer or silently enable periodic writes in every script.

### A6 — Bug/recommendation reports

The Help workflow can create annotated reports, browse them, edit descriptions and delete
obsolete entries. No feedback operation family is registered in `Session.command`.
The existing Qt-independent [`ReportService`](../src/anthroforge/feedback/service.py)
and [`LocalReportInbox`](../src/anthroforge/feedback/local_inbox.py) already provide
delivery/storage/inbox behavior; Python can use those services directly.

**Proposed:** expose that service contract for authoring clients, with explicit report
directory and image inputs. Keep live-window capture and the interactive annotation
editor in the desktop adapter. Do not route human bug reports through anatomical Issues
or alter the replaceable report consumer.

## Deliberate desktop-only interaction

Hover highlighting, mouse capture, gizmo drag math, keyboard/focus routing, panel layout,
dialogs, transient selection and temporary camera restoration are presentation mechanisms.
Their anatomical results are requested through explicit operations/transactions. Persisted
cameras, bookmarks, visibility and workspace state remain available to authoring.

Opening Explorer, Windows file association and opening Default Apps settings have no
meaning in a Qt-free process without a desktop. They are disclosed desktop integrations,
not missing anatomical operations. Recording a headless session cannot produce actual
QML binding or render-thread timings; collectors report that capability difference.

Do not turn these differences into artificial mouse/key APIs just to increase command
counts. A future live-desktop automation adapter would be a separately defined scope.

## Verification and limits

- Reproducible read/transport probes:
  [`authoring_parity_probes_043.py`](../tools/authoring_parity_probes_043.py).
  Uses disposable sessions and a preferences/recovery directory under
  `build/authoring-parity-043`; user projects and the real report inbox are untouched.
- Current packaged 0.4.2 passed all **35 portable workflow groups**, minimal PATH,
  offscreen UI and hidden QQuickRenderControl capture. Executable: the existing relocated
  `build/assembly-live-mirroring/portable/AnthroForge.dist/AnthroForge.exe`, built from
  `b3d6f898`; subsequent baseline changes are typing/docs/tooling, not runtime behavior.
- Portable evidence: `build/authoring-parity-043/portable/portable-check.json` and
  `portable.log`. That harness includes desktop-only adapters for feedback and recovery;
  their successful checks do **not** contradict A5/A6.
- Full Python suite: **2,763 passed** in 386.40 seconds. Existing dependency/Qt
  deprecation warnings remain; no failed tests. Audit-tool lint/function checks and
  link review are recorded in [the task record](tasks/authoring-parity-043.md).
- This is a family-level code/contract audit with representative behavioral checks,
  not an exhaustive cross-product of every parameter or a new addon geometry comparison.
  No interactive desktop acceptance or new geometry/algorithm qualification is claimed.

Reproduction uses the qualified native build and `uv run --no-sync python` with each
tool above. Generated inventories and probe JSON remain under ignored `build/`.

## Fix discussion and delivery boundary

Recommended order for discussion: **A1 current editing state, A2 candidate inspection,
A3 choice/effective-state queries, A4 literal transport, then A5/A6 runtime services**.
The first four directly improve reliable automated modeling and review. Recovery/report
coverage completes broader application parity, with the explicit policy choices above.

For any approved implementation, add paired desktop/public-operation cases for the
reported discrepancy, shared restrictions, cancel/undo, accepted/Manual revisions and
resource lifetime. Keep independent Qt-free API checks distinct from desktop rendering.
Retain this audit inventory to detect future UI paths that bypass the supported contract;
registration checks alone must never become a complete-parity gate.

No production changes, schema/version changes, new distribution or geometry changes are
part of this delivery. Fixes require the next discussion, as explicitly requested.
