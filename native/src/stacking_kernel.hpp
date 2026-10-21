#pragma once
#include "routing_kernel.hpp"
#include "af_smoothing/model.hpp"
#include <Eigen/LU>
#include <Eigen/Geometry>
#include <Eigen/SparseQR>
#include <map>
#include <set>
#include "stacking_normal_support.hpp"

// Qualified donor kernels plus documented standalone policies; no legacy worker pool.
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
#pragma warning(disable:4068 4100 4505)
#endif
namespace af::stacking::kernel {
using namespace af::routing::kernel;
inline Vec af_env_unit(Vec v) { const double length=norm(v); return length>0?mul(v,1/length):Vec{0,0,0}; }
#include "../migration/stacking/pair_detection/projection.hpp"
#include "../migration/stacking/pair_detection/model.hpp"
#include "../migration/stacking/pair_detection/budget.hpp"
#include "../migration/stacking/pair_detection/cache.hpp"
#include "../migration/stacking/pair_detection/broad.hpp"
#include "../migration/stacking/pair_detection/chart.hpp"
#include "../migration/stacking/pair_detection/fast.hpp"
#include "../migration/stacking/pair_detection/traversal.hpp"
#include "../migration/stacking/pair_detection/store.hpp"
#include "../migration/stacking/pair_detection/pipeline.hpp"
namespace af_pair { struct Work { std::vector<Side> incoming; }; }
#include "../migration/stacking/layer_stacking/model.hpp"
#include "../migration/stacking/layer_stacking/relationship_policy.hpp"
#include "../migration/stacking/layer_stacking/explicit_pairs.hpp"
#include "../migration/stacking/layer_stacking/intersections.hpp"
#include "../migration/stacking/layer_stacking/ordering.hpp"
#include "../migration/stacking/layer_stacking/material_topology.hpp"
#include "../migration/stacking/layer_stacking/material.hpp"
#include "../migration/stacking/layer_stacking/support.hpp"
#include "../migration/stacking/layer_stacking/collision.hpp"
#include "../migration/stacking/layer_stacking/explicit_geometry.hpp"
#include "../migration/stacking/layer_stacking/contact_validation.hpp"
#include "../migration/stacking/layer_stacking/validation.hpp"
#include "../migration/stacking/vector_stacking/engine.hpp"
#include "../migration/stacking/layer_stacking/reuse.hpp"
#include "../migration/stacking/layer_stacking/graph.hpp"
}
#if defined(__clang__)
#pragma clang diagnostic pop
#elif defined(__GNUC__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
