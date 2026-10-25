cmake_minimum_required(VERSION 3.24)
project(af_scm_trial LANGUAGES CXX)
add_library(af_scm_trial SHARED regional.cpp)
target_compile_features(af_scm_trial PRIVATE cxx_std_17)
target_include_directories(af_scm_trial SYSTEM PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../native/vendor")
target_compile_definitions(af_scm_trial PRIVATE NOMINMAX EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)

# Isolated direct SQP experiment. Not linked into af_native or the application.
add_library(af_scm_solver_only SHARED solver_only.cpp)
target_compile_features(af_scm_solver_only PRIVATE cxx_std_17)
target_include_directories(af_scm_solver_only PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../native/include")
target_include_directories(af_scm_solver_only SYSTEM PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../../native/vendor")
target_compile_definitions(af_scm_solver_only PRIVATE NOMINMAX EIGEN_MPL2_ONLY EIGEN_DONT_PARALLELIZE)
