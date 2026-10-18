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
#ifdef __cplusplus
}
#endif
