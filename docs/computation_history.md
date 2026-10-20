# Computation inventory and approach history

This is the maintained register of **what AnthroForge computes, how it computes it,
and why an approach changed**. Update the current inventory and add a change record
in the same change set as the implementation. A passing solver return is not proof
that a shape is correct; records must connect the observed problem to the actual result.

Initial inventory: **0.2.2**, source `a93b5149e853eefd71a7875a3885a3a68a1d4a3a`,
2026-10-20. The historical entries below are backfilled from identified implementation
and qualification records, not a claim to reconstruct every earlier commit.
Subsequent entries must record every computational approach change.

## Scope and reading guide

The inventory groups operations by computational responsibility, rather than listing
every function, command alias or UI button. It includes numerical construction,
interactive geometry queries, evaluation coordination and supporting workloads.
Rows have permanent IDs; add IDs without renumbering or reusing old ones.

- Numerical geometry, fitting, optimization and repeated geometric queries run in
  the existing C++ library. Python supplies owned inputs, application policies and
  publication. Some fixed-size camera/UI arithmetic remains in Python.
- Qt/GPU rendering and Pillow image decoding are distinct supporting computations;
  they are not anatomical solvers. Scheduling policies are Python application logic.
- Fiber is a Curve with anatomical bindings. Membrane is a Surface made from Fibers.
  They reuse curve/surface engines rather than duplicating them.
- Tissue Base, Rest, Intrinsic, Plan and Final are separate evaluation stages.
  Muscle/fat classifications select defaults, not different evaluators.
- Test links identify maintained validation entry points. They do not claim that
  every possible input is valid or that this documentation task reran those tests.

Current behavior is governed by the [primitive](primitives_012.md),
[curve/fiber/surface](specification_020.md), [routing workflow](specification_021.md)
and [tissue](specification_022.md) specifications. See
[architecture](architecture.md) for ownership and [validation](development_status.md)
for qualified builds. Historical UI/version statements in linked task records are
evidence for those revisions, not current workflow instructions.

## Current computation inventory

### Meshes, primitives and deformers

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| G01 | Mesh import: parse OBJ/STL/PLY, convert units/axes and construct owned canonical mesh data. | [mesh_io.cpp](../native/src/mesh_io.cpp) | [import formats](../tests/test_import_formats.py) |
| G02 | Mesh preparation: polygon triangulation, topology reuse, joins/deformed copies, bounds, normals, spatial acceleration and render chunks. Geometry-only intermediates finalize once; deformation preserves compatible accepted connectivity. | [mesh_build.cpp](../native/src/mesh_build.cpp), [mesh_topology.cpp](../native/src/mesh_topology.cpp) | [geometry preparation](../tests/test_geometry_preparation.py) |
| G03 | Coordinate/frame calculations: TRS, matrix products/inverses, parent-relative placement, batched point transforms, quaternion/axis rotation and transformed bounds. Shared by anatomy, controls, consumers and tools. | [transforms.cpp](../native/src/transforms.cpp), [object frames](../src/anthroforge/application/object_frames.py) | [transform deltas](../tests/test_transform_delta.py), [shared curves](../tests/test_shared_curves.py) |
| G04 | SCP loft primitives: sample ordered curve pairs, produce shared strips, caps and canonical polygons using consumer ranges, placement and density. | [loft.cpp](../native/src/loft.cpp), [construction adapter](../src/anthroforge/native/construction.py) | [primitive parity](../tests/test_primitive_parity.py) |
| G05 | Curve-deformed bodies: box/cylinder/capsule bases, whole-curve fit or fixed-length placement, radius/tilt-aware deformation and multiple-piece assembly. Cache reusable undeformed bases. | [curve_body.cpp](../native/src/curve_body.cpp), [curve_deform.cpp](../native/src/curve_deform.cpp) | [primitives](../tests/test_primitives.py), [geometry preparation](../tests/test_geometry_preparation.py) |
| G06 | Hook deformation: bind/reset/recenter transforms, point membership, weights, inversion, strength and distance/custom-curve falloff. Shared influence preparation is native. | [hooks.cpp](../native/src/hooks.cpp), [influence.cpp](../native/src/influence.cpp), [curve_mapping.cpp](../native/src/curve_mapping.cpp) | [primitive parity](../tests/test_primitive_parity.py), [native preparation](../tests/test_native_preparation.py) |
| G07 | Lattice deformation: grid generation/resizing, interpolation, cage/object frames, weighted influence and Outside behavior. | [lattices.cpp](../native/src/lattices.cpp) | [primitive parity](../tests/test_primitive_parity.py), [anatomical primitives](../tests/test_anatomy_primitives.py) |
| G08 | Thickness: Blender Simple Solidify behavior, weighted offsets, rims, even thickness, normal handling and clamping. Ordered after applicable deformation; Complex mode is absent. | [solidify.cpp](../native/src/solidify.cpp) | [primitive parity](../tests/test_primitive_parity.py) |

