#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstring>
#include <deque>
#include <limits>
#include <memory>
#include <mutex>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>
#include <omp.h>
#include "skin_centerlines.hpp"

#ifndef _OPENMP
#error Skin kernels require their dedicated OpenMP target and coordinator CPU reservation.
#endif

namespace af::skin {
struct KernelCancellation {
    std::atomic<int> local{0};
    std::atomic<bool>* external=nullptr;
    operator bool() const { return local.load()!=0||(external&&external->load()); }
    KernelCancellation& operator=(int value) { local.store(value); return *this; }
};
}

// Pinned addon kernels; cancellation bridge is documented in migration/skin/README.md.
#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wunknown-pragmas"
#pragma clang diagnostic ignored "-Wunused-function"
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-variable"
#pragma clang diagnostic ignored "-Wlogical-op-parentheses"
#pragma clang diagnostic ignored "-Wmisleading-indentation"
#pragma clang diagnostic ignored "-Wmissing-field-initializers"
#elif defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunknown-pragmas"
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-variable"
#pragma GCC diagnostic ignored "-Wparentheses"
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#elif defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable:4068 4100 4189 4244 4505)
#endif
namespace af::skin::kernel {
#define AF_EXPORT static
// Reuse source triangle predicates in a separate namespace; do not import routing execution.
#include "../migration/routing/af_roadmap_preparation.hpp"
#include "../migration/routing/collision_reference.hpp"
#include "../migration/routing/af_fiber_planner43.hpp"
#include "../migration/skin/af_skin_gap.hpp"
#include "../migration/skin/af_skin_wrap.hpp"
#include "../migration/skin/af_skin_finish.hpp"
#include "../migration/skin/af_skin_bind.hpp"
#include "../migration/skin/af_skin_precision.hpp"
#include "../migration/skin/af_skin_tiles.hpp"
#include "../migration/skin/af_skin_tile_wrap.hpp"
#include "../migration/skin/af_skin_gap_corridors.hpp"
#include "../migration/skin/af_skin_exterior_precision.hpp"
#include "../migration/skin/af_skin_quality.hpp"
#include "../migration/skin/af_skin_tile_finish.hpp"
#include "../migration/skin/af_skin_components.hpp"
#include "../migration/skin/af_skin_gap_validation.hpp"
#undef AF_EXPORT
}
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
