#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Owned immutable path results. Engine 0: Bezier; 1: exact polyline.
 * Input uses the 13-double authored curve record. Sample records have 11 doubles:
 * position, tangent, normal, radius, tilt. Parameters identify authored segment+t.
 * Closed paths contain no repeated endpoint. Buffers live until handle release. */
AF_API uint64_t af_path_evaluate(const double* records, int count, int engine,
    int closed, int resolution, uint64_t cancel);
AF_API uint64_t af_path_restore(const double* samples, const double* parameters,
    int count, int closed);
AF_API void af_path_release(uint64_t handle);
AF_API int af_path_info(uint64_t handle, int64_t* counts, double* bounds);
AF_API const double* af_path_buffer(uint64_t handle, int kind);
AF_API int af_path_sample(uint64_t handle, int count, double start, double span,
    const double* matrix, int reverse, double* output, uint64_t cancel);
AF_API int af_path_body(uint64_t handle, int reverse, int closed_start,
    double* output, uint64_t cancel);
#ifdef __cplusplus
}
#endif
