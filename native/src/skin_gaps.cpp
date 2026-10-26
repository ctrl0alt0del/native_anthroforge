#include "skin_kernel.hpp"
#include "mesh_internal.hpp"
#include "anthroforge/skin_gaps.h"

namespace af::skin {
namespace kernel=af::routing::kernel;
using Scene=kernel::af_skin::GapScene;
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<Scene>> scenes;
static uint64_t next_scene=1;
static uint64_t retain(void* raw) {
    if(!raw) throw std::runtime_error("Cannot prepare skin sources: invalid geometry, policies or allocation.");
    auto owned=std::shared_ptr<Scene>(static_cast<Scene*>(raw));
    std::lock_guard<std::mutex> lock(mutex); const auto handle=next_scene++;
    scenes.emplace(handle,std::move(owned)); return handle;
}
static std::shared_ptr<Scene> scene(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=scenes.find(handle);
    if(found==scenes.end()) throw std::runtime_error("Unknown skin source scene.");
    return found->second;
}
static void release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); scenes.erase(handle);
}
static void sample(const Scene& s,const double* points,int count,double reach,double* output,uint64_t cancel) {
    if(!points||!output||count<0||!std::isfinite(reach)||reach<=0)
        throw std::runtime_error("Invalid skin gap query buffers.");
    for(int i=0;i<count;++i) {
        check_cancel(cancel); const auto p=kernel::load3(points+3LL*i);
        if(!std::isfinite(p.x)||!std::isfinite(p.y)||!std::isfinite(p.z))
            throw std::runtime_error("Skin gap queries require finite positions.");
        kernel::af_skin::sample(s,p,reach,output+13LL*i);
    }
}
}
uint64_t af_skin_scene_create(const double* xyz,int vertices,const int64_t* faces,int triangles,
                             const int* owners,int sources,const double* policies,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        return af::skin::retain(af::routing::kernel::af_skin_gap_create(xyz,vertices,faces,triangles,owners,sources,policies));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_scene_sample(uint64_t handle,const double* points,int count,double reach,double* output,uint64_t cancel) {
    try {
        const auto source=af::skin::scene(handle);
        af::skin::sample(*source,points,count,reach,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_skin_scene_destroy(uint64_t handle) { af::skin::release(handle); }
