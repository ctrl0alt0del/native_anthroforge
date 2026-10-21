// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "tissue_shapes.hpp"
#include "path_internal.hpp"

namespace af::tissue {
struct Constraints {
    Vertices goals,normals;
    std::vector<double> mass,tethers;
};
using WeightField=std::vector<double>;
WeightField region_mask(const Mesh& rest,const Mesh* base,const AfTissueRelax& settings,const AfTissueRegion& region,uint64_t cancel);
WeightField feather(const Mesh& rest,const WeightField& core,double amount,uint64_t cancel);
Vertices source_normals(const Mesh& rest,const AfTissueSource& source,uint64_t cancel);
V3 region_goal(const Mesh& rest,const Vertices& normals,const AfTissueRegion& region,int64_t index);
Constraints prepare_constraints(const Mesh& rest,const AfTissueSource& source,const AfTissueRelax& settings,const AfTissueRegion* regions,int count,uint64_t cancel);
Vertices relax_geometric(const Mesh& rest,const Constraints& constraints,const AfTissueSource& source,const AfTissueRelax& settings,double* report,uint64_t cancel);
Vertices relax_static(const Mesh& rest,const Constraints& constraints,const AfTissueRelax& settings,double* report,uint64_t cancel);
Vertices relax_point(const Mesh& rest,const Constraints& constraints,const AfTissueSource& source,const AfTissueRelax& settings,double* report,uint64_t cancel);
void apply_constraints(Vertices& points,const Constraints& constraints);
}
