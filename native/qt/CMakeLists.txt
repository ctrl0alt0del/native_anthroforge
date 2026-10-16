qt_standard_project_setup(REQUIRES 6.12)
qt_add_qml_module(af_viewport
    URI AnthroForge.Native
    VERSION 1.0
    OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/qml/AnthroForge/Native"
    SOURCES probe_geometry.h probe_geometry.cpp mesh_geometry.h mesh_geometry.cpp
)
target_link_libraries(af_viewport PRIVATE Qt6::Quick3D af_native)

