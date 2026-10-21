#include "painting_internal.hpp"
#include <Eigen/LU>
namespace af::painting {
View view(const double* values) {
    View camera{V3(values),V3(values+3),V3(values+6),V3(values+9),values[12],values[13]!=0};
    if(!camera.origin.allFinite()||!camera.right.allFinite()||!camera.up.allFinite()||!camera.forward.allFinite()
        ||!std::isfinite(camera.scale)||camera.scale<=0) throw std::runtime_error("Invalid paint camera.");
    const auto& r=camera.right; const auto& u=camera.up; const auto& f=camera.forward;
    if(std::abs(r.norm()-1)>1e-6||std::abs(u.norm()-1)>1e-6||std::abs(f.norm()-1)>1e-6
        ||std::abs(r.dot(u))+std::abs(r.dot(f))+std::abs(u.dot(f))>1e-6)
        throw std::runtime_error("Paint camera axes must be orthonormal.");
    return camera;
}
static bool visible(const V3& world,const View& camera,const std::vector<Occluder>& occluders) {
    const double depth=(world-camera.origin).dot(camera.forward);
    if(depth<=1e-9) return false;
    const V3 start=camera.perspective?camera.origin:V3(world-camera.forward*depth);
    for(const auto& obstacle:occluders) {
        const V3 local=point(obstacle.inverse,start),end=point(obstacle.inverse,world); RayHit hit;
        if(intersect_ray(*obstacle.geometry,local,end-local,hit)&&hit.t<1-1e-7) return false;
    }
    return true;
}
void project(Prepared& out,const M4& frame,const View& camera,const std::vector<Occluder>& occluders,uint64_t cancel) {
    out.projected.resize(out.target->vertices.rows(),3); out.visible.resize(size_t(out.projected.rows()));
    for(int64_t i=0;i<out.projected.rows();++i) {
        check_cancel(cancel); const V3 world=point(frame,out.target->vertices.row(i)),delta=world-camera.origin;
        const double depth=delta.dot(camera.forward),scale=camera.scale/(camera.perspective?std::max(depth,1e-9):1);
        out.projected.row(i)<<delta.dot(camera.right)*scale,delta.dot(camera.up)*scale,depth;
        out.visible[size_t(i)]=uint8_t(visible(world,camera,occluders));
    }
}
}
