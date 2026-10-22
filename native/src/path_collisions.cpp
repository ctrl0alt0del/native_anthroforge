/* Read-only accepted-path checks reuse the pinned addon collision kernels. */
#include "routing_internal.hpp"
#include "path_contacts.hpp"
#include "path_collision_cache.hpp"
#include "anthroforge/path_collisions.h"
#include <Eigen/LU>

namespace af::routing {
struct CheckedPath {
    std::vector<Vec> points;
    std::vector<double> lengths;
    std::map<int,PathContacts> contacts;
    kernel::Bounds bounds=kernel::empty_bounds();
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
        for(int axis=0;axis<3;++axis) {
            result.bounds.lo[axis]=std::min(result.bounds.lo[axis],p[axis]);
            result.bounds.hi[axis]=std::max(result.bounds.hi[axis],p[axis]);
        }
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
    for(int a=0;a<3;++a)
        if(path.bounds.hi[a]<surface.bounds.lo[a]-tolerance||path.bounds.lo[a]>surface.bounds.hi[a]+tolerance) return -1;
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
static void reuse_row(const CollisionCache& cache,const std::string& key,const std::vector<int>& indices,int* output) {
    const auto found=cache.rows.find(key);
    for(size_t i=0;i<indices.size();++i)
        output[i]=found==cache.rows.end()||indices[i]<0?-2:found->second[indices[i]];
}
static void missing_pairs(const AfCollisionPath& input,const World& world,int* output,double tolerance,uint64_t* stats,uint64_t cancel) {
    const auto size=world.collision->items.size();
    const auto count=std::count(output,output+size,-2); stats[0]+=size-count; stats[1]+=count;
    if(!count) return;
    const auto source=path(input.path);
    if(source->samples.size()!=source->parameters.size()*11) throw std::runtime_error("Invalid collision path samples.");
    auto checked=transformed_path(*source,Eigen::Map<const M4>(input.world),cancel);
    add_pins(checked,*source,input,tolerance);
    for(size_t i=0;i<size;++i) if(output[i]==-2)
        output[i]=first_collision(checked,world.collision->items[i],tolerance,cancel);
}
static void retain_row(std::map<std::string,std::vector<int>>& rows,const std::string& key,
    const int* values,int count,uint64_t& bytes) {
    const uint64_t size=key.capacity()+size_t(count)*sizeof(int)+128;
    if(bytes+size>16*1024*1024) return;
    rows[key]=std::vector<int>(values,values+count); bytes+=size;
}
static std::map<std::string,std::vector<int>> checked_rows(const AfCollisionPath* paths,int count,const World& world,
    const CollisionCache& cache,const std::vector<int>& indices,int* output,double tolerance,uint64_t* stats,uint64_t cancel) {
    std::map<std::string,std::vector<int>> rows; const int surfaces=int(indices.size()); uint64_t bytes=0;
    for(int i=0;i<count;++i) {
        check_cancel(cancel); validate(paths[i],surfaces); const auto key=collision_key(paths[i]);
        auto* row=output+i*surfaces; reuse_row(cache,key,indices,row);
        missing_pairs(paths[i],world,row,tolerance,stats,cancel);
        retain_row(rows,key,row,surfaces,bytes);
    }
    return rows;
}
static void cached(const AfCollisionPath* paths,int count,const World& world,CollisionCache& cache,
    const uint64_t* meshes,int surfaces,int* output,double* tolerance,uint64_t* stats,uint64_t cancel) {
    if(count<0||surfaces!=int(world.collision->items.size())||int64_t(count)*surfaces>1000000
        ||!tolerance||!stats||(surfaces&&!meshes)||(count&&(!paths||!output)))
        throw std::runtime_error("Invalid cached collision batch.");
    check_cancel(cancel); stats[0]=stats[1]=0; *tolerance=std::max(1e-9,1e-9*world.length);
    auto keys=surface_keys(world,meshes); const auto indices=previous_surfaces(cache,keys,*tolerance);
    auto rows=checked_rows(paths,count,world,cache,indices,output,*tolerance,stats,cancel);
    check_cancel(cancel); commit_cache(cache,std::move(rows),std::move(keys),*tolerance);
}
}
int af_path_collisions_cached(uint64_t handle,const AfCollisionPath* paths,int count,
    const uint64_t* meshes,const double* matrices,int surfaces,int* output,double* tolerance,uint64_t* stats,uint64_t cancel) {
    try {
        const auto cache=af::routing::collision_cache(handle);
        std::lock_guard<std::mutex> lock(cache->mutex);
        try {
            af::routing::refresh_world(*cache,meshes,matrices,surfaces,cancel);
            af::routing::cached(paths,count,cache->world,*cache,meshes,surfaces,output,tolerance,stats,cancel);
        } catch(...) { af::routing::bound_cache(*cache); throw; }
        af::routing::bound_cache(*cache); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
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
