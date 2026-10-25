#pragma once
#include "routing.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Optional read-only solve. Failure retains diagnostic evidence; cancellation fails the call.
 * Bounded to 128 complete path records, 131072 points and 4096 contact witnesses.
 * Record: stage,span,attempt,trial,accepted,termination,point_begin,count,contact_begin,count.
 * Contact: edge,collider,face,feature,contained,limiting,factor,gap,pointXYZ,surfaceXYZ,normalXYZ.
 * Coordinates are world-space. Buffers remain owned until release. */
AF_API uint64_t af_route_inspect(const double* records,int count,const double* world,const int* owners,
    uint64_t scene,const AfRoutingOptions* options,uint64_t warm,uint64_t cancel,int backend);
AF_API int af_route_trace_info(uint64_t handle,int64_t* info,int64_t* counters,double* measures);
AF_API const int64_t* af_route_trace_records(uint64_t handle);
AF_API const double* af_route_trace_buffer(uint64_t handle,int kind);
AF_API const char* af_route_trace_error(uint64_t handle);
AF_API void af_route_trace_release(uint64_t handle);
AF_API uint64_t af_route_inspect_configured(const double* records,int count,const double* world,const int* owners,
    uint64_t scene,const AfRoutingOptions* options,uint64_t warm,uint64_t cancel,int backend,
    double length_weight,int checkpoint_steps);
#ifdef __cplusplus
}
#endif
