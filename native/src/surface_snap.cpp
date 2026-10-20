#include "mesh_internal.hpp"
#include <cmath>

namespace af {
V3 surface_normal(const Mesh& mesh,const M4& matrix,int triangle) {
    if(triangle<0||triangle>=mesh.triangles.rows()) throw std::runtime_error("Invalid surface triangle.");
    const auto face=mesh.triangles.row(triangle);
    const V3 a=mesh.vertices.row(face[1])-mesh.vertices.row(face[0]);
    const V3 b=mesh.vertices.row(face[2])-mesh.vertices.row(face[0]);
    const V3 normal=matrix.block<3,3>(0,0).inverse().transpose()*a.cross(b);
    if(!normal.allFinite()||normal.norm()==0) throw std::runtime_error("Degenerate surface normal.");
    return normal.normalized();
}
static double snap_margin(const Mesh& mesh,const M4& matrix,const V3& position) {
    const V3 low=Eigen::Map<const V3>(mesh.bounds),high=Eigen::Map<const V3>(mesh.bounds+3);
    const V3 extent=matrix.block<3,3>(0,0).cwiseAbs()*(high-low);
    const double scale=std::max({1.,position.cwiseAbs().maxCoeff(),extent.norm()});
    // Survive float-based curve adapters while staying below routing's contact floor.
    return 2*double(std::numeric_limits<float>::epsilon())*scale;
}
V3 surface_snap(const Mesh& mesh,const M4& matrix,int triangle,const V3& position,double offset) {
    if(!position.allFinite()||!std::isfinite(offset)) throw std::runtime_error("Invalid surface snap.");
    const V3 normal=surface_normal(mesh,matrix,triangle);
    V3 result=position+(std::max(0.,offset)+snap_margin(mesh,matrix,position))*normal;
    for(int axis=0;axis<3;++axis) if(normal[axis]!=0)
        result[axis]=std::nextafter(result[axis],std::copysign(INFINITY,normal[axis]));
    return result;
}
}
int af_surface_snap(uint64_t handle,const double* matrix,int triangle,const double* position,double offset,double* output) {
    try {
        const auto mesh=af::mesh(handle); const af::M4 frame=Eigen::Map<const af::M4>(matrix);
        const af::V3 start=Eigen::Map<const af::V3>(position);
        const af::V3 normal=af::surface_normal(*mesh,frame,triangle);
        Eigen::Map<af::V3> target(output),direction(output+3);
        target=af::surface_snap(*mesh,frame,triangle,start,offset); direction=normal;
        output[6]=(target-start).dot(normal); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
