#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Prior/output/info: one XYZ row per triangle. Samples: position/direction/normal/owner.
   Mesh and sample positions share the same coordinate frame. No input is modified. */
AF_API int af_skin_flow(uint64_t mesh,const double* prior,const double* samples,int count,
                       double* output,double* information,uint64_t cancel);
AF_API int af_skin_flow_route(uint64_t mesh,const double* points,int count,
                             int* edges,int capacity,uint64_t cancel);
AF_API int af_skin_flow_select(uint64_t mesh,const double* points,int points_count,
                              const int* offsets,int paths,int* selected,uint64_t cancel);
#ifdef __cplusplus
}
#endif
