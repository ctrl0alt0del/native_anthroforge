// Included by stacking.cpp; opaque donor cache uses its configured upper bound.
#include "stacking_internal.hpp"

namespace af::stacking {
static uint64_t snapshot_storage(const kernel::TriangleSnapshot& value) {
    return sizeof(value)+value.vertices.capacity()*sizeof(kernel::Vec)+value.triangles.capacity()*sizeof(int64_t)
        +(value.faces.capacity()+value.indexed_faces.capacity())*sizeof(kernel::Bounds)
        +value.nodes.capacity()*sizeof(kernel::BvhNode);
}
static uint64_t side_storage(const pair::Side& value) {
    return sizeof(value)+(value.base.capacity()+value.own.capacity()+value.direction.capacity())*sizeof(kernel::Vec)
        +(value.faces.capacity()+value.parts.capacity()+value.sources.capacity())*sizeof(int64_t)
        +(value.snapshot?snapshot_storage(*value.snapshot):0);
}
static uint64_t session_storage(const pair::Session& value) {
    uint64_t size=sizeof(value)+value.cache.bytes()+pair::bytes(value.result)
        +value.published.pairs.capacity()*sizeof(pair::PairRecord)+value.indices.size()*64;
    for(const auto& side:value.sides) size+=side_storage(side);
    return size;
}
static uint64_t material_storage(const layer::Material& value) {
    uint64_t size=sizeof(value)+value.mesh.vertices.size()*sizeof(double)+value.mesh.faces.size()*sizeof(int)
        +(value.interpolation.capacity()+value.fixed.capacity())*sizeof(int64_t)+value.weights.capacity()*sizeof(double)
        +value.constraints.capacity()*sizeof(afs::Row)+value.original_pins.size()*64+value.error.capacity();
    for(const auto& row:value.constraints) size+=row.terms.capacity()*sizeof(std::pair<int,double>);
    return size;
}
static uint64_t solved_storage(const layer::Solved& value) {
    return sizeof(value)+value.points.capacity()*sizeof(kernel::Vec)+value.bonus.size()*sizeof(double);
}
static uint64_t state_storage(const layer::State& value) {
    uint64_t size=sizeof(value)+session_storage(value.bases)+value.bases.settings.cache_bytes;
    for(const auto* rows:{&value.orders,&value.effective})
        for(const auto& row:*rows) size+=sizeof(row)+(row.geometry?pair::bytes(*row.geometry):0);
    for(const auto* rows:{&value.obstacles,&value.incoming_obstacles})
        for(const auto& row:*rows) size+=side_storage(row);
    for(const auto& row:value.materials) size+=material_storage(row.second)+64;
    for(const auto& row:value.outputs) size+=solved_storage(row.second)+64;
    for(const auto& row:value.solved_cache) size+=solved_storage(row.second.result)+row.second.signature.capacity()+128;
    for(const auto& row:value.policies) size+=sizeof(row)+128+row.second.faces.size()*64;
    return size+value.cache.size()*(sizeof(layer::CachedOrder)+64)+value.policy_results.size()*512
        +value.invalid_directions.size()*64+value.exclusions.size()*64;
}
}
uint64_t af_stack_bytes(uint64_t handle) {
    try {
        if(!handle) throw std::runtime_error("Missing stacking session.");
        auto& engine=*reinterpret_cast<af::stacking::Engine*>(handle);
        std::lock_guard<std::mutex> lock(engine.mutex);
        return sizeof(engine)+af::stacking::session_storage(engine.session)+af::stacking::state_storage(engine.state);
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
