#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
// Plane nx,ny,nz,d keeps world points with dot(n,p)+d >= 0.
// Bounded world-space contour segment pairs; counts: vertices, coplanar faces, truncated.
AF_API int af_section_contours(uint64_t mesh,const double* frame,const double* plane,
    int capacity,double* lines,int64_t* counts,uint64_t cancel);
AF_API int af_scene_pick_clipped(int count,const uint64_t* meshes,const double* matrices,
    const double* planes,const double* origin,const double* direction,double* hits);
#ifdef __cplusplus
}
#endif
