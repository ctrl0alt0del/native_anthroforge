#include "routing_planner.hpp"
#include <set>

namespace af::routing {
static std::array<double,3> point_key(Vec point) {
    return {std::nearbyint(point.x*1e10)/1e10,std::nearbyint(point.y*1e10)/1e10,std::nearbyint(point.z*1e10)/1e10};
}
void append_unique(Route& points,const Route& additions) {
    std::set<std::array<double,3>> seen; for(const auto& point:points) seen.insert(point_key(point));
    for(const auto& point:additions) if(seen.insert(point_key(point)).second) points.push_back(point);
}
static Route exit_directions(Vec normal,bool oblique) {
    if(!oblique) return {normal};
    int axis=0; for(int i=1;i<3;++i) if(std::abs((&normal.x)[i])<std::abs((&normal.x)[axis])) axis=i;
    Vec basis{0,0,0}; (&basis.x)[axis]=1;
    const Vec tangent=kernel::af_unit(kernel::cross(normal,basis)),bitangent=kernel::cross(normal,tangent);
    Route result{normal,kernel::mul(normal,-1)};
    for(double sign:{1.0,-1.0}) {
        const Vec side=kernel::mul(normal,sign);
        for(const Vec vector:{tangent,kernel::mul(tangent,-1),bitangent,kernel::mul(bitangent,-1)})
            result.push_back(kernel::af_unit(kernel::add(side,vector)));
    }
    return result;
}
static Vec surface_normal(const Planning& plan,Vec point,int owner) {
    const auto& item=plan.world.collision->items[owner-1]; kernel::AfNearest closest{{},{},INFINITY,-1};
    kernel::af_nearest_item(item,owner-1,point,closest);
    const bool inside=kernel::af_inside_instance(item,point);
    Vec normal=kernel::af_unit(inside?kernel::sub(closest.point,point):kernel::sub(point,closest.point));
    if(kernel::norm(normal)<=kernel::eps()) normal=kernel::af_unit(closest.face_normal);
    return normal;
}
static Route access(const Planning& plan,Vec point,int owner,bool oblique) {
    if(!owner) return {};
    const Vec normal=surface_normal(plan,point,owner);
    if(kernel::norm(normal)<=1e-12) return {};
    const double scale=std::max({plan.input.options.radius,4*plan.world.slack,plan.world.floor,1e-7});
    Route result;
    for(const auto& direction:exit_directions(normal,oblique)) for(double factor:{2.0,4.0}) {
        const Vec candidate=kernel::add(point,kernel::mul(direction,scale*factor));
        if(clear(plan,point,candidate,owner,0)&&clear(plan,candidate,candidate)) result.push_back(candidate);
    }
    return result;
}
Route access_points(const Planning& plan,bool oblique) {
    auto first=access(plan,plan.start,plan.first,oblique);
    const auto second=access(plan,plan.end,plan.last,oblique);
    first.insert(first.end(),second.begin(),second.end()); return first;
}
Graph extend_graph(const Planning& plan,const Route& points,const Graph& original) {
    Graph graph=original; graph.resize(points.size()); std::vector<kernel::af_roadmap::Item> work;
    for(int64_t i=int64_t(original.size());i<int64_t(points.size());++i) {
        check_cancel(plan.input.cancel);
        kernel::af_roadmap::nearest(reinterpret_cast<const double*>(points.data()),int64_t(points.size()),i,48,work);
        kernel::af_roadmap::add_edge(graph,i,0); kernel::af_roadmap::add_edge(graph,i,1);
        for(const auto& item:work) kernel::af_roadmap::add_edge(graph,i,item.second);
    }
    for(auto& row:graph) {
        check_cancel(plan.input.cancel); std::sort(row.begin(),row.end());
        row.erase(std::unique(row.begin(),row.end()),row.end());
    }
    return graph;
}
void filter_anchors(const Planning& plan,const Route& points,Graph& graph) {
    std::set<std::pair<int64_t,int64_t>> pairs,blocked;
    for(size_t i=0;i<graph.size();++i) for(auto j:graph[i])
        if(int64_t(i)!=j&&(i<2||j<2)) pairs.insert(std::minmax(int64_t(i),j));
    for(const auto& [a,b]:pairs) {
        const int first=a==0?plan.first:a==1?plan.last:0,last=b==0?plan.first:b==1?plan.last:0;
        if(!clear(plan,points[a],points[b],first,last)) blocked.emplace(a,b);
    }
    for(size_t i=0;i<graph.size();++i) {
        auto& row=graph[i]; row.erase(std::remove_if(row.begin(),row.end(),[&](int64_t j) {
            return blocked.count(std::minmax(int64_t(i),j))!=0;
        }),row.end());
    }
}
}
