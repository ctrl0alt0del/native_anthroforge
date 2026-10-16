#pragma once
#include <stdint.h>

#if defined(_WIN32)
#if defined(AF_NATIVE_BUILD)
#define AF_API __declspec(dllexport)
#else
#define AF_API __declspec(dllimport)
#endif
#else
#define AF_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif
AF_API uint32_t af_abi_version(void);
/* Packed XYZ doubles; output is min XYZ then max XYZ, unchanged on failure.
   Return 0 on success, 1 for invalid/empty input. Caller owns both buffers. */
AF_API int af_bounds3d(const double* xyz, uint64_t count, double* bounds);
#ifdef __cplusplus
}
#endif

