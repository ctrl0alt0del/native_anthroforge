#pragma once
#include "mesh.h"
#ifdef __cplusplus
extern "C" {
#endif
/* RGBA tiles are prepared off-thread. Each GUI adoption copies at most 256 KiB. */
AF_API uint64_t af_image_create(const unsigned char* rgba, int width, int height, uint64_t cancel);
AF_API void af_image_release(uint64_t handle);
/* Width, height, tile count, owned bytes. */
AF_API int af_image_info(uint64_t handle, uint64_t* info);
/* Tile pixel x, y, width, height. The owning handle must remain alive while reading. */
AF_API int af_image_tile(uint64_t handle, int tile, const unsigned char** data, int* info);
AF_API int af_image_calibration(const double* frame, const double* dimensions,
    const double* landmarks, double distance, double* output);
#ifdef __cplusplus
}
#endif
