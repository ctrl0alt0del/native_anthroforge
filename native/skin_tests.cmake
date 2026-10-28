add_executable(af_skin_buffer_tests tests/skin_buffers_test.cpp tests/skin_assembly_test.cpp
    tests/skin_fields_test.cpp src/skin_assembly.cpp src/skin_distance.cpp
    src/skin_grid.cpp src/skin_collagen.cpp src/skin_exterior.cpp)
target_include_directories(af_skin_buffer_tests PRIVATE src include migration/smoothing/include)
target_include_directories(af_skin_buffer_tests SYSTEM PRIVATE vendor)
target_compile_definitions(af_skin_buffer_tests PRIVATE NOMINMAX _USE_MATH_DEFINES
    EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)
target_link_libraries(af_skin_buffer_tests PRIVATE OpenMP::OpenMP_CXX)
if(MSVC)
    target_compile_options(af_skin_buffer_tests PRIVATE /W4 /WX /fp:precise)
else()
    target_compile_options(af_skin_buffer_tests PRIVATE -Wall -Wextra -Werror)
endif()
add_test(NAME native_skin_buffers COMMAND af_skin_buffer_tests)
