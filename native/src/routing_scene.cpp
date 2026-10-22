#include "routing_internal.hpp"
#include <mutex>
#include <unordered_map>

namespace af::routing {
static std::mutex scene_mutex;
static uint64_t next_scene=1;
static std::unordered_map<uint64_t,std::shared_ptr<const World>> scenes;
std::shared_ptr<const World> routing_scene(uint64_t handle) {
    std::lock_guard<std::mutex> lock(scene_mutex);
    const auto found=scenes.find(handle);
    if(found==scenes.end()) throw std::runtime_error("Unknown routing scene handle.");
    return found->second;
}
static uint64_t retain_scene(std::shared_ptr<const World> scene) {
    std::lock_guard<std::mutex> lock(scene_mutex);
    const auto handle=next_scene++; scenes.emplace(handle,std::move(scene)); return handle;
}
static uint64_t snapshot_bytes(const kernel::TriangleSnapshot& value) {
    return sizeof(value)+value.vertices.capacity()*sizeof(Vec)+value.triangles.capacity()*sizeof(int64_t)
        +(value.faces.capacity()+value.indexed_faces.capacity())*sizeof(kernel::Bounds)
        +value.nodes.capacity()*sizeof(kernel::BvhNode);
}
uint64_t world_bytes(const World& value) {
    const auto& world=*value.collision;
    uint64_t total=sizeof(value)+sizeof(world)+snapshot_bytes(*value.snapshot)
        +value.owners.capacity()*sizeof(int)+world.items.capacity()*sizeof(kernel::AfInstance)
        +world.order.capacity()*sizeof(kernel::Bounds)+world.nodes.capacity()*sizeof(kernel::BvhNode);
    for(const auto& item:world.items) total+=snapshot_bytes(*item.mesh);
    return total;
}
}
uint64_t af_routing_scene_capture(const uint64_t* handles,const double* matrices,int count,double radius,uint64_t cancel) {
    try {
        if(!std::isfinite(radius)||radius<0) throw std::runtime_error("Invalid routing clearance.");
        auto world=af::routing::capture_world(handles,matrices,count,radius,cancel);
        af::check_cancel(cancel);
        return af::routing::retain_scene(std::make_shared<af::routing::World>(std::move(world)));
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
void af_routing_scene_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::routing::scene_mutex);
    af::routing::scenes.erase(handle);
}
uint64_t af_routing_scene_bytes(uint64_t handle) {
    try { return af::routing::world_bytes(*af::routing::routing_scene(handle)); }
    catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
