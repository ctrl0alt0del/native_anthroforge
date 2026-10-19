// SPDX-License-Identifier: GPL-3.0-or-later
#include "stacking_internal.hpp"

namespace af::stacking {
static void retain_caches(layer::State& next,layer::State& previous) {
    next.bases=std::move(previous.bases); next.cache=std::move(previous.cache);
    next.solved_cache=std::move(previous.solved_cache); next.clock=previous.clock;
    next.vector_cache=previous.vector_cache;
}
void detect(Engine& engine,Inputs& input,std::atomic<bool>& cancel) {
    pair::require(!cancel,"PAIR_CANCELLED"); const auto start=pair::Clock::now();
    retain_caches(input.state,engine.state); pair::synchronize(engine.session,input.work.incoming,input.detection);
    engine.session.published=pair::detect(engine.session,1,cancel,false);
    input.state.input_ms=pair::milliseconds(start);
    layer::include_explicit_pairs(input.state,engine.session,cancel);
    layer::order_pairs(input.state,engine.session,cancel); layer::apply_policies(input.state);
}
void execute(Engine& engine,Inputs input,std::atomic<bool>& cancel) {
    detect(engine,input,cancel);
    layer::stack(input.state,engine.session,cancel); layer::evict_solved(input.state,engine.session);
    pair::require(!cancel,"PAIR_CANCELLED"); engine.state=std::move(input.state);
}
}
uint64_t af_stack_create() {
    try { return reinterpret_cast<uint64_t>(new af::stacking::Engine()); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_stack_release(uint64_t handle) { delete reinterpret_cast<af::stacking::Engine*>(handle); }
int af_stack_run(uint64_t handle,const AfStackDomain* domains,int count,const AfStackSettings* settings,
    const AfStackPolicy* policies,int policy_count,const int64_t* regions,int region_count,
    const AfStackObstacle* obstacles,int obstacle_count,uint64_t cancel) {
    try {
        if(!handle||!settings) throw std::runtime_error("Missing stacking session or settings.");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle); std::lock_guard<std::mutex> lock(engine.mutex);
        auto inputs=af::stacking::capture(domains,count,*settings,policies,policy_count,regions,region_count,obstacles,obstacle_count,cancel);
        std::atomic<bool> idle{false}; auto& cancelled=cancel?reinterpret_cast<af::Cancellation*>(cancel)->cancelled:idle;
        af::stacking::execute(engine,std::move(inputs),cancelled); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

// The pinned donor headers define non-inline cache methods; keep one numerical TU.
#include "stacking_capture.cpp"
#include "stacking_settings.cpp"
#include "stacking_results.cpp"
#include "stacking_plan.cpp"
#include "stacking_resolve.cpp"
#include "stacking_group.cpp"
#include "stacking_surface_validation.cpp"
#include "mesh_quality.cpp"
