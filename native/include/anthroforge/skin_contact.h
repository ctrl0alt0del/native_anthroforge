#pragma once
#include "api.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AfSkinContact {
    const double* reference;
    const double* current;
    const double* proposed;
    int count;
    const int* faces;
    int face_count;
    const int* symmetry;
    const double* plane;
    uint64_t budget;
} AfSkinContact;
/* Source advisory contact/symmetry correction; eight explicit quality diagnostics. */
AF_API int af_skin_contact(const AfSkinContact* input,double* output,double* report,uint64_t cancel);
AF_API int af_skin_contact_symmetry(const double* points,int count,const double* plane,
    int* partners,double* maximum,uint64_t cancel);
#ifdef __cplusplus
}
#endif
