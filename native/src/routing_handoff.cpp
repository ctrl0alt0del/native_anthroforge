#include "routing_planner.hpp"

namespace af::routing {
static int edge_count(const std::vector<Route>& routes) {
    int result=0; for(const auto& route:routes) result+=int(route.size())-1;
    return result;
}
static double removal_cost(const Route& route,size_t index) {
    return kernel::norm(kernel::sub(route[index],route[index-1]))+
        kernel::norm(kernel::sub(route[index+1],route[index]))-
        kernel::norm(kernel::sub(route[index+1],route[index-1]));
}
static bool remove_corner(std::vector<Route>& routes,const Planning& plan) {
    std::tuple<double,int,int> best{INFINITY,-1,-1};
    for(int i=0;i<int(routes.size());++i) for(int j=1;j+1<int(routes[i].size());++j)
        if(clear(plan,routes[i][j-1],routes[i][j+1])) best=std::min(best,{removal_cost(routes[i],j),i,j});
    const auto [cost,route,point]=best;
    if(route<0) return false;
    routes[route].erase(routes[route].begin()+point);
    return true;
}
static std::vector<double> lengths(const std::vector<Route>& routes) {
    std::vector<double> result;
    for(const auto& route:routes) for(size_t i=1;i<route.size();++i)
        result.push_back(kernel::norm(kernel::sub(route[i],route[i-1])));
    return result;
}
static Route subdivide(const Route& route,const std::vector<int>& allocation,int& cursor) {
    Route result{route.front()};
    for(size_t i=1;i<route.size();++i) {
        const int count=allocation[cursor++]; const Vec delta=kernel::sub(route[i],route[i-1]);
        for(int step=1;step<=count;++step)
            result.push_back(kernel::add(route[i-1],kernel::mul(delta,double(step)/count)));
    }
    return result;
}
std::vector<Route> handoff(std::vector<Route> routes,const Input& input,World& world) {
    if(routes.empty()) return {};
    const int budget=input.options.samples-int(!input.options.closed);
    Planning plan{world,input,0,0,{},{},std::max(2.5*input.options.radius,1e-7),input.options.radius-world.slack};
    while(edge_count(routes)>budget) if(!remove_corner(routes,plan)) return {};
    const auto allocation=allocate_edges(lengths(routes),budget); int cursor=0;
    for(auto& route:routes) { check_cancel(input.cancel); route=subdivide(route,allocation,cursor); }
    return routes;
}
}
