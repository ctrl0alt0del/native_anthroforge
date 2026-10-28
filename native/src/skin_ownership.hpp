#pragma once
#include "anthroforge/skin_ownership.h"
#include "mesh_internal.hpp"
#include "skin_point_index.hpp"
#include <map>
#include <set>
namespace af::skin_ownership {
using skin::PointIndex;
struct Samples { Vertices points; std::vector<int> sources; std::vector<std::vector<int>> indices; };
Samples samples(const AFSkinOwnershipInput& input,uint64_t cancel);
void assign(const Mesh& mesh,const AFSkinOwnershipInput& input,int* owners,int* sources,int* fallback,uint64_t cancel);
void clean(const Mesh& mesh,int* owners,double ratio,uint64_t cancel);
}
