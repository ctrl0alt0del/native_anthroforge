#pragma once
#include "mesh_internal.hpp"

namespace af::stacking {
struct NormalSupport { int face=-1; V3 weights=V3::Zero(), normal=V3::Zero(), point=V3::Zero(); double distance=0; };
std::vector<NormalSupport> ambiguous_support(const Vertices& base,const Triangles& faces,
    const Vertices& provider,const Triangles& provider_faces,std::atomic<bool>& cancel);
}
