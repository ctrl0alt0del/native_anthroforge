#include "routing_planner.hpp"

namespace af::routing {
double line_distance(Vec point,Vec start,Vec end) {
    const Vec delta=kernel::sub(end,start); const double divisor=kernel::dot(delta,delta);
    if(divisor<=1e-24) return kernel::norm(kernel::sub(point,start));
    const double t=std::clamp(kernel::dot(kernel::sub(point,start),delta)/divisor,0.0,1.0);
    return kernel::norm(kernel::sub(point,kernel::add(start,kernel::mul(delta,t))));
}
Route rank_points(Route points,Vec start,Vec end,int limit) {
    unique_adjacent(points);
    std::stable_sort(points.begin(),points.end(),[&](Vec a,Vec b){return line_distance(a,start,end)<line_distance(b,start,end);});
    points.resize(std::min(points.size(),size_t(std::max(0,limit))));
    return points;
}
static Vec center(const Route& points) {
    Vec sum{0,0,0}; for(const auto& point:points) sum=kernel::add(sum,point);
    return kernel::mul(sum,1.0/points.size());
}
static Route vertices_shell(const Route& points,double pad,bool dense) {
    const Vec mean=center(points); Route output;
    for(const auto& point:sampled(points,dense?96:32)) {
        const Vec delta=kernel::sub(point,mean);
        output.push_back(kernel::add(point,kernel::mul(delta,std::max(pad,1e-6)/std::max(kernel::norm(delta),1e-12))));
    }
    return output;
}
struct ShellFace { Vec center,normal; double distance; };
static ShellFace shell_face(const Planning& plan,const Route& points,const int64_t* face,Vec mean) {
    const Vec a=points[face[0]],b=points[face[1]],c=points[face[2]];
    const Vec center=kernel::mul(kernel::add(kernel::add(a,b),c),1.0/3);
    Vec normal=kernel::cross(kernel::sub(b,a),kernel::sub(c,a));
    if(kernel::dot(normal,kernel::sub(center,mean))<0) normal=kernel::mul(normal,-1);
    normal=kernel::mul(normal,1/std::max(kernel::norm(normal),1e-12));
    return {center,normal,line_distance(center,plan.start,plan.end)};
}
static void face_shell(Route& output,const Planning& plan,const kernel::AfInstance& item,const Route& points,bool dense) {
    const Vec mean=center(points); std::vector<ShellFace> faces;
    const double pad=std::max(8*plan.input.options.radius,0.001*plan.world.length);
    for(size_t i=0;i<item.mesh->triangles.size();i+=3) {
        check_cancel(plan.input.cancel); faces.push_back(shell_face(plan,points,item.mesh->triangles.data()+i,mean));
    }
    std::stable_sort(faces.begin(),faces.end(),[](const auto& a,const auto& b){return a.distance<b.distance;});
    faces.resize(std::min(faces.size(),size_t(dense?48:20)));
    for(const auto& face:faces) for(int sign=1;sign>=(dense?-1:1);sign-=2)
        output.push_back(kernel::add(face.center,kernel::mul(face.normal,sign*pad)));
}
Route collider_shell(const Planning& plan,const kernel::AfInstance& item,bool dense) {
    const auto points=surface_vertices(item);
    auto output=bounds_shell(item.bounds,std::max(4*plan.input.options.radius,0.00025*plan.world.length),dense);
    const auto vertices=vertices_shell(points,std::max(8*plan.input.options.radius,0.001*plan.world.length),dense);
    output.insert(output.end(),vertices.begin(),vertices.end()); face_shell(output,plan,item,points,dense);
    return output;
}
static double corridor_distance(const kernel::Bounds& bounds,Vec start,Vec end) {
    double distance=INFINITY; const Vec delta=kernel::sub(end,start);
    for(int step=0;step<=32;++step) {
        const Vec point=kernel::add(start,kernel::mul(delta,step/32.0)); Vec closest=point;
        for(int i=0;i<3;++i) (&closest.x)[i]=std::clamp((&point.x)[i],bounds.lo[i],bounds.hi[i]);
        distance=std::min(distance,kernel::norm(kernel::sub(point,closest)));
    }
    return distance;
}
std::vector<const kernel::AfInstance*> nearby_colliders(const Planning& plan,bool dense) {
    std::vector<std::pair<double,int>> order; const auto& items=plan.world.collision->items;
    for(int i=0;i<int(items.size());++i) order.emplace_back(corridor_distance(items[i].bounds,plan.start,plan.end),i);
    std::stable_sort(order.begin(),order.end()); const double threshold=std::max(0.05,0.3*kernel::norm(kernel::sub(plan.end,plan.start)));
    std::vector<const kernel::AfInstance*> result; const int limit=dense?16:8;
    for(const auto& row:order) if(row.first<=threshold&&int(result.size())<limit) result.push_back(&items[row.second]);
    if(result.empty()) for(size_t i=0;i<std::min(order.size(),size_t(limit));++i) result.push_back(&items[order[i].second]);
    return result;
}
static bool contains(const Route& points,Vec target) {
    return std::any_of(points.begin(),points.end(),[&](Vec point){return kernel::norm(kernel::sub(point,target))<=1e-10;});
}
static Route quota(const Planning& plan,Route points,int count,bool dense) {
    unique_adjacent(points);
    if(dense) { points.resize(std::min(points.size(),size_t(count))); return points; }
    const size_t boundary=std::min(size_t(14),points.size());
    Route bounds(points.begin(),points.begin()+boundary),mesh(points.begin()+boundary,points.end());
    bounds=rank_points(bounds,plan.start,plan.end,std::min(int(boundary),std::max(1,count/4)));
    mesh=rank_points(mesh,plan.start,plan.end,count-int(bounds.size()));
    bounds.insert(bounds.end(),mesh.begin(),mesh.end()); return bounds;
}
Route roadmap_candidates(const Planning& plan,bool dense) {
    const auto items=nearby_colliders(plan,dense); const int limit=dense?240:96;
    if(items.empty()) return {plan.start,plan.end};
    const int count=std::max(1,(limit-2)/int(items.size())); Route result{plan.start,plan.end},remainder;
    for(const auto* item:items) {
        auto points=collider_shell(plan,*item,dense); unique_adjacent(points);
        const auto chosen=quota(plan,points,count,dense); result.insert(result.end(),chosen.begin(),chosen.end());
        for(const auto& point:points) if(!contains(chosen,point)) remainder.push_back(point);
    }
    unique_adjacent(result); remainder=rank_points(remainder,plan.start,plan.end,limit-int(result.size()));
    result.insert(result.end(),remainder.begin(),remainder.end()); result.resize(std::min(result.size(),size_t(limit)));
    unique_adjacent(result); return result;
}
}
