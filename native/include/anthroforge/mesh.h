#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
AF_API const char* af_last_error(void);
AF_API uint64_t af_mesh_import(const char* path, double units, int y_up, uint64_t cancel);
AF_API uint64_t af_mesh_create(const double* vertices, int64_t count,
    const int64_t* corners, const int64_t* offsets, int64_t faces);
AF_API void af_mesh_release(uint64_t handle);
AF_API int af_surface_point(uint64_t mesh, const double* matrix, int triangle, const double* weights, double* output);
AF_API int af_measure_points(const double* first, const double* second, double* output);
/* Bounded rows: handle, allocation identity, buffers, estimated tree, render, vertices, triangles. */
AF_API int af_mesh_memory_snapshot(uint64_t* rows, int capacity, uint64_t* total_handles);
AF_API int af_mesh_sizes(uint64_t handle, int64_t* sizes);
AF_API const void* af_mesh_buffer(uint64_t handle, int kind);
AF_API int af_mesh_bounds(uint64_t handle, double* bounds);
AF_API int af_mesh_chunk(uint64_t handle, int chunk, const float** data, int* count);
AF_API uint64_t af_cancel_create(void);
AF_API void af_cancel_request(uint64_t token);
AF_API void af_cancel_release(uint64_t token);
AF_API int af_transform(const double* trs, double* matrix);
AF_API int af_decompose(const double* matrix, double* trs);
AF_API int af_point(const double* matrix, const double* point, double* output);
AF_API int af_quaternion(const double* matrix, double* quaternion);
/* Unit axis and degrees to world XYZ Euler angles (degrees). */
AF_API int af_axis_rotation(const double* axis, double angle, double* angles);
/* Unit world normal, respecting nonuniform scale and mirrored transforms. */
AF_API int af_surface_normal(uint64_t mesh, const double* matrix, int triangle, double* normal);
AF_API int af_geometry_matrix(const double* matrix, const double* offset, double* output);
/* Conservative world bounds from transformed local bounds; O(mesh count). */
AF_API int af_scene_bounds(int count, const uint64_t* meshes, const double* matrices, double* bounds);
AF_API int af_scene_pick(int count, const uint64_t* meshes, const double* matrices,
    const double* origin, const double* direction, double* hits);
/* Hit: world distance, polygon, triangle, nearest vertex, world xyz, barycentrics. */
AF_API int af_pick(uint64_t mesh, const double* matrix, const double* origin,
    const double* direction, double* hit);
/* Binding has 28 doubles; geometry offsets are local to each transform origin. */
AF_API int af_capture(uint64_t child, uint64_t parent, const double* child_matrix,
    const double* parent_matrix, const double* child_offset, const double* parent_offset,
    int parent_mode, int child_mode, int lock, int flow, double* binding);
AF_API int af_propagate(int count, const uint64_t* meshes, const int* parents,
    double* matrices, const double* offsets, const double* bindings, const int* modes,
    const int* follows, const int* flows, const int* active, int* status, uint64_t cancel);
AF_API int af_move_origin(const double* matrix, const double* offset,
    const double* binding, double* updated_matrix, double* updated_offset);
AF_API int af_anchor_points(uint64_t parent, const double* child_matrix,
    const double* parent_matrix, const double* parent_offset, const double* binding, double* points);
#ifdef __cplusplus
}
#endif
