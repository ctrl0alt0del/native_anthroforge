include(FetchContent)
foreach(package IN ITEMS cgal boost)
    set(bundled "${CMAKE_CURRENT_SOURCE_DIR}/dependencies/${package}")
    string(TOUPPER "af_query_${package}" key)
    if(EXISTS "${bundled}" AND NOT FETCHCONTENT_SOURCE_DIR_${key})
        set(FETCHCONTENT_SOURCE_DIR_${key} "${bundled}")
    endif()
endforeach()
FetchContent_Declare(af_query_cgal
    URL https://github.com/CGAL/cgal/releases/download/v6.1.1/CGAL-6.1.1.tar.xz
    URL_HASH SHA256=52506935f70e247ed2777e3c65f20e86f79208c2a2d0e180ae7475daf11c96ef
    SOURCE_SUBDIR unused)
FetchContent_Declare(af_query_boost
    URL https://archives.boost.io/release/1.89.0/source/boost_1_89_0.tar.bz2
    URL_HASH SHA256=85a33fa22621b4f314f8e85e1a5e2a9363d22e4f4992925d4bb3bc631b5a0c7a
    SOURCE_SUBDIR unused)
FetchContent_MakeAvailable(af_query_cgal af_query_boost)
file(WRITE "${CMAKE_BINARY_DIR}/boolean-dependencies.json"
    "{\"cgal\":\"${af_query_cgal_SOURCE_DIR}\",\"boost\":\"${af_query_boost_SOURCE_DIR}\"}\n")
add_library(af_boolean STATIC exterior.cpp qualification.cpp inspection.cpp)
set_target_properties(af_boolean PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(af_boolean SYSTEM PRIVATE ../vendor
    "${af_query_cgal_SOURCE_DIR}/include" "${af_query_boost_SOURCE_DIR}")
target_compile_definitions(af_boolean PRIVATE NOMINMAX _USE_MATH_DEFINES
    CGAL_DISABLE_GMP CGAL_USE_CORE CGAL_CORE_USE_BOOST_BACKEND
    IGL_PARALLEL_FOR_FORCE_SERIAL EIGEN_DONT_PARALLELIZE)
if(MSVC)
    target_compile_options(af_boolean PRIVATE /bigobj /fp:precise /W4 /WX)
else()
    target_compile_options(af_boolean PRIVATE -Wall -Wextra -Werror)
endif()
