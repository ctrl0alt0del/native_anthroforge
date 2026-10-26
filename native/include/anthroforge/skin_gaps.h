#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Source ownership is per triangle; policies hold absolute gap limit, strength, SCP flag. */
AF_API uint64_t af_skin_scene_create(const double* xyz,int vertices,const int64_t* faces,int triangles,
    const int* owners,int sources,const double* policies,uint64_t cancel);
AF_API int af_skin_scene_sample(uint64_t scene,const double* points,int count,double reach,double* output,uint64_t cancel);
AF_API void af_skin_scene_destroy(uint64_t scene);
AF_API int af_skin_scene_progress(uint64_t scene,int* values);
AF_API int af_skin_scene_bind(uint64_t scene,uint64_t mesh,int* owners,int* triangles,
    float* barycentric,float* weights,float* offsets,float* support,uint64_t cancel);
/* diagnostics[19]: completed-check mask, mesh quality[9], gap coverage[7], source intersections, removed components. */
AF_API uint64_t af_skin_envelope_mesh(uint64_t fields,uint64_t scene,uint64_t budget,double* diagnostics,uint64_t cancel);
#ifdef __cplusplus
}
#endif
