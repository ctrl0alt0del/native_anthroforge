// SPDX-License-Identifier: GPL-3.0-or-later
#include "material_binding.hpp"
#include "anthroforge/attachments.h"
#include <set>

namespace af::binding {
static std::set<int64_t> required(const Mesh& reference,int count,const double* records) {
    if(count<0||(count&&!records)) throw std::runtime_error("Invalid retained attachment records.");
    std::set<int64_t> result;
    for(int row=0;row<count;++row) for(int start:{0,6}) for(int j=0;j<3;++j) {
        const double value=records[28*row+start+j];
        if(value<0&&start==6) continue;
        if(!std::isfinite(value)||std::floor(value)!=value||value<0||value>=reference.vertices.rows())
            throw std::runtime_error("Invalid retained attachment vertex identity.");
        result.insert(int64_t(value));
    }
    return result;
}
static void validate_locations(const Mesh& reference,const Index& current,int count,const double* records,uint64_t cancel) {
    for(int row=0;row<count;++row) for(int start:{0,6}) {
        const auto* r=records+28*row+start; if(r[0]<0) continue;
        Weights location; int64_t side=0;
        for(int j=0;j<3;++j) {
            const auto vertex=int64_t(r[j]); side=std::max(side,reference.tissue.sides[size_t(vertex)]);
            for(const auto& [key,value]:weights(reference.tissue,vertex)) location[key]+=value*r[j+3];
        }
        material_point(current,location,side,cancel);
    }
}
static std::shared_ptr<Mesh> material(const Mesh& reference,const Mesh& current,const std::set<int64_t>& used,int count,const double* records,uint64_t cancel) {
    const auto& before=reference.tissue; const auto& after=current.tissue;
    if(before.kind!=after.kind||before.source_count!=after.source_count)
        throw std::runtime_error("Tissue material domain changed; explicitly rebind.");
    const auto current_index=index(current,cancel); Vertices points=reference.vertices;
    validate_locations(reference,current_index,count,records,cancel);
    for(auto i:used) points.row(i)=material_point(current_index,weights(before,i),before.sides[size_t(i)],cancel,false);
    return deform_mesh(reference,points,cancel,false);
}
static std::shared_ptr<Mesh> adapt(const Mesh& reference,const Mesh& current,int count,const double* records,uint64_t cancel) {
    const auto used=required(reference,count,records);
    const auto& before=reference.tissue; const auto& after=current.tissue;
    if(before.kind!=after.kind) throw std::runtime_error("Anatomical material domain changed; explicitly rebind.");
    if(before.kind<3) {
        if(reference.vertices.rows()!=current.vertices.rows()||reference.corners!=current.corners||reference.offsets!=current.offsets)
            throw std::runtime_error("Anatomical surface topology changed; explicitly rebind.");
        return deform_mesh(reference,current.vertices,cancel,false);
    }
    return material(reference,current,used,count,records,cancel);
}
}
uint64_t af_material_binding_surface(uint64_t reference,uint64_t current,int count,const double* records,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto before=af::mesh(reference),after=af::mesh(current);
        return af::retain(af::binding::adapt(*before,*after,count,records,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
