// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <vector>

namespace af {
// Owned source coordinates, never source geometry or a live handle. Grid indices
// refer to source vertices; a patch stores projected UV and boundary arclength
// per source vertex (-1 marks interior vertices).
struct MaterialBasis {
    int64_t count=0;
    std::vector<int64_t> grids;
    std::vector<double> parameters;
};
struct Mesh;
MaterialBasis material_basis(const Mesh& mesh);
void validate_basis(const MaterialBasis& basis);
uint64_t basis_storage(const MaterialBasis& basis);
bool same_basis(const MaterialBasis& a,const MaterialBasis& b);
}
