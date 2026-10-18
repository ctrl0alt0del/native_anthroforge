#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Bézier records: position, left, right, radius, tilt, left/right mode (13 doubles).
 * Samples: position, tangent, normal, radius, tilt (11 doubles). */
AF_API int af_curve_sample(const double* points, int count, int closed, int resolution,
    int samples, double start, double span, const double* matrix, double* output, uint64_t cancel);
AF_API int af_curve_handles(double* points, int count, int closed);
/* Cubics: four world-space xyz controls per segment. Output: t, xyz, ray distance. */
AF_API int af_curve_cubics(const double* resolved, int count, int closed,
    const double* matrix, double* output);
AF_API int af_curve_closest(const double* cubics, int count, const double* origin,
    const double* direction, double* output);
AF_API int af_curve_split(const double* points, int count, int closed, int segment,
    double t, double* output);
AF_API int af_curve_path(const double* points, int count, int closed, int resolution,
    double* output, int* output_count, uint64_t cancel);
AF_API int af_curve_point_edit(double* points, int count, int closed, int index,
    const double* replacement, int fields, double* output);
AF_API uint64_t af_loft(const double* samples, int curves, int count, int strips,
    int closed, int caps, uint64_t cancel);
AF_API uint64_t af_body_base(int count, int shape, int sides, double width, double depth,
    double length, int closed, uint64_t cancel);
AF_API uint64_t af_curve_deform(uint64_t base, const double* samples, int count,
    int fit, double length, double position, int closed, uint64_t cancel);
AF_API uint64_t af_mesh_deformed(uint64_t source, const double* points, int64_t count, uint64_t cancel);
AF_API uint64_t af_mesh_join(const uint64_t* sources, int count, uint64_t cancel);
AF_API uint64_t af_mesh_reuse_topology(uint64_t source, uint64_t previous, uint64_t cancel);
/* Geometry-only roots propagate deferred preparation through deformation/join/solidify.
 * Draft handles expose immutable arrays/bounds, but cannot be queried or displayed.
 * Finalization creates a separate ready handle, preserving accepted canonical topology. */
AF_API uint64_t af_mesh_draft(uint64_t source, uint64_t cancel);
AF_API uint64_t af_mesh_storage_bytes(uint64_t source);
AF_API uint64_t af_mesh_finalize(uint64_t source, uint64_t previous, uint64_t cancel);
AF_API uint64_t af_loft_geometry(const double* samples, int curves, int count, int strips,
    int closed, int caps, uint64_t cancel);
AF_API uint64_t af_body_base_geometry(int count, int shape, int sides, double width, double depth,
    double length, int closed, uint64_t cancel);
AF_API uint64_t af_mesh_restore(const double* vertices, int64_t count, const int64_t* corners,
    const int64_t* offsets, int64_t faces, const int32_t* triangles, const int64_t* polygons,
    int64_t triangle_count);
AF_API int af_matrix_relative(const double* frame, const double* world, double* output);
AF_API int af_matrix_product(const double* a, const double* b, double* output);
AF_API int af_points_transform(const double* points, int count, const double* matrix, double* output);
/* Output capacity: 2*count xyz values; group partitions independent polylines. */
AF_API int af_polyline_lines(const double* points, int count, int group, int closed,
    const double* matrix, double* output);
/* Output capacity: 6*count xyz values. Returns written point count, -1 on error. */
AF_API int af_lattice_lines(const double* points, int count, const int* resolution,
    const double* matrix, double* output);
/* Null weights mean unit influence. Invert affects explicit weights only.
 * Restriction with no indices yields zero; out-of-range positive indices are ignored.
 * Output contains count doubles; cancellation leaves unpublished scratch only. */
AF_API int af_influence(const double* weights, int count, int invert, const int* indices,
    int index_count, int restricted, double* output, uint64_t cancel);
AF_API int af_component_pick(const double* points, int count, const double* origin,
    const double* direction, double radius, int depth);
AF_API int af_component_hits(const double* points, int count, const double* origin,
    const double* direction, double radius, double* output);
AF_API uint64_t af_component_index_create(const double* points, int count, int segments, const int* labels);
AF_API void af_component_index_release(uint64_t handle);
AF_API int af_component_index_pick(uint64_t handle, const double* origin,
    const double* direction, double radius, int depth);
AF_API int af_hook(double* points, int count, const double* matrix, const double* uniform,
    const double* center, double strength, double radius, int falloff, const double* weights,
    const double* custom, int custom_count, uint64_t cancel);
AF_API int af_curve_mapping(const double* points, const int* modes, int count, int extrapolate, double* table);
AF_API int af_lattice_grid(const int* resolution, double* points);
AF_API int af_lattice_resolution(int* resolution);
AF_API int af_lattice(double* points, int count, const double* cage, const int* resolution,
    const int* interpolation, const double* matrix, double strength, const double* weights,
    const double* cage_weights, uint64_t cancel);
AF_API int af_lattice_outside(double* cage, const int* resolution);
AF_API uint64_t af_solidify(uint64_t source, const double* settings, const double* weights, uint64_t cancel);
#ifdef __cplusplus
}
#endif
