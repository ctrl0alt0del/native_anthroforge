#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AFSkinLoopInput {
    const uint64_t* paths;
    const double* frames;
    const double* plane;
    int count;
} AFSkinLoopInput;
typedef struct AFSkinLoopOutput {
    double* samples; /* capacity count * 192 * 6; XYZ + normal */
    int* sources; /* original input index for each retained loop */
    int* pairs; /* outer/inner retained loop indices, capacity count * 2 */
    int* statuses; /* per input: 0 paired, 1 unpaired, 2 duplicate, 3 zero perimeter */
    int* symmetric; /* retained loop reflection classification */
    int* sizes; /* retained loops, pairs */
} AFSkinLoopOutput;
AF_API int af_skin_loops(uint64_t mesh,const AFSkinLoopInput* input,AFSkinLoopOutput* output,uint64_t cancel);
#ifdef __cplusplus
}
#endif
