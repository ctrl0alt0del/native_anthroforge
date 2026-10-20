#include "routing_planner.hpp"

namespace af::routing {
static int edge_count(const std::vector<Route>& routes) {
    int result=0; for(const auto& route:routes) result+=int(route.size())-1;
    return result;
}
static std::vector<double> lengths(const std::vector<Route>& routes) {
    std::vector<double> result;
    for(const auto& route:routes) for(size_t i=1;i<route.size();++i)
        result.push_back(kernel::norm(kernel::sub(route[i],route[i-1])));
    return result;
}
static Route subdivide(const Route& route,const std::vector<int>& allocation,int& cursor,uint64_t cancel) {
    Route result{route.front()};
    for(size_t i=1;i<route.size();++i) {
        const int count=allocation[cursor++]; const Vec delta=kernel::sub(route[i],route[i-1]);
        for(int step=1;step<=count;++step) {
            check_cancel(cancel);
            result.push_back(kernel::add(route[i-1],kernel::mul(delta,double(step)/count)));
        }
    }
    return result;
}
std::vector<Route> handoff(std::vector<Route> routes,const Input& input,const World& world) {
    if(routes.empty()) return {};
    const int budget=std::max(input.options.samples-int(!input.options.closed),edge_count(routes));
    if(budget>1000000-int(!input.options.closed))
        throw std::runtime_error("Routing requires more than the one-million-point safety limit.");
    const auto allocation=allocate_edges(lengths(routes),budget); int cursor=0;
    for(auto& route:routes) route=subdivide(route,allocation,cursor,input.cancel);
    return valid_handoff(routes,input,world)?routes:std::vector<Route>{};
}
}
