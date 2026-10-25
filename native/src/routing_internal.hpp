#pragma once
#include "path_internal.hpp"
#include "anthroforge/routing.h"
#include "routing_kernel.hpp"

namespace af::routing {
using Vec=kernel::Vec;
using WorldHandle=std::unique_ptr<kernel::AfWorld,decltype(&kernel::af_world_destroy)>;
using SessionHandle=std::unique_ptr<kernel::AfV3NativeSession,decltype(&kernel::af_v3_session_destroy)>;
using ControllerHandle=std::unique_ptr<kernel::AfV3SqpCoordinator,decltype(&kernel::af_v3_native_sqp_destroy)>;
struct World {
    WorldHandle collision{new kernel::AfWorld(),kernel::af_world_destroy};
    std::unique_ptr<kernel::TriangleSnapshot> snapshot{new kernel::TriangleSnapshot()};
    std::vector<int> owners;
    double length=1,coordinate=1,floor=1e-9,slack=1e-9,radius=0;
};
struct Trace;
struct Input {
    const double* records;
    int count;
    M4 world,inverse;
    std::vector<int> owners;
    AfRoutingOptions options;
    uint64_t cancel;
    int backend=AF_ROUTING_CUSTOM;
    Trace* trace=nullptr;
    double length_weight=0.9;
    int checkpoint_steps=1;
};
struct Reference {
    std::vector<Vec> points;
    std::vector<int64_t> pins;
    std::vector<double> parameters;
};
struct Span {
    std::vector<Vec> reference,seed,output,targets;
    std::vector<int64_t> pins;
    std::vector<int> first,second;
    SessionHandle session{nullptr,kernel::af_v3_session_destroy};
    kernel::AfV3SqpJob job{};
};
World capture_world(const uint64_t* handles,const double* matrices,int count,double radius,uint64_t cancel);
World capture_collision_world(const uint64_t* handles,const double* matrices,int count,double radius,uint64_t cancel);
std::shared_ptr<const World> routing_scene(uint64_t handle);
uint64_t world_bytes(const World& world);
World reuse_collision_world(World previous,const std::vector<uint64_t>& old,const uint64_t* handles,
    const double* matrices,int count,uint64_t cancel);
Reference reference(const Input& input);
Reference reference(const Input& input,const std::vector<int>& counts);
std::vector<Span> spans(const Input& input,const World& world,const Reference& reference);
bool warm_start(const Input& input,const World& world,const Reference& reference,std::vector<Span>& spans,uint64_t handle);
bool solve(std::vector<Span>& spans,const Input& input,int64_t* counters,double* measures);
void configure_piqp(kernel::AfV3SqpJob& job,uint64_t cancel);
EvaluatedPath result(const Input& input,const Reference& reference,const std::vector<Span>& spans);
}
