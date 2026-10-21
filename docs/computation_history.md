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
| C04 | Drawing/fitting: pointer-stroke depth, surface projection/fallback, offsets, image-plane drawing, corner detection and native cubic fitting. Branch placement can explicitly seed an existing control position (CH-015). A completed stroke authors one curve. | [drawing.cpp](../native/src/drawing.cpp), [curve_fit.cpp](../native/src/curve_fit.cpp), [drawing tasks](../src/anthroforge/application/drawing_tasks.py) | [drawing parity](../tests/test_drawing_parity.py), [strokes](../tests/test_strokes.py), [branch placement](../tests/test_branch_placement.py) |
| C05 | Curve editing math: closest location to the pointer, cubic subdivision/insertion, handle updates, selected-control transforms and current-path rebasing/deformation. | [curve_queries.cpp](../native/src/curve_queries.cpp), [path_editing.cpp](../native/src/path_editing.cpp) | [curve queries](../tests/test_curve_queries.py), [standalone editing](../tests/test_standalone_editing.py) |
| C06 | Routed path solving: capture obstacles, classify contacts, plan corridors, retain required bends with adaptive sampling, validate warm starts, solve constrained SQP with collision/clearance checks and report termination. Open/cyclic paths share the engine. Geometry and correspondence use one prepared layout. | [routing.cpp](../native/src/routing.cpp), [routing_planner.cpp](../native/src/routing_planner.cpp), [routing_handoff.cpp](../native/src/routing_handoff.cpp), [routing_solve.cpp](../native/src/routing_solve.cpp) | [routing parity](../tests/test_routing_parity.py), [surface pins](../tests/test_routing_surface_pins.py), [snapped routing](../tests/test_snapped_routing.py), [adaptive layout](../tests/test_routing_layout.py) |
| C07 | Explicit junction resolution: canonical shared-point identity, incident-curve updates, transforms and atomic propagation. Branched placement creates/reuses a junction in the new curve's single transaction (CH-015). Proximity alone never creates a junction. | [junction evaluation](../src/anthroforge/application/junction_evaluation.py), [junction edits](../src/anthroforge/application/junction_edits.py), [branch creation](../src/anthroforge/application/curve_branch_creation.py) | [junction workflow](../tests/test_junction_workflow.py), [fiber junctions](../tests/test_fiber_junctions.py), [branch creation](../tests/test_branch_creation.py) |

### Attachments and attached construction

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| A01 | SCP attachments: nearest/ray capture, retained surface/frame/offset records and batched parent-to-child transform propagation. | [attachment.cpp](../native/src/attachment.cpp), [attachment adapter](../src/anthroforge/native/attachments.py) | [addon parity](../tests/test_addon_parity.py), [assembly](../tests/test_assembly.py) |
| A02 | Anchor/point bindings: capture and resolve explicit SCP or Tissue Base/Final material locations, orientation and offsets. Resolve against accepted deformed material without automatic nearest reassignment. | [point attachment adapter](../src/anthroforge/native/point_attachments.py), [material_binding.cpp](../native/src/material_binding.cpp), [surface providers](../src/anthroforge/application/surface_providers.py) | [point attachments](../tests/test_point_attachments.py), [tissue anchor material](../tests/test_tissue_anchor_material.py) |
| A03 | Fiber attachment fields: dense surface captures, nearest-owner runs, arc-length blending between owners, structural pins and retained material influence. Applies across curve engines. | [attachment_weights.cpp](../native/src/attachment_weights.cpp), [attachment fields](../src/anthroforge/native/attachment_fields.py) | [attachment weights](../tests/test_attachment_weights.py), [attachment fields](../tests/test_attachment_fields.py) |
| A04 | Fiber resolution/editing: resolve its current attached shape, edit authored controls, rebind edited endpoints using Current/Any eligible parent policy, preserve unedited pins, then evaluate its path engine. | [fiber bindings](../src/anthroforge/application/fiber_bindings.py), [fiber edit evaluation](../src/anthroforge/application/fiber_edit_evaluation.py), [path_editing.cpp](../native/src/path_editing.cpp) | [fiber editing](../tests/test_fiber_editing.py), [tissue fiber material](../tests/test_tissue_fiber_material.py) |
| A05 | Automatic attached construction: native nearest-SCP capture for new Anchor/Fiber bindings, independent graph copies, preserved existing Fiber bindings, and native Membrane evaluation under one reserved worker job. One atomic publication/undo; Tissue evaluation remains downstream. | [creation plan](../src/anthroforge/application/attached_creation.py), [worker assembly](../src/anthroforge/application/attached_creation_compute.py), [lifecycle](../src/anthroforge/application/attached_creation_jobs.py) | [conversion](../tests/test_attached_creation.py), [lifecycle](../tests/test_attached_creation_lifecycle.py) |

