#pragma once
#include "mesh.h"
extern "C" {
struct AfFiberReference {
    uint64_t path;
    const double* records;
    int controls;
    const double* world;
    const int* owners;
    const double* weights;
    const double* bindings;
    int surfaces;
    const uint64_t* meshes;
    const double* frames; // Zero matrix requests recovery from retained capture evidence.
    int pins;
    const int* indices; // Authored control indices, not evaluated samples.
    const int* groups; // First capture of each anatomical surface, independent of pin history.
    const double* hints; // Saved document poses resolve unobservable directions in legacy captures.
};
AF_API uint64_t af_fiber_deformation_prepare(const AfFiberReference* input,uint64_t cancel);
AF_API int af_fiber_deformation_evaluate(uint64_t handle,const uint64_t* meshes,
    const double* frames,const double* goals,double* output,uint64_t cancel);
AF_API uint64_t af_fiber_deformation_bytes(uint64_t handle);
AF_API void af_fiber_deformation_release(uint64_t handle);
}