### Curves and path engines

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| C01 | Bézier path evaluation: handle modes, cubic sampling, open/closed paths and authored radius/tilt. | [curves.cpp](../native/src/curves.cpp), [path registry](../native/src/path_registry.cpp) | [curve parity](../tests/test_curve_parity.py), [curve engines](../tests/test_curve_engine.py) |
| C02 | Exact polyline evaluation: straight segments through authored points, including ordinary closure without a duplicated authored endpoint. | [path registry](../native/src/path_registry.cpp) | [native paths](../tests/test_native_paths.py) |
| C03 | Path frames and consumer sampling: arc-length/range sampling, direction and start correspondence, anchored sampling, frame transport and body placement. Solver samples remain separate from authored controls. | [curve_frames.cpp](../native/src/curve_frames.cpp), [path_resampling.cpp](../native/src/path_resampling.cpp) | [anchored sampling](../tests/test_anchored_sampling.py), [consumer sampling](../tests/test_consumer_sampling.py) |
| C04 | Drawing/fitting: pointer-stroke depth, surface projection/fallback, offsets, image-plane drawing, corner detection and native cubic fitting. A completed stroke authors one curve. | [drawing.cpp](../native/src/drawing.cpp), [curve_fit.cpp](../native/src/curve_fit.cpp), [drawing tasks](../src/anthroforge/application/drawing_tasks.py) | [drawing parity](../tests/test_drawing_parity.py), [strokes](../tests/test_strokes.py) |
| C05 | Curve editing math: closest location to the pointer, cubic subdivision/insertion, handle updates, selected-control transforms and current-path rebasing/deformation. | [curve_queries.cpp](../native/src/curve_queries.cpp), [path_editing.cpp](../native/src/path_editing.cpp) | [curve queries](../tests/test_curve_queries.py), [standalone editing](../tests/test_standalone_editing.py) |
| C06 | Routed path solving: capture eligible obstacles, classify pin contacts, plan feasible corridors/roadmaps, validate warm starts, solve constrained SQP with collision/clearance checks and report termination. Open/cyclic paths share the engine. | [routing.cpp](../native/src/routing.cpp), [routing_planner.cpp](../native/src/routing_planner.cpp), [routing_solve.cpp](../native/src/routing_solve.cpp) | [routing parity](../tests/test_routing_parity.py), [surface pins](../tests/test_routing_surface_pins.py), [snapped routing](../tests/test_snapped_routing.py) |
| C07 | Explicit junction resolution: canonical shared-point identity, incident-curve updates, transforms and atomic propagation. Proximity alone never creates a junction. | [junction evaluation](../src/anthroforge/application/junction_evaluation.py), [junction edits](../src/anthroforge/application/junction_edits.py) | [junction workflow](../tests/test_junction_workflow.py), [fiber junctions](../tests/test_fiber_junctions.py) |

### Attachments and attached construction

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| A01 | SCP attachments: nearest/ray capture, retained surface/frame/offset records and batched parent-to-child transform propagation. | [attachment.cpp](../native/src/attachment.cpp), [attachment adapter](../src/anthroforge/native/attachments.py) | [addon parity](../tests/test_addon_parity.py), [assembly](../tests/test_assembly.py) |
| A02 | Anchor/point bindings: capture and resolve explicit SCP or Tissue Base/Final material locations, orientation and offsets. Resolve against accepted deformed material without automatic nearest reassignment. | [point attachment adapter](../src/anthroforge/native/point_attachments.py), [material_binding.cpp](../native/src/material_binding.cpp), [surface providers](../src/anthroforge/application/surface_providers.py) | [point attachments](../tests/test_point_attachments.py), [tissue anchor material](../tests/test_tissue_anchor_material.py) |
| A03 | Fiber attachment fields: dense surface captures, nearest-owner runs, arc-length blending between owners, structural pins and retained material influence. Applies across curve engines. | [attachment_weights.cpp](../native/src/attachment_weights.cpp), [attachment fields](../src/anthroforge/native/attachment_fields.py) | [attachment weights](../tests/test_attachment_weights.py), [attachment fields](../tests/test_attachment_fields.py) |
| A04 | Fiber resolution/editing: resolve its current attached shape, edit authored controls, rebind edited endpoints using Current/Any eligible parent policy, preserve unedited pins, then evaluate its path engine. | [fiber bindings](../src/anthroforge/application/fiber_bindings.py), [fiber edit evaluation](../src/anthroforge/application/fiber_edit_evaluation.py), [path_editing.cpp](../native/src/path_editing.cpp) | [fiber editing](../tests/test_fiber_editing.py), [tissue fiber material](../tests/test_tissue_fiber_material.py) |

### Surfaces and membranes

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| S01 | Source correspondence: align compatible closed paths initially, persist starting correspondence/direction, apply per-source sampling ranges and transforms; explicit Realign recalculates correspondence. | [surface_alignment.cpp](../native/src/surface_alignment.cpp), [surface_sampling.cpp](../native/src/surface_sampling.cpp) | [native surfaces](../tests/test_native_surfaces.py), [surface sources](../tests/test_surface_sources.py) |
| S02 | General lofts: construct open/compatible closed surfaces from Curve/Fiber samples with material grids, stable seams and structural material pins. All-Fiber inputs produce a Membrane through the same evaluator. | [surface_loft.cpp](../native/src/surface_loft.cpp), [surface_material_pins.cpp](../native/src/surface_material_pins.cpp) | [surface workflow](../tests/test_surface_workflow.py), [material pins](../tests/test_material_pins.py) |
| S03 | Closed-curve patches: project and triangulate a boundary, subdivide, fair interior samples while retaining boundary constraints, and retain material correspondence. | [surface_patch_projection.cpp](../native/src/surface_patch_projection.cpp), [surface_patch_fairing.cpp](../native/src/surface_patch_fairing.cpp) | [native surfaces](../tests/test_native_surfaces.py) |
| S04 | Branched open lofts: explicit junction-based branch sampling, connector assembly and welded seams. Reject unsupported nested/closed branches and overlapping root intervals. | [surface_branches.cpp](../native/src/surface_branches.cpp), [surface_branch_sampling.cpp](../native/src/surface_branch_sampling.cpp) | [native surface branches](../tests/test_native_surface_branches.py), [surface branches](../tests/test_surface_branches.py) |

### Tissue construction, inflation and relaxation

