#include "routing_kernel.hpp"
#include <iostream>

using namespace af::routing::kernel;
static void contacts(AfV3SqpState& state) {
    state.points.resize(40);
    for(int i=0;i<20;++i) {
        AfV3SqpContact row{}; row.edge=2*i; row.normal={1,0,0};
        row.gap=-1; row.model_gap=NAN; state.contacts.push_back(row);
    }
}
static std::vector<std::vector<Vec>> responses() {
    std::vector<std::vector<Vec>> result(20,std::vector<Vec>(40));
    for(int i=0;i<20;++i) result[i][2*i]={1,0,0};
    return result;
}
int main() {
    AfV3NativeSession native; native.base.resize(40);
    AfV3SqpState state; state.native=&native; contacts(state);
    std::vector<int> active; std::vector<Vec> solved;
    const auto dual=af_v3_sqp_active_set(state,responses(),active,solved);
    if(active.size()!=15||active.size()!=dual.size()) {
        std::cerr<<"Iteration limit returned unmatched constraints and multipliers\n"; return 1;
    }
    for(size_t i=0;i<active.size();++i)
        if(std::abs(solved[2*active[i]].x-dual[i])>1e-12) return 2;
    return 0;
}
