#include "skin_symmetry.hpp"
#include "anthroforge/skin_symmetry.h"
namespace af::skin_symmetry {
static double diagonal(const Quads& mesh) {
    Eigen::AlignedBox3d box; for(const auto& point:mesh.points) box.extend(point);
    const double value=box.diagonal().norm();
    if(!std::isfinite(value)||value<=0) throw std::runtime_error("Skin symmetry requires nonzero finite bounds.");
    return value;
}
static double distance(const V3& point,const Plane& plane) { return (point-plane.origin).dot(plane.normal); }
static void snap(Quads& mesh,const Plane& plane,double diagonal,uint64_t cancel) {
    std::set<int64_t> boundary;
    for(const auto& edge:skin_stitch::boundary(mesh.faces)) { boundary.insert(edge.first); boundary.insert(edge.second); }
    for(size_t i=0;i<mesh.points.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        const double value=distance(mesh.points[i],plane);
        if(value>0||(boundary.count(int64_t(i))&&std::abs(value)<.02*diagonal)) mesh.points[i]-=value*plane.normal;
    }
}
static Quads exterior(Quads source,const Plane& plane,double tolerance,uint64_t cancel) {
    Quads result; result.points=std::move(source.points);
    for(size_t i=0;i<source.faces.size();++i) {
        if(i%4096==0) check_cancel(cancel); double maximum=0;
        for(const auto id:source.faces[i]) maximum=std::max(maximum,std::abs(distance(result.points[id],plane)));
        if(maximum<=tolerance) continue;
        result.faces.push_back(source.faces[i]); result.regions.push_back(source.regions[i]); result.guides.push_back(source.guides[i]);
    }
    if(result.faces.empty()) throw std::runtime_error("Skin symmetry leaves only internal cut-plane faces.");
    return result;
}
Quads mirror(Quads source,const Plane& plane,uint64_t cancel) {
    const double extent=diagonal(source); snap(source,plane,extent,cancel);
    source=exterior(std::move(source),plane,1e-6*extent,cancel); auto reflected=source;
    for(size_t i=0;i<reflected.points.size();++i) {
        if(i%4096==0) check_cancel(cancel);
        reflected.points[i]-=2*distance(reflected.points[i],plane)*plane.normal;
    }
    for(auto& face:reflected.faces) std::reverse(face.begin(),face.end());
    return skin_stitch::weld({source,reflected},1e-6*extent,false,cancel);
}
static Plane required(const double* value) {
    const auto result=skin_loops::plane(value);
    if(!result.enabled) throw std::runtime_error("Skin symmetry requires an explicit plane.");
    return result;
}
}
uint64_t af_skin_symmetry_half(uint64_t mesh,const double* plane,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto source=af::mesh(mesh);
        return af::retain(af::skin_symmetry::half(*source,af::skin_symmetry::required(plane),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_skin_symmetry_mirror(uint64_t mesh,const double* plane,uint64_t cancel) {
    try {
        af::check_cancel(cancel); const auto source=af::mesh(mesh); const size_t count=source->offsets.size()-1;
        std::vector<int> regions(count,0),guides(count,-1);
        auto quads=af::skin_quads::capture(*source,regions.data(),guides.data(),cancel);
        auto result=af::skin_symmetry::mirror(std::move(quads),af::skin_symmetry::required(plane),cancel);
        return af::skin_quads::retain(af::skin_quads::complete(std::move(result),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
