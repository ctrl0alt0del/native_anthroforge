#include "anthroforge/api.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>

namespace {
bool valid_points(const double* xyz, uint64_t count, const double* bounds) {
    if (!xyz || !bounds || !count || count > std::numeric_limits<uint64_t>::max() / 3)
        return false;
    for (uint64_t i = 0; i < count * 3; ++i)
        if (!std::isfinite(xyz[i]))
            return false;
    return true;
}

std::array<double, 6> compute_bounds(const double* xyz, uint64_t count) {
    std::array<double, 6> result{xyz[0], xyz[1], xyz[2], xyz[0], xyz[1], xyz[2]};
    for (uint64_t point = 1; point < count; ++point) {
        for (uint64_t axis = 0; axis < 3; ++axis) {
            result[axis] = std::min(result[axis], xyz[point * 3 + axis]);
            result[axis + 3] = std::max(result[axis + 3], xyz[point * 3 + axis]);
        }
    }
    return result;
}
}

uint32_t af_abi_version(void) {
    return 1;
}

int af_bounds3d(const double* xyz, uint64_t count, double* bounds) {
    if (!valid_points(xyz, count, bounds))
        return 1;
    const auto result = compute_bounds(xyz, count);
    std::copy(result.begin(), result.end(), bounds);
    return 0;
}

