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
/* Dense path nodes followed by knot/left/right controls; two weighted influences per row. */
AF_API int af_curve_attachment_capture(int surfaces,const uint64_t* meshes,const double* frames,
    uint64_t path,const double* records,int knots,const double* world,const int* pins,
    const int* parents,int pin_count,int* owners,double* weights,double* bindings,uint64_t cancel);
AF_API int af_blended_attachment_resolve(int surfaces,const uint64_t* meshes,const double* frames,
    int count,const int* owners,const double* weights,const double* bindings,double* points,uint64_t cancel);
AF_API uint64_t af_attached_path(uint64_t path,const double* points,const double* world,uint64_t cancel);
AF_API int af_attached_controls(const double* records,int count,const double* points,
    const double* world,double* output);
AF_API int af_attachment_compact(int count,const int* owners,int surfaces,int* output,int* used);
#ifdef __cplusplus
}
#endif
