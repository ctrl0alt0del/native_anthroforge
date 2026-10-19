#pragma once
#include "api.h"
#include <stdint.h>

struct AfTissueInflation {
    int mode,enabled,reverse,falloff,direction,initialize_control;
    double amount,radius,depth,boundary_strength,boundary_band,boundary_power,taper;
    double control[3],profile[9];
};
struct AfTissueShape {
    int enabled,reverse,segments;
    double amount,minimum,power,width,endpoint_taper,scale[3];
};
struct AfTissueSource {
    uint64_t mesh,path,host;
    double frame[16],host_frame[16];
};
struct AfTissueRelax {
    int mode,iterations,passes;
    double gravity[3],sagginess,limit,shape,volume,slack,tolerance,amount,minimum,power;
};
struct AfTissueRegion {
    int mask,mode,domain;
    double strength,feather,offset;
    const double* weights;
    int64_t count;
    const double* goals;
};
#ifdef __cplusplus
extern "C" {
#endif
AF_API uint64_t af_tissue_normal_shell(uint64_t source,const AfTissueShape* settings,const double* weights,int64_t count,uint64_t cancel);
AF_API uint64_t af_tissue_profile_sweep(const double* samples,int count,int closed,const AfTissueShape* settings,uint64_t cancel);
AF_API uint64_t af_tissue_radial(const double* frame,const AfTissueShape* settings,int resolution,uint64_t cancel);
AF_API uint64_t af_tissue_relax(uint64_t rest,const AfTissueSource* source,const AfTissueRelax* settings,const AfTissueRegion* regions,int count,double* report,uint64_t cancel);
// Operates on accepted material grids, without resampling the source.
AF_API uint64_t af_tissue_inflate_grid(uint64_t source,const AfTissueInflation* settings,
    int count,uint64_t cancel);
AF_API uint64_t af_tissue_inflate_parts(uint64_t source,const AfTissueInflation* settings,int count,const double* connectors,int envelope,uint64_t cancel);
AF_API uint64_t af_tissue_envelope(uint64_t first,uint64_t second,int reverse,uint64_t cancel);
AF_API int af_tissue_profile_reset(double depth,double* profile);
AF_API int af_tissue_control_default(uint64_t source,int part,double* point);
AF_API uint64_t af_tissue_source_mesh(uint64_t source,const double* matrix,uint64_t cancel);
AF_API uint64_t af_tissue_refine_grid(uint64_t source,int resolution,uint64_t cancel);
AF_API int af_mesh_tissue_sizes(uint64_t source,int64_t* sizes);
AF_API int af_mesh_tissue_copy(uint64_t source,int64_t* data,int64_t count,double* weights,int64_t entries);
AF_API uint64_t af_mesh_tissue_restore(uint64_t source,const int64_t* data,int64_t count,const double* weights,int64_t entries,uint64_t cancel);
#ifdef __cplusplus
}
#endif
