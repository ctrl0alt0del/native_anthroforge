#include "routing_pin_graph.hpp"

namespace af::routing {
static PinTree tree(const Planning& plan,const Route& points,const Groups& components,int side) {
    const auto goals=goal_points(points,goal_indices(components[1-side]));
    const auto validate=[&plan](Vec a,Vec b,int first,int last) { return clear(plan,a,b,first,last); };
    const double scale=std::max({plan.input.options.radius,4*plan.world.slack,plan.world.floor,1e-7});
    return PinTree(side?plan.end:plan.start,side?plan.last:plan.first,goals,validate,scale);
}
static Route sample(const Planning& plan,const Route& points,const Groups& components,std::vector<PinTree>& trees) {
    Route result;
    for(int side=0;side<2;++side) {
        trees.push_back(tree(plan,points,components,side));
        const auto added=initial_exits(trees.back());
        const auto found=connect_goals(trees.back(),added);
        const auto route=join(plan,points,components,side,found);
        if(result.empty()) result=route;
    }
    return result;
}
static Route augment(const Planning& plan,Route& points,Graph& graph,const std::vector<PinTree>& trees) {
    for(const auto& tree:trees) append_unique(points,{tree.points.begin()+1,tree.points.end()});
    graph=extend_graph(plan,points,graph); filter_anchors(plan,points,graph);
    auto route=search_graph(plan,points,graph);
    if(!route_clear(plan,route)) return {};
    route=shortcut(plan,route);
    return route_clear(plan,route)?route:Route{};
}
static Route growth(const Planning& plan,const Route& points,const Groups& components,std::vector<PinTree>& trees) {
    const bool reverse=components[0].order.size()>components[1].order.size();
    for(int side:{int(reverse),int(!reverse)}) {
        auto& tree=trees[side]; tree.goals=goal_points(points,goal_indices(components[1-side]));
        if(tree.goals.empty()) continue;
        auto forest=goal_forest(tree);
        for(int batch=0;batch<256;++batch) {
            check_cancel(plan.input.cancel); const auto found=grow_pair(tree,forest,batch);
            if(found.goal>=0) {
                auto route=join(plan,points,components,side,found); if(!route.empty()) return route;
                break;
            }
        }
    }
    return {};
}
Route pin_recovery(const Planning& plan,Route points,Graph graph) {
    EdgeCache cache; std::vector<PinTree> trees;
    auto components=groups(plan,points,graph,cache);
    auto route=sample(plan,points,components,trees); if(!route.empty()) return route;
    route=augment(plan,points,graph,trees); if(!route.empty()) return route;
    components=groups(plan,points,graph,cache);
    return growth(plan,points,components,trees);
}
}
