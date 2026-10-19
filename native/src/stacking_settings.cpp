// SPDX-License-Identifier: GPL-3.0-or-later
#include "stacking_internal.hpp"

namespace af::stacking {
void configure(Inputs& input,const AfStackSettings& s) {
    input.detection={s.search,s.area,s.epsilon,s.fragment_limit,1,s.cache_bytes,s.result_bytes};
    pair::validate_settings(input.detection);
    for(double value:{s.clearance,s.radius,s.strength,s.blend,s.adjustment})
        pair::require(std::isfinite(value)&&value>=0,"STACK_NONNEGATIVE_SETTINGS");
    pair::require(std::isfinite(s.preservation)&&s.preservation>=1,"STACK_VECTOR_PRESERVATION");
    input.state.settings={1,s.clearance,s.radius,s.strength,0};
    input.state.vector_settings={s.blend,s.preservation,s.adjustment};
}
static void policies(Inputs& input,const AfStackPolicy* rows,int count,const int64_t* regions,int size) {
    pair::require(count>=0&&count<=1000000&&(!count||rows),"RELATIONSHIP_INPUT");
    std::vector<layer::PolicyInputV2> converted;
    for(int i=0;i<count;++i) {
        const auto& p=rows[i];
        converted.push_back({{p.first,p.second,p.cover,p.excluded,p.invalid,p.offset,p.count},p.mode});
    }
    layer::capture_policies_v2(input.state,input.work,converted.data(),count,regions,size);
}
Inputs capture(const AfStackDomain* domains,int count,const AfStackSettings& settings,
    const AfStackPolicy* rows,int policy_count,const int64_t* regions,int region_count,
    const AfStackObstacle* obstacles,int obstacle_count,uint64_t cancel) {
    Inputs result; configure(result,settings); capture_domains(result,domains,count,cancel);
    policies(result,rows,policy_count,regions,region_count);
    capture_obstacles(result.state,obstacles,obstacle_count,cancel); return result;
}
}
