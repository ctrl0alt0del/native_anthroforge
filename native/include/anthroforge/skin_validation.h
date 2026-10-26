#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Sixteen named topology quality observations; geometry is never repaired or rejected for quality. */
AF_API int af_skin_topology_quality(uint64_t mesh,uint64_t envelope,const int* regions,
    int guide_faces,int patches,const double* plane,double* output,uint64_t cancel);
#ifdef __cplusplus
}
#endif
