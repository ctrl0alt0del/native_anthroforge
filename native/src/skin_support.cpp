#include "anthroforge/skin_support.h"
#include "skin_deformation.hpp"
#include "material_binding.hpp"

namespace af::skin::support {
static M4 frame(const double* input) {
    if(!input) throw std::runtime_error("Missing skin support frame.");
    const M4 value=Eigen::Map<const M4>(input);
    if(!value.allFinite()||std::abs(value.block<3,3>(0,0).determinant())<1e-18)
        throw std::runtime_error("Skin support frame must be finite and nonsingular.");
    return value;
}
static Vertices world(const Mesh& mesh,const M4& frame,uint64_t cancel) {
    Vertices result(mesh.vertices.rows(),3);
    for(int i=0;i<result.rows();++i) {
        if(i%4096==0) check_cancel(cancel);
        result.row(i)=point(frame,mesh.vertices.row(i));
    }
    return result;
}
static std::vector<double> masses(const Mesh& mesh,const Vertices& xyz,uint64_t cancel) {
    std::vector<double> mass(size_t(xyz.rows()),0);
    for(size_t f=1;f<mesh.offsets.size();++f) {
        check_cancel(cancel); const auto begin=mesh.offsets[f-1],end=mesh.offsets[f];
        for(auto k=begin+1;k+1<end;++k) {
            const auto a=mesh.corners[begin],b=mesh.corners[k],c=mesh.corners[k+1];
            const V3 u=xyz.row(b)-xyz.row(a),v=xyz.row(c)-xyz.row(a);
            const double area=u.cross(v).norm()/6; mass[a]+=area; mass[b]+=area; mass[c]+=area;
        }
    }
    return mass;
}
static void validate(const Mesh& before,const Mesh& after,const int* ids,int count) {
    if(!ids||count<1||count>80) throw std::runtime_error("Invalid retained skin support samples.");
    if(before.tissue.kind!=after.tissue.kind||before.tissue.source_count!=after.tissue.source_count)
        throw std::runtime_error("Skin support material identity changed; rebuild the reference.");
    if(before.tissue.kind<3&&(before.vertices.rows()!=after.vertices.rows()||before.corners!=after.corners||before.offsets!=after.offsets))
        throw std::runtime_error("Skin support topology changed; rebuild the reference.");
    for(int i=0;i<count;++i) if(ids[i]<0||ids[i]>=before.vertices.rows())
        throw std::runtime_error("Skin support sample identity is unavailable.");
}
static V3 position(const Mesh& before,const binding::Index& after,int id,uint64_t cancel) {
    if(&before==&after.current||before.tissue.kind<3) return after.current.vertices.row(id);
    return binding::material_point(after,binding::weights(before.tissue,id),before.tissue.sides.at(id),cancel);
}
static void targets(const Mesh& before,const Mesh& after,const M4& frame,const int* ids,int count,double* out,uint64_t cancel) {
    validate(before,after,ids,count);
    const auto index=before.tissue.kind<3||&before==&after?binding::Index{after,{},{}}:binding::index(after,cancel);
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const V3 value=point(frame,position(before,index,ids[i],cancel));
        if(!value.allFinite()) throw std::runtime_error("Nonfinite skin support target.");
        Eigen::Map<V3>(out+3*i)=value;
    }
}
static double total(const double* masses,const int* counts,int sources,int count) {
    double mass=0; int size=0;
    for(int i=0;i<sources;++i) {
        if(!std::isfinite(masses[i])||masses[i]<=0||counts[i]<1||counts[i]>80)
            throw std::runtime_error("Invalid skin support sampling mass.");
        mass+=masses[i]; size+=counts[i];
    }
    if(size!=count||!std::isfinite(mass)||mass<=0) throw std::runtime_error("Invalid total skin support mass.");
    return mass;
}
}
int af_skin_support_sample(uint64_t handle,const double* matrix,int* ids,double* out,double* mass,uint64_t cancel) {
    try {
        if(!ids||!out||!mass) throw std::runtime_error("Missing skin support buffers.");
        const auto mesh=af::mesh(handle); const auto frame=af::skin::support::frame(matrix);
        const auto xyz=af::skin::support::world(*mesh,frame,cancel);
        const int count=af::skin::deformation::select(af::skin::support::masses(*mesh,xyz,cancel),ids,mass);
        for(int i=0;i<count;++i) Eigen::Map<af::V3>(out+3*i)=xyz.row(ids[i]);
        return count;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
int af_skin_support_targets(uint64_t reference,uint64_t current,const double* matrix,const int* ids,int count,double* out,uint64_t cancel) {
    try {
        if(!out) throw std::runtime_error("Missing skin support output.");
        const auto before=af::mesh(reference),after=af::mesh(current);
        af::skin::support::targets(*before,*after,af::skin::support::frame(matrix),ids,count,out,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_support_weights(const double* masses,const int* counts,int sources,double* weights,int count) {
    try {
        if(!masses||!counts||!weights||sources<1) throw std::runtime_error("Missing skin support weights.");
        const double total=af::skin::support::total(masses,counts,sources,count); int offset=0;
        for(int i=0;i<sources;++i) for(int j=0;j<counts[i];++j) weights[offset++]=masses[i]/counts[i]/total;
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_reference_replay(const double* reference,const double* replay,int count,double* error) {
    try {
        if(!reference||!replay||!error||count<1) throw std::runtime_error("Missing skin replay buffers.");
        const Eigen::Map<const af::Vertices> a(reference,count,3),b(replay,count,3);
        if(!a.allFinite()||!b.allFinite()) throw std::runtime_error("Nonfinite skin reference replay.");
        const double extent=std::max(1e-12,(a.colwise().maxCoeff()-a.colwise().minCoeff()).maxCoeff());
        *error=(a-b).rowwise().norm().maxCoeff();
        if(*error>extent*1e-6) throw std::runtime_error("Skin reference identity replay exceeded tolerance.");
        return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
