#pragma once
#include "api.h"
#include "skin_ownership.h"
#ifdef __cplusplus
extern "C" {
#endif
AF_API int af_skin_proximity(uint64_t mesh,const AFSkinOwnershipInput* input,const uint8_t* enabled,
    const double* lengths,double* output,double* weights,double* statistics,uint64_t cancel);
AF_API int af_skin_base_target(uint64_t mesh,const double* lengths,int target,int reserved,int* result,uint64_t cancel);
/* Owned result bundle: mesh plus per-polygon region and guide provenance. */
AF_API uint64_t af_skin_quads_split(uint64_t mesh,const uint8_t* selected,const int* regions,const int* guides,uint64_t cancel);
AF_API uint64_t af_skin_refine(uint64_t mesh,uint64_t density,const double* lengths,const int* regions,
    const int* guides,int target,int passes,const double* plane,uint64_t cancel);
AF_API uint64_t af_skin_topology_mesh(uint64_t result);
AF_API int af_skin_topology_labels(uint64_t result,int* regions,int* guides,int count);
AF_API void af_skin_topology_release(uint64_t result);
#ifdef __cplusplus
}
#endif
