// SPDX-License-Identifier: GPL-3.0-or-later
#include "tissue_preparation.hpp"
#include "tissue_branches.hpp"
#include <mutex>
#include <unordered_map>

namespace af::tissue {
static std::mutex preparation_mutex;
static uint64_t next_preparation=1;
static std::unordered_map<uint64_t,std::shared_ptr<const InflationPreparation>> preparations;
static auto preparation(uint64_t handle) {
    std::lock_guard<std::mutex> lock(preparation_mutex);
    const auto found=preparations.find(handle);
    if(found==preparations.end()) throw std::runtime_error("Expired tissue preparation.");
    return found->second;
}
static void compatible(const InflationPreparation& value,const AfTissueInflation* settings,int count) {
    if(!settings||count<1||size_t(count)!=value.parts.size()) throw std::runtime_error("Tissue preparation parts changed.");
    for(int i=0;i<count;++i) {
        const auto& p=value.parts[i]; const auto& s=settings[i];
        if(p.mode!=preparation_mode(s)||(p.mode==2&&p.direction!=s.direction))
            throw std::runtime_error("Tissue preparation mode changed.");
    }
}
}
uint64_t af_tissue_preparation_create(uint64_t source,const AfTissueInflation* settings,int count,uint64_t cancel) {
    try {
        auto value=std::make_shared<const af::tissue::InflationPreparation>(af::tissue::prepare_inflation(af::mesh(source),settings,count,cancel));
        std::lock_guard<std::mutex> lock(af::tissue::preparation_mutex);
        const auto handle=af::tissue::next_preparation++; af::tissue::preparations.emplace(handle,std::move(value)); return handle;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_tissue_preparation_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::tissue::preparation_mutex); af::tissue::preparations.erase(handle);
}
uint64_t af_tissue_preparation_bytes(uint64_t handle,int retained) {
    try {
        const auto value=af::tissue::preparation(handle);
        return af::tissue::preparation_bytes(*value)+(retained?af::mesh_storage(*value->source):0);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_tissue_inflate_prepared(uint64_t handle,const AfTissueInflation* settings,int count,const double* connectors,int envelope,uint64_t cancel,int complete) {
    try {
        af::check_cancel(cancel); const auto value=af::tissue::preparation(handle); af::tissue::compatible(*value,settings,count);
        return af::retain(af::tissue::inflate_parts(*value->source,settings,count,connectors,envelope!=0,cancel,value.get(),complete!=0));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
