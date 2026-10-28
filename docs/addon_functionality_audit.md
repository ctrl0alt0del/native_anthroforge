# Addon functionality audit — standalone 0.3.3

Audit date: 2026-10-24. Standalone runtime: `51ff0af`; subsequent `f0c1caf` adds
diagnostics only. This is an implementation audit, not a new release plan or a claim
that every Blender shape/update matches. Known shoulder/Thumb differences are recorded
separately in [confirmed parity findings](addon_parity_findings.md).

The subsequent [0.3.5 mirroring contract](specification_035.md) is implemented and qualified;
evidence is tracked in the [runtime walkthrough](mirroring_035.md). Its
[plan](implementation_035.md) preserves the addon inventory. Strict read-only reflection
replaces independent mirror solving; existing independent counterparts are not migrated.
The historical audit observations below remain scoped to their recorded revisions.
## Follow-up implementation status

The table below updates the original audit without rewriting its historical inventory.
`codex/parity-workflows-034` implemented D01–D12 through shared operations and desktop
entry points. They are integrated and qualified with mirroring and smooth propagation in
[0.3.6](workflows_036.md); no 0.3.4 release was delivered.

| Findings | Implemented follow-up |
| --- | --- |
| D01–D04 | Separate Fiber support policy, pin checks/approved repairs, Normal Offset, Rebind All, saved warm-start policy and cold rerouting. |
| D05 | Active length weight and trial checkpoint controls for Custom/PIQP; collision checks retained. |
| D06 | Connected body splitting with first SCP/children retained, siblings and shared Hook controls. |
| D07–D08 | Read-only source-replacement assessments, explicit loss/rebind approval, stale rejection and one-action application for imported SCPs and tissues. |
| D09 | Existing-tissue preset application with explicit preset/custom constraint ownership. |
| D10 | Surface-click creation of an already-bound, solved ROUTED Fiber, without an authored draft Curve. |
| D11 | Per-workspace world-space Fiber radius; native background tubes, staged rendering and displayed-mesh picking. |
| D12 | One-action ordered selection of all surface sources. |

Combined qualification is recorded in [the delivery task](tasks/workflows-036.md), with
donor evidence preserved in [the historical task](tasks/parity-workflows-034.md).
The user chose welded Ribs;
exact source shoulder response is not claimed fixed. Mirroring is now implemented;
skin and other deferred major systems remain outside this integration.

## Method and scope

Inspected the current addon operators, registered RNA properties, UI, and production
call paths against standalone typed records, command catalogue, native adapters, QML
controls and relevant regression tests. Runtime RNA inspection includes dynamically
installed fields, not just class annotations. Negative findings mean no corresponding
shared operation/control was found at this revision; custom scripts editing internal
records are not a finished user feature.

Addon paths below are relative to
`C:/Users/alexe/AppData/Roaming/Blender Foundation/Blender/5.0/scripts/addons/anthroforge`.
That working tree contains unrelated local changes, including new shortcut bone fitting.
Its base revision is `fae36aba1b208676cf21d7c4a78a20d5b1f68c66`; local changes were
inspected without editing or discarding them. Local inventory artifacts are
under `build/addon-capability-audit`. Existing release evidence, including the 0.3.3
2,056-test gate, remains historical evidence; it was not rerun as interactive acceptance
for this documentation audit.

## Major functionality already implemented

