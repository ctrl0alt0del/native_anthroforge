#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Owned mesh leases remain with caller. Output geometry is world-space and outward-oriented.
   Source policies are ratio/strength/SCP; output policies convert ratio to absolute distance. */
AF_API int af_skin_capture(const uint64_t* meshes,const double* frames,int sources,
    int vertices,int faces,const double* policies,double* xyz,int64_t* triangles,
    int* owners,uint8_t* skeletal,double* absolute_policies,uint64_t cancel);
#ifdef __cplusplus
}
#endif
