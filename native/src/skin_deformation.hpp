#pragma once
#include "mesh_internal.hpp"
#include "anthroforge/skin_deformation.h"
namespace af::skin::deformation {
struct Preparation;
std::shared_ptr<Preparation> prepare(const AfSkinReference& input,uint64_t cancel);
void solve(Preparation& value,const double* targets,int count,double* points,
    double* predicted,double* diagnostics,uint64_t cancel);
void embedding(Preparation& value,int* ids,double* weights);
uint64_t bytes(const Preparation& value);
int select(const std::vector<double>& mass,int* out,double* total);
}
