add_library(af_native SHARED src/api.cpp src/mesh_io.cpp src/mesh_build.cpp
    src/mesh_registry.cpp src/transforms.cpp src/spatial.cpp src/attachment.cpp
    src/construction_mesh.cpp src/curves.cpp src/loft.cpp src/curve_body.cpp
    src/hooks.cpp src/lattices.cpp src/solidify.cpp src/component_queries.cpp src/curve_deform.cpp
    src/mesh_topology.cpp src/curve_frames.cpp src/curve_mapping.cpp src/component_index.cpp
    src/curve_queries.cpp src/influence.cpp src/control_geometry.cpp src/measurement.cpp
    src/path_registry.cpp src/path_presentation.cpp src/image.cpp src/image_placement.cpp
    src/curve_fit.cpp src/drawing.cpp src/attachment_weights.cpp src/path_editing.cpp)

add_library(af_curve_fit STATIC vendor/curve_fit_nd/intern/curve_fit_cubic.c
    vendor/curve_fit_nd/intern/curve_fit_cubic_refit.c
    vendor/curve_fit_nd/intern/curve_fit_corners_detect.c
    vendor/curve_fit_nd/intern/generic_heap.c)
set_target_properties(af_curve_fit PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_link_libraries(af_native PRIVATE af_curve_fit)
target_include_directories(af_native PUBLIC include)
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
endif()

