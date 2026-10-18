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
    double length=1,coordinate=1,floor=1e-9,slack=1e-9;
};
struct Input {
    const double* records;
    int count;
    M4 world,inverse;
    const int* owners;
    AfRoutingOptions options;
    uint64_t cancel;
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
Reference reference(const Input& input);
std::vector<int> allocate_edges(const std::vector<double>& lengths,int edges);
std::vector<Span> spans(const Input& input,World& world,const Reference& reference);
void solve(std::vector<Span>& spans,const Input& input,int64_t* counters,double* measures);
EvaluatedPath result(const Input& input,const Reference& reference,const std::vector<Span>& spans);
}
