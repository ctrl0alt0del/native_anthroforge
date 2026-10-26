#include "skin_fields.hpp"
#include "mesh_internal.hpp"
#include "anthroforge/skin_fields.h"
#include <algorithm>
#include <memory>
#include <mutex>
#include <unordered_map>

namespace af::skin {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<const Fields>> registry;
static uint64_t next_handle=1;
static uint64_t retain(Fields value) {
    auto owned=std::make_shared<const Fields>(std::move(value));
    std::lock_guard<std::mutex> lock(mutex);
    const auto handle=next_handle++; registry.emplace(handle,std::move(owned)); return handle;
}
std::shared_ptr<const Fields> get_fields(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=registry.find(handle);
    if(found==registry.end()) throw std::runtime_error("Unknown skin field resource.");
    return found->second;
}
static void release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); registry.erase(handle);
}
}
uint64_t af_skin_fields_create(const double* xyz,int vertices,const int64_t* faces,int triangles,
                              const uint8_t* scp,const double* collagen,const double* settings,
                              int resolution,uint64_t budget,uint64_t cancel) {
    try {
        const af::skin::Source source{xyz,vertices,faces,triangles,scp,collagen};
        return af::skin::retain(af::skin::prepare(source,settings,resolution,budget,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
uint64_t af_skin_fields_sources(const double* xyz,int vertices,const int64_t* faces,int triangles,
    const uint8_t* scp,const double* collagen,const int64_t* segments,int segment_count,
    const double* settings,int resolution,uint64_t budget,uint64_t cancel) {
    try {
        const af::skin::Source source{xyz,vertices,faces,triangles,scp,collagen,segments,segment_count};
        return af::skin::retain(af::skin::prepare(source,settings,resolution,budget,cancel));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_fields_info(uint64_t handle,int* shape,double* origin_voxel,int* resolution) {
    try {
        if(!shape||!origin_voxel||!resolution) throw std::runtime_error("Missing skin information buffers.");
        const auto value=af::skin::get_fields(handle); const auto& g=value->grid;
        std::copy(g.shape.begin(),g.shape.end(),shape); std::copy(g.origin.begin(),g.origin.end(),origin_voxel);
        origin_voxel[3]=g.voxel; *resolution=g.resolution; return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_fields_copy(uint64_t handle,int kind,double* output,uint64_t capacity) {
    try {
        const auto value=af::skin::get_fields(handle);
        if(kind<0||kind>3||!output||capacity<value->grid.count) throw std::runtime_error("Invalid skin field buffer.");
        std::copy(value->values[kind].begin(),value->values[kind].end(),output); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
uint64_t af_skin_fields_bytes(uint64_t handle) {
    try {
        const auto value=af::skin::get_fields(handle); uint64_t result=sizeof(af::skin::Fields);
        for(const auto& values:value->values) result+=values.capacity()*sizeof(double);
        return result;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_skin_fields_destroy(uint64_t handle) { af::skin::release(handle); }
