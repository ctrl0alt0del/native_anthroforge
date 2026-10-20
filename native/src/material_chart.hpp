// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "material_binding.hpp"
#include "material_domain.hpp"

namespace af::material {
struct Chart {
    bool closed_u=false,closed_v=false;
    std::vector<double> boundary;
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
Atlas atlas(const MaterialBasis& basis,uint64_t cancel);
Triangle coordinates(const Mesh& mesh,const Atlas& atlas,const Eigen::Vector3i& vertices);
Indices indexed(const Mesh& mesh,const Atlas& atlas,uint64_t cancel);
Location locate(const Indices& index,const Atlas& atlas,int chart,const V3& query,uint64_t cancel);
M4 frame(const Mesh& current,const Location& location,const Tangents& directions,const M4& world,const double* record);
void disk_boundary(Chart& chart);
void transport(const Chart& before,const Chart& after,V3& query,V3& tangent);
Coordinate transported(const Chart& before,const Chart& after,const M3& triangle,const V3& weights);
}
