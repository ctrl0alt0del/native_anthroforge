# Skin kernels and independent coarse-field lines use the addon's bounded OpenMP teams.
# Routing and the other af_native translation units retain coordinator-only execution.
add_library(af_skin_kernels OBJECT src/skin_gaps.cpp src/skin_precision.cpp
    src/skin_envelope.cpp src/skin_diagnostics.cpp src/skin_execution.cpp src/skin_distance.cpp)
set_target_properties(af_skin_kernels PROPERTIES POSITION_INDEPENDENT_CODE ON
    CXX_VISIBILITY_PRESET hidden)
target_include_directories(af_skin_kernels PRIVATE include migration/smoothing/include)
target_include_directories(af_skin_kernels SYSTEM PRIVATE vendor)
target_compile_definitions(af_skin_kernels PRIVATE AF_NATIVE_BUILD NOMINMAX
    _USE_MATH_DEFINES EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)
target_link_libraries(af_skin_kernels PRIVATE OpenMP::OpenMP_CXX)
if(MSVC)
    target_compile_options(af_skin_kernels PRIVATE /W4 /WX /fp:precise)
else()
    target_compile_options(af_skin_kernels PRIVATE -Wall -Wextra -Werror)
endif()
