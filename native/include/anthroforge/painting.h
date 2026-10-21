#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
// Frozen displayed mesh and field correspondence. Source=1 uses sparse base weights;
// source=0 uses retained Rest correspondence. View: camera/right/up/forward (3 each),
// pixels per unit at depth 1, perspective (0/1). Occluders are ordinary visible meshes.
AF_API uint64_t af_paint_prepare(uint64_t target,uint64_t reference,int source,int count,
    const double* frame,const double* view,const uint64_t* others,const double* frames,int other_count,uint64_t cancel);
AF_API void af_paint_release(uint64_t handle);
AF_API uint64_t af_paint_bytes(uint64_t handle);
// Samples are screen XY, origin at viewport centre, Y up. Result owns RGBA chunks.
// Settings: radius pixels, target weight, strength, falloff power, paint through.
AF_API uint64_t af_paint_stroke(uint64_t handle,const double* baseline,const double* samples,
    int samples_count,const double* settings,double* values,uint64_t cancel);
#ifdef __cplusplus
}
#endif
