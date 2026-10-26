#pragma once
#include "skin_kernel.hpp"
#include "mesh_internal.hpp"

namespace af::skin {
namespace kernel=af::routing::kernel;
using Scene=kernel::af_skin::GapScene;
struct SceneRecord { std::unique_ptr<Scene> value; std::mutex mutex; };
std::shared_ptr<SceneRecord> get_scene(uint64_t handle);
struct SceneAccess {
    std::shared_ptr<SceneRecord> owner;
    std::unique_lock<std::mutex> lock;
    Scene& value;
    SceneAccess(uint64_t handle,uint64_t cancel):owner(get_scene(handle)),lock(owner->mutex),value(*owner->value) {
        check_cancel(cancel); value.cancelled=0;
        value.cancelled.external=cancel?&reinterpret_cast<Cancellation*>(cancel)->cancelled:nullptr;
    }
    ~SceneAccess() { value.cancelled.external=nullptr; }
};
}
