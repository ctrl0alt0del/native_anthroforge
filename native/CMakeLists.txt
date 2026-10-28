add_subdirectory(boolean)
add_subdirectory(blender)
include(skin_fit.cmake)
include(skin_kernels.cmake)
set(SKIN_DEFORMATION_SOURCES src/skin_deformation.cpp src/skin_deformation_api.cpp src/skin_deformation_samples.cpp src/skin_contact.cpp src/skin_support.cpp)
set(SKIN_STITCH_SOURCES src/skin_stitch_boundary.cpp src/skin_stitch_zipper.cpp src/skin_stitch_centered.cpp
    src/skin_stitch_weld.cpp src/skin_stitch_quality.cpp src/skin_stitch_transition.cpp src/skin_stitch_api.cpp
    src/skin_stitch_orientation.cpp src/skin_stitch_assembly.cpp src/skin_stitch_mirror.cpp)
set(SKIN_PROXY_SOURCES src/skin_proxy_api.cpp src/blender_mesh.cpp src/blender_edges.cpp
    src/blender_decimate.cpp src/blender_bisect.cpp src/blender_attributes.cpp src/blender_tasks.cpp)
set(SKIN_LOOP_SOURCES src/skin_loops.cpp src/skin_loops_projection.cpp src/skin_loops_closure.cpp src/skin_loops_pairing.cpp)
set(SKIN_ANNULUS_SOURCES src/skin_annuli.cpp src/skin_annuli_api.cpp src/skin_annuli_result.cpp
    src/skin_annuli_planar.cpp src/skin_annuli_radial.cpp src/skin_annuli_symmetry.cpp src/skin_ring.cpp src/skin_guide_cut.cpp
    vendor/scipy_lsap/rectangular_lsap.cpp)
set(SKIN_SOURCES src/skin_proximity.cpp src/skin_quads_split.cpp src/skin_quads_result.cpp src/skin_refine_candidates.cpp src/skin_refine.cpp src/skin_point_index.cpp src/skin_ownership_samples.cpp src/skin_ownership.cpp src/skin_ownership_islands.cpp src/skin_ownership_api.cpp src/skin_proxy_smooth.cpp src/skin_density.cpp src/skin_density_api.cpp src/skin_guides_merge.cpp src/skin_features.cpp src/skin_guides.cpp src/skin_guides_api.cpp src/skin_flow.cpp src/skin_grid.cpp src/skin_raster.cpp
    src/skin_exterior.cpp src/skin_collagen.cpp src/skin_fields.cpp src/skin_fields_api.cpp
    src/skin_meshing.cpp src/skin_assembly.cpp src/skin_capture.cpp src/skin_centerlines.cpp)
