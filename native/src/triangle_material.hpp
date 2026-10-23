// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <vector>

namespace af {
struct Mesh;
// Per-triangle provenance survives exact Boolean splits and shared seam vertices.
struct TriangleMaterial {
    int64_t source_count=0;
    std::vector<int64_t> origins;
    std::vector<double> coordinates;
    // Untrimmed Boolean construction chart; intentionally unaffected by later deformers.
    int64_t layer_size=0;
    std::vector<double> source_positions;
};
uint64_t triangle_material_storage(const TriangleMaterial& material);
void validate_triangle_material(const TriangleMaterial& material,int64_t triangles);
void validate_triangle_source(const TriangleMaterial& material);
void refine_triangle_material(const Mesh& source,Mesh& output,const std::vector<int>& parents,uint64_t cancel);
}
