#include "skin_symmetry.hpp"
#include "blender_mesh.hpp"
namespace af::skin_symmetry {
std::shared_ptr<Mesh> half(const Mesh& source,const Plane& plane,uint64_t cancel) {
    return blender_mesh::half(source,plane.origin,plane.normal,cancel);
}
}
