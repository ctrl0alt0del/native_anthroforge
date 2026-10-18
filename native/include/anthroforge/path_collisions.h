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
#ifdef __cplusplus
}
#endif
