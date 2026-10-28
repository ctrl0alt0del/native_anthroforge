#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AFGuideInput {
    const double* samples; int64_t sample_count;
    const double* points; int64_t point_count;
    const int64_t* offsets; int64_t path_count;
} AFGuideInput;
AF_API uint64_t af_skin_guides_merge(const AFGuideInput* inputs,int count,uint64_t cancel);
AF_API int64_t af_skin_guides_regions(uint64_t handle,int64_t* output,int64_t capacity);
AF_API uint64_t af_skin_guides_charts(uint64_t base,uint64_t current,const double* frame,int reverse,uint64_t cancel);
AF_API uint64_t af_skin_guides_path(uint64_t path,const double* frame,uint64_t cancel);
AF_API int af_skin_guides_sizes(uint64_t handle,int64_t* sizes);
AF_API int af_skin_guides_copy(uint64_t handle,double* samples,double* points,int64_t* offsets,const int64_t* capacities);
AF_API void af_skin_guides_release(uint64_t handle);
#ifdef __cplusplus
}
#endif
