#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Blender-default POLY bevel: 12 ring vertices, minimum twist, open ends. Radius is metres. */
AF_API uint64_t af_skin_fiber_bevel(uint64_t path,const double* frame,double radius,uint64_t cancel);
/* Owned mesh leases remain with caller. Output geometry is world-space and outward-oriented.
   Source policies are ratio/strength/SCP; output policies convert ratio to absolute distance. */
AF_API int af_skin_capture(const uint64_t* meshes,const double* frames,int sources,
    int vertices,int faces,const double* policies,double* xyz,int64_t* triangles,
    int* owners,uint8_t* skeletal,double* absolute_policies,uint64_t cancel);
/* Kinds: 0 mesh, 1 accepted path. Capacities: vertex/triangle/segment counts.
   Centerlines retain their world positions with no physical display radius. */
AF_API int af_skin_capture_sources(const uint64_t* handles,const int* kinds,const double* frames,int count,
    const int* limits,const double* policies,double* xyz,int64_t* triangles,int* owners,uint8_t* skeletal,
    double* absolute_policies,int64_t* segments,int* segment_owners,uint64_t cancel);
#ifdef __cplusplus
}
#endif
