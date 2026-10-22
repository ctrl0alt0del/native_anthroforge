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

Additional active authoring/inspection work for T09, K01 and Q05 is recorded in CH-024/025.
Nearest attachment queries (A01–A03) exclude numerically unusable triangles from their
transient spatial index while preserving original material indices; see CH-032.

### Meshes, primitives and deformers

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| G01 | Mesh import: parse OBJ/STL/PLY, convert units/axes and construct owned canonical mesh data. | [mesh_io.cpp](../native/src/mesh_io.cpp) | [import formats](../tests/test_import_formats.py) |
| G02 | Mesh preparation: polygon triangulation, topology reuse, joins/deformed copies, bounds, normals, spatial acceleration and render chunks. Generated quads choose a non-overlapping initial diagonal. Geometry-only intermediates finalize once; deformation preserves compatible accepted connectivity. | [mesh_build.cpp](../native/src/mesh_build.cpp), [mesh_topology.cpp](../native/src/mesh_topology.cpp) | [geometry preparation](../tests/test_geometry_preparation.py) |
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
| C06 | Routed path solving: capture obstacles, classify contacts, plan corridors, retain required bends with adaptive sampling, validate warm starts, solve constrained SQP with collision/clearance checks and report termination. Open/cyclic paths share the engine. Geometry and correspondence use one prepared layout. Application preferences choose Custom or PIQP (CH-020). Optional bounded read-only path/contact snapshots use the same execution (CH-026), without changing accepted geometry. | [routing.cpp](../native/src/routing.cpp), [routing_planner.cpp](../native/src/routing_planner.cpp), [routing_handoff.cpp](../native/src/routing_handoff.cpp), [routing_trace.cpp](../native/src/routing_trace.cpp) | [routing parity](../tests/test_routing_parity.py), [surface pins](../tests/test_routing_surface_pins.py), [snapped routing](../tests/test_snapped_routing.py), [route diagnostics](../tests/test_route_inspection.py) |
| C07 | Explicit junction resolution: canonical shared-point identity, incident-curve updates, transforms and atomic propagation. Branched placement creates/reuses a junction in the new curve's single transaction (CH-015). Proximity alone never creates a junction. | [junction evaluation](../src/anthroforge/application/junction_evaluation.py), [junction edits](../src/anthroforge/application/junction_edits.py), [branch creation](../src/anthroforge/application/curve_branch_creation.py) | [junction workflow](../tests/test_junction_workflow.py), [fiber junctions](../tests/test_fiber_junctions.py), [branch creation](../tests/test_branch_creation.py) |

### Attachments and attached construction

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| A01 | SCP attachments: nearest/ray capture, retained surface/frame/offset records and batched parent-to-child transform propagation. | [attachment.cpp](../native/src/attachment.cpp), [attachment adapter](../src/anthroforge/native/attachments.py) | [addon parity](../tests/test_addon_parity.py), [assembly](../tests/test_assembly.py) |
| A02 | Anchor/point bindings: capture and resolve explicit SCP or Tissue Base/Final material locations, orientation and offsets. Resolve against accepted deformed material without automatic nearest reassignment. | [point attachment adapter](../src/anthroforge/native/point_attachments.py), [material_binding.cpp](../native/src/material_binding.cpp), [surface providers](../src/anthroforge/application/surface_providers.py) | [point attachments](../tests/test_point_attachments.py), [tissue anchor material](../tests/test_tissue_anchor_material.py) |
| A03 | Fiber attachment fields: dense surface captures, nearest-owner runs, arc-length blending between owners, structural pins and retained material influence. Automatic skeletal supports exclude unrelated tissues; explicitly tissue-backed fields use selected parents (CH-036). Applies across curve engines. | [attachment_weights.cpp](../native/src/attachment_weights.cpp), [attachment fields](../src/anthroforge/native/attachment_fields.py), [support policy](../src/anthroforge/application/fiber_supports.py) | [attachment weights](../tests/test_attachment_weights.py), [attachment fields](../tests/test_attachment_fields.py), [support policy](../tests/test_fiber_support_policy.py) |
| A04 | Fiber resolution/editing: resolve its current attached shape, edit authored controls, rebind edited endpoints using Current/Any eligible parent policy, preserve unedited pins, then evaluate its path engine. | [fiber bindings](../src/anthroforge/application/fiber_bindings.py), [fiber edit evaluation](../src/anthroforge/application/fiber_edit_evaluation.py), [path_editing.cpp](../native/src/path_editing.cpp) | [fiber editing](../tests/test_fiber_editing.py), [tissue fiber material](../tests/test_tissue_fiber_material.py) |
| A05 | Automatic attached construction: native nearest-SCP capture for new Anchor/Fiber bindings, independent graph copies, preserved existing Fiber bindings, and native Membrane evaluation under one reserved worker job. One atomic publication/undo; Tissue evaluation remains downstream. | [creation plan](../src/anthroforge/application/attached_creation.py), [worker assembly](../src/anthroforge/application/attached_creation_compute.py), [lifecycle](../src/anthroforge/application/attached_creation_jobs.py) | [conversion](../tests/test_attached_creation.py), [lifecycle](../tests/test_attached_creation_lifecycle.py) |

