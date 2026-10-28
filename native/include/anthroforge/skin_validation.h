#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Sixteen named topology quality observations; geometry is never repaired or rejected for quality. */
AF_API int af_skin_topology_quality(uint64_t mesh,uint64_t envelope,const int* regions,
    int guide_faces,int patches,const double* plane,double* output,uint64_t cancel);
AF_API int af_skin_intersections(uint64_t mesh,uint64_t budget,int64_t* witnesses,
    int capacity,int64_t* statistics,uint64_t cancel);
AF_API int af_skin_anatomy_clearance(uint64_t reference,uint64_t current,const double* rest_samples,
    const double* samples,int count,double* statistics,uint64_t cancel);
AF_API int af_skin_deformed_quality(uint64_t mesh,double* output,uint64_t cancel);
#ifdef __cplusplus
}
#endif
