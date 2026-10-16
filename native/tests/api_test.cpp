#include "anthroforge/api.h"
#include <array>
#include <iostream>
#include <limits>

bool bounds_contract() {
    const double xyz[]{-2., 4., 1., 3., -5., 9.};
    std::array<double, 6> bounds{};
    const std::array<double, 6> expected{-2., -5., 1., 3., 4., 9.};
    return af_bounds3d(xyz, 2, bounds.data()) == 0 && bounds == expected;
}

bool invalid_contract() {
    const double xyz[]{0., 0., std::numeric_limits<double>::quiet_NaN()};
    std::array<double, 6> bounds{1., 2., 3., 4., 5., 6.};
    const auto before = bounds;
    return af_bounds3d(xyz, 1, bounds.data()) == 1 && bounds == before
        && af_bounds3d(nullptr, 1, bounds.data()) == 1
        && af_bounds3d(xyz, 0, bounds.data()) == 1
        && af_bounds3d(xyz, 1, nullptr) == 1;
}

int main() {
    if (af_abi_version() != 1 || !bounds_contract() || !invalid_contract()) {
        std::cerr << "Native boundary contract failed\n";
        return 1;
    }
    std::cout << "Native boundary contract passed\n";
    return 0;
}

