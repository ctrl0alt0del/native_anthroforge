#include "skin_deformation.hpp"
#include <map>
#include <mutex>
namespace af::skin::deformation {
static std::mutex mutex;
static std::map<uint64_t,std::shared_ptr<Preparation>> values;
static uint64_t next=1;
static std::shared_ptr<Preparation> get(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=values.find(handle);
    if(found==values.end()) throw std::runtime_error("Skin deformation preparation has expired.");
    return found->second;
}
}
uint64_t af_skin_deformation_prepare(const AfSkinReference* input,uint64_t cancel) {
    try {
        if(!input) throw std::runtime_error("Missing skin reference inputs.");
        auto value=af::skin::deformation::prepare(*input,cancel);
        std::lock_guard<std::mutex> lock(af::skin::deformation::mutex);
        const auto id=af::skin::deformation::next++; af::skin::deformation::values.emplace(id,std::move(value)); return id;
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
int af_skin_deformation_solve(uint64_t handle,const double* targets,int count,double* points,
    double* predicted,double* diagnostics,uint64_t cancel) {
    try {
        af::skin::deformation::solve(*af::skin::deformation::get(handle),targets,count,points,predicted,diagnostics,cancel); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
int af_skin_deformation_embedding(uint64_t handle,int* ids,double* weights) {
    try { af::skin::deformation::embedding(*af::skin::deformation::get(handle),ids,weights); return 0; }
    catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
uint64_t af_skin_deformation_bytes(uint64_t handle) {
    try { return af::skin::deformation::bytes(*af::skin::deformation::get(handle)); }
    catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
void af_skin_deformation_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::skin::deformation::mutex); af::skin::deformation::values.erase(handle);
}
