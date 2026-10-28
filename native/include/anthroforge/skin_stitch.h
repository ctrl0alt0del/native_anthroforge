#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AFSkinTransitionInput {
    const double* first;
    const double* second;
    const double* plane;
    int first_count,second_count;
    double diagonal;
} AFSkinTransitionInput;
/* diagnostics: mode(sparse/staged/centered),reason,shift,candidates,intersections,
   boundary count,annulus count,aspect P95,aspect max. Owned topology result. */
AF_API uint64_t af_skin_transition(const AFSkinTransitionInput* input,double* diagnostics,uint64_t cancel);
typedef struct AFSkinStitchOutput {
    double* transitions; /* capacity * 9 values */
    int capacity,count;
    char* warning;
    int warning_capacity;
} AFSkinStitchOutput;
AF_API uint64_t af_skin_stitch(uint64_t mesh,uint64_t annuli,const double* plane,int allow_unstitched,
                              AFSkinStitchOutput* output,uint64_t cancel);
#ifdef __cplusplus
}
#endif
