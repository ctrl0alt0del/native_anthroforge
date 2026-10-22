// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Immutable compiled programs. Symbol names are newline-separated. Each input
   type is (kind:0=int64,1=real; length exponent; angle exponent). Caller owns all
   input/output buffers. Frames are row-major and use separate exact integer and
   real arrays. No callbacks, I/O, assignments, loops or implicit casts to int. */
AF_API uint64_t af_expression_compile(const char* source,const char* names,const int* types,int count,uint64_t cancel);
AF_API int af_expression_info(uint64_t handle,int* type,uint64_t* bytes);
AF_API int af_expression_evaluate(uint64_t handle,const int64_t* integers,const double* reals,int rows,
                                 int64_t* output_integer,double* output_real,uint64_t cancel);
AF_API void af_expression_release(uint64_t handle);
#ifdef __cplusplus
}
#endif
