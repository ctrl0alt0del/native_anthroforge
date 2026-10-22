// SPDX-License-Identifier: GPL-3.0-or-later
#include "stacking_internal.hpp"

namespace af::stacking {
static const Engine& required(uint64_t handle) {
    if(!handle) throw std::runtime_error("Missing stacking session.");
    return *reinterpret_cast<const Engine*>(handle);
}
static AfStackOutput output(const layer::Output& row) {
    AfStackOutput result{row.id,row.status,row.vertices,row.maximum,row.map_ms,row.solve_ms,row.validation_ms,
        row.baseline_self,row.baseline_bone_crossings,row.open_obstacles,row.baseline_penetration,{}};
    std::copy(row.message,row.message+256,result.message); return result;
}
static AfStackOrder order(const layer::Order& row) {
    AfStackOrder result{row.first,row.second,row.underlying,row.covering,row.status,row.warnings,
        {row.positive[0],row.positive[1]},{row.negative[0],row.negative[1]},row.coincident,row.minimum,row.maximum,
        row.fragments,row.points,row.crossings,{}};
    std::copy(row.diagnostic,row.diagnostic+128,result.diagnostic); return result;
}
}
int af_stack_sizes(uint64_t handle,int64_t* sizes) {
    try {
        const auto& engine=af::stacking::required(handle); if(!sizes) throw std::runtime_error("Missing stacking sizes.");
        sizes[0]=int64_t(engine.state.outputs.size()); sizes[1]=int64_t(engine.state.effective.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stack_results(uint64_t handle,AfStackOutput* rows,int count) {
    try {
        const auto& outputs=af::stacking::required(handle).state.outputs;
        if(count!=int(outputs.size())||(!rows&&count)) throw std::runtime_error("Invalid stacking output capacity.");
        int i=0; for(const auto& entry:outputs) rows[i++]=af::stacking::output(entry.second.summary); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stack_orders(uint64_t handle,AfStackOrder* rows,int count) {
    try {
        const auto& orders=af::stacking::required(handle).state.effective;
        if(count!=int(orders.size())||(!rows&&count)) throw std::runtime_error("Invalid stacking order capacity.");
        for(int i=0;i<count;++i) rows[i]=af::stacking::order(orders[size_t(i)].summary);
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stack_points(uint64_t handle,uint64_t identity,double* points,int count,double* metrics) {
    try {
        const auto& result=af::stacking::required(handle).state.outputs.at(identity);
        if(count!=int(result.points.size())||(!points&&count)||!metrics) throw std::runtime_error("Invalid stacking point capacity.");
        std::memcpy(points,result.points.data(),result.points.size()*sizeof(af::stacking::kernel::Vec));
        std::copy(result.vector_metrics,result.vector_metrics+24,metrics); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_stack_dependencies(uint64_t handle,uint64_t* pairs,int capacity) {
    try {
        const auto graph=af::stacking::layer::plan(af::stacking::required(handle).state);
        int count=0; for(const auto& row:graph.parents) count+=int(row.second.size());
        if(!pairs&&capacity==0) return count;
        if(capacity!=count||(!pairs&&count)) throw std::runtime_error("Invalid stacking dependency capacity.");
        int i=0; for(const auto& row:graph.parents) for(auto parent:row.second) {
            pairs[2*i]=row.first; pairs[2*i+1]=parent; ++i;
        }
        return count;
    } catch(const std::exception& error) { af::set_error(error.what()); return -1; }
}
