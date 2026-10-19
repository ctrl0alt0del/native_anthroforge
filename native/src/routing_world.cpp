#include "routing_internal.hpp"
#include <map>
#include <Eigen/LU>

namespace af::routing {
static bool closed_mesh(const Triangles& triangles) {
    std::map<std::pair<int,int>,int> edges;
    for(int face=0;face<triangles.rows();++face)
        for(int side=0;side<3;++side) {
            const int a=triangles(face,side),b=triangles(face,(side+1)%3);
            ++edges[std::minmax(a,b)];
        }
    return std::all_of(edges.begin(),edges.end(),[](const auto& edge){return edge.second==2;});
}
static kernel::Bounds transformed_bounds(const Mesh& mesh,const M4& matrix) {
    auto bounds=kernel::empty_bounds();
    for(int i=0;i<mesh.vertices.rows();++i) {
        const V3 vertex=point(matrix,mesh.vertices.row(i));
        for(int axis=0;axis<3;++axis) {
            bounds.lo[axis]=std::min(bounds.lo[axis],vertex[axis]);
            bounds.hi[axis]=std::max(bounds.hi[axis],vertex[axis]);
        }
    }
    return bounds;
}
static void add_surface(World& world,const Mesh& mesh,const M4& matrix,int owner) {
    if(mesh.triangles.rows()==0) throw std::runtime_error("Routing surface has no triangles.");
    if(!matrix.fullPivLu().isInvertible()) throw std::runtime_error("Routing surface transform is singular.");
    const M4 inverse=matrix.inverse(); const auto triangles=mesh.triangles.cast<int64_t>().eval();
    const int index=kernel::af_world_add_collider(world.collision.get(),mesh.vertices.data(),
        triangles.data(),int(triangles.rows()),owner,owner,closed_mesh(mesh.triangles),matrix.data(),inverse.data());
    if(index<0) throw std::runtime_error("Routing surface capture failed.");
    world.collision->items[index].bounds=transformed_bounds(mesh,matrix);
}
static void snapshot_geometry(World& world,uint64_t cancel) {
    std::vector<double> vertices; std::vector<int64_t> triangles;
    for(const auto& item:world.collision->items) {
        check_cancel(cancel); const int64_t offset=int64_t(vertices.size()/3);
        for(const auto& vertex:item.mesh->vertices) {
            const Vec point=kernel::af_transform(item.matrix,vertex);
            vertices.insert(vertices.end(),{point.x,point.y,point.z});
        }
        for(const auto index:item.mesh->triangles) triangles.push_back(offset+index);
        world.owners.insert(world.owners.end(),item.mesh->triangles.size()/3,item.owner);
    }
    if(!triangles.empty()) world.snapshot.reset(kernel::create_snapshot(vertices.data(),triangles.data(),int(triangles.size()/3)));
}
static void resolve_scales(World& world,double radius) {
    auto bounds=kernel::empty_bounds(); double coordinate=1;
    for(const auto& item:world.collision->items) bounds=kernel::merge_bounds(bounds,item.bounds);
    double squared=0;
    if(!world.collision->items.empty()) for(int i=0;i<3;++i) {
        squared+=(bounds.hi[i]-bounds.lo[i])*(bounds.hi[i]-bounds.lo[i]);
        coordinate=std::max({coordinate,std::abs(bounds.lo[i]),std::abs(bounds.hi[i])});
    }
    world.length=std::max({std::sqrt(squared),radius,1e-6});
    world.coordinate=std::max(coordinate,world.length);
    world.floor=std::max(1e-9*world.length,8*double(std::numeric_limits<float>::epsilon())*world.coordinate);
    world.slack=std::max(world.floor,0.01*radius);
}
World capture_collision_world(const uint64_t* handles,const double* matrices,int count,double radius,uint64_t cancel) {
    if(count<0||count>100000||(count&&(!handles||!matrices))) throw std::runtime_error("Invalid routing surfaces.");
    World world;
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const M4 matrix=Eigen::Map<const M4>(matrices+16*i);
        if(!matrix.allFinite()) throw std::runtime_error("Invalid routing surface transform.");
        add_surface(world,*mesh(handles[i]),matrix,i+1);
    }
    kernel::af_world_commit(world.collision.get());
    resolve_scales(world,radius);
    return world;
}
World capture_world(const uint64_t* handles,const double* matrices,int count,double radius,uint64_t cancel) {
    auto world=capture_collision_world(handles,matrices,count,radius,cancel);
    snapshot_geometry(world,cancel); return world;
}
}