| Area | Standalone behavior present | Owning implementation / evidence |
| --- | --- | --- |
| SCP hierarchy and anatomical attachments | Empty grouping roots, parenting, promotion/reparenting through shared operations, independent duplication, child-preserving deletion, origin-to-attachment, surface/origin anchors, face/vertex locks, rotation strategies, explicit recapture | `application/operations.py`, `native/attachments.py`, `desktop/qml/Inspector.qml`; `tests/test_attachment_provenance.py`, `tests/test_task_priorities.py` |
| Editable primitives and deformers | Imported mesh, ordered loft, curve-deformed bodies and Segment Chain; shared Hooks, lattice, Shrinkwrap, simple subdivision, displacement and Simple Solidify | `core/construction.py`, `application/construction_evaluator.py`, `desktop/qml/{PrimitiveInspector,ControlInspector,DeformerStack,ThicknessInspector}.qml`; primitive/deformer parity tests |
| Curves and construction editing | First-class curves, Bézier/polyline/ROUTED/Parametric engines, handles/radius/tilt, closure, point insertion, drawing/placement, snapping/offset gestures, junctions, live consumers and independent copies | `core/construction.py`, `application/curve_edit_operations.py`, `desktop/qml/{CurveEditor,CurveEngine,ParametricInspector}.qml`; curve and Parametric tests |
| Fibers and surface bindings | Fiber subclasses Curve; independent creation, mandatory open endpoints/closed anchors, editable intermediate bindings, current-parent/any-parent capture, current-shape editing, automatic support fields, retained material bindings, SCP and tissue surface roles | `core/fibers.py`, `application/{fiber_operations,fiber_bindings,fiber_supports}.py`, `desktop/qml/FiberBinding.qml`; Fiber binding/edit/support tests |
| Routing | Native current solver, automatic obstacles plus explicit exclusions, preferred/adaptive samples, accepted-step budget, warm reuse, cancellation, Custom/PIQP preference and read-only route/contact inspection | `core/curve_engines.py`, `application/routing_evaluation.py`, `native/routing.py`, `desktop/qml/{RoutingSettings,RouteInspection}.qml`; routing and warm-start tests |
| Surfaces and membranes | Open/closed lofts, closed-boundary patches, branched open lofts, explicit junctions, source ordering/direction/ranges, persistent correspondence, Realign, source add/remove and Membrane conversion | `core/surfaces.py`, `application/surface_operations.py`, `desktop/qml/{SurfaceInspector,SurfaceSources,SurfaceBranches}.qml`; surface/branch/material tests |
| Muscle inflation | Control Point, Distributed and Section Profile; boundary power/attenuation/taper, per-part/per-side settings, two-sided envelopes, reversal, profile reset/scaling, side copy, branch connectors, height smoothing and cropping | `core/tissue_settings.py`, `application/{tissue_operations,tissue_part_operations}.py`, `desktop/qml/TissueInspector.qml`; inflation/profile/branch/crop tests |
| Soft tissue / legacy Blob equivalents | Unified TissueVCP over Anchor/Fiber/Membrane; radial sphere/ellipsoid, profile sweep and normal shells, backing/rims, fields, None/Geometric/Static PBD, fixed/soft source-relative and target-relative regions | `core/{tissues,tissue_settings,tissue_constraints,tissue_presets}.py`, `desktop/qml/{TissueRelaxation,TissueRegions,TissueFields}.qml`; shape/relaxation/constraint tests |
| Stacking | Automatic candidates, exclusions, requested/explicit order, multiple providers/chains, support regions, exact constraints, native vector stacking, diagnostics and footprint inspection | `core/tissue_stacking.py`, `application/tissue_stack_operations.py`, `desktop/qml/TissueStacking.qml`; stacking workflow/material tests |
| Numerical shortcuts and drivers | Implicit/explicit wrappers, Uniform vectors, labels/search/reordering, typed formulas/chains, cycles/failures, ownership/scope and temporary attachment policies; Parametric variables and retained Bézier construction | `application/{shortcut_operations,driving_operations,parametric_operations}.py`, `desktop/qml/{Shortcuts,ShortcutPolicies}.qml`; shortcut/formula/Parametric tests |
| Presentation and precise inspection | Anatomy/Construction views, focused workspaces, opacity/picking filters, axis cameras/restore, reference images, measurements/bookmarks, tissue stages, constraints/findings, painting/cutaways and shortcut Before/After reports | `desktop/qml`, `application/inspection_commands.py`; background acceptance tools and corresponding tests. Several are standalone additions or replacements for Blender host services. |
| Lifecycle, diagnostics and automation | Shared Qt-free headless commands, one coordinator, update modes, revision guards, undo/redo, checkpoints and atomic native-project saving; Issues, profiling, feedback reports, comparison/replay | `application/{commands,session,projects}.py`, `application/issues`, `profiling`; current release gate/portable evidence in [development status](development_status.md) |

The main numerical construction families are therefore present. The smaller omissions
below are concentrated in authoring/recovery controls and a few lifecycle operations.
Implementation presence must not be confused with universal geometry parity.

## Missing details within implemented systems

Priorities are audit recommendations, not approved implementation scope. H = accuracy or
recovery first; M = useful editing capability; L = convenience/presentation.

