#include "path_collision_cache.hpp"
#include <unordered_map>

namespace af::routing {
static std::mutex registry_mutex;
static uint64_t next_cache=1;
static std::unordered_map<uint64_t,std::shared_ptr<CollisionCache>> caches;
std::shared_ptr<CollisionCache> collision_cache(uint64_t handle) {
    std::lock_guard<std::mutex> lock(registry_mutex);
    const auto found=caches.find(handle);
    if(found==caches.end()) throw std::runtime_error("Unknown collision cache.");
    return found->second;
}
std::string collision_key(const AfCollisionPath& input) {
    std::string key(reinterpret_cast<const char*>(&input.path),sizeof(input.path));
    key.append(reinterpret_cast<const char*>(input.world),sizeof(input.world));
    key.append(reinterpret_cast<const char*>(input.owners),size_t(input.count)*sizeof(int));
    return key;
}
std::vector<std::string> surface_keys(const World& world,const uint64_t* handles) {
    std::vector<std::string> keys;
    for(size_t i=0;i<world.collision->items.size();++i) {
        std::string key(reinterpret_cast<const char*>(handles+i),sizeof(uint64_t));
        const auto& item=world.collision->items[i];
        key.append(reinterpret_cast<const char*>(item.matrix),sizeof(item.matrix));
        keys.push_back(std::move(key));
    }
    return keys;
}
static std::vector<std::string> input_keys(const uint64_t* handles,const double* matrices,int count) {
    std::vector<std::string> result;
    for(int i=0;i<count;++i) {
        std::string key(reinterpret_cast<const char*>(handles+i),sizeof(uint64_t));
        key.append(reinterpret_cast<const char*>(matrices+16*i),16*sizeof(double));
        result.push_back(std::move(key));
    }
    return result;
}
void refresh_world(CollisionCache& cache,const uint64_t* handles,const double* matrices,int count,uint64_t cancel) {
    if(count<0||count>100000||(count&&(!handles||!matrices))) throw std::runtime_error("Invalid collision surfaces.");
    check_cancel(cancel); auto keys=input_keys(handles,matrices,count);
    if(keys==cache.world_keys) return;
    auto previous=std::move(cache.world); auto old=std::move(cache.handles);
    cache.world=World(); cache.handles.clear(); cache.world_keys.clear();
    cache.world=reuse_collision_world(std::move(previous),old,handles,matrices,count,cancel);
    if(count) cache.handles.assign(handles,handles+count);
    cache.world_keys=std::move(keys);
}
void bound_cache(CollisionCache& cache) {
    uint64_t bytes=sizeof(cache);
    for(const auto& row:cache.rows) bytes+=row.first.capacity()+row.second.capacity()*sizeof(int)+128;
    for(const auto& key:cache.surfaces) bytes+=key.capacity()+64;
    auto size=world_bytes(cache.world)+cache.world_keys.capacity()*sizeof(std::string)
        +cache.handles.capacity()*sizeof(uint64_t);
    for(const auto& key:cache.world_keys) size+=key.capacity();
    cache.bytes=bytes;
    if(bytes+size>128*1024*1024) {
        cache.world=World(); cache.world_keys.clear(); cache.handles.clear();
    } else cache.bytes=bytes+size;
}
std::vector<int> previous_surfaces(const CollisionCache& cache,const std::vector<std::string>& keys,double tolerance) {
    std::map<std::string,int> indices;
    if(tolerance==cache.tolerance)
        for(size_t i=0;i<cache.surfaces.size();++i) indices.emplace(cache.surfaces[i],int(i));
    std::vector<int> result;
    for(size_t i=0;i<keys.size();++i) {
        const auto found=indices.find(keys[i]);
        result.push_back(found==indices.end()||found->second!=int(i)?-1:found->second);
    }
    return result;
}
void commit_cache(CollisionCache& cache,std::map<std::string,std::vector<int>> rows,
    std::vector<std::string> surfaces,double tolerance) {
    uint64_t bytes=sizeof(cache);
    for(const auto& row:rows) bytes+=row.first.capacity()+row.second.capacity()*sizeof(int)+128;
    for(const auto& key:surfaces) bytes+=key.capacity()+64;
    cache.rows.clear(); cache.surfaces.clear(); cache.bytes=0;
    if(bytes>32*1024*1024) return;
    cache.rows=std::move(rows); cache.surfaces=std::move(surfaces);
    cache.tolerance=tolerance; cache.bytes=bytes;
}
}
uint64_t af_collision_cache_create(void) {
    std::lock_guard<std::mutex> lock(af::routing::registry_mutex);
    const auto handle=af::routing::next_cache++;
    af::routing::caches.emplace(handle,std::make_shared<af::routing::CollisionCache>()); return handle;
}
void af_collision_cache_release(uint64_t handle) {
    std::lock_guard<std::mutex> lock(af::routing::registry_mutex); af::routing::caches.erase(handle);
}
uint64_t af_collision_cache_bytes(uint64_t handle) {
    try {
        const auto cache=af::routing::collision_cache(handle);
        std::lock_guard<std::mutex> lock(cache->mutex); return cache->bytes;
    } catch(const std::exception& error) { af::set_error(error.what()); return 0; }
}
