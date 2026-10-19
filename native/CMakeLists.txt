add_library(af_native SHARED src/api.cpp src/mesh_io.cpp src/mesh_build.cpp
    src/mesh_registry.cpp src/transforms.cpp src/spatial.cpp src/ray_queries.cpp src/attachment.cpp src/material_domain.cpp src/material_axes.cpp
    src/construction_mesh.cpp src/curves.cpp src/loft.cpp src/curve_body.cpp
    src/hooks.cpp src/lattices.cpp src/solidify.cpp src/component_queries.cpp src/curve_deform.cpp
    src/mesh_topology.cpp src/curve_frames.cpp src/curve_mapping.cpp src/component_index.cpp
    src/curve_queries.cpp src/influence.cpp src/control_geometry.cpp src/measurement.cpp
    src/path_registry.cpp src/path_presentation.cpp src/image.cpp src/image_placement.cpp
    src/curve_fit.cpp src/drawing.cpp src/attachment_weights.cpp src/path_editing.cpp
    src/routing.cpp src/routing_world.cpp src/routing_scene.cpp src/routing_reference.cpp src/routing_solve.cpp
    src/routing_planner.cpp src/routing_candidates.cpp src/routing_surface.cpp src/routing_handoff.cpp
    src/routing_mesh_surface.cpp src/routing_shells.cpp src/routing_access.cpp src/routing_roadmap.cpp
    src/routing_random.cpp src/routing_pin_tree.cpp src/routing_pin_growth.cpp
    src/path_contacts.cpp src/path_collisions.cpp src/routing_clearance.cpp src/sampling_allocation.cpp src/path_resampling.cpp
    src/routing_pin_graph.cpp src/routing_pin_recovery.cpp src/routing_search.cpp src/routing_warm.cpp
    src/curve_surface.cpp src/surface_inputs.cpp src/surface_sampling.cpp src/surface_alignment.cpp
    src/surface_loft.cpp src/surface_patch_projection.cpp src/surface_patch_triangulation.cpp
    src/surface_patch_subdivision.cpp src/surface_patch_fairing.cpp
    src/surface_branch_inputs.cpp src/surface_branch_sampling.cpp src/surface_branches.cpp
    src/tissue_inflation.cpp src/tissue_validation.cpp src/tissue_refinement.cpp src/tissue_branch_refinement.cpp
    src/tissue_prepared_fields.cpp src/tissue_branch_connections.cpp src/tissue_branch_connector.cpp src/tissue_parts.cpp src/tissue_envelope.cpp src/tissue_parameters.cpp src/tissue_crop_envelope.cpp src/tissue_crop.cpp src/tissue_crop_inputs.cpp src/tissue_smoothing.cpp src/smoothing_core.cpp
    src/tissue_domain.cpp src/tissue_domain_api.cpp src/tissue_shapes_api.cpp
    src/tissue_shape_fields.cpp src/tissue_normal_shell.cpp src/tissue_profile_sweep.cpp src/tissue_radial.cpp
    src/tissue_masks.cpp src/tissue_source_normals.cpp src/tissue_constraints.cpp
    src/material_binding.cpp src/material_binding_index.cpp src/material_binding_query.cpp
    src/tissue_relaxation.cpp src/tissue_geometric.cpp src/tissue_static.cpp src/tissue_point_relaxation.cpp
    src/stacking.cpp src/tissue_stacking.cpp src/tissue_stack_material.cpp
    src/tissue_stack_directions.cpp src/tissue_stack_geometry.cpp src/tissue_stack_constraints.cpp
    src/tissue_stack_assembly.cpp)

add_library(af_curve_fit STATIC vendor/curve_fit_nd/intern/curve_fit_cubic.c
    vendor/curve_fit_nd/intern/curve_fit_cubic_refit.c
    vendor/curve_fit_nd/intern/curve_fit_corners_detect.c
    vendor/curve_fit_nd/intern/generic_heap.c)
set_target_properties(af_curve_fit PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_link_libraries(af_native PRIVATE af_curve_fit)
target_include_directories(af_native PUBLIC include)
target_include_directories(af_native PRIVATE migration/smoothing/include)
target_include_directories(af_native SYSTEM PRIVATE vendor)
target_compile_definitions(af_native PRIVATE NOMINMAX _USE_MATH_DEFINES EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)
target_compile_definitions(af_native PRIVATE AF_NATIVE_BUILD)
set_target_properties(af_native PROPERTIES CXX_VISIBILITY_PRESET hidden)
if(MSVC)
    target_compile_options(af_native PRIVATE /W4 /WX /fp:precise)
else()
    target_compile_options(af_native PRIVATE -Wall -Wextra -Werror)
endif()
if(BUILD_TESTING)
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