| ID | Gap | What already exists / what is missing | Source evidence and owning standalone boundary | Priority |
| --- | --- | --- | --- | --- |
| D01 | Author extra Fiber deformation supports | Dense support fields and automatic bone candidates exist. The user cannot explicitly add/remove an additional deformation support, particularly a tissue support not used by a bound control point. Routing obstacle selection is a different relationship. | Addon `ui/panels/fiber_attachment.py`, `operators/fiber_attachment.py`; app `application/fiber_supports.py`, `core/fibers.py`, `commands.py`: no authored support-list operation. Preserve current automatic defaults if adding explicit policy. | H |
| D02 | Rebind all Fiber anchors and propose bulk pin repairs | Per-point Rebind, generic Issues, Recalculate and Retry exist. The addon's one-action retained-position Rebind All and scan/propose/confirm pin-repair workflow are missing. Recalculation alone does not select a replacement binding. | Addon `app/use_cases/fiber_attachment.py::rebind_fiber`, `operators/fiber_repair.py`; app `application/fiber_bindings.py`, `application/issues/repairs.py`. Use the existing attachment/Issues/transaction infrastructure. | H |
| D03 | Persistent per-pin normal-offset editor | Captured offset data and Ctrl-wheel snap offset exist. A named editable Normal Offset on an existing Fiber pin, like an addon mid-touch offset, has no shared configuration operation or inspector control. | Addon `AF_FiberTouchPoint_Property.normal_offset`, `ui/panels/fiber_edit_panel.py::_draw_touch_offset`; app `FiberBinding`, `desktop/qml/FiberBinding.qml`. This is narrower than adding snapping. | M |
| D04 | Cold routing as an authoritative calculation | Automatic warm reuse exists; Inspect route has Start from planner, but that is read-only. No clear-warm/disable-warm or cold Recalculate operation publishes the cold result as accepted geometry. | Addon `app/use_cases/fiber_tools.py::clear_fiber_warm_start`, `fiber.use_warm_start`; app `application/{routing_evaluation,route_inspection}.py`, `desktop/qml/RouteInspection.qml`. | M |
| D05 | Remaining active routing controls | Samples, clearance and one accepted-step budget are editable. The addon's active length weight and distinction between interactive checkpoints/final solve budget are not exposed; the app uses length weight `.9` in its native configuration. | Addon `core/vcp/fiber_solver.py::_strengths`, `core/vcp/fiber_v2_runtime.py`, V3 settings; app `core/curve_engines.py`, `native/src/routing_solve.cpp`. Expose through typed native options and coordinator policy, not Python numerical loops. | M |
| D06 | Split a curve-driven SCP into connected SCPs | Curve subdivision and multi-piece bodies exist. App `curve.split` inserts a knot; it does not split the anatomical entity into multiple SCPs with shared joint Hooks. The addon has that composite authoring action. | Addon `core/action_library_split_corner.py::_run_split_corner`; app `application/primitive_operations.py::curve_split`, duplication/control operations. Reuse those operations in one coherent transaction. | M |
| D07 | Replace an imported SCP's source mesh in place | Import creates a new SCP. No Replace Geometry/source operation retains the old SCP identity, hierarchy and assigned controls. Image replacement already has its own correct lifecycle. | Addon `ui/panels/scp_objects_panel.py`, `af.set_scp_geometry_object`; app `application/importing.py`, `primitive_operations.py::update`. Attachment/topology remap or explicit rebind must be designed, not silently assumed. | M |
| D08 | Retarget an existing tissue to another attached construction source | Editing its current source and Make Independent work. `tissue.configure` does not accept `source`, so switching to another Anchor/Fiber/Membrane requires rebuilding the tissue rather than an explicit validated retarget operation. | Addon soft-tissue base/source controls; app `application/tissue_operations.py::CONFIGURATION`, `desktop/qml/TissueInspector.qml`. Field, constraint and topology handling need explicit rules. | M |
| D09 | Apply a preset to an existing tissue | Closed Bulk/Rim/Layer/Pouch/Custom are implemented creation defaults. No Apply Preset operation/control reapplies them to an existing tissue; changing a classification intentionally does not reset settings. | Addon `af.apply_soft_tissue_preset`, `ui/panels/soft_tissue_edit_panel.py`; app `core/tissue_presets.py::settings`, `application/tissue_operations.py`, `desktop/qml/TissueCreate.qml`. Define overwrite scope before implementing. | M |
| D10 | Direct surface-click Fiber creation | Place points -> Create Fiber works, with automatic endpoints/optional target overrides. The addon's Quick Fiber captures surface clicks and creates the already-bound Fiber in one tool; that entry point is missing. | Addon `operators/action_library_quick_fiber.py`; app `desktop/qml/FiberCreation.qml`, `application/fiber_operations.py::create`. Reuse generic creation and binding services. | L |
| D11 | Per-Fiber display thickness | Point radius, routing clearance and tissue width are different properties. Addon Fiber `thickness` controls presentation; app PathScene uses fixed line widths and has no equivalent per-Fiber display setting. | Addon `ui/panels/fiber_edit_panel.py::_draw_display`; app `desktop/qml/PathScene.qml`, `core/fibers.py`. Keep this in presentation, separate from collision radius. | L |
| D12 | Select all surface source curves/Fibers at once | Source references, ordering and individual Edit curve navigation exist. The addon's Select Sources action has no equivalent one-action group selection in the surface inspector. This does not imply simultaneous multi-curve component editing. | Addon `af.select_fiber_surface_sources`; app `desktop/qml/SurfaceSources.qml`. UI convenience over existing selection/reference queries. | L |

