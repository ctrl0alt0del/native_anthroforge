#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AfSkinFit {
    const double* vertices; int count;
    const int* quads; int quad_count;
    const double* targets; int frames;
    int bones, strategy;
    double smoothing;
} AfSkinFit;
AF_API int af_skin_fit(const AfSkinFit* input,double* weights,double* transforms,double* report,uint64_t cancel);
AF_API int af_skin_fit_predict(const double* vertices,int count,const double* weights,int bones,
    const double* keys,const double* matrices,int frames,const double* values,int samples,
    double* output_matrices,double* output_positions,uint64_t cancel);
AF_API int af_skin_fit_quality(const double* vertices,int count,const double* targets,const double* predicted,
    const int* training,int frames,double* report,uint64_t cancel);
AF_API int af_skin_fit_channels(const double* vertices,int count,const double* weights,int bones,const double* matrices,
    int frames,double* bases,double* channels,uint64_t cancel);
AF_API int af_skin_fit_playback(const double* vertices,int count,const double* weights,int bones,const double* bases,
    const double* keys,const double* channels,int frames,double value,double* output,uint64_t cancel);
AF_API int af_skin_fit_sampling(double minimum,double maximum,int count,double* values,int* training);
AF_API int af_skin_fit_repeatability(const double* first,const double* replay,int count,double* error);
#ifdef __cplusplus
}
#endif
