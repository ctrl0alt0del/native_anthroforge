#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Sources are separate geometric instances; bone_ids map them to authored budgets.
   Offsets delimit contiguous source vertices and candidate source indices (CSR).
   Triangles and segments carry source indices, never authored bone indices. */
typedef struct AFSkinOwnershipInput {
    const double* vertices;
    const int* vertex_offsets;
    const int64_t* triangles;
    const int* triangle_sources;
    const int64_t* segments;
    const int* segment_sources;
    const int* bone_ids;
    const int* candidate_offsets;
    const int* candidates;
    int source_count,vertex_count,triangle_count,segment_count,candidate_count;
} AFSkinOwnershipInput;
/* Output owner and nearest-source labels per skin vertex; fallback count before cleanup. */
AF_API int af_skin_ownership(uint64_t mesh,const AFSkinOwnershipInput* input,double island_ratio,
    int* owners,int* sources,int* fallback,uint64_t cancel);
AF_API int af_skin_owner_regions(const int* owners,int count,const int* mapping,int owner_count,
    int remainder,int* regions,uint64_t cancel);
/* Transfer discrete ownership and density from accepted skin vertices to output vertices. */
AF_API int af_skin_sample_density(uint64_t source,uint64_t target,const int* owners,
    const double* lengths,int* sampled_owners,double* sampled_lengths,uint64_t cancel);
#ifdef __cplusplus
}
#endif