Before these conveniences, resolve the separately confirmed [migration/anchor fidelity
findings](addon_parity_findings.md): transferred shoulder frames, effective Thumb policy,
and stable owner anchors through Boolean remeshing. They are defects within present
functionality, not missing major engines. The small residual after enabling Thumb
backsolve must not be hidden by calling that option alone a complete fix.

## Existing capabilities that should not be proposed again as missing

- Boundary Power, copy inflation between sides/all parts, proportional Section Profile
  maximum-depth editing, profile reset, and branch width/fullness are already in the
  inspector and shared operations.
- Hook membership/weights, Reset/Recenter, ordered deformers, lattice interpolation/
  resize/Outside, Simple Solidify options and Shrinkwrap controls exist. Some weight
  editing uses text/index arrays rather than Blender's visual vertex-group workflow;
  that is a host-editor convenience gap, not a missing deformation kernel.
- SCP face/vertex locking includes Lock from last pick and Clear in Inspector. Surface
  source add/remove/order, Realign, Make Independent, and direct Membrane/Tissue creation
  are already present.
- Native routing warm starts, obstacle exclusions and contact/planner inspection exist.
  The missing cold authoritative solve in D04 must not be confused with the existing
  read-only cold inspection.
- Both current addon V3 and app enforce segment collision checks. The addon V3 policy
  forces curvature weight to zero despite older UI controls. Do not recreate legacy
  switches or claim an effective curvature-control regression merely from property names.
- Blob sphere/ellipsoid and gravity/sag functionality maps to attached radial tissue;
  a second Blob entity hierarchy is unnecessary. Muscle-to-surface conversion is largely
  replaced by the already-independent live construction source, which survives consumers.
- Free/Controlled and special loop entities, Blender bound-object bookkeeping and proxy
  edit Apply/Refresh steps were deliberately replaced by curve engines, closure, typed
  relationships and normal edit transactions. Their old buttons are not missing features.

## Larger unimplemented systems and intentional release boundaries

| System | Audit status |
| --- | --- |
| Live mirroring/symmetry across SCPs, Fibers, surfaces and tissues | Implemented in [0.3.5](mirroring_035.md) as strict source reflection, with shared identities, source-only evaluation and read-only inspection. Independent mirrored bones in migrated projects remain separate. |
| Draft Skin, collagen/gap fields, remeshing/topology budgets, final-skin reference/deformation and warm skin/topology updates | Implemented in [0.4.0](tasks/skin-040.md), including accepted whole-body draft parity. [0.4.1](tasks/release-041.md) restores the audited reference preparation, diagnostics, achieved budgets, persistent weights and UI details. Legacy update compatibility remains distinct from the durable-reference path. Existing quality limitations remain explicit. |
| Reusable anatomical package/document/subgraph import and SCP-diff application | Native projects open/save and meshes import; there is no general public merge/append or addon AF package/diff importer. Custom migration scripts do not establish this as a desktop feature. |
| Non-numeric shortcut exposure and general Blender RNA paths | Addon supports Boolean/enum/string proxy values. Standalone 0.3 deliberately supports numerical wrappers and a restricted formula language; extending that contract is a separate choice. |
| Shortcuts baked to an armature / shortcut bone fitting | Implemented in [0.4.0](skin_workflow.md): independent derived fitting and playback preserve editable anatomy. Source fingerprints and strategy limits remain in the inventory. 0.4.1 exposes active bone count and moving-region held-out error. Product export remains skin-only OBJ; armature export is not claimed. |
| Anatomical reconstruction/fitting, legacy project conversion and arbitrary Blender editing/Geometry Nodes | Deferred or outside the specialized standalone contract. The current one-off migration and limited editable primitives do not imply a general Blender replacement. |
| Apply/Bake and duplicate-derived-final-mesh authoring | Destructive Apply/Bake remains unavailable. The explicitly requested 0.4.0 shortcut-fitting workflow adds an independent derived skinning result while retaining editable source anatomy; it does not authorize general snapshot baking. |

## Recommended sequence for discussion

1. Repair the known parity defects and qualify the migrated assembly against the addon.
2. D01–D04: Fiber support, binding/repair and cold-solve control, where missing authoring
   operations hinder recovery from the failures users actually encounter.
3. D05–D09: active solver settings and reusable SCP/tissue editing operations. Confirm
   overwrite/remap behavior for replacements/presets before implementation.
4. D10–D12: shorter creation/selection workflows and display thickness.

Keep mirroring, skin and rig fitting visible as larger releases. No priorities here
authorize changes to existing attachment behavior, collision safety, accepted results,
or the permanently editable construction model.