### Surfaces and membranes

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| S01 | Source correspondence: optional identity-qualified material stations preserve authored open loft correspondence (CH-031); align compatible closed paths initially, persist starting correspondence/direction, apply per-source sampling ranges and transforms; explicit Realign recalculates correspondence. | [surface_alignment.cpp](../native/src/surface_alignment.cpp), [surface_sampling.cpp](../native/src/surface_sampling.cpp) | [native surfaces](../tests/test_native_surfaces.py), [surface sources](../tests/test_surface_sources.py) |
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
| T04 | Section Profile: four station depths/peaks, native proportional depth scaling (CH-022), roundness, initialization and Local/Smooth/Section directions, restricted to ordinary open lofts. | [tissue_inflation.cpp](../native/src/tissue_inflation.cpp), [tissue_parameters.cpp](../native/src/tissue_parameters.cpp) | [tissue inflation](../tests/test_tissue_inflation.py), [profile scaling](../tests/test_tissue_profile_scaling.py) |
| T05 | Parts/sides and envelope assembly: per-part inflation, branch geodesic fields, seam displacements, Hermite connectors, reversal and independent two-sided composition. | [tissue_parts.cpp](../native/src/tissue_parts.cpp), [tissue_branch_connector.cpp](../native/src/tissue_branch_connector.cpp), [tissue_envelope.cpp](../native/src/tissue_envelope.cpp) | [tissue branches](../tests/test_tissue_branches.py), [envelopes](../tests/test_tissue_envelopes.py) |
| T06 | Anchor-based radial tissue: sphere/ellipsoid construction in the resolved source frame. | [tissue_radial.cpp](../native/src/tissue_radial.cpp) | [tissue shapes](../tests/test_tissue_shapes.py) |
| T07 | Fiber-based tissue: open/cyclic profile sweep, width/depth/power, resolution, taper, backing and cap construction. | [tissue_profile_sweep.cpp](../native/src/tissue_profile_sweep.cpp) | [tissue shapes](../tests/test_tissue_shapes.py) |
| T08 | Membrane normal shell: weighted normals, minimum/maximum thickness, power, backing and rims. Missing fields use boundary-distance defaults; explicit all-zero fields remain authoritative. | [tissue_normal_shell.cpp](../native/src/tissue_normal_shell.cpp), [tissue_shape_fields.cpp](../native/src/tissue_shape_fields.cpp) | [tissue shapes](../tests/test_tissue_shapes.py), [shape workflow](../tests/test_tissue_shape_workflow.py) |
| T09 | Fields and regions: material-domain masks, boundary/geodesic distances, custom values, feathering, region selection/outline geometry and source-domain signature validation. Native visible/through brushes use cached projection and material weights, with one authored commit; goal witnesses share constraint formulas (CH-024/026). | [tissue_masks.cpp](../native/src/tissue_masks.cpp), [tissue_regions.cpp](../native/src/tissue_regions.cpp), [painting.cpp](../native/src/painting.cpp), [inspection_goals.cpp](../native/src/inspection_goals.cpp) | [field editing](../tests/test_tissue_field_editing.py), [painting](../tests/test_tissue_painting.py), [constraint goals](../tests/test_constraint_goal_inspection.py) |
| T10 | Constraint goals: source/target-relative Fixed/Soft regions, material binding resolution, normal offsets, tethers, exact backing and conflicting-goal detection. Constraint enforcement remains active with relaxation None. | [tissue_constraints.cpp](../native/src/tissue_constraints.cpp), [material bindings](../src/anthroforge/native/material_bindings.py) | [target regions](../tests/test_tissue_target_regions.py), [tissue relaxation](../tests/test_tissue_relaxation.py) |
| T11 | Height smoothing: cotangent-biharmonic bounded height QP with PIQP, exact boundary/seam/zero-height pins, independent optimality checks and complete-mesh acceptance. Off bypasses the solve. | [smoothing_core.cpp](../native/src/smoothing_core.cpp), [tissue_smoothing.cpp](../native/src/tissue_smoothing.cpp) | [tissue smoothing](../tests/test_tissue_smoothing.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
| T12 | Geometric relaxation: source-specific static sag; radial tissue iterates gravity, neighbor smoothing and host-surface projection, while sweep/shell use their supported geometric displacement rules. | [tissue_geometric.cpp](../native/src/tissue_geometric.cpp), [tissue_point_relaxation.cpp](../native/src/tissue_point_relaxation.cpp) | [relaxation parity](../tests/test_tissue_relaxation_parity.py) |
| T13 | Static PBD relaxation: native iterative gravity, shape/volume retention where applicable, slack, constraints and convergence diagnostics. Reuses canonical triangles; not animation or generalized contact. | [tissue_static.cpp](../native/src/tissue_static.cpp), [tissue_relaxation.cpp](../native/src/tissue_relaxation.cpp) | [relaxation parity](../tests/test_tissue_relaxation_parity.py), [relaxation quality](../tests/test_tissue_relaxation_quality.py) |
| T14 | Material-domain crop: clip corresponding base/output and assemble crop topology while retaining material mappings. Crop edges do not become attachments or zero-inflation boundaries. | [tissue_crop.cpp](../native/src/tissue_crop.cpp), [tissue_crop_envelope.cpp](../native/src/tissue_crop_envelope.cpp) | [tissue crops](../tests/test_tissue_crops.py), [crop workflow](../tests/test_tissue_crop_workflow.py) |

### Stacking

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| K01 | Candidate/support planning: detect surface relationships/support regions with authored group and discovery allowance (CH-022), derive automatic order, apply explicit order/exclusions and retain provenance. Policy changes invalidate observed plans without rebuilding intrinsic geometry. Only accepted providers become final prerequisites. | [stacking.cpp](../native/src/stacking.cpp), [stack evaluation](../src/anthroforge/application/tissue_stack_evaluation.py) | [stacking phases](../tests/test_stacking_phases.py), [authoring controls](../tests/test_tissue_authoring_controls.py) |
| K02 | Vector stacking: material correspondence and direction transport, selected support regions, multiple providers and provider-first chains without redundant ancestor displacement. | [tissue_stacking.cpp](../native/src/tissue_stacking.cpp), [tissue_stack_directions.cpp](../native/src/tissue_stack_directions.cpp) | [native stacking](../tests/test_tissue_stacking_native.py), [mixed stacking](../tests/test_tissue_mixed_stacking.py) |
| K03 | Constrained stacking smoothing: sparse exact material-pin/backing equations, localized displacement smoothing and assembled side/group output. Whole-tissue groups retain the actual side dependency graph. | [tissue_stack_constraints.cpp](../native/src/tissue_stack_constraints.cpp), [material_pin_equations.cpp](../native/src/material_pin_equations.cpp), [stack groups](../src/anthroforge/application/tissue_group_tasks.py) | [stack material](../tests/test_tissue_stack_material.py), [stack groups](../tests/test_tissue_stack_groups.py) |
| K04 | Final stacking validation: inspect complete assembled output for folds, self-intersections and bone/neighbor conflicts. Failed stacking displays current intrinsic geometry but does not publish a successful Final prerequisite. | [stacking_surface_validation.cpp](../native/src/stacking_surface_validation.cpp), [tissue_stack_assembly.cpp](../native/src/tissue_stack_assembly.cpp) | [complete geometry](../tests/test_stacking_complete_geometry.py), [group lifecycle](../tests/test_tissue_group_lifecycle.py) |

### Spatial queries, measurements and images

| ID | Computation and current approach | Owning implementation | Validation entry point |
| --- | --- | --- | --- |
| Q01 | Interactive picking/snapping: double-precision ray/surface hits, native outward snap margins and nonnegative user offsets, cached component queries, path picking and displayed-revision agreement. Exact measurement hits are not offset. | [ray_queries.cpp](../native/src/ray_queries.cpp), [surface_snap.cpp](../native/src/surface_snap.cpp), [component_index.cpp](../native/src/component_index.cpp), [path_presentation.cpp](../native/src/path_presentation.cpp) | [surface snapping](../tests/test_surface_snapping.py), [component picking](../tests/test_component_picking.py), [surface picking](../tests/test_surface_picking.py), [held input](../tests/test_held_input.py) |
| Q02 | Confirmed placement: qualify topology, intersections, exterior exposure, orientation and original-face correspondence; retain qualified source geometry/BVH, otherwise build a transient Boolean exterior. Shared allocation-aware bounded cache; preview and material resolution remain separate (CH-021). | [qualification.cpp](../native/boolean/qualification.cpp), [surface_query_reuse.cpp](../native/src/surface_query_reuse.cpp) | [query reuse](../tests/test_surface_query_reuse.py), [exterior semantics](../tests/test_surface_query_modes.py) |
| Q02 | Tissue acceptance permits self-intersections; checks finite coordinates, canonical identity and new collapsed faces. Explicit diagnostics retain transverse-crossing counts and strict validation; large normal rotation is informational. Inflation/smoothing/relaxation use native tissue acceptance (CH-016). | [mesh_quality.cpp](../native/src/mesh_quality.cpp) | [mesh quality](../tests/test_mesh_quality.py), [intersection policy](../tests/test_tissue_intersection_policy.py), [inflation regression](../tests/test_tissue_inflation_regression.py) |
| Q03 | Advisory path collision: check accepted authored-engine Fiber centerline segments against eligible surfaces, with attachment-contact handling and incomplete-provider reporting. Does not silently reroute the curve. | [path_collisions.cpp](../native/src/path_collisions.cpp), [fiber collision Issues](../src/anthroforge/application/issues/fiber_collisions.py) | [path collisions](../tests/test_path_collisions.py), [fiber collision Issues](../tests/test_fiber_collision_issues.py) |
| Q04 | Measurements: resolve retained barycentric surface witnesses to world XYZ and compute straight-line distance. Camera framing/axis-view/restore calculations preserve gesture continuity. | [measurement.cpp](../native/src/measurement.cpp), [desktop view tools](../src/anthroforge/desktop) | [measurements](../tests/test_measurements.py), [view framing](../tests/test_view_framing.py), [view gestures](../tests/test_view_gestures.py) |
| Q05 | Read-only tissue stages, point/region explanation, advisory spatial checks, production stacking support polygons, and native triangle-plane sections. Material sampling produces displacement/field buffers. Cutaway picking skips hidden intersections while preserving original face identities. No repair or acceptance change (CH-023–026). | [inspection mapping](../native/src/inspection_mapping.cpp), [point inspection](../native/src/inspection_point.cpp), [stacking inspection](../native/src/stacking_inspection.cpp), [sections](../native/src/sections.cpp) | [inspection geometry](../tests/test_tissue_inspection_geometry.py), [stacking inspection](../tests/test_stacking_inspection.py), [sections](../tests/test_tissue_sections.py), [displayed revisions](../tests/test_tissue_inspection_view.py) |
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

- **2026-10-21; 0.2.2; implemented.** Q02,
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
  downstream changes, recorded in CH-017/018 below. The user approved a
  temporary base-backed closure for open tissue and an in-memory Boolean query mesh;
  the test's base and single-sided tissue each have 168 boundary edges. The original
  tissue and material bindings remain authoritative; added closure is not selectable.
  Skin handling remains deferred; no claim of downstream intersection immunity.
- [Regression fixture](../tests/fixtures/tissue/control_point_crossings.json),
  [tests](../tests/test_tissue_intersection_policy.py),
  [active task](tasks/tissue-intersection-policy.md). Raw local evidence is in
  `build/tissue-create-diagnosis/` and `build/tissue-intersection-policy/`.

### CH-017 — Transient exterior queries for confirmed placement

- **2026-10-21; 0.2.2; implemented.** Shared snapping/attachment
  boundary now distinguishes original-mesh preview from confirmed exterior queries.
- **Before:** nearest raw triangle could bind to a buried fold or sealed cavity.
- **After:** CGAL exact intersection arrangement through the pinned libigl adapter,
  followed by ambient-cell extraction, source-face filtering and per-face material
  mapping. Temporary closure uses the base belonging to the accepted final result,
  including Manual provenance. Added closure faces cannot be selected. Reversed
  exposed lobes survive; sealed cavities do not. Originals remain unchanged.
- **Ownership:** one native query service, bounded 64 MiB/64-entry owned cache tracked
  by existing profiler resource collection; attachments capture original triangle and
  barycentric coordinates. Resolution uses the original material surface. Confirmed
  curve edits run as coordinator jobs in the initiating undo step; expensive query
  preparation is never an interactive inline attachment recapture.
- **Evidence:** Windows native build and five query tests pass: nested sealed cavity,
  overlapping shells, open zero-volume sheet, actual compact crossed-tissue fixture,
  cancellation and cache leases. Three authored-placement tests pass for one-action
  undo/redo, cancelled gesture and unrelated later edits. Mypy and function limits
  pass. Subsequent interaction and release evidence appears below.
- **Limits:** exact remeshing observes cancellation between native stages, not within
  the CGAL call. This does not repair displayed geometry or establish safe skinning.
  Drawing/creation use the same confirmed query service, as detailed below.

### CH-018 — Geometric-normal support for ambiguous stacking

- **2026-10-21; 0.2.2; implemented.** The old inverse
  chart query selected minimum absolute distance along the provider's inflation
  field. Control Point inflation can point sideways, so changing that minimum to
  a maximum would not implement the confirmed geometric-normal rule.
- **After:** native area-weighted receiver base normals and the shared watertight
  ray/BVH query identify distinct positive provider hits. Multiple hits select the
  farthest support; coincident triangle-edge hits do not imply ambiguity. Ordinary
  single-hit vector transport, localized PIQP smoothing and exact constraints stay
  intact. Caches include base topology and new policy versions. Same-tissue crossing
  rejection is removed; other-tissue, bone, finite-coordinate and fold checks remain.
- **Evidence:** all 14 donor stacking cases and existing group/complete-geometry
  tests pass. A folded two-level provider chooses its outer roof at all nine receiver
  points, including a tangential inflation direction. Updated-provider/cache tests
  pass. Exact-constraint and inequality residuals remain below 2e-7 in this case.
  This fixture tests multi-valued support; it does not establish arbitrary physical
  contact or anatomical correctness. The actual folded-provider cross-section was
  inspected; complete release evidence appears below.
- **Provenance:** original donor hashes remain in `upstream_sources.json`; the
  maintained `sources.json` includes the three changed headers and new adapter.

CH-017 integration update: completed drawing/placed-point gestures and cursor surface
placement now use the shared confirmed query in coordinator workers. Raw preview stays
interactive. Per-sample native intent preserves unsnapped/plane samples. New snapped
edits supersede obsolete requests; undoing a later edit recovers the original pending
placement. Four authored-snap lifecycle and five creation/placement tests pass.

Final lifecycle qualification also covers target motion and ordinary transform-parent
motion during confirmation. The latter exposed double-applied movement when a saved
preview-world coordinate was reused after a parent update. Confirmed intent now carries
the selected anchor component identity; dispatch resolves its current world position
before applying the exterior correction. This preserves multiselection offsets and
does not add a second undo step. Both new regression cases and the production offscreen
curve-gesture suite pass. Full development gate at `010a948`: 1,439 tests; the subsequent
application-only corrections receive separate final full-suite/package qualification.

The portable mixed-tissue case exposed incorrect resource typing in the query adapter:
a CURVE material base is a retained path, not a missing mesh. Only SURFACE construction
supplies the accepted backing mesh for temporary closure. Radial/swept generated shells
remain queryable without that mesh. The save/reopen/conversion regression passes alongside
the sealed-cavity and original-material tests; no resource or geometry is substituted.

CH-016–018 final qualification: runtime `7438a62` passes the complete relocated Windows
portable suite with minimal PATH, including cavity-safe confirmed placement, mixed-tissue
conversion after reopening, retained material bindings, stacking and hidden rendering.
Final application/numerical suite: 1,442 passed; full native/development gate passed at
`010a948`, with unchanged native code afterward. Actual query/stacking shapes were inspected.
The user source file is unchanged. The native query is visible separately in the existing
profiler (about 0.693 seconds in one local run, not an input-latency measurement).
Bundled CGAL/Boost headers compile offline. See the [current validation record](development_status.md#tissue-queries-stacking-and-readable-controls-022)
for artifact identity, UI checks and evidence limits.

### CH-019 — Isolated PIQP routing-backend comparison; production unchanged

- **2026-10-21; C06; experiment, not adopted.** The user asked whether PIQP improves
  routing performance. The current native banded/active-set candidate solver was
  compared with sparse and dense PIQP 0.6.4, using identical quadratic objectives,
  linearized contacts and pins. Numerical assembly and iteration remain in C++.
- **Preserved:** original planner, exact pins, trust limiter, CCD, sampling,
  acceptance and final validation. Generated benchmark adapters live outside app
  imports. Neither production source nor project inputs were changed.
- **Evidence:** 22 input variants, 1,584 serial complete-route trials, matched inner
  subproblems, another tolerance block, baseline instrumentation-cost comparisons,
  existing runtime-profiler captures and inspected route overlays. Sparse PIQP is
  slower on small problems and most cold anatomical cases, but reduces the heavy
  256-sample attached warm route from 379.37 to 72.76 ms. Identical warm QPs take
  373.82 versus 53.78 ms, with tighter constraint residuals. Dense PIQP is slower.
  These local native-route timings do not establish UI latency or a backend policy.
- **Counterevidence:** one historical skull input fails independent clearance for
  every backend; its first fixed point is about 5.50e-8 inside the cranium. Using
  existing outward snap in a diagnostic copy makes every backend pass. Original
  inputs remain unchanged. The current bounded active-set loop can return unequal
  active/dual list sizes at its cap; such diagnostic stationarity is unavailable.
  This result-consistency risk is recorded, not repaired under a speed comparison.
- **Decision:** retain production routing. Sparse PIQP merits a separately qualified
  adaptive-backend experiment for heavy contact systems; no universal replacement
  or safe sample-count threshold is established. Full development gate: 1,442 tests
  and all three native tests pass. No new packaged backend is claimed.
- **Reproduction and limits:** [comparison record](tasks/routing-piqp-benchmark.md),
  [machine-readable evidence](tasks/routing-piqp-evidence.json),
  [isolated tools](../tools/routing_qp_benchmark/README.md).


### CH-020 — User-selectable ROUTED QP backend and consistent capped active sets

- **2026-10-21; C06; 0.2.3.** The CH-019 benchmark found workload-dependent sparse
  PIQP gains. The user requests an explicit application preference, retaining Custom
  as default and applying changes only to future calculations.
- **Old/new:** fixed Custom candidate solver becomes an owned per-job strategy.
  Sparse PIQP uses identical objective/pin/contact assembly, 1e-9 absolute/relative
  and duality-gap tolerances, max 250 inner iterations. Reuse setup only for matching
  dimensions/sparsity. Selection is captured at dispatch, including preview jobs;
  no ambient global state or silent fallback. Saved diagnostics and profile spans
  retain backend identity. Preferences do not modify projects or schedule work.
- **Required correction:** the Custom loop changed active membership after the last
  capped solve, then returned multipliers belonging to the preceding membership.
  CH-019 measured 34/94 mismatched calls in the heavy warm case. Stop before that final
  membership edit so candidate/active/dual agree; a native cap regression exercises
  this exact condition. This is a consistency fix, not a replacement objective.
- **Preserved:** planner, pins, trust limiting, CCD, outer acceptance, retained corners,
  material bindings, cancellation, result lifetime and failed-result retention. Earlier
  historical points slightly inside surfaces are not moved or excused by this change.
- **Evidence:** final development gate passes 1,498 tests and four native contracts,
  including both backends on 18 compact cold/warm fixtures, independent clearance/pins,
  concurrent invocation, dispatch capture, original ABI and failure retention. Material
  attachment workflows pass under both backends. Actual Preferences QML inspected
  offscreen; selection preserves results and explicit evaluation uses PIQP for Fibers.
- **Performance:** 528 serial production routes over 22 inputs show workload-dependent
  gains: heavy 256-sample warm Fiber medians 325.55 ms Custom / 61.51 ms PIQP; the actual
  24-sample cold fixture is 9.21 / 11.82 ms. Shapes inspected; 21/22 inputs clear for both.
  The known historical skull pin slightly inside Cranium remains unchanged. These are
  route timings, not UI latency or a universal PIQP advantage. CH-019 numbers describe
  its pinned original Custom implementation, before the consistency correction.
- **Qualification:** the canonical 0.2.3 executable passes the complete relocated
  portable suite, saved/profile provenance, Qt-free headless checks and offscreen UI /
  hidden-render acceptance. No interactive desktop acceptance is claimed. See
  [the task record](tasks/preferences-routing-023.md) and
  [release evidence](development_status.md#preferences-and-routed-backends-023).

### CH-021 — Qualify original geometry before confirmed-query cleanup

- **2026-10-21; Q02, G02; 0.2.3.** Every uncached confirmed query previously performed
  exact intersection remeshing, exterior classification and preparation of a new mesh.
  The user requests reuse when the original already satisfies every cleanup requirement.
- **Change:** native qualification checks unique/nondegenerate/manifold input, exact
  intersection predicates, exterior-connected cell exposure and selectable-face
  orientation. The query adapter verifies complete unchanged source correspondence,
  including temporary closure. Qualified queries retain the original allocation/BVH;
  unqualified inputs use the unchanged exact Boolean builder. No intersection-only
  shortcut, tissue mutation, Python geometry loop or new scheduler exists.
- **Preserved:** sealed-cavity exclusion, exposed reversed lobes, nonselectable temporary
  closure, original material bindings, preview behavior, safe cancellation and cached
  revision identity. Mesh/backing changes cannot reuse a previous qualification.
- **Accounting correction:** the old query cache called a draft-only size function on
  prepared meshes and recorded zero bytes. Scoped native accounting now includes full
  prepared storage and deduplicates aliases. Budget eviction releases only cache ownership;
  live query leases remain valid. The existing draft API contract is unchanged.
- **Evidence:** the full development gate passes 1,514 tests and five native contracts. Cases cover
  original allocation reuse, cavities without crossings, reversed orientation, duplicate
  seam vertices, temporary closure, changed geometry/backing, material bindings, byte
  eviction, oversized entries and cancellation. Six serial counterbalanced rounds over
  nine cases preserve every oriented triangle geometry hash against the previous runtime.
  Complete preparation improves 14.895 to 8.697 ms on the actual clean base and 6.014 to
  4.307 ms on radial tissue; small nested cavities add about 1.17 ms before cleanup.
  Dirty outputs still require cleanup; no general UI-latency improvement is claimed.
  Actual shapes inspected. The relocated packaged application passes clean/cavity
  placement, material capture, profiling, persistence and offscreen/hidden-render tests.
  [Release evidence](development_status.md#confirmed-query-reuse-023) records limits and
  [the task record](tasks/confirmed-query-reuse.md) links reproducible measurements.

### CH-022 — Expose tissue authoring policies and proportional profile scaling

- **2026-10-21; T04, T05, K01; 0.2.3.** The addon audit identified missing authoring controls:
  boundary attenuation power, automatic stack families/discovery allowance, full side
  copying and proportional station depths. Existing evaluators already support Boundary
  Power and stack family/allowance; no inflation or stacking objective is replaced.
- **Old/new:** unique families and hardcoded 0.5 discovery allowance become authored
  per-tissue policies passed into the existing native stack domain. Matching named groups
  suppress automatic pairs; explicit overrides remain eligible, matching the donor.
  Membership read signatures and candidate invalidation now include these policies so
  stale jobs cannot publish old plans. Intrinsic geometry remains reusable.
- **Profile:** a native batched parameter adapter scales four depths by a finite
  nonnegative factor, validating all outputs before writing. Desktop Overall depth sets
  the maximum using the same adapter; a frozen gesture baseline preserves proportions
  through zero and back. Peaks/roundness/direction remain unchanged. After committing an
  all-zero profile, a station edit/reset establishes proportions again.
- **Ownership:** side copying remains a shared validated application edit (entire
  inflation/smoothing record, current part/all current parts); source/connector identities
  and inactive historical settings remain untouched. Qt transport snapshots projections
  and converts return arrays without moving numerical work into UI/Python loops.
- **Evidence:** the full development gate passes 1,534 tests and all five native contracts.
  Actual offscreen inspector typing, drag, cancel, undo, copy and preview checks pass.
  Hidden geometry renders inspect proportional raised profiles, copied envelopes and
  grouped stacking; picking agrees. The source CLI batch round-trips new settings.
  The relocated runtime `2287808` passes the full portable suite, including the new authoring
  commands and saved settings. No interactive desktop acceptance or new performance gain
  is claimed. [The task record](tasks/tissue-authoring-controls.md) records reproduction.

### CH-023 — Inspect accepted tissue stages and spatial findings without changing evaluation

- **2026-10-21; Q05, supporting presentation/inspection; 0.2.3.** Stage geometry and
  material provenance already existed, but the desktop lacked stage comparison, clicked
  constraint explanation and locatable detailed geometry findings. This adds read-only
  presentation/diagnostics rather than a new inflation, repair or acceptance algorithm.
- **Approach:** native canonical/sparse material correspondence samples the selected
  reference at target vertices, transforms displacements into world metres, and prepares
  bounded colored render chunks. It does not fit nearest points, mutate sampling or alter
  topology. Incompatible accepted bases fail explicitly; reverse base matching is rejected
  because a base location can have multiple inflated sides. Statistics are vertex-weighted,
  not area/volume integrals. Native point queries sample source flags and the actual
  constrained-region core/feather functions; zero-height evidence uses accepted rest, not
  a relaxed or stacked position. Explanations are not a causal solver-force decomposition.
- **Geometry checks:** reuse qualified BVH/transverse predicates, with strict plane
  straddling to exclude contact. Degenerate faces use relative area tolerance `1e-12`;
  plane straddling uses 64 machine epsilons times coordinate scale. Shared-vertex self
  pairs, coplanar/touching cases, containment and penetration depth are outside this check.
  At 512 findings, scanning stops and reports truncation. Original topology and triangle
  IDs are retained. Self-intersections remain permitted under CH-016.
- **Execution/lifetime:** manual Issue jobs and read-only inspection jobs use existing
  dispatch capture, cancellation and stale publication rejection. Geometry changes mark
  detailed findings stale without rerunning them. Display buffers own their source meshes,
  stay outside project state, and switch with picking at frame boundaries. Profiler memory
  inventory includes these owners. Frozen report replay preserves the selected stage view.
- **Evidence:** real Control Point crossing fixture, cropped one/two-sided correspondence,
  exact backing/region weights, transformed crossings, cancellation, retained revisions,
  resource disposal and buffer-type replacement are exercised by dedicated tests. Actual
  hidden GPU captures were inspected for overlay, displacement, point markers and occluded
  face witnesses; that inspection found and corrected the framing-contract mismatch and
  added labeled x-ray guides. [Task evidence](tasks/tissue-inspection.md) records final gates,
  package qualification and limitations. No new physical-contact guarantee is claimed.
- **Idle projection:** profiler review found repeated native matrix preparation on unchanged
  inspection ticks. Desktop projection now refreshes only when the document, settings, jobs
  or Issues revision changes; an explicit 100-tick test verifies no repeated preparation.
  In the scripted recorded workload matrix calls fell from 862 to 244. This is removal of
  redundant preparation, not a claimed general frame-rate improvement.

### CH-024 — Explain stacking support and paint material fields through native queries

- **2026-10-21; T09, K01, Q05; 0.2.3.** Existing field point
  assignment and stacking configuration did not provide brush strokes or show evaluated
  support. Native support extraction now uses the production material masks, verifies the
  accepted plan and displays its intrinsic frame. Geometric ordering and active support
  are reported separately: excluded pairs can still have an ordering record.
- **Painting:** native screen projection and mesh BVH occlusion are cached by immutable
  geometry, transforms, field correspondence and camera. The cache is bounded to four
  entries/64 MiB, with existing profiler cache/ownership tracking. A stroke uses distance
  to the screen polyline, smoothstep/power falloff and maximum per-domain coverage against
  its starting weights. Event frequency therefore does not accumulate additional strength.
  Visible-only is the default; Paint Through bypasses occlusion. Base samples can influence
  multiple tissue sides; Rest samples retain their own material correspondence.
- **Ownership:** numerical work and colored buffers stay native. The existing read-only
  inspection scheduler captures/revalidates inputs. Preview does not mutate anatomy;
  releasing commits through the shared field command as one undo action. Interrupted or
  obsolete strokes cannot commit. Existing material lookup now exposes its interpolation
  coefficients to painting, retaining the same correspondence rules for attachments.
- **Evidence:** native visibility, external occlusion, event-rate independence,
  single-sample radial fields, Base/Rest commit/undo, cancellation, stale inputs and staged
  desktop colors pass focused tests. Existing material-binding/fiber tests also pass.
  Hidden GPU paint preview and frozen inspection export ran successfully; the generated
  color surface was visually inspected. QML stroke/undo/cancellation, profile and full-gate
  results are included in the qualification follow-up below.

### CH-025 — Section displayed geometry without changing topology

- **2026-10-21; Q01, Q05, supporting presentation; 0.2.3.** A world plane
  now cuts the selected tissue and compared stages, optionally surrounding geometry.
  Native triangle-plane queries produce bounded contour segments. Coplanar patches emit
  boundary edges without their internal triangulation. Reports count coplanar faces and
  flag truncation; no remesh, cap or replacement anatomical surface is generated.
- **Picking/rendering contract:** Qt CustomMaterial discards the hidden half-space;
  native BVH ray traversal rejects hidden candidates and continues to the next visible
  intersection. Returned triangle IDs and barycentric locations remain those of the
  original accepted mesh. Measurement and tissue-point inspection share this boundary.
  Ordinary queries use the existing unclipped path. Authoring geometry remains complete.
- **Execution:** plane movement updates presentation immediately and coalesces contour
  work in the shared inspection scheduler. Stale contours disappear until the current
  plane/revision is ready. Scoped masks are cached for repeated pointer queries. Stage
  comparison uses one world plane, not separately fitted per-stage planes.
- **Evidence:** transformed/coplanar/outside-plane native cases, picking the visible
  far surface, scope changes, comparison stages, read-only history and frozen report
  settings pass focused tests. Hidden GPU tissue-only and whole-scene cutaways were
  inspected. QML controls, camera persistence and frozen replay also pass. This is a geometric
  section view, not a boolean union or tissue repair.

### CH-026 — Optional route snapshots and material constraint-goal witnesses

- **2026-10-21; C06, A04, T09, Q05, R10; 0.2.3.** Ordinary
  routing previously exposed aggregate counters only. Explicit read-only diagnostic jobs
  now capture bounded world-space reference/planner/seed/trial/final paths and native contact
  witnesses from the same Custom/PIQP execution. Normal solves allocate no trace. Complete
  path records are omitted when budgets are exhausted; truncation is explicit. Cancellation
  remains cancellation, while a completed failed solve retains evidence with `success=false`.
- **Shared inputs:** Fiber attachment and junction resolution was extracted into the common
  curve input boundary, used by both ordinary evaluation and diagnostics. Preferences and
  geometry are captured at dispatch; current-read validation rejects superseded evidence.
  A diagnostic never adopts Fiber edit bindings, publishes path geometry or changes undo.
- **Goal witnesses:** native inspection reuses the production source-relative region-goal
  formula and retained target binding resolver, then interpolates through material identity.
  It reports world goals, displayed results and distances. Current target-relative goals
  are explicitly distinguished from historical accepted output; no force decomposition is
  implied. The formula and tissue constraint application are unchanged.
- **Evidence:** Custom/PIQP trace versus normal final coordinates/counters, moved
  Fiber bindings, failure retention, cancellation, capture limits, source offsets and Manual
  target/result divergence pass focused tests. Actual offscreen QML brush strokes, undo,
  Escape, section controls and route action passed. Hidden GPU/profile and complete-gate
  results are recorded below; packaged qualification is recorded with the delivery evidence.

### CH-024–026 qualification follow-up

- Actual offscreen QML and hidden D3D11 tests cover painting release/cancel/undo, stacking
  footprints/displacement, section scopes, routed contacts, failed planning and frozen replay.
  Routes around the cube and the retained failing-route output were inspected. Contact
  markers make near-zero-length contact witnesses visible without exaggerating their gaps.
- An 8,192-point footprint stalled QML activation because geometry crossed reference-sequence
  getters repeatedly. `ViewSnapshot` now copies geometry once per change; status maps contain
  metadata only. A regression walks all points and 100 unchanged reads without another Python
  snapshot call. Both recording-on/off hidden scenes now complete. This fixes presentation
  transport, not stacking mathematics. Footprints show clipped support polygons, not a merged
  outer silhouette; dense triangulation and output truncation are explicit limitations.
- Camera saves exposed overly broad document-revision invalidation. Inspection and brush
  signatures now compare immutable scene records while excluding workspace/camera metadata.
  Scene edits and changed backend preferences still invalidate affected evidence. Regression
  tests preserve live/frozen route steps and active paint across camera saves.
- Scripted profiler captures: native paint preparation 2.599 ms (one call), two strokes
  0.166/0.314 ms using the same preparation; section contours 0.164 ms; support footprint
  8.837 ms; successful cold route diagnosis 11.622 ms. These are inclusive instrumented wall
  durations on small fixtures. Hidden GPU readback runs do not emit real window presentation
  intervals, so no display-latency/FPS guarantee follows. Full gate and relocated executable
  results are recorded in the task/development validation documents.
- The dense 8,192-point support overlay's first Canvas paint took 53.076 ms in the recorded
  scene; copied snapshot activation peaked at 33.498 ms. This is bounded but can cause a
  visible hitch on dense support diagrams. No general frame-rate claim is made. Subsequent
  optimization should target overlay projection/transport, not the stacking solver.

### CH-027 — Editable target-driven Shrinkwrap (2026-10-21)

Previously the application supported only Hook and Lattice deformation; importing
the already wrapped scapula would lose its live rib relationship. The user rejected
that approach. The native nearest-surface adapter now consumes accepted target geometry
through explicit surface roles. Target pose and geometry are separate declared inputs;
existing revision guards, scheduling, undo, resource snapshots and failure retention
remain authoritative. Copies remap internal targets and retain external references.
Source formulas and provenance are in `native/migration/BLENDER_PRIMITIVES.md`.
Evidence: 24 Blender 5.0.1 weighted/transform/offset reference cases and focused
application lifecycle checks passed. Both scapulae now use the raw source plate and
live rib target in the delivered assembly. Their local deviations are documented below;
source and native shapes were inspected separately from API success.

### CH-028 — Segment construction and Boolean material identity (2026-10-21)

The previous body primitive could not express the approved node-group controls.
Segment Chain now constructs circular, capped segments natively from lengths, radii,
bends, spread and an AUTO radius profile. Adjacent-pair bending reproduces the source;
cumulative bending is explicit. Exact exterior union uses the existing CGAL adapter.
G10 is owned by `native/src/segment_chain.cpp`; `test_segment_chain.py` compares
Blender Index/Big_Toe raw output, including zero-length profile behavior.

Union triangle numbers change with parameters. New per-triangle provenance stores
original triangle identity and barycentric coordinates at each output corner,
avoiding ambiguous shared-vertex identity at seams. Attachment frames follow that
material location; a location newly covered by the union fails explicitly rather
than silently selecting another face. SCP bindings now retain their capture resource
alongside Fiber/Anchor bindings. Provenance survives deformation, refinement, shell
construction, saving and normal resource ownership. Numerical work remains native.
Evidence: changed-triangulation, child attachment, round-trip and deformation tests
pass; full checkpoint suite 1,635 passed. Full source migration comparison then
exposed reversed segment side winding relative to the caps, which made exterior
classification discard whole segments. Side winding now follows Blender's
Curve-to-Mesh topology. Directed-edge and positive-volume tests cover the defect;
all ten source final digit surfaces agree within approximately 2e-6 scene units.
Zero radius is permitted only for a disabled zero-length segment. Full-file visual
comparison, retained attachments, independent counterpart edits and undo now pass.

### CH-029 — Explicit subdivision and local displacement (2026-10-21)

The scapula requires Simple subdivision before Shrinkwrap and local-Z displacement
afterward. Baking either into the source would hide approved editable stages.
G11 uses native linear face/edge subdivision and weighted constant local displacement
in the ordered modifier stack, followed by existing thickness. Body bases can also
be refined before their BASE lattice. Topology edits use shared attachment locks;
estimates account for refinement growth. Compact Blender subdivision coordinates,
ordered stage persistence and topology locking pass. The migrated scapulae preserve
the stage sequence; their target differs intentionally at connected rib seams. Native
subdivision is qualified against Blender Simple for the migration's quad stages, not
higher-level nonplanar n-gons. Ilium instead fits its editable cage against captured
Blender pre-bend cap surfaces; earlier coarse/native-n-gon fits were rejected.
The migration also exposed an independent BODY closure error: fixed-length pieces
on closed guides inherited closed body topology. Only whole-guide fitted bodies
close now; a fixed-length piece retains its caps while its path distance can wrap.
The regression checks its spherical (rather than toroidal) mesh topology.


### CH-030 — Dependency-safe pose batches (2026-10-21)

Whole-document evaluation of the 59-SCP migration stalled with 52 queued jobs.
The output graph was acyclic, but a single pose batch waited for geometry whose
controls required a pose from that same batch. Attachment admission now partitions
outputs at intervening non-pose dependency stages, retaining batching of direct
pose chains. The coordinator still owns reservations, dispatch capture, cancellation
and publication; no dependency is ignored. Existing cycle failures remain explicit.
Regression coverage includes simple batch retention, pose/geometry chains and real
cycles. The migrated file now completes full evaluation, shared-hook edits,
independent opposite-side chain edits, undo and save/reopen. Maximum placement
change during binding establishment was 3.4e-7 scene units.

Generated Segment Chain vertex membership changes under its exact union and disabled
segments. Indexed/weighted final-geometry bindings are rejected at document validation;
whole-target deformers and Hook-weighted lattice cages remain available. Material
attachments continue using triangle provenance. This does not enable direct mesh editing.


Migration qualification for CH-027-030: all 59 entries (33 originals, 26 independent
counterparts) complete evaluation. Approved mesh imports and raw pre-deformation sources
are explicit; no rejected native construction falls back to a final mesh. The 20 native
digit chains agree with source surface samples within approximately 2e-6 scene units.
Ilium maximum/mean/p95 deviation is 0.01143/0.000394/0.002249 (source diagonal 4.77),
with the broad rim/underside retained. Rounded spine and connected rib seams are approved
construction differences. Ribs max/mean deviation is 0.12168/0.01210; live scapula target
response max/mean is 0.09459/0.01854. These are two-way vertex-to-surface measurements,
not continuous Hausdorff bounds. The comparison page contains original and opposite-side
front/side images. Startup attachment reevaluation changes geometry by less than 1e-12.

Separate ownership review: typed definitions and relationship policies remain in core;
commands share validation/transactions; native C++ owns geometry, union and material
queries; the existing coordinator owns execution and publication. Lazy worker mesh views
avoid constructing wrappers for unrelated assets per Shrinkwrap call. The desktop value
adapter recursively converts identity-free typed settings while retaining identity-bearing
incremental records; actual visible-field tests caught and fixed missing parameter values.
See the task and development validation records for final gate/package evidence and limits.


### CH-031 — Preserve authored open-loft material correspondence (2026-10-22)

- Affects S01/S02, tissue input preparation; defaults and inflation kernels unchanged.
- Evidence: four randomly selected canonical addon muscles were reconstructed with exact
  saved Free paths on the migrated skeleton. Reassigning correspondence by arclength
  increased mesh density and changed cross-sections. TFL inflation differed by 0.315
  scene units; merely preserving curve positions did not preserve its material loft.
- Change: optional per-source stations belong to SurfaceAlignment and reference stable
  authored point IDs. C++ maps evaluated path parameters to these retained stations,
  preserves evaluated corners and normalizes the accepted material domain. Duplication
  remaps identities, persistence retains definitions, missing points fail explicitly,
  and Realign deliberately resets correspondence. Existing surfaces remain unchanged.
- The one-off migration preserves donor transverse density and selects resolution 3,
  which adds no evaluated refinement to these already denser donor grids. No mesh
  substitute, Python numerical fallback or special-case muscle evaluator is used.
- Observed bilateral parity: FCR, sartorius, pronator teres and TFL inflation meshes
  match within 6.4e-7 scene units, with original vertex counts. Two-sided inflation and
  the material-domain crop are retained. External captures and comparisons are in the
  run linked by [task context](tasks/four-muscle-migration.md).
- Tests: native mapping/reversal, incompatible sampling, edit stability, copy, save,
  reopen, explicit Realign/undo and stale identities. The Windows development gate,
  final 1655-test suite, five native CTests and portable checks pass. The installed
  executable recalculates all 38 migrated construction/tissue targets and renders
  the saved project without a visible window. This is not interactive acceptance.
- Scope: explicit stations require complete open ordinary loft inputs and exact
  sampling. They do not silently apply to closed paths, ranges, or branched layouts.
  CH-033 subsequently extends explicit stations to complete open branched layouts.

### CH-032 — Query usable triangles without changing authored geometry (2026-10-22)

- Affects A01–A03 and shared nearest-surface consumers.
- Observed failure: remaining-muscle migration encountered Boolean exterior slivers
  with squared cross-product area 3.97168e-35. Nearest-point selection could return
  such a triangle, then barycentric capture rejected it. This depended on the target
  and queried point; rebuilding alone did not reliably resolve the failure.
- Before: Surface indexed every triangle and rejected the selected triangle later.
  Now: the transient world-space query index includes only triangles satisfying the
  existing 1e-30 squared-area resolution threshold and maps hits to original face IDs.
  Empty usable sets fail explicitly. No document mesh, topology, binding identity or
  Boolean exterior policy is changed.
- Barycentric coordinates use oriented cross products instead of subtracting nearly
  equal Gram products, avoiding cancellation for thin but resolvable triangles.
  Libigl nearest queries still determine the nearest position; this change does not
  claim exact interior projection for arbitrarily ill-conditioned triangles.
- Targeted evidence: 15 point/field/exterior-query tests pass, including sliver
  exclusion, original-index retention, offset resolution and an all-degenerate target.
  Five native CTests pass. Previously failing migrated scalenus/iliocostalis units
  now reproduce their saved source inflation within 2.3e-7 scene units.
- Ownership: filtering and numerical coordinates belong to the shared C++ spatial
  query; Python migration retains ordinary application capture and transactions.
  The final 1669-test gate and canonical portable suite pass; complete assembly
  qualification is recorded below under CH-036.

### CH-033 — Retain correspondence through branch evaluation (2026-10-22)

- Affects S01/S02 and branched tissue base preparation.
- Observed: the saved deltoid's explicit material stations were absent from the
  standalone branch adapter. Arclength reconstruction yielded 6646 vertices instead
  of 859 and a 0.7468 scene-unit maximum two-way vertex-to-surface discrepancy.
- The shared correspondence operation now accepts all curves of an open branch
  assembly with empty transverse-density overrides. The branch adapter forwards
  each consumer's retained alignment to the existing native path/branch pipeline.
  Native assembly, shared seam identity, connector and inflation algorithms stay unchanged.
- The one-off transfer additionally retains the source composite surface's normal
  direction; ignoring that authored setting inverted deltoid inflation. With both
  correct inputs the 859-vertex output matches within 2.63e-7 scene units.
- 26 correspondence/branch/native parity tests pass, including shared sections after
  deformation, exact seam counts, save/reopen/recompute, and invalid-density rejection.
  Branch addition cannot silently discard an existing ordinary-loft material mapping.
- Scope remains complete open curves with exact evaluated-corner preservation.
  The final 1669-test gate, canonical portable suite and complete assembled
  qualification pass (CH-036); this is not anatomical reapproval.

### CH-034 — Valid initial diagonals for generated quads (2026-10-22)

- Affects G02 and generated surface/tissue mesh preparation. The final migration
  audit added triangle-centroid samples to its two-way vertex-to-surface comparison.
  Matching vertices had hidden 15 incorrect deltoid quad splits (maximum surface
  discrepancy .0289393) and three biceps splits (.000588219). Smaller cases occurred
  in eleven other base/envelope pairs, including two previously migrated families.
- Before: every generated quad used diagonal 0–2, including concave/folded quads
  where those triangles overlap. Initial construction now uses Blender 5.0.1's
  `is_quad_flip_v3_first_third_fast` rule and switches such quads to diagonal 1–3.
  Source paths, hashes and attribution are recorded in the primitive provenance.
- Ownership stays in native mesh preparation. Polygon corners, authored vertices,
  material identities and inflation equations are unchanged. Deformation and
  finalization continue to reuse compatible accepted triangulation; they do not
  retessellate moving geometry. Existing files are not silently rewritten on load.
- A bounded donor-case experiment using that rule reduced deltoid/biceps sampled
  discrepancies to 2.63e-7/2.39e-7. A native regression checks concave coverage,
  picking outside the polygon and preserved connectivity after later deformation.
  The 39 focused geometry/correspondence/branch tests and native CTests pass.
- This migration regenerates its affected pre-delivery result caches through the
  normal coordinator, keeping authored definitions. Full assembly and package
  qualification with the repaired tessellation pass (CH-036).
- The first integrated audit then exposed a second ownership boundary: single-side
  inflation inherited its base's connectivity even before its own first publication.
  Intrinsic finalization now selects initial triangulation for the completed tissue
  surface after relaxation/crop; later results reuse compatible accepted topology.
  The native operation retains vertex/polygon material domains and refuses to discard
  incompatible retained triangle provenance. It does not change the deformation API.
  A regression reproduces the base-to-inflated concavity and checks first coverage,
  source immutability and later connectivity retention. Crop checks also pass.

### CH-035 — Stable Section Profile poles and material crop triangulation (2026-10-22)

- Affects tissue Section Profile directions, stacking direction queries, and material
  cropping. Final migration recomputation exposed round-off-sensitive collapsed poles:
  FCU base changes around 2e-14 changed inflation by .003; the radial FDS pole could
  reverse one entire row of normals and change its envelope by .0194 scene units.
- The qualified profile adapter now applies the existing scale-relative frame-area
  validity threshold before normalization and orientation propagation. Degenerate
  boundary frames contribute zero to smoothing/section averaging, as exact collapsed
  source coordinates did. Positive-height degenerate interior samples still fail.
  Inflation and stacking share the corrected direction function. Pinned addon source
  bytes remain unchanged; profile depths, shape formula and smoothing modes are retained.
- Display quad tessellation and material-domain triangulation are distinct policies.
  Native cropping previously reused display triangles. The adductor magnus base's
  changed display diagonal introduced a .00203 output discrepancy despite unchanged
  vertices. Cropping now ports the addon's dominant-plane projection, convex fans,
  concave ear clipping and nonplanar-quad fallback. Wholly excluded faces are skipped
  before triangulation; material interpolation and source-face identities remain.
- Recomputing the actual FCU, both FDS bellies and adductor magnus with these changes
  matches saved donor surfaces within 4.86e-7 scene units, using vertices and triangle
  centroids in both directions. Evidence: `roundoff-and-material-crop-experiment.json`
  in the all-muscle migration run. Synthetic collapsed-pole and nonplanar material
  quad regressions pass, alongside existing addon inflation/crop fixtures. Full
  assembly, lifecycle and packaged qualification pass (CH-036).

### CH-036 — Declared Fiber deformation supports (2026-10-22)

- Affects A03–A05. Full-assembly bone editing exposed three failed Fiber fields.
  Their explicit endpoint bindings were correct, but dense capture had silently
  used unrelated tissues already present in the document. Subsequent cropping of
  those tissues invalidated material locations absent from the Blender sources.
  Endpoint/crop tolerances were investigated and rejected as the cause.
- Previously creation and editing captured dense influences from all selectable
  anatomical surfaces. The shared application support policy now separates
  endpoint selection from dense deformation candidates. Skeletal fibers use SCP
  candidates; fibers explicitly attached to tissue use their selected parents,
  including an explicitly selected SCP. Any-parent endpoint selection still works.
- This restores the production addon's distinction in
  `core/vcp/fiber_node_attachment.py` and `core/vcp/attachment_surface.py`.
  Native field capture, blending, retained pins and material resolution are unchanged.
  Creation and current-shape editing use the same policy; no numerical Python loop
  or per-feature dependency exception is introduced.
- The migration recaptures 315 new Fiber fields against each donor's recorded
  support set. It preserves the original 139 objects, structural bindings, current
  paths and native capture algorithm. Source per-node weights are not copied
  verbatim. Existing user projects are not silently recaptured on load.
- Focused creation/editing tests pass, including nearby unrelated tissue, explicit
  tissue support, mixed explicit parents, and Any-parent rebinding. The production
  publication-frontier fixture now binds its tissue explicitly, retaining coverage
  of tissue-to-Fiber-to-Membrane dependencies without relying on implicit support.
- Combined acceptance for CH-032–036: **1669 tests**, five native CTests, style,
  typing, numerical-boundary audit, doctor and the canonical portable suite pass.
  All 96 authored units match donor surfaces within 9.56e-7 scene units, including
  bidirectional triangle-centroid checks. Three bone and five Fiber edits pass;
  undo is exact and normal reopen drifts at most 1.76e-12. The installed executable
  recalculates 518 objects with no failed jobs and again passes all source comparisons.
  Actual 96 source/app pairs and three installed viewport views were inspected.
- Evidence is frozen in `review.json`, `qualification.json`, and `checks/` under
  `E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-all-muscle-transfer-958f7969`.
  Original 139 authored objects and 74 source files remain preserved. Six generated
  bone face lists reorder without changing oriented triangles or vertices. Donor
  approval, construction proxies, and whole-body packing limits remain unchanged;
  offscreen evidence is not interactive desktop acceptance.

### CH-037 — Reuse validated snapshot relationships during publication (2026-10-22)

- Large-assembly opening spent about 141 of 149 seconds in result publication.
  Every pending/result change reconstructed relationships and revalidated the entire
  document; non-routed paths also enumerated every tissue surface unnecessarily.
- Snapshot indexes now reuse per-record links when definitions and the cross-record
  parent/type/junction context are unchanged. Registry maps still own current records;
  only validation and consumer relationships are reused for known evaluated fields.
  Unknown/new authored fields invalidate validation by default. Stack plans remain
  relationship inputs. Constructors continue validating every changed record.
- Manual routing discovers anatomical providers only when requested. Tissue pending
  states publish together, with no publication when already pending. Geometry pending
  publication likewise batches SCPs/surfaces and skips empty or unchanged sets. Algorithms,
  geometry tolerances, input revision checks and attachment capture remain unchanged.
- Initial evidence: 26 focused tests cover value/result edits, immutable old snapshots,
  parent frame walks, provider changes, invalid references and batched pending states.
  The first assembly trial fell from 148.95 s to 12.55 s before further scheduling work.
  Frozen baseline versus optimized replay is bit-for-bit equal across 11 snapshots of
  1,456 geometry/path/transform arrays (opening, three bone edits, two fiber edits, undo).
  Final packaged output also matches all 1,456 arrays exactly; see CH-038 for delivery.

### CH-038 — Exact pose provenance and renewable pending work (2026-10-22)

- Startup recomputation changed 55 bone matrices by at most 6.573e-14. These exact
  differences caused a large downstream wave despite no authoring edit. Accepted
  SCP poses now store evaluator version, exact parent pose/offset/geometry, child pose/offset and binding
  settings. Matching receipts retain the accepted pose; any changed input, recapture,
  failure or absent receipt follows normal native evaluation. There is no coordinate
  epsilon, binding reassignment or geometry-kernel change. Older schema-4 files with
  no receipt still perform their normal first startup evaluation.
- Previously repeated requests superseded uncaptured queued jobs, creating thousands
  of obsolete records. Fixed-output evaluators now explicitly declare renewable input
  contracts. Their pending requests share a job/deadline and refresh dependency indexes
  before admission. Once inputs are captured, cancellation/read checks are unchanged.
  Attachment recapture, payload-owning operations and final tissue jobs do not opt in.
  A changed stack plan may require a coupled evaluator with different reservations;
  ownership review found that renewing a single final job could bypass this selection.
  A failing queued-final regression established the loss of restart behavior; restoring
  its original static contract passes the regression and preserves group selection.
  Observation sets
  and dependency graphs form the contract cache key; no input values are cached.
- Focused tests cover exact reopen, tiny parent motion, undo, missing receipts,
  explicit recapture, changed geometry/settings, parent failure, pending input changes,
  refreshed relationship indexes, cancellation and output reservations. The assembly
  now has 34 obsolete rather than 2,968 obsolete requests, with 956 successes in both.
  Full fixture geometry/edit replay is exact (CH-037). Development gate passes with
  five native CTests; final Python checks pass 1,687 tests. Hidden GPU and offscreen
  UI opening/edit/undo/save checks and the canonical 0.2.3 portable suite pass.
- Final serial packaged trials: 17.423, 16.507 and 16.730 s without recording;
  recorder-on opening falls from 155.280 to 26.383 s. Recorded publication time falls
  from 136.672 to 5.485 s. Saved receipt reopen takes 7.842 s with no revision change.
  Profile timing events are retained; bounded resource-reference observations truncate
  in both captures. Background system load is recorded, not controlled. These are
  headless opening/settling trials and offscreen presentation checks, not interactive
  latency measurements. Original project bytes remain untouched. Evidence lives in
  `diagnostics/open-optimization-20261022/` under the CH-032–036 run directory above.

### CH-039 — Prepared tissue inspection presentation (2026-10-22)

- The viewport read a recursively converted full inspection report for every mesh's
  visibility binding. Repeated edits dispatched in 632–650 ms; repeated hidden
  viewport settling took 3.56–3.66 s in the 96-tissue assembly.
- Tissue inspection now owns a persistent PropertyProjection with per-field change
  notifications. Reports are prepared on state changes; property reads do no report
  conversion. Snapshot serialization remains explicit. Deselection clears rows.
- Ten targeted inspection/stacking/view tests pass, including repeated property reads
  and clearing selection. Serial off/on/on/off hidden viewport trials dispatch in
  46.7/57.9/55.1/47.8 ms and settle in 1.208/1.332/1.334/1.218 s. No QML warnings;
  actual captured geometry/selection remains visible. Native algorithms and bindings
  are unchanged. Frame intervals still reach 185 ms: this is not smooth-frame acceptance.
- Local evidence: `build/vcp-performance-024-release/step1/`, including two profiler
  captures, viewport images, trial load observations and timings. Full release checks
  remain pending; offscreen evidence is not interactive acceptance.

### CH-040 — Result metadata and recording-only resource observation (2026-10-22)

- Pending provenance now indexes the declared owner set once, retaining document order,
  all revision inputs and self exclusion. Known local TissueVCP strategy changes reuse
  validated relationships, but still run tissue capability validation against current
  sources. Other records, new fields, source/constraint/relationship changes invalidate
  reuse. Dataclass field discovery is bounded and cached by type.
- Profiler job capture records weak resource-catalogue groups instead of repeatedly
  expanding shared catalogues. Inventory expands live groups at observation boundaries;
  duplicate references no longer exhaust unique-resource limits. Group/job/native limits
  and real truncation remain explicit. No observation is added when recording is off.
- 26 metadata/publication/profiler/architecture tests pass; typing/style pass. Recorded
  ribs-edit resource observation falls from 2,110.9 to 34.7 ms across the same 1,230
  boundary calls, with zero losses versus 360 reference-limit losses. Recorded total
  falls from 7.497 to 4.654 s; three recorder-off trials take 4.234/4.324/4.208 s versus
  4.539/4.570/4.617 s. Single-profile settling remains about 1.02 s, dominated by
  advisory collision queries. Fiber results show no established improvement yet.
- Evidence: `build/vcp-performance-024-release/step2/`; baseline native geometry replay
  frozen in `baseline-replay/` before numerical changes (11 snapshots, 1,456 arrays each).
  Original fixtures remain untouched. Full combined release checks remain pending.

### CH-041 — Incremental native advisory collision evidence (2026-10-22)

- Each check previously copied all collider geometry, rebuilt BVHs/closure metadata,
  and tested every path/surface pair. A first pair-cache experiment exposed the next
  cost: the 71 MB collision scene exceeded the existing 64 MiB routing cache; two
  captures alone took 425 ms. Increasing that cache was not the implemented solution.
- The advisory checker now owns an exclusive native context. It transfers unchanged
  colliders into changed scenes, updates transforms/bounds exactly, and caches pair
  results by immutable path handle, complete frame/contact membership, surface handle,
  surface frame/index and the original global metric tolerance. Path bounds reject
  only provably disjoint surfaces. Numerical contact/collision kernels are unchanged.
- Only current rows/surfaces are retained; evidence metadata is capped at 32 MiB and
  complete retained context at 128 MiB. Jobs retain leases across cache eviction;
  failed/cancelled partial scene captures release ownership safely. Existing issue
  fingerprints, eligibility, unavailable surfaces and stale-publication guards remain.
- Native CTests and 30 focused collision/profiler/architecture checks pass, with an
  additional failed-capture recovery check. Warm reuse, miss-to-hit motion, changed
  contacts, reordered/removed surfaces, changed tolerance and cancellation match a
  fresh full query. Modified native files pass clang-tidy.
- On the assembly, recorded collision calls after a profile edit total about 26 ms
  versus the original 849 ms. Recorder-off profile settling is 221–324 ms versus
  1,023–1,043 ms. Broad ribs-edit end-to-end trials are noisy and slower in this run;
  no improvement is claimed there pending serial counterbalanced qualification.
  Local evidence: `build/vcp-performance-024-release/step3-retained/`. Full geometry
  replay and combined release checks remain pending.

### CH-042 — Exclusive retained stacking sessions and batched obstacle handles (2026-10-22)

- Planning/final jobs created and discarded numerical sessions, losing qualified native
  detection/material/solve caches. Sessions now use exclusive multi-call leases keyed
  by receiver. Concurrent leases never share mutable sessions; failures discard them,
  and cache clears invalidate outstanding returns. Group solving and support inspection
  keep leases until every native call is complete. Full inputs are still recaptured
  and qualified by the existing native signatures on every plan.
- Production planning requests only status/order metadata; the low-level full-result
  path remains available for numerical tests. Bone obstacles cross as mesh handles and
  frames, with transform/copy/preparation in C++; legacy array inputs remain a parity
  oracle. Geometry, settings, providers, constraints and final surface validation remain.
- Idle sessions are bounded to four and a conservative 512 MiB retained budget. Native
  accounting includes owned buffers and the configured allowance for the opaque donor
  vector cache. Profiler reports label this category as an upper bound, not exact RSS.
- 63 existing stacking/inspection/group/geometry checks pass, plus lease exclusivity,
  failed lease disposal, lifecycle clearing, metadata-only reads and transformed obstacle
  parity. Typing/style, native CTests and changed-native clang-tidy pass.
- Serial fresh/warm/warm/fresh 625-vertex fixture trials preserve every output vertex
  exactly. Planning: fresh 18.1–21.4 ms, warm 0.98–1.75 ms. Final: fresh 196.5–241.7 ms,
  warm 5.08–6.07 ms. These are unchanged-input reuse measurements, not claimed gains
  for changed providers. Prior changed-receiver evidence was smaller (CH-040 task analysis).
  Local timings/profile: `build/vcp-performance-024-release/step4/`. Combined release
  qualification and changed-input replay remain pending.

### CH-043 — Reduced height QP with native variable bounds (2026-10-22)

- The original height problem encoded fixed samples as equalities and free sample
  limits as identity inequality rows. A narrow native adapter now eliminates fixed
  variables, adjusts the linear term, and supplies PIQP's direct variable bounds.
  Expanded primal/dual results still pass the original full-problem certification;
  the objective, tolerances, pinning, displacement limits and cancellation stay intact.
- Serial old/new/new/old trials repeated twice in one process on the 13,845-vertex
  assembly base measured 1,768–1,819 ms original versus 1,561–1,601 ms reduced.
  Both used 24 iterations. Maximum vertex difference was 3.94e-13 m; topology was
  exact, stationarity remained ~6.3e-10 and constraint violation ~1.4e-16.
  System busy fractions ranged 17–23%; this is a kernel measurement, not UI latency.
- All 24 smoothing/workflow/architecture checks, five native CTests and modified
  native clang-tidy checks pass. Other inflation/relaxation fixture arrays are exact.
  Local evidence: `build/vcp-performance-024-release/height-comparison.json` and
  `kernel-baseline/`, `kernel-reduced/`. Solver state reuse was not needed for this
  gain; no claim is made for warm-start or symbolic caching in height smoothing.
- References: [PIQP variable bounds](https://predict-epfl.github.io/piqp/interfaces/python/getting_started).
