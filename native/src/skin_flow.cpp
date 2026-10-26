#include "mesh_internal.hpp"
#include "anthroforge/skin_flow.h"
#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4456 4267)
#endif
#include "../migration/topology/field.hpp"
#ifdef _MSC_VER
#pragma warning(pop)
#endif

namespace af::skin_flow {
struct Samples { std::vector<double> points,directions,normals; std::vector<int> owners; };
static Samples unpack(const double* data,int count,uint64_t cancel) {
    if(count<0 || (count && !data)) throw std::runtime_error("Invalid FLOW samples.");
    Samples result; result.owners.resize(count);
    for(auto* values:{&result.points,&result.directions,&result.normals}) values->resize(3LL*count);
    for(int i=0;i<count;++i) {
        if(i%4096==0) af::check_cancel(cancel);
        for(int j=0;j<10;++j) if(!std::isfinite(data[10LL*i+j])) throw std::runtime_error("Nonfinite FLOW sample.");
        const double owner=data[10LL*i+9];
        if(owner<0 || owner>INT_MAX || owner!=std::floor(owner)) throw std::runtime_error("Invalid FLOW owner.");
        result.owners[i]=int(owner);
        for(int j=0;j<3;++j) { result.points[3LL*i+j]=data[10LL*i+j];
            result.directions[3LL*i+j]=data[10LL*i+3+j]; result.normals[3LL*i+j]=data[10LL*i+6+j]; }
    }
    return result;
}
static void validate(const Mesh& mesh,const double* prior) {
    if(!prior || !mesh.triangles.rows()) throw std::runtime_error("FLOW requires a prior triangle field.");
    for(int i=0;i<mesh.triangles.rows();++i) {
        const V3 a=mesh.vertices.row(mesh.triangles(i,0)), b=mesh.vertices.row(mesh.triangles(i,1));
        const V3 c=mesh.vertices.row(mesh.triangles(i,2)), p=V3(prior+3LL*i);
        if(!p.allFinite() || (b-a).cross(c-a).squaredNorm()<=1e-30)
            throw std::runtime_error("FLOW requires finite priors and nondegenerate triangles.");
    }
}
static void solve(const Mesh& mesh,const double* prior,const Samples& s,double* out,double* info,uint64_t token) {
    const V3 extent=mesh.vertices.colwise().maxCoeff()-mesh.vertices.colwise().minCoeff();
    cancellation=token; af::check_cancel(token);
    const int result=af_field(mesh.vertices.data(),mesh.triangles.data(),int(mesh.triangles.rows()),prior,
        s.points.data(),s.directions.data(),s.normals.data(),s.owners.data(),int(s.owners.size()),
        std::max(extent.maxCoeff()*.035,1e-10),1,out,info);
    af::check_cancel(token);
    if(!result) throw std::runtime_error("Native topology FLOW failed.");
    for(int64_t i=0;i<3LL*mesh.triangles.rows();++i)
        if(!std::isfinite(out[i])||!std::isfinite(info[i])) throw std::runtime_error("Nonfinite FLOW result.");
}
}
int af_skin_flow(uint64_t handle,const double* prior,const double* samples,int count,
                 double* output,double* information,uint64_t cancel) {
    try {
        if(!output||!information) throw std::runtime_error("Missing FLOW output buffers.");
        const auto mesh=af::mesh(handle); af::skin_flow::validate(*mesh,prior);
        const auto inputs=af::skin_flow::unpack(samples,count,cancel);
        af::skin_flow::solve(*mesh,prior,inputs,output,information,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
