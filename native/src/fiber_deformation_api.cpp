#include "fiber_deformation.hpp"
#include <map>
#include <mutex>
namespace af::fiber {
static std::mutex mutex;
static std::map<uint64_t,std::shared_ptr<Preparation>> preparations;
static uint64_t next=1;
static std::shared_ptr<Preparation> get(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=preparations.find(handle);
    if(found==preparations.end()) throw std::runtime_error("Smooth fiber preparation has expired.");
    return found->second;
}
uint64_t bytes(const Preparation& p) {
    uint64_t result=uint64_t(p.points.size()+p.weights.size())*8+p.arc.size()*8+p.mass.size()*8;
    result+=uint64_t(p.laplacian.nonZeros()+p.bending.nonZeros()+p.coupling.nonZeros())*16;
    result+=uint64_t(p.path->parameters.size())*256; // Includes sparse factor and index allocations.
    for(const auto& b:p.parents) {
        result+=uint64_t(b.vertices.size())*8+b.records.size()*8+b.indices.size()*4;
        for(const auto& r:b.regions) result+=sizeof(Region)+r.ids.size()*4;
        result+=mesh_storage(*b.mesh);
    }
    return result;
}
}
uint64_t af_fiber_deformation_prepare(const AfFiberReference* input,uint64_t cancel) {
    try {
        if(!input) throw std::runtime_error("Missing fiber reference.");
        auto result=af::fiber::prepare(*input,cancel); std::lock_guard<std::mutex> lock(af::fiber::mutex);
        const uint64_t handle=af::fiber::next++; af::fiber::preparations.emplace(handle,std::move(result)); return handle;
    } catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
int af_fiber_deformation_evaluate(uint64_t handle,const uint64_t* meshes,const double* frames,const double* goals,double* output,uint64_t cancel) {
    try {
        if(!meshes||!frames||!goals||!output) throw std::runtime_error("Missing smooth fiber inputs.");
        af::fiber::evaluate(*af::fiber::get(handle),meshes,frames,goals,output,cancel); return 0;
    } catch(const std::exception& e) { af::set_error(e.what()); return 1; }
}
uint64_t af_fiber_deformation_bytes(uint64_t handle) {
    try { return af::fiber::bytes(*af::fiber::get(handle)); }
    catch(const std::exception& e) { af::set_error(e.what()); return 0; }
}
void af_fiber_deformation_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::fiber::mutex); af::fiber::preparations.erase(handle);
}
