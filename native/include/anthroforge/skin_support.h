#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
AF_API int af_skin_support_sample(uint64_t mesh,const double* frame,int* selected,
    double* positions,double* mass,uint64_t cancel);
AF_API int af_skin_support_targets(uint64_t reference,uint64_t current,const double* frame,
    const int* selected,int count,double* positions,uint64_t cancel);
AF_API int af_skin_support_weights(const double* masses,const int* counts,int sources,
    double* weights,int count);
#ifdef __cplusplus
}
#endif
