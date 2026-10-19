#pragma once
#include "api.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
// Same-connectivity deformation: baseline/new transverse crossings, new collapses,
// and normal rotations over 90 degrees (informational, not an inversion test).
AF_API int af_mesh_deformation_quality(uint64_t rest,uint64_t result,int64_t* counts,uint64_t cancel);
AF_API int af_mesh_validate_deformation(uint64_t rest,uint64_t result,uint64_t cancel);
#ifdef __cplusplus
}
#endif
