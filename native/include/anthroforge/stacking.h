#pragma once
#include "mesh.h"

struct AfStackMaterial {
    const double *vertices, *weights, *constraint_weights;
    const int64_t *faces, *interpolation, *fixed, *constraints;
    int vertices_count, faces_count, samples, width, fixed_count, constraint_count;
};
struct AfStackDomain {
    uint64_t id;
    const double *base, *own, *direction;
    const int64_t *faces, *parts, *sources;
    int vertices, triangles, family, root, enabled, side;
    double allowance;
    AfStackMaterial material;
};
struct AfStackSettings {
    double search, area, epsilon, clearance, radius, strength, blend, preservation, adjustment;
    uint64_t cache_bytes, result_bytes;
    int fragment_limit;
};
struct AfStackPolicy {
    uint64_t first, second, cover;
    int excluded, invalid, offset, count, mode;
};
struct AfStackObstacle { const double* vertices; const int64_t* faces; int count, triangles; };
struct AfStackOutput {
    uint64_t id;
    int status;
    int64_t vertices;
    double maximum, map_ms, solve_ms, validation_ms;
    int64_t baseline_self, baseline_bone_crossings, open_obstacles;
    double baseline_penetration;
    char message[256];
};
struct AfStackOrder {
    uint64_t first, second, underlying, covering;
    int status, warnings;
    double positive[2], negative[2], coincident, minimum, maximum;
    int64_t fragments, points, crossings;
    char diagnostic[128];
};

#ifdef __cplusplus
extern "C" {
#endif
AF_API uint64_t af_stack_create();
AF_API void af_stack_release(uint64_t handle);
AF_API int af_stack_run(uint64_t handle,const AfStackDomain* domains,int count,const AfStackSettings* settings,
    const AfStackPolicy* policies,int policy_count,const int64_t* regions,int region_count,
    const AfStackObstacle* obstacles,int obstacle_count,uint64_t cancel);
AF_API int af_stack_sizes(uint64_t handle,int64_t* sizes);
AF_API int af_stack_results(uint64_t handle,AfStackOutput* rows,int count);
AF_API int af_stack_orders(uint64_t handle,AfStackOrder* rows,int count);
AF_API int af_stack_points(uint64_t handle,uint64_t identity,double* points,int count,double* metrics);
#ifdef __cplusplus
}
#endif
