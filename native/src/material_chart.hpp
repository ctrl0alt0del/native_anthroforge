// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "material_binding.hpp"
#include "material_domain.hpp"

namespace af::material {
using V2=Eigen::Vector2d;
struct Chart {
    bool closed_u=false,closed_v=false;
    std::map<double,V2> boundary;
    std::map<int64_t,V3> points;
};
struct Atlas {
    std::vector<Chart> charts;
    std::vector<std::vector<int>> membership;
};
struct Triangle {
    int chart=-1;
    M3 coordinates=M3::Zero();
};
struct ChartIndex {
    Vertices vertices;
    Triangles triangles;
    std::vector<int> geometry;
    igl::AABB<Vertices,3> tree;
};
using Indices=std::vector<std::unique_ptr<ChartIndex>>;
using Tangents=Eigen::Matrix<double,3,2>;
struct Coordinate { V3 point; Tangents tangents; };
struct Location { int triangle=-1; V3 weights=V3::Zero(); M3 coordinates=M3::Zero(); };
struct Cage { std::vector<V2> source,target; };
struct Mapping { V2 point=V2::Zero(); Eigen::Matrix2d derivative=Eigen::Matrix2d::Zero(); };
Atlas atlas(const MaterialBasis& basis,uint64_t cancel);
Triangle coordinates(const Mesh& mesh,const Atlas& atlas,const Eigen::Vector3i& vertices);
Indices indexed(const Mesh& mesh,const Atlas& atlas,uint64_t cancel);
Location locate(const Indices& index,const Atlas& atlas,int chart,const V3& query,const Tangents& directions,uint64_t cancel);
M4 frame(const Mesh& current,const Location& location,const Tangents& directions,const M4& world,const double* record);
std::vector<Cage> cages(const Atlas& before,const Atlas& after,uint64_t cancel);
Mapping mean_value(const Cage& cage,const V2& query,uint64_t cancel);
Coordinate transported(const Cage& cage,const M3& triangle,const V3& weights,uint64_t cancel);
}
namespace af::triangle_material {
void frames(const Mesh& before,const Mesh& after,const M4& world,int count,const double* records,double* output,uint64_t cancel);
}
