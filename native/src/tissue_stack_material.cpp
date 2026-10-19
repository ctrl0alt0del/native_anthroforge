// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_stacking.hpp"
#include "tissue_envelope.hpp"
#include <set>

namespace af::tissue::stacking {
Row row(const TissueDomain& domain,size_t index) {
    Row result;
    for(auto k=domain.offsets.at(index);k<domain.offsets.at(index+1);++k)
        result[domain.indices[size_t(k)]]+=domain.weights[size_t(k)];
    return result;
}
std::shared_ptr<Mesh> visible_material(const Mesh& base,const Mesh& rest,const AfTissueStackSource& config,uint64_t cancel) {
    auto result=deform_mesh(base,base.vertices,cancel,false);
    auto& d=result->tissue; d=tissue_identity(4,base.vertices.rows(),int64_t(base.offsets.size())-1);
    for(size_t i=0;i<rest.tissue.faces.size();++i) {
        const auto face=rest.tissue.faces[i];
        if(face>=0) d.parts.at(size_t(face))=rest.tissue.parts[i];
    }
    if(config.cropped) result=crop_material(base,*result,config.crop,cancel);
    return result;
}
static std::map<Row,V3> indexed_side(const Mesh& own,int side,uint64_t cancel) {
    std::map<Row,V3> result;
    for(size_t i=0;i<own.tissue.sides.size();++i) {
        check_cancel(cancel); const auto s=own.tissue.sides[i];
        if(s==0||s==side) result.emplace(row(own.tissue,i),own.vertices.row(int64_t(i)));
    }
    return result;
}
Vertices resolved_side(const Mesh& material,const Mesh& own,int side,uint64_t cancel) {
    const auto values=indexed_side(own,side,cancel),first=indexed_side(own,1,cancel);
    Vertices result(material.vertices.rows(),3);
    for(int64_t i=0;i<result.rows();++i) {
        check_cancel(cancel); const auto key=row(material.tissue,size_t(i)); const auto found=values.find(key);
        if(found!=values.end()) result.row(i)=found->second;
        else if(own.tissue.kind==5&&side==2&&first.count(key)) result.row(i)=first.at(key);
        else throw std::runtime_error("Stacking material correspondence is unavailable; reevaluate intrinsic tissue.");
    }
    return result;
}
std::vector<int64_t> triangles(const Mesh& mesh) {
    std::vector<int64_t> output;
    for(const auto& face:mesh_faces(mesh)) for(size_t i=1;i+1<face.size();++i)
        output.insert(output.end(),{face[0],face[i],face[i+1]});
    return output;
}
void append_row(const Row& row,std::vector<int64_t>& indices,std::vector<double>& weights) {
    if(row.empty()||row.size()>4) throw std::runtime_error("Stacking requires at most four exact material weights per sample.");
    for(const auto& [index,weight]:row) { indices.push_back(index); weights.push_back(weight); }
    for(size_t i=row.size();i<4;++i) { indices.push_back(row.begin()->first); weights.push_back(0); }
}
void pack_material(Prepared& output,uint64_t cancel) {
    output.material=output.base->vertices;
    for(int64_t i=0;i<output.material.rows();++i) {
        check_cancel(cancel); output.material.row(i)=point(output.frame,output.base->vertices.row(i));
    }
    output.material_faces=triangles(*output.base);
    for(auto index:output.selected) append_row(row(output.visible->tissue,size_t(index)),output.interpolation,output.weights);
}
}
