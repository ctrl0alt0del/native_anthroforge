// SPDX-License-Identifier: GPL-3.0-or-later
// Included by stacking.cpp: the pinned numerical cache has a single owning translation unit.
#include "stacking_internal.hpp"
namespace af::stacking {
std::vector<uint64_t> ready(const layer::Graph& graph,const std::set<uint64_t>& pending,const std::set<uint64_t>& done) {
    std::vector<uint64_t> result;
    for(auto id:pending) if(std::all_of(graph.parents.at(id).begin(),graph.parents.at(id).end(),[&](uint64_t p){return done.count(p);}))
        result.push_back(id);
    return result;
}
void cycles(layer::Graph& graph,std::atomic<bool>& cancel) {
    std::set<uint64_t> pending,done;
    for(const auto& item:graph.parents) pending.insert(item.first);
    while(!pending.empty()) {
        pair::require(!cancel,"PAIR_CANCELLED"); const auto next=ready(graph,pending,done);
        if(next.empty()) break;
        for(auto id:next) { pending.erase(id); done.insert(id); }
    }
    for(auto id:pending) { graph.blocked.insert(id); graph.reasons[id]="STACK_DEPENDENCY_CYCLE_OR_DESCENDANT"; }
}
void failures(layer::State& state,const layer::Graph& graph) {
    for(auto id:graph.blocked) {
        auto& output=state.outputs.at(id); if(output.summary.status==3) continue;
        output.summary.status=2;
        const auto reason=graph.reasons.find(id);
        layer::message(output.summary,reason!=graph.reasons.end()?reason->second:"STACK_INVALID_INPUT_DEPENDENCY");
    }
}
void plan(Engine& engine,Inputs input,std::atomic<bool>& cancel) {
    detect(engine,input,cancel); layer::own_outputs(input.state,engine.session);
    auto graph=layer::plan(input.state); cycles(graph,cancel); layer::propagate(graph);
    failures(input.state,graph); pair::require(!cancel,"PAIR_CANCELLED");
    layer::evict_solved(input.state,engine.session); engine.state=std::move(input.state);
}
}
int af_stack_plan(uint64_t handle,const AfStackDomain* domains,int count,const AfStackSettings* settings,
    const AfStackPolicy* policies,int policy_count,const int64_t* regions,int region_count,
    const AfStackObstacle* obstacles,int obstacle_count,uint64_t cancel) {
    try {
        if(!handle||!settings) throw std::runtime_error("Missing stacking session or settings.");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle); std::lock_guard<std::mutex> lock(engine.mutex);
        auto inputs=af::stacking::capture(domains,count,*settings,policies,policy_count,regions,region_count,obstacles,obstacle_count,cancel);
        std::atomic<bool> idle{false}; auto& cancelled=cancel?reinterpret_cast<af::Cancellation*>(cancel)->cancelled:idle;
        af::stacking::plan(engine,std::move(inputs),cancelled); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
