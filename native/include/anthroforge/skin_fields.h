#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Owned coarse fields. Settings: minimum offset, collagen depth/core/falloff ratios.
   Faces carry an SCP flag; collagen is an absolute value per source vertex.
   Field kinds: required, full, collagen, combined. All arrays use XYZ row-major grids. */
AF_API uint64_t af_skin_fields_create(const double* xyz,int vertices,const int64_t* faces,int triangles,
    const uint8_t* scp,const double* collagen,const double* settings,int resolution,uint64_t budget,uint64_t cancel);
/* Centerlines have no radius and seed the anatomy envelope, not collagen. */
AF_API uint64_t af_skin_fields_sources(const double* xyz,int vertices,const int64_t* faces,int triangles,
    const uint8_t* scp,const double* collagen,const int64_t* segments,int segment_count,
    const double* settings,int resolution,uint64_t budget,uint64_t cancel);
AF_API int af_skin_fields_info(uint64_t handle,int* shape,double* origin_voxel,int* resolution);
AF_API int af_skin_fields_copy(uint64_t handle,int kind,double* output,uint64_t capacity);
AF_API uint64_t af_skin_fields_bytes(uint64_t handle);
AF_API void af_skin_fields_destroy(uint64_t handle);
AF_API uint64_t af_skin_tile_mesh(const float* values,const int* shape,uint64_t cancel);
#ifdef __cplusplus
}
#endif
