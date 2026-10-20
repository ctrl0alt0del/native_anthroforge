#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Bind-time C2 owner blending from the addon. Each node has at most two influences.
 * Owner -1 denotes an unused second influence. Fixed indices partition arc-length spans. */
AF_API int af_attachment_weights(const double* points,const int* owners,int count,
    const int* pins,int pin_count,int closed,int* targets,double* weights,uint64_t cancel);
/* Generic anatomical point bindings use the existing 28-double attachment record.
 * Capture accepts -1 for nearest eligible target, otherwise a fixed surface index.
 * Resolve returns one affine point/frame per binding, including its captured offset. */
AF_API int af_point_attachment_capture(int surfaces,const uint64_t* meshes,const double* frames,
    int count,const double* points,const int* forced,int* targets,double* bindings,uint64_t cancel);
AF_API int af_point_attachment_resolve(int surfaces,const uint64_t* meshes,const double* frames,
    int count,const int* targets,const double* bindings,double* output,uint64_t cancel);
AF_API int af_attachment_goal_points(const double* frames,int count,const double* local_frame,
    double offset,double* output,uint64_t cancel);
/* Resolve only referenced bind-time material vertices; never nearest-surface recapture.
 * Output is a geometry-only lease for attachment evaluation, not display or spatial queries. */
AF_API uint64_t af_material_binding_surface(uint64_t reference,uint64_t current,int count,const double* bindings,uint64_t cancel);
AF_API int af_mesh_basis_sizes(uint64_t source,int64_t* sizes);
AF_API int af_mesh_basis_copy(uint64_t source,int64_t* records,int64_t count,double* parameters,int64_t size);
AF_API uint64_t af_mesh_basis_restore(uint64_t source,const int64_t* records,int64_t count,const double* parameters,int64_t size,uint64_t cancel);
AF_API int af_material_binding_frames(uint64_t reference,uint64_t current,const double* world,int count,const double* records,double* frames,uint64_t cancel);
AF_API int af_attachment_blend_frames(int count,const double* frames,const double* weights,double* points,uint64_t cancel);
/* Dense path nodes followed by knot/left/right controls; two weighted influences per row. */
AF_API int af_curve_attachment_capture(int surfaces,const uint64_t* meshes,const double* frames,
    uint64_t path,const double* records,int knots,const double* world,const int* pins,
    const int* parents,int pin_count,const double* retained,int* owners,double* weights,double* bindings,uint64_t cancel);
AF_API int af_blended_attachment_resolve(int surfaces,const uint64_t* meshes,const double* frames,
    int count,const int* owners,const double* weights,const double* bindings,double* points,uint64_t cancel);
AF_API uint64_t af_attached_path(uint64_t path,const double* points,const double* world,uint64_t cancel);
AF_API int af_attached_controls(const double* records,int count,const double* points,
    const double* world,double* output);
AF_API int af_attachment_compact(int count,const int* owners,int surfaces,int* output,int* used);
/* Restore unedited structural pins against their own retained material surface snapshots. */
AF_API int af_attachment_retain_pins(uint64_t path,int knots,const int* pins,const int* targets,
    const double* records,int count,int* owners,double* weights,double* bindings);
#ifdef __cplusplus
}
#endif
