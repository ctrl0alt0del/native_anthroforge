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
/* Expand a validated authored half into a closed path without duplicate seam points.
 * Reflection is expressed in the half's local coordinates; source data is unchanged. */
AF_API uint64_t af_path_symmetric(uint64_t path,const double* reflection,uint64_t cancel);
/* Constrain authored half endpoints to its local reflection plane, translating handles. */
AF_API int af_path_constrain_seams(const double* records,int count,const double* reflection,
    double* output);
/* XYZ programs share typed inputs beginning with dimensionless t. Closed sampling
 * excludes the interval end; output contains exactly count points and no seam copy. */
AF_API uint64_t af_parametric_path(const uint64_t* handles,int variables,
    const int64_t* integers,const double* reals,const double* metadata,int previous,
    int count,int closed,double start,double end,double* records,uint64_t cancel);
/* Interpolation 0 retains Bezier handle metadata; 1 connects generated knots directly. */
AF_API uint64_t af_parametric_interpolated_path(const uint64_t* handles,int variables,
    const int64_t* integers,const double* reals,const double* metadata,int previous,
    int count,int closed,double start,double end,int interpolation,int resolution,
    double* records,uint64_t cancel);
AF_API void af_path_release(uint64_t handle);
AF_API int af_path_info(uint64_t handle, int64_t* counts, double* bounds);
AF_API const double* af_path_buffer(uint64_t handle, int kind);
AF_API int af_path_sample(uint64_t handle, int count, double start, double span,
    const double* matrix, int reverse, double* output, uint64_t cancel);
/* Resample between required authored knots; output indices preserve their identities. */
AF_API int af_path_sample_anchored(uint64_t handle,const int* knots,int anchors,int count,
    double* output,int* indices,uint64_t cancel);
AF_API int af_path_body(uint64_t handle, int reverse, int closed_start,
    double* output, uint64_t cancel);
AF_API int af_path_memory_snapshot(uint64_t* rows, int capacity, uint64_t* total);
/* Rebase an explicit edit over the current dense attachment shape. Missing knot mappings
 * use ordered nearest correspondence. Entering edit mode never calls this operation. */
AF_API uint64_t af_path_rebase(uint64_t current,uint64_t opening,uint64_t draft,
    const double* records,const int* indices,int count,double* controls,uint64_t cancel);
/* Apply a consumer's control deformation without replacing its source's accepted shape. */
AF_API uint64_t af_path_control_deform(uint64_t current,uint64_t opening,uint64_t draft,uint64_t cancel);
/* Render-only closing vertex; bounded chunks share one boundary vertex. */
AF_API int af_path_chunk(uint64_t handle, int chunk, const float** data, int* count);
AF_API int af_path_chunk_count(uint64_t handle);
/* Render-only capped world-space tube. Radius does not inherit transform scale.
 * Returns an ordinary owned mesh with prepared render buffers and picking tree. */
AF_API uint64_t af_path_display_tube(uint64_t handle,const double* matrix,
    double radius,int sides,uint64_t cancel);
AF_API uint64_t af_path_tube(uint64_t handle,const double* matrix,
    double radius,int sides,uint64_t cancel);
/* One nearest segment hit per path: input index, ray distance, segment, XYZ. */
AF_API int af_paths_pick(int count, const uint64_t* paths, const double* matrices,
    const double* origin, const double* direction, double radius, double* output);
#ifdef __cplusplus
}
#endif
