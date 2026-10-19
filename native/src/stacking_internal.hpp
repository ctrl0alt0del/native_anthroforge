#pragma once
#include "mesh_internal.hpp"
#include "anthroforge/stacking.h"
#include "stacking_kernel.hpp"

namespace af::stacking {
namespace pair=kernel::af_pair;
namespace layer=kernel::af_layer;
struct Engine { pair::Session session; layer::State state; std::mutex mutex; };
struct Inputs { pair::Work work; pair::Settings detection; layer::State state; };
Inputs capture(const AfStackDomain* domains,int count,const AfStackSettings& settings,
    const AfStackPolicy* policies,int policy_count,const int64_t* regions,int region_count,
    const AfStackObstacle* obstacles,int obstacle_count,uint64_t cancel);
void configure(Inputs& input,const AfStackSettings& settings);
void capture_domains(Inputs& input,const AfStackDomain* domains,int count,uint64_t cancel);
void capture_obstacles(layer::State& state,const AfStackObstacle* inputs,int count,uint64_t cancel);
void execute(Engine& engine,Inputs input,std::atomic<bool>& cancel);
void plan(Engine& engine,Inputs input,std::atomic<bool>& cancel);
void resolve(Engine& engine,const AfStackAccepted* accepted,int count,const uint64_t* targets,int target_count,std::atomic<bool>& cancel);
}
