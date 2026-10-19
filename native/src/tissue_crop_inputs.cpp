// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_crop.hpp"

namespace af::tissue {
static MaterialRow material_row(const TissueDomain& d,int64_t index) {
    MaterialRow row;
    for(auto k=d.offsets[size_t(index)];k<d.offsets[size_t(index+1)];++k)
        row[d.indices[size_t(k)]]+=d.weights[size_t(k)];
    return row;
}
static V3 plane_normal(const double* plane) {
    if(!plane) throw std::runtime_error("Missing material crop plane.");
    const V3 normal(plane+3),origin(plane);
    if(!normal.allFinite()||!origin.allFinite()||normal.norm()<1e-12||!std::isfinite(plane[6]))
        throw std::runtime_error("Material crop needs a finite plane and nonzero normal.");
    return normal.normalized()*(plane[6]?1.0:-1.0);
}
CropState crop_inputs(const Mesh& base,const Mesh& own,const double* plane,uint64_t cancel) {
    const auto& domain=own.tissue; const auto normal=plane_normal(plane); CropState s;
    if((domain.kind!=4&&domain.kind!=5)||domain.source_count!=base.vertices.rows())
        throw std::runtime_error("Material crop requires muscle grid inflation and its accepted base.");
    for(int64_t i=0;i<own.vertices.rows();++i) {
        check_cancel(cancel); auto row=material_row(domain,i); V3 point=V3::Zero();
        for(const auto& [index,weight]:row) point+=weight*V3(base.vertices.row(index));
        const double distance=normal.dot(point-V3(plane));
        s.base.push_back(point); s.own.push_back(own.vertices.row(i)); s.material.push_back(std::move(row));
        s.distances.push_back(std::abs(distance)<=1e-10?0:distance);
    }
    s.sides=domain.sides; return s;
}
static void append(CropState& output,const CropState& source,size_t index) {
    output.own.push_back(source.own[index]); output.material.push_back(source.material[index]);
    output.sides.push_back(source.sides[index]);
}
static CropState compact(const CropState& source,uint64_t cancel) {
    std::vector<int64_t> mapping(source.own.size(),-1); CropState output;
    for(const auto& face:source.faces) for(const auto index:face) mapping[size_t(index)]=0;
    for(size_t i=0;i<mapping.size();++i) if(mapping[i]==0) {
        check_cancel(cancel); mapping[i]=int64_t(output.own.size()); append(output,source,i);
    }
    output.faces=source.faces;
    for(auto& face:output.faces) for(auto& index:face) index=mapping[size_t(index)];
    output.parts=source.parts; output.sources=source.sources; return output;
}
static TissueDomain correspondence(const CropState& s,const TissueDomain& source) {
    TissueDomain d; d.kind=source.kind; d.source_count=source.source_count; d.offsets={0};
    for(const auto& row:s.material) {
        for(const auto& [index,weight]:row) if(weight>0) { d.indices.push_back(index); d.weights.push_back(weight); }
        d.offsets.push_back(int64_t(d.indices.size()));
    }
    d.sides=s.sides; d.parts=s.parts; d.faces=s.sources; return d;
}
std::shared_ptr<Mesh> crop_output(const CropState& state,const TissueDomain& source,uint64_t cancel) {
    const auto result=compact(state,cancel); auto mesh=make_mesh(result.own,result.faces,cancel,true);
    mesh->tissue=correspondence(result,source);
    tissue_validate(mesh->tissue,mesh->vertices.rows(),int64_t(mesh->offsets.size())-1); return mesh;
}
}
