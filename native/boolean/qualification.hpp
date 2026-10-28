// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "exterior.hpp"
#include <cstdint>

namespace af::boolean {
enum class Suitability { Reusable, Topology, Intersections, Interior, Orientation };
// The mask excludes temporary closure faces, which still participate in volume tests.
Suitability qualify(const Vertices& vertices,const Triangles& faces,
    const std::vector<uint8_t>& selectable,const std::atomic<bool>* cancel);
int classify(const Vertices& vertices,const Triangles& faces,const Vertices& points,
    std::vector<int>& sides,const std::atomic<bool>* cancel);
}
