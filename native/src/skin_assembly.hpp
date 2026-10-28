#pragma once
#include "construction_internal.hpp"
#include "skin_meshing.hpp"

namespace af::skin {
struct Assembly {
    Points vertices;
    Faces faces;
    uint64_t cancel=0;
};
void append(Assembly& output,const TileMesh& tile,const std::array<int,3>& start);
std::shared_ptr<Mesh> assemble(Assembly& output,const V3& origin,double voxel);
}
