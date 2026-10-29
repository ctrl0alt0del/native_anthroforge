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
// World bounds(6), extents(3), edge min/max, minimum area/longest-edge^2, transform condition,
// offset/extent ratio. Counts: edges, boundary, nonmanifold, orientation conflicts, degenerates.
AF_API int af_inspection_metrics(uint64_t mesh,const double* frame,double* values,int64_t* counts,double* lines,uint64_t cancel);
// Plane basis spans(2), U/V(6); two axis segments; counts: contour points, coplanar, truncated.
AF_API int af_inspection_section_spans(uint64_t mesh,const double* frame,const double* plane,double* values,double* lines,int64_t* counts,uint64_t cancel);
// Read-only nearest/ray evidence using the production query mesh and material correspondence.
// Request: origin(3), direction(3), offset. Returns closest candidate, -1 for no hit, -2 on error.
AF_API int af_inspection_placement(int count,const uint64_t* meshes,const double* frames,const double* request,int ray,double* rows,uint64_t cancel);
// At most 512 deterministic source-vertex samples. Rows: side, nearest distance, point, nearest point.
// 0 qualified volume; positive values explain unavailable volume; -1 error/cancel.
AF_API int af_inspection_volume(uint64_t source,const double* frame,uint64_t volume,const double* volume_frame,int limit,double* rows,int64_t* count,uint64_t cancel);
// Geometric min/max/mean/RMS from <=512 vertices per side; not an exact Hausdorff bound.
// When verified, material min/max/mean/RMS from every canonical vertex follow. Counts: both sample counts.
AF_API int af_comparison_distances(uint64_t first,const double* a,uint64_t second,const double* b,int verified,double* values,int64_t* counts,uint64_t cancel);
#ifdef __cplusplus
}
#endif
