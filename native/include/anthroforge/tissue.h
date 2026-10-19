#pragma once
#include "api.h"
#include <stdint.h>

struct AfTissueInflation {
    int mode,enabled,reverse,falloff,direction,initialize_control;
    double amount,radius,depth,boundary_strength,boundary_band,boundary_power,taper;
    double control[3],profile[9];
};
#ifdef __cplusplus
extern "C" {
#endif
// Operates on accepted material grids, without resampling the source.
AF_API uint64_t af_tissue_inflate_grid(uint64_t source,const AfTissueInflation* settings,
    int count,uint64_t cancel);
AF_API uint64_t af_tissue_source_mesh(uint64_t source,const double* matrix,uint64_t cancel);
AF_API uint64_t af_tissue_refine_grid(uint64_t source,int resolution,uint64_t cancel);
#ifdef __cplusplus
}
#endif
