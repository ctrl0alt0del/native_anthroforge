#include "mesh_internal.hpp"
#include <stdexcept>

int af_surface_point(uint64_t handle,const double* matrix,int triangle,const double* weights,double* output) {
    try {
        const auto mesh=af::mesh(handle); const af::V3 bary=Eigen::Map<const af::V3>(weights);
        const af::M4 frame=Eigen::Map<const af::M4>(matrix);
        if(triangle<0||triangle>=mesh->triangles.rows()||!bary.allFinite()||!frame.allFinite()
            ||bary.minCoeff()<-1e-6||std::abs(bary.sum()-1)>1e-6)
            throw std::runtime_error("Invalid surface witness.");
        af::V3 local=af::V3::Zero();
        for(int i=0;i<3;++i) local+=bary[i]*mesh->vertices.row(mesh->triangles(triangle,i)).transpose();
        Eigen::Map<af::V3> result(output); result=af::point(frame,local);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_measure_points(const double* first,const double* second,double* output) {
    const af::V3 delta=Eigen::Map<const af::V3>(second)-Eigen::Map<const af::V3>(first);
    if(!delta.allFinite()) { af::set_error("Measurement coordinates must be finite."); return 1; }
    Eigen::Map<af::V3> result(output); result=delta; output[3]=delta.norm(); return 0;
}
