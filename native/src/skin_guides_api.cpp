#include "skin_guides.hpp"
#include "anthroforge/skin_guides.h"
#include <mutex>
#include <unordered_map>

namespace af::skin_guides {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<const Guides>> registry;
static uint64_t next=1;
static uint64_t retain(Guides value) {
    auto owned=std::make_shared<const Guides>(std::move(value));
    std::lock_guard<std::mutex> lock(mutex); const auto id=next++;
    registry.emplace(id,std::move(owned)); return id;
}
static std::shared_ptr<const Guides> get(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=registry.find(handle);
    if(found==registry.end()) throw std::runtime_error("Unknown FLOW guide resource.");
    return found->second;
}
}
uint64_t af_skin_guides_charts(uint64_t base,uint64_t current,const double* frame,int reverse,uint64_t cancel) {
    try {
        if(!frame) throw std::runtime_error("Missing FLOW frame.");
        return af::skin_guides::retain(af::skin_guides::charts(*af::mesh(base),*af::mesh(current),
            Eigen::Map<const af::M4>(frame),reverse!=0,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_skin_guides_path(uint64_t path,const double* frame,uint64_t cancel) {
    try {
        if(!frame) throw std::runtime_error("Missing FLOW frame.");
        return af::skin_guides::retain(af::skin_guides::path(*af::path(path),Eigen::Map<const af::M4>(frame),cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_guides_sizes(uint64_t handle,int64_t* sizes) {
    try {
        if(!sizes) throw std::runtime_error("Missing FLOW sizes.");
        const auto value=af::skin_guides::get(handle);
        sizes[0]=int64_t(value->samples.size()); sizes[1]=int64_t(value->points.size()/3);
        sizes[2]=int64_t(value->offsets.size()); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_guides_copy(uint64_t handle,double* samples,double* points,int64_t* offsets,const int64_t* caps) {
    try {
        const auto value=af::skin_guides::get(handle);
        if(!caps||!offsets||caps[0]!=int64_t(value->samples.size())||caps[1]!=int64_t(value->points.size()/3)
           ||caps[2]!=int64_t(value->offsets.size())||(!samples&&caps[0])||(!points&&caps[1]))
            throw std::runtime_error("Invalid FLOW output buffers.");
        for(size_t i=0;i<value->samples.size();++i)
            std::copy(value->samples[i].begin(),value->samples[i].end(),samples+10*i);
        std::copy(value->points.begin(),value->points.end(),points);
        std::copy(value->offsets.begin(),value->offsets.end(),offsets); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_skin_guides_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::skin_guides::mutex); af::skin_guides::registry.erase(handle);
}
