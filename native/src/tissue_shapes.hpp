// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "construction_internal.hpp"
#include "anthroforge/tissue.h"
#include <map>

namespace af::tissue {
using Edge=std::pair<int64_t,int64_t>;
struct EdgeUse { int count=0; Edge oriented{}; };
using Edges=std::map<Edge,EdgeUse>;
V3 unit(const V3& value);
Edges boundary_topology(const Faces& faces,uint64_t cancel);
Edges mesh_edges(const Faces& faces,uint64_t cancel);
Vertices surface_normals(const Mesh& source,const Faces& faces,uint64_t cancel);
std::vector<double> boundary_weights(const Mesh& mesh,const Edges& edges,uint64_t cancel);
std::vector<double> mask_distances(const Mesh& mesh,const Edges& edges,const std::vector<double>& mask,uint64_t cancel);
void validate_shape(const AfTissueShape& settings);
std::shared_ptr<Mesh> normal_shell(const Mesh& mesh,const AfTissueShape& settings,const double* weights,int64_t count,uint64_t cancel);
std::shared_ptr<Mesh> profile_sweep(const double* samples,int count,bool closed,const AfTissueShape& settings,uint64_t cancel);
std::shared_ptr<Mesh> radial(const M4& frame,const AfTissueShape& settings,int resolution,uint64_t cancel);
}
