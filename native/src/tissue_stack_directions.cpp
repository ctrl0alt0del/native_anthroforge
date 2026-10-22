// SPDX-License-Identifier: GPL-3.0-or-later
// Limiting fields port core/muscle_pairs/field.py and pair_detection/field.hpp.
#include "tissue_stacking.hpp"
#include "tissue_branches.hpp"
#include "tissue_profile.hpp"
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunused-function"
#endif
#include "tissue_kernel.hpp"
#if defined(__clang__)
#pragma clang diagnostic pop
#endif

namespace af::tissue::stacking {
static std::vector<kernel::Vec> points(const Mesh& mesh,const MaterialGrid& grid) {
    std::vector<kernel::Vec> result;
    for(auto index:grid.indices) { const V3 p=mesh.vertices.row(index); result.push_back({p.x(),p.y(),p.z()}); }
    return result;
}
static std::vector<kernel::Vec> profile(const std::vector<kernel::Vec>& base,const MaterialGrid& grid,const AfTissueInflation& s,int sign) {
    std::vector<double> areas;
    auto result=section_directions(base,grid.rows,grid.columns,s.direction,areas);
    for(auto& value:result) value=kernel::mul(kernel::af_env_unit(value),sign);
    return result;
}
static std::vector<kernel::Vec> directions(const Mesh& mesh,const MaterialGrid& grid,const AfTissueInflation& s) {
    validate_inflation(s,grid); const auto base=points(mesh,grid);
    if(!s.enabled) return std::vector<kernel::Vec>(base.size());
    const int sign=(bool(s.reverse)!=grid_reversed(mesh,grid))?-1:1;
    if(s.mode==2) return profile(base,grid,s,sign);
    auto result=kernel::af_muscle_normals(base,grid.rows,grid.columns,s.mode==1);
    const auto control=s.initialize_control?base[size_t((grid.rows/2)*grid.columns+grid.columns/2)]:kernel::af_vec(s.control);
    const auto n0=result[kernel::af_muscle_closest(base,control)],center=kernel::sub(control,kernel::mul(n0,s.depth*sign));
    for(size_t i=0;i<result.size();++i) {
        const auto d=s.mode==1?kernel::mul(result[i],sign):kernel::sub(base[i],center);
        result[i]=kernel::af_env_unit(kernel::norm(d)>1e-12?d:kernel::mul(n0,sign));
    }
    return result;
}
static void accumulate(Vertices& result,std::vector<int>& counts,const MaterialGrid& grid,const std::vector<kernel::Vec>& values) {
    for(size_t i=0;i<grid.indices.size();++i) {
        const auto index=grid.indices[i]; const auto v=values[i];
        result.row(index)+=V3(v.x,v.y,v.z); ++counts[size_t(index)];
    }
}
Vertices limiting(const Mesh& base,const AfTissueStackSource& config,uint64_t cancel) {
    if(mesh(config.own)->tissue.kind==3) {
        auto normals=surface_normals(base,mesh_faces(base),cancel);
        return normals*(config.reverse?-1:1);
    }
    const kernel::CancelScope scope(cancel); const auto grids=material_grids(base);
    if(grids.size()!=size_t(config.parts)) throw std::runtime_error("Stacking part settings must match accepted material parts.");
    Vertices result=Vertices::Zero(base.vertices.rows(),3); std::vector<int> counts(size_t(result.rows()),0);
    for(size_t i=0;i<grids.size();++i) accumulate(result,counts,grids[i],directions(base,grids[i],config.inflation[i]));
    for(int64_t i=0;i<result.rows();++i) if(counts[size_t(i)]) result.row(i)/=counts[size_t(i)];
    return result;
}
}
