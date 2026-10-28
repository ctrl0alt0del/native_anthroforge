#pragma once
#include "skin_stitch.hpp"
namespace af::skin_symmetry {
using skin_loops::Plane;
using skin_quads::Quads;
std::shared_ptr<Mesh> half(const Mesh& source,const Plane& plane,uint64_t cancel);
Quads mirror(Quads source,const Plane& plane,uint64_t cancel);
}
