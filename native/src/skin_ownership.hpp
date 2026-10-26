#pragma once
#include "anthroforge/skin_ownership.h"
#include "mesh_internal.hpp"
#include <map>
#include <set>
namespace af::skin_ownership {
struct PointIndex {
    Eigen::VectorXi elements;
    igl::AABB<Vertices,3> tree;
    PointIndex(const Vertices& vertices,const std::vector<int>& indices,uint64_t cancel);
    std::pair<int,double> nearest(const Vertices& vertices,const V3& p) const;
};
struct Samples { Vertices points; std::vector<int> sources; std::vector<std::vector<int>> indices; };
Samples samples(const AFSkinOwnershipInput& input,uint64_t cancel);
void assign(const Mesh& mesh,const AFSkinOwnershipInput& input,int* owners,int* sources,int* fallback,uint64_t cancel);
void clean(const Mesh& mesh,int* owners,double ratio,uint64_t cancel);
}
