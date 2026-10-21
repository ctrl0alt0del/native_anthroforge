// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "mesh_internal.hpp"

namespace af::query {
struct Input { Vertices vertices; Triangles faces; std::vector<int64_t> origins; };
Input close(const Mesh& source,const Mesh* base,uint64_t cancel);
std::shared_ptr<Mesh> confirmed(const std::shared_ptr<Mesh>& source,const Mesh* base,uint64_t cancel);
std::shared_ptr<Mesh> original(const std::shared_ptr<Mesh>& source);
Hit material_hit(const Mesh& proxy,const Surface& original,Hit hit);
}
