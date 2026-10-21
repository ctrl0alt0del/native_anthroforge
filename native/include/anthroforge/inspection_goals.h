#pragma once
#include "tissue.h"
#ifdef __cplusplus
extern "C" {
#endif
/* One row per region: world goal XYZ, displayed result XYZ, world residual length. */
AF_API int af_inspection_goals(uint64_t target,uint64_t rest,const AfTissueSource* source,
    int triangle,const double* bary,const double* frame,const AfTissueRegion* regions,
    int count,double* rows,uint64_t cancel);
#ifdef __cplusplus
}
#endif
