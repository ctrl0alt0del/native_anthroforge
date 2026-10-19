/* Read-only accepted-path checks reuse the pinned addon collision kernels. */
#include "routing_internal.hpp"
#include "path_contacts.hpp"
#include "anthroforge/path_collisions.h"
#include <Eigen/LU>

namespace af::routing {
struct CheckedPath {
    std::vector<Vec> points;
    std::vector<double> lengths;
    std::map<int,PathContacts> contacts;
};
static void validate(const AfCollisionPath& input,int surfaces) {
    if(input.count<2||input.count>100000||!input.owners) throw std::runtime_error("Invalid collision path owners.");
    const M4 frame=Eigen::Map<const M4>(input.world);
    if(!frame.allFinite()||!frame.fullPivLu().isInvertible()) throw std::runtime_error("Invalid collision path frame.");
    for(int i=0;i<input.count;++i)
        if(input.owners[i]<0||input.owners[i]>surfaces) throw std::runtime_error("Invalid collision surface owner.");
}
static CheckedPath transformed_path(const Path& path,const M4& frame,uint64_t cancel) {
    CheckedPath result; const int count=int(path.parameters.size());
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const V3 p=point(frame,Eigen::Map<const V3>(path.samples.data()+i*11));
        result.points.push_back({p.x(),p.y(),p.z()});
    }
    for(int i=0;i<count-int(!path.closed);++i)
        result.lengths.push_back(kernel::norm(kernel::sub(result.points[(i+1)%count],result.points[i])));
    return result;
}
static void add_pins(CheckedPath& checked,const Path& path,const AfCollisionPath& input,double tolerance) {
    for(int i=0;i<input.count;++i) if(input.owners[i]) {
        const auto found=std::lower_bound(path.parameters.begin(),path.parameters.end(),double(i)-1e-9);
        if(found==path.parameters.end()||std::abs(*found-i)>1e-8)
            throw std::runtime_error("Accepted authored path is missing an attachment knot.");
        add_contact(checked.contacts[input.owners[i]],checked.lengths,int(found-path.parameters.begin()),8*tolerance,path.closed);
    }
}
static bool clear_interval(const kernel::AfInstance& surface,Vec a,Vec b,double low,double high,double tolerance) {
    const Vec delta=kernel::sub(b,a);
    a=kernel::add(a,kernel::mul(delta,low)); b=kernel::add(a,kernel::mul(delta,high-low));
    return kernel::af_instance_validation_row(surface,a,b,0,0,0,tolerance).clear!=0;
}
static int first_collision(const CheckedPath& path,const kernel::AfInstance& surface,double tolerance,uint64_t cancel) {
    const PathContacts empty; const auto found=path.contacts.find(surface.owner);
    const auto& contacts=found==path.contacts.end()?empty:found->second;
    for(int i=0;i<int(path.lengths.size());++i) {
        check_cancel(cancel); const Vec a=path.points[i],b=path.points[(i+1)%path.points.size()];
        for(const auto& [low,high]:tested_intervals(contacts,i))
            if(!clear_interval(surface,a,b,low,high,tolerance)) return i;
    }
    return -1;
}
static void check_path(const AfCollisionPath& input,const World& world,int* output,double tolerance,uint64_t cancel) {
    validate(input,int(world.collision->items.size()));
    const auto source=path(input.path);
    if(source->samples.size()!=source->parameters.size()*11) throw std::runtime_error("Invalid collision path samples.");
    auto checked=transformed_path(*source,Eigen::Map<const M4>(input.world),cancel);
    add_pins(checked,*source,input,tolerance);
    for(size_t i=0;i<world.collision->items.size();++i)
        output[i]=first_collision(checked,world.collision->items[i],tolerance,cancel);
}
}
int af_path_collisions(const AfCollisionPath* paths,int count,const uint64_t* meshes,
    const double* matrices,int surfaces,int* output,double* tolerance,uint64_t cancel) {
    try {
        if(count<0||surfaces<0||int64_t(count)*surfaces>1000000||!tolerance||(count&&(!paths||!output)))
            throw std::runtime_error("Collision batch exceeds one million path/surface pairs.");
        auto world=af::routing::capture_collision_world(meshes,matrices,surfaces,0,cancel);
        *tolerance=std::max(1e-9,1e-9*world.length);
        for(int i=0;i<count;++i) {
            af::check_cancel(cancel);
            af::routing::check_path(paths[i],world,output+i*surfaces,*tolerance,cancel);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
