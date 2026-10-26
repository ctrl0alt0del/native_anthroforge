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
#ifdef __cplusplus
}
#endif
