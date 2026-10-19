#include "routing_pin_tree.hpp"

namespace af::routing {
struct SearchState { Route points; Graph graph; };
static Route attempt(const Planning& plan,SearchState& state,Route points,Graph graph,bool validate=false) {
    state={std::move(points),std::move(graph)};
    const auto path=search_graph(plan,state.points,state.graph);
    if(path.empty()||(validate&&!route_clear(plan,path))) return {};
    return shortcut(plan,path);
}
static Route expanded(const Planning& plan,SearchState& state) {
    Route candidates=state.points;
    for(bool dense:{false,true}) for(const auto* item:nearby_colliders(plan,dense))
        append_unique(candidates,collider_shell(plan,*item,dense));
    Route points=state.points;
    for(size_t i=points.size();i<candidates.size();++i)
        if(clear(plan,candidates[i],candidates[i])) points.push_back(candidates[i]);
    auto graph=extend_graph(plan,points,state.graph); filter_anchors(plan,points,graph);
    return attempt(plan,state,std::move(points),std::move(graph),true);
}
static Route exits(const Planning& plan,SearchState& state) {
    const auto base=roadmap_candidates(plan,true); const auto original=neighbors(base,48);
    for(bool oblique:{false,true}) {
        auto points=base; append_unique(points,access_points(plan,oblique));
        if(points.size()==base.size()) continue;
        auto graph=extend_graph(plan,points,original); filter_anchors(plan,points,graph);
        auto path=attempt(plan,state,std::move(points),std::move(graph),true);
        if(!path.empty()) return path;
    }
    return {};
}
Route ordinary_roadmap(const Planning& plan) {
    SearchState state; auto points=compatibility(plan);
    auto route=attempt(plan,state,points,neighbors(points,points.size()<=48?int(points.size()):48));
    if(!route.empty()) return route;
    for(bool dense:{false,true}) {
        points=roadmap_candidates(plan,dense); route=attempt(plan,state,points,neighbors(points,dense?48:24));
        if(!route.empty()) return route;
    }
    route=exits(plan,state); if(!route.empty()) return route;
    route=expanded(plan,state); if(!route.empty()) return route;
    return pin_recovery(plan,std::move(state.points),std::move(state.graph));
}
}