add_library(af_native SHARED src/api.cpp src/mesh_io.cpp src/mesh_build.cpp
    ${SKIN_DEFORMATION_SOURCES}
    ${SKIN_SOURCES} ${SKIN_PROXY_SOURCES} ${SKIN_LOOP_SOURCES} ${SKIN_ANNULUS_SOURCES} ${SKIN_STITCH_SOURCES} src/process_api.cpp src/process_windows.cpp src/process_log.cpp
    src/comparison_fingerprint.cpp
    src/inspection_mapping.cpp src/inspection_compare.cpp src/inspection_buffers.cpp src/inspection_point.cpp
    src/painting.cpp src/painting_mapping.cpp src/painting_projection.cpp src/painting_stroke.cpp
    src/sections.cpp
    src/inspection_goals.cpp
    src/surface_query.cpp src/surface_query_closure.cpp src/surface_query_reuse.cpp
    src/mesh_registry.cpp src/transforms.cpp src/spatial.cpp src/ray_queries.cpp src/surface_snap.cpp src/attachment.cpp src/material_domain.cpp src/material_axes.cpp
    src/construction_mesh.cpp src/curves.cpp src/loft.cpp src/curve_body.cpp src/segment_chain.cpp
    src/hooks.cpp src/lattices.cpp src/shrinkwrap.cpp src/simple_subdivision.cpp src/solidify.cpp src/component_queries.cpp src/curve_deform.cpp
    src/mesh_topology.cpp src/mesh_equivalence.cpp src/curve_frames.cpp src/curve_mapping.cpp src/component_index.cpp
    src/curve_queries.cpp src/influence.cpp src/control_geometry.cpp src/measurement.cpp
    src/path_registry.cpp src/path_presentation.cpp src/path_symmetry.cpp src/path_tube.cpp src/image.cpp src/image_placement.cpp
    src/curve_fit.cpp src/drawing.cpp src/placement.cpp src/attachment_weights.cpp src/path_editing.cpp
    src/routing.cpp src/routing_world.cpp src/routing_scene.cpp src/routing_reference.cpp src/routing_solve.cpp
    src/routing_planner.cpp src/routing_candidates.cpp src/routing_surface.cpp src/routing_handoff.cpp
    src/routing_piqp.cpp src/routing_qp_problem.cpp src/routing_trace.cpp
    src/routing_mesh_surface.cpp src/routing_shells.cpp src/routing_access.cpp src/routing_roadmap.cpp
    src/routing_random.cpp src/routing_pin_tree.cpp src/routing_pin_growth.cpp
    src/path_contacts.cpp src/path_collisions.cpp src/path_collision_cache.cpp src/routing_clearance.cpp src/sampling_allocation.cpp src/path_resampling.cpp
    src/routing_pin_graph.cpp src/routing_pin_recovery.cpp src/routing_search.cpp src/routing_warm.cpp
    src/curve_surface.cpp src/surface_inputs.cpp src/surface_sampling.cpp src/surface_alignment.cpp src/surface_correspondence.cpp
    src/surface_loft.cpp src/surface_symmetry.cpp src/surface_patch_projection.cpp src/surface_patch_triangulation.cpp
    src/surface_patch_subdivision.cpp src/surface_patch_fairing.cpp src/surface_patch_coordinates.cpp
    src/surface_branch_inputs.cpp src/surface_branch_sampling.cpp src/surface_branches.cpp
    src/tissue_inflation.cpp src/tissue_profile.cpp src/tissue_directions.cpp src/tissue_validation.cpp src/tissue_refinement.cpp src/tissue_branch_refinement.cpp
    src/tissue_preparation.cpp src/tissue_preparation_api.cpp
    src/tissue_prepared_fields.cpp src/tissue_branch_connections.cpp src/tissue_branch_connector.cpp src/tissue_parts.cpp src/tissue_envelope.cpp src/tissue_parameters.cpp src/tissue_crop_envelope.cpp src/tissue_crop.cpp src/tissue_crop_inputs.cpp src/tissue_smoothing.cpp src/smoothing_core.cpp src/height_box_solver.cpp
    src/tissue_crop_triangles.cpp src/tissue_crop_reference.cpp src/tissue_domain.cpp src/tissue_domain_api.cpp src/tissue_regions.cpp src/tissue_shapes_api.cpp
    src/tissue_shape_fields.cpp src/tissue_normal_shell.cpp src/tissue_profile_sweep.cpp src/tissue_radial.cpp
    src/tissue_masks.cpp src/tissue_source_normals.cpp src/tissue_constraints.cpp
    src/material_binding.cpp src/material_binding_index.cpp src/material_binding_query.cpp
    src/material_basis.cpp src/material_chart.cpp src/material_chart_query.cpp src/material_binding_frames.cpp
    src/material_cage.cpp src/material_mean_value.cpp src/triangle_material.cpp src/triangle_material_frames.cpp
    src/triangle_material_source.cpp src/triangle_material_exterior.cpp
    src/tissue_relaxation.cpp src/tissue_geometric.cpp src/tissue_static.cpp src/tissue_point_relaxation.cpp
    src/stacking.cpp src/stacking_normal_support.cpp src/tissue_stacking.cpp src/tissue_stack_material.cpp
    src/tissue_stack_directions.cpp src/tissue_stack_geometry.cpp src/tissue_stack_constraints.cpp
    src/tissue_stack_assembly.cpp src/material_pins.cpp src/material_pin_equations.cpp src/surface_material_pins.cpp)

