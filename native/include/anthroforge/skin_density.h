#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* One region per vertex; exclusive budgets per region. Initial may be null.
   Outputs: edge lengths and vertex areas per vertex, area and unusable flag per region. */
AF_API int af_skin_density(uint64_t mesh,const int* regions,const double* budgets,int count,
    const double* initial,int iterations,double* lengths,double* areas,double* region_areas,
    int* unusable,uint64_t cancel);
#ifdef __cplusplus
}
#endif
