#pragma once
#include "mesh_internal.hpp"
#include <set>
namespace af::skin_density {
struct Region { std::vector<int> vertices; double budget=0,area=0; };
using Neighbors=std::vector<std::set<int>>;
void areas(const Mesh& mesh,double* result,uint64_t cancel);
std::vector<Region> regions(const Mesh& mesh,const int* ids,const double* budgets,int count,const double* areas,uint64_t cancel);
void initialize(const std::vector<Region>& regions,int64_t count,double* lengths);
void smooth(const Mesh& mesh,const std::vector<Region>& regions,const double* areas,double* values,int iterations,uint64_t cancel);
}
