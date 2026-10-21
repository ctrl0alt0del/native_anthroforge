#pragma once
#include "routing_internal.hpp"

namespace af::routing {
struct Trace {
    std::vector<int64_t> records;
    std::vector<Vec> points;
    std::vector<double> contacts;
    std::vector<int> last_trials;
    std::array<int64_t,8> counters{};
    std::array<double,8> measures{};
    std::string error;
    int attempt=0,omitted=0;
    bool success=false,warm=false;
};
void trace_path(Trace* trace,int stage,int span,const std::vector<Vec>& points);
void trace_begin(Trace* trace,const std::vector<Span>& spans);
void trace_step(Trace* trace,const kernel::AfV3SqpCoordinator& controller);
uint64_t retain_trace(std::shared_ptr<Trace> trace);
}