target_sources(af_native PRIVATE src/expression_lexer.cpp src/expression_types.cpp
    src/expression_parser.cpp src/expression_values.cpp src/expression_evaluation.cpp src/expression_api.cpp
    src/shortcut_attachments.cpp src/parametric.cpp)
target_sources(af_native PRIVATE src/skin_symmetry.cpp src/skin_symmetry_cut.cpp)
target_sources(af_native PRIVATE src/skin_topology_quality.cpp)
target_sources(af_native PRIVATE src/process_shutdown.cpp)
target_sources(af_native PRIVATE src/blender_mesh_normals.cpp)
target_sources(af_native PRIVATE src/skin_fiber.cpp src/skin_bevel_frames.cpp src/skin_bevel_points.cpp)
target_sources(af_native PRIVATE src/fiber_deformation_api.cpp src/fiber_deformation_inputs.cpp
    src/fiber_deformation_reference.cpp src/fiber_deformation_weights.cpp src/fiber_deformation_filter.cpp
    src/fiber_deformation_fit.cpp src/fiber_deformation_solve.cpp)

add_library(af_curve_fit STATIC vendor/curve_fit_nd/intern/curve_fit_cubic.c
    vendor/curve_fit_nd/intern/curve_fit_cubic_refit.c
    vendor/curve_fit_nd/intern/curve_fit_corners_detect.c
    vendor/curve_fit_nd/intern/generic_heap.c)
set_target_properties(af_curve_fit PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_link_libraries(af_native PRIVATE af_curve_fit af_boolean af_bmesh af_skin_fit af_skin_kernels)
if(AF_OPENMP_RUNTIME)
    add_custom_command(TARGET af_native POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${AF_OPENMP_RUNTIME}" "$<TARGET_FILE_DIR:af_native>")
endif()
target_include_directories(af_native PUBLIC include)
target_include_directories(af_native PRIVATE migration/smoothing/include)
target_include_directories(af_native SYSTEM PRIVATE vendor)
target_include_directories(af_native SYSTEM PRIVATE vendor/bioimage-cpp/include)
target_compile_definitions(af_native PRIVATE NOMINMAX _USE_MATH_DEFINES EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)
target_compile_definitions(af_native PRIVATE AF_NATIVE_BUILD)
set_target_properties(af_native PROPERTIES CXX_VISIBILITY_PRESET hidden)
if(MSVC)
    target_compile_options(af_native PRIVATE /W4 /WX /fp:precise)
else()
    target_compile_options(af_native PRIVATE -Wall -Wextra -Werror)
endif()
if(BUILD_TESTING)
    include(skin_tests.cmake)
    add_executable(af_query_qualification_tests tests/surface_query_qualification_test.cpp)
    target_include_directories(af_query_qualification_tests SYSTEM PRIVATE vendor)
    target_link_libraries(af_query_qualification_tests PRIVATE af_boolean)
    add_test(NAME native_surface_qualification COMMAND af_query_qualification_tests)
    add_executable(af_routing_qp_tests tests/routing_qp_test.cpp)
    target_include_directories(af_routing_qp_tests PRIVATE src)
    target_compile_definitions(af_routing_qp_tests PRIVATE NOMINMAX)
    add_test(NAME native_routing_active_set COMMAND af_routing_qp_tests)
    add_executable(af_native_tests tests/api_test.cpp)
    target_link_libraries(af_native_tests PRIVATE af_native)
    add_test(NAME native_contract COMMAND af_native_tests)
    add_executable(af_routing_tests tests/routing_tree_test.cpp src/routing_random.cpp
        src/routing_pin_tree.cpp src/routing_pin_growth.cpp)
    target_include_directories(af_routing_tests PRIVATE src include)
    target_include_directories(af_routing_tests SYSTEM PRIVATE vendor)
    target_compile_definitions(af_routing_tests PRIVATE NOMINMAX)
    add_test(NAME native_routing_tree COMMAND af_routing_tests
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/fixtures/pin_tree.txt")
    add_executable(af_contact_tests tests/path_contacts_test.cpp src/path_contacts.cpp)
    target_include_directories(af_contact_tests PRIVATE src)
    add_test(NAME native_path_contacts COMMAND af_contact_tests)
endif()

