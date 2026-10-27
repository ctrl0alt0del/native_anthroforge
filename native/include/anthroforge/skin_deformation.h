#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AfSkinReference {
    const double* proxy; int proxy_count;
    const int* tets; int tet_count;
    const double* points; int point_count;
    const double* samples; int sample_count;
    const double* weights;
    int method, handles;
    double strength;
    const char* cache_path;
} AfSkinReference;
/* Owned preparation; world-space inputs are normalized exactly as the addon. */
AF_API uint64_t af_skin_deformation_prepare(const AfSkinReference* input,uint64_t cancel);
AF_API int af_skin_deformation_solve(uint64_t handle,const double* targets,int count,
    double* points,double* predicted,double* diagnostics,uint64_t cancel);
AF_API int af_skin_deformation_embedding(uint64_t handle,int* ids,double* weights);
AF_API uint64_t af_skin_deformation_bytes(uint64_t handle);
AF_API void af_skin_deformation_release(uint64_t handle);
/* Original area-CDF sampling: at most 80 unique vertex addresses, normalized per caller. */
AF_API int af_skin_deformation_samples(const double* points,int count,const int* faces,
    int face_count,int arity,int* selected,double* mass,uint64_t cancel);
#ifdef __cplusplus
}
#endif
