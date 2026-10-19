#pragma once
#include "stacking.h"
#include "tissue.h"

// Owned material preparation; all matrices and crop planes use tissue-local coordinates.
struct AfTissueStackSource {
    uint64_t base,rest,own;
    double frame[16],crop[7];
    int cropped,side,reverse;
    const AfTissueInflation* inflation;
    int parts;
    AfTissueRelax relaxation;
    const AfTissueRegion* regions;
    int region_count;
    const int64_t* pins;
    const double* pin_weights;
    int pin_count;
};
#ifdef __cplusplus
extern "C" {
#endif
AF_API uint64_t af_tissue_stack_prepare(const AfTissueStackSource* source,uint64_t cancel);
AF_API void af_tissue_stack_release(uint64_t handle);
// Returned pointers remain valid for the lifetime of the preparation lease.
AF_API int af_tissue_stack_domain(uint64_t handle,AfStackDomain* domain);
AF_API uint64_t af_tissue_stack_apply(uint64_t first,uint64_t second,const double* a,int acount,
    const double* b,int bcount,uint64_t cancel);
#ifdef __cplusplus
}
#endif
