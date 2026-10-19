// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_relaxation.hpp"

namespace af::tissue {
static WeightField mapped_field(const Mesh& mesh,const AfTissueRegion& region) {
    const auto& d=mesh.tissue; const auto count=region.domain==0?d.source_count:mesh.vertices.rows();
    if(!region.weights||region.count!=count) throw std::runtime_error("Custom region field no longer matches its material domain.");
    for(int64_t i=0;i<count;++i) if(!std::isfinite(region.weights[i])||region.weights[i]<0||region.weights[i]>1)
        throw std::runtime_error("Region weights must be finite and normalized.");
    if(region.domain==1) return {region.weights,region.weights+count};
    WeightField result(size_t(mesh.vertices.rows()),0);
    for(size_t i=0;i<result.size();++i) for(auto j=d.offsets[i];j<d.offsets[i+1];++j)
        result[i]+=region.weights[d.indices[size_t(j)]]*d.weights[size_t(j)];
    return result;
}
static WeightField mapped_boundary(const Mesh& mesh,const Mesh* base,uint64_t cancel) {
    if(!base||(mesh.tissue.kind!=3&&mesh.tissue.kind!=4&&mesh.tissue.kind!=5))
        throw std::runtime_error("Boundary regions require a surface-based tissue.");
    const auto edges=boundary_topology(mesh_faces(*base),cancel); WeightField field(size_t(base->vertices.rows()),0);
    for(const auto& pair:edges) if(pair.second.count==1) field[size_t(pair.first.first)]=field[size_t(pair.first.second)]=1;
    AfTissueRegion region{}; region.weights=field.data(); region.count=int64_t(field.size());
    return mapped_field(mesh,region);
}
static WeightField backing(const Mesh& mesh) {
    const auto& d=mesh.tissue; WeightField result(d.sides.size(),0);
    if(d.kind!=2&&d.kind!=3) throw std::runtime_error("This construction does not provide a backing region.");
    for(size_t i=0;i<result.size();++i) result[i]=(d.kind==3?d.sides[i]==2:d.sides[i]==0)?1:0;
    return result;
}
static WeightField endpoints(const Mesh& mesh) {
    const auto& d=mesh.tissue; WeightField result(d.sides.size(),0);
    if(d.kind!=2||d.ring_size<3) throw std::runtime_error("Endpoint regions require a profile sweep.");
    if(!d.closed) for(size_t i=0;i<size_t(d.ring_size);++i) result[i]=result[result.size()-1-i]=1;
    return result;
}
static WeightField suspension(const Mesh& mesh,const AfTissueRelax& s) {
    const auto& d=mesh.tissue; WeightField result(d.sides.size(),0); std::vector<size_t> choices;
    if(d.kind!=3) throw std::runtime_error("Suspension regions require a normal shell.");
    for(int64_t i=0;i<d.source_count;++i) {
        const double thickness=(mesh.vertices.row(i)-mesh.vertices.row(i+d.source_count)).norm();
        const double weight=s.amount>s.minimum?std::pow(std::clamp((thickness-s.minimum)/(s.amount-s.minimum),0.,1.),1/s.power):0;
        if(weight>=.45&&weight<=.75) choices.push_back(size_t(i));
    }
    const auto step=std::max(size_t(1),choices.size()/9);
    for(size_t i=0,n=0;i<choices.size()&&n<9;i+=step,++n) result[choices[i]]=1;
    return result;
}
WeightField region_mask(const Mesh& rest,const Mesh* base,const AfTissueRelax& settings,const AfTissueRegion& region,uint64_t cancel) {
    switch(region.mask) {
        case 0:return WeightField(size_t(rest.vertices.rows()),1);
        case 1:return backing(rest);
        case 2:return mapped_boundary(rest,base,cancel);
        case 3:return endpoints(rest);
        case 4:return suspension(rest,settings);
        case 5:return mapped_field(rest,region);
        default:throw std::runtime_error("Unknown tissue region mask.");
    }
}
static double scale(const Mesh& rest) {
    Eigen::AlignedBox3d bounds; const auto& d=rest.tissue;
    for(int64_t i=0;i<rest.vertices.rows();++i)
        if((d.kind==3&&d.sides[size_t(i)]==2)||(d.kind==2&&d.sides[size_t(i)]==0)||(d.kind!=2&&d.kind!=3))
            bounds.extend(V3(rest.vertices.row(i)));
    return bounds.diagonal().norm();
}
WeightField feather(const Mesh& rest,const WeightField& core,double amount,uint64_t cancel) {
    const double width=std::clamp(amount,0.,1.)*scale(rest);
    if(width<=1e-12) return core;
    const auto distances=mask_distances(rest,mesh_edges(mesh_faces(rest),cancel),core,cancel);
    WeightField values=core;
    for(size_t i=0;i<values.size();++i) if(!core[i]) {
        const double x=std::clamp(1-distances[i]/width,0.,1.); values[i]=x*x*(3-2*x);
    }
    return values;
}
}
