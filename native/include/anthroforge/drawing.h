#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Blender 5.0.1 curve_fit_nd adapter. Input xyz or xyz/radius, methods REFIT=0,
 * SPLIT=1, exact polyline=2. Owned output uses the 13-double authored point layout.
 * Cancellation is checked before/after the upstream atomic fitting call. */
AF_API int af_curve_fit(const double* points, int count, int dimensions, int method,
    int closed, double error, double angle, double** output, int* output_count, uint64_t cancel);
AF_API void af_curve_fit_free(double* output);
#ifdef __cplusplus
}
#endif
