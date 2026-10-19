// SPDX-License-Identifier: GPL-3.0-or-later
#include "anthroforge/mesh_quality.h"
#include "stacking_internal.hpp"

namespace af::quality {
using namespace stacking;
static pair::Side snapshot(const Mesh& mesh,const Triangles& triangles,uint64_t cancel) {
    pair::Side result;
    for(int64_t i=0;i<mesh.vertices.rows();++i) {
        check_cancel(cancel); const auto p=mesh.vertices.row(i);
        result.base.push_back({p.x(),p.y(),p.z()});
    }
    result.own=result.base;
    result.faces.assign(triangles.data(),triangles.data()+triangles.size());
    pair::prepare_snapshot(result,nullptr); return result;
}
static void faces(const Mesh& before,const Mesh& after,int64_t* counts,uint64_t cancel) {
    for(int f=0;f<before.triangles.rows();++f) {
        check_cancel(cancel); V3 a[3],b[3];
        for(int j=0;j<3;++j) { const auto id=before.triangles(f,j); a[j]=before.vertices.row(id); b[j]=after.vertices.row(id); }
        const V3 first=(a[1]-a[0]).cross(a[2]-a[0]),second=(b[1]-b[0]).cross(b[2]-b[0]);
        if(first.norm()<=1e-14) continue;
        if(second.norm()<=1e-10*first.norm()) ++counts[2];
        else if(first.dot(second)<=0) ++counts[3];
    }
}
static void inspect(const Mesh& before,const Mesh& after,int64_t* counts,uint64_t token) {
    pair::require(before.vertices.rows()==after.vertices.rows()&&before.corners==after.corners&&before.offsets==after.offsets,
        "Deformation quality requires identical vertex and polygon identities.");
    std::fill(counts,counts+4,0); faces(before,after,counts,token);
    if(!before.triangles.rows()) return;
    auto first=snapshot(before,before.triangles,token),second=snapshot(after,before.triangles,token);
    std::atomic<bool> idle{false}; auto& cancel=token?reinterpret_cast<Cancellation*>(token)->cancelled:idle;
    const auto old=layer::intersections(first,first,true,cancel),next=layer::intersections(second,second,true,cancel);
    counts[0]=int64_t(old.size());
    for(auto crossing:next) if(!old.count(crossing)) ++counts[1];
}
}
int af_mesh_deformation_quality(uint64_t rest,uint64_t result,int64_t* counts,uint64_t cancel) {
    try {
        if(!counts) throw std::runtime_error("Missing deformation quality output.");
        af::quality::inspect(*af::mesh(rest),*af::mesh(result),counts,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_mesh_validate_deformation(uint64_t rest,uint64_t result,uint64_t cancel) {
    try {
        int64_t counts[4]{}; af::quality::inspect(*af::mesh(rest),*af::mesh(result),counts,cancel);
        if(counts[1]||counts[2]) throw std::runtime_error(
            "Unusable deformation: "+std::to_string(counts[1])+" new self-intersections and "+
            std::to_string(counts[2])+" collapsed faces. Adjust thickness, relaxation or constraints; no geometry was accepted.");
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
