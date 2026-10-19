#include "routing_pin_graph.hpp"

namespace af::routing {
static Graph checked(const Planning& plan,const Route& points,const Graph& graph,EdgeCache& cache) {
    Graph output(graph.size());
    for(size_t i=0;i<graph.size();++i) for(int64_t j:graph[i]) {
        if(int64_t(i)==j) continue;
        const std::pair<int,int> key{std::min(int(i),int(j)),std::max(int(i),int(j))};
        auto found=cache.find(key);
        if(found==cache.end()) found=cache.emplace(key,clear(plan,points[i],points[j],
            i==0?plan.first:i==1?plan.last:0,j==0?plan.first:j==1?plan.last:0)).first;
        if(found->second) output[i].push_back(j);
    }
    return output;
}
static Component component(const Graph& graph,int start) {
    Component result{{start},std::vector<int>(graph.size(),-2)}; result.parents[start]=-1;
    for(size_t i=0;i<result.order.size();++i) {
        const int node=result.order[i];
        for(int64_t other:graph[node]) if(result.parents[other]==-2) {
            result.parents[other]=node; result.order.push_back(int(other));
        }
    }
    return result;
}
Groups groups(const Planning& plan,const Route& points,const Graph& graph,EdgeCache& cache) {
    const auto filtered=checked(plan,points,graph,cache);
    return {component(filtered,0),component(filtered,1)};
}
std::vector<int> goal_indices(const Component& component) {
    std::vector<int> goals;
    for(int index:component.order) if(index>=2) goals.push_back(index);
    return goals;
}
Route goal_points(const Route& points,const std::vector<int>& indices) {
    Route result;
    for(int index:indices) result.push_back(points[index]);
    return result;
}
Route join(const Planning& plan,const Route& points,const Groups& groups,int side,const Connection& connection) {
    if(connection.goal<0) return {};
    const auto& opposite=groups[1-side]; const auto goals=goal_indices(opposite);
    Route route=connection.path;
    for(int node=goals[connection.goal];node>=0;node=opposite.parents[node]) route.push_back(points[node]);
    if(side) std::reverse(route.begin(),route.end());
    if(!route_clear(plan,route)) return {};
    route=shortcut(plan,route);
    return route_clear(plan,route)?route:Route{};
}
}
