#pragma once
#include "mesh.h"
#include "tissue.h"

#ifdef __cplusplus
extern "C" {
#endif
// Read-only, owned presentation buffers. Reference mode: 0 canonical, 1 source material.
AF_API uint64_t af_inspection_compare(uint64_t reference,uint64_t target,int source,const double* frame,uint64_t cancel);
AF_API void af_inspection_release(uint64_t handle);
AF_API int af_inspection_summary(uint64_t handle,double* values,int64_t* counts);
AF_API int af_inspection_chunk(uint64_t handle,int chunk,const float** data,int* count);
AF_API uint64_t af_inspection_bytes(uint64_t handle);
// Point row (20): position, source position, delta, normal (3 each), part/face/side/boundary,
// material boundary/seam/zero-height/structural-backing barycentric fractions.
AF_API int af_inspection_point(uint64_t target,uint64_t base,uint64_t rest,int triangle,const double* bary,double* row,uint64_t cancel);
AF_API int af_inspection_point_lines(uint64_t target,const double* frame,const double* row,double* lines);
// One row per region: core weight, feathered weight, fixed fraction, effective strength.
AF_API int af_inspection_regions(uint64_t target,uint64_t rest,uint64_t base,int triangle,const double* bary,
    const AfTissueRelax* settings,const AfTissueRegion* regions,int count,double* rows,uint64_t cancel);
// Bounded advisory findings: kind, other index, triangle, other triangle; six bounds values.
// Kinds: 1 degenerate, 2 self crossing, 3 other crossing. Touching/coplanar contact excluded.
AF_API int af_inspection_findings(uint64_t target,const double* frame,const uint64_t* others,
    const double* frames,int count,int limit,int64_t* ids,double* bounds,int64_t* total,uint64_t cancel);
AF_API int af_inspection_face_lines(uint64_t mesh,const double* frame,int triangle,double* lines);
#ifdef __cplusplus
}
#endif
