#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Accepted sampled path, complete world frame, one surface owner per authored knot.
 * Owners are zero (unbound) or one-based surface indices. No path is mutated.
 * Output is path-major first offending segment, -1 when clear, plus metric tolerance.
 * Each invocation captures one collision world for the complete batch. */
typedef struct AfCollisionPath { uint64_t path; double world[16]; int count; const int* owners; } AfCollisionPath;
AF_API int af_path_collisions(const AfCollisionPath* paths,int count,const uint64_t* meshes,
    const double* matrices,int surfaces,int* output,double* tolerance,uint64_t cancel);
AF_API uint64_t af_collision_cache_create(void);
AF_API void af_collision_cache_release(uint64_t cache);
AF_API uint64_t af_collision_cache_bytes(uint64_t cache);
AF_API int af_path_collisions_cached(uint64_t cache,const AfCollisionPath* paths,int count,
    const uint64_t* meshes,const double* matrices,int surfaces,int* output,double* tolerance,uint64_t* statistics,uint64_t cancel);
#ifdef __cplusplus
}
#endif
