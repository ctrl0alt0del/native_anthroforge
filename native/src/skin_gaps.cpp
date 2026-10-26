#include "skin_gap_internal.hpp"
#include "anthroforge/skin_gaps.h"

namespace af::skin {
static std::mutex mutex;
static std::unordered_map<uint64_t,std::shared_ptr<SceneRecord>> scenes;
static uint64_t next_scene=1;
static uint64_t retain(void* raw) {
    if(!raw) throw std::runtime_error("Cannot prepare skin sources: invalid geometry, policies or allocation.");
    std::unique_ptr<Scene> input(static_cast<Scene*>(raw));
    auto owned=std::make_shared<SceneRecord>(); owned->value=std::move(input);
    std::lock_guard<std::mutex> lock(mutex); const auto handle=next_scene++;
    scenes.emplace(handle,std::move(owned)); return handle;
}
std::shared_ptr<SceneRecord> get_scene(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); const auto found=scenes.find(handle);
    if(found==scenes.end()) throw std::runtime_error("Unknown skin source scene.");
    return found->second;
}
static void release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(mutex); scenes.erase(handle);
}
static std::unique_ptr<Scene> empty_scene(int sources,const double* policies) {
    if(sources<1||!policies) throw std::runtime_error("Missing skin source policies.");
    auto scene=std::make_unique<Scene>(); scene->mesh=std::make_unique<kernel::TriangleSnapshot>();
    for(int i=0;i<sources;++i) {
        if(!std::isfinite(policies[3*i])||policies[3*i]<0||!std::isfinite(policies[3*i+1])
           ||policies[3*i+1]<0||policies[3*i+1]>1) throw std::runtime_error("Invalid skin source policy.");
        scene->limits.push_back(policies[3*i]); scene->strengths.push_back(policies[3*i+1]);
        scene->skeletal.push_back(policies[3*i+2]!=0); scene->normal_sign.push_back(0);
    }
    return scene;
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
        const af::skin::SceneAccess source(handle,cancel);
        af::skin::sample(source.value,points,count,reach,output,cancel); return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
void af_skin_scene_destroy(uint64_t handle) { af::skin::release(handle); }
int af_skin_scene_progress(uint64_t handle,int* values) {
    try {
        if(!values) throw std::runtime_error("Missing skin progress buffer.");
        const auto source=af::skin::get_scene(handle);
        return af::routing::kernel::af_skin_gap_progress(source->value.get(),values);
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
int af_skin_scene_bind(uint64_t handle,uint64_t mesh,int* owners,int* triangles,
                       float* barycentric,float* weights,float* offsets,float* support,uint64_t cancel) {
    try {
        const af::skin::SceneAccess source(handle,cancel); const auto geometry=af::mesh(mesh);
        const int status=af::routing::kernel::af_skin_bind(&source.value,geometry->vertices.data(),
            int(geometry->vertices.rows()),owners,triangles,barycentric,weights,offsets,support);
        af::check_cancel(cancel);
        if(status) throw std::runtime_error("Cannot capture skin source bindings.");
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}

uint64_t af_skin_scene_sources(const double* xyz,int vertices,const int64_t* faces,int triangles,
    const int* owners,int sources,const double* policies,const int64_t* segments,int count,const int* segment_owners,uint64_t cancel) {
    try {
        af::check_cancel(cancel);
        auto lines=af::skin::centerlines(xyz,vertices,segments,segment_owners,count,sources,cancel);
        auto scene=triangles?std::unique_ptr<af::skin::Scene>(static_cast<af::skin::Scene*>(
            af::routing::kernel::af_skin_gap_create(xyz,vertices,faces,triangles,owners,sources,policies)))
            :af::skin::empty_scene(sources,policies);
        if(!scene||(triangles==0&&count==0)) throw std::runtime_error("Skin source geometry is empty or invalid.");
        scene->lines=std::move(lines); return af::skin::retain(scene.release());
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
int af_skin_scene_bind_sources(uint64_t handle,uint64_t mesh,int* owners,int* elements,
    float* bary,float* weights,float* offsets,float* support,int* kinds,uint64_t cancel) {
    try {
        if(!owners||!elements||!bary||!weights||!offsets||!support||!kinds)
            throw std::runtime_error("Missing skin source binding buffers.");
        const af::skin::SceneAccess source(handle,cancel); const auto geometry=af::mesh(mesh);
        for(int i=0;i<geometry->vertices.rows();++i) {
            af::check_cancel(cancel);
            af::routing::kernel::af_skin::bind_point(source.value,af::routing::kernel::load3(geometry->vertices.data()+3LL*i),
                owners+4LL*i,elements+4LL*i,bary+12LL*i,weights+4LL*i,offsets[i],support[i],kinds+4LL*i);
        }
        return 0;
    } catch(const std::exception& error) { af::set_error(error.what()); return 1; }
}
