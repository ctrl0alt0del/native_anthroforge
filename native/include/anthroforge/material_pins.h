#pragma once
#include "curve_surface.h"

struct AfSurfacePins {
    const AfSurfaceRow* rows;
    int count,exact,main_count;
    const int* across;
    const AfSurfaceBranch* branches;
    int branch_count;
    // Pairs: source-row index and authored point parameter. Never sampled-output indices.
    const int* points;
    int point_count;
};
#ifdef __cplusplus
extern "C" {
#endif
AF_API uint64_t af_surface_material_pins(uint64_t mesh,const AfSurfacePins* inputs,uint64_t cancel);
AF_API int64_t af_mesh_material_pins(uint64_t mesh,double* data,int64_t count);
AF_API uint64_t af_mesh_with_material_pins(uint64_t mesh,const double* data,int64_t count,uint64_t cancel);
#ifdef __cplusplus
}
#endif