The [capability matrix](specification_022.md#supported-combinations) controls composition.
Presence in this inventory does not make every mode available on every source.

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| T01 | Base preparation: capture accepted Anchor frame, Fiber path or Membrane geometry; refine material grids/branches without editing sources. Subdivide existing intervals, retaining source grid lines and correspondence. | [tissue sources](../src/anthroforge/application/tissue_sources.py), [tissue_refinement.cpp](../native/src/tissue_refinement.cpp), [tissue_branch_refinement.cpp](../native/src/tissue_branch_refinement.cpp) | [tissue workflow](../tests/test_tissue_workflow.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
| T02 | Control Point inflation: displaced control, falloff, boundary attenuation, longitudinal taper, direction and enable/disable over supported material grids. | [tissue_inflation.cpp](../native/src/tissue_inflation.cpp), [pinned tissue kernels](../native/migration/tissue/sources.json) | [tissue inflation](../tests/test_tissue_inflation.py) |
| T03 | Distributed inflation: area-weighted source normals, physical mass/cotangent screened diffusion of directions, normalization and authored amount/edge/taper application. The old local height-reduction heuristic is removed. | [tissue_directions.cpp](../native/src/tissue_directions.cpp), [tissue_inflation.cpp](../native/src/tissue_inflation.cpp) | [inflation regression](../tests/test_tissue_inflation_regression.py) |
| T04 | Section Profile: four station depths/peaks, roundness, initialization and Local/Smooth/Section directions, restricted to ordinary open lofts. | [tissue_inflation.cpp](../native/src/tissue_inflation.cpp), [tissue_parameters.cpp](../native/src/tissue_parameters.cpp) | [tissue inflation](../tests/test_tissue_inflation.py), [tissue controls](../tests/test_tissue_controls.py) |
| T05 | Parts/sides and envelope assembly: per-part inflation, branch geodesic fields, seam displacements, Hermite connectors, reversal and independent two-sided composition. | [tissue_parts.cpp](../native/src/tissue_parts.cpp), [tissue_branch_connector.cpp](../native/src/tissue_branch_connector.cpp), [tissue_envelope.cpp](../native/src/tissue_envelope.cpp) | [tissue branches](../tests/test_tissue_branches.py), [envelopes](../tests/test_tissue_envelopes.py) |
| T06 | Anchor-based radial tissue: sphere/ellipsoid construction in the resolved source frame. | [tissue_radial.cpp](../native/src/tissue_radial.cpp) | [tissue shapes](../tests/test_tissue_shapes.py) |
| T07 | Fiber-based tissue: open/cyclic profile sweep, width/depth/power, resolution, taper, backing and cap construction. | [tissue_profile_sweep.cpp](../native/src/tissue_profile_sweep.cpp) | [tissue shapes](../tests/test_tissue_shapes.py) |
| T08 | Membrane normal shell: weighted normals, minimum/maximum thickness, power, backing and rims. Missing fields use boundary-distance defaults; explicit all-zero fields remain authoritative. | [tissue_normal_shell.cpp](../native/src/tissue_normal_shell.cpp), [tissue_shape_fields.cpp](../native/src/tissue_shape_fields.cpp) | [tissue shapes](../tests/test_tissue_shapes.py), [shape workflow](../tests/test_tissue_shape_workflow.py) |
| T09 | Fields and regions: material-domain masks, boundary/geodesic distances, custom values, feathering, region selection/outline geometry and source-domain signature validation. | [tissue_masks.cpp](../native/src/tissue_masks.cpp), [tissue_regions.cpp](../native/src/tissue_regions.cpp), [tissue fields](../src/anthroforge/application/tissue_fields.py) | [field editing](../tests/test_tissue_field_editing.py), [region editing](../tests/test_tissue_region_editing.py) |
| T10 | Constraint goals: source/target-relative Fixed/Soft regions, material binding resolution, normal offsets, tethers, exact backing and conflicting-goal detection. Constraint enforcement remains active with relaxation None. | [tissue_constraints.cpp](../native/src/tissue_constraints.cpp), [material bindings](../src/anthroforge/native/material_bindings.py) | [target regions](../tests/test_tissue_target_regions.py), [tissue relaxation](../tests/test_tissue_relaxation.py) |
| T11 | Height smoothing: cotangent-biharmonic bounded height QP with PIQP, exact boundary/seam/zero-height pins, independent optimality checks and complete-mesh acceptance. Off bypasses the solve. | [smoothing_core.cpp](../native/src/smoothing_core.cpp), [tissue_smoothing.cpp](../native/src/tissue_smoothing.cpp) | [tissue smoothing](../tests/test_tissue_smoothing.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
| T12 | Geometric relaxation: source-specific static sag; radial tissue iterates gravity, neighbor smoothing and host-surface projection, while sweep/shell use their supported geometric displacement rules. | [tissue_geometric.cpp](../native/src/tissue_geometric.cpp), [tissue_point_relaxation.cpp](../native/src/tissue_point_relaxation.cpp) | [relaxation parity](../tests/test_tissue_relaxation_parity.py) |
| T13 | Static PBD relaxation: native iterative gravity, shape/volume retention where applicable, slack, constraints and convergence diagnostics. Reuses canonical triangles; not animation or generalized contact. | [tissue_static.cpp](../native/src/tissue_static.cpp), [tissue_relaxation.cpp](../native/src/tissue_relaxation.cpp) | [relaxation parity](../tests/test_tissue_relaxation_parity.py), [relaxation quality](../tests/test_tissue_relaxation_quality.py) |
| T14 | Material-domain crop: clip corresponding base/output and assemble crop topology while retaining material mappings. Crop edges do not become attachments or zero-inflation boundaries. | [tissue_crop.cpp](../native/src/tissue_crop.cpp), [tissue_crop_envelope.cpp](../native/src/tissue_crop_envelope.cpp) | [tissue crops](../tests/test_tissue_crops.py), [crop workflow](../tests/test_tissue_crop_workflow.py) |

### Stacking

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| K01 | Candidate/support planning: detect surface relationships and support regions, derive automatic order, apply explicit order/exclusions, and retain provenance. Only accepted providers become final prerequisites. | [stacking.cpp](../native/src/stacking.cpp), [stack evaluation](../src/anthroforge/application/tissue_stack_evaluation.py) | [stacking phases](../tests/test_stacking_phases.py), [stack workflow](../tests/test_tissue_stack_workflow.py) |
| K02 | Vector stacking: material correspondence and direction transport, selected support regions, multiple providers and provider-first chains without redundant ancestor displacement. | [tissue_stacking.cpp](../native/src/tissue_stacking.cpp), [tissue_stack_directions.cpp](../native/src/tissue_stack_directions.cpp) | [native stacking](../tests/test_tissue_stacking_native.py), [mixed stacking](../tests/test_tissue_mixed_stacking.py) |
| K03 | Constrained stacking smoothing: sparse exact material-pin/backing equations, localized displacement smoothing and assembled side/group output. Whole-tissue groups retain the actual side dependency graph. | [tissue_stack_constraints.cpp](../native/src/tissue_stack_constraints.cpp), [material_pin_equations.cpp](../native/src/material_pin_equations.cpp), [stack groups](../src/anthroforge/application/tissue_group_tasks.py) | [stack material](../tests/test_tissue_stack_material.py), [stack groups](../tests/test_tissue_stack_groups.py) |
| K04 | Final stacking validation: inspect complete assembled output for folds, self-intersections and bone/neighbor conflicts. Failed stacking displays current intrinsic geometry but does not publish a successful Final prerequisite. | [stacking_surface_validation.cpp](../native/src/stacking_surface_validation.cpp), [tissue_stack_assembly.cpp](../native/src/tissue_stack_assembly.cpp) | [complete geometry](../tests/test_stacking_complete_geometry.py), [group lifecycle](../tests/test_tissue_group_lifecycle.py) |

### Spatial queries, measurements and images

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| Q01 | Interactive picking/snapping: double-precision ray/surface hits, native outward snap margins and nonnegative user offsets, cached component queries, path picking and displayed-revision agreement. Exact measurement hits are not offset. | [ray_queries.cpp](../native/src/ray_queries.cpp), [surface_snap.cpp](../native/src/surface_snap.cpp), [component_index.cpp](../native/src/component_index.cpp), [path_presentation.cpp](../native/src/path_presentation.cpp) | [surface snapping](../tests/test_surface_snapping.py), [component picking](../tests/test_component_picking.py), [surface picking](../tests/test_surface_picking.py), [held input](../tests/test_held_input.py) |
| Q02 | Deformation quality: compare canonical meshes for new transverse crossings and collapsed faces, distinguishing coincident boundary contact; large normal rotation is informational. Shared by inflation/smoothing/relaxation. | [mesh_quality.cpp](../native/src/mesh_quality.cpp) | [mesh quality](../tests/test_mesh_quality.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
| Q03 | Advisory path collision: check accepted authored-engine Fiber centerline segments against eligible surfaces, with attachment-contact handling and incomplete-provider reporting. Does not silently reroute the curve. | [path_collisions.cpp](../native/src/path_collisions.cpp), [fiber collision Issues](../src/anthroforge/application/issues/fiber_collisions.py) | [path collisions](../tests/test_path_collisions.py), [fiber collision Issues](../tests/test_fiber_collision_issues.py) |
| Q04 | Measurements: resolve retained barycentric surface witnesses to world XYZ and compute straight-line distance. Camera framing/axis-view/restore calculations preserve gesture continuity. | [measurement.cpp](../native/src/measurement.cpp), [desktop view tools](../src/anthroforge/desktop) | [measurements](../tests/test_measurements.py), [view framing](../tests/test_view_framing.py), [view gestures](../tests/test_view_gestures.py) |
| I01 | Image decoding/preparation: PNG/JPEG decode, EXIF orientation, asset sharing and native RGBA tile preparation, executed as background creation work. | [image assets](../src/anthroforge/application/image_assets.py), [image.cpp](../native/src/image.cpp) | [reference images](../tests/test_reference_images.py) |
| I02 | Image placement/presentation: world/local frames, world-preserving reparenting, two-point physical calibration, aspect-preserving replacement, plane picking, side/axis visibility and affine tile geometry. | [image_placement.cpp](../native/src/image_placement.cpp), [Qt image geometry](../native/qt/image_geometry.cpp) | [image presentation](../tests/test_image_presentation.py), [image tools](../tests/test_image_tools.py) |

### Evaluation and supporting application workloads

These are real costs but not numerical anatomy algorithms. Keep them visible when
explaining performance; a fast native kernel does not imply a responsive application.

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| R01 | Dependency/index computation: hierarchy/registry lookup, reference/topology restrictions, output-port graphs, reverse invalidation, SCC cycles, automatic obstacle eligibility and publication-frontier traversal. Reuse immutable structure on value-only edits. | [document index](../src/anthroforge/core/document_index.py), [routing obstacles](../src/anthroforge/core/routing_obstacles.py), [dependent tasks](../src/anthroforge/application/dependent_tasks.py) | [document index](../tests/test_document_index.py), [publication frontier](../tests/test_publication_frontier.py) |
| R02 | Task assessment/coordination: workload estimates plus measured history, coalescing/delays, shared inline budget, worker admission, reservations, dispatch-time capture, cancellation and stale-result checks. | [coordinator](../src/anthroforge/application/coordinator.py), [task schedulers](../src/anthroforge/application/task_schedulers.py), [tissue scheduling](../src/anthroforge/application/tissue_scheduling.py) | [task coordination](../tests/test_task_coordination.py), [active jobs](../tests/test_active_jobs.py) |
| R03 | Transactions/history/checkpoints: derive changes, commit/cancel edits, maintain undo/redo restart recipes, choose saveable revisions and validate historical asynchronous captures. | [history](../src/anthroforge/application/history.py), [changes](../src/anthroforge/application/changes.py), [authored jobs](../src/anthroforge/application/authored_jobs.py) | [interleaving](../tests/test_interleaving.py), [capture history](../tests/test_capture_history.py) |
| R04 | Cache/resource work: keys, immutable leases, hit/miss/eviction, content equivalence and ownership across document/history/jobs/viewport. Includes Body bases, routing scenes and tissue material preparation. | [resource cache](../src/anthroforge/native/resource_cache.py), [base cache](../src/anthroforge/native/base_cache.py), [resources](../src/anthroforge/application/resources.py), [mesh_equivalence.cpp](../native/src/mesh_equivalence.cpp) | [routing scene cache](../tests/test_routing_scene_cache.py), [tissue material cache](../tests/test_tissue_material_cache.py), [construction resources](../tests/test_construction_resources.py) |
| R05 | Viewport publication/rendering: stage complete native mesh/path/image buffers, switch displayed geometry and picking together, generate controls, perform Qt Quick 3D shading, opacity/depth and selection-outline passes. | [Qt geometry adapters](../native/qt), [outline shader](../native/qt/shaders/outline.frag), [desktop](../src/anthroforge/desktop) | [viewport publication](../tests/test_viewport_publication.py), [capture staging](../tests/test_capture_staging.py), [path presentation](../tests/test_path_presentation.py) |
| R06 | UI projection/model work: incremental scene/property/outliner/Activity/Issues/choice rows, summaries, display-unit conversion and filtered lists. Preserve identities instead of recreating whole models on every edit. | [scene projection](../src/anthroforge/desktop/scene_projection.py), [property projection](../src/anthroforge/desktop/property_projection.py), [Activity](../src/anthroforge/desktop/activity_model.py) | [scene changes](../tests/test_scene_changes.py), [Activity model](../tests/test_activity_model.py), [choice model](../tests/test_choice_model.py) |
| R07 | Issues checks: evaluate structural/readiness/attachment/dependency diagnostics and optional native collision checks, retain scoped stale evidence, and verify requested repairs. Read-only checks use the common coordinator. | [Issue system](../src/anthroforge/application/issues/system.py), [providers](../src/anthroforge/application/issues/providers.py) | [Issue lifecycle](../tests/test_issue_lifecycle.py), [Issue integration](../tests/test_issue_integration.py) |
| R08 | Runtime profiling: opt-in Qt/native/application events, monotonic alignment, bounded rings/queues, summaries, model churn, invalidation causes, cache/resource attribution and background trace archive export. | [profiling](../src/anthroforge/profiling), [Qt collector](../native/profiling) | [profiling](../tests/test_profiling.py), [profile diagnostics](../tests/test_profile_diagnostics.py) |
| R09 | Project persistence: schema-4 validation, encode/decode editable records and accepted resources, compression/decompression, atomic saving and background opening. Never serialize native handles or undo history. | [storage](../src/anthroforge/application/storage.py), [resource storage](../src/anthroforge/application/resource_storage.py) | [headless](../tests/test_headless.py), [tissue headless](../tests/test_tissue_headless.py) |
| R10 | Inspection/feedback reports: freeze a revision/presentation, hidden GPU capture and archive creation; screenshot annotations, PNG encoding, report preview decoding, atomic text updates and deletion are a separate reporting service. | [inspection report](../src/anthroforge/application/inspection_report.py), [feedback painting](../src/anthroforge/desktop/feedback_paint.py), [feedback storage](../src/anthroforge/feedback/storage.py) | [inspection export](../tests/test_inspection_export.py), [feedback](../tests/test_feedback.py), [feedback inbox](../tests/test_feedback_inbox.py) |

### Coverage and exclusions

The inventory covers all public native interface families in
[native/include/anthroforge](../native/include/anthroforge), compiled geometry sources
in [native/CMakeLists.txt](../native/CMakeLists.txt), the Qt/profiling libraries, and
the registered application job families. Helper routines and variants belong to their
owning row rather than receiving separate IDs.

Coordinator job names map to the register as follows:

| Job family | Inventory |
| --- | --- |
| `attachments`, `control_pose` | A01, G03 |
| `mesh_import`, `construction` | G01–G08, S02–S04, G02 finalization |
| `curve_path`, `curve_routing`, `curve_draw`, `surface_layout` | C01–C06, S01 |
| `fiber_capture`, `fiber_path`, `anchor_capture`, `anchor_binding` | A02–A04 |
| `tissue_base`, `tissue_rest`, `tissue_intrinsic` | T01; T02–T11; T10, T12–T14 respectively |
| `tissue_plan`, `tissue_final`, `tissue_constraint_capture` | K01; K02–K04; T10 respectively |
| `image_decode`, `issue_check`, `inspection_report` | I01, R07, R10 |
| `project_open`, `project_save` | R09 |
| `generic` | Shared lifecycle fallback, not an additional numerical algorithm |

Not currently implemented product computations: Draft Skin generation/export,
automatic anatomical reconstruction/fitting, mirroring, animation dynamics,
general physical contact/mutual compression, Complex Solidify and Apply/Bake.
Installed numerical packages and unused vendor code do not establish a product feature.
The existing skin-only export policy is a restriction, not evidence of a working skin solver.

## How to maintain the history

Record any change to an algorithm, objective, constraints, numerical tolerance,
sampling/refinement, validation, dependency/invalidation policy, execution location,
cache strategy or preparation/publication approach. Include optimizations intended to
preserve geometry. Pure renaming, formatting and UI wording need no entry unless they
change how computation is invoked or interpreted.

1. Update the affected inventory rows and link new ownership/tests.
2. Add the next `CH-###` record with the template below. Several tightly related
   changes may share an entry if each old/new approach and effect is explicit.
3. Keep evidence adjacent to the claim: baseline/candidate revisions, fixture/settings,
   comparison method, result and limits. Link compact committed fixtures and tests;
   identify raw profiles, `.blend` files and project copies under `build/` as local-only.
4. Distinguish observed defects, suspected causes, experiments, qualified results and
   remaining failures. A proposal or successful API call is not a demonstrated fix.
5. Preserve historical records. When replaced, set `Superseded by CH-###`; never reuse
   the ID or rewrite an old result as if the new approach had always been used.
   Record failed alternatives that would otherwise be tempting to repeat.
6. Include the entry in the implementation checkpoint and finish its qualification
   before the validated merge. Link to detailed task evidence rather than duplicating
   entire investigation diaries. No new user-approval gate is introduced.

This adapts the context/decision/consequences structure of
[Michael Nygard's decision records](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
with explicit numerical and performance evidence.

### Entry template

```text
### CH-NNN — Specific computation change

- Date; application version; status: Proposed / Experimental / Implemented /
  Qualified / Rejected / Superseded by CH-NNN.
- Computation IDs; owning components.
- Baseline and changed commit(s), plus packaged runtime when applicable.
- Observed problem: exact fixture/settings/trigger and user-visible failure.
- Before: algorithm, preparation, validation or execution approach.
- After: replacement and the specific difference.
- Why it addresses the cause: mechanism, not merely the desired outcome.
- Preserved contracts / intentional differences: topology, units, parameters,
  bindings, cancellation, history, failure retention, parity deviations.
- Evidence: baseline vs candidate, regression and representative cases, shape
  inspection where needed, profiler method/variance/overhead when relevant.
- Outcome and limits: fixed / improved / unchanged / still failing; scope and costs.
- Rejected alternatives and reason, if any.
- Evidence links; raw artifact location and local/committed availability.
```

## Recorded approach changes

### CH-001 — Incremental Activity presentation

- **2026-10-17; 0.1.5; Qualified.** R06, with R08 used for evidence.
  Baseline `3fa664d`; packaged correction `ce64fc3`.
- **Problem/before:** the user's 0.1.4 capture contained 170 Activity model
  replacements in 9.03 seconds, average binding time 13 ms; native picking averaged
  0.072 ms. Rebuilding list values/delegates made presentation expensive.
- **After/why:** one keyed Qt model updates changed rows/roles and inexpensive
  summaries. Stable delegates eliminate repeated model/binding construction.
  Job scheduling, recent 40-row scope, Cancel/Retry and geometry are unchanged.
- **Evidence/outcome:** serial comparisons over 24 processes and 48 gestures measured
  55.9–62.1% lower unrecorded handler means; snapping/undo passed. Retained candidate
  traces had no Activity replacements. Rings evicted older events, so total event
  counts across unequal retained windows must not be compared.
  This did not prove a twofold Ctrl-specific native snapping cost.
- [Investigation/qualification](tasks/activity-panel-015.md);
  [committed trial evidence](tasks/activity-panel-015-evidence.json).
  Raw profiles/captures are local under `build/activity-015/`.

### CH-002 — Incremental evaluation and deliberate geometry preparation

- **2026-10-18; 0.1.5; Qualified.** G02, G05, R01, R02, R04–R06.
  Baseline `d810557`; packaged correction `7436790`; implementation/qualification
  on the `codex/standalone-optimizations` history.

| Before and observed cause | Replacement and reason | Recorded outcome |
| --- | --- | --- |
| Deep scene/property projections and repeated object/model replacement during value edits. | Bounded ChangeJournal, incremental scene/property projections and stable field objects; recompute only affected presentation. | Integrated unrecorded ABBA handler means 9.27–11.20 ms → 3.99–4.94 ms; all expected snapping targets and undo checks passed. |
| Repeated document searches, relationship validation and dependency ordering on value-only edits. | Snapshot-owned lookup/structure indexes; rebuild on structural edits, reuse on value/revision changes. | Synthetic 1,024-SCP admission median approximately 86.8 ms → 1.4 ms; excludes worker and GUI time. |
| Build spatial/render data at intermediate deformation steps and recreate identical Body bases. | Geometry-only native intermediates, compatible topology reuse, one explicit finalization and bounded per-engine base cache. | Geometry microbenchmarks: 1.8 → 0.43 ms at 482 vertices; 20 → 4.2 ms at 4,034; 87 → 16.3 ms at 16,258. Large baseline variance reached 130 ms. |
| Scheduling scanned terminal history and retained captured inputs/closures. | Active job indexes separate from history; retire execution resources, keep compact retry/restart descriptions. | 50,000-row idle tick approximately 33 ms → 0.0013 ms; 5,000-job soak retained no captured snapshots/cancellation objects. |

These changes preserve dispatch-time inputs, complete read validation, coherent undo,
checkpoint blocking, canonical topology and staged visibility. They do not establish
real-time behavior on dense scenes: a large-cage spot check still measured 67 ms edit
commands and 43 ms mean frame interval.
[Qualification](tasks/standalone-optimizations.md) and
[committed measurements](tasks/standalone-optimizations-evidence.json) identify individual
trials and trace retention limits. Raw comparisons are under local
`build/standalone-optimizations/`.

### CH-003 — Batch remaining numerical preparation in C++

- **2026-10-18; 0.1.5; Qualified.** G03, G06, G07, C05, Q01.
  Baseline `7c55151`; qualified runtime `42af2d9`.
- **Before/problem:** Python built influence masks, curve/cage display connectivity,
  cubic query buffers and dispatched native transforms once per selected point.
  Numerical preparation still paid Python loop/boundary overhead.
- **After/why:** native influence and display/query preparation, plus coordinate
  conversion batched by target frame. Preserve order, explicit-empty membership,
  transforms and command semantics while reducing repeated interpreter crossings.
- **Evidence/outcome:** serial ABBA preparation trials produced identical rounded
  output hashes. 1,000-point curve query preparation fell from 1.614–1.641 ms to
  0.571–0.572 ms; 1,000 selected-point conversion from 22.379–22.968 ms to
  1.116–1.165 ms. The latter intercepts publication and is not full gesture latency.
  Python still owns authored records, graph/scheduler policies and serialization.
- [Audit/qualification](tasks/native-boundary-audit.md);
  [committed measurements](tasks/native-boundary-audit-evidence.json).
  Raw snapshots/reports are local under `build/native-boundary-audit/`.

### CH-004 — Surface contacts and invalid warm routes

- **2026-10-19; 0.2.0 correction; Qualified.** C06, Q03.
  Baseline `2e8dc0b`; qualified runtime `7e146a1`.
- **Before/problem:** `solver_test.anthroforge` had a routed curve but an empty
  obstacle set. Selecting its cubes then exposed rejection of unbound surface knots
  and reuse of a straight warm path crossing the cubes.
- **After/why:** native classification recognizes exact surface contacts within the
  numerical floor without creating anatomical bindings. Validate warm seeds for
  solid-interior feasibility; invalid seeds use corridor planning, and failed warm
  solves receive one cold attempt. Explicit owners remain authoritative.
- **Evidence/outcome:** exact fixture paths had no centerline intersections after
  save/reopen; authored points stayed unchanged. Inside/merely-near points remain
  rejected. Existing donor/skull cases passed.
- **Rejected:** full-clearance rejection of every warm seed broke valid skull
  continuation; mere retry-on-failure missed incorrectly accepted crossing seeds.
  Feasibility and recoverable clearance are different conditions.
- [Evidence](tasks/solver-routing.md),
  [warm regression](../tests/test_routing_warm.py),
  [contact regression](../tests/test_routing_surface_pins.py).
  Raw project/captures are local under `build/solver-routing/`.
  Explicit-only obstacle defaults were subsequently replaced by CH-005.

### CH-005 — Automatic obstacles and reusable collision captures

- **2026-10-19; 0.2.1; Qualified.** C06, R01, R04, R08.
  Development baseline `58a28a3`; packaged correction `57e1c53`; qualification in the
  `codex/021-curve-workflows` history.
- **Before/problem:** manual obstacle enumeration could leave solves with no
  obstacles, and every solve rebuilt the same collision capture.
- **After/why:** default AUTO eligibility with optional exclusions and scene-membership
  revisions. Remove only automatic cyclic source-consumer edges; explicit cycles
  remain errors. Cache owned collision worlds by exact handles/transforms/clearance,
  bounded to 64 MiB/eight entries, with leases independent of cache eviction.
- **Evidence/outcome:** scene additions, moving obstacles, exclusions, cycles,
  undo and persistence pass. The 100-cube trial captured once (0.60 ms) over eight
  solves; solve means 72.34 ms versus 72.64 ms uncached establish reuse, **not a
  meaningful whole-solve speedup**. Capture and solve costs remain separately profiled.
- [Implementation/evidence](tasks/021-curve-workflows.md),
  [automatic routing lifecycle](../tests/test_automatic_routing_lifecycle.py),
  [cache tests](../tests/test_routing_scene_cache.py).
  Manual intent and the contact/warm safeguards from CH-004 remain supported.

### CH-006 — One clearance policy for route graph edges

- **2026-10-20; 0.2.2; Qualified.** C06, Q03.
  Baseline `248cc66`; qualified runtime `64fe0ef`.
- **Before/problem:** explicit routing of the user's two snapped points produced
  segments crossing the cube even though sampled points were not interior.
  Graph search bypassed the planner's rejection of a solid-interior chord between
  pins on the same owner; the later broad contact exemption could accept it.
- **After/why:** graph edges call the existing shared `clear` policy. The planner
  cannot introduce a chord disallowed by the same geometric contract.
- **Evidence/outcome:** bound/unbound actual pins at 32/64/128 samples, warm
  continuation and independent whole-segment checks pass. The corrected donor
  bound-box result passes where the original donor result failed; other donor/skull
  cases remain numerically identical. Preserve the intentional parity difference.
- **Rejected:** removing adjacent-edge expansion from `owner_span` caused conversion
  failure and changed four parity cases. Increasing budgets would not fix the bypass.
- [Evidence](tasks/snapped-solver-routing.md),
  [fixture/tests](../tests/test_snapped_routing.py).
  Raw geometry/captures are local under `build/snapped-solver-routing/`.
  The contemporaneous preview/accept UI was later replaced by
  [direct engine selection](tasks/direct-curve-engine.md); that does not change this solver fix.

### CH-007 — Correct Distributed inflation before smoothing

- **2026-10-20; 0.2.2; Qualified.** T03, T05.
  Baseline `dda3af4`; implementation `3a13625`; final packaged runtime `3b69cc9`;
  merged in `a93b514`.
- **Observed problem:** `muscle_test.anthroforge`, Distributed amount **1 m**,
  Height radius 0.2, strength 0.8, maximum change 0.05. The inflated surface already
  crossed itself before smoothing: 356 crossing pairs on the source grid; the old
  refined output had 1,456 proper crossings under independent exact-predicate checking.
  The addon produced bit-identical unsmoothed positions and the same smoothing error.
- **Before:** local normal displacements and a local stability height-reduction
  heuristic produced inconsistent directions and sharp height depressions on the bend.
- **After/why:** construct area-weighted normals on the physical material mesh;
  solve `(M + h²K) d = M n` with mass `M`, cotangent stiffness `K` and `h` equal to
  the authored inflation amount; normalize directions before applying unchanged
  amount/edge/taper settings. Remove the old local height reduction.
  This makes displacement directions coherent across the bend instead of reducing
  requested heights locally. It is a deliberate standalone algorithm change.
- **Preservation/difference:** authored settings, attachments and material identities
  remain; the legacy per-vertex displacement formula intentionally does not.
  Keeping that exact intersecting field and removing its intersections is impossible.
  This does not prove the user's parameter values themselves were impossible.
- **Evidence/outcome:** after this and CH-008–CH-010, the actual final
  4,816-vertex/9,350-triangle mesh has zero independently detected proper nonadjacent
  noncoplanar crossings. Actual packaged shape, undo/redo, edits and save/reopen were
  inspected. Regressions cover 0.02/0.1/1 m, planar height and rigid/scale equivariance.
  This is not a general injectivity guarantee or anatomical fitting; mesh validation
  remains necessary. The unchanged 1 m setting still makes a tall, steep envelope.
- [Full diagnosis/reproduction/qualification](tasks/muscle-height-smoothing.md),
  [compact fixture](../tests/fixtures/tissue/bent_membrane.json),
  [regressions](../tests/test_tissue_inflation_regression.py).
  Donor snapshots remain intact; [corrected snapshots](../tests/fixtures/tissue/distributed_correction.json)
  are labelled regression evidence, not addon parity.

### CH-008 — Refine existing material intervals without slivers

- **2026-10-20; 0.2.2; Qualified.** T01, T11.
  Baseline `dda3af4`; correction `3a13625`.
- **Before/problem:** overlaying a uniform grid on retained source lines produced a
  78×108 refined grid from the actual 56×86 source, including near-coincident lines.
  It amplified bad inflation and made the smoothing system poorly conditioned.
- **After/why:** subdivide each existing interval only when requested density requires
  it. Keep original lines and piecewise-bilinear source geometry; avoid nearly
  duplicate intersections between two independent sampling grids.
- **Evidence/outcome:** this fixture remains 56×86, with unchanged source geometry.
  Denser requested refinement, boundary pins, transforms and accepted-source reuse
  pass. Already saved 78×108 results are still supported; they are not silently
  rewritten on open. Their distinct numerical issue is addressed in CH-010.
- [Evidence](tasks/muscle-height-smoothing.md),
  [refinement/regression checks](../tests/test_tissue_inflation_regression.py).
  No sampling control or Manual-source semantics were removed.

### CH-009 — Validate actual geometry rather than normal rotation

- **2026-10-20; 0.2.2; Qualified.** Q02, T03, T11, T13.
  Baseline `dda3af4`; correction `3a13625`.
- **Before/problem:** smoothing rejected faces whose normals rotated over 90°.
  That was neither necessary nor sufficient for detecting an unusable deformation:
  a 0.1 m comparison accepted 36 new crossings, while later valid candidates could
  fail the normal test. A shared edge-intersection classifier also misclassified
  coincident Static PBD shell contact as a transverse crossing.
- **After/why:** validate the complete canonical mesh for new crossings/collapses.
  Intersection candidates must strictly straddle both triangle planes to count as
  transverse; touching shell boundaries are distinguished. Report large normal
  rotations as information instead of using them alone as rejection.
- **Evidence/outcome:** independent exact-predicate comparison confirmed the actual
  original folds. Shell pair 24/1127 had zero intersection length, confirming the
  false-positive contact. Genuine crossing, coincident contact, rotation, relaxation
  and actual tissue regressions pass with no tolerance/parameter reduction.
- **Limits:** this is discrete accepted-output validation, not continuous collision
  resolution, coplanar-overlap certification or anatomical approval. Pre-existing
  crossings are reported separately.
- [Diagnosis](tasks/muscle-height-smoothing.md),
  [quality tests](../tests/test_mesh_quality.py),
  [contact fixture](../tests/fixtures/tissue/boundary_contact.json).

### CH-010 — Independently certify iteration-limited height results

- **2026-10-20; 0.2.2; Qualified.** T11, R07.
  Baseline for this change `3a13625`; correction/runtime `3b69cc9`.
- **Before/problem:** settings-only edits legitimately reused the saved old 78×108
  base. At 0.02 m PIQP reached 250 iterations, and the migrated session rejected
  the result before checking whether it already met the application's requirements.
- **After/why:** for the maximum-iteration status only, run the existing independent
  KKT certificate at the unchanged `2e-7` tolerance. A certified candidate still
  goes through exact pin enforcement, certification again and geometry validation.
  Preserve `ITERATION_LIMIT` in the diagnostic ABI and show a warning; other solver
  failures are not reclassified.
- **Evidence/outcome:** actual retained-grid relative stationarity approximately
  `5.07e-9`, primal residual approximately `1.12e-26` before exact pins, relative
  complementarity approximately `8.17e-14`, and valid geometry. The packaged
  settings-only workflow succeeds without rebuilding the base or changing settings.
  The old 12-value ABI remains available; the new diagnostic ABI adds terminal status.
- **Rejected alternatives:** robust linear solving worsened convergence; variable
  normalization/fixed-variable elimination did not resolve this case; augmented
  curvature experiments were not qualified across the required amount range.
  None became production code.
- **Cost/limit:** the old grid can still take about 8.8 seconds. Recorded new-grid
  headless smoothing was 282.8–461.5 ms, inflation 32.9–35.6 ms and base preparation
  about 5.85 ms. These are fixture observations, not a controlled whole-app speedup.
- [Evidence](tasks/muscle-height-smoothing.md),
  [regression](../tests/test_tissue_inflation_regression.py),
  [diagnostic adapter](../src/anthroforge/native/tissue_smoothing.py).
  Combined CH-007–CH-010 qualification passed 1,325 tests, native/style/type checks,
  background GUI and portable checks. Raw Blender files, profiles and project copies
  are local under `build/muscle-height-smoothing/`; compact fixtures/tests are committed.

### Known limitation retained with the tissue correction

The original independent ordinary Curve `bc859526-c885-4d9b-abd9-a4b6b61d3d61`
still correctly rejects routing: its second fixed point is inside the cube,
0.08012986 m from the nearest surface, independent winding number 1. Isolating the
cube still fails; isolating the tissue succeeds. Its independently attached Fiber
and the tissue work. Moving that point or excluding the cube is a change of authored
intent, not a numerical tolerance fix. Neither was done. Keep this distinct from the
resolved inflation/smoothing defect when assessing the fixture.

### CH-011 — Outward surface snapping and consistent numeric editing

- **2026-10-20; 0.2.2; implementation under qualification.** Q01, C05, C06, R02, R06.
  Baseline `a816ee3`; candidate is this task branch (see linked task record).
- **Before/problem:** curve dragging and drawing independently applied signed normal
  offsets; negative offsets deliberately placed points inside. Ray calculations used
  doubles but narrowed barycentric coordinates and distance to `igl::Hit` floats.
  Number fields formatted/parsing with dot notation used a system-locale validator:
  the actual `uk_UA` configuration rejects `0.` and `0.25`; comma input passed the
  validator but failed JavaScript `Number`.
- **After/why:** keep ray hits double precision. A native placement helper uses the
  transformed face normal and nonnegative user offset plus two float epsilons times
  the maximum of one metre, coordinate magnitude and transformed bounds extent.
  Round displacement outward with `nextafter`. The small safety margin survives the
  curve adapters' float precision and remains below the routing contact floor.
  Curve edits, Place Points, surface drawing and cursor placement use this policy.
  Exact picking, retained bindings and measurements remain unshifted.
- **Numeric ownership:** one `UiNumberField` accepts dot or comma decimals without
  locale-dependent grouping, with separate integer policy and displayed-unit steps.
  A desktop `NumericEdits` adapter owns the existing begin/commit/cancel transaction.
  Scrubbing publishes ordinary shared operations live and commits one undo action;
  local tool drafts commit their value only on release.
- **Evidence so far:** 31 targeted native/history tests pass, including nonuniform
  and mirrored transforms, inside-camera hits, drawing, negative offset clamping,
  preserved measurement coordinates and complete clear routed segments between
  snapped opposite faces. Real QML keyboard/mouse checks pass decimal entry under
  Ukrainian/Romanian/English locales, integer dragging, undo and Escape cancellation.
  Full gate and portable evidence remain pending.
- **Preserved contracts and limits:** displayed geometry remains the snap source;
  explicit anatomical bindings are unchanged. Face winding defines the exterior,
  including on open meshes; this is not a mesh-normal repair or general inter-object
  collision solver. Ordinary curves do not acquire attachments by snapping. Existing
  deeply interior authored points are not rewritten. The routing solver still checks
  whole paths; outward endpoint placement alone is not proof of clear segments.
- [Task/evidence](tasks/outward-snap-numeric-fields.md),
  [native regression](../tests/test_surface_snapping.py),
  [numeric history](../tests/test_numeric_edits.py),
  [real input acceptance](../tools/numeric_input_acceptance.py).
  Design references: [Qt locale validation](https://doc.qt.io/qt-6/qml-qtquick-doublevalidator.html),
  [PBRT rounding error](https://pbr-book.org/4ed/Shapes/Managing_Rounding_Error).
