#include "fiber_deformation.hpp"
#include "anthroforge/attachments.h"
#include <Eigen/SVD>
namespace af::fiber {
static bool same_topology(const Mesh& a,const Mesh& b) {
    return a.vertices.rows()==b.vertices.rows()&&a.triangles.rows()==b.triangles.rows()
        &&(a.triangles.array()==b.triangles.array()).all();
}
static Vertices current(const Parent& p,uint64_t handle,const M4& frame,uint64_t cancel) {
    const auto geometry=mesh(handle); Vertices result(p.indices.size(),3);
    if(same_topology(*p.mesh,*geometry)) {
        for(size_t i=0;i<p.indices.size();++i) result.row(int(i))=point(frame,geometry->vertices.row(p.indices[i]));
        return result;
    }
    std::vector<double> resolved(p.indices.size()*16);
    if(af_material_binding_frames(p.reference,handle,frame.data(),int(p.indices.size()),p.records.data(),resolved.data(),cancel))
        throw std::runtime_error(af_last_error());
    for(size_t i=0;i<p.indices.size();++i) result.row(int(i))=Eigen::Map<const M4>(resolved.data()+16*i).block<3,1>(0,3);
    return result;
}
static Map fit_region(const Region& patch,const Vertices& before,const Vertices& after) {
    V3 center=V3::Zero(); for(int i:patch.ids) center+=after.row(i); center/=double(patch.ids.size()); M3 cross=M3::Zero();
    for(int i:patch.ids) cross+=(after.row(i).transpose()-center)*(before.row(i).transpose()-patch.center).transpose();
    Eigen::JacobiSVD<M3> svd(cross,Eigen::ComputeFullU|Eigen::ComputeFullV);
    M3 sign=M3::Identity(); sign(2,2)=(svd.matrixU()*svd.matrixV().transpose()).determinant()<0?-1:1;
    const M3 rotation=svd.matrixU()*sign*svd.matrixV().transpose();
    const M3 linear=(cross+patch.ridge*rotation)*patch.inverse;
    return {linear,center-linear*patch.center};
}
std::vector<std::vector<Map>> fit(const Preparation& v,const uint64_t* meshes,const double* frames,uint64_t cancel) {
    std::vector<std::vector<Map>> result;
    for(size_t b=0;b<v.parents.size();++b) {
        check_cancel(cancel); const auto& parent=v.parents[b]; const M4 frame=Eigen::Map<const M4>(frames+16*b);
        if(parent.alias>=0) { result.push_back(result[size_t(parent.alias)]); continue; }
        if(!frame.allFinite()) throw std::runtime_error("Invalid fiber support transform.");
        const auto geometry=current(parent,meshes[b],frame,cancel); std::vector<Map> own;
        for(const auto& patch:parent.regions) own.push_back(fit_region(patch,parent.vertices,geometry));
        result.push_back(std::move(own));
    }
    return result;
}
}
