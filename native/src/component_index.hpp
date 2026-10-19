#pragma once
#include "construction_internal.hpp"

namespace af {
using Edges=Eigen::Matrix<int,Eigen::Dynamic,2,Eigen::RowMajor>;
using ComponentTree=igl::AABB<Vertices,3>;
struct ComponentIndex { Vertices vertices; Edges edges; ComponentTree tree; std::vector<int> labels; };
struct ComponentRay { V3 origin,direction; double radius; };
std::shared_ptr<ComponentIndex> path_index(const double* samples,int count,bool closed,uint64_t cancel);
uint64_t component_bytes(const ComponentIndex& index);
std::pair<double,int> component_nearest(const ComponentIndex& index,const M4& frame,const ComponentRay& ray);
}
