#include "routing_trace.hpp"
#include "anthroforge/routing_trace.h"
#include <mutex>
#include <unordered_map>

namespace af::routing {
static std::mutex trace_mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Trace>> traces;
static uint64_t next_trace=1;
uint64_t retain_trace(std::shared_ptr<Trace> trace) {
    std::lock_guard<std::mutex> lock(trace_mutex);
    const auto handle=next_trace++; traces.emplace(handle,std::move(trace)); return handle;
}
static std::shared_ptr<Trace> trace(uint64_t handle) {
    std::lock_guard<std::mutex> lock(trace_mutex);
    const auto found=traces.find(handle);
    if(found==traces.end()) throw std::runtime_error("Unknown route diagnostic handle.");
    return found->second;
}
static bool append(Trace& trace,int stage,int span,const std::vector<Vec>& points) {
    if(trace.records.size()/10>=128||trace.points.size()+points.size()>131072) {
        ++trace.omitted; return false;
    }
    trace.records.insert(trace.records.end(),{stage,span,trace.attempt,0,0,0,
        int64_t(trace.points.size()),int64_t(points.size()),int64_t(trace.contacts.size()/17),0});
    trace.points.insert(trace.points.end(),points.begin(),points.end()); return true;
}
void trace_path(Trace* trace,int stage,int span,const std::vector<Vec>& points) {
    if(trace) append(*trace,stage,span,points);
}
void trace_begin(Trace* trace,const std::vector<Span>& spans) {
    if(!trace) return;
    ++trace->attempt; trace->last_trials.assign(spans.size(),-1);
    for(size_t i=0;i<spans.size();++i) trace_path(trace,2,int(i),spans[i].seed);
}
static void contact(Trace& trace,const kernel::AfV3SqpState& state,const kernel::AfV3SqpContact& c) {
    if(c.edge<0||size_t(c.edge+1)>=state.points.size()) return;
    if(trace.contacts.size()/17>=4096) { ++trace.omitted; return; }
    const auto p=kernel::add(state.points[c.edge],kernel::mul(
        kernel::sub(state.points[c.edge+1],state.points[c.edge]),c.factor));
    trace.contacts.insert(trace.contacts.end(),{double(c.edge),double(c.collider),double(c.face),
        double(c.feature),double(c.contained),double(c.limiting),c.factor,c.gap,
        p.x,p.y,p.z,c.surface.x,c.surface.y,c.surface.z,c.normal.x,c.normal.y,c.normal.z});
}
static void state(Trace& trace,const kernel::AfV3SqpState& state,int span) {
    const int stamp=state.trials*8+state.termination;
    if(trace.last_trials[span]==stamp) return;
    trace.last_trials[span]=stamp;
    if(!append(trace,3,span,state.points)) return;
    const size_t begin=trace.records.size()-10,contacts=trace.contacts.size()/17;
    trace.records[begin+3]=state.trials; trace.records[begin+4]=state.accepted;
    trace.records[begin+5]=state.termination;
    for(const auto& value:state.contacts) contact(trace,state,value);
    trace.records[begin+9]=int64_t(trace.contacts.size()/17-contacts);
}
void trace_step(Trace* trace,const kernel::AfV3SqpCoordinator& controller) {
    if(!trace) return;
    for(size_t i=0;i<controller.states.size();++i) state(*trace,controller.states[i],int(i));
}
}
int af_route_trace_info(uint64_t handle,int64_t* info,int64_t* counters,double* measures) {
    try {
        if(!info||!counters||!measures) throw std::runtime_error("Route trace outputs are required.");
        const auto t=af::routing::trace(handle);
        const int64_t values[]{int64_t(t->records.size()/10),int64_t(t->points.size()),
            int64_t(t->contacts.size()/17),t->omitted,t->success,t->warm,t->attempt};
        std::copy_n(values,7,info); std::copy(t->counters.begin(),t->counters.end(),counters);
        std::copy(t->measures.begin(),t->measures.end(),measures); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
const int64_t* af_route_trace_records(uint64_t handle) {
    try { return af::routing::trace(handle)->records.data(); }
    catch(const std::exception& error) { af::set_error(error.what()); return nullptr; }
}
const double* af_route_trace_buffer(uint64_t handle,int kind) {
    try {
        const auto t=af::routing::trace(handle);
        if(kind<0||kind>1) throw std::runtime_error("Unknown route trace buffer.");
        return kind?t->contacts.data():reinterpret_cast<const double*>(t->points.data());
    } catch(const std::exception& error) { af::set_error(error.what()); return nullptr; }
}
const char* af_route_trace_error(uint64_t handle) {
    try { return af::routing::trace(handle)->error.c_str(); }
    catch(const std::exception& error) { af::set_error(error.what()); return nullptr; }
}
void af_route_trace_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::routing::trace_mutex); af::routing::traces.erase(handle);
}
