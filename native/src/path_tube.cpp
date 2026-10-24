// Presentation-only tube geometry; never anatomical attachment or collision output.
#include "path_internal.hpp"
#include <numeric>

namespace af {
static Samples world_samples(const Path& path,const M4& frame,uint64_t cancel) {
    auto samples=read_samples(path.samples.data(),int(path.parameters.size()));
    for(auto& sample:samples) { check_cancel(cancel); sample.position=point(frame,sample.position); }
    curve_frames(samples,path.closed,cancel,true);
    return samples;
}
static void tube_ring(Points& points,const CurveSample& sample,double radius,int sides) {
    const V3 normal=sample.normal.normalized(),lateral=sample.tangent.cross(normal).normalized();
    for(int j=0;j<sides;++j) {
        const double angle=2*3.141592653589793*j/sides;
        points.push_back(sample.position+radius*(std::cos(angle)*normal+std::sin(angle)*lateral));
    }
}
static void tube_caps(Faces& faces,int count,int sides) {
    std::vector<int64_t> first(sides),last(sides);
    std::iota(first.rbegin(),first.rend(),0); std::iota(last.begin(),last.end(),(count-1)*sides);
    faces.push_back(first); faces.push_back(last);
}
static Faces tube_faces(int count,int sides,bool closed) {
    Faces faces;
    for(int i=0;i<count-int(!closed);++i) {
        const int next=(i+1)%count;
        for(int j=0;j<sides;++j) {
            const int after=(j+1)%sides;
            faces.push_back({i*sides+j,i*sides+after,next*sides+after,next*sides+j});
        }
    }
    if(!closed) tube_caps(faces,count,sides);
    return faces;
}
static std::shared_ptr<Mesh> path_tube(const Path& path,const M4& frame,double radius,int sides,uint64_t cancel) {
    if(!frame.allFinite()||!std::isfinite(radius)||radius<=0||sides<3||sides>64)
        throw std::runtime_error("Tube display requires a finite transform and positive radius.");
    if(path.parameters.size()*size_t(sides)>8000000) throw std::runtime_error("Tube display exceeds vertex budget.");
    const auto samples=world_samples(path,frame,cancel); Points points; points.reserve(samples.size()*sides);
    for(const auto& sample:samples) { check_cancel(cancel); tube_ring(points,sample,radius,sides); }
    return make_mesh(points,tube_faces(int(samples.size()),sides,path.closed),cancel);
}
}
uint64_t af_path_display_tube(uint64_t handle,const double* matrix,double radius,int sides,uint64_t cancel) {
    try {
        if(!matrix) throw std::runtime_error("Tube display needs a world transform.");
        return af::retain(af::path_tube(*af::path(handle),Eigen::Map<const af::M4>(matrix),radius,sides,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
