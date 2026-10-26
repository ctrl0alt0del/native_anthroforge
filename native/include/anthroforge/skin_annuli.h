#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AFSkinAnnulusInput {
    const double* samples; /* loop_count * 192 * 6: XYZ and normals */
    const int* pairs; /* pair_count * 2: retained loop indices, outer first */
    const int* symmetric; /* per loop */
    const double* plane; /* optional origin XYZ, unit normal XYZ */
    int loop_count,pair_count;
} AFSkinAnnulusInput;
AF_API uint64_t af_skin_annuli(uint64_t mesh,const AFSkinAnnulusInput* input,uint64_t cancel);
AF_API int af_skin_annuli_sizes(uint64_t handle,int* sizes); /* points, quads, patches */
AF_API int af_skin_annuli_copy(uint64_t handle,double* samples,int64_t* quads,int* patches,const int* sizes);
/* samples: XYZ/normal. patches: point offset, segments, quad offset/count, source loops,
   mode (direct/planar/radial), mirror source (-1 none), inversion count. Quad indices global. */
AF_API void af_skin_annuli_release(uint64_t handle);
AF_API uint64_t af_skin_cut_guides(uint64_t mesh,uint64_t annuli,const double* plane,uint64_t cancel);
#ifdef __cplusplus
}
#endif