### Surfaces and membranes

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| S01 | Source correspondence: align compatible closed paths initially, persist starting correspondence/direction, apply per-source sampling ranges and transforms; explicit Realign recalculates correspondence. | [surface_alignment.cpp](../native/src/surface_alignment.cpp), [surface_sampling.cpp](../native/src/surface_sampling.cpp) | [native surfaces](../tests/test_native_surfaces.py), [surface sources](../tests/test_surface_sources.py) |
| S02 | General lofts: preserve evaluated corners with normalized material axes, coalescing numerically coincident stations. Shared attachment frames use material charts across adaptive sample changes (CH-013). All-Fiber inputs produce a Membrane through the same evaluator. | [surface_loft.cpp](../native/src/surface_loft.cpp), [material_binding_frames.cpp](../native/src/material_binding_frames.cpp) | [surface workflow](../tests/test_surface_workflow.py), [adaptive material](../tests/test_adaptive_material_frames.py), [routed surface lifecycle](../tests/test_routed_surface_material.py) |
| S03 | Closed-curve patches: project and triangulate a boundary, subdivide, fair interior samples while retaining boundary constraints, and retain material correspondence. | [surface_patch_projection.cpp](../native/src/surface_patch_projection.cpp), [surface_patch_fairing.cpp](../native/src/surface_patch_fairing.cpp) | [native surfaces](../tests/test_native_surfaces.py) |
| S04 | Branched open lofts: infer semantic source groups from explicit junctions before unchanged native branch sampling, connector assembly and welded seams (CH-015). Ask for ambiguous groups; reject unsupported nested/closed branches and overlapping root intervals. | [grouping](../src/anthroforge/application/surface_grouping.py), [surface_branches.cpp](../native/src/surface_branches.cpp), [surface_branch_sampling.cpp](../native/src/surface_branch_sampling.cpp) | [native surface branches](../tests/test_native_surface_branches.py), [surface grouping](../tests/test_surface_grouping.py), [surface branches](../tests/test_surface_branches.py) |

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
| Q02 | Tissue acceptance permits self-intersections; checks finite coordinates, canonical identity and new collapsed faces. Explicit diagnostics retain transverse-crossing counts and strict validation; large normal rotation is informational. Inflation/smoothing/relaxation use native tissue acceptance (CH-016). | [mesh_quality.cpp](../native/src/mesh_quality.cpp) | [mesh quality](../tests/test_mesh_quality.py), [intersection policy](../tests/test_tissue_intersection_policy.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
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

Tissue crossing-rejection policy superseded by CH-016; the diagnostic classifier
and collapsed-face protection remain. Evidence below describes the historical policy.

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

- **2026-10-20; 0.2.2; Qualified.** Q01, C05, C06, R02, R06.
  Baseline `a816ee3`; correction/runtime `275ff9d`.
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
- **Evidence/outcome:** 31 targeted native/history tests pass, including nonuniform
  and mirrored transforms, inside-camera hits, drawing, negative offset clamping,
  preserved measurement coordinates and complete clear routed segments between
  snapped opposite faces. Real QML keyboard/mouse checks pass decimal entry under
  Ukrainian/Romanian/English locales, integer dragging, undo and Escape cancellation.
  Vector editing also exposed NumPy scalars crossing into Qt as nonnumeric variants:
  the model received the edit but displayed values became -1/empty. The shared Qt
  value adapter now converts NumPy scalars to built-in Python values. Real vector
  typing followed immediately by dragging and undo passes; property-projection
  tests exercise float32/float64 without replacing stable curve identities.
  All 1,344 tests, three native CTests, style/type/numerical checks, real offscreen
  gesture checks and minimal-PATH portable checks pass. A hidden GPU render of the
  saved snapped-endpoint fixture shows its route around the cube's exterior.
  Numeric checks also cover rollback on window deactivation and owner destruction.
  Offscreen input and texture rendering do not establish visible-window acceptance.
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

### CH-012 — Preserve route layout through solver preparation

- **2026-10-20; 0.2.2; Qualified.** C06, Q03.
  Baseline `9cc6c7c`; correction/runtime `3a03092`.
- **Before/problem:** `solver_fail1.anthroforge`, four surface pins on two cubes,
  failed at 24 samples. The planner's 24-point handoff passed collision checks, but
  a second uniform resampling changed per-span counts from 8/10/8 to 7/13/6, cutting
  corners and crossing both cubes. Independent segment checks identified crossings
  at segments 3 and 20. Increasing density hid the defect at 128 samples.
- **After/why:** prepare reference parameters and fixed-knot indices from the
  validated corridor allocation; pass its exact vertices into SQP. Remove the
  second resampling. The user's confirmed preference allows evaluated sampling to
  exceed the requested count when retaining required bends/knots needs more points.
  No authored preferences, points, clearance or iteration budget are rewritten.
- **Related continuation defect:** a zero distance threshold accepted zero-distance
  crossings in warm remaps. Handoff validation now uses the existing positive
  `max(1e-9, 1e-9 * world_length)` centerline tolerance and checks interval endpoint
  containment. Full clearance and recoverable warm feasibility remain distinct;
  invalid warm seeds use the existing cold replan.
- **Evidence/outcome:** exact original settings now solve; complete native segment
  checks pass. 41 routing/layout regressions pass, including all existing addon/skull
  parity cases, bound/unbound pins, cold/warm paths, closed-loop growth and the captured
  rejected seed. API undo/redo, roundtrip, consumer connectivity and topology locks pass.
  All 1,358 tests, three native CTests and the complete development gate pass.
  Real QML checks cover direct engine selection, undo/redo and a preference of four
  growing to 13 samples while retaining authored points. Minimal-PATH portable
  qualification passes; the executable opens, recalculates and saves the original
  case at 24 samples and the adaptive case at 13. Independent reopened-result checks
  confirm clear segments. Hidden GPU renders show the route around both cubes;
  the packaged capture has no warnings. No visible-window acceptance is claimed.
- **Preserved contracts/limits:** generated points remain solver variables, not new
  authored constraints. SCP consumers retain their own mesh density; exact standalone
  surfaces require the additional material work identified in CH-013. Native cancellation
  and the one-million-point bound remain enforced. This fixes sampling and validation;
  it does not establish complete pathfinding for arbitrary geometry or move interior pins.
- [Task/evidence](tasks/solver-fail1.md), [fixture](../tests/fixtures/routing/solver_fail1.json),
  [layout tests](../tests/test_routing_layout.py),
  [lifecycle tests](../tests/test_routing_layout_workflow.py).
  Design reference: [OMPL path interpolation](https://ompl.kavrakilab.org/classompl_1_1geometric_1_1PathGeometric.html)
  retains existing path vertices when adding samples. No new dependency was introduced.

### CH-013 — Exact corners with sampling-independent attachment correspondence

- **2026-10-20; implemented and qualified.** C06, S01–S04, A02–A04.
  Baseline `4be30b4`; comparison `18dfeba`; first implementation checkpoint `2868c05`.
- **Observed:** actual routed Fibers preserve bindings while growing 3 → 4 → 3.
  Exact loft station unions change mesh connectivity; downstream Tissue Base attachment
  resolution rejects old indices. Near-coincident station duplicates also cause degenerate
  tissue frames. The previous BODY-consumer check did not establish exact-surface safety.
- **Compared:** exact-corner geometry with a stable normalized material-coordinate probe,
  versus fixed consumer sampling on identical accepted paths. Numerical preparation is an
  isolated C++ experiment. After the requested visual comparison, the user approved exact corners.
- **Evidence:** exact probe preserves corners and has clear boundary segments. Fixed 32
  matches current uniform surface geometry but deviates 5.984 mm at the bend and crosses
  the cube on both boundaries. Fixed 8 deviates 24.707 mm and also crosses. These are corner
  deviations, not penetration depths. Real uniform-surface Base/Final bindings survive
  motion, undo/redo and reopening.
- **Production change:** preserve normalized arc-length grid axes and merge stations within
  `1e-12` of normalized length. Store source material coordinates on accepted tissue meshes;
  interpolation through crops/envelopes retains source/side provenance. Shared native frame
  resolution maps the captured material location to the current triangle and transports its
  tangent, normal and offset. It never nearest-recaptures or rewrites the saved binding.
  Anchors, dense Fiber fields and target-relative tissue constraints use the same service.
  Unchanged parameter domains retain the existing canonical correspondence implementation.
- **Rejected patch attempt (`9427d13`):** harmonic disk coordinates plus radial boundary
  transport passed finiteness checks but moved an attachment by 0.1173 m when a collinear
  boundary sample was inserted into an unchanged one-metre square. Interior coordinates
  depended on triangulation. Finiteness was insufficient evidence; that approach is removed.
- **Patch replacement:** store projected material positions and normalized boundary arclength.
  Signed mean-value coordinates transport positions using the union of both boundaries'
  stations, including new corners. Linear precision preserves unchanged planar geometry
  despite remeshing. Interior derivatives are analytic; exact edge interpolation uses
  symmetric derivative limits with a `1e-5` normalized-coordinate step. Current material
  triangles supply the actual 3D frame. Boundary queries select compatible material planes
  so a rim attachment cannot resolve onto a sheet face solely because they share an edge.
  All work remains native, cancellable and bounded. Metadata owns no live source handles.
- **Intentional donor difference:** two curved branch fixtures contain two duplicate vertices
  and zero-width strips from floating-point station unions. Tests retain the original donor
  data and compare against its canonical removal of those duplicates; other geometry/seam
  expectations remain exact. See [donor canonicalization](../tests/surface_donor_canonical.py).
- **Evidence so far:** real routed Fibers, exact Membranes, Tissue Base/Final Anchors and
  downstream Fibers survive growth/shrink, undo/redo and reopening with unchanged bindings.
  Native checks cover frames/offsets under nonuniform transforms, closed seams, branches and
  adaptive patches. Additional regression checks explicitly compare every captured position
  and frame across square/concave-patch resampling, resolutions 2/4/7, corners/edges, shell
  rims, rigid motion, scale and metadata restoration. Hidden GPU captures show the surface retaining both obstacle
  bends and returning to its original shape. Runtime `c30211d` passes the full gate: 1,378 tests,
  three CTests and native/Python style/type/numerical checks. Additional targeted tests verify
  target-relative goals and disposal of source handles while coordinate metadata remains
  owned. Unchanged-patch position drift measures at most `4.58e-16` m in the local view.
  A complete profile records 30 material-frame calls averaging 0.409 ms (max 2.099 ms),
  with no lost events or unattributed geometry bytes. This is a small profiled workload,
  not a general responsiveness benchmark. The canonical Windows package passes the complete
  minimal-PATH suite and exact-surface grow/shrink/save/reopen checks with unchanged captures.
  Its hidden GPU renders were inspected. Visible-window/manual editing is not claimed.
- **Preserved limits:** this does not guarantee collision-free interiors of arbitrary lofts.
  Authored topology locks, unsupported domains and cropped-away material remain explicit
  failures. Indexed custom tissue weight fields/selected face masks retain their existing
  topology qualification; they are not automatically resampled by this attachment repair.
  Old captures lacking source material metadata are not guessed from unrelated current meshes.
- [Task and measurements](tasks/routed-fiber-surface-stability.md),
  [reproducible experiment](../tools/experiments/routed_sampling/README.md).
  Design references: [libigl parameterization](https://libigl.github.io/libigl/tutorial/),
  [CGAL mean-value coordinate properties](https://doc.cgal.org/latest/Barycentric_coordinates_2/index.html).
  No new dependency is introduced; the vendored libigl MVC routine is explicitly marked
  broken upstream and is not used.

### CH-014 — Atomic automatic attached construction

- **Inventory:** A02–A05, C07, S01–S04; application orchestration and scheduling.
- **Observed limitation:** Create Tissue required attached construction or opened a
  source modal. There was no complete Surface-to-Membrane operation; issuing independent
  curve conversion commands would create multiple undo steps and partial graphs on failure.
- **Before:** separate explicit Anchor/Fiber captures and Surface creation; only Fiber
  creation had the automatic nearest-SCP default. Baseline `6f72018`.
- **Replacement:** one shared plan copies the required graph, remaps internal sharing once,
  captures new anatomical bindings natively, copies existing Fiber binding intent, and
  evaluates the Membrane using its retained correspondence. One coordinator job reserves
  every new output, captures dispatch-time data, validates reads, and publishes all records
  and owned resources into the initiating history action. Tissue jobs are registered before
  creation is terminal. Input changes replan safely; old histories replay their own captures.
  `anchor.create` also supports the shared nearest-SCP default.
- **Preserved:** original shapes, ordering, per-consumer transforms, canonical sampling,
  internal junction sharing, existing external bindings, cancellation, workspace association,
  one-action undo and complete saves. Numerical algorithms/clearance/collision rules are
  unchanged. No Python numerical fallback or second scheduler is introduced.
- **Evidence:** automatic Point/Curve/Surface workflows, mixed Fiber/Curve surfaces,
  branched seams, retained shape and bindings, bone-following, independence, undo/redo,
  injected capture failure, running cancellation, superseding edits and schema-4 roundtrip
  checks pass. Offscreen direct actions select the primary new object and exit editing.
  The hidden Direct3D render of the automatically converted arch was inspected; no visible
  window or physical input-latency acceptance is claimed. Full final qualification is
  recorded in the [task record](tasks/direct-tissue-stable-inspectors.md). Final runtime
  `be7e506` passes 1,397 tests and relocated portable checks. The complete native/development
  gate passed before the final explicit-role input-validation guard; final Python lint,
  typing and regression checks include that guard.
- **Intentional behavior/limits:** generic sources become independent attached copies.
  New implicit bindings choose ready SCP geometry, not Tissue Base/Final; explicit binding
  operations remain available for other targets. Missing supports fail without partial
  creation. Tissue inflation can still report its normal capability/geometry errors after
  successful attached-source creation. No general performance improvement is claimed.


### CH-015 — Direct branched placement and surface grouping

- **Date / affected IDs:** 2026-10-20; C04, C05, C07, S04.
- **Observed gap / baseline:** `99737ca` supports explicit junction editing and native
  branched surfaces, but placement cannot start at an existing control with a junction.
  Surface creation needs manual branch assignment even when connections determine it.
- **Previous approach:** create independent curves, join points through inspector selectors,
  create a main loft, then add each branch. Regular component picking selects a near-ray
  hit within a radius, which is different from the requested nearest projected control.
- **Replacement / ownership:** native projected-distance selection over cached displayed
  authored coordinates; explicit native first-sample seeding; one shared application
  operation authors the new curve and junction. The source remains canonical and existing
  junctions are reused. The common surface operation infers semantic groups from explicit
  point identities, with a read-only draft for multiple valid groupings. Partitions are
  generated lazily. Up to six branch curves use exhaustive parent
  assignments; larger graphs use exact identity matching and a minimum-two-roots check.
  With more than six children on two outer boundaries, any valid allocation proves at
  least two group partitions. Invalid graphs return reasons, not a grouping prompt.
  Numerical projection remains C++, graph policy remains Python.
- **Preserved contracts:** source geometry and bindings, point identities, workspace
  editability, subsequent placement/snapping controls, one-action undo, cancellation,
  ordinary scheduling and Manual prerequisites, surface sampling/material correspondence,
  native assembly and all-Fiber Membrane substitution. No proximity-based automatic welding.
- **Evidence:** 33 focused creation, placement, grouping, conversion and architecture checks
  pass. Actual offscreen QML right-click/menu, root preview, Shift continuation, completion,
  undo and explicit ambiguous grouping pass. Hidden Direct3D surface and converted Membrane
  images were inspected: continuous T-shaped branch seam and unchanged shape; vertices
  match the existing branch fixture and conversion result within 1e-10 / 1e-12 respectively.
  A 102-curve selection resolves ambiguity without enumerating all partitions. A cached
  10,000-control projection microcheck over 500 queries measured median 0.0271 ms and
  p95 0.039605 ms while native-style checks were running. This includes the Python/native
  call boundary, excludes index preparation and whole input/frame costs, and is not an
  application responsiveness guarantee. Local artifacts live under
  `build/branched-point-placement/`; qualification status is in the
  [task record](tasks/branched-point-placement.md). Final runtime `1490635` passes 1,417
  tests and the relocated portable suite, including branched creation and conversion.
  The full development/native gate passed before the final application-only matching
  correction; final Python, offscreen interaction and hidden GPU checks include it.
- **Rejected during qualification:** a 256-assignment search cap could misclassify an
  exhausted search as ambiguity and suggest duplicate roots. A 30-curve cross-connected
  regression exposed both a missed valid grouping and an invalid graph that prompted.
  Exact unweighted identity matching replaces that cap; 120 small graph cases agree with
  exhaustive assignment feasibility. This is application relationship policy, not numerical
  geometry/optimization, and changes no native evaluator.
- **Limits:** the projected query is a native linear scan of cached controls, not a new
  mesh-query accelerator. Existing open, outer-boundary, nonnested branch constraints
  remain. Generic branches are ordinary curves; attached conversion remains explicit or
  part of Create Tissue. No physical desktop-input or visible-window acceptance is claimed.

### CH-016 — Permit tissue self-intersections without repairing inflation

- **2026-10-21; 0.2.2; Implemented, integration qualification pending.** Q02,
  T03, T11 and T13. Baseline `6918888`; work on `codex/tissue-intersection-policy`.
- **Before/problem:** `tissue_create.anthroforge` at Control Point amount 0.599,
  depth zero, fails before smoothing with 106 newly detected crossings and no collapsed
  faces. The user explicitly accepts these intersections and wants the existing
  inflation/smoothing mathematics retained. This is a product-policy change, not a
  claim that the crossed surface has been repaired.
- **After/why:** the shared native tissue acceptance function checks canonical
  connectivity, finite coordinates and new collapsed faces. Crossing counts remain
  available through the explicit diagnostic API but do not reject inflation,
  smoothing or relaxation. Relaxation invokes this policy in native evaluation so
  headless/direct callers and the application agree. No field, solver, tolerance,
  control-point radius, direction, topology or smoothing constraints change.
- **Evidence:** 29 targeted tests pass, including unchanged addon inflation witnesses,
  smoothing bounds/fixed vertices, crossed Pouch relaxation with exact backing,
  previous valid inflation regressions, cancellation and strict diagnostic checks.
  In-memory evaluation of the unchanged user project at 0.2 then 0.599 now publishes
  ready base/rest/intrinsic/final outputs. No project file was overwritten.
  Full suite at `e922aeb`: 1,421 tests pass; Mypy, focused Ruff and changed-native
  clang-tidy checks pass.
- **Limits:** attachment Boolean cleanup and ambiguous stacking queries are separate
  downstream work, not completed by this acceptance change. The user approved a
  temporary base-backed closure for open tissue and an in-memory Boolean query mesh;
  the test's base and single-sided tissue each have 168 boundary edges. The original
  tissue and material bindings remain authoritative; added closure is not selectable.
  Skin handling remains deferred; no claim of downstream intersection immunity.
- [Regression fixture](../tests/fixtures/tissue/control_point_crossings.json),
  [tests](../tests/test_tissue_intersection_policy.py),
  [active task](tasks/tissue-intersection-policy.md). Raw local evidence is in
  `build/tissue-create-diagnosis/` and `build/tissue-intersection-policy/`.
