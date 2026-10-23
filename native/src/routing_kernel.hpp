#pragma once
#include <algorithm>
#include <array>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <cmath>
#include <cstdint>
#include <limits>
#include <memory>
#include <mutex>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <unordered_map>
#include <tuple>
#include <thread>
#include <utility>
#include <vector>

// Pinned addon kernels have their own formatting. No exported legacy ABI or worker pool.
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
// Imported kernels keep unused OpenMP workers and bounded integer narrowing.
#pragma warning(disable:4068 4100 4189 4244 4505)
#endif
#ifdef _OPENMP
#error Routing concurrency belongs to the application task coordinator.
#endif
namespace af::routing::kernel {
#define AF_EXPORT static
#include "../migration/routing/af_roadmap_preparation.hpp"
#include "../migration/routing/collision_reference.hpp"
#include "../migration/routing/af_fiber_planner43.hpp"
#include "../migration/routing/af_fiber_contact3.hpp"
#include "../migration/routing/af_fiber_v3_session.hpp"
#include "../migration/routing/af_fiber_v3_batch.hpp"
#include "../migration/routing/af_fiber_v3_operations.hpp"
#include "../migration/routing/af_fiber_v3_coordinator.hpp"
#include "../migration/routing/af_fiber_v3_native_sqp.hpp"
#undef AF_EXPORT
}
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
