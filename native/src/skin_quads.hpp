#pragma once
#include "construction_internal.hpp"
#include "skin_ownership.hpp"
#include "anthroforge/skin_topology.h"
#include <set>
#include <map>
namespace af::skin_quads {
using Quad=std::array<int64_t,4>;
using Edge=std::pair<int64_t,int64_t>;
using Mask=std::vector<uint8_t>;
struct Quads { Points points; std::vector<Quad> faces; std::vector<int> regions,guides; };
struct Result { std::shared_ptr<Mesh> mesh; std::vector<int> regions,guides; };
Quads capture(const Mesh& mesh,const int* regions,const int* guides,uint64_t cancel);
std::array<Edge,4> edges(const Quad& face);
Quads split(const Quads& source,const Mask& selected,uint64_t cancel);
Quads refine(Quads source,const Mesh& density,const double* lengths,int target,int passes,const double* plane,uint64_t cancel);
bool even_boundaries(const Quads& source,uint64_t cancel);
std::vector<std::vector<int>> candidates(const Quads& source,const std::vector<double>& scores,const double* plane,uint64_t cancel);
Result complete(Quads source,uint64_t cancel);
uint64_t retain(Result result);
}
