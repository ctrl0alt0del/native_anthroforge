// SPDX-License-Identifier: GPL-3.0-or-later
#include "anthroforge/mesh_quality.h"
#include "mesh_quality.hpp"
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
static bool straddles(const Mesh& mesh,const Triangles& triangles,int plane,int face) {
    const auto a=triangles.row(plane),b=triangles.row(face);
    const V3 origin=mesh.vertices.row(a[0]),u=V3(mesh.vertices.row(a[1]))-origin,v=V3(mesh.vertices.row(a[2]))-origin;
    const V3 normal=u.cross(v).normalized();
    double lower=INFINITY,upper=-INFINITY,scale=origin.cwiseAbs().maxCoeff();
    for(int i=0;i<3;++i) {
        const V3 point=mesh.vertices.row(b[i]);
        const double distance=normal.dot(point-origin);
        lower=std::min(lower,distance); upper=std::max(upper,distance);
        scale=std::max(scale,point.cwiseAbs().maxCoeff());
    }
    const double tolerance=64*std::numeric_limits<double>::epsilon()*std::max(scale,1.);
    return lower < -tolerance&&upper > tolerance;
}
static std::set<std::pair<int,int>> crossings(const Mesh& mesh,const Triangles& triangles,uint64_t token,std::atomic<bool>& cancel) {
    const auto side=snapshot(mesh,triangles,token);
    auto result=layer::intersections(side,side,true,cancel);
    for(auto it=result.begin();it!=result.end();) {
        check_cancel(token);
        if(!straddles(mesh,triangles,it->first,it->second)||!straddles(mesh,triangles,it->second,it->first))
            it=result.erase(it);
        else ++it;
    }
    return result;
}
static void inspect(const Mesh& before,const Mesh& after,int64_t* counts,uint64_t token) {
    pair::require(before.vertices.rows()==after.vertices.rows()&&before.corners==after.corners&&before.offsets==after.offsets,
        "Deformation quality requires identical vertex and polygon identities.");
    std::fill(counts,counts+4,0); faces(before,after,counts,token);
    if(!before.triangles.rows()) return;
    std::atomic<bool> idle{false}; auto& cancel=token?reinterpret_cast<Cancellation*>(token)->cancelled:idle;
    const auto old=crossings(before,before.triangles,token,cancel),next=crossings(after,before.triangles,token,cancel);
    counts[0]=int64_t(old.size());
    for(auto crossing:next) if(!old.count(crossing)) ++counts[1];
}
void validate_tissue(const Mesh& before,const Mesh& after,uint64_t cancel) {
    pair::require(before.vertices.rows()==after.vertices.rows()&&before.corners==after.corners&&before.offsets==after.offsets,
        "Deformation quality requires identical vertex and polygon identities.");
    pair::require(after.vertices.allFinite(),"NUMERICAL_FAILURE: tissue deformation produced nonfinite coordinates.");
    int64_t counts[4]{}; faces(before,after,counts,cancel);
    if(counts[2]) throw std::runtime_error("Unusable deformation: "+std::to_string(counts[2])+
        " collapsed faces. Adjust thickness, relaxation or constraints; no geometry was accepted.");
}
void validate(const Mesh& before,const Mesh& after,uint64_t cancel) {
    int64_t counts[4]{}; inspect(before,after,counts,cancel);
    if(counts[1]||counts[2]) throw std::runtime_error(
        "Unusable deformation: "+std::to_string(counts[1])+" new self-intersections and "+
        std::to_string(counts[2])+" collapsed faces. Adjust thickness, relaxation or constraints; no geometry was accepted.");
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
        af::quality::validate(*af::mesh(rest),*af::mesh(result),cancel);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}


