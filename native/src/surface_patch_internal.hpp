#pragma once
#include "curve_surface_internal.hpp"
#include <map>
#include <set>

namespace af::curve_surface {
using V2=Eigen::Vector2d;
using Polygon=std::vector<V2>;
using Triangle=std::array<int,3>;
using PatchKey=std::array<int,5>;
struct Patch {
    Points points;
    Faces faces;
    std::vector<PatchKey> keys;
    std::map<PatchKey,int> indices;
};
Polygon project(const Points& points,uint64_t cancel);
double orient(const V2& a,const V2& b,const V2& c);
std::vector<Triangle> triangulate(Points& points,const Polygon& projected,uint64_t cancel);
Patch subdivide(const Points& points,const std::vector<Triangle>& triangles,int level,uint64_t cancel);
void fair(Patch& patch,int boundary_count,uint64_t cancel);
void boundary_last(Patch& patch,int count);
}
