#pragma once
#include "routing_internal.hpp"
#include "anthroforge/path_collisions.h"
#include <map>

namespace af::routing {
struct CollisionCache {
    std::mutex mutex;
    std::map<std::string,std::vector<int>> rows;
    std::vector<std::string> surfaces;
    double tolerance=0;
    uint64_t bytes=0;
    World world;
    std::vector<uint64_t> handles;
    std::vector<std::string> world_keys;
};
std::shared_ptr<CollisionCache> collision_cache(uint64_t handle);
std::string collision_key(const AfCollisionPath& input);
std::vector<std::string> surface_keys(const World& world,const uint64_t* handles);
void refresh_world(CollisionCache& cache,const uint64_t* handles,const double* matrices,int count,uint64_t cancel);
void bound_cache(CollisionCache& cache);
std::vector<int> previous_surfaces(const CollisionCache& cache,const std::vector<std::string>& keys,double tolerance);
void commit_cache(CollisionCache& cache,std::map<std::string,std::vector<int>> rows,
    std::vector<std::string> surfaces,double tolerance);
}
