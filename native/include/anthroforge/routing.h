#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* All inputs are owned by the caller for this synchronous worker invocation.
 * Records: 13 doubles per authored knot. Owners: zero for unbound or surface index+1.
 * Meshes/matrices: accepted surface handles and complete world transforms.
 * Report: eight counters and eight measures, described by the Python adapter. */
typedef struct AfRoutingOptions { int samples,accepted_steps,closed; double radius; } AfRoutingOptions;
AF_API uint64_t af_route_path(const double* records,int count,const double* world,
    const int* owners,const uint64_t* meshes,const double* matrices,int surfaces,
    const AfRoutingOptions* options,int64_t* counters,double* measures,uint64_t warm,uint64_t cancel);
/* Immutable captured collision geometry; release after all synchronous callers finish.
 * The cached scene and solve options must use the same clearance radius. */
AF_API uint64_t af_routing_scene_capture(const uint64_t* meshes,const double* matrices,
    int surfaces,double radius,uint64_t cancel);
AF_API void af_routing_scene_release(uint64_t scene);
AF_API uint64_t af_routing_scene_bytes(uint64_t scene);
AF_API uint64_t af_route_path_in_scene(const double* records,int count,const double* world,
    const int* owners,uint64_t scene,const AfRoutingOptions* options,
    int64_t* counters,double* measures,uint64_t warm,uint64_t cancel);
#ifdef __cplusplus
}
#endif
