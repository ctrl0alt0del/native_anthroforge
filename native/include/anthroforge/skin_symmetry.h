#pragma once
#include "api.h"
#include "skin_guides.h"
extern "C" {
AF_API uint64_t af_skin_symmetry_half(uint64_t mesh,const double* plane,uint64_t cancel);
AF_API uint64_t af_skin_symmetry_mirror(uint64_t mesh,const double* plane,uint64_t cancel);
AF_API uint64_t af_skin_guides_half(const AFGuideInput* input,const double* plane,uint64_t cancel);
AF_API int af_skin_symmetry_plane(const double* frame,const double* plane,double* output);
}
