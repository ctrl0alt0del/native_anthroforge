add_library(af_profiler SHARED qt_profile.h qt_profile.cpp qt_events.cpp qt_api.cpp)
set_target_properties(af_profiler PROPERTIES AUTOMOC ON)
target_link_libraries(af_profiler PRIVATE Qt6::Quick Qt6::QmlDebugPrivate)
target_compile_definitions(af_profiler PRIVATE NOMINMAX)
