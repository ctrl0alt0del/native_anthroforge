// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "material_chart.hpp"

namespace af::triangle_material {
struct ExteriorLayer {
    Vertices vertices;
    Triangles triangles;
    std::vector<int> identities;
    igl::AABB<Vertices,3> tree;
};
using ExteriorLayers=std::map<int64_t,std::unique_ptr<ExteriorLayer>>;
M3 coordinates(const Mesh& mesh,int triangle);
M4 exterior_frame(const Mesh& mesh,ExteriorLayers& layers,int64_t origin,const V3& query,
    const material::Tangents& directions,const M4& world,const double* record,uint64_t cancel);
}
