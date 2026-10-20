#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Blender 5.0.1 curve_fit_nd adapter. Input xyz or xyz/radius, methods REFIT=0,
 * SPLIT=1, exact polyline=2. Owned output uses the 13-double authored point layout.
 * Cancellation is checked before/after the upstream atomic fitting call. */
AF_API int af_curve_fit(const double* points, int count, int dimensions, int method,
    int closed, double error, double angle, double** output, int* output_count, uint64_t cancel);
AF_API void af_curve_fit_free(double* output);
/* Stroke owns immutable mesh snapshots; samples are xyz/radius. Plane is point/normal.
 * Settings: surface, first-hit plane (0:none,1:view,2:surface,3:tangent view), offset, relative offset.
 * Pointer input: ray origin/direction, screen xy, radius. Append returns total count;
 * Sampling mode: 0=discrete, 1=distance filter and depth substeps, 2=distance filter only.
 * Probe does not mutate the stroke. All access is serialized by the owning input tool. */
AF_API uint64_t af_stroke_create(int count,const uint64_t* meshes,const double* matrices,
    const double* plane,const double* settings);
AF_API void af_stroke_release(uint64_t handle);
AF_API int af_stroke_append(uint64_t handle,const double* pointer,int interpolate);
AF_API int af_stroke_seed(uint64_t handle, const double* pointer, const double* position, int retain_plane);
AF_API int af_stroke_probe(uint64_t handle,const double* pointer,double* output);
/* Temporary nearest-surface override; preserves the stroke's configured depth plane. */
AF_API int af_stroke_snapping(uint64_t handle,int enabled);
AF_API int af_stroke_read(uint64_t handle,int start,int capacity,double* output);
AF_API int af_stroke_pop(uint64_t handle);
AF_API int af_drawing_plane(const double* frame,double* output);
AF_API int af_stroke_view(uint64_t handle,const double* normal);
AF_API int af_stroke_batch(uint64_t handle,int count,const double* pointers,int interpolate,uint64_t cancel);
/* Owned capacities, excluding shared source meshes and allocator overhead. */
AF_API uint64_t af_stroke_bytes(uint64_t handle);
/* Returns world fit tolerance and closure eligibility from logical screen pixels. */
AF_API int af_stroke_settings(uint64_t handle,double pixels,double close_radius,double* output);
#ifdef __cplusplus
}
#endif
