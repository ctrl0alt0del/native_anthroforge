#pragma once
#include "mesh_internal.hpp"
#include "anthroforge/construction.h"
#include <algorithm>
#include <array>
#include <cmath>

namespace af {
struct CurveSample { V3 position, tangent, normal; double radius=1, tilt=0; };
using Samples = std::vector<CurveSample>;
using Points = std::vector<V3>;
std::shared_ptr<Mesh> make_mesh(const Points& points,const Faces& faces,uint64_t cancel,bool complete=true);
std::shared_ptr<Mesh> deform_mesh(const Mesh& source,const Vertices& vertices,uint64_t cancel,bool complete=true);
Faces mesh_faces(const Mesh& source);
Samples read_samples(const double* values,int count);
void rebuild_mesh(Mesh& mesh,uint64_t cancel);
void curve_frames(Samples& samples,bool closed,uint64_t cancel,bool rebuild_tangents=true);
}
