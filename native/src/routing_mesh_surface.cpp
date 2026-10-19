#include "routing_planner.hpp"

namespace af::routing {
Route surface_vertices(const kernel::AfInstance& item) {
    Route output; for(const auto& p:item.mesh->vertices) output.push_back(kernel::af_transform(item.matrix,p));
    return output;
}
static Vec centroid(const Route& points) {
    Vec center{0,0,0}; for(const auto& point:points) center=kernel::add(center,point);
    return kernel::mul(center,1.0/points.size());
}
Route vertex_normals(const Route& points,const std::vector<int64_t>& triangles) {
    Route normals(points.size(),{0,0,0}); const Vec center=centroid(points);
    for(int slot=0;slot<3;++slot) for(size_t face=0;face<triangles.size();face+=3) {
        const Vec a=points[triangles[face]],b=points[triangles[face+1]],c=points[triangles[face+2]];
        const Vec normal=kernel::cross(kernel::sub(b,a),kernel::sub(c,a));
        auto& target=normals[triangles[face+slot]]; target=kernel::add(target,normal);
    }
    for(size_t i=0;i<points.size();++i) {
        const Vec delta=kernel::sub(points[i],center);
        if(kernel::dot(normals[i],delta)<0) normals[i]=kernel::mul(normals[i],-1);
        if(kernel::norm(normals[i])<=1e-12) normals[i]=kernel::mul(delta,1/std::max(kernel::norm(delta),1e-12));
        normals[i]=kernel::mul(normals[i],1/std::max(kernel::norm(normals[i]),1e-12));
    }
    return normals;
}
static Route bridge(const Planning& plan,Vec first,Vec last,double factor) {
    const Vec delta=kernel::sub(plan.end,plan.start); const double radius=plan.input.options.radius;
    const int count=std::clamp(int(std::ceil(kernel::norm(delta)/std::max(4*radius,1e-6))),2,16);
    Route result{plan.start};
    for(int i=0;i<=count;++i) {
        const double t=double(i)/count; Vec normal=kernel::add(kernel::mul(first,1-t),kernel::mul(last,t));
        normal=kernel::mul(normal,1/std::max(kernel::norm(normal),1e-12));
        result.push_back(kernel::add(kernel::add(plan.start,kernel::mul(delta,t)),kernel::mul(normal,radius*factor)));
    }
    result.push_back(plan.end); unique_adjacent(result); return result;
}
static int nearest_vertex(const Route& points,Vec target) {
    return int(std::min_element(points.begin(),points.end(),[&](Vec a,Vec b) {
        const Vec x=kernel::sub(a,target),y=kernel::sub(b,target); return kernel::dot(x,x)<kernel::dot(y,y);
    })-points.begin());
}
static Route local_bridge(const Planning& plan,const Route& normals,int first,int last) {
    for(double factor:{1.25,1.75,2.5,4.0,8.0}) for(double sign:{1.0,-1.0}) {
        const auto route=bridge(plan,normals[first],normals[last],sign*factor);
        if(route_clear(plan,route)) return shortcut(plan,route);
    }
    return {};
}
static std::vector<int64_t> mesh_route(const Route& points,const std::vector<int64_t>& triangles,int first,int last) {
    std::vector<int64_t> path(points.size()); kernel::AfSearchResult result{};
    const int status=kernel::af_mesh_shortest_path(reinterpret_cast<const double*>(points.data()),int(points.size()),
        triangles.data(),int(triangles.size()/3),first,last,path.data(),int(path.size()),&result);
    if(status||result.status) return {};
    path.resize(result.path_count); return path;
}
static Route offset_route(const Planning& plan,const Route& points,const Route& normals,
                          const std::vector<int64_t>& path,double factor) {
    Route result{plan.start};
    for(const auto index:path) result.push_back(kernel::add(points[index],kernel::mul(normals[index],factor*plan.input.options.radius)));
    result.push_back(plan.end); unique_adjacent(result);
    return result;
}
double route_length(const Route& route) {
    double length=0;
    for(size_t i=1;i<route.size();++i) length+=kernel::norm(kernel::sub(route[i],route[i-1]));
    return length;
}
static Route shortest_offset(const Planning& plan,const Route& points,const Route& normals,const std::vector<int64_t>& path) {
    for(double factor:{1.25,1.75,2.5,4.0,8.0}) {
        Route best;
        for(double sign:{1.0,-1.0}) {
            auto route=offset_route(plan,points,normals,path,sign*factor);
            if(route_clear(plan,route)) {
                route=shortcut(plan,route);
                if(best.empty()||route_length(route)<route_length(best)) best=std::move(route);
            }
        }
        if(!best.empty()) return best;
    }
    return {};
}
Route mesh_surface_route(const Planning& plan) {
    const auto& item=plan.world.collision->items[plan.first-1]; const auto points=surface_vertices(item);
    const auto normals=vertex_normals(points,item.mesh->triangles);
    const int first=nearest_vertex(points,plan.start),last=nearest_vertex(points,plan.end);
    const auto local=local_bridge(plan,normals,first,last);
    if(!local.empty()) return local;
    const auto path=mesh_route(points,item.mesh->triangles,first,last);
    return path.empty()?Route{}:shortest_offset(plan,points,normals,path);
}
}
