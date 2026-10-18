#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Owned path inputs; all output positions are consumer-local. Origin is an authored
 * path parameter, so closed correspondence survives geometric deformation. */
typedef struct AfSurfaceRow {
    uint64_t path;
    double matrix[16];
    double start,span,origin;
    int reverse,samples,alignment_reverse;
} AfSurfaceRow;
/* Explicit initial/Realign calculation. alignment: origin + reversal per row.
 * across: insert counts for adjacent rows. strips=0 chooses donor density. */
AF_API int af_curve_surface_layout(const AfSurfaceRow* rows,int count,int exact,int strips,
    double* alignment,int* across,uint64_t cancel);
/* Uses persisted correspondence and density; never realigns during deformation.
 * kind=0 loft; kind=1 single closed patch. Result is a draft mesh for canonical
 * topology finalization. close_across is independent of along-path closure. */
AF_API uint64_t af_curve_surface_geometry(const AfSurfaceRow* rows,int count,int exact,
    const int* across,int kind,int patch_resolution,int close_across,int flip,uint64_t cancel);
#ifdef __cplusplus
}
#endif
