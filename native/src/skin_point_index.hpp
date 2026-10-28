#pragma once
#include "mesh_internal.hpp"
namespace af::skin {
struct PointIndex {
    Eigen::VectorXi elements;
    igl::AABB<Vertices,3> tree;
    PointIndex(const Vertices& vertices,const std::vector<int>& indices,uint64_t cancel);
    std::pair<int,double> nearest(const Vertices& vertices,const V3& point) const;
};
}
